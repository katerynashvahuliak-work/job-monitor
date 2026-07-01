import json
import logging
from datetime import date
from pathlib import Path

import yaml
from openai import OpenAI

from config import OPENAI_API_KEY

logger = logging.getLogger(__name__)
client = OpenAI(api_key=OPENAI_API_KEY)

_prompts = yaml.safe_load((Path(__file__).parent / "prompts.yaml").read_text())
EXTRACT_SYSTEM: str = _prompts["extract_jobs"]["system"].strip()
FILTER_SYSTEM: str = _prompts["filter_ml_jobs"]["system"].strip()


def extract_jobs(page_text: str, company_name: str) -> list[dict]:
    today = date.today().isoformat()
    user_message = f"Company: {company_name}\nToday's date: {today}\n\nPage content:\n{page_text}"

    response = client.chat.completions.create(
        model="gpt-5.4-mini",
        messages=[
            {"role": "system", "content": EXTRACT_SYSTEM},
            {"role": "user", "content": user_message},
        ],
        temperature=0,
    )

    raw = response.choices[0].message.content.strip()
    try:
        jobs = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("Failed to parse extract_jobs response for %s: %s", company_name, raw)
        return []

    for job in jobs:
        job["company_name"] = company_name
        if not job.get("posted_date"):
            job["posted_date"] = today

    return jobs


def filter_ml_jobs(jobs: list[dict]) -> list[dict]:
    if not jobs:
        return []

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": FILTER_SYSTEM},
            {"role": "user", "content": json.dumps(jobs)},
        ],
        temperature=0,
    )

    raw = response.choices[0].message.content.strip()
    # strip markdown fencing if model wraps response
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("Failed to parse filter_ml_jobs response: %s", raw)
        return []
