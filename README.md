# 优质信息自动抓取

AI 主题信息捕捉器 — 每日从中英文互联网抓取 AI 相关内容，AI 提炼要点后推送至 Obsidian。

## 核心需求

- **内容方向**：AI 新技术动态 + 一人公司/OPC 通过 AI 赚钱的案例和实操
- **每日数量**：初期 10 条，可动态调整
- **输出形式**：Obsidian 文档，每日一份，含 AI 摘要
- **用途**：了解趋势 + 沉淀为"创业项目灵感库"

---

## 关注主题方向

按优先级排序：

| 优先级 | 方向 | 说明 |
|--------|------|------|
| ⭐⭐⭐ | OPC / AI 赚钱案例 | 一人公司通过 AI 实现收入的具体案例和路径 |
| ⭐⭐⭐ | AI + 电商 | AI 用于选品/广告/客服/独立站/工作流/提示词等任意电商环节 |
| ⭐⭐⭐ | AI 工具实操 / Agent 工作流 | 实操教程、prompt 技巧、自动化工作流落地案例 |
| ⭐⭐⭐ | AI 新技术 / 新模型 | 模型发布、benchmark、技术突破 |
| ⭐⭐ | AI 投融资动态 | 钱流向哪里，趋势就在哪里 |
| ⭐⭐ | AI 对行业的冲击 | 判断机会与风险 |

---

## 信息源

### 当前已启用（feeds.toml）

| 类别 | 来源 | 语言 | 状态 |
|------|------|------|------|
| OPC 案例 | Indie Hackers | EN | ✅ |
| OPC 案例 | Starter Story | EN | ✅ |
| OPC 案例 | Reddit r/SideProject | EN | ✅ |
| AI Newsletter | Ben's Bites | EN | ✅ |
| AI Newsletter | TLDR AI | EN | ✅ |
| AI Newsletter | The Batch (deeplearning.ai) | EN | ✅ |
| AI Newsletter | Latent Space | EN | ✅ |
| AI Newsletter | Lenny's Newsletter | EN | ✅ |
| AI 技术 | Simon Willison's Blog | EN | ✅ |
| AI 技术 | Hugging Face Blog | EN | ✅ |
| AI 技术 | Hacker News Show HN | EN | ✅ |
| AI 技术 | Reddit r/LocalLLaMA | EN | ✅ |
| AI 技术 | GitHub Trending | EN | ✅ (阈值 ≥6) |
| 科技媒体 | VentureBeat AI | EN | ✅ |
| 科技媒体 | TechCrunch AI | EN | ✅ |
| 科技媒体 | MIT Technology Review AI | EN | ✅ |
| 商业趋势 | Trends.vc | EN | ✅ |
| 产品动态 | Product Hunt | EN | ✅ |
| AI + 电商 | Practical Ecommerce | EN | ✅ |
| AI + 电商 | Shopify Blog | EN | ✅ |
| AI + 电商 | Marketing AI Institute | EN | ✅ |
| AI + 电商 | Search Engine Journal (Ecommerce) | EN | ✅ |
| AI + 电商 | eCommerceFuel | EN | ✅ |
| AI 新闻 | 量子位 | ZH | ✅ |
| AI 新闻 | 机器之心 | ZH | ✅ |
| 科技媒体 | 36氪 | ZH | ✅ |
| 工具评测 | 少数派 | ZH | ✅ |
| 科技媒体 | 爱范儿 | ZH | ✅ |
| 科技媒体 | 极客公园 | ZH | ✅ |

### 待加入 / 备选信息源

| 来源 | 类别 | 语言 | 说明 | 状态 |
|------|------|------|------|------|
| 虎嗅 | 科技媒体 | ZH | 质量好，但服务器反爬超时 | ⚠️ 待解决 |
| 晚点 LatePost | 科技媒体 | ZH | 深度报道质量高 | ⚠️ 待验证 RSS |
| 亿邦动力 | AI + 电商 | ZH | 电商行业专业媒体 | ⚠️ 待验证 RSS |
| Klaviyo Blog | AI + 电商 | EN | 邮件营销 + AI，电商相关 | ⚠️ 待验证 RSS |
| r/Entrepreneur | OPC 案例 | EN | Reddit 创业社区 | 📋 待加入 |
| eCommerceBytes | AI + 电商 | EN | 电商行业新闻 | 📋 待加入 |
| 即刻（爱范儿/硅星人） | 科技速报 | ZH | RSSHub 可抓，但不稳定 | ⚠️ 有限 |
| B站 | 视频平台 | ZH | RSSHub 可抓特定 UP 主 | 📋 待加入 |
| 知乎 | 问答社区 | ZH | RSSHub 可抓特定话题 | 📋 待加入 |
| 微信公众号 | 公众号 | ZH | RSSHub 部分支持 | ⚠️ 有限 |
| 小红书 / 抖音 | 短视频 | ZH | 暂无可靠方案 | ❌ |
| X/Twitter | 社交媒体 | EN/ZH | 需 API Key，follow-builders 项目单独处理 | — |

---

## AI Prompt 设计

### Prompt 1：筛选 + 评分（每篇文章执行一次，Claude Haiku）

```
你是一个 AI 信息策展人。请分析以下文章，判断它是否值得推送给一个关注 AI 趋势和一人公司创业的读者。

文章标题：{title}
文章内容：{content}

请按以下 JSON 格式输出：
{
  "topic": "主题分类（从以下选一个）：OPC/AI赚钱案例 | AI+电商 | AI工具实操/Agent工作流 | AI新技术/新模型 | AI投融资动态 | AI对行业的冲击 | 无关",
  "score": 评分(0-10，整数),
  "tags": ["标签1", "标签2"],
  "keep": true或false
}

评分标准（信息密度 × 可操作性）：
有具体事实（数字/产品名/技术名）才有信息密度；读完之后能做某件事或做更好的判断，才有可操作性。
泛泛观点、营销软文、无数据的预测，直接 ≤4 分。

按主题的高分门槛：

▸ OPC / AI 赚钱案例（得 8+ 分须满足）：
  - 有具体收入数字（月收入/年收入/ARR）
  - 有产品/服务形态描述
  - 有获客方式或冷启动路径
  缺收入数字 → 最高 6 分；缺其余任意一项 → 降 1 分

▸ AI + 电商（得 8+ 分须满足）：
  - 内容涵盖：AI 工具用于电商选品/广告/客服/独立站/内容生成/工作流/提示词等任意环节
  - 有具体工具名、操作步骤、效果数据或案例
  - 信息层面（行业动态）、实用技巧、新产品、工作流、提示词均视为高价值
  泛泛的"AI 将改变电商"无数据 → 最高 4 分

▸ AI 工具实操 / Agent 工作流（得 8+ 分须满足）：
  - 工具实操类：有可直接复用的 prompt 或操作步骤，有效果对比
  - Agent/工作流类：有具体工具组合或架构描述，有实际效果或成本数据
  - GitHub 开源项目：有明确功能描述和使用场景即可
  只有概念介绍、无落地内容 → 最高 5 分

▸ AI 新技术 / 新模型（得 8+ 分须满足）：
  - 有具体 benchmark 数据或与现有模型的对比
  - 有 API 可用性、定价或开源状态
  - 有实际能力演示或用户反馈
  缺以上任意两项 → 降 2 分

▸ AI 对行业的冲击（得 8+ 分须满足）：
  - 有具体行业 + 具体影响数据（就业/效率/市场规模）
  - 有机会或风险的可操作结论
  纯观点预测无数据 → 最高 5 分

▸ AI 投融资动态（得 8+ 分须满足）：
  - 有融资金额 + 投资方 + 业务方向
  - 有估值或与上轮对比
  缺金额 → 最高 6 分

通用扣分项：
- 明显是 PR 稿 / 官方宣传：直接 ≤3 分
- 无原创内容，纯转载/聚合：-2 分
- 内容超过 14 天：-1 分
- 标题党，正文与标题严重不符：-3 分

keep 规则：score >= 7 且 topic != 无关 时为 true（GitHub Trending 来源 score >= 6 即为 true）。
只输出 JSON，不要其他文字。
```

### Prompt 2：摘要生成（仅对 keep=true 的文章执行，Claude Sonnet）

```
请为以下文章生成一段中文摘要，2-3 句话。

要求：
- 包含文章中最关键的具体事实（数字、产品名、技术名）
- 如果是 OPC/赚钱案例，必须包含：收入规模、实现方式、获客路径
- 如果是技术/模型，必须包含：核心能力提升、与现有方案的对比
- 如果是工具实操，必须包含：具体操作步骤或可复用的 prompt
- 如果是 AI+电商，必须包含：具体工具/方法、应用场景、效果数据
- 不写"本文介绍了……"这类套话，直接陈述事实

文章标题：{title}
文章内容：{content}

只输出摘要文本，不要其他内容。
```

---

## 技术架构

```
RSS 信息源（28个）
    ↓
Python 脚本抓取（feedparser，每日 UTC 01:00 触发）
    ↓
AI 筛选 + 评分（Claude Haiku，逐篇，≥7 分保留，GitHub Trending ≥6）
    ↓
AI 去重（Claude Haiku，一次调用，同一事件只保留最高分版本）
    ↓
AI 摘要生成（Claude Sonnet，仅对保留文章）
    ↓
生成 Obsidian Markdown 日报 + 淘汰记录
    ↓
Git commit → 仓库 output/ 目录
    ↓
Obsidian Git 插件自动同步到本地 vault
```

**调度**：GitHub Actions 定时触发，与本地电脑状态无关。

---

## Obsidian 文档格式

**文件名**：`AI Daily - YYYY-MM-DD.md`

```markdown
---
date: 2026-04-03
tags: [ai-daily]
---

## OPC / AI 赚钱案例

### [文章标题](原文链接)
- **来源**：Indie Hackers
- **评分**：9/10
- **标签**：`#OPC` `#Claude` `#月收入`
- **摘要**：2-3 句话，包含收入数字、实现路径、冷启动方式。

---

## AI + 电商

...

（其余主题同上，当天无内容的方向不显示）
```

**格式规则：**
- 先按主题分组（顺序同"关注主题方向"表），组内按评分从高到低
- YAML frontmatter 只放 `date` 和 `tags`，方便 Dataview 查询
- 行内标签 `#tag` 方便 Obsidian 点击筛选
- 每日同时生成 `rejected.md`，记录所有被淘汰的文章及评分，供评分机制验证

---

## 参考开源项目

| 项目 | 说明 | 参考价值 |
|------|------|---------|
| [RSSidian](https://github.com/pedramamini/RSSidian) | Python，专为 Obsidian 设计，支持 MCP | 架构最接近 |
| [RSS-GPT](https://github.com/yinan-c/RSS-GPT) | 成熟方案，去重、多语言 | RSS 抓取 + 摘要实现 |
| [curator-ai](https://github.com/marmelab/curator-ai) | 按用户兴趣评分筛选 | 评分/筛选逻辑 |

---

## 待决策 / 待优化

- [ ] 虎嗅反爬问题：寻找替代抓取方案
- [ ] 中文电商信息源补充：亿邦动力、晚点 LatePost RSS 验证
- [ ] 量子位 / 机器之心 RSS 返回 0 条问题排查
- [ ] 微信公众号补充方案

---

## 讨论记录

- 2026-04-03：初步需求讨论，确定信息源范围和技术方向
- 2026-04-03：扩充信息源、增加关注主题方向、确定技术方案（Python + GitHub Actions）
- 2026-04-03：评估 RSSidian；确定 Obsidian 文档格式；完成 AI Prompt 设计（含按主题细化评分标准）
- 2026-04-03：接入 OpenRouter；修复 API Key 问题（Management Key vs API Key）；跑通完整流程
- 2026-04-03：新增 AI+电商主题；移除"本地AI/开源模型"独立章节（并入其他主题）；新增去重步骤；GitHub Trending 阈值降至 6 分；合并工具实操与 Agent 工作流为同一主题；调整主题顺序
- 2026-04-03：修复 4 个失效 RSS 地址（Ben's Bites/TLDR AI/The Batch/Starter Story）；新增 11 个信息源（VentureBeat/TechCrunch/MIT TR/Latent Space/Lenny's/Trends.vc/爱范儿/极客公园/eCommerceFuel 等）；整理备选信息源候选列表
