from datetime import datetime, timezone
from collections import defaultdict

TOPIC_ORDER = [
    "AI新技术/新模型",
    "OPC/AI赚钱案例",
    "AI+电商",
    "AI工具实操/Prompt技巧",
    "AI Agent/自动化工作流",
    "AI对行业的冲击",
    "AI投融资动态",
]


def generate_markdown(articles: list[dict], date: str) -> str:
    """
    Generate a daily digest Markdown string.
    Articles are grouped by topic, sorted by score descending within each group.
    """
    by_topic = defaultdict(list)
    for a in articles:
        by_topic[a["topic"]].append(a)

    lines = [
        "---",
        f"date: {date}",
        "tags: [ai-daily]",
        "---",
        "",
    ]

    has_content = False
    for topic in TOPIC_ORDER:
        group = by_topic.get(topic)
        if not group:
            continue
        has_content = True
        group.sort(key=lambda x: x["score"], reverse=True)

        lines.append(f"## {topic}")
        lines.append("")

        for a in group:
            tags_str = " ".join(f"`#{t}`" for t in a.get("tags", []))
            lines.append(f"### [{a['title']}]({a['url']})")
            lines.append(f"- **来源**：{a['source']}")
            lines.append(f"- **评分**：{a['score']}/10")
            if tags_str:
                lines.append(f"- **标签**：{tags_str}")
            if a.get("summary"):
                lines.append(f"- **摘要**：{a['summary']}")
            lines.append("")
            lines.append("---")
            lines.append("")

    if not has_content:
        lines.append("_今日暂无符合标准的内容。_")

    return "\n".join(lines)


def write_output(articles: list[dict], output_dir: str = "output") -> str:
    """Write the daily digest to output_dir/AI Daily - YYYY-MM-DD.md. Returns file path."""
    import os
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    content = generate_markdown(articles, date)

    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"AI Daily - {date}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return path


def write_rejected(articles: list[dict], output_dir: str = "output") -> str:
    """Write rejected articles log for scoring verification."""
    import os
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"AI Daily - {date} - rejected.md")

    lines = [
        "---",
        f"date: {date}",
        "tags: [ai-daily-debug]",
        "---",
        "",
        f"# 淘汰记录 {date}",
        "",
        f"共 {len(articles)} 篇，评分 <7 或主题无关。",
        "",
    ]

    # Sort by score descending so borderline cases are easy to review
    for a in sorted(articles, key=lambda x: x.get("score", 0), reverse=True):
        score = a.get("score", "?")
        topic = a.get("topic", "未分类")
        lines.append(f"- **{score}/10** [{a['title']}]({a['url']})  ")
        lines.append(f"  来源：{a['source']} | 主题：{topic}")
        lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return path
