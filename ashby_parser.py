"""Ashby ATS public API parser."""

import logging
from datetime import date

import httpx

logger = logging.getLogger(__name__)

API_BASE = "https://api.ashbyhq.com/posting-api/job-board/{slug}"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; JobMonitorBot/1.0)",
    "Accept": "application/json",
}


def fetch_ashby_vacancies(company_name: str, slug: str) -> list[dict]:
    url = API_BASE.format(slug=slug)
    response = httpx.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    jobs = response.json().get("jobs", [])

    today = date.today().isoformat()
    result = []
    for item in jobs:
        if not item.get("isListed"):
            continue

        title = item.get("title", "").strip()
        if not title:
            continue

        posted_raw = item.get("publishedAt", "")
        posted_date = posted_raw[:10] if posted_raw else today

        location = item.get("location", "")
        department = item.get("department", "")
        description = " | ".join(filter(None, [department, location]))

        result.append({
            "company_name": company_name,
            "title": title,
            "url": item.get("jobUrl", ""),
            "posted_date": posted_date,
            "description": description,
        })

    return result
