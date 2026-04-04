# AI 信息雷达

> 每天自动从 30+ 信息源抓取 AI 内容，Claude 智能评分筛选，生成 Obsidian 日报。

关注方向：**OPC/AI 赚钱案例 · AI+电商 · AI 工具实操 · AI 新技术 · 投融资动态**

---

## 效果预览

每天早上 9 点（北京时间）自动生成，推送到 GitHub，Obsidian 自动同步到本地。

```markdown
## OPC/AI赚钱案例

### [40 installs per day to 130. 34 USD per day to 130.](https://reddit.com/...)
- **来源**：Reddit r/SideProject
- **评分**：8/10
- **标签**：`#ASO实战` `#一人公司` `#增长黑客`
- **摘要**：开发者通过5个ASO优化调整，将应用从每天40次自然安装、34美元收入提升至
  130次安装、130美元收入。核心改动包括：在标题中加入主关键词、副标题改为结果导向
  表述、首屏截图展示使用后效果（转化率提升18%）...

## AI新技术/新模型

### [Gemma 4: 全面超越 Gemma 3 的最佳小型多模态开源模型](https://latent.space/...)
- **来源**：Latent Space
- **评分**：8/10
...
```

→ 查看完整示例：[examples/AI Daily - 2026-04-03.md](examples/AI%20Daily%20-%202026-04-03.md)

---

## 特性

- **全自动**：GitHub Actions 定时运行，与本地电脑状态无关
- **智能筛选**：Claude Haiku 对每篇文章评分（0-10），按主题设置差异化门槛
- **自动去重**：同一事件多个来源只保留最高分版本
- **高质量摘要**：Claude Sonnet 生成，必须包含具体数字/产品名/操作路径
- **Obsidian 原生**：YAML frontmatter + 行内标签，支持 Dataview 查询
- **完全可配置**：所有信息源在 `feeds.toml` 中管理，增删只需一行

---

## 快速开始

### 第一步：Fork 仓库

点击右上角 **Fork**，fork 到你的 GitHub 账户。

### 第二步：获取 OpenRouter API Key

前往 [openrouter.ai](https://openrouter.ai) 注册，在 **Settings → API Keys** 页面创建一个 API Key。

> OpenRouter 支持按量计费，每天运行成本约 $0.01-0.05（取决于抓取到的文章量）。

### 第三步：添加 Secret

在你 fork 的仓库中：**Settings → Secrets and variables → Actions → New repository secret**

| Name | Value |
|------|-------|
| `OPENROUTER_API_KEY` | 你的 OpenRouter API Key |

### 第四步：启用 Actions

进入 **Actions** 标签页，点击 **"I understand my workflows, go ahead and enable them"**。

**完成。** 每天北京时间 09:00 自动运行，结果写入 `output/` 目录。

---

## 同步到 Obsidian（可选）

使用 [Obsidian Git](https://github.com/denolehov/obsidian-git) 插件自动拉取。

1. 将本仓库 clone 到 Obsidian vault 的子目录：
   ```bash
   cd /path/to/your/vault
   git clone https://github.com/your-username/ai-info-aggregator.git "AI Daily"
   ```
2. 安装 Obsidian Git 插件（Vinzent，社区插件市场搜索 "Git"）
3. 插件设置：
   - **Custom base path**：`AI Daily`
   - **Pull on startup**：开启
   - **Auto pull interval**：`60`（分钟）

---

## 信息源（31个）

覆盖中英文，按方向分类：

| 方向 | 来源 |
|------|------|
| OPC/创业案例 | Indie Hackers · Reddit r/SideProject · Reddit r/Entrepreneur |
| AI Newsletter | Ben's Bites · TLDR AI · The Batch · Latent Space · Lenny's Newsletter |
| AI 技术 | Simon Willison · Hugging Face Blog · Hacker News Show HN · Reddit r/LocalLLaMA · GitHub Trending |
| 科技媒体（英文） | VentureBeat AI · TechCrunch AI · MIT Technology Review |
| 商业趋势 | Trends.vc · Product Hunt |
| AI + 电商 | Practical Ecommerce · Shopify Blog · Marketing AI Institute · SEJ Ecommerce · eCommerceFuel · eCommerceBytes |
| 中文媒体 | 量子位 · 机器之心 · 36氪 · 少数派 · 爱范儿 · 极客公园 · 晚点 LatePost |

在 `feeds.toml` 中增删信息源：

```toml
[[feeds]]
name = "你的信息源名称"
url  = "https://example.com/feed.xml"
lang = "zh"  # 或 "en"
```

---

## 评分机制

每篇文章由 Claude Haiku 评分（0-10），评分标准核心是**信息密度 × 可操作性**：

- 有具体事实（数字/产品名/技术名）才有信息密度
- 读完能做某件事或做更好的判断，才有可操作性
- 泛泛观点、营销软文、无数据的预测：直接 ≤4 分

**保留门槛**：≥7 分（GitHub Trending 来源 ≥6 分）且主题相关。

各主题的详细评分标准见 [PROMPTS.md](PROMPTS.md)。

---

## 本地运行

```bash
# 克隆仓库
git clone https://github.com/your-username/ai-info-aggregator.git
cd ai-info-aggregator

# 安装依赖
pip install -r requirements.txt

# 配置 API Key
cp .env.example .env
# 编辑 .env，填入你的 OPENROUTER_API_KEY

# 运行（需先 export 环境变量）
export $(cat .env | xargs)
python main.py

# 或指定回溯天数（默认1天）
LOOKBACK_DAYS=3 python main.py
```

输出文件在 `output/` 目录：
- `AI Daily - YYYY-MM-DD.md`：当日日报
- `AI Daily - YYYY-MM-DD - rejected.md`：淘汰记录（含评分，用于验证评分机制）

---

## 项目结构

```
ai-info-aggregator/
├── main.py              # 入口
├── feeds.toml           # 信息源配置
├── requirements.txt
├── .env.example
├── src/
│   ├── feeds.py         # RSS 抓取
│   ├── scorer.py        # AI 评分 / 去重 / 摘要
│   └── writer.py        # Markdown 生成
├── output/              # 生成的日报（Git 追踪）
└── .github/workflows/
    └── daily.yml        # GitHub Actions 定时任务
```

---

## 技术栈

- **Python 3.11+** · feedparser · requests
- **OpenRouter**（Claude Haiku 评分/去重，Claude Sonnet 摘要）
- **GitHub Actions**（定时调度，免费额度够用）
- **Obsidian Git**（本地同步，可选）

---

## License

MIT
