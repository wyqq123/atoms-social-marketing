# Stage 1 - Intent, App End-User ICP Vector & Demand Probes

## Purpose

把 `app_context` / `builder_prompt` / `positioning` / 可选 `ga4_snapshot` 归一化为 3 个下游对象:

- `intent_profile`: 给 Stage 3-5 使用的营销定位摘要。
- `app_icp_vector`: 给 Stage 2 做平台交集和稳定评分的结构化 **应用终端用户 ICP** 表示。
- `demand_probe_pack`: 给 Stage 2b 做轻量需求证据探针的终端用户需求语言 query,最多 8 个。

Stage 1 不选择平台、不计算 fit score、不写趋势判断。

## Entity Boundary

必须始终区分 4 个对象:

| 对象 | 含义 | 可进入哪些字段 |
|---|---|---|
| Atoms platform | 承载 builder 构建应用的平台 | 只出现在系统/上层责任描述中 |
| Builder / Atoms user | 在 Atoms 上创建应用并想推广应用的人 | `builder_prompt`、素材/生产约束、授权数据、渠道偏好 |
| Built app | Builder 在 Atoms 上构建出来、需要被推广的应用/产品 | `app_context`、`app_capability_summary`、`value_proposition`、proof assets |
| App end users | 该应用真正服务和转化的终端用户 | `app_icp_vector.end_user_identity`、pains、JTBD、alternatives、demand probes |

`app_icp_vector` 的 ICP 永远指 **built app 的终端用户**,不是 Atoms builder 本人。只有当 builder 明确说明“我的应用就是卖给 indie builders / no-code founders / Atoms-like builders”时,这些身份才可进入 `end_user_identity`,并必须在 confidence 或 rationale 中标注依据。

## 输入

`data/inputs_schema.json` 定义的完整 inputs 对象。

## 输出

```json
{
  "intent_profile": {},
  "app_icp_vector": {},
  "demand_probe_pack": {}
}
```

### `intent_profile`

`intent_profile.audience` 描述 built app 的终端用户摘要,不是 builder 自画像。

```json
{
  "app_summary": {
    "name": "string",
    "one_liner": "string, <= 100 chars",
    "category_normalized": "saas | ecommerce | creator-tool | content-app | tool-utility | local-service | other",
    "market_primary": ["US"],
    "market_secondary": ["UK"]
  },
  "promo_intent": {
    "goal_type": "cold-start | user-acquisition | brand-awareness | conversion | lead-capture | purchase | demo-booking",
    "goal_metric_hint": "string",
    "time_horizon": "week-1 | month-1"
  },
  "audience": {
    "primary_persona": "string, built app 的终端用户, e.g. 'Shopify sellers who need faster product-page copy'",
    "pain_points": ["string, end-user pains; mark synthetic vs observed in app_icp_vector"],
    "tone_preference": "casual | professional | build-in-public | polished | playful"
  },
  "value_prop": {
    "key_selling_point": "string",
    "supporting_points": ["string"],
    "differentiators": ["string"]
  },
  "ga4_signals": null,
  "_rationale": "string"
}
```

### `app_icp_vector`

`app_icp_vector` 是 Stage 2 的可计算输入,不是 persona 文案。它必须把显式输入、合理推断和外部证据分开。每个会影响平台评分、query 召回或内容角度的字段都必须带 `confidence` 或 item-level `source`。

字段生成原则:

- Stage 1 可以基于 `app_context`、`positioning`、`builder_prompt` 和可选 `ga4_snapshot` 生成 hypothesis,但不得把 hypothesis 写成 observed fact。
- Built app 代码、UI 或描述只能先归纳为 `app_capability_summary`;不能从产品功能直接跳到终端用户身份、购买意图或真实痛点。
- `pains`、`jtbd`、`alternatives` 可由 LLM 推断,但必须标注来源和置信;没有外部证据时不得写成真实用户原话或真实竞品结论。
- Builder 自身身份、制作能力、授权账号和素材只进入 `builder_context` / `production_constraints`,不能进入 `end_user_identity` 或 demand probes,除非 built app 明确服务同类 builders。

```json
{
  "icp_id": "runtime",
  "icp_subject": "built_app_end_users",
  "source_confidence": "low | medium | medium-high | high",
  "geo_language": {
    "markets": ["US"],
    "languages": ["en"],
    "market_priority_reason": "positioning target market plus GA4 top geo when available",
    "confidence": "high"
  },
  "end_user_identity": {
    "roles": [
      { "value": "Shopify seller", "source": "positioning.target_audience", "confidence": "high" }
    ],
    "organization_context": [
      { "value": "small ecommerce operator", "source": "inferred_from_target_audience", "confidence": "medium" }
    ],
    "industry_context": [
      { "value": "ecommerce", "source": "app_context.category", "confidence": "medium-high" }
    ],
    "community_identities": [
      { "value": "independent retailer", "source": "inferred_from_target_audience", "confidence": "medium" }
    ],
    "explicitly_not_builder_identity": true,
    "confidence": "medium-high"
  },
  "app_capability_summary": {
    "core_capabilities": ["rewrite product-page copy from product inputs"],
    "user_visible_workflow": ["paste product details", "review conversion-focused suggestions"],
    "limitations_or_unknowns": ["pricing unknown", "customer proof unknown"],
    "source": ["app_context.description", "builder_prompt"],
    "confidence": "medium"
  },
  "jtbd": {
    "primary_jobs": [
      { "value": "improve product-page conversion", "source": "positioning.key_selling_point + target_audience", "confidence": "medium-high" }
    ],
    "trigger_moments": [
      { "value": "new product launch", "source": "inferred_from_ecommerce_context", "confidence": "medium" }
    ],
    "success_criteria": [
      { "value": "clearer product benefits", "source": "inferred_from_key_selling_point", "confidence": "medium" }
    ],
    "confidence": "medium-high"
  },
  "pains": {
    "pain_points": [
      { "value": "product pages get traffic but do not convert", "source": "synthetic_from_jtbd_and_key_selling_point", "confidence": "medium" }
    ],
    "urgency": "low | medium | high",
    "synthetic_pain_language_examples": ["product page traffic but no sales"],
    "observed_pain_language_examples": [],
    "confidence": "medium"
  },
  "alternatives": {
    "workaround_categories": [
      { "value": "manual copywriting", "source": "inferred_from_app_capability", "confidence": "medium" },
      { "value": "generic AI writing tool", "source": "inferred_from_app_category", "confidence": "medium" }
    ],
    "named_competitor_candidates": [
      { "value": "string, only when user input/cache/web evidence names it", "source": "user_input | cache | web_evidence", "confidence": "low | medium | high" }
    ],
    "switching_triggers": [
      { "value": "generic copy is not specific to the product page", "source": "inferred_from_key_selling_point", "confidence": "medium" }
    ],
    "confidence": "medium"
  },
  "value_proposition": {
    "key_selling_point_raw": "string, positioning.key_selling_point 原文",
    "user_benefit": "string, built app 给终端用户带来的结果",
    "unique_mechanism": "string, built app 的独特价值机制;不可只是 slogan",
    "key_claims": ["speed", "simplicity"],
    "proof_assets": ["built app product screenshots", "built app demo flow"],
    "proof_gaps": ["customer proof unknown"],
    "claim_risk": "low | medium | high"
  },
  "conversion_goal": {
    "goal_type": "awareness | signup | demo_booking | purchase | lead_capture | app_install | waitlist",
    "desired_action": "string",
    "friction_level": "low | medium | high",
    "tracking_options": ["UTM", "GA4"],
    "confidence": "medium"
  },
  "builder_context": {
    "builder_role": "string | null, only if explicitly provided",
    "available_assets": ["built app screenshots", "built app landing page"],
    "channel_preferences": ["string"],
    "constraints": ["builder cannot record founder-led video", "built app has limited testimonials"],
    "must_not_be_used_as_end_user_identity": true
  },
  "production_constraints": {
    "available_assets": ["built app screenshots", "built app landing page"],
    "can_create": ["text", "image", "short_video"],
    "constraints": ["builder cannot record founder-led video", "built app has limited testimonials"],
    "confidence": "medium"
  }
}
```

#### Field Evidence Rules

| 字段 | 允许来源 | 生成/置信规则 |
|---|---|---|
| `end_user_identity.roles` | `positioning.target_audience`, app description 中明确服务对象 | 不得从 builder 自称推断;未明确时 `confidence<=medium` |
| `organization_context` | target audience、app category、明确业务场景 | 不用虚构精确公司规模;只有用户或证据明确时才写人数范围 |
| `app_capability_summary` | app context、builder prompt、可读取的 built app UI/代码摘要 | 只描述产品能力和可见 workflow,不描述用户动机 |
| `jtbd.primary_jobs` | target audience + key selling point + app capability summary | 属于 hypothesis;除非用户明确描述 job,通常 `confidence<=medium-high` |
| `pains.pain_points` | target audience、key selling point 的反面、JTBD friction、外部 evidence | 无 evidence 时写 synthetic pain;不得伪装成真实用户原话 |
| `alternatives.workaround_categories` | app category、JTBD、用户输入 | 可推断类别,但要保守 |
| `alternatives.named_competitor_candidates` | 用户输入、授权/cache/web evidence | Stage 1 默认不编造竞品名;没有证据时为空数组 |
| `value_proposition` | key selling point、app capability summary、proof assets | 保留原始卖点,但另拆 user benefit 与 mechanism |
| `conversion_goal` | promo_goal、目标转化路径、GA4/UTM 可用性 | 可归一化;signup/purchase/demo 等高摩擦动作要标注 friction |
| `production_constraints` | `production_context`、builder prompt、assets refs、授权账号/素材清单 | 描述 builder 能生产什么内容;不得影响 end-user identity |

### `demand_probe_pack`

`demand_probe_pack` 是运行时 query 计划,不是趋势库。它必须来自 built app 终端用户的 end_user_identity / pain / JTBD / alternatives / trigger moments / desired outcomes。它不能来自 Atoms 平台、builder 自画像或 built app 品牌口号。

```json
{
  "app_id": "runtime",
  "probe_subject": "built_app_end_users",
  "generated_at": "2026-07-27T00:00:00Z",
  "icp_summary": "Shopify sellers improving product-page conversion",
  "probes": [
    {
      "probe_id": "p01",
      "intent": "pain_expression | problem_search | alternative_comparison | jtbd_how_to | trigger_moment | desired_outcome",
      "query": "Shopify seller product page traffic no sales",
      "query_variants": [
        {
          "type": "long_tail_precision",
          "query": "Shopify seller product page traffic no sales",
          "purpose": "high relevance pain evidence"
        },
        {
          "type": "keyword_recall",
          "terms": ["product page conversion", "traffic no sales", "Shopify"],
          "purpose": "broader recall when long-tail results are sparse"
        },
        {
          "type": "platform_native",
          "reddit": "product page traffic no sales Shopify",
          "youtube": "product page conversion Shopify tutorial",
          "web_search": "site:reddit.com/r ecommerce product page traffic no sales"
        }
      ],
      "language": "en",
      "market": "US",
      "source_terms": {
        "end_user_identity": ["Shopify seller"],
        "pain": ["product page traffic no sales"],
        "jtbd": ["improve product page conversion"],
        "alternative": ["manual copywriting", "generic AI writing tool"],
        "trigger_moment": ["new product launch"],
        "desired_outcome": ["increase sales"]
      },
      "priority": 0.92,
      "expected_evidence_type": "pain discussion | how-to search | workaround comparison | trigger-moment question",
      "platform_surfaces_hint": ["reddit_search", "youtube_search"],
      "must_not_include": ["product name", "brand slogan", "Atoms", "builder identity unless end users are builders"]
    }
  ],
  "constraints": {
    "max_probes": 8,
    "prefer_user_language": true,
    "avoid_product_keywords_only": true,
    "avoid_builder_identity_unless_target_user": true
  }
}
```

## LLM 动作

### 1. 从 `builder_prompt` 抽取线索,并标注归属

抽取时必须先判断线索属于哪一类:

- Builder context: builder 自己的身份、能力、素材、渠道偏好、预算和制作约束。
- Built app: 应用类别、功能、价值机制、证明资产。
- App end users: 应用目标用户的身份、痛点、任务、替代方案、触发时机和目标结果。

只有 app end-user 线索可以进入 `end_user_identity`、pains、JTBD、alternatives 和 demand probes。Builder context 只能进入 `builder_context` 或 `production_constraints`。

### 2. 与 `positioning` 三要素对齐

- `positioning.key_selling_point` 原文进入 `intent_profile.value_prop.key_selling_point` 和 `app_icp_vector.value_proposition.key_selling_point_raw`;再基于 built app 能力拆出 `user_benefit` 和 `unique_mechanism`。
- `positioning.target_audience` 原文优先进入 `intent_profile.audience.primary_persona`,再拆到 `app_icp_vector.end_user_identity`。
- `positioning.promo_goal` 归一到 `promo_intent.goal_type` 和 `app_icp_vector.conversion_goal`。
- 冲突时以 `positioning` 为准,在 `_rationale` 标注冲突项。

### 3. GA4 校准

若 `ga4_snapshot` 可用:

- `top_geo` 校准 `geo_language.markets`,但不得覆盖明确定位市场。
- `by_channel`、engagement、conversion 只作为 built app 已发生路径线索,不得代表平台整体潜在人群。
- GA4 缺失不扣分,只降低部分 confidence。

### 4. 生成 `app_icp_vector`

按显式输入优先级填字段:

1. positioning 明确字段。
2. app_context 描述、分类和素材。
3. app_context 或可读取 built app UI/代码归纳出的 `app_capability_summary`。
4. builder_prompt 中可归属为 app end-user 的线索。
5. `production_context` 中明确提供的 builder 素材、渠道偏好和制作约束。
6. builder_prompt 中可归属为 builder context 的素材/约束线索。
7. GA4 或授权数据的校准。

不得把 Atoms platform、builder 自身身份、平台画像、平台趋势或平台热榜写进 `end_user_identity`。

### 5. 生成 `demand_probe_pack`

生成 4-8 个高优先级 probe。每个 probe 保留 `query` 作为兼容用 primary query,同时尽量输出 `query_variants` 支持长尾 + 关键词组混合检索。模板池:

```text
{end_user_identity} {pain}
{end_user_identity} how to {jtbd}
{pain} {alternative}
best way to {desired_outcome} for {end_user_identity}
{trigger_moment} {pain}
{alternative} vs {desired_outcome}
```

Query mix 规则:

- 4-8 个 probes 中至少 50% 来自 pain 或 JTBD,避免只搜产品功能。
- 至少 2 个 `long_tail_precision` query,用于高相关证据。
- 至少 2 个 `keyword_recall` query variant,用于召回更广的相关内容。
- 至少 1 个 workaround/alternative query;没有 named competitor evidence 时只用 workaround category。
- 每个平台实际最多跑 3 个 query 时,应优先覆盖不同 intent,而不是只按 priority 取前三个同质 query。
- Reddit query 更偏 pain、workaround、trigger moment;YouTube query 更偏 how-to、desired outcome、comparison;web_search query 可加入 `site:` 限定做 evidence locator。
- 宽召回 query 必须仍包含至少一个 end-user/pain/JTBD 线索,不得退化为产品品类词或 built app 功能词。

约束:

- 不生成 product-name-only query。
- 不把 app 功能词等同于终端用户需求语言。
- 不使用 builder 自我描述,除非目标用户明确就是同类 builders。
- `must_not_include` 至少包含产品名、品牌 slogan、Atoms 平台名和纯营销口号。
- 每个 probe 必须可追溯到 `source_terms`。
- 每个 probe 必须声明 `expected_evidence_type`;Stage 2 可用它过滤高热但低相关结果。
- 优先使用目标市场语言;不确定时 `en` + `US`。

## 边界情况

| 场景 | 处理 |
|---|---|
| builder_prompt 极短 | probe 减到 4-5 个,主要来自 positioning,`source_confidence=medium` 或更低 |
| target_market 为空 | 默认 `["US"]`,language 默认 `["en"]`,并写 `_rationale` |
| 目标用户非常宽泛 | `app_icp_vector.end_user_identity.confidence=low`,probe 优先痛点/JTBD,Stage 2 confidence 受限 |
| builder 自称 solo founder,但目标用户未说明 | 不把 solo founder 写入 `end_user_identity`;只写入 `builder_context.builder_role` |
| 应用目标用户就是 builders/founders | 可写入 `end_user_identity`,但必须引用 `positioning.target_audience` 或明确 app description |
| 只看到产品功能,看不到终端用户痛点 | 用 JTBD/desired outcome 改写为终端用户需求语言;不得直搜产品功能词 |
| 只看到卖点,看不到真实竞品 | `alternatives.named_competitor_candidates=[]`,只生成 workaround category query |
| 无素材/制作能力信息 | `production_constraints.confidence=low`,Stage 2 production feasibility 不得高估 |
| pain language 没有外部 evidence | 只能写入 `synthetic_pain_language_examples`,不得写入 `observed_pain_language_examples` |
| 多语言或 CN 市场 | 同语言生成 probe;CN 市场优先 `zh`,并允许 rednote/douyin 进入 stable shortlist |

## 输出交给下游

Stage 2 读取 `intent_profile`、`app_icp_vector`、`demand_probe_pack`。
Stage 3-5 读取 `intent_profile`;Stage 3 可读取 `app_icp_vector` 的 `value_proposition`、`conversion_goal`、`builder_context` 和 `production_constraints` 做 angle 约束。


