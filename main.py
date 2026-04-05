#!/usr/bin/env python3
import os
import sys

from src.feeds import fetch_all
from src.scorer import process_articles
from src.writer import write_output


def main():
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY environment variable not set.")
        sys.exit(1)

    lookback_days = int(os.environ.get("LOOKBACK_DAYS", "1"))

    print(f"=== AI Info Aggregator ===")
    print(f"Lookback: {lookback_days} day(s)\n")

    print("[Fetching RSS feeds...]")
    articles = fetch_all("feeds.toml", lookback_days=lookback_days)
    print(f"Total fetched: {len(articles)} articles\n")

    if not articles:
        print("No articles found. Exiting.")
        sys.exit(0)

    kept, rejected = process_articles(articles, api_key)

    if not kept:
        print("\nNo articles passed the quality filter today.")

    path = write_output(kept, output_dir="output")
    print(f"\nDone. Output written to: {path}")
    print(f"Final digest: {len(kept)} articles | Rejected: {len(rejected)} articles")


if __name__ == "__main__":
    main()
