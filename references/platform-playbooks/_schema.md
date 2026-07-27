---
name: platform-playbook-schema
type: template
description: 社媒平台 playbook 的通用结构模板。v3 中 playbook 主要服务 Stage 3/4 内容生成;Stage 2 平台覆盖、稳定 profile 和 data access 以 data/platform_registry.json 为准。
version: 2.0
last_updated: 2026-07-26
---

# Platform Playbook Schema

## v3 使用说明

- Stage 2 平台评分优先读取 `data/platform_registry.json` 的 L0/L1/L2 层。
- Playbook 主要服务 Stage 3/4:语言风格、内容格式、发布节奏、可复用结构、避坑。
- Playbook 不得写 app-specific 趋势适配字段,也不得把 Atoms builder 自身身份写成 built app 的终端用户画像,包括 `fit_verticals`、`fit_goal_types`、`relevance_to_atoms`。
- 旧 §8 的业务类型适配只能作为 evergreen 内容策略参考,不得作为 Stage 2 `fit_score` 输入。
- 每个平台 playbook 的平台 id 应使用 registry 全称:`instagram`, `youtube`, `tiktok`, `reddit`, `x`, `linkedin`, `pinterest`, `rednote`, `douyin`。

## 与 Registry 的字段映射

| v3 Registry 层 | 主文件 | Playbook 是否可补充 | 用途 |
|---|---|---|---|
| L0 `platform_coverage_registry` | `data/platform_registry.json` | 否 | 平台覆盖、renderer、数据策略 |
| L1 `stable_platform_profile` | `data/platform_registry.json` | 可补充说明 | Stage 2 稳定评分;Stage 3 surface 选择 |
| L2 `data_access_profile` | `data/platform_registry.json` | 否 | Stage 2b 是否可 probe/缓存/授权 |
| 内容格式/语言/节奏 | playbook | 是 | Stage 3/4 生成内容 |
| 案例/结构归纳 | playbook | 是 | Angle、hook、storyboard 结构 |

## 必填 Section

每个平台 playbook 严格按下列 section 编写,标题和顺序尽量保持稳定。

### Section 1 - 平台定位与核心用户

- `platform_name`
- `platform_id`(必须匹配 registry)
- `elevator_pitch`
- `primary_use_cases`
- `builder_relevance`: 只描述 Atoms builder（应用创建者）为什么应考虑该平台,不得当作 built app 终端用户画像
- `registry_ref`: 指向 `data/platform_registry.json.platforms.{platform_id}`

### Section 2 - 稳定受众与心智补充

补充 registry L1,但不得用作 app-specific 推荐结论。

- `audience_pools_notes`
- `mindset_modes_notes`
- `intent_layers`
- `known_limits`: 不可推断 demographics/购买力的边界

### Section 3 - 分发机制

- `distribution_model`
- `ranking_signals`
- `content_type_priorities`
- `engagement_window`
- `algo_penalties`
- `recent_changes`

### Section 4 - 内容格式规格

- `post_types`
- `dimensions_and_ratios`
- `caption_length_recommendation`
- `hashtag_or_keyword_rules`
- `link_and_cta_rules`

### Section 5 - 调性关键词与语言风格

- `tone_descriptors`
- `voice_do`
- `voice_dont`
- `emoji_and_emphasis`
- `hook_patterns`

### Section 6 - Hashtag/Keyword 策略

不同平台可解释为 hashtag、keyword、topic 或 title/description term。

- `optimal_count`
- `mix_strategy`
- `research_method`
- `banned_or_risky`
- `evidence_gate`: 无 usable evidence 时只使用 evergreen terms

### Section 7 - 发布节奏与频率

- `best_posting_times`
- `default_timezone`
- `frequency_recommendation`
- `first_week_ramp_up`
- `production_load_notes`

### Section 8 - 业务类型 × 内容打法参考

仅作内容策略参考,不得直接输出 Stage 2 `fit_score`。

每业务类型可包含。注意这里的业务类型指 built app 的业务/品类,不是 builder 自身身份:

- `content_angles`
- `visual_style`
- `caption_focus`
- `cta_style`
- `common_traps`
- `stable_fit_notes`(文字说明,非数值评分)

### Section 9 - 高转化模式

- `sample_size_and_source`
- `winning_structures`
- `visual_patterns`
- `engagement_triggers`
- `known_biases`

### Section 10 - 避坑清单 + 数据源

- `avoid_list`
- `references`
- `next_review_date`
- `data_access_boundary`: 与 registry L2 一致,禁止 request-time 非授权抓取

## Frontmatter Convention

```yaml
---
name: <platform>-playbook
platform: <instagram | youtube | tiktok | reddit | x | linkedin | pinterest | rednote | douyin>
version: <major.minor>
last_updated: <YYYY-MM-DD>
data_freshness_note: <关键数据时效性说明>
review_by: <下次复核日期>
sources_summary: <数据源摘要>
---
```

## 质量约束

- 每个动态或近期样本必须标来源和时间。
- 不引用长段原文 caption/description,只做结构归纳。
- 不把单条爆款或热榜样本泛化为平台趋势。
- 不把授权账号 insight 泛化为平台整体趋势。
- 新平台先补 registry,再补 playbook,最后才接 adapter。


