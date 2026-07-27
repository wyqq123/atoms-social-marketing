# Runtime Opportunity Probe 轻量实时方案

## 1. 为什么要从“趋势情报系统”收敛

Atoms builder（应用创建者）触发 social marketing skill 时,系统才知道具体 built app 上下文、终端用户 ICP、痛点、卖点和转化目标。因此真正有价值的趋势判断必须和当前 built app 相关,不能提前把所有平台所有趋势都采完。

但如果每次都做完整流程:

```text
Built app end-user ICP -> 生成需求话题 -> 全平台检索 -> 抽取 audience/content/distribution/metrics -> 归一 -> 打分 -> 生成策略
```

这个链路太长、太脆、太贵,容易在 API 权限、平台限制、网络延迟、LLM 抽取、数据缺失任一环节失败。

更可行的生产方案是:

```text
稳定基线 + 缓存趋势 + 运行时轻量探测 + 明确降级
```

运行时不追求“完整趋势情报”,只回答一个小问题:

> 当前 built app 的 3-5 个终端用户核心需求话题,在少数候选平台上是否存在近期可观察的活跃内容机会?

## 2. 新方案一句话

把复杂的 Trend Intelligence Layer 收敛成 **Runtime Opportunity Probe**:

1. 先用稳定层快速选出 3-5 个候选平台。
2. 从 built app 终端用户 ICP / JTBD / pains 生成 6-12 个 demand-language seed。
3. 每个平台只探测 top 2-3 个最相关 seed。
4. 每个平台最多取 5-10 条近期证据。
5. 总探测时间控制在 3-8 秒。
6. 探测失败不阻塞,使用缓存/稳定层降级。
7. Stage 2 分数里把 freshness 当 confidence,而不是硬性前置条件。

## 3. 三层数据架构

### 3.1 L0 Stable Platform Baseline

长期稳定,随 skill 一起发布或每月/季度维护。

内容包括:

- 平台用户心智
- 平台主要 surface
- 内容格式规则
- 转化路径
- 小账号可达性常识
- 社区/平台禁忌
- 默认行业适配基线

来源:

- playbook
- platform registry
- 官方文档
- 过往人工研究

作用:

- 没有实时数据也能生成可用内容。
- 先筛出候选平台,避免全平台探测。

### 3.2 L1 Cached Market Signals

离线/人工维护,不要求每次实时。

内容包括:

- 各垂类常驻 demand topic pool
- 平台近期 broad trend brief
- evergreen winning structures
- 高频搜索词/社区列表/内容样本

刷新频率:

- YouTube/Reddit:每周自动或半自动
- TikTok/Pinterest/Rednote/LinkedIn:1-4 周人工或官方后台导入
- 稳定结构:1-3 个月复核

作用:

- 给运行时 seed expansion 提供候选词和平台入口。
- 实时探测失败时作为 fallback。

### 3.3 L2 Runtime Opportunity Probe

Atoms builder（应用创建者）触发 skill 后才执行,时间严格受限。

内容包括:

- 根据当前 built app 的终端用户 ICP/JTBD/pain 生成 demand-language seed
- 对少数候选平台做 top-k 检索/探测
- 返回轻量 evidence pack

不做:

- 不做全平台趋势采集
- 不做完整趋势快照
- 不做大规模评论抓取
- 不做复杂聚类
- 不抓需要登录态的数据

## 4. 运行时主流程

```text
Input app context
  v
Stage A: App Signal Extraction
  -> end-user ICP / JTBD / pains / value props / goal / builder assets
  v
Stage B: Platform Preselect
  -> 用 L0 baseline 选 3-5 个候选平台
  v
Stage C: Demand Seed Generation
  -> 生成 6-12 个终端用户需求语言 seed
  v
Stage D: Probe Planning
  -> 每个平台选择 2-3 个 seed + 1-2 个 source
  v
Stage E: Parallel Lightweight Probe
  -> 每个平台最多 5-10 条结果,总耗时 3-8 秒
  v
Stage F: Evidence Pack Normalization
  -> 只抽取轻量字段
  v
Stage G: Fit Score + Strategy
  -> 有实时证据则增强;无则降级
```

## 5. Stage A: App Signal Extraction

从 builder 输入中抽取最小必要信号,并区分 built app 终端用户 ICP 与 builder 生产上下文:

```json
{
  "end_user_icp": {
    "roles": ["Shopify seller"],
    "market": ["US"],
    "language": ["en"],
    "explicitly_not_builder_identity": true
  },
  "jtbd": ["improve product page conversion", "publish better product copy faster"],
  "pains": ["low add-to-cart rate", "generic product descriptions", "unclear product-page benefits"],
  "value_props": ["AI-assisted product-page copy", "conversion-focused rewrite suggestions"],
  "goal": "trial-signup",
  "builder_context": {
    "assets": {
      "screen_demo": true,
      "visual_result": true,
      "founder_story": true,
      "customer_proof": false
    },
    "must_not_be_used_as_end_user_identity": true
  }
}
```

这一步必须很快,只用 LLM 或规则抽取一次。

## 6. Stage B: Platform Preselect

先不要全平台实时探测。用稳定层筛平台。

### 6.1 预筛规则

| App/目标特征 | 候选平台倾向 |
|---|---|
| AI/SaaS/tool + end-user ICP explicitly founders/builders | X, Reddit, LinkedIn, YouTube, TikTok |
| 强视觉结果/ecommerce/lifestyle | TikTok, Instagram, Pinterest, Rednote |
| B2B/professional buyer | LinkedIn, X, YouTube, Reddit |
| 强教程/how-to/search intent | YouTube, Reddit, Pinterest, Rednote |
| CN market/lifestyle/ecom | Rednote, Douyin, Bilibili(后续), WeChat(后续) |
| local business | Facebook, Instagram, Google/Maps(后续), Rednote(CN) |

### 6.2 输出

最多 5 个候选平台:

```json
{
  "platform_candidates": ["x", "reddit", "youtube", "linkedin", "tiktok"],
  "reason": "AI/SaaS built app for Shopify sellers, with builder-provided founder story and demo assets; prioritize platforms with merchant/operator audience and demo-friendly surfaces."
}
```

## 7. Stage C: Demand Seed Generation

这一步不是生成产品关键词,而是生成用户会说的话。

### 7.1 Seed 类型

每个 App 生成 6-12 个 seed,分成 4 类即可,不要太多。

| 类型 | 说明 | 例子 |
|---|---|---|
| Pain seeds | 用户痛点表达 | "chasing invoices", "manual admin takes too long" |
| JTBD seeds | 终端用户要完成的任务 | "improve product page conversion", "publish better product copy" |
| Workaround seeds | 终端用户当前替代方案 | "manual product copywriting", "generic AI writing tool" |
| Outcome seeds | 终端用户想要的结果 | "increase add to cart", "increase product page sales" |

### 7.2 Seed 生成约束

- 不超过 12 个。
- 每个 seed 3-8 个词。
- 至少一半必须是 built app 终端用户痛点或任务,不是产品功能。
- 每个 seed 带 `source`: pain / jtbd / workaround / outcome。
- 每个 seed 带 `confidence`。

### 7.3 输出示例

```json
{
  "seeds": [
    { "text": "improve product page conversion", "type": "jtbd", "confidence": "high" },
    { "text": "manual product copywriting", "type": "workaround", "confidence": "medium" },
    { "text": "increase product page sales", "type": "outcome", "confidence": "medium-high" },
    { "text": "product page traffic no sales", "type": "pain", "confidence": "medium" }
  ]
}
```

## 8. Stage D: Probe Planning

为每个平台选择少量 seed 和 source。

### 8.1 计划规则

```text
max_platforms = 5
max_seeds_per_platform = 3
max_results_per_seed = 3
max_results_per_platform = 8
max_total_probe_time = 8s
```

Query planning must keep precision and recall in balance:

- Use at least one long-tail pain/JTBD query when available.
- Use at least one broader keyword group when available.
- Prefer platform-native rewrites over raw generic queries.
- Keep `query` as a backward-compatible primary query, but plan from `query_variants` when present.
- Reject or down-rank results that do not match `expected_evidence_type`, even if they have high engagement.

### 8.2 平台 source 选择

| 平台 | 默认 runtime probe | fallback |
|---|---|---|
| Reddit | subreddit search/hot/top via API or public JSON | cached subreddit topic pool |
| YouTube | Data API search.list + videos.list or oEmbed | cached query samples |
| X | API recent search if configured | cached/manual weekly brief |
| TikTok | 不做 live UI 抓取;读最近 Creative Center cache | stable TikTok baseline |
| Pinterest | Trends/API if configured;否则 cache | stable Pinterest baseline |
| LinkedIn | 不做全站 live probe;读 manual/cache/authorized Page data | stable LinkedIn baseline |
| Instagram | 不做全站 live probe;读 own-account insights/cache | stable IG baseline |
| Rednote | 不做 live probe;读 manual/cache | stable Rednote baseline |

关键取舍：**运行时实时探测只优先做 Reddit / YouTube / 可配置 X。** 其它平台用近期缓存或 manual brief。这样稳定性会高很多。

## 9. Stage E: Lightweight Probe

### 9.1 返回轻量 Evidence Pack

运行时 probe 不生成完整 snapshot,只返回 evidence pack:

```json
{
  "platform": "reddit",
  "probe_status": "success | timeout | unavailable | cache_only",
  "queried_seeds": ["product page traffic no sales", "improve product page conversion"],
  "results": [
    {
      "source": "reddit_api",
      "surface": "subreddit_search",
      "query": "product page traffic no sales Shopify",
      "title": "Product page gets traffic but no sales - what should I fix?",
      "url": "https://reddit.com/...",
      "community": "r/ecommerce",
      "observed_at": "2026-07-26T00:00:00Z",
      "metrics": {
        "score": 182,
        "comments": 64,
        "age_hours": 20
      },
      "text_excerpt": "Store owner asking how to improve product-page copy and conversion..."
    }
  ],
  "known_biases": ["selected_query_bias", "no_demographic_ground_truth"]
}
```

### 9.2 Probe 失败处理

| 状态 | 处理 |
|---|---|
| `success` | 用 runtime evidence 增强 score 和 why_now |
| `timeout` | 使用 cache,confidence 降一级 |
| `unavailable` | 使用 stable baseline,confidence 最高 medium |
| `cache_only` | 可生成,但不能说实时趋势 |
| `no_results` | 不代表平台不适合,只代表本次 seed 未探测到机会;用 baseline 继续但降低 evidence quality |

## 10. Stage F: Evidence Pack Normalization

只抽取最必要字段,不做重型分析。

```json
{
  "platform": "reddit",
  "observations_light": [
    {
      "topic_label": "improving product page conversion",
      "audience_clues": ["Shopify seller", "ecommerce operator"],
      "pain_clues": ["traffic but no sales", "unclear product benefits", "low conversion"],
      "content_clues": ["question post", "advice-seeking", "long comments"],
      "distribution_clues": ["subreddit discussion", "high comment density"],
      "metric_clues": {
        "activity": "medium-high",
        "discussion_depth": "high",
        "recency": "fresh"
      },
      "evidence_refs": ["reddit:r/ecommerce:post_id"]
    }
  ]
}
```

不要在这里写 `relevance_to_atoms`。是否相关交给 Stage 2 用 built app end-user ICP 计算。Builder 素材只影响 production feasibility。

## 11. Stage G: Fit Score 简化版

为了稳定,运行时评分不要过细。建议使用 5 个维度:

```text
fit_score =
  ICP Demand Match        35
+ Platform Mindset Fit    20
+ Content Expression Fit  15
+ Reach Feasibility       15
+ Conversion Feasibility  10
+ Evidence Freshness       5
- Risk Penalty           0..15
```

其中运行时 probe 主要影响：

- `ICP Demand Match`
- `Evidence Freshness`
- `Reach Feasibility` 的一部分
- `why_now`

稳定层主要影响：

- `Platform Mindset Fit`
- `Content Expression Fit`
- `Conversion Feasibility`
- 风险项

这样即使 probe 失败,分数不会崩。

## 12. 缓存策略

### 12.1 Query Cache

缓存 key:

```text
platform + region + seed_hash + window
```

TTL:

| 平台 | TTL |
|---|---|
| Reddit | 24h |
| YouTube | 3-7d |
| X | 6-24h |
| TikTok cache | 7-14d |
| Pinterest cache | 14-30d |
| Rednote/LinkedIn manual | 7-30d |

### 12.2 Demand Seed Cache

对常见 built app category + end-user ICP 组合缓存 seed pool:

```text
ecommerce + shopify_seller + product_page_conversion
creator_tool + content_creator + cold_start
local_business + consumer + conversion
```

这样运行时不必每次从零发散。

## 13. 稳定性设计

### 13.1 硬超时

```text
total_probe_budget = 8s
per_platform_budget = 2s
per_request_budget = 1s
```

任何 source 超时直接 fallback,不重试长链路。

### 13.2 并行执行

平台 probe 并行执行,谁先回来用谁。不要串行等所有平台。

### 13.3 限流保护

- 每个平台每次最多 6-8 条结果。
- 每次最多 20-30 条总结果。
- 相同 seed 24h 内优先读 cache。

### 13.4 Typed Output

每个 probe adapter 必须返回统一结构:

```json
{
  "status": "success | timeout | unavailable | error | cache_only",
  "results": [],
  "errors": [],
  "source_confidence": "high | medium | low"
}
```

Stage 2 不读取 adapter 私有字段。

## 14. 质量设计

### 14.1 不追求全量,追求相关

运行时只要证明“有一些近期相关信号”,不是证明“全平台趋势全貌”。

### 14.2 Seed 多样性

每次至少覆盖:

- 2 个 pain seed
- 2 个 JTBD seed
- 1 个 workaround seed
- 1 个 outcome seed

避免只搜产品关键词。

### 14.3 反证机制

如果某个平台 probe 返回高热但低相关内容,要记录 rejected reason:

```json
{
  "rejected": true,
  "reason": "high activity but audience is consumer entertainment, no ICP pain overlap"
}
```

### 14.4 文案约束

- runtime evidence fresh:可以写“近期在 X/Reddit/YouTube 上观察到……”
- cache fresh:可以写“最近样本显示……”
- cache stale:只能写“适合采用 evergreen angle……”
- no evidence:不能写趋势判断

## 15. MVP 工程落地

### Week 1: 最小闭环

实现:

- `generate_demand_seeds.py`
- `probe_reddit.py`
- `probe_youtube.py`
- `runtime_opportunity_probe.py`
- `probe_cache/`

输出:

```text
run_outputs/opportunity_probe.json
```

### Week 2: 接 Stage 2

- Stage 2 读取 `opportunity_probe.json`
- fit_score 增加 `probe_status` 和 `evidence_freshness`
- Stage 5 增加 probe warning

### Week 3: Cache/manual 平台

- TikTok cache importer
- Rednote manual importer
- LinkedIn manual importer
- Pinterest manual importer

### Week 4: 质量评测

用 20 个真实 builder app prompt 测试:

- probe 是否 8 秒内完成
- 失败是否可降级
- seed 是否像 built app 终端用户的需求语言
- 平台排序是否合理
- 内容是否避免伪热点

## 16. 推荐最终取舍

| 问题 | 取舍 |
|---|---|
| 实时性 | 只对 Reddit/YouTube/可配置 X 做轻量 runtime probe;其它平台用 cache/manual |
| 稳定性 | probe 失败不阻塞;所有 source 有 status 和 fallback |
| 质量 | seed 从 built app end-user ICP/JTBD/pains 生成,但只取 top-k,避免全量发散 |
| 成本 | 单次最多 3-5 平台、6-12 seeds、20-30 results |
| 合规 | 不登录抓取,不用第三方 scraping API |
| 可解释 | 每个平台输出 evidence refs、probe_status、confidence |

## 17. 最重要的修正

“这批内容/话题”不再是预先采集的大型趋势池,而是运行时生成的 **small, bounded, app-specific opportunity probe set**。

它来自:

```text
Built app end-user ICP + JTBD + pains + value props
  -> 6-12 demand-language seeds
  -> 3-5 preselected platforms
  -> bounded top-k runtime/cache probe
  -> evidence pack
```

这条链路短、可控、可缓存、可降级。它没有全量趋势系统那么“完整”,但更适合 SMB builder 的即时生成场景,也更接近工程上能稳定跑起来的方案。



