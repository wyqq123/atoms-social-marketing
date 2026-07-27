# Stage 3 - Content Strategy per Platform

## Purpose

为 Stage 2 ranking 内的发布平台生成 `PlatformStrategy`:3-5 个 angles + hashtag/keyword mix + posting cadence + 可选 `trend_borrow`。

Stage 3 的核心变化:默认使用 evergreen platform strategy。只有当 `platform_fit.scores.{platform}.probe_status == "usable"` 且 `_evidence_refs` 至少 2 条时,才允许使用 `why_now` 或近期终端用户需求语言做轻量校准。

## 输入

- `intent_profile`(Stage 1)
- `app_icp_vector`(Stage 1; `end_user_identity`/pains/JTBD 用于 angle 和 wording, `builder_context`/production_constraints 用于制作约束)
- `platform_fit`(Stage 2)
- `data/platform_registry.json` 的 stable profile 和 content surfaces
- 对已有 playbook 平台: `references/platform-playbooks/{platform}.md` §5 §6 §7 §9
- 可选: `platform_fit.opportunity_evidence_briefs[]`
- 可选: 手动/cache 趋势样本,但必须不含 fit 标签

## 输出

对每个发布 platform 产出一个 `PlatformStrategy`(见 `data/launch_pack_schema.json`)。

```json
{
  "youtube": {},
  "reddit": {},
  "instagram": {}
}
```

`web_search` 不是发布平台,不得出现在 `strategies`。

## LLM 动作

### 1. 选择可渲染 surfaces

优先使用 Stage 2 的 `recommended_surfaces`。若该平台无完整 playbook,使用 `data/platform_registry.json.platforms.{platform}.stable_platform_profile.surface_map` 和 `platform_coverage_registry.content_surfaces` 生成保守 strategy,并降低 confidence。

### 2. Angle 生成

数量按 `fit_score`:

- `fit_score >= 70`:5 angles
- `40 <= fit_score < 70`:4 angles
- `fit_score < 40`:3 angles

每个 angle 必须:

- 覆盖 `intent_profile.value_prop.key_selling_point` 的核心机制。
- 对齐 `app_icp_vector.conversion_goal.desired_action`,并面向 `app_icp_vector.end_user_identity` 描述的终端用户。
- 使用平台原生表达方式,如 Reddit problem story/comment reply、YouTube tutorial/comparison、Instagram carousel/Reels、TikTok short demo、LinkedIn POV/document、Pinterest template/checklist、Rednote note guide。
- 不把 evidence brief 中的少量样本夸大为平台趋势。

### 3. Hashtag/keyword mix

保留五槽结构,但按平台解释:

- Instagram/TikTok/Rednote/Douyin: hashtag mix。
- YouTube/Pinterest: keyword/topic mix,可作为 title/description/tag/Pin title 输入。
- Reddit/LinkedIn/X: topic/keyword mix,hashtags 仅在平台规范允许时少量使用。

不得从过期或 `weak/unavailable` evidence 中提取“当前热门”标签。无 usable evidence 时只使用 evergreen keywords。

### 4. Posting cadence

根据 ranking 和 production constraints:

- 首位平台:3-5 posts。
- 第二平台:2-3 posts。
- 低 fit 或高生产摩擦平台:1-2 posts 试水。
- 所有 cadence 必须引用 registry/playbook 的 distribution 或 posting time rationale。

### 5. `trend_borrow` gate

`trend_borrow` 只能来自:

- `probe_status == usable` 且 evidence refs >= 2 的 `opportunity_evidence_brief`。
- 授权账号 insight。
- 未过期的 manual/cache platform sample。

`trend_borrow.usage_boundary` 必须说明“用于校准 wording/angle,不声明 broad trend”。无 usable evidence 时 `trend_borrow: null`。

### 6. `_rationale`

写 3-5 句:

1. angle 数量和 surface 选择依据。
2. 平台心智、CTA 和 production constraints 的匹配。
3. 是否使用 usable evidence;若未使用,明确说明是 stable strategy。
4. 主要风险或 confidence 限制。

## 禁止行为

- 无 usable evidence 时写“现在很火”“近期大家都在讨论”。
- 使用 `fit_verticals`、`fit_goal_types`、`relevance_to_atoms`。
- 从 web_search fallback 单独得出平台热度结论。
- 为 cache/manual/authorized-only 平台假装运行了实时全站探针。

## 边界情况

| 场景 | 处理 |
|---|---|
| 平台无 playbook 但 registry 完整 | 生成保守 strategy,`_rationale` 标注 registry-only |
| `score_confidence <= medium` | angle confidence 不得整体标 high |
| `probe_status != usable` | `trend_borrow=null`,避免 why-now wording |
| 平台 policy 与 CTA 冲突 | 调整 CTA 为评论/私信/profile 轻动作,必要时 Stage 5 warning |
| builder 生产素材不足 | 降低视频类 angle 数量,优先 text/image/screenshot 可表达内容 |

## 输出交给下游

Stage 4 读取 strategies 渲染 caption/storyboard/media prompts。Stage 5 检查 evidence gate、trend wording、confidence 和 platform registry version。

