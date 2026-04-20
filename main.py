#!/usr/bin/env python3
import os
import sys
from datetime import datetime, timezone

from src.feeds import fetch_all
from src.history import (
    filter_unseen,
    load_history,
    prune_history,
    record_pushed,
    save_history,
)
from src.scorer import process_articles
from src.writer import write_output

HISTORY_PATH = "data/pushed.json"
DEDUP_WINDOW_DAYS = 90


def main():
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY environment variable not set.")
        sys.exit(1)

    lookback_days = int(os.environ.get("LOOKBACK_DAYS", "1"))
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    print(f"=== AI Info Aggregator ===")
    print(f"Lookback: {lookback_days} day(s) | Dedup window: {DEDUP_WINDOW_DAYS} day(s)\n")

    print("[Fetching RSS feeds...]")
    articles = fetch_all("feeds.toml", lookback_days=lookback_days)
    print(f"Total fetched: {len(articles)} articles")

    history = load_history(HISTORY_PATH)
    print(f"Loaded history: {len(history)} entries")

    articles, skipped = filter_unseen(articles, history, days=DEDUP_WINDOW_DAYS, today=today)
    print(f"Skipped {len(skipped)} already-pushed articles; {len(articles)} remaining\n")

    if not articles:
        print("No new articles after history dedup. Exiting.")
        sys.exit(0)

    kept, rejected = process_articles(articles, api_key)

    if not kept:
        print("\nNo articles passed the quality filter today.")

    path = write_output(kept, output_dir="output")
    print(f"\nDone. Output written to: {path}")
    print(f"Final digest: {len(kept)} articles | Rejected: {len(rejected)} articles")

    history = record_pushed(history, kept, today=today)
    history = prune_history(history, days=DEDUP_WINDOW_DAYS, today=today)
    save_history(HISTORY_PATH, history)
    print(f"History updated: {len(history)} entries retained")


if __name__ == "__main__":
    main()
