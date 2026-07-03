# Search Queries — YouTube Playbook Research

## 使用方式

YT 数据采集与 IG 有**关键差异**:YT 的 oEmbed + Data API v3 让**Category A(直接抓 YT 元数据)是可行的第一手路径**,不像 IG 已废弃。所以 YT 走 **Category A(YT 元数据抓取)+ Category B(博客二手案例)+ Category C(官方权威)+ Category D(人工补齐)** 四条并行链路。

**执行者**:Agent(WebSearch + WebFetch + 本地 Python 脚本)
**执行时间**:P1.4 阶段
**目标产出**:15-20 篇高质量博客 URL + 5-8 篇官方文档 + 20-30 支 YT video 直抓元数据

---

## ✅ Category A — 主链路(YT 原生元数据抓取,可用)

YT 公开元数据可通过两条路径拿到:

### A1 — oEmbed(无需 API key,基础字段)
- Endpoint: `https://www.youtube.com/oembed?url=<VIDEO_URL>&format=json`
- 返回字段:title / author_name / author_url / thumbnail_url / html embed
- 用法:走 `scripts/fetch_youtube_metadata.py --mode oembed --input data/youtube_industry_urls.txt`
- 适用场景:快速构建样本 title/thumbnail 对比;不需要 view/like 数字的定性研究

### A2 — YouTube Data API v3(需 API key,完整字段)
- Endpoint: `https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,contentDetails&id=<VIDEO_ID>&key=<API_KEY>`
- 返回字段:标题 / 描述 / tags / 分类 / 发布时间 / duration / viewCount / likeCount / commentCount / definition(HD/SD)/ caption 是否可用
- 用法:走 `scripts/fetch_youtube_metadata.py --mode api --input data/youtube_industry_urls.txt`(需 `YOUTUBE_API_KEY` 环境变量)
- Quota:免费 10000 units/day;单个 videos.list 请求消耗 1 unit,可抓 10000 支视频/天
- 申请路径:https://console.cloud.google.com/ → 新建项目 → 启用 YouTube Data API v3 → 生成 API key
- Atoms 用法:配到本地 `.env` 或 shell profile;不进 skill 仓库(secret hygiene)

### A3 — 目标视频挖掘 query(在 YT 内搜)

先通过 YT 站内搜索找到 Atoms 目标业务类型的 top 视频,收集 URL 到 `data/youtube_industry_urls.txt`,再喂给脚本:

**SaaS / AI Tool**
```
how to use notion for productivity 2025
notion tutorial for beginners 2025
best AI tools for developers 2025
how I built a saas in 30 days
saas demo walkthrough
```

**Ecommerce**
```
unboxing [popular product] 2025
[product category] review honest 2025
[product] vs [product] comparison 2025
first impression [ecom brand]
```

**Creator / Indie Hacker**
```
build in public solo founder
indie hacker journey MRR
how i built [tool] with [stack]
solopreneur daily vlog
```

**采集流程**:
1. YT 站内跑 query,肉眼筛出 5-10 支 top 视频/query(按 view / likes / 发布时间 综合判断)
2. URL 追加到 `data/youtube_industry_urls.txt`,按业务类型分组
3. 跑 `scripts/fetch_youtube_metadata.py` 批量抓元数据到 `data/youtube_video_samples.json`
4. 归纳时结合 §9 winning structures 拆解 title / description / thumbnail / hashtag 规律

---

## Category B(辅助链路)— 行业博客与分析报告

博客提供跨样本的**结构性洞察 + 数据点**,弥补 Data API 只能拿单点数据的短板。

### B1 — YT 算法 + SEO 主源(Backlinko / VidIQ / TubeBuddy)

```
Backlinko YouTube SEO guide 2025
VidIQ blog YouTube algorithm ranking signals 2025
TubeBuddy blog channel growth benchmarks 2025
YouTube ranking factors 2025 study
YouTube CTR average by niche 2025
```

### B2 — Shorts vs long-form 数据

```
YouTube Shorts vs long-form comparison data 2025
YouTube Shorts algorithm ranking 2025
Shorts to long-form conversion rate creator study 2025
YouTube Shorts 3 minute update analysis 2024
```

### B3 — 分业务类型深挖

```
YouTube SaaS marketing case study 2025
YouTube ecommerce channel growth strategy 2025
indie hacker YouTube channel case study
build in public YouTube growth story
YouTube for small business best practices 2025
```

### B4 — 内容格式深度(thumbnail / title / retention)

```
YouTube thumbnail design best practices 2025 CTR
YouTube title optimization study 2025
YouTube average view duration benchmark by niche
YouTube retention curve analysis creator
YouTube chapters SEO impact study
```

### B5 — 商业化 + YPP

```
YouTube Partner Program requirements 2024 2025
YouTube Shopping affiliate program creator earnings
YouTube ad revenue by niche average 2025
YouTube membership channel growth study
```

**筛选标准**(执行后 Agent 手工筛):
- ✅ 保留:含 specific 数据点 + case detail + 结构性归纳
- ❌ 剔除:纯 SEO 灌水 tips list、无 case 的 generic advice、pay-to-play 广告平台报告

---

## Category C — YT 官方与 Google 官方资源

作为算法 / policy 权威 quote 来源。

```
site:blog.youtube algorithm ranking
site:blog.youtube creator update 2024 2025
site:support.google.com/youtube algorithm
site:creators.youtube.com strategy
site:developers.google.com/youtube/v3
"YouTube Creator Insider" algorithm explained
"YouTube blog" AI content disclosure
"YouTube Partner Program" eligibility 2024
```

**核心目标 URL 已知(直接列)**:
- https://blog.youtube/how-youtube-works/product-features/algorithms/ —— algorithm overview
- https://support.google.com/youtube/answer/9527654 —— YPP requirements
- https://support.google.com/youtube/answer/13554835 —— AI content disclosure(2024-03)
- https://developers.google.com/youtube/v3/docs/videos —— Data API v3 videos.list docs
- https://blog.youtube/inside-youtube/aloud-multilingual-audio-tracks/ —— Aloud multi-language dubbing

---

## Category D — 人工补齐(与 IG 相同角色)

用户提供的 YT 频道/视频样本,由 Agent 在 `data/youtube_manual_supplements.md` 按模板整理。

**优先补齐方向**:
- 2025 最新 launch / demo 视频(博客覆盖偏 2024 及以前)
- **Atoms 用户画像贴近的 solo builder** —— indie hacker / vibe coding builder / no-code founder
- **中位表现视频**(1K-10K views 的真实 SMB 视频,平衡博客的"top 5% success 案例 bias")
- 失败案例(YT 视频冷启动失败或 monetization rejected 的具体案例)—— 教训价值高

---

## 执行 checklist

- [ ] Category A1 oEmbed:跑 30-50 支视频 URL 快速抓 title/thumbnail(无需 API key)
- [ ] Category A2 Data API v3:若已配 key,同一批 URL 补完整元数据到 `data/youtube_video_samples.json`
- [ ] Category B1/B2:跑 8-10 条 query,收集 10-15 篇 SEO + algorithm 博客 URL
- [ ] Category B3/B4/B5:跑 10-15 条 query,收集 12-18 篇业务 + 格式 + 商业化 URL
- [ ] Category C:直接 WebFetch 已知 URL(5-8 篇官方)
- [ ] 汇总:所有 URL 落到 `data/youtube_industry_urls.txt`(按 A/B/C 分组)
- [ ] LLM 按 `data/youtube_case_study_schema.json` 提取 → `data/youtube_case_studies.json`
- [ ] Category D 人工补齐 4-7 条(尤其 Creator 类)→ `data/youtube_manual_supplements.md`
- [ ] §5-§10 归纳填充 playbook

---

## 与 IG 采集流程的关键差异

| 环节 | IG | YT |
|------|----|----|
| 原生元数据抓取 | ❌ 已废弃(OG 剥离) | ✅ oEmbed + Data API v3 |
| 首选数据源 | Category B 博客二手 | **Category A YT 原生**(其次 B/C) |
| 目标样本数 | 40-60 | 60-80(A 与 B 各 30-40)|
| 人工补齐比重 | 高(博客 bias 严重)| 中(有原始数据平衡)|
| 数字锚点可信度 | 依赖博客汇总 | 直接 YT 官方 metric |

**含义**:YT playbook 的数据锚点可以更硬(直接 YT metric 而非博客汇总),可信度显著高于 IG playbook。这也是为什么 YT 版本可以更早从 §5-§10 stub 迭代到 v1.0。
