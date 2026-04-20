import json
import os
from datetime import datetime, timedelta


def load_history(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("pushed", [])
    except (json.JSONDecodeError, OSError):
        return []


def filter_unseen(
    articles: list[dict],
    history: list[dict],
    days: int,
    today: str,
) -> tuple[list[dict], list[dict]]:
    """Return (unseen, skipped).

    An article is 'skipped' if its URL appears in history with pushed_at within
    the last `days` days relative to `today` (YYYY-MM-DD).
    """
    today_dt = datetime.strptime(today, "%Y-%m-%d")
    cutoff = today_dt - timedelta(days=days)

    recent_urls = set()
    for entry in history:
        url = entry.get("url")
        pushed_at = entry.get("pushed_at")
        if not url or not pushed_at:
            continue
        try:
            pushed_dt = datetime.strptime(pushed_at, "%Y-%m-%d")
        except ValueError:
            continue
        if pushed_dt >= cutoff:
            recent_urls.add(url)

    unseen = [a for a in articles if a.get("url") not in recent_urls]
    skipped = [a for a in articles if a.get("url") in recent_urls]
    return unseen, skipped


def record_pushed(history: list[dict], articles: list[dict], today: str) -> list[dict]:
    """Return a new history list with entries for each article appended."""
    new_entries = [
        {
            "url": a.get("url", ""),
            "pushed_at": today,
            "title": a.get("title", ""),
            "score": a.get("score", 0),
        }
        for a in articles
    ]
    return list(history) + new_entries
