# Stage 2 - Platform Shortlist, Demand Evidence & Fit Score

## Purpose

对 `inputs.platform_scope` 或默认平台池计算平台适配排序。Stage 2 使用三段式流程:

1. `Stage 2a Platform Shortlist`: 用稳定平台层和 `app_icp_vector` 中的 built app end-user identity / JTBD / pains 先选最多 3 个可选 probe 平台,并把 builder production constraints 作为独立扣分/可行性维度。
2. `Stage 2b Optional Demand Probe`: 只对 shortlist 做轻量需求证据探针,失败不阻塞。
3. `Stage 2c Fit Score`: 计算 `stable_fit_score + realtime_adjustment` 并输出解释、置信和措辞边界。

Stage 2 衡量的不是“平台一般适合某垂类”,也不是“某趋势天然适配 Atoms”,而是当前 built app 的终端用户 ICP、转化目标、builder 素材能力和转化路径与平台稳定机制和少量可用证据之间的交集。

## 输入

- `intent_profile`(Stage 1 输出)
- `app_icp_vector`(Stage 1 输出)
- `demand_probe_pack`(Stage 1 输出,最多 8 个 probes)
- `inputs.platform_scope` 或默认 publishable platform pool
- `data/platform_registry.json`
- `data/platform_registry_schema.json`
- 可选 `opportunity_evidence_briefs`(Stage 2b 或 cache 输出,须符合 `data/opportunity_evidence_brief_schema.json`)
- 可选 GA4、授权账号 insight 或人工导入近期样本

## 输出

```json
{
  "ranking": ["reddit", "youtube", "instagram"],
  "probe_shortlist": ["reddit", "youtube", "web_search"],
  "scores": {
    "reddit": {
      "fit_score": 82,
      "stable_fit_score": 76,
      "realtime_adjustment": 6,
      "score_confidence": "medium-high",
      "probe_status": "usable",
      "subscores": {
        "icp_reach_quality": 25,
        "mindset_intent_fit": 18,
        "value_expression_fit": 12,
        "distribution_feasibility": 11,
        "conversion_path_fit": 6,
        "production_feasibility": 4
      },
      "audience_intersection": {
        "matched_dimensions": ["end_user_role:Shopify seller", "pain:product page traffic no sales"],
        "missing_dimensions": ["purchase urgency evidence"],
        "reachable_icp_scale": "medium",
        "quality": "high_intent_small_scale"
      },
      "recommended_surfaces": ["subreddit_discussion", "comment_reply"],
      "why_this_platform": ["Evergreen platform mechanism and end-user ICP overlap explanation."],
      "why_now": ["Only present when probe_status == usable and evidence refs >= 2."],
      "risks": ["Community anti-promotion norm."],
      "_evidence_refs": ["registry:reddit", "probe:reddit:p01:r03"]
    }
  },
  "opportunity_evidence_briefs": [],
  "_rationale": "string"
}
```

Required score fields per platform:

- `stable_fit_score`
- `realtime_adjustment`
- `fit_score`
- `score_confidence`
- `probe_status`
- `subscores`
- `audience_intersection`
- `recommended_surfaces`
- `why_this_platform`
- `why_now`(only usable evidence)
- `risks`
- `_evidence_refs`

## Stage 2a - Platform Shortlist

### 1. Load platform context layers

Read `data/platform_registry.json`. Each publishable platform must have:

- `platform_coverage_registry`(L0): supported markets, languages, content surfaces, renderer support, realtime mode, data policy, confidence cap.
- `stable_platform_profile`(L1): audience pools, mindset modes, surface map, distribution, content formats, conversion paths, production requirements, policy/norms, measurement.
- `data_access_profile`(L2): runtime access mode, available/unavailable signals, source priority, freshness SLA, fallback, compliance notes.

`web_search` is evidence fallback, not a publishing platform. It can enter `probe_shortlist` but not final launch content ranking unless explicitly used as an evidence source key.

### 2. Determine platform pool

If `inputs.platform_scope` exists, keep those platforms plus optional `web_search` fallback for probe. If absent, default by market and renderer coverage:

- English/global SMB: `youtube`, `reddit`, `instagram`, `tiktok`.
- Visual/ecommerce: add `pinterest`; keep `instagram`/`tiktok` high in shortlist.
- B2B/professional: add `linkedin`; use `reddit`/`youtube` for problem validation.
- CN market: use `rednote`, `douyin`; keep `youtube` only if target language/market supports it.

Do not remove a user-specified platform from final scoring solely because realtime probe is unsupported. Instead score from stable layers and cap confidence.

### 3. Shortlist scoring for optional probe

Select max 3 probe targets using stable signals:

```text
shortlist_score =
  built app end-user ICP-platform audience overlap
+ end-user mindset and JTBD match
+ built app value expression feasibility
+ conversion path feasibility
+ market/language support
+ data access reliability
- builder production difficulty
- policy/norm risk
```

Default realtime-capable probe order is `reddit`, `youtube`, then `web_search`. Cache/authorized/manual platforms may be probed only when fresh cache or authorized data is already available.

## Stage 2b - Optional Demand Probe

Run only after Stage 2a and only within budget:

| Budget | Limit |
|---|---:|
| Platforms probed | max 3 |
| Demand probes | max 8 |
| Queries per platform | max 3 |
| Results per query | 5-8 |
| Total fetched items | max 60 |
| Hard timeout | default 8000 ms, max 12000 ms |

Probe rules:

- Queries come from `demand_probe_pack`, not platform hot lists and not product-name-only terms.
- If `query_variants` exists, adapters should plan from it first and keep `query` only as the backward-compatible primary query.
- Query selection must mix `long_tail_precision` and `keyword_recall` when possible; do not spend all 3 platform queries on near-duplicate long tails.
- Platform-native variants should be preferred when present: Reddit favors pain/workaround/trigger language, YouTube favors how-to/outcome/comparison language, and web_search may use `site:` constraints as evidence locators.
- `expected_evidence_type` is a filter hint. High-activity results that do not match the expected end-user pain/JTBD/workaround evidence should be rejected or treated as weak wording evidence only.
- Adapters must output raw evidence and `OpportunityEvidenceBrief`; they must not calculate scores or recommendations.
- Missing credentials, timeout, rate limits, API errors, cache miss, or summarizer failure must degrade to `skipped`, `timeout`, `unavailable`, `weak`, or rule-based brief. They must not stop Stage 2c.
- Every dynamic brief must carry `evidence_refs`, `known_biases`, and `probe_status`/`status`.

Allowed default runtime sources:

| Platform | Default mode | Role |
|---|---|---|
| Reddit | official API or public web summary/cache | Pain wording, community entry, anti-promotion risk |
| YouTube | Data API/oEmbed/cache | How-to/search intent, tutorial/comparison evidence |
| Web Search fallback | authorized search connector or cache | Public evidence locator, weak/medium evidence |

All other platforms default to authorized/cache/manual evidence. Do not scrape login-state pages or public feeds at request time.

## Stage 2c - Stable Fit Score

Compute:

```text
stable_fit_score = sum(stable subscores)                  # 0..100
realtime_adjustment = optional opportunity adjustment      # -5..+10
fit_score = clamp(round(stable_fit_score + realtime_adjustment), 0, 100)
```

Stable subscores total 100:

| Dimension | Points | Core question |
|---|---:|---|
| ICP Reach & Quality | 30 | Does the platform stably contain reachable high-quality built-app end-user ICP overlap? |
| Mindset & Intent Fit | 20 | Does platform mindset support the conversion goal? |
| Value Expression Fit | 15 | Can the app's mechanism and proof be expressed natively? |
| Distribution Feasibility | 15 | Can a small/new account reach the intersection user? |
| Conversion Path Fit | 10 | Is the CTA path natural, short, trustworthy, and measurable? |
| Production Feasibility | 10 | Can the builder produce enough good content for this platform, given assets and constraints? |

Use only user input, GA4/authorized data, platform registry/profile, playbooks, and valid evidence briefs. Keep end-user ICP scoring separate from builder production constraints: end-user identity/JTBD/pain drive `icp_reach_quality` and `mindset_intent_fit`; builder assets/constraints drive `production_feasibility` only. LLM must give subscores before final score and cite evidence refs.

### Stable score anchors

- 0-30%: clear mismatch or missing critical evidence.
- 31-60%: weak/indirect relevance, unclear surface/path/assets.
- 61-80%: fit is valid with clear surface and path, but has scale/friction/evidence gaps.
- 81-100%: highly matched, well evidenced, and executable in week 1.

## Realtime Adjustment

`realtime_adjustment` must stay in `[-5, +10]`:

| Evidence | Adjustment | Rule |
|---|---:|---|
| `usable`, 2+ high-relevance refs, active engagement | +6..+10 | Direct end-user ICP/pain/JTBD overlap; not a single viral item |
| `usable` or `weak`, related but activity limited | +2..+5 | Useful wording/surface clues, small sample |
| `weak`, ICP/pain weakly related | 0 | Wording only, no score lift |
| `usable`/`weak`, strong anti-promotion or bad entry | -3..-5 | Recent/community evidence signals launch risk |
| `unavailable`/`timeout`/`error`/`skipped`/`not_run` | 0 | No score change, confidence capped |

Additional caps:

- If `stable_fit_score < 45`, final `fit_score` cannot exceed 55 unless user explicitly specifies the platform and authorized data is strong.
- Web Search fallback alone usually cannot trigger adjustment above +5.
- Single evidence item cannot trigger +6 or higher.
- Expired evidence cannot enter `why_now`.

## Score Confidence

| Confidence | Conditions |
|---|---|
| `high` | End-user ICP clear, registry/profile complete, and usable recent/authorized evidence agrees with stable layer |
| `medium-high` | stable layer complete and usable evidence exists but sample is limited |
| `medium` | stable layer complete but no usable dynamic evidence, or probe failed without changing base judgment |
| `low` | End-user ICP vague, registry/profile missing, major stable/dynamic conflict, or platform capability unknown |

Caps:

- No usable dynamic or authorized evidence: max `medium` unless this is a user-validated own channel.
- Probe `timeout`/`error`: max `medium` for that platform.
- Platform `default_confidence_cap` from registry always applies.

## Wording Gates

- `why_now` may mention current/recent opportunity only when `probe_status == usable`, `evidence_refs.length >= 2`, and evidence is within freshness SLA.
- Without usable evidence, Stage 3-5 must use evergreen platform strategy wording only.
- `opportunity_evidence_brief` and trend/cache objects must not contain `fit_verticals`, `fit_goal_types`, `relevance_to_atoms`, `fit_score`, or `realtime_adjustment`.
- Do not infer demographics, income, buying power, signup intent, or platform-wide trend scale from snippets, comments, hashtags, or single examples.

## Ranking Rules

Rank by `fit_score` descending. Ties break by:

1. Higher `stable_fit_score`.
2. Higher `conversion_path_fit`.
3. Higher `score_confidence`.
4. Higher `production_feasibility`.
5. Lower risk.

If all `fit_score < 40`, still output ranking and mark `all platforms weak fit` in `_rationale`; Stage 5 should add blocker or warning depending on user goal.

## Boundary Cases

| Case | Handling |
|---|---|
| `platform_scope` has one platform | Score only that platform; no forced comparison |
| Registry missing | User-specified platform kept with low confidence; non-specified missing platform excluded |
| `demand_probe_pack` missing | Probe not run; adjustment 0; no current-trend wording |
| Realtime probe fails | Stable score remains; adjustment 0; confidence capped |
| User specifies unsupported realtime platform | Stable strategy only, plus cache/authorized/manual note |
| Platform policy conflicts with goal | Lower conversion/distribution subscores and add risk/blocker |
| GA4 absent | No penalty; GA4 only calibrates when present |

## Output Handoff

Stage 3 reads `ranking`, `scores.{platform}.fit_score`, `score_confidence`, `probe_status`, `recommended_surfaces`, `audience_intersection`, `why_this_platform`, `why_now`, and `risks`.

Stage 5 reads `subscores`, `score_confidence`, `probe_status`, `_evidence_refs`, and `opportunity_evidence_briefs` to enforce warning/blocker gates.



