import json
from pathlib import Path

SEEN_FILE = Path(__file__).parent / "seen_jobs.json"


def _make_key(job: dict) -> str:
    return f"{job['company_name']}|{job['title']}|{job['posted_date']}"


def load_seen() -> dict:
    if not SEEN_FILE.exists():
        return {}
    return json.loads(SEEN_FILE.read_text())


def save_seen(seen: dict) -> None:
    SEEN_FILE.write_text(json.dumps(seen, indent=2))


def filter_new_jobs(jobs: list[dict], seen: dict) -> list[dict]:
    return [job for job in jobs if _make_key(job) not in seen]


def mark_as_seen(jobs: list[dict], seen: dict) -> dict:
    updated = dict(seen)
    for job in jobs:
        updated[_make_key(job)] = job.get("url", "")
    return updated
