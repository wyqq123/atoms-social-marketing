# Sample Research Workflow — Platform Playbooks (Atoms)

为 `references/platform-playbooks/*.md` 归纳"Atoms 用户可复用的高转化模式"章节收集有效样本。

**当前覆盖平台**:Instagram(IG)/ YouTube(YT)/ TikTok(TT)。LinkedIn / X 待补齐。

---

## 平台间的数据采集能力差异

| 平台 | 一手元数据可否直接抓 | 主通道 | 备注 |
|---|---|---|---|
| **YouTube** | ✅ 公开暴露 | Category A(oEmbed 无 key / Data API v3 需 key) | 有工作中的 fetcher 脚本,可动态更新 |
| **Instagram** | ❌ 已剥离(2026-07-02 实测) | Category B(行业博客) + Category D(人工补齐) | 老 OG scraper 已废弃保留在 `extract_og_metadata.py`,仅作历史参考 |
| **TikTok** | ❌ 无公开元数据 API(Research API 门槛高) | Category B(博客)+ Category D(人工重补齐)+ **Category E(Creative Center 官方趋势数据,独有)** | Creative Center 是 TikTok 独有优势 —— 无登录门槛的官方趋势入口,2-4 周动态刷新 |

**结论**:
- YT 数据管线是"动态更新"的实工作通路 —— 直接 metric 锚点硬
- IG 是"半人工"通路 —— 完全依赖博客与人工补齐
- TT 是"混合"通路 —— 案例走 IG 模式(博客 + 人工),但趋势层有官方 Creative Center 硬数据,§5 hook / §6 hashtag / §9 sound 三节数据锚点比 IG 硬

同一 skill 面向多个平台时,§9 归纳的信噪比标注要按此差异对齐。

---

## Instagram Playbook Research

### 为什么不直接抓 IG

IG 已对未登录请求剥离 OG meta(2026-07-02 实测),第一手抓取路径失效。第三方 scraping API 违反 IG ToS,不走。

**当前策略**:走行业博客案例(Later / Buffer / SocialInsider / Hootsuite / Sprout Social)已发布的 IG 分析文章 + 用户人工补齐。

### Pipeline

```
Step 1  搜索博客案例     →  WebSearch (Category B/C queries in search_queries.md)
                            → data/ig_industry_urls.txt(博客文章 URL,一行一个)

Step 2  提取结构化案例   →  逐个 WebFetch,LLM 按 case_study_schema.json 提取
                            → data/ig_case_studies.json(结构化案例数组)

Step 3  人工补齐         →  用户提供 blogs 未覆盖的高质量样本
                            → data/ig_manual_supplements.md(markdown 模板逐条填)

Step 4  归纳分析         →  合并 case_studies + supplements,填 playbook §9
                            → references/platform-playbooks/instagram.md
```

### 产物形态

| 文件 | 内容 | 来源 |
|---|---|---|
| `data/ig_industry_urls.txt` | 博客/官方文档 URL 列表 | Category B/C WebSearch |
| `data/ig_case_studies.json` | 结构化案例(brand / caption / hashtag / engagement / insight) | WebFetch + LLM 提取 |
| `data/ig_manual_supplements.md` | 用户提供的补齐样本 | 人工填 |
| `data/case_study_schema.json` | 提取 schema | 见文件 |

### 目标样本量

- Category B 博客提取:**30-40 个**(SaaS/ecommerce/creator 各 10-15)
- 人工补齐:**10-20 个**(补 blogs 覆盖不到的细分或 2025 最新样本)
- **合计 40-60**

### 已废弃脚本

- `scripts/extract_og_metadata.py` — 老 OG scraper,IG 剥离 OG meta 后失效。保留仅作历史 + 若 IG 政策回滚可复用。**不进当前 pipeline。**

---

## YouTube Playbook Research

### 为什么 YT 可以直接抓

YouTube 官方通过两个公开通道暴露视频元数据:
- **oEmbed** (`https://www.youtube.com/oembed`)—— 无需 API key,返回 title / author / thumbnail_url。够做定性分析。
- **Data API v3** (`videos.list`)—— 需 `YOUTUBE_API_KEY`,返回完整字段:views / likes / comments / duration / tags / publishedAt / captions / defaultLanguage 等。10000 units/day 免费配额,batch 50 支/请求。

这两个都是**官方接口**,不是 scraping。因此 YT 的 Category A(直接抓)是主通道,可动态更新。

### Pipeline

```
Step 1  收集 YT 视频 URL      →  按 scripts/youtube_search_queries.md § A 里的 query
                                在 YT 站内搜 top 视频,粘贴 URL 到:
                                → data/youtube_industry_urls.txt(§ A 分类下)

Step 2  批量抓元数据          →  运行 fetch_youtube_metadata.py(oembed 或 api 模式)
                                → data/youtube_video_samples.json(结构化元数据)

Step 3  搜行业博客深度案例    →  WebSearch (Category B queries in youtube_search_queries.md)
                                → data/youtube_industry_urls.txt(§ B 分类下)+ 逐个 WebFetch
                                → data/youtube_case_studies.json(带 CTR/AVD/AVP 深度数据)

Step 4  官方文档核对          →  Category C 已知 URL 直接 WebFetch(见 youtube_industry_urls.txt § C)
                                → 用于 §3 算法机制 / §7 商业化 / policy 引用

Step 5  人工补齐              →  用户按 data/youtube_manual_supplements.md 模板填
                                → 补失败/中位样本、非英语市场、Shorts 3min 新形式、Atoms 用户自建频道

Step 6  归纳分析              →  合并 samples + case_studies + supplements,填 playbook §5-§10
                                → references/platform-playbooks/youtube.md
```

### 产物形态

| 文件 | 内容 | 来源 |
|---|---|---|
| `data/youtube_industry_urls.txt` | Category A/B/C 分组 URL(视频 + 博客 + 官方) | 手动种子 + WebSearch 补齐 |
| `data/youtube_video_samples.json` | 每支视频的结构化元数据(oEmbed 或 API v3 字段) | `fetch_youtube_metadata.py` 输出 |
| `data/youtube_case_studies.json` | 带深度洞察的博客案例(含 CTR/AVD/AVP) | WebFetch + LLM 按 schema 提取 |
| `data/youtube_case_study_schema.json` | 提取 schema(与 IG 版本对齐,差异见 `$fields_vs_ig_schema_diff`) | 见文件 |
| `data/youtube_manual_supplements.md` | 用户提供的补齐样本 | 人工填 |
| `data/youtube_errors.txt` | fetcher 失败样本(私有/删除/id 无效等) | fetcher 输出 |

### fetch_youtube_metadata.py 使用

```bash
# 模式 1:oEmbed(无 key,基础字段)—— 快速做 title/author/thumbnail 采集
python3 scripts/fetch_youtube_metadata.py \
    --input data/youtube_industry_urls.txt \
    --output data/youtube_video_samples.json

# 模式 2:Data API v3(完整字段,含 views/likes/duration/tags)—— 用于硬数据
export YOUTUBE_API_KEY="AIzaSy..."
python3 scripts/fetch_youtube_metadata.py \
    --input data/youtube_industry_urls.txt \
    --mode api \
    --output data/youtube_video_samples.json

# 模式 3:单支视频快速测试
python3 scripts/fetch_youtube_metadata.py \
    --url "https://www.youtube.com/watch?v=xxx" \
    --mode oembed
```

**获取 API key**:https://console.cloud.google.com/ → 启用 YouTube Data API v3 → 创建 API key。10000 units/day 免费(每次 videos.list 消耗 1 unit,batch 50 支视频仍算 1 unit)。

**脚本特性**:
- video_id 去重(重跑不会重复抓)
- 失败样本记录到 `data/youtube_errors.txt`,不阻塞整体流程
- 每请求间隔 0.5s(远宽松于 quota)
- Data API mode 支持 batch 50 支/请求,自动分批
- 支持 URL 格式:`/watch?v=`, `youtu.be/`, `/shorts/`, `/embed/`, `/v/`, `/live/`

### 目标样本量

- **Category A(直接抓)**:每业务类型 8-15 支 top 视频,合计 **25-45 支**——主数据锚点
- **Category B(博客案例)**:**15-25 个**——带 CTR/AVD/AVP 深度数据
- **Category D(人工补齐)**:**6-12 个**——补失败/中位样本、非英语、Shorts 3min 新形式、Atoms 用户自建频道
- **合计 45-80**

### 数据源可信度分级(§9 归纳时用)

| Category | Confidence | 用途 |
|---|---|---|
| A(YT Data API v3) | **high** | 数据锚点主源;可作硬数字引用 |
| A(YT oEmbed 仅 title/thumbnail) | medium | 定性对比,不作 engagement 数据 |
| C(YT 官方 blog / help) | **high** | Algorithm / policy quote 权威源 |
| B(Backlinko / VidIQ 类专业博客) | medium-high | 结构性洞察 + 案例引用 |
| D(用户人工补齐) | medium | 中位样本 + 冷启动失败案例平衡 bias |

---

## TikTok Playbook Research

### 为什么不直接抓 TikTok 视频

TikTok 无对外公开的 oEmbed / Data API(TikTok Research API 仅学术机构可申请,门槛高,不进 Atoms 生产管线)。第三方 scraping API 违反 ToS,不走。

**当前策略**:与 IG 类似走博客案例 + 人工补齐,但**额外增加 Category E(Creative Center)**—— TikTok 官方公开的趋势数据入口,无登录门槛,是 TikTok 相对 IG 的独有优势。

### Pipeline

```
Step 1  搜索博客案例       →  WebSearch (Category B/C queries in tiktok_search_queries.md)
                              → data/tiktok_industry_urls.txt(按 B1/B2/B3/B4/B5/C 分组)

Step 2  提取结构化案例     →  逐个 WebFetch,LLM 按 case_study_schema.json + TikTok 独有字段提取
                              → data/tiktok_case_studies.json

Step 3  人工补齐(重度)   →  用户提供 blogs 未覆盖的样本(尤其 Creator 类 solo builder ≥10 条)
                              → data/tiktok_manual_supplements.md

Step 4  Creative Center 快照 → WebFetch 4 类子页(hashtag / sound / top ads / keyword insights)
                              → data/tiktok_trend_snapshot.json(2-4 周刷新)

Step 5  归纳分析           →  合并 case_studies + supplements + trend snapshot,填 playbook §5-§10
                              → references/platform-playbooks/tiktok.md
```

### 产物形态

| 文件 | 内容 | 来源 | 刷新节奏 |
|---|---|---|---|
| `data/tiktok_industry_urls.txt` | 博客 + 官方 URL 池,按 B1/B2/B3/B4/B5/C/E 分组 | Category B/C WebSearch | 6 个月 |
| `data/tiktok_case_studies.json` | 结构化案例(含 video_length / sound_type / hook_pattern / loop_designed / fyp_penetration) | WebFetch + LLM 提取 | 12 个月 |
| `data/tiktok_manual_supplements.md` | 用户提供样本(重点 Creator / vibe coding SMB) | 人工填 | 按增量 |
| `data/tiktok_trend_snapshot.json` | Creative Center 4 类趋势数据(hashtags / sounds / top ads patterns / keyword insights) | WebFetch(Category E) | **2-4 周** |

### Category E — Creative Center 独有链路

**动态刷新层,与 case studies / manual 分离**。完整 workflow 见 `scripts/tiktok_creative_center_workflow.md`。

- 入口:https://ads.tiktok.com/business/creativecenter(公开,无登录)
- 抓取方式:WebFetch 首选,playwright 兜底(未预置脚本)
- 过滤维度:region × industry × time window(7d / 30d)
- 数据分层:
  - `trending_hashtags[]` — playbook §6 mix_strategy slot 2/3 候选
  - `trending_sounds[]` — playbook §9 sound recommendation 主源(TikTok 独有关键分发信号)
  - `top_ads_patterns[]` — playbook §5 hook 建议 + §9 长期结构佐证(需连续 2+ 次 refresh 验证才下沉)
  - `keyword_insights[]` — playbook §6 caption / voiceover 关键词候选

### 目标样本量

- Category B 博客提取:**30-40 个**(SaaS/Ecom/Creator 各 10-15)
- Category D 人工补齐:**≥10 个**(Creator 类必补,博客覆盖极稀疏)
- Category E Creative Center 首次快照:总 entries **≥ 80 条**(4 类合计)
- **合计案例 40-60,趋势数据独立快照**

### 数据源可信度分级(§9 归纳时用)

| Category | Confidence | 用途 |
|---|---|---|
| E(Creative Center trending hashtags / sounds) | **high** | 短期借势素材硬数据(有 decay 窗口)|
| E(Creative Center top ads patterns) | medium-high | 结构 pattern 建议;需连续 refresh 验证才下沉 §9 |
| E(Creative Center keyword insights) | high | TikTok SEO 层官方数据 |
| C(TikTok Newsroom / For Business) | **high** | Algorithm / policy quote 权威源 |
| B(SocialInsider / Later / Hootsuite / RivalIQ) | medium-high | 结构性洞察 + engagement 数字引用 |
| D(用户人工补齐) | medium | Creator 类关键补齐;中位样本平衡 bias |

### Refresh Log

每次 Creative Center refresh 在此记录:

```
- 2026-07-02: v0.1 骨架建立,cases/entries 全部为空,等首轮 WebFetch
- (未来 refresh 在此追加,格式:YYYY-MM-DD: scope=[regions × industries],entries=[hashtag:N, sound:N, top_ads:N, keywords:N])
```

---

## 合规底线(通用)

- ✅ 只用平台官方公开接口(YT oEmbed / Data API v3)或 Google 索引里的公开博客文章
- ✅ 引用博客的分析结论时标注来源
- ✅ 引用帖子/视频链接遵循 fair use(评论 + 分析用途)
- ❌ 不用任何第三方 scraping API(尤其 IG)
- ❌ 不用登录 session 抓取
- ❌ 不复述整段 caption/description(取要点 + 分析)
- ❌ 不缓存 YT 缩略图图片(只存 URL + 文字描述),缩略图版权归 uploader

---

## 归纳时的信噪比说明(跨平台通用)

样本源天然带 bias,归纳 playbook §9 时要:

- 博客案例:已经被博主筛选过(通常是"高 engagement"或"值得学"的),偏向"成功案例"→ 明确标注"高转化案例",不代入"普通用户平均表现"
- YT Category A top 视频:YT 搜索排序算法本身偏 high-view → 结论要标注"符合当前 YT 推荐系统偏好的模式"
- 交叉验证:3+ 独立来源提到同一模式再采纳(避免 single-source 推论)
- 人工补齐样本尽量补"典型/中位"表现 + 失败样本,平衡样本 bias
- Atoms 用户 90%+ 在 0-1K subs / 0-1K followers 区间——归纳时优先取小账号可复制的样本,大账号(>100K)结论标注"仅供品牌方向参考"

---

## 后续扩展(待补齐平台)

| 平台 | 元数据可否直接抓 | 优先级 | 备注 |
|---|---|---|---|
| LinkedIn | ❌ 严格封锁 | P2 | 只能走博客 + 人工;组织号 vs 个人号差异需分层 |
| X(Twitter) | ✅ 有 API(但付费门槛高) | P3 | 免费层几乎不可用,评估 ROI |
