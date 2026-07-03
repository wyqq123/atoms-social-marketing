# Search Queries — TikTok Playbook Research

## 使用方式

TikTok 数据采集与 IG / YT 都有差异,关键分野:

- **无官方深度数据 API**:TikTok Research API 门槛高(仅学术机构),不进 Atoms 生产管线。TikTok Display API 只返回轻量字段。
- **Creative Center 是官方开放的趋势数据入口**:短期 trending sound / hashtag / top ads / keyword 无登录即可访问 —— 这是 TikTok 独有优势,**Category E** 单列为独立链路。
- **博客案例仍是主链路**:与 IG 一致,SocialInsider / Later / Buffer / Hootsuite / RivalIQ 有大量 TikTok 分析。
- **Creator 类样本稀疏**:博客几乎不覆盖 solo builder / indie hacker,人工补齐(Category D)必须重度补(≥10 条)。

**执行者**:Agent(WebSearch + WebFetch,少量 playwright 兜底)
**执行时间**:P1.X 阶段(建议在 IG / YT 完成后并行推进)
**目标产出**:15-20 篇高质量博客 URL + 5-8 篇官方文档 + Creative Center 首次快照(4 个数组)+ 人工补齐 10-20 条

---

## ⚠️ Category A — 不适用

TikTok 无对未登录请求的 oEmbed / Data API 公开元数据接口。TikTok Research API 仅学术机构可申请,门槛高、审批慢,不进 Atoms 生产管线。

**如需 TikTok 原生数据**:走 Category D(人工补齐),或从 Creative Center(Category E)拿趋势数据。

---

## Category B(主链路)— 行业博客案例分析

### B1 — 通用 TikTok Benchmark / Data 报告

```
SocialInsider TikTok benchmark 2025 2026
SocialInsider TikTok engagement rate industry 2025
Sprout Social TikTok stats 2025
RivalIQ TikTok benchmark report 2025
Hootsuite TikTok statistics 2025
Buffer TikTok analytics report 2025
DataReportal TikTok users 2026
TikTok watch time benchmark 2025
TikTok completion rate by video length study
```

### B2 — Later / Buffer / Hootsuite / HubSpot 深度案例

```
Later blog TikTok case study 2025
Later blog how to go viral on TikTok
Later blog TikTok algorithm 2025 explained
Buffer TikTok growth case study small business
Buffer TikTok marketing playbook
Hootsuite TikTok algorithm 2026 update
Hootsuite TikTok marketing guide
HubSpot TikTok marketing strategy 2025
```

### B3 — 分业务类型深挖

**SaaS / AI Tool**
```
TikTok SaaS marketing case study 2025
TikTok B2B strategy small tech company
TikTok AI tool viral case study 2025
Notion TikTok growth strategy analysis
Duolingo TikTok strategy breakdown
"AI tool" TikTok launch case study 2025
```

**Ecommerce / TikTok Shop**
```
TikTok Shop case study small brand 2025
TikTok Made Me Buy It case study analysis
TikTok Shop GMV report 2025
Gymshark TikTok strategy analysis
The Ordinary TikTok case study
"TikTok organic" ecommerce SMB growth story 2025
```

**Creator / Build in Public**
```
indie hacker TikTok growth story
solo builder TikTok case study
build in public TikTok SaaS 2025
vibe coding TikTok solo founder
"@tdinh_me" OR "indie hacker" TikTok case
Codie Sanchez TikTok strategy analysis
```

### B4 — 算法 / hashtag / sound 机制

```
TikTok FYP algorithm 2025 2026 explained
TikTok hashtag strategy 2025 small business
TikTok trending sound how to use marketing
TikTok video length optimal 2025 study
TikTok watch time completion rate study 2025
TikTok posting time best 2025
TikTok rewatch signal algorithm
TikTok search ranking 2025 SEO
```

### B5 — 内容形式深度(Live / Photo Mode / Series)

```
TikTok Live shopping case study 2025
TikTok Photo Mode engagement study
TikTok Series monetization 2025
TikTok Stitch Duet strategy 2025
TikTok Photo carousel vs video comparison
```

**筛选标准**(执行后 Agent 手工筛):
- ✅ 保留:含具体 handle + engagement 数字 + 内容拆解 + 发布年份 2025+
- ❌ 剔除:纯 tips list、无 case 的 generic advice、pay-to-play 平台报告、TikTok 早期(≤2022)案例(算法已重构)

---

## Category C — TikTok 官方资源

作为算法 / policy 权威 quote 来源。

```
site:newsroom.tiktok.com how TikTok recommends content
site:newsroom.tiktok.com algorithm
site:tiktok.com/business creative best practices
site:tiktok.com/creators playbook 2025
site:effecthouse.tiktok.com
"TikTok For Business" best practices 2025 2026
"TikTok Creator Portal" content strategy
```

**核心目标 URL 已知(直接列,可直接 WebFetch)**:
- https://newsroom.tiktok.com/en-us/how-tiktok-recommends-content —— 算法官方口径
- https://www.tiktok.com/business/en/blog —— Creative best practices blog
- https://www.tiktok.com/creators/creator-portal/ —— 创作者官方指南
- https://www.tiktok.com/community-guidelines —— Community Guidelines
- https://ads.tiktok.com/business/creativecenter —— Creative Center(见 Category E)

---

## Category D — 人工补齐

用户提供样本,由 Agent 在 `data/tiktok_manual_supplements.md` 按模板整理。

**重点补齐方向**(比 IG / YT 更关键):
- **Creator 类 solo builder / indie hacker**(≥10 条)—— 博客覆盖极稀疏,需重度补齐
- **Vibe coding SMB launch post**(2025+)—— 无博客覆盖
- **中位表现样本**(1K-30K views,平衡博客的"高转化 bias")
- **TikTok Shop 从 0 起量的 SMB**(区别于博客的大品牌案例)
- **失败/低表现样本**(冷启动失败案例,教训价值高)

---

## Category E(TikTok 独有)— Creative Center 趋势快照

**动态刷新层,与 Category B/C 独立**。数据落 `data/tiktok_trend_snapshot.json`,workflow 见 `scripts/tiktok_creative_center_workflow.md`。

**刷新节奏**:2-4 周(TikTok trending 生命周期 7-14 天,过期数据无价值)
**主入口**:https://ads.tiktok.com/business/creativecenter
**抓取方式**:WebFetch 首选,playwright 兜底

**关键子页(4 个数组的数据源)**:
- Trending Hashtags → `trending_hashtags[]`
- Trending Sounds → `trending_sounds[]`(TikTok 独有关键分发信号)
- Top Ads Library → `top_ads_patterns[]`(归纳 hook / 时长 / 视觉 pattern,而非抓具体广告)
- Keyword Insights → `keyword_insights[]`(TikTok SEO 层)

**目标过滤维度**:
- Region:US / UK / DE / AU / CA(Atoms 主要市场)
- Industry:Tech / Ecommerce / Beauty / Food / Finance
- Time window:Last 7 days / 30 days —— trending 只看短窗口

详见 `tiktok_creative_center_workflow.md`。

---

## 执行 checklist

### 首轮 v0.1 → v0.2 冷启动

- [ ] Category B1:跑 5-7 条 query,收集 8-10 篇通用报告 URL
- [ ] Category B2:跑 6-8 条 query,收集 10-15 篇 Later / Buffer / Hootsuite / HubSpot URL
- [ ] Category B3(SaaS + Ecom + Creator):跑 12-15 条 query,收集 15-20 篇业务 URL
- [ ] Category B4/B5:跑 8-10 条 query,收集 10-15 篇机制 + 形式 URL
- [ ] Category C:直接 WebFetch 已知 URL(5-8 篇官方)
- [ ] 汇总所有 URL 到 `data/tiktok_industry_urls.txt`(按 B1/B2/B3/B4/B5/C 分组)
- [ ] 逐个 WebFetch → 按 `data/case_study_schema.json` + TikTok 独有字段 → `data/tiktok_case_studies.json`
- [ ] Category D 人工补齐 ≥10 条(重点 Creator 类)→ `data/tiktok_manual_supplements.md`
- [ ] **Category E 首次 Creative Center 快照** → 按 `tiktok_creative_center_workflow.md` → `data/tiktok_trend_snapshot.json`
- [ ] §5-§10 归纳填充 playbook

### 长期维护

- [ ] 每 2-4 周:Category E Creative Center refresh(必做,trending 时效性)
- [ ] 每 6 个月:Category B/C URL 池刷新(与 playbook §3/§4 复核同步)
- [ ] 每次 refresh 后:在 `scripts/README.md` TikTok 章节记录 log

---

## 与 IG / YT 采集流程的关键差异

| 环节 | IG | YT | TikTok |
|------|----|----|--------|
| 原生元数据抓取 | ❌ 废弃 | ✅ oEmbed + API v3 | ❌ 无公开 API |
| 首选案例数据源 | Category B 博客 | Category A YT 原生 | Category B 博客 |
| 官方趋势数据入口 | 无 | 无 | ✅ **Creative Center** |
| 目标样本数 | 40-60 | 60-80 | 40-60 案例 + Creative Center 快照 |
| 人工补齐比重 | 高 | 中 | **极高**(Creator 类博客几乎不覆盖)|
| 数据锚点可信度 | 依赖博客汇总 | 直接 YT metric | 博客汇总 + Creative Center 官方数据 |
| 独有维度 | Carousel vs Reel | Shorts vs long-form | trending sound / FYP penetration / loop design |

**含义**:
- TikTok playbook 的 §9 winning structures 主要依赖博客 + 人工补齐(与 IG 类似),但 §5 hook_patterns / §6 hashtag / §9 sound 三节可以引用 Creative Center 硬数据,数据锚点比 IG 硬。
- Creator 类板块可信度较低(样本稀疏),归纳时必须标注 "based on N samples, low confidence" caveat。
- Creative Center 数据只作为 **短期借势素材** 引用(有 decay 窗口),不进 §9 长期 winning structures。
