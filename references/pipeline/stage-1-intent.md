# Stage 1 — Intent & Positioning

## Purpose

把 4 类原始输入(app_context / builder_prompt / positioning / ga4_snapshot)归一化为下游可直接消费的 `intent_profile`。

## 输入

`data/inputs_schema.json` 定义的完整 inputs 对象。

## 输出

结构化 `intent_profile` 对象:

```json
{
  "app_summary": {
    "name": "string",
    "one_liner": "string, <= 100 chars",
    "category_normalized": "saas | ecommerce | creator-tool | content-app | tool-utility | ...",
    "market_primary": ["US"],
    "market_secondary": ["UK"]
  },
  "promo_intent": {
    "goal_type": "cold-start | user-acquisition | brand-awareness | conversion",
    "goal_metric_hint": "string, 从 positioning.promo_goal 抽",
    "time_horizon": "week-1 | month-1"
  },
  "audience": {
    "primary_persona": "string, e.g. 'SMB solo builder working on AI side projects'",
    "pain_points": ["string"],
    "tone_preference": "casual | professional | build-in-public"
  },
  "value_prop": {
    "key_selling_point": "string, 直接从 positioning.key_selling_point 承接",
    "supporting_points": ["string"],
    "differentiators": ["string"]
  },
  "ga4_signals": null | {
    "traffic_source_bias": "string",
    "mobile_first": true | false,
    "confirmed_geo": ["string"]
  },
  "_rationale": "string, 抽取逻辑说明"
}
```

## LLM 动作(4 步)

### 1. 从 `builder_prompt` 抽取隐含线索
读一遍 `builder_prompt`(可能几百到几千字),抽取:
- **tone 线索**:builder 的语气(严肃 / 幽默 / build-in-public),映射到 `audience.tone_preference`
- **隐含受众**:prompt 中反复提到的用户角色 / 使用场景 → 补充到 `audience.primary_persona`
- **竞品/参考物**:prompt 中提到的其他产品 → 提炼 `value_prop.differentiators`
- **非功能诉求**:如"简洁"/"快速"/"美观"→ 补充到 `value_prop.supporting_points`

### 2. 与 `positioning` 三要素对齐
- `positioning.key_selling_point` **原文**灌入 `value_prop.key_selling_point`,不改写
- `positioning.target_audience` **原文**灌入 `audience.primary_persona`,builder_prompt 抽出的补丁作为 supplement
- `positioning.promo_goal` 分类:
  - 含"launch" / "冷启动" / "首发" → `goal_type: cold-start`
  - 含具体注册/下载数字 → `goal_type: user-acquisition`,并把数字抽到 `goal_metric_hint`
  - 含"品牌" / "认知" / "曝光" → `goal_type: brand-awareness`
  - 含"转化" / "付费" / "conversion" → `goal_type: conversion`
- **冲突处理**:若 builder_prompt 与 positioning 对同一维度给出矛盾信息(如 prompt 说面向企业用户,positioning 写"solo builder"),**以 positioning 为准**,在 `_rationale` 明确标注冲突。

### 3. GA4 校准(若 ga4_snapshot 非 null)
- `ga4_snapshot.top_geo` → `ga4_signals.confirmed_geo`(取 sessions top 3)
- `ga4_snapshot.device_split.mobile > 0.55` → `ga4_signals.mobile_first: true`
- `ga4_snapshot.top_referrer` → `ga4_signals.traffic_source_bias`(如 producthunt-heavy / organic-search-heavy / paid-social)
- **不覆盖 positioning**:若 GA4 top_geo 与 `positioning.target_market` 不一致,positioning 保留在 `market_primary`,GA4 附加到 `market_secondary` 并在 `_rationale` 标注

### 4. category_normalized 归一
从 `app_context.category` + `app_context.description` 推断,归到以下枚举之一:
- `saas` — 订阅式软件工具
- `ecommerce` — 卖实物 / 数字商品
- `creator-tool` — 内容创作类(视频编辑、写作辅助等)
- `content-app` — 内容消费类(阅读、播客等)
- `tool-utility` — 单点工具(计算器、转换器等)
- 其他 → `other`,并在 `_rationale` 标注

## 边界情况

| 场景 | 处理 |
|---|---|
| builder_prompt 极短(接近 50 字符下限)| 隐含线索抽取降级,tone_preference 默认 `casual`;`_rationale` 标注"prompt 信息量不足,主要依赖 positioning" |
| builder_prompt 与 positioning 冲突 | 以 positioning 为准;`_rationale` 明确列出冲突项 |
| ga4_snapshot 存在但字段大部分空 | 视为 null 处理;`_rationale` 标注"GA4 数据不足,未使用" |
| positioning.promo_goal 无法归类到 4 种 goal_type | 归 `cold-start`(默认最激进),`_rationale` 标注原因 |
| target_market 为空数组 | 默认 `["US"]`,`_rationale` 标注 |

## 输出交给下游

Stage 2 会读:`app_summary.category_normalized`、`audience.primary_persona`、`promo_intent.goal_type`、`ga4_signals`。
Stage 3 会读:全量 intent_profile。
Stage 4 会读:`audience.tone_preference`、`value_prop.*`。
