import json
import os
from datetime import date
from pathlib import Path

_data_dir = Path(os.environ.get("DATA_DIR", str(Path(__file__).parent)))
_data_dir.mkdir(parents=True, exist_ok=True)
SEEN_FILE = _data_dir / "seen_jobs.json"


def _make_key(job: dict) -> str:
    return f"{job['company_name']}|{job['title']}|{job['posted_date']}"


def _current_month() -> str:
    return date.today().strftime("%Y-%m")


def load_seen() -> dict:
    if not SEEN_FILE.exists():
        return {"_month": _current_month()}
    seen = json.loads(SEEN_FILE.read_text())
    if seen.get("_month") != _current_month():
        return {"_month": _current_month()}
    return seen


def save_seen(seen: dict) -> None:
    seen["_month"] = _current_month()
    SEEN_FILE.write_text(json.dumps(seen, indent=2))


def filter_new_jobs(jobs: list[dict], seen: dict) -> list[dict]:
    return [job for job in jobs if _make_key(job) not in seen]


def mark_as_seen(jobs: list[dict], seen: dict) -> dict:
    updated = dict(seen)
    for job in jobs:
        updated[_make_key(job)] = job.get("url", "")
    return updated
