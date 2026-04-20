import json
from pathlib import Path

from src.history import filter_unseen, load_history, prune_history, record_pushed, save_history


def test_load_history_returns_empty_list_when_file_missing(tmp_path):
    missing = tmp_path / "nope.json"
    assert load_history(str(missing)) == []


def test_load_history_returns_pushed_list_when_file_exists(tmp_path):
    path = tmp_path / "pushed.json"
    data = {
        "pushed": [
            {"url": "https://a.com", "pushed_at": "2026-04-01", "title": "A", "score": 8}
        ]
    }
    path.write_text(json.dumps(data), encoding="utf-8")
    result = load_history(str(path))
    assert result == data["pushed"]


def test_load_history_returns_empty_list_when_file_is_malformed(tmp_path):
    path = tmp_path / "pushed.json"
    path.write_text("{ not valid json", encoding="utf-8")
    assert load_history(str(path)) == []


def test_filter_unseen_keeps_all_when_history_empty():
    articles = [{"url": "https://a.com", "title": "A"}]
    unseen, skipped = filter_unseen(articles, history=[], days=90, today="2026-04-21")
    assert unseen == articles
    assert skipped == []


def test_filter_unseen_skips_recent_match():
    articles = [{"url": "https://a.com", "title": "A"}]
    history = [{"url": "https://a.com", "pushed_at": "2026-04-15", "title": "A", "score": 8}]
    unseen, skipped = filter_unseen(articles, history, days=90, today="2026-04-21")
    assert unseen == []
    assert skipped == articles


def test_filter_unseen_ignores_expired_match():
    articles = [{"url": "https://a.com", "title": "A"}]
    history = [{"url": "https://a.com", "pushed_at": "2025-12-01", "title": "A", "score": 8}]
    unseen, skipped = filter_unseen(articles, history, days=90, today="2026-04-21")
    assert unseen == articles
    assert skipped == []


def test_filter_unseen_exact_boundary_is_still_within_window():
    # 90 天前 == 窗口内
    articles = [{"url": "https://a.com", "title": "A"}]
    history = [{"url": "https://a.com", "pushed_at": "2026-01-21", "title": "A", "score": 8}]
    unseen, skipped = filter_unseen(articles, history, days=90, today="2026-04-21")
    assert skipped == articles


def test_filter_unseen_handles_mix():
    articles = [
        {"url": "https://a.com", "title": "A"},
        {"url": "https://b.com", "title": "B"},
        {"url": "https://c.com", "title": "C"},
    ]
    history = [
        {"url": "https://a.com", "pushed_at": "2026-04-10", "title": "A", "score": 8},
        {"url": "https://c.com", "pushed_at": "2025-01-01", "title": "C", "score": 7},
    ]
    unseen, skipped = filter_unseen(articles, history, days=90, today="2026-04-21")
    unseen_urls = {a["url"] for a in unseen}
    skipped_urls = {a["url"] for a in skipped}
    assert unseen_urls == {"https://b.com", "https://c.com"}
    assert skipped_urls == {"https://a.com"}


def test_record_pushed_appends_new_entries():
    history = [
        {"url": "https://old.com", "pushed_at": "2026-04-01", "title": "Old", "score": 7}
    ]
    articles = [
        {"url": "https://new.com", "title": "New", "score": 8},
        {"url": "https://new2.com", "title": "New2", "score": 9},
    ]
    updated = record_pushed(history, articles, today="2026-04-21")
    assert len(updated) == 3
    assert updated[-2] == {
        "url": "https://new.com",
        "pushed_at": "2026-04-21",
        "title": "New",
        "score": 8,
    }
    assert updated[-1]["url"] == "https://new2.com"


def test_record_pushed_empty_articles_returns_history_unchanged():
    history = [
        {"url": "https://old.com", "pushed_at": "2026-04-01", "title": "Old", "score": 7}
    ]
    updated = record_pushed(history, [], today="2026-04-21")
    assert updated == history


def test_record_pushed_does_not_mutate_input_history():
    history = [
        {"url": "https://old.com", "pushed_at": "2026-04-01", "title": "Old", "score": 7}
    ]
    original = list(history)
    record_pushed(history, [{"url": "https://new.com", "title": "N", "score": 8}], "2026-04-21")
    assert history == original


def test_prune_history_drops_expired_entries():
    history = [
        {"url": "https://old.com", "pushed_at": "2025-01-01", "title": "Old", "score": 7},
        {"url": "https://new.com", "pushed_at": "2026-04-10", "title": "New", "score": 8},
    ]
    pruned = prune_history(history, days=90, today="2026-04-21")
    assert len(pruned) == 1
    assert pruned[0]["url"] == "https://new.com"


def test_prune_history_keeps_exact_boundary():
    history = [
        {"url": "https://edge.com", "pushed_at": "2026-01-21", "title": "Edge", "score": 8}
    ]
    pruned = prune_history(history, days=90, today="2026-04-21")
    assert len(pruned) == 1


def test_prune_history_drops_entries_with_malformed_date():
    history = [
        {"url": "https://bad.com", "pushed_at": "not-a-date", "title": "Bad", "score": 5},
        {"url": "https://good.com", "pushed_at": "2026-04-10", "title": "Good", "score": 8},
    ]
    pruned = prune_history(history, days=90, today="2026-04-21")
    urls = {e["url"] for e in pruned}
    assert urls == {"https://good.com"}


def test_save_history_writes_pushed_wrapper(tmp_path):
    path = tmp_path / "sub" / "pushed.json"
    entries = [
        {"url": "https://a.com", "pushed_at": "2026-04-21", "title": "A", "score": 8}
    ]
    save_history(str(path), entries)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data == {"pushed": entries}


def test_save_history_roundtrips_with_load_history(tmp_path):
    path = tmp_path / "pushed.json"
    entries = [
        {"url": "https://a.com", "pushed_at": "2026-04-21", "title": "A", "score": 8},
        {"url": "https://b.com", "pushed_at": "2026-04-20", "title": "B", "score": 9},
    ]
    save_history(str(path), entries)
    assert load_history(str(path)) == entries
