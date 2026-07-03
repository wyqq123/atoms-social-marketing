---
name: atoms-social-marketing
description: 为 Atoms 用户构建的应用生成首发社媒内容包(IG/YT/TikTok)。输入应用上下文 + 定位澄清 + 可选 GA4,输出多产物 JSON(caption + storyboard + schedule + 挂载 media prompt)。媒体产物只挂载 injectable_prompt,不触发生成。
---

# Atoms Social Marketing

## 何时启用

- 用户已在 Atoms builder 完成应用构建
- 需要为该应用生成社媒首发内容包(首周节奏)
- 已通过上层对话/表单收集齐 positioning 三要素(promo_goal / target_audience / key_selling_point)

**不适用**:
- 长期(> 1 周)运营节奏规划(v0.1 不覆盖)
- LinkedIn / X 平台(playbook 未沉淀)
- 直接生成图片/视频素材(见"媒体资产两级触发契约")

## Pipeline 概览

5 阶段线性 pipeline,无状态,每次调用独立完成。

```
inputs
   ↓
Stage 1  Intent & Positioning   →  intent_profile
   ↓
Stage 2  Platform Fit           →  platform_fit
   ↓
Stage 3  Content Strategy       →  strategies[per platform]
   ↓
Stage 4  Deliverable Rendering  →  deliverables[per platform]
   ↓
Stage 5  Pack & Self-check      →  Launch Pack JSON
```

详见 `references/pipeline/stage-{1..5}-*.md`。

## 输入契约

见 `data/inputs_schema.json`(JSON Schema draft-07)。

**必填**:
- `app_context.{name, description, category}`
- `builder_prompt`(> 50 字符)
- `positioning.{promo_goal, target_audience, key_selling_point}`

**可选**:
- `ga4_snapshot`(GA4 汇总数据;若无,pipeline 只用 positioning 与 builder_prompt)
- `platform_scope`(默认 `["ig", "yt", "tt"]`)

## 输出契约

见 `data/launch_pack_schema.json`。

顶层字段:
- `launch_brief` — 精简摘要
- `platform_fit` — 平台匹配度 ranking + scores
- `strategies` — 每平台 angles + hashtag mix + cadence
- `deliverables` — 每平台 posts + storyboards + ab_variants
- `schedule` — 首周节奏表
- `checks` — 自检结果(blocker / warning / info)
- `_pipeline_meta` — 版本 / 时效 / 计数元数据

## 媒体资产两级触发契约

**Pipeline 只挂载 `injectable_prompt` 字符串,不生成任何图片/视频**。

- Stage 4 输出的每个 `media_prompts.*` 对象含 `trigger: "on-demand"` 标记
- `injectable_prompt` 是可直接注入对话让下游 image/video 工具消费的完整 prompt
- **上层 Atoms builder 负责**:
  1. 展示挂载的 prompt(隐藏或折叠)
  2. 提供"生成图片"/"生成视频"按钮
  3. 用户点击时,把 `injectable_prompt` 注入对话由下游工具生成

Pipeline 侧责任边界到此为止,不管生成成功与否。`_pipeline_meta.media_generation_deferred == true` 恒成立。

## Stage 索引

| Stage | 文件 | 用途 |
|---|---|---|
| 1 Intent | `references/pipeline/stage-1-intent.md` | 归一化定位画像 |
| 2 Fit | `references/pipeline/stage-2-fit.md` | 平台匹配度评分 |
| 3 Strategy | `references/pipeline/stage-3-strategy.md` | Angles + hashtag mix + cadence |
| 4 Render | `references/pipeline/stage-4-render.md` | 渲染 caption/storyboard + 挂载 prompt |
| 5 Pack | `references/pipeline/stage-5-pack.md` | 组装 + 自检 |

## 模板

| 模板 | 文件 | 消费 stage |
|---|---|---|
| Caption | `references/templates/caption.md` | Stage 4 |
| Storyboard | `references/templates/storyboard.md` | Stage 4 |
| Schedule | `references/templates/schedule.md` | Stage 5 |

## Playbook 引用

`references/platform-playbooks/{ig,yt,tiktok}.md` —— 各平台十节结构知识(契约见 `_schema.md`)。

Stage 消费映射:
- Stage 2 读 §2 §4
- Stage 3 读 §5 §6 §7 §9
- Stage 5 读顶部 frontmatter 取 `_schema_version`

## 数据资产

| 文件 | 用途 |
|---|---|
| `data/tiktok_trend_snapshot.json` | Creative Center 快照(2-4 周刷新);Stage 3 TT trend_borrow 消费 |
| `data/tiktok_case_studies.json` | TT 案例;Stage 3 定性引用 |
| `data/ig_case_studies.json` | IG 案例;Stage 3 定性引用 |
| `data/youtube_case_studies.json` | YT 案例;Stage 3 定性引用 |
| `data/*_manual_supplements.md` | 各平台人工补齐;Stage 3 定性引用 |

## 采集脚本(不在 pipeline 内)

`scripts/` 目录含平台数据采集流程(oEmbed / Data API / Creative Center refresh)。Pipeline 只消费 `data/` 内已落盘产物,不实时抓取。

## 扩展点(v0.1 不实现,v0.2+ 会引入)

| 扩展点 | 预留位置 | 处理 |
|---|---|---|
| Session/memory | inputs 顶层 `session_id` | v0.1 忽略;v0.2 引入,支持二次生成 diff |
| 反馈闭环 | Stage 5 后接 Stage 6 | v0.1 不实现;v0.3 接效果反馈 |
| LinkedIn / X | `platform_scope` 白名单扩展 | v0.1 拒绝非 ig/yt/tt;补齐 playbook 后自动生效 |
| 自定义模板 | `references/templates/` | v0.1 固定 3 类;v0.2 用户可上传 |
| 多语言 | Stage 4 `locale_override` | v0.1 英文;v0.3 按 target_market 本地化 |

## 版本

- $schema_version: **0.1.0**
- 首次落盘:2026-07-03
- Spec: `/Users/shendufuzhi2026/Documents/社媒内容需求洞察/2026-07-03-launch-pack-pipeline-design.md`
