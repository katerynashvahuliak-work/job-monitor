"""AltexSoft direct API parser."""

import logging
from datetime import date

import httpx

logger = logging.getLogger(__name__)

API_URL = "https://www.altexsoft.com/api/careers/vacancies?limit=500"
VACANCY_BASE = "https://www.altexsoft.com/vacancy/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}


def fetch_altexsoft_vacancies(company_name: str) -> list[dict]:
    response = httpx.get(API_URL, headers=HEADERS, timeout=15)
    response.raise_for_status()
    items = response.json().get("data", [])

    today = date.today().isoformat()
    result = []
    for item in items:
        title = item.get("title", "").strip()
        if not title:
            continue

        permalink = item.get("permalink", "")
        url = VACANCY_BASE + permalink + "/" if permalink else ""

        locations = ", ".join(item.get("locationAgr") or [])
        skill = (item.get("skill") or {}).get("title", "")
        levels = ", ".join(t["title"] for t in item.get("techLevels") or [])
        description = " | ".join(filter(None, [levels, skill, locations]))

        result.append({
            "company_name": company_name,
            "title": title,
            "url": url,
            "posted_date": today,
            "description": description,
        })

    return result
