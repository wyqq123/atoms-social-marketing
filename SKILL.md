---
name: atoms-social-marketing
description: 为 Atoms builder（应用创建者）在 Atoms 上构建的应用生成首发社媒内容包,并用轻量稳定的平台 fit score 选择社媒平台。输入 built app 上下文 + 终端用户定位澄清 + 可选 GA4/授权数据,输出多产物 Launch Pack JSON(caption + storyboard + schedule + media prompt)。Stage 1/2 会生成 app_icp_vector、demand_probe_pack、平台 stable_fit_score、optional realtime_adjustment 和 evidence-gated confidence。媒体产物只挂载 injectable_prompt,不触发生成。
---

# Atoms Social Marketing

## 何时启用

- Atoms builder（应用创建者）已在 Atoms platform 完成 built app 构建。
- 需要为该应用生成社媒首发内容包或判断优先投放平台。
- 已收集 positioning 三要素:`promo_goal` / `target_audience` / `key_selling_point`,其中 `target_audience` 必须指 built app 的终端用户。

**不适用**:

- 长期(> 1 周)运营节奏规划。
- 直接生成图片/视频素材(见媒体资产两级触发契约)。
- 无授权抓取平台登录态、profile/feed 或第三方爬虫数据。
## 概念边界

本 skill 必须始终区分 4 个对象:

| 对象 | 含义 | 在 pipeline 中的位置 |
|---|---|---|
| Atoms platform | 承载应用构建与 skill 调用的平台 | 只用于系统责任说明 |
| Builder / Atoms user | 在 Atoms 上创建 built app 并发起营销生成的人 | `builder_prompt`、素材能力、授权数据、生产约束 |
| Built app | Builder 创建并需要推广的应用/产品 | `app_context`、`app_capability_summary`、`value_prop`、proof assets |
| App end users | Built app 真正服务、触达和转化的终端用户 | `target_audience`、`app_icp_vector.end_user_identity`、pains/JTBD/probes |

`app_icp_vector` 和 `demand_probe_pack` 的 ICP 永远指 built app 的终端用户,不是 builder 自己。只有当输入明确说明 built app 面向 builders/founders/no-code creators 时,这些身份才可作为终端用户身份写入 `end_user_identity`。

全局硬约束:

- Built app 功能/代码/UI 先归纳为 `app_capability_summary`,不得直接推成终端用户身份、购买力或真实痛点。
- `pains`、`jtbd`、`alternatives` 可以是 hypothesis,但必须标注 source/confidence;没有证据时不得写成 observed fact。
- 竞品名只来自用户输入、cache、授权数据或 web evidence;Stage 1 默认只推断 workaround category。
- `demand_probe_pack` 应使用长尾精准 query + 关键词组召回 + platform-native rewrite 的混合检索,并保留 `query` 作为兼容 primary query。

## Pipeline 概览

5 阶段线性 pipeline,无状态,每次调用独立完成。

```text
inputs
   ↓
Stage 1  Intent, End-User ICP Vector & Demand Probes
         → intent_profile + app_icp_vector(end users) + demand_probe_pack(end-user language)
   ↓
Stage 2  Platform Shortlist, Demand Evidence & Fit Score
         → stable_fit_score + realtime_adjustment + fit_score + confidence
   ↓
Stage 3  Content Strategy
         → strategies[per platform]
   ↓
Stage 4  Deliverable Rendering
         → deliverables[per platform]
   ↓
Stage 5  Pack & Self-check
         → Launch Pack JSON
```

主链路降级路径:

```text
no realtime evidence -> stable platform strategy -> confidence <= medium -> no current-trend wording
```

详见 `references/pipeline/stage-{1..5}-*.md`。

## 输入契约

见 `data/inputs_schema.json`。

**必填**:

- `app_context.{name, description, category}`
- `builder_prompt`(> 50 字符;描述 builder 构建 built app 的原始 prompt,不能直接当作终端用户画像)
- `positioning.{promo_goal, target_audience, key_selling_point}`

**可选**:

- `production_context`:可选 builder 素材、渠道偏好和制作约束;只进入 `builder_context` / `production_constraints`,不得进入终端用户 ICP。
- `ga4_snapshot`:上层拉取的 GA4 汇总快照;若无,pipeline 只用 positioning 与 builder_prompt。
- `platform_scope`:默认 `['instagram', 'youtube', 'tiktok', 'reddit']`;旧别名 `ig/yt/tt` 应在上层映射到全称。
- `probe_options`:控制 Stage 2b 是否跑 realtime/cache probe、超时、平台数和 query 数。

## Positioning Intake

当上层未提供完整 `positioning` 时,先走 Positioning Intake,再进入 Stage 1。支持同级两条路径:

- `hil_form`:上层 HIL 表单直接收集并由用户确认三要素。
- `conversation_clarifier`:通用模型从用户 prompt 和 built app context 抽取候选,再通过单选/多选/自定义编辑逐项澄清。

默认自动路由:只有 `promo_goal`、`target_audience`、`key_selling_point` 都来自 `user_prompt` 或 `app_context`、置信为 high 时,才展示快速确认;仍必须由用户确认。任一字段缺失、冲突、low/medium,或疑似把 builder 自述当成终端用户身份时,按 `target_audience -> promo_goal -> key_selling_point` 逐项澄清。

使用 `scripts/positioning_intake/run_positioning_intake.py` 处理确定性的 intake state。其 `route == "ready"` 且 `handoff` 非空是生成 `app_icp_vector`、`demand_probe_pack` 或运行 Stage 2b 的前置条件。用户随时可切换至 HIL 表单;使用 `form_prefill` 保留已收集值。详情见 `references/conversation-clarifier-protocol.md` 与 `data/positioning_intake_schema.json`。

严禁在用户确认前把候选值当作事实、调用实时 API 或写入 cache。`intake_meta` 仅用于审计;下游一律读取同一份 `positioning` 契约。

## Executable Runtime

当运行环境支持 tool calling 时,通用模型必须通过唯一入口 `scripts/social_marketing_runtime/tool_adapter.py::run_social_marketing` 调用本 skill,而不是自行拼接 shell 命令或直接调用平台 API。没有 Python tool adapter 的宿主可调用 `scripts/social_marketing_runtime/run_social_marketing.py --request <json> --output <json>`。

调用结果只可能是:

- `needs_input` / `needs_confirmation`:展示 `next_hil`,收集或确认 positioning 后带同一 `session_id` 再次调用。
- `completed`:读取 `result` 中 schema `0.3.0` 的完整 Launch Pack。
- `blocked`:展示 `checks.blocker`,不得让模型编造缺失信息继续生成。

`completed` 的 Launch Pack 包含 `publish_platforms`、每平台的完整标题/hook/正文/CTA/discoverability、图文 slides 或视频 storyboard 的按需多媒体 prompt,以及可引用真实 `post_id` 的 `schedule.week_1`。无 usable realtime evidence 时仍交付 evergreen 包,但禁止加入当前热门或近期趋势措辞。
## 输出契约

兼容层见 `data/launch_pack_schema.json`;可执行 runtime 的完整交付契约见 `data/launch_pack_runtime_schema.json` (schema 0.3.0)。

顶层字段:

- `launch_brief` — 精简摘要。
- `platform_fit` — ranking + stable/realtime score + evidence-gated confidence。
- `strategies` — 每平台 angles + hashtag/keyword mix + cadence。
- `deliverables` — 每平台 posts + storyboards + ab_variants。
- `schedule` — 首周节奏表。
- `checks` — blocker / warning / info。
- `_pipeline_meta` — registry/playbook 版本、probe meta、置信摘要、媒体 prompt 计数。

## 平台覆盖与数据边界

平台覆盖由 `data/platform_registry.json` 管理,契约见 `data/platform_registry_schema.json`。每个平台必须包含:

- L0 `platform_coverage_registry`:支持市场/语言、content surfaces、renderer support、realtime mode、data policy、confidence cap。
- L1 `stable_platform_profile`:长期 audience pools、mindset、surface、distribution、conversion、production、policy/norms。
- L2 `data_access_profile`:运行时可获得哪些信号、不可获得哪些信号、fallback 和合规边界。

默认 realtime 自动路径仅面向 `reddit`、`youtube`、`web_search` fallback。Instagram、TikTok、X、LinkedIn、Pinterest、Rednote、Douyin 默认使用 stable profile + cache/authorized/manual evidence,不得 request-time 抓取公共 feed 或登录态页面。

`web_search` 只用于 evidence fallback,不是发布平台。

## Stage 索引

| Stage | 文件 | 用途 |
|---|---|---|
| 1 Intent/ICP | `references/pipeline/stage-1-intent.md` | 生成 `intent_profile`、`app_icp_vector`、`demand_probe_pack` |
| 2 Fit | `references/pipeline/stage-2-fit.md` | 平台短名单、可选 probe、稳定评分和实时校准 |
| 3 Strategy | `references/pipeline/stage-3-strategy.md` | Angles + hashtag/keyword mix + cadence |
| 4 Render | `references/pipeline/stage-4-render.md` | 渲染 caption/storyboard + 挂载 prompt |
| 5 Pack | `references/pipeline/stage-5-pack.md` | 组装 + evidence/wording 自检 |
| GA4 契约 | `references/ga4-snapshot-contract.md` | 上层拉取 GA4 快照口径 |
| Probe 架构 | `references/just-in-time-demand-probe-architecture.md` | Stage 2b 执行细节 |
| v3 重构方案 | `references/platform-coverage-and-trend-intelligence-rebuild.md` | 平台覆盖、趋势情报和 fit score 设计来源 |

## 模板

| 模板 | 文件 | 消费 stage |
|---|---|---|
| Caption | `references/templates/caption.md` | Stage 4 |
| Storyboard | `references/templates/storyboard.md` | Stage 4 |
| Schedule | `references/templates/schedule.md` | Stage 5 |

## Playbook 与 Registry

- `references/platform-playbooks/{instagram,youtube,tiktok}.md`:已沉淀的内容生成 playbook。
- `references/platform-playbooks/_schema.md`:playbook 结构和 v3 registry/stable profile 对齐说明。
- `data/platform_registry.json`:Stage 2 的平台覆盖与稳定评分主数据源。

没有 playbook 但 registry 完整的平台可以进入 Stage 2 排序;Stage 3/4 应生成保守 strategy 并降低 confidence。

## Realtime Probe 脚本

`Stage 2b` 可使用 `scripts/realtime_probe/` 的轻量脚本骨架:

- `select_platform_shortlist.py`
- `query_planner.py`
- `run_realtime_probe.py`
- `summarize_opportunity_brief.py`
- `validate_probe_output.py`
- `cache_store.py`
- `adapters/{reddit_probe,youtube_probe,web_search_probe,cached_platform_probe}.py`

默认 no-network/cache path 必须可跑。缺 credential 不报错中断,只输出 `skipped` brief 并让 Stage 2c 使用 stable strategy。

## 媒体资产两级触发契约

Pipeline 只挂载 `injectable_prompt` 字符串,不生成任何图片/视频。

- Stage 4 输出的每个 `media_prompts.*` 对象含 `trigger: "on-demand"`。
- `injectable_prompt` 是可直接注入下游 image/video 工具的完整 prompt。
- 上层 Atoms builder 负责展示按钮、用户点击和工具调用;这些行为属于 builder 操作,不得进入终端用户 ICP。
- `_pipeline_meta.media_generation_deferred == true` 恒成立。

## Evidence 与措辞硬约束

- 趋势/证据对象不得包含 `fit_verticals`、`fit_goal_types`、`relevance_to_atoms`、`fit_score`、`realtime_adjustment`。
- 没有 `usable` evidence 时,不得写“当前热门”“近期大家都在讨论”等表达。
- `why_now` 只有在 `probe_status == usable` 且 evidence refs >= 2 且 freshness 在 SLA 内才可填写。
- 不推断真实 demographics、收入、购买力或 signup intent。

## 版本

- $schema_version: **0.2.0**
- v3 重构落盘:2026-07-26




