# 历史推送去重（90 天窗口）实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 过滤掉 90 天内已推送过的 URL，避免老内容被算法翻炒后重复进入日报。

**Architecture:** 新增一个 `src/history.py` 模块，在 `main.py` 中于 `process_articles` 之前按 URL 过滤输入、之后记录本次推送结果。历史存储为仓库内的 `data/pushed.json`，由 GitHub Actions 和 `output/` 一起 commit 回仓库。过滤发生在评分之前，省掉重复文章的 Haiku 评分成本。

**Tech Stack:** Python 3.11, pytest (新引入), 标准库 json + datetime (无新依赖)。

---

## 背景上下文（执行者必读）

项目是一个每日自动抓取 AI 内容、Claude 评分筛选、生成 Obsidian 日报的 GitHub Actions 工作流。现有代码结构：

- `main.py`：入口，顺序调用 fetch → process → write
- `src/feeds.py`：从 RSS 抓取，文章 dict 结构 `{title, url, content, source, lang, published_at}`
- `src/scorer.py`：`process_articles(articles, api_key)` 内部顺序为
  1. `score_article` (Haiku) — 给每篇 0-10 分，判定 keep
  2. `dedup_articles` (Haiku) — 同批次内同一事件去重
  3. `summarize_article` (Sonnet) — 给 kept 的文章生成摘要
- `src/writer.py`：`write_output(kept)` 生成 `output/AI Daily - YYYY-MM-DD.md`
- `.github/workflows/daily.yml`：每天 UTC 01:00 跑一次，`git add output/` 后 commit+push

**关键约束**：GitHub Actions 无持久存储，所有状态必须 commit 回仓库才能跨天保留。

**为什么过滤要放在 `process_articles` 之前**：评分是最大头的 API 成本（每篇都调 Haiku），过滤放在评分前，重复 URL 直接跳过，一分钱不花。

---

## File Structure

**新建文件：**

- `src/history.py` — 纯函数模块：load/filter/record/prune/save 历史
- `tests/__init__.py` — 空文件，让 pytest 识别 tests 包
- `tests/test_history.py` — `src/history.py` 的单元测试
- `data/.gitkeep` — 占位文件，保证空目录被 git 追踪

**修改文件：**

- `main.py` — 在 fetch 后过滤历史；在 process 后记录历史
- `requirements.txt` — 添加 `pytest`
- `.github/workflows/daily.yml` — commit 时也 add `data/`
- `.gitignore` — 不忽略 `data/`（明确一下，虽然默认就不忽略）
- `README.md` — 在"特性"一节补上 90 天 URL 去重说明

**数据结构**（`data/pushed.json`）：

```json
{
  "pushed": [
    {
      "url": "https://example.com/article",
      "pushed_at": "2026-04-21",
      "title": "文章标题",
      "score": 8
    }
  ]
}
```

- `url` + `pushed_at` 是 load-bearing 字段
- `title` + `score` 仅用于调试可读性，不参与逻辑

---

## Task 1: 搭建 pytest 环境

**Files:**
- Modify: `requirements.txt`
- Create: `tests/__init__.py`
- Create: `tests/test_smoke.py`

- [ ] **Step 1: 添加 pytest 到 requirements.txt**

在 `requirements.txt` 末尾追加：

```
pytest>=8.0
```

- [ ] **Step 2: 创建空的 tests 包**

创建 `tests/__init__.py`（内容为空）。

- [ ] **Step 3: 写一个 smoke test 验证 pytest 可用**

创建 `tests/test_smoke.py`：

```python
def test_pytest_is_working():
    assert 1 + 1 == 2
```

- [ ] **Step 4: 安装依赖并运行 smoke test**

```bash
pip install -r requirements.txt
pytest tests/test_smoke.py -v
```

Expected: `1 passed`

- [ ] **Step 5: Commit**

```bash
git add requirements.txt tests/__init__.py tests/test_smoke.py
git commit -m "chore: add pytest for unit testing"
```

---

## Task 2: `load_history` — 读取历史文件

**Files:**
- Create: `src/history.py`
- Create: `tests/test_history.py`

- [ ] **Step 1: 写失败测试（文件不存在返回空列表；文件存在返回解析后的列表）**

创建 `tests/test_history.py`：

```python
import json
from pathlib import Path

from src.history import load_history


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
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
pytest tests/test_history.py -v
```

Expected: `ImportError: cannot import name 'load_history' from 'src.history'`（或文件不存在错误）

- [ ] **Step 3: 写最小实现**

创建 `src/history.py`：

```python
import json
import os


def load_history(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("pushed", [])
    except (json.JSONDecodeError, OSError):
        return []
```

- [ ] **Step 4: 运行测试，确认通过**

```bash
pytest tests/test_history.py -v
```

Expected: `3 passed`

- [ ] **Step 5: Commit**

```bash
git add src/history.py tests/test_history.py
git commit -m "feat(history): add load_history"
```

---

## Task 3: `filter_unseen` — 过滤 90 天内已推送的 URL

**Files:**
- Modify: `src/history.py`
- Modify: `tests/test_history.py`

- [ ] **Step 1: 写失败测试**

在 `tests/test_history.py` 末尾追加：

```python
from src.history import filter_unseen


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
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
pytest tests/test_history.py -v
```

Expected: `ImportError: cannot import name 'filter_unseen'`

- [ ] **Step 3: 写实现**

在 `src/history.py` 末尾追加：

```python
from datetime import datetime, timedelta


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
```

- [ ] **Step 4: 运行测试，确认通过**

```bash
pytest tests/test_history.py -v
```

Expected: `8 passed`（3 旧 + 5 新）

- [ ] **Step 5: Commit**

```bash
git add src/history.py tests/test_history.py
git commit -m "feat(history): add filter_unseen with configurable window"
```

---

## Task 4: `record_pushed` — 追加本次推送到历史

**Files:**
- Modify: `src/history.py`
- Modify: `tests/test_history.py`

- [ ] **Step 1: 写失败测试**

在 `tests/test_history.py` 末尾追加：

```python
from src.history import record_pushed


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
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
pytest tests/test_history.py -v
```

Expected: `ImportError: cannot import name 'record_pushed'`

- [ ] **Step 3: 写实现**

在 `src/history.py` 末尾追加：

```python
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
```

- [ ] **Step 4: 运行测试，确认通过**

```bash
pytest tests/test_history.py -v
```

Expected: `11 passed`

- [ ] **Step 5: Commit**

```bash
git add src/history.py tests/test_history.py
git commit -m "feat(history): add record_pushed"
```

---

## Task 5: `prune_history` — 丢弃超过 90 天的条目

**Files:**
- Modify: `src/history.py`
- Modify: `tests/test_history.py`

- [ ] **Step 1: 写失败测试**

在 `tests/test_history.py` 末尾追加：

```python
from src.history import prune_history


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
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
pytest tests/test_history.py -v
```

Expected: `ImportError: cannot import name 'prune_history'`

- [ ] **Step 3: 写实现**

在 `src/history.py` 末尾追加：

```python
def prune_history(history: list[dict], days: int, today: str) -> list[dict]:
    """Drop entries whose pushed_at is older than `days` days before `today`."""
    today_dt = datetime.strptime(today, "%Y-%m-%d")
    cutoff = today_dt - timedelta(days=days)

    kept = []
    for entry in history:
        pushed_at = entry.get("pushed_at")
        if not pushed_at:
            continue
        try:
            pushed_dt = datetime.strptime(pushed_at, "%Y-%m-%d")
        except ValueError:
            continue
        if pushed_dt >= cutoff:
            kept.append(entry)
    return kept
```

- [ ] **Step 4: 运行测试，确认通过**

```bash
pytest tests/test_history.py -v
```

Expected: `14 passed`

- [ ] **Step 5: Commit**

```bash
git add src/history.py tests/test_history.py
git commit -m "feat(history): add prune_history"
```

---

## Task 6: `save_history` — 原子写入 JSON

**Files:**
- Modify: `src/history.py`
- Modify: `tests/test_history.py`

- [ ] **Step 1: 写失败测试**

在 `tests/test_history.py` 末尾追加：

```python
from src.history import save_history


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
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
pytest tests/test_history.py -v
```

Expected: `ImportError: cannot import name 'save_history'`

- [ ] **Step 3: 写实现**

在 `src/history.py` 末尾追加：

```python
def save_history(path: str, history: list[dict]) -> None:
    """Write history to path, creating parent dirs as needed."""
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"pushed": history}, f, ensure_ascii=False, indent=2)
```

- [ ] **Step 4: 运行测试，确认通过**

```bash
pytest tests/test_history.py -v
```

Expected: `16 passed`

- [ ] **Step 5: Commit**

```bash
git add src/history.py tests/test_history.py
git commit -m "feat(history): add save_history"
```

---

## Task 7: 集成进 main.py

**Files:**
- Modify: `main.py`
- Create: `data/.gitkeep`

- [ ] **Step 1: 创建 data 目录占位文件**

```bash
mkdir -p data
touch data/.gitkeep
```

- [ ] **Step 2: 修改 main.py 接入历史去重**

把 `main.py` 整体改写为：

```python
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
```

- [ ] **Step 3: 本地 dry-run（不调 API，只跑 fetch + history 逻辑）**

由于完整跑会烧钱，先手动校验 import 和语法：

```bash
python -c "import main; print('imports ok')"
```

Expected: `imports ok`

然后跑一次完整测试套件确认没破东西：

```bash
pytest -v
```

Expected: `17 passed`（16 history + 1 smoke）

- [ ] **Step 4: 初始化空历史文件**

```bash
python -c "from src.history import save_history; save_history('data/pushed.json', [])"
cat data/pushed.json
```

Expected: `{"pushed": []}`

- [ ] **Step 5: Commit**

```bash
git add main.py data/.gitkeep data/pushed.json
git commit -m "feat: wire 90-day URL dedup into main pipeline"
```

---

## Task 8: GitHub Actions 也 commit data 目录

**Files:**
- Modify: `.github/workflows/daily.yml`

- [ ] **Step 1: 修改 commit 步骤同时包含 data/**

将 daily.yml 第 33-39 行的 Commit output 步骤改为：

```yaml
      - name: Commit output
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add output/ data/
          git diff --cached --quiet || git commit -m "daily digest $(date -u +%Y-%m-%d)"
          git push
```

（唯一改动：`git add output/` → `git add output/ data/`）

- [ ] **Step 2: 验证 yaml 合法**

```bash
python -c "import yaml; yaml.safe_load(open('.github/workflows/daily.yml'))"
```

Expected: 无输出，无报错

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/daily.yml
git commit -m "ci: commit data/ alongside output/ for history persistence"
```

---

## Task 9: 更新 README 说明新行为

**Files:**
- Modify: `README.md`

- [ ] **Step 1: 找到现有"特性"小节**

在 README.md 中找到如下行：

```
- **自动去重**：同一事件多个来源只保留最高分版本
```

- [ ] **Step 2: 在其下方追加一条新特性**

替换为：

```
- **自动去重**：同一事件多个来源只保留最高分版本
- **历史去重**：90 天内已推送过的 URL 自动跳过，避免算法翻炒老内容
```

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: document 90-day history dedup"
```

---

## Task 10: 端到端验收 + 推送到远端

**Files:** 无代码改动

- [ ] **Step 1: 跑一次完整测试**

```bash
pytest -v
```

Expected: 全部 passed

- [ ] **Step 2: 验证 git status 干净、仓库状态正确**

```bash
git status
git log --oneline -10
```

Expected：
- status 无未提交改动
- log 中能看到 Task 1-9 对应的 9 个 commit

- [ ] **Step 3: 验证新结构确实存在**

```bash
ls data/ tests/ src/history.py
```

Expected: 三个都存在

- [ ] **Step 4: 推送到远端**

```bash
git push origin main
```

- [ ] **Step 5: 手动触发一次 GitHub Actions 验证线上生效**

在仓库页面打开 Actions → Daily AI Digest → Run workflow。

等跑完后检查：
1. Actions log 中出现 `Loaded history: 0 entries` 和 `Skipped 0 already-pushed articles`（第一次跑历史为空）
2. 仓库里新增 `data/pushed.json`，且 `pushed` 数组非空
3. 第二天（或再次手动触发）的 log 中 `Loaded history: N entries`，N 等于昨天 kept 的数量
4. 第二次触发如果命中重复，`Skipped X` 应该 > 0

验收通过后本任务完成。

---

## Self-Review Notes

- **Spec 覆盖**：用户需求 = "30 天内已推送过的就不再推送"，讨论后调整为 "90 天 URL 维度去重"。Task 3 `filter_unseen` 实现核心过滤；Task 5 `prune_history` 保持历史文件不膨胀；Task 7 把三者接入 pipeline。覆盖完整。
- **成本承诺**：用户问过会不会增加成本。实际上过滤在 `process_articles` 之前发生（main.py step 2），重复 URL 根本不进入评分步骤。无新 API 调用，符合"降低成本"承诺。
- **GitHub Actions 持久化**：Task 8 确保 `data/pushed.json` 被 commit 回仓库，否则每次跑都是空历史，去重形同虚设。
- **边界条件**：Task 3/5 的测试覆盖了"恰好 90 天前"（保留）、"91 天前"（丢弃）、格式错误的日期（忽略）。
- **幂等**：`filter_unseen` 和 `prune_history` 都是纯函数返回新 list，不 mutate 输入。
