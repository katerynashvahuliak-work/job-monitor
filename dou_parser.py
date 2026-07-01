"""DOU HTML parser using BeautifulSoup."""

import re
from datetime import date

from bs4 import BeautifulSoup

MONTH_MAP = {
    "січня": "01", "лютого": "02", "березня": "03", "квітня": "04",
    "травня": "05", "червня": "06", "липня": "07", "серпня": "08",
    "вересня": "09", "жовтня": "10", "листопада": "11", "грудня": "12",
}

_DATE_RE = re.compile(r"(\d+)\s+(\w+)")


def _parse_date(text: str) -> str:
    m = _DATE_RE.search(text)
    if not m:
        return date.today().isoformat()
    day, month_word = m.group(1), m.group(2).lower()
    month = MONTH_MAP.get(month_word)
    if not month:
        return date.today().isoformat()
    year = date.today().year
    return f"{year}-{month}-{day.zfill(2)}"


def _is_location(text: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-zА-Яа-яІіЇїЄєҐґ'\-\s,]+", text.strip()))


def parse_dou_vacancies(html: str, company_name: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")

    vacancy_anchors = soup.find_all(
        "a",
        href=lambda h: h and h.startswith("https://jobs.dou.ua/companies/") and "/vacancies/" in h,
    )

    results = []
    seen_urls: set[str] = set()

    for a_tag in vacancy_anchors:
        li = a_tag.find_parent("li")
        if li is None:
            continue

        title = a_tag.get_text(strip=True)
        if not title:
            continue

        url = a_tag["href"].split("?")[0]
        if url in seen_urls:
            continue
        seen_urls.add(url)

        # Find date text node before the <a> tag
        posted_date = date.today().isoformat()
        for child in li.children:
            if child == a_tag:
                break
            if isinstance(child, str) and _DATE_RE.search(child):
                posted_date = _parse_date(child)
                break

        # Collect description: all text chunks except title and date node
        description = ""
        for chunk in li.stripped_strings:
            if chunk == title:
                continue
            if _DATE_RE.fullmatch(chunk.strip()):
                continue
            if _is_location(chunk) and len(chunk) < 60:
                continue
            if len(chunk) > 20:
                description = chunk
                break

        results.append({
            "company_name": company_name,
            "title": title,
            "url": url,
            "posted_date": posted_date,
            "description": description,
        })

    return results
