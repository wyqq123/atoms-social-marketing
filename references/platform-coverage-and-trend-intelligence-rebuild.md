# 社媒平台覆盖、趋势情报与 Fit Score 轻量稳定重构方案 v3

## 1. 这版方案解决什么

上一版方案的问题不是“趋势情报不重要”,而是把趋势情报做成了主链路大脑:先收集大量平台趋势,再在趋势快照里写入 `fit_verticals`、`fit_goal_types`、`relevance_to_atoms` 这类 app-specific 适配判断。这样会产生三个严重问题:

1. **复用性低**:同一条趋势对不同 app 的 ICP、痛点、客单价、转化目标可能完全不同。
2. **证据不稳**:多数平台无法稳定获得完整 audience demographic 和消费偏好数据,硬做会依赖猜测。
3. **链路脆弱**:用户触发 skill 时才知道 app 上下文,如果此时再做多平台、多 query、多轮扩展和聚类,很容易超时或失败。

v3 的目标是把系统改成轻量、稳定、可解释、可降级的版本:

```text
App End-User ICP Vector
  ×
Platform Context Layers
  ×
Optional Just-in-time Demand Evidence
  ->
stable_fit_score + realtime_adjustment + score_confidence
```

也就是说:

- 平台上下文负责回答“这个平台长期是什么机制、什么心智、什么入口、什么限制”。
- 数据获取层负责回答“哪些平台数据能实时拿,哪些只能缓存/授权/人工导入”。
- 轻量需求探针负责回答“对当前 app,现在能否找到少量真实需求表达”。
- Fit Score 负责在运行时计算 built app end-user ICP 与平台/证据之间的交集。

## 2. 核心原则

1. **适配度不写进趋势数据**:趋势或平台数据只记录客观信号和低阶归纳,不记录“适合某垂类/某目标/Atoms”。
2. **先稳定评分,再可选实时校准**:`stable_fit_score` 必须在没有实时数据时也能完成;实时数据只做 `-5..+10` 小幅修正。
3. **先选平台,再查数据**:不做全平台实时趋势采集。先用稳定层选最多 3 个平台,再对这些平台做轻量 probe。
4. **先生成需求探针,不生成泛话题**:probe 来自 built app end-user ICP / pain / JTBD / alternatives / trigger moments,不是平台热榜,也不是 app 功能词直搜。
5. **数据可获得性优先**:默认只自动跑 YouTube、Reddit、Web Search fallback。其他平台走 cache、授权数据或人工导入。
6. **无证据不写当前趋势**:没有 `usable` evidence 时,下游只能使用 evergreen platform strategy。
7. **证据可追溯**:每个动态判断必须带 `evidence_refs`、`known_biases` 和 `probe_status`。

## 3. 总体架构

```text
Stage 1 Intent & ICP
  - intent_profile
  - app_icp_vector
  - demand_probe_pack(max 8)

Stage 2a Platform Shortlist
  - platform_registry
  - stable_platform_profiles
  - max 3 platforms for optional probe

Stage 2b Optional Demand Probe
  - official API / authorized data / cache / web fallback
  - hard timeout: default 8s, max 12s
  - opportunity_evidence_brief per platform

Stage 2c Fit Score
  - stable_fit_score: 0..100
  - realtime_adjustment: -5..+10
  - fit_score: 0..100
  - score_confidence and wording gates

Stage 3-5 Launch Pack
  - use recommended_surfaces, angle constraints, confidence, risks
```

主链路降级路径:

```text
no realtime evidence -> stable platform strategy -> confidence <= medium -> no current-trend wording
```

## 4. 社媒平台上下文信息分层

平台上下文不是一个“趋势库”,而是一组分层对象。每一层都解决不同问题,也有不同更新频率和数据来源。

| 层级 | 对象 | 解决的问题 | 更新频率 | 是否 app-specific |
|---|---|---|---|---|
| L0 | `platform_coverage_registry` | 系统覆盖哪些平台、哪些市场、哪些数据入口可用 | 30-90 天或 adapter 变化时 | 否 |
| L1 | `stable_platform_profile` | 平台长期心智、surface、分发、转化、风险是什么 | 30-90 天 | 否 |
| L2 | `data_access_profile` | 每个平台哪些数据能实时拿、缓存拿、授权拿、人工拿 | 30-90 天或政策变化时 | 否 |
| L3 | `demand_probe_pack` | 当前 built app 应该用哪些终端用户需求语言去找需求表达 | 每次运行生成 | 是 |
| L4 | `opportunity_evidence_brief` | 当前 app 在某平台是否找到少量真实需求证据 | 每次运行或缓存 24-72 小时 | 是 |
| L5 | `trend_observation_cache` | 可复用的客观近期样本,不含 app fit 判断 | 1-14 天 | 否 |
| L6 | `platform_fit_score` | 当前 app 与平台机会的适配评分 | 每次运行生成 | 是 |

### 4.1 L0: Platform Coverage Registry

`platform_coverage_registry` 是平台覆盖控制表。它告诉系统“哪些平台可以生成内容、哪些可以实时探针、哪些只能使用缓存或手动情报”。

核心字段:

| 字段 | 含义 | 作用 | 示例 |
|---|---|---|---|
| `platform_id` | 平台唯一标识 | 下游路由和输出 key | `reddit`, `youtube`, `tiktok` |
| `supported_markets` | 默认支持市场 | 判断地域语言可用性 | `["US", "UK", "CN"]` |
| `supported_languages` | 支持语言 | 校准内容语言和检索语言 | `["en", "zh"]` |
| `content_surfaces` | 可生成/推荐的内容入口 | Stage 3 选择内容形态 | `subreddit_post`, `shorts`, `pin` |
| `renderer_support` | 是否已有内容渲染模板 | 判断生产可行性 | `text`, `image`, `short_video` |
| `realtime_probe_mode` | 运行时数据能力 | 决定是否进入 Stage 2b | `api`, `cache`, `manual`, `unsupported` |
| `data_policy` | 合规数据边界 | 防止违规抓取 | `official_api_only`, `authorized_only` |
| `default_confidence_cap` | 无动态证据时置信上限 | 控制输出保守性 | `medium` |

示例:

```json
{
  "platform_id": "reddit",
  "supported_markets": ["US", "UK", "CA", "AU"],
  "supported_languages": ["en"],
  "content_surfaces": ["subreddit_post", "comment_reply", "discussion_thread"],
  "renderer_support": ["text", "link_preview"],
  "realtime_probe_mode": "api",
  "data_policy": "official_api_or_public_web_summary",
  "default_confidence_cap": "medium"
}
```

### 4.2 L1: Stable Platform Profile

`stable_platform_profile` 记录平台长期稳定机制。它不回答“这个 app 是否适合”,只回答“平台通常如何工作”。

核心对象:

| 对象 | 含义 | 作用 | 示例属性 |
|---|---|---|---|
| `audience_pools` | 平台可稳定触达的人群池 proxy | 给 ICP 交集提供基础候选 | roles, interests, communities, market strength |
| `mindset_modes` | 用户打开平台时的主心智 | 计算 `mindset_intent_fit` | entertainment, search, learning, advice, professional identity |
| `surface_map` | 平台原生内容入口 | 推荐 surfaces 和判断触达入口 | feed, search, community, profile, short_video, long_video |
| `distribution_mechanics` | 平台分发机制 | 计算小账号触达与内容生命周期 | recommendation, search, follower graph, community gate |
| `content_format_affordances` | 哪些表达方式天然适合平台 | 计算 `value_expression_fit` | demo, tutorial, before_after, review, story, meme |
| `conversion_affordances` | 平台支持的 CTA 和转化路径 | 计算 `conversion_path_fit` | bio link, description link, comment CTA, DM |
| `production_requirements` | 合格内容生产门槛 | 计算 `production_feasibility` | video editing, screenshots, founder voice, visual quality |
| `policy_and_norms` | 平台规则和社区禁忌 | 计算风险和负向调整 | anti-promotion, link limits, ad disclosure, AI content risk |
| `measurement_options` | 可衡量能力 | 评估 tracking 可行性 | UTM, platform insight, pixel, GA4, manual tracking |

示例片段:

```json
{
  "platform_id": "youtube",
  "mindset_modes": [
    { "mode": "search_learning", "strength": "high", "fit_goals": ["education", "problem_solution", "demo_to_signup"] },
    { "mode": "entertainment", "strength": "medium", "fit_goals": ["awareness"] }
  ],
  "surface_map": [
    {
      "surface": "youtube_search",
      "content_formats": ["how_to_video", "comparison", "tutorial"],
      "small_account_access": "medium",
      "content_half_life": "long",
      "cta_routes": ["description_link", "pinned_comment"]
    }
  ],
  "policy_and_norms": {
    "commercial_content_tolerance": "medium-high",
    "risk_notes": ["claims need proof", "avoid misleading before-after claims"]
  }
}
```

注意:`fit_goals` 在 stable profile 中只能描述平台心智通常承接的动作类型,不是趋势快照字段,也不是对某个 app 的推荐结论。

### 4.3 L2: Data Access Profile

`data_access_profile` 记录每个平台的数据获取现实边界。它回答“我们到底能拿到什么,多久能拿到,失败时怎么办”。

核心字段:

| 字段 | 含义 | 作用 | 示例 |
|---|---|---|---|
| `runtime_access_mode` | 运行时是否自动取数 | 决定 Stage 2b 是否执行 | `realtime_api`, `cache_only`, `authorized_only`, `manual_only` |
| `available_signals` | 可获得信号 | 决定 brief 字段质量 | title, comments, views, likes, published_at |
| `unavailable_signals` | 不可获得信号 | 防止模型编造 | demographic_ground_truth, watch_duration |
| `source_priority` | 数据源优先级 | 统一 adapter 选择 | official_api > authorized_insight > cache > manual |
| `freshness_sla` | 数据新鲜度要求 | 控制是否可写 why_now | 24h, 72h, 7d |
| `rate_limit_risk` | 速率和权限风险 | 控制降级路径 | low, medium, high |
| `fallback_mode` | 失败时兜底 | 保证主链路不中断 | use_cache, skip_probe, web_summary |
| `compliance_notes` | 合规边界 | 禁止违规 scraping | no login-state scraping |

MVP 平台数据获取策略:

| 平台 | 默认运行时方式 | 可获得信号 | 不建议做什么 | 默认用途 |
|---|---|---|---|---|
| YouTube | 官方 API 或公开 oEmbed/cache | title, description, published_at, view/like/comment stats | 每次大规模爬频道或评论 | 搜索/教程/评测需求验证 |
| Reddit | Reddit API 或公开网页摘要 | title, subreddit, score, comments, created_at, text excerpt | 批量抓私有/登录态内容 | 痛点表达、社区入口、反营销风险 |
| Web Search fallback | 搜索公开网页摘要 | title, snippet, url, source | 当作平台全量趋势 | 找公开证据和补充入口 |
| X | 授权 API 或 cache/manual | post text, engagement, author/context when available | 默认无授权实时抓取 | build-in-public/early adopter 线索 |
| TikTok | Creative Center/cache/manual | trend/category样本、热门创意结构 | request-time 抓 UI | 视觉消费和短视频表达参考 |
| Instagram | Graph/authorized insight/cache/manual | 自有账号表现、内容样本 | 全站实时抓取 | 视觉品牌、ecom、creator proof |
| LinkedIn | Marketing API/authorized/cache/manual | 自有页数据、行业话题样本 | 无授权抓 profile/feed | B2B 心智与专业信任 |
| Pinterest | Trends/API/cache/manual | keyword/category trend, pins structure | 依赖实时抓页面 | 长尾搜索、视觉种草 |
| Rednote/抖音 | 官方商业工具/cache/manual | 类目、笔记/短视频样本、人工观察 | request-time 爬取 | CN 市场消费心智和内容样式 |

### 4.4 L3: Demand Probe Pack

`demand_probe_pack` 是运行时对象,由 Stage 1 根据当前 built app 生成。它不是“话题库”,而是一组终端用户需求语言检索意图,用来找 built app 目标用户如何表达需求。

Probe 来源:

| 来源 | 含义 | 示例 |
|---|---|---|
| End-user identity | 目标用户如何称呼自己 | Shopify seller, freelancer, Shopify seller |
| Pain | 用户痛点的自然语言表达 | landing page not converting, clients not paying |
| JTBD | 用户想完成的任务 | launch product, automate invoices |
| Alternative | 当前替代方案或竞品 | spreadsheet, Notion template, Canva, Zapier |
| Trigger moment | 需求爆发时机 | first client, Black Friday, product launch |
| Desired outcome | 用户想要的结果 | get more leads, save admin time |

示例:

```json
{
  "app_id": "runtime",
  "generated_at": "2026-07-26T00:00:00Z",
  "icp_summary": "Shopify sellers improving product-page conversion",
  "probes": [
    {
      "probe_id": "p01",
      "intent": "pain_expression",
      "query": "Shopify seller product page traffic no sales",
      "language": "en",
      "market": "US",
      "source_terms": {
        "end_user_identity": ["Shopify seller"],
        "pain": ["landing page not converting"],
        "jtbd": ["launch product"],
        "alternative": ["Carrd", "Webflow", "Notion page"]
      },
      "priority": 0.92,
      "platform_surfaces_hint": ["reddit_search", "youtube_search"],
      "must_not_include": ["product name", "brand slogan"]
    }
  ],
  "constraints": {
    "max_probes": 8,
    "prefer_user_language": true,
    "avoid_product_keywords_only": true
  }
}
```

### 4.5 L4: Opportunity Evidence Brief

`opportunity_evidence_brief` 是 Stage 2 真正读取的轻量实时证据对象。它是 app-specific,但不是评分本身。

字段说明:

| 字段 | 含义 | 作用 | 示例 |
|---|---|---|---|
| `platform` | 平台 | 对应 scores key | `reddit` |
| `status` | 可用状态 | 控制修正和措辞 | `usable`, `weak`, `unavailable`, `timeout`, `error` |
| `freshness` | 新鲜度 | 控制 why_now | `realtime`, `cache_24h`, `cache_7d` |
| `matched_probe_ids` | 命中的 probes | 追溯需求来源 | `["p01", "p03"]` |
| `audience_clues` | 可观察人群线索 | 校准 ICP 交集 | `Shopify sellers`, `store operators` |
| `pain_clues` | 痛点表达 | 校准 Pain/JTBD overlap | `traffic but no signups` |
| `content_clues` | 内容消费线索 | 校准 angle 和 format | `specific problem title`, `comment-heavy discussion` |
| `distribution_clues` | 分发入口线索 | 校准 surface 和风险 | `subreddit search`, `comment-first entry` |
| `activity_clues` | 轻量活跃度 | 决定实时修正幅度 | volume, velocity, engagement, saturation |
| `recommended_use` | 证据用途边界 | 防止过度借势 | `calibrate wording, not claim broad trend` |
| `confidence` | brief 可信度 | 影响 score_confidence | `medium-high` |
| `evidence_refs` | 证据引用 | 可审计 | `reddit:p01:r01` |
| `known_biases` | 已知偏差 | 降低过度自信 | `selected subreddit bias` |

示例:

```json
{
  "platform": "reddit",
  "status": "usable",
  "freshness": "realtime",
  "evidence_count": 7,
  "matched_probe_ids": ["p01", "p03"],
  "audience_clues": ["Shopify sellers", "store operators", "problem-aware users"],
  "pain_clues": ["traffic but no signups", "unclear positioning", "manual launch workflow"],
  "content_clues": ["specific problem title", "transparent founder answer", "long comments"],
  "distribution_clues": ["subreddit search", "comment-first entry", "anti-promotion norm"],
  "activity_clues": {
    "volume": "medium",
    "velocity": "fresh",
    "engagement": "high-comment-depth",
    "saturation": "medium"
  },
  "recommended_use": "calibrate angle and wording, not claim broad platform trend",
  "confidence": "medium-high",
  "evidence_refs": ["reddit:p01:r01", "reddit:p03:r02"],
  "known_biases": ["search_result_bias", "no demographic ground truth"]
}
```

### 4.6 L5: Trend Observation Cache

`trend_observation_cache` 是可选增强,用于降低实时失败率。它不是主链路必需品,也不按 app 预写 fit。

它只记录平台/市场/语言/需求簇下的客观观察:

| 字段 | 含义 | 示例 |
|---|---|---|
| `cache_key` | platform + market + language + demand_cluster + week | `reddit|US|en|landing-page-conversion|2026-W31` |
| `source_mix` | 来源组合 | official_api, manual_review |
| `observed_surfaces` | 观察入口 | subreddit_search, youtube_search |
| `topic_or_need_label` | 低阶需求标签 | landing page conversion pain |
| `audience_observed` | 人群线索 | self descriptions, communities, role hints |
| `content_consumption_observed` | 内容消费方式 | advice, comparison, tutorial, teardown |
| `distribution_observed` | 分发和入口 | small_account_access, gatekeepers, policy risk |
| `trend_metrics` | 平台内归一指标 | volume_index, velocity_index, engagement_index |
| `evidence` | 来源引用 | URLs/API ids/manual note ids |
| `known_biases` | 偏差 | selected community bias, no demographic ground truth |
| `expires_at` | 过期时间 | 2026-08-02 |

缓存 TTL 建议:

| 数据 | TTL |
|---|---:|
| Reddit/YouTube probe raw result | 24-72 小时 |
| Opportunity evidence brief | 24 小时 |
| Manual TikTok/Instagram/LinkedIn/Rednote cache | 7-14 天 |
| Platform stable profile | 30-90 天 |

### 4.7 L6: Platform Fit Score

`platform_fit_score` 是运行时计算结果,不是平台数据资产。

```text
stable_fit_score = stable platform profile + platform registry + app_icp_vector
realtime_adjustment = opportunity_evidence_brief based adjustment
fit_score = clamp(stable_fit_score + realtime_adjustment, 0, 100)
```

输出必须包括:

- `stable_fit_score`
- `realtime_adjustment`
- `fit_score`
- `score_confidence`
- `probe_status`
- `subscores`
- `audience_intersection`
- `recommended_surfaces`
- `why_this_platform`
- `why_now`(只有 usable evidence 才能写当前机会)
- `risks`
- `_evidence_refs`

## 5. App End-User ICP Vector 的作用和设计

### 5.1 App End-User ICP Vector 是什么

`app_icp_vector` 是把 built app 上下文转成可计算的终端用户与增长约束表示;它不是 builder 自画像。它不是 marketing persona 文案,而是 Stage 2 做平台交集计算的结构化输入。

它回答 8 个问题:

1. 目标用户在哪里,用什么语言。
2. 目标用户是谁,处于什么业务/生活场景。
3. 他们要完成什么任务。
4. 他们有什么高优先级痛点。
5. 他们现在用什么替代方案。
6. 这个 app 的独特价值机制是什么。
7. 本次内容希望用户完成什么动作。
8. builder 现在有什么素材和生产能力（只进入 production constraints,不得进入 end_user_identity）。

### 5.2 App End-User ICP Vector 对下游的作用

| 下游模块 | 使用方式 |
|---|---|
| Stage 2a Platform Shortlist | 用 ICP、目标、素材能力先选最多 3 个最可能平台 |
| Stage 2b Demand Probe | 生成终端用户需求语言 query,避免用产品功能词随机搜索 |
| Stage 2c Fit Score | 计算 built app end-user ICP 与平台上下文/证据的交集 |
| Stage 3 Angle Strategy | 决定内容 angle、surface、CTA 和风险边界 |
| Stage 4 Asset Generation | 决定文案语气、素材优先级和证明方式 |
| Stage 5 QA | 检查是否伪造趋势、是否偏离目标用户和转化目标 |

### 5.3 App End-User ICP Vector Schema

`app_icp_vector` 的主契约以 `references/pipeline/stage-1-intent.md` 为准。本节只保留设计来源摘要:它是 built app 终端用户 ICP、built app 能力、value proposition、conversion goal 和 builder production constraints 的结构化输入,不是 persona 文案。

Key schema decisions:

- `end_user_identity` 指 built app 终端用户,不得从 builder 自称推断。
- Built app 代码/UI/描述先进入 `app_capability_summary`,再辅助生成 JTBD/pain hypothesis。
- `jtbd`、`pains`、`alternatives` 使用 item-level `source` 和 `confidence`;没有外部 evidence 时只能是 hypothesis。
- `pains` 拆分 `synthetic_pain_language_examples` 与 `observed_pain_language_examples`。
- `alternatives` 拆分 `workaround_categories` 与 `named_competitor_candidates`;竞品名只来自用户输入、cache、授权数据或 web evidence。
- `value_proposition` 保留 `key_selling_point_raw`,并另拆 `user_benefit` 和 `unique_mechanism`,避免把 slogan 当机制。
- `builder_context` / `production_constraints` 只描述 builder 可生产什么和 built app 有什么 proof assets,不得进入 end-user ICP。

### 5.4 Stage 1 如何构建 App End-User ICP Vector

Stage 1 应在输出 `intent_profile` 的同时输出 `app_icp_vector`。构建步骤如下:

1. **读取明示输入**:优先读取 `positioning.target_audience`、`positioning.key_selling_point`、`positioning.promo_goal`、`app_context.description`、`app_context.category`、`target_market`。
2. **归纳 built app 能力**:从 app context、builder prompt、可读取的 built app UI/代码摘要生成 `app_capability_summary`;这一步只描述产品能力和可见 workflow。
3. **抽取并归属线索**:从 `builder_prompt` 中区分 app end-user 线索、built app 线索和 builder 生产上下文;三者不得混写。
4. **生成 JTBD/pain/alternatives hypothesis**:基于 target audience、key selling point、app capability summary 生成,并标注 `source` / `confidence`。没有 evidence 时不得写成真实用户原话或真实竞品。
5. **拆分功能语言和需求语言**:功能词进入 `app_capability_summary` / `value_proposition`;终端用户会搜索、抱怨或提问的表达进入 pains/JTBD 和 `demand_probe_pack`。
6. **校准 GA4/授权数据**:GA4 只校准 market、device、source、engagement、conversion path;不得覆盖 positioning 中明示的目标用户。
7. **记录 confidence 和冲突**:每个高影响字段都要标 `confidence`;若 positioning、builder_prompt、GA4 冲突,以 positioning 为主并记录 rationale。

Stage 1 输出建议:

```json
{
  "intent_profile": {},
  "app_icp_vector": {},
  "demand_probe_pack": {
    "probes": []
  }
}
```

### 5.5 Demand Probe 生成规则

使用模板池 + query variants,不做多轮扩展。`query` 保留为兼容用 primary query,`query_variants` 用于长尾精准、关键词组召回和 platform-native rewrite。

模板池:

```text
{end_user_identity} {pain}
{end_user_identity} how to {jtbd}
{pain} {workaround_category}
best way to {desired_outcome} for {end_user_identity}
{trigger_moment} {pain}
{workaround_category} vs {desired_outcome}
```

筛选规则:

- 最多 8 个 probes。
- 至少 50% probes 来自 pain 或 JTBD。
- 至少包含 2 个 `long_tail_precision` variants 和 2 个 `keyword_recall` variants,用于平衡精准度与召回。
- 每个 probe 必须至少包含 end_user_identity/pain/JTBD/workaround/trigger/outcome 中的 2 类。
- 优先终端用户需求语言,不是产品功能语言、builder 自画像或 Atoms 平台词。
- 不包含 product name 或 brand slogan,除非用户明确要求做品牌监测。
- Named competitors 只能来自用户输入、cache、授权数据或 web evidence;否则只用 workaround category。
- 每个 probe 带 `priority`、`source_terms` 和 `expected_evidence_type`。

## 6. 轻量趋势洞察如何设计

这里的“趋势洞察”不再指全平台趋势监测,而是两类轻量情报:

1. **Evergreen platform intelligence**:平台长期上下文,来自 registry/playbook/manual research。
2. **Just-in-time demand evidence**:针对当前 app 的少量实时/缓存需求证据,来自最多 3 个平台、最多 8 个 probes。

### 6.1 数据获取流程

```text
Input app context
  -> Stage 1 builds app_icp_vector + demand_probe_pack
  -> Stage 2a stable shortlist picks max 3 platforms
  -> Stage 2b chooses adapter by data_access_profile
  -> run 2-3 queries per platform under 8s timeout
  -> collect top 5-8 lightweight results per query
  -> summarize opportunity_evidence_brief
  -> Stage 2c applies realtime_adjustment and confidence gates
```

### 6.2 Probe Budget

| 项 | 上限 |
|---|---:|
| Demand probes per request | 8 |
| Platforms probed | 3 |
| Queries per platform | 3 |
| Results per query | 5-8 |
| Total fetched items | 60 以内 |
| Hard timeout | 默认 8 秒,最大 12 秒 |
| LLM summarization calls | 1 次合并 summarizer |

### 6.3 Adapter 选择规则

```text
if platform.realtime_probe_mode == api and credentials available:
    run official adapter
elif fresh cache exists:
    use cache
elif platform supports public web summary fallback:
    run web fallback with strict result limit
else:
    skip probe and mark probe_status = unavailable
```

禁止:

- 登录态 scraping。
- 绕过平台访问限制。
- 运行时全站抓取。
- 无来源地把 LLM 猜测写成动态事实。

### 6.4 Realtime Probe Result

raw result 只保存轻量字段,避免过度处理:

```json
{
  "platform": "youtube",
  "probe_id": "p02",
  "query": "how to improve product page conversion for Shopify seller",
  "status": "success",
  "results": [
    {
      "result_id": "r01",
      "surface": "youtube_search",
      "title": "How I launched my SaaS landing page and got first users",
      "url": "https://www.youtube.com/watch?v=...",
      "published_at": "2026-07-24T00:00:00Z",
      "metrics": {
        "views": 18400,
        "likes": 720,
        "comments": 81
      },
      "text_excerpt": "short excerpt only",
      "evidence_type": "official_api"
    }
  ],
  "latency_ms": 530,
  "known_biases": ["search_result_bias", "no_viewer_demographic_ground_truth"]
}
```

## 7. Fit Score v3

Stage 2 使用稳定分 + 实时修正,与 `references/pipeline/stage-2-fit.md` 保持一致。

```text
stable_fit_score =
  ICP Reach & Quality       30
+ Mindset & Intent Fit      20
+ Value Expression Fit      15
+ Distribution Feasibility  15
+ Conversion Path Fit       10
+ Production Feasibility    10

realtime_adjustment = -5..+10
fit_score = clamp(round(stable_fit_score + realtime_adjustment), 0, 100)
```

### 7.1 Stable Fit Score 维度

| 维度 | 分值 | 主要数据来源 |
|---|---:|---|
| ICP Reach & Quality | 30 | app_icp_vector, stable_platform_profile.audience_pools, surface_map, GA4/授权数据 |
| Mindset & Intent Fit | 20 | app_icp_vector.conversion_goal, stable_platform_profile.mindset_modes |
| Value Expression Fit | 15 | app_icp_vector.value_proposition, production_constraints, content_format_affordances |
| Distribution Feasibility | 15 | distribution_mechanics, surface_map, data_access_profile, opportunity_evidence_brief |
| Conversion Path Fit | 10 | conversion_affordances, measurement_options, GA4/UTM |
| Production Feasibility | 10 | production_requirements, builder assets, renderer_support |

### 7.2 Realtime Adjustment

| 证据 | 调整 |
|---|---:|
| 找到 2+ 高相关需求表达,且互动活跃 | +6 到 +10 |
| 找到相关内容但活动弱 | +2 到 +5 |
| 找到内容但 ICP 或 pain 弱相关 | 0 |
| 发现平台/社区强反营销或入口不适合 | -3 到 -5 |
| 探针失败/超时/未运行 | 0,但 confidence 降级 |

实时修正只允许小幅影响分数。若 `stable_fit_score < 45`,除非有强授权数据且用户明确指定平台,`fit_score` 最高不得超过 55。

### 7.3 Confidence 与措辞闸门

| 条件 | `score_confidence` | 下游措辞 |
|---|---|---|
| 稳定层完整 + usable 实时证据或强授权数据 | high / medium-high | 可以写具体近期机会,必须引用 evidence |
| 稳定层完整 + weak/partial 证据 | medium-high / medium | 可写“观察到少量相关表达”,不能夸大趋势 |
| 只有稳定层 | medium | 只能写 evergreen strategy |
| playbook/registry 缺失或证据冲突 | low | 输出 warning,降低投入建议 |

## 8. 平台短名单如何选择

Stage 2a 先用稳定层做轻量 shortlist,最多 3 个平台进入实时探针。

```text
shortlist_score =
  ICP stable overlap
+ mindset/goal compatibility
+ content format feasibility
+ conversion path feasibility
+ market/language availability
- production difficulty
- policy/community friction
```

示例启发:

| App 类型/目标 | 优先候选 | 说明 |
|---|---|---|
| AI/SaaS/build-in-public | X, Reddit, YouTube, LinkedIn | early adopter、问题讨论、教程心智较强 |
| Ecom/visual product | TikTok, Instagram, Pinterest, Rednote | 视觉表达、种草、搜索长尾更重要 |
| B2B/professional buyer | LinkedIn, YouTube, X, Reddit | 专业信任、教程证明、问题验证 |
| Local/service business | Instagram, Facebook, YouTube, Google/Web fallback | 本地发现、服务证明、搜索意图 |
| Creator/knowledge product | YouTube, TikTok, Instagram, X | 教育内容、人格信任和短内容分发 |

这些只是 shortlist seed,不是最终 fit_score。最终仍按 Stage 2c 规则算分。

## 9. 数据获取脚本工程实现方案

Just-in-time demand evidence 的脚本目标不是“抓趋势大全”,而是在用户调用 skill 后,基于当前 `app_icp_vector` 和 `demand_probe_pack`,对少数候选平台获取最小可用证据包。

工程目标:

- 运行时最多探针 3 个平台。
- 每个平台最多 2-3 个 query。
- 每个 query 最多 5-8 条结果。
- 总 fetched items 控制在 60 以内。
- 默认 8 秒硬超时,最大 12 秒。
- 任一 adapter 失败不影响主链路,只输出 `probe_status` 和 warning。
- 输出只进入 `opportunity_evidence_brief`,不直接生成 `fit_score`。

### 9.1 推荐目录结构

```text
scripts/platform_intel/
  README.md                         # 可选,工程内部说明;skill 可不加载
  run_demand_probe.py               # 运行时主入口
  build_demand_probe_pack.py        # Stage 1 可调用,也可内嵌到 Stage 1
  select_platform_shortlist.py      # Stage 2a 稳定短名单
  summarize_opportunity_brief.py    # 合并 raw results -> brief
  validate_probe_output.py          # schema + 禁用字段 + evidence refs 校验
  cache_store.py                    # 文件/kv cache 读写
  rate_limit.py                     # adapter 级速率和预算控制
  query_planner.py                  # probe -> platform-native query
  models.py                         # pydantic/dataclass 数据模型
  adapters/
    base.py                         # PlatformProbeAdapter 抽象类
    youtube_probe.py                # MVP: official API
    reddit_probe.py                 # MVP: official API / public JSON fallback
    web_search_probe.py             # MVP: 搜索公开网页摘要
    cached_platform_probe.py        # TikTok/IG/LinkedIn/Rednote 等缓存/人工导入
    x_probe.py                      # optional: 仅授权 token 可用时启用
    pinterest_probe.py              # optional: Trends API/cache
```

如果这是作为 Codex skill 的资源,`README.md` 可以不创建;脚本行为应由本文和 schema 约束。

### 9.2 运行时主命令

```bash
python scripts/platform_intel/run_demand_probe.py \
  --app-icp run_outputs/app_icp_vector.json \
  --demand-probes run_outputs/demand_probe_pack.json \
  --platform-registry data/platform_registry.json \
  --platform-scope auto \
  --max-platforms 3 \
  --queries-per-platform 3 \
  --results-per-query 6 \
  --timeout-ms 8000 \
  --cache-dir .cache/social_intel \
  --output run_outputs/opportunity_evidence_briefs.json
```

可选参数:

| 参数 | 含义 | 默认 |
|---|---|---|
| `--platform-scope` | 用户指定平台或 auto | `auto` |
| `--max-platforms` | 进入实时 probe 的平台数 | `3` |
| `--queries-per-platform` | 每个平台 query 数 | `3` |
| `--results-per-query` | 每个 query 返回结果数 | `6` |
| `--timeout-ms` | 全局硬超时 | `8000` |
| `--fresh-cache-max-age-hours` | 可复用缓存年龄 | `24` |
| `--allow-web-fallback` | 是否允许公开网页摘要兜底 | `true` |
| `--no-network` | 禁止实时网络,只读 cache/manual | `false` |
| `--debug-save-raw` | 是否保存 raw result 调试文件 | `false` |

### 9.3 统一 Adapter 接口

每个平台 adapter 都实现同一个窄接口,避免把平台差异泄露到 Stage 2。

```python
class PlatformProbeAdapter:
    platform_id: str
    access_mode: str  # realtime_api | cache_only | authorized_only | manual_only | unsupported

    def preflight(self, env: dict, registry: dict) -> ProbeCapability:
        """检查 credential、政策、区域、语言、速率预算。不得发起重请求。"""

    def plan_queries(self, probes: list[DemandProbe], max_queries: int) -> list[PlatformQuery]:
        """把 demand probes 转成平台原生 query。"""

    async def fetch(self, query: PlatformQuery, limit: int, timeout_ms: int) -> ProbeFetchResult:
        """取轻量结果。失败必须返回 error/timeout 状态,不得抛出到主链路。"""

    def normalize(self, raw: ProbeFetchResult) -> list[EvidenceItem]:
        """归一成通用 evidence item。"""
```

关键约束:

- adapter 不计算 `fit_score`。
- adapter 不生成营销建议。
- adapter 不写 `fit_verticals`、`fit_goal_types`、`relevance_to_atoms`。
- adapter 只能输出 raw evidence 和可解释的 source metadata。
- adapter 必须显式声明不可获得字段,如 demographic ground truth、watch duration、buyer intent。

### 9.4 通用数据模型

#### `PlatformQuery`

```json
{
  "platform": "reddit",
  "probe_id": "p01",
  "query": "Shopify seller product page traffic no sales",
  "surface": "subreddit_search",
  "market": "US",
  "language": "en",
  "intent": "pain_expression",
  "limit": 6
}
```

#### `EvidenceItem`

```json
{
  "evidence_id": "reddit:p01:r01",
  "platform": "reddit",
  "probe_id": "p01",
  "surface": "subreddit_search",
  "title": "Landing page gets traffic but no signups",
  "url": "https://www.reddit.com/r/SaaS/...",
  "published_at": "2026-07-24T00:00:00Z",
  "text_excerpt": "short excerpt only",
  "metrics": {
    "score": 128,
    "comments": 47
  },
  "author_or_community_context": {
    "community": "r/SaaS",
    "author_public_context": null
  },
  "source_type": "official_api",
  "known_biases": ["search_result_bias", "no_demographic_ground_truth"]
}
```

#### `ProbeExecutionReport`

```json
{
  "platform": "reddit",
  "status": "success | partial | timeout | error | skipped",
  "started_at": "2026-07-26T00:00:00Z",
  "latency_ms": 760,
  "queries_attempted": 3,
  "items_fetched": 18,
  "items_after_dedupe": 12,
  "errors": [],
  "capability": {
    "access_mode": "realtime_api",
    "credential_status": "available",
    "confidence_cap": "medium-high"
  }
}
```

#### `OpportunityEvidenceBrief`

最终输出沿用 L4:

```json
{
  "platform": "reddit",
  "status": "usable",
  "freshness": "realtime",
  "evidence_count": 7,
  "matched_probe_ids": ["p01", "p03"],
  "audience_clues": ["Shopify sellers", "store operators"],
  "pain_clues": ["traffic but no signups", "manual launch workflow"],
  "content_clues": ["specific problem title", "long comments"],
  "distribution_clues": ["subreddit search", "comment-first entry"],
  "activity_clues": {
    "volume": "medium",
    "velocity": "fresh",
    "engagement": "high-comment-depth",
    "saturation": "medium"
  },
  "recommended_use": "calibrate wording, not claim broad trend",
  "confidence": "medium-high",
  "evidence_refs": ["reddit:p01:r01", "reddit:p03:r02"],
  "known_biases": ["selected community bias", "no demographic ground truth"]
}
```

### 9.5 主流程伪代码

```python
async def run_demand_probe(args):
    icp = load_json(args.app_icp)
    probes = load_json(args.demand_probes)
    registry = load_json(args.platform_registry)

    shortlist = select_platform_shortlist(
        icp=icp,
        probes=probes,
        registry=registry,
        platform_scope=args.platform_scope,
        max_platforms=args.max_platforms,
    )

    tasks = []
    for platform in shortlist:
        access = registry[platform]["data_access_profile"]
        cache_key = build_cache_key(platform, icp, probes)

        if fresh_cache_exists(cache_key, args.fresh_cache_max_age_hours):
            tasks.append(load_cached_brief(cache_key))
            continue

        adapter = load_adapter(platform)
        capability = adapter.preflight(env=os.environ, registry=registry)

        if args.no_network or not capability.can_run:
            tasks.append(skipped_brief(platform, capability.reason))
            continue

        planned_queries = adapter.plan_queries(probes.top_for(platform), args.queries_per_platform)
        tasks.append(run_adapter_with_budget(adapter, planned_queries, args))

    raw_reports = await run_with_global_timeout(tasks, timeout_ms=args.timeout_ms)
    evidence_items = normalize_and_dedupe(raw_reports)
    briefs = summarize_opportunity_briefs(evidence_items, icp, probes)
    valid_briefs = validate_or_degrade(briefs)
    write_json(args.output, valid_briefs)
```

失败策略:

| 失败 | 输出 | 下游影响 |
|---|---|---|
| 缺 credential | `status=skipped`, `reason=missing_credentials` | `realtime_adjustment=0`, confidence cap medium |
| API rate limit | 读 cache;无 cache 则 `status=unavailable` | 不阻塞 |
| 单平台 timeout | `status=timeout` | 该平台不加实时修正 |
| 部分 query 成功 | `status=partial` 或 `weak` | 只允许 +0..+5 |
| summarizer 失败 | rule-based brief | confidence 降级 |
| schema 校验失败 | degrade to unavailable | 禁止污染 Stage 2 |

### 9.6 Query Planner 设计

`query_planner.py` 负责把通用 demand probe 转为平台原生 query。

通用规则:

- 每个平台优先选择 `priority` 高、且适合该平台心智的 probes。
- 搜索平台优先 `pain + JTBD`。
- 社区平台优先 `end_user_identity + pain`。
- 视觉/种草平台优先 `desired outcome + visual category + alternative`。
- B2B/职业平台优先 `role + trigger + outcome`。

示例:

```python
def plan_reddit_queries(probes):
    return [
        quote(p.query) for p in probes
        if p.intent in ["pain_expression", "problem_search", "alternative_comparison"]
    ][:3]


def plan_youtube_queries(probes):
    return [
        f"how to {p.source_terms['jtbd'][0]} for {p.source_terms['end_user_identity'][0]}"
        for p in probes
        if p.source_terms.get("jtbd") and p.source_terms.get("end_user_identity")
    ][:3]
```

Web fallback query 应带平台限定:

```text
site:reddit.com/r/SaaS "landing page not converting" "Shopify seller"
site:youtube.com "product page conversion" "Shopify seller"
site:pinterest.com "small business branding checklist"
```

### 9.7 平台 Adapter 实现策略

#### YouTube Adapter(MVP)

实现方式:

1. 用 `search.list` 按 query 搜索公开视频,限制 `type=video`、`maxResults=5-8`、`regionCode`、`relevanceLanguage`、可选 `publishedAfter`。
2. 从 search result 提取 video IDs。
3. 用 `videos.list` 批量拉取 `snippet,statistics,contentDetails`。
4. 归一为 `EvidenceItem`。

可用信号:

- title / description / channelTitle
- publishedAt
- viewCount / likeCount / commentCount
- duration
- region/language proxy

不可用或不应推断:

- 真实 viewer demographic
- signup intent
- 完整 watch duration,除非授权频道 analytics

适合用途:

- 教程、搜索意图、how-to、comparison、demo 内容验证。
- 长尾需求语言和标题结构校准。

官方文档参考:

- [YouTube Data API search.list](https://developers.google.com/youtube/v3/docs/search/list)
- [YouTube Data API videos.list](https://developers.google.com/youtube/v3/docs/videos/list)

#### Reddit Adapter(MVP)

实现方式:

1. 使用 Reddit OAuth 和官方 Data API。
2. 对 demand probe 执行 subreddit/global search,优先相关 subreddit。
3. 拉取 title、selftext excerpt、subreddit、score、num_comments、created_utc、permalink。
4. 可选读取 top-level comments 的少量摘要,只用于判断评论深度和反营销语境。
5. 归一为 `EvidenceItem`。

可用信号:

- title / post excerpt / subreddit
- score / comments / created time
- community context
- visible discussion depth proxy

不可用或不应推断:

- 作者真实身份、收入、购买力。
- 全 Reddit 趋势规模。
- 私有或登录态内容。

适合用途:

- 痛点表达、求助问题、替代方案比较、社区规则和反营销风险。

官方文档参考:

- [Reddit Data API Wiki](https://support.reddithelp.com/hc/en-us/articles/16160319875092-Reddit-Data-API-Wiki)
- [Reddit Data API Terms](https://redditinc.com/policies/data-api-terms)

#### Web Search Fallback(MVP)

实现方式:

1. 使用搜索 API 或已授权搜索 connector。
2. Query 必须限定公开网页和少量平台域名。
3. 只保存 title、snippet、url、source、observed_at。
4. 不抓全文、不绕登录、不批量爬取。

可用信号:

- 公开结果标题和摘要。
- 是否存在相关公开讨论入口。
- 来源域名和时间线索。

不可用或不应推断:

- 平台内部趋势热度。
- 真实互动数据。
- 人群 demographics。

适合用途:

- 当平台 API 不可用时,寻找公开证据和 surface 线索。
- 只作为 weak/medium evidence,通常不能单独触发 +6 以上修正。

#### X Adapter(Optional)

实现方式:

1. 仅在存在授权 Bearer token 且计划允许时启用。
2. 使用 recent search 搜索最近 7 天 posts。
3. Query 应限制语言、排除 retweet,并限制结果数。
4. 只保存公开 text、created_at、public_metrics、author/context 可用字段。

可用信号:

- recent posts text
- repost/reply/like/quote metrics
- language/operator query

限制:

- API 权限和成本变化大,不进入默认 MVP。
- 不得无授权抓取网页或登录态 feed。

官方文档参考:

- [X API Search Posts](https://docs.x.com/x-api/posts/search/introduction)

#### Pinterest Adapter(Optional/Cache Preferred)

实现方式:

1. 优先使用 Trends API 或人工/cache 数据。
2. 按 region、trend_type、interest/category 获取 trending keywords。
3. 将 keyword growth、time series、category context 写入 cache。
4. 运行时只读取与 demand_probe_pack 语义相邻的缓存项。

可用信号:

- trending keywords
- week/month/year growth
- normalized time series
- region/category filters

限制:

- Trends API 返回的是关键词趋势,不是 app ICP 适配结论。
- 更适合 ecom、visual product、creator template、lifestyle 场景。

官方文档参考:

- [Pinterest Trends API](https://developer.pinterest.com/docs/analytics-and-reports/trends/)

#### TikTok Adapter(Cache/Manual Preferred)

实现方式:

1. 不做 request-time UI 抓取。
2. 使用 TikTok Creative Center / TikTok One / Market Insights 的人工导出、授权能力或最近缓存。
3. 缓存内容包括 trending hashtags、top ads patterns、industry/category、region、timeframe、creative structures。
4. Stage 2b 默认通过 `cached_platform_probe.py` 读取。

可用信号:

- trend hashtag/category
- top ad creative structures
- region/timeframe
- creative pattern examples

限制:

- 公开 Creative Center 更适合人工/后台刷新,不应作为 skill 调用时硬依赖。
- 不得在运行时抓取登录态页面。

官方文档参考:

- [TikTok Creative Center](https://ads.us.tiktok.com/help/article/creative-center)
- [TikTok Trends](https://ads.us.tiktok.com/help/article/how-to-use-trends)

#### Instagram / Threads Adapter(Authorized/Cache Only)

实现方式:

1. 只对用户授权的 Business/Creator account 或自有账号 insight 取数。
2. 可读取自有内容表现、account/media insights、comments/mentions 等授权数据。
3. 非授权公共趋势不进入 request-time 默认路径。
4. 对 trends/competitor/category 样本使用人工导入或 cache。

可用信号:

- reach / impressions / profile views / engagement / saves / shares 等授权 insight。
- 自有内容评论和 media metadata。
- hashtag/media discovery 能力需按权限核验。

限制:

- 不能访问普通消费者账号数据。
- 不能把自有账号 insight 泛化为平台整体趋势。

参考:

- [Instagram API 文档集合](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api)

#### LinkedIn Adapter(Authorized/Cache Only)

实现方式:

1. 只在用户授权 LinkedIn member/page 或 organization 权限时读取自有 posts、comments、analytics。
2. B2B 趋势/行业话题默认使用人工/cache 资料。
3. 不抓公开 feed、profile 或搜索页。

可用信号:

- 自有 post impressions/reach/engagement。
- page/member posts 和评论,受权限约束。
- 专业身份心智可由 stable profile 处理。

限制:

- API 权限审批严格,公共趋势不可作为默认实时能力。
- post analytics 数字可能是估算值,需在 `known_biases` 标注。

官方文档参考:

- [LinkedIn Posts API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api)
- [LinkedIn Post Analytics Help](https://www.linkedin.com/help/linkedin/answer/a516971/post-analytics-for-your-content)

#### Rednote/小红书、抖音 Adapter(Manual/Cache Only)

实现方式:

1. 默认不做 request-time 抓取。
2. 只使用官方商业后台、品牌授权数据、人工样本或可合规复用 cache。
3. 运行时通过 `cached_platform_probe.py` 读取最近 7-14 天的类目样本。
4. 第三方采集服务不得默认接入 skill 主链路;若使用,必须经过合规和数据授权审查。

可用信号:

- 类目内容样式、热门笔记/短视频结构、评论语境、商业投放洞察。
- CN 市场语言、审美、消费心智和平台禁忌。

限制:

- 不把第三方爬虫结果当默认可信数据源。
- 不绕过登录态、风控或平台规则。

### 9.8 Cache 设计

缓存 key:

```text
platform | market | language | icp_cluster | demand_cluster | week
```

示例:

```text
reddit|US|en|solo-founder-saas|landing-page-conversion|2026-W31
```

缓存文件建议:

```text
.cache/social_intel/
  briefs/reddit/US/en/2026-W31/landing-page-conversion.json
  raw/youtube/US/en/2026-W31/p01.json
  manual/tiktok/US/en/2026-W31/creative-center-saas.json
```

缓存策略:

| 数据 | TTL | 使用方式 |
|---|---:|---|
| raw API result | 24-72 小时 | 调试、重新 summarize |
| opportunity brief | 24 小时 | Stage 2 优先读 |
| manual/cache platform sample | 7-14 天 | 非 MVP 平台默认路径 |
| stable platform profile | 30-90 天 | registry/playbook 更新 |

### 9.9 Summarizer 与规则兜底

`summarize_opportunity_brief.py` 可以使用一次 LLM 合并 summarizer,但必须受规则保护。

输入:

- `app_icp_vector`
- `demand_probe_pack`
- normalized `EvidenceItem[]`
- platform stable profile 的相关片段

LLM 只允许输出:

- audience clues
- pain clues
- content clues
- distribution clues
- activity clues
- known biases
- recommended use boundary
- confidence
- evidence refs

LLM 不允许输出:

- `fit_score`
- `realtime_adjustment`
- 平台最终 ranking
- app-specific 趋势字段
- 无证据的“当前热门”判断

规则兜底:

```python
def summarize_without_llm(items, probes):
    matched = keyword_and_embedding_match(items, probes)
    if len(matched.high_relevance_refs) >= 2 and matched.engagement_depth != "low":
        status = "usable"
    elif matched.any_relevant:
        status = "weak"
    else:
        status = "unavailable"
    return build_brief(status=status, evidence_refs=matched.refs)
```

### 9.10 Validation Gate

`validate_probe_output.py` 必须在写入 `opportunity_evidence_briefs.json` 前执行。

校验项:

| 校验 | 规则 |
|---|---|
| schema | 必须符合 `opportunity_evidence_brief_schema.json` |
| 禁用字段 | 不得包含 `fit_verticals`、`fit_goal_types`、`relevance_to_atoms` |
| evidence refs | `usable` 至少 2 个 refs |
| freshness | `why_now` 可用 evidence 必须在 SLA 内 |
| status 降级 | evidence 不足时自动降为 `weak` 或 `unavailable` |
| PII | 不保存不必要个人信息;author 只存公开 id 或 community context |
| source policy | source_type 必须在 allowlist 中 |

输出文件示例:

```json
{
  "generated_at": "2026-07-26T00:00:00Z",
  "global_timeout_ms": 8000,
  "platforms_attempted": ["reddit", "youtube"],
  "briefs": [],
  "execution_reports": [],
  "warnings": []
}
```

### 9.11 环境变量与凭证

```text
YOUTUBE_API_KEY=...
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USER_AGENT=atoms-social-marketing/0.1
X_BEARER_TOKEN=...
PINTEREST_ACCESS_TOKEN=...
META_ACCESS_TOKEN=...
LINKEDIN_ACCESS_TOKEN=...
```

凭证规则:

- 没有凭证就跳过对应实时 adapter,不要报错中断。
- 不在 output 中写入 token、request headers 或敏感响应。
- 每个 adapter preflight 必须返回 `credential_status`。
- 用户未授权的平台不得读取账号 insight。

### 9.12 测试策略

单元测试:

- query planner 不生成 product-name-only query。
- adapter normalize 输出统一 `EvidenceItem`。
- cache key 稳定且不含敏感信息。
- validation 能拦截禁用字段。
- timeout/error 能降级成 `unavailable` brief。

集成测试:

- `--no-network` 下只读 fixture/cache,仍可输出 valid briefs。
- Reddit/YouTube credential 缺失时不中断。
- mocked API 返回部分失败时输出 `partial/weak`。
- LLM summarizer 失败时走 rule-based summarizer。

验收 fixture:

```text
tests/fixtures/platform_intel/
  app_icp_saas_founder.json
  demand_probe_pack_saas_founder.json
  reddit_search_response.json
  youtube_search_response.json
  opportunity_briefs_expected.json
```

### 9.13 MVP 实施顺序

1. 先实现 `models.py`、`validate_probe_output.py`、`cache_store.py`。
2. 实现 `query_planner.py` 和 `select_platform_shortlist.py`。
3. 实现 `cached_platform_probe.py`,保证无网络时主链路可跑。
4. 实现 `youtube_probe.py` 和 `reddit_probe.py`。
5. 实现 `web_search_probe.py` 作为兜底。
6. 接入 `summarize_opportunity_brief.py` 和规则兜底。
7. 最后再考虑 X、Pinterest、Instagram、LinkedIn、TikTok、Rednote 的授权/cache adapter。

## 10. 验收标准

| 项 | 标准 |
|---|---|
| 主链路稳定性 | 无实时数据时 100% 可生成 Stage 2 排序 |
| 数据边界 | 禁止 `fit_verticals`、`fit_goal_types`、`relevance_to_atoms` 进入趋势/证据对象 |
| 平台覆盖 | 每个平台必须有 registry、stable profile、data access profile |
| 数据可得性 | 默认实时只启用 YouTube、Reddit、Web fallback;其他平台必须说明 cache/authorized/manual |
| Probe 复杂度 | 最多 3 平台、8 probes、60 fetched items、8-12 秒硬超时 |
| 真实性 | 没有 `usable` evidence 不得写当前趋势或近期热度 |
| 可解释性 | `fit_score` 必须拆子分,并输出 audience intersection 和 evidence refs |
| 可降级 | timeout/rate limit/API error 不阻塞 Launch Pack,只影响 confidence |
| Stage 1 输出 | 必须同时输出 `intent_profile`、`app_icp_vector`、`demand_probe_pack` |

## 11. 关键取舍

不要把社媒趋势系统做成“全平台实时洞察大脑”。对 atoms social marketing skill 来说,更合理的主链路是:

```text
App End-User ICP Vector + Stable Platform Context + Platform-native Content Generation
```

轻量趋势/需求证据只承担三个角色:

1. 找到少量当前真实终端用户需求语言,校准 angle 和 wording。
2. 识别平台入口、社区规范和反营销风险。
3. 在证据足够时,小幅提高或降低平台 fit_score 与 confidence。

这样能同时保住:

- **可行性**:不依赖多数平台不可获得的全量趋势数据。
- **稳定性**:实时失败不阻塞内容包生成。
- **质量**:有证据时更贴近用户真实表达,无证据时不伪造趋势。
- **可维护性**:新增平台先补 registry/profile/data access,稳定后再接 adapter。

## 12. 与现有文档的关系

- `references/pipeline/stage-1-intent.md` 应升级为同时输出 `intent_profile`、`app_icp_vector`、`demand_probe_pack`。
- `references/pipeline/stage-2-fit.md` 已采用 `stable_fit_score + realtime_adjustment` 规则,本文件是其平台情报与数据获取设计说明。
- `references/just-in-time-demand-probe-architecture.md` 可作为 Stage 2b 的执行细节参考,但平台覆盖、数据分层和 App End-User ICP 设计应以本文为准。

## 13. 后续实现优先级

1. 新增 `platform_registry_schema.json` 和每平台 registry 条目。
2. 补齐每个平台的 `stable_platform_profile` 与 `data_access_profile`。
3. 更新 Stage 1,让它输出 `app_icp_vector` 和 `demand_probe_pack`。
4. 实现 Reddit、YouTube、Web fallback 三个轻量 adapter。
5. 在 Stage 2 接入 `opportunity_evidence_brief`,并严格执行 confidence 和措辞闸门。
6. 建立 20 个测试 app,覆盖 SaaS、ecommerce、creator tool、local/service business。



