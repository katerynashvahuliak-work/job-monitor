import logging
import sys
from datetime import datetime

from altexsoft_parser import fetch_altexsoft_vacancies
from config import CLIENTS, SLACK_WEBHOOK_URL
from dou_parser import parse_dou_vacancies
from extractor import extract_jobs, filter_ml_jobs
from fetcher import fetch_html, fetch_page
from notifier import send_slack_report
from reporter import generate_report
from storage import filter_new_jobs, load_seen, mark_as_seen, save_seen

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def ts() -> str:
    return datetime.now().strftime("%H:%M:%S")


def _fetch_paginated(base_url: str, company_name: str) -> list[dict]:
    all_jobs: list[dict] = []
    seen_titles: set[str] = set()
    for page_num in range(1, 21):
        page_url = base_url if page_num == 1 else base_url.rstrip("/") + f"/page/{page_num}/"
        if page_num > 1:
            print(f"[{ts()}]   → page {page_num}")
        try:
            page_text = fetch_page(page_url)
            page_jobs = extract_jobs(page_text, company_name)
        except Exception:
            break
        new_on_page = [j for j in page_jobs if j["title"] not in seen_titles]
        if not new_on_page:
            break
        seen_titles.update(j["title"] for j in new_on_page)
        all_jobs.extend(new_on_page)
    return all_jobs


def main() -> None:
    print(f"[{ts()}] Starting Job Monitor Agent")

    seen = load_seen()
    all_new_jobs: list[dict] = []

    for client in CLIENTS:
        name = client["name"]
        url = client.get("url", "")

        print(f"[{ts()}] Fetching {name}...")
        try:
            if client["source_type"] == "dou":
                html = fetch_html(url)
                raw_jobs = parse_dou_vacancies(html, name)
            elif client["source_type"] == "altexsoft":
                raw_jobs = fetch_altexsoft_vacancies(name)
            else:
                raw_jobs = _fetch_paginated(url, name)
        except Exception as e:
            logger.error("Failed to fetch/extract %s: %s", name, e)
            continue

        new_jobs = filter_new_jobs(raw_jobs, seen)
        print(f"[{ts()}] {len(new_jobs)} new job(s) found at {name}")
        all_new_jobs.extend(new_jobs)

    if not all_new_jobs:
        print(f"[{ts()}] No new jobs found. Exiting.")
        save_seen(seen)
        sys.exit(0)

    print(f"[{ts()}] Filtering {len(all_new_jobs)} jobs for ML/AI relevance...")
    ml_jobs = filter_ml_jobs(all_new_jobs)
    print(f"[{ts()}] {len(ml_jobs)} ML/AI relevant job(s) found")

    seen = mark_as_seen(all_new_jobs, seen)
    save_seen(seen)

    generate_report(ml_jobs)
    send_slack_report(ml_jobs, SLACK_WEBHOOK_URL)

    from datetime import date
    today = date.today().isoformat()
    print(f"[{ts()}] Done. Report saved to reports/{today}_report.md")


if __name__ == "__main__":
    main()
