import sys
import feedparser
import requests
from datetime import datetime, timezone, timedelta
from dateutil import parser as dateparser
from typing import Optional

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomllib


def load_feeds(config_path: str = "feeds.toml") -> list[dict]:
    with open(config_path, "rb") as f:
        return tomllib.load(f)["feeds"]


def fetch_feed(feed: dict, lookback_days: int = 1) -> list[dict]:
    """
    Fetch articles from a single RSS feed published within the lookback window.
    Returns a list of article dicts with: title, url, content, source, lang, published_at.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)

    headers = {"User-Agent": "Mozilla/5.0 (compatible; ai-info-aggregator/1.0)"}
    try:
        resp = requests.get(feed["url"], headers=headers, timeout=60)
        resp.raise_for_status()
        parsed = feedparser.parse(resp.content)
    except Exception as e:
        print(f"[WARN] Failed to fetch {feed['name']}: {e}")
        return []

    articles = []
    for entry in parsed.entries:
        published_at = _parse_date(entry)
        if published_at and published_at < cutoff:
            continue

        content = _extract_content(entry)
        title = entry.get("title", "").strip()
        # WeWe RSS feeds return garbled content; fall back to title
        if not content or len(content.strip()) < 100:
            if title:
                content = title
            else:
                continue

        articles.append({
            "title": entry.get("title", "").strip(),
            "url": entry.get("link", ""),
            "content": content[:4000],  # cap to avoid excessive token usage
            "source": feed["name"],
            "lang": feed["lang"],
            "published_at": published_at.isoformat() if published_at else None,
        })

    return articles


def _parse_date(entry) -> Optional[datetime]:
    for field in ("published", "updated", "created"):
        raw = entry.get(field)
        if raw:
            try:
                dt = dateparser.parse(raw)
                if dt and dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except Exception:
                continue
    return None


def _extract_content(entry) -> str:
    # Prefer full content over summary
    if entry.get("content"):
        return entry["content"][0].get("value", "")
    return entry.get("summary", "") or entry.get("description", "")


def fetch_all(config_path: str = "feeds.toml", lookback_days: int = 1) -> list[dict]:
    feeds = load_feeds(config_path)
    all_articles = []
    for feed in feeds:
        articles = fetch_feed(feed, lookback_days)
        print(f"  {feed['name']}: {len(articles)} articles")
        all_articles.extend(articles)
    return all_articles
