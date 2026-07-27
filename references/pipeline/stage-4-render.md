# Stage 4 - Deliverable Rendering per Platform

## Purpose

把 Stage 3 每平台 strategy 渲染成用户可直接使用的产物:captions / storyboards / ab_variants。Pipeline 不生成图片或视频,只挂载 `injectable_prompt` 字符串。

## 输入

- `intent_profile`(Stage 1)
- `app_icp_vector`(Stage 1; end-user ICP + builder production constraints)
- `platform_fit`(Stage 2,用于 confidence/probe gate)
- `strategies`(Stage 3)
- `references/templates/caption.md`
- `references/templates/storyboard.md`

## 输出

对每个发布 platform:

```json
{
  "posts": [],
  "storyboards": [],
  "ab_variants": []
}
```

## 渲染规则

### Caption

- `caption.body` 必须覆盖 `intent_profile.value_prop.key_selling_point` 的核心语义,并使用 built app 终端用户能理解的 pain/JTBD 语言。
- `caption.confidence` 不得高于 Stage 2/3 的可解释置信:若 `score_confidence <= medium`,caption confidence 最高 `medium`。
- 若 `probe_status != usable`,不得写当前趋势、近期热度、大家正在讨论等措辞。
- hashtags/keywords 必须来自 Stage 3 的五槽 mix,按槽位展平。

### CTA 映射

默认 CTA 路径:

| Platform | Preferred CTA |
|---|---|
| instagram | `bio-link` 或 `comment-pin` |
| tiktok | `comment-pin` 或 `profile-link` |
| youtube | `description-link` 或 `comment-pin` |
| reddit | `comment-pin`/soft resource,避免首帖硬广 |
| x | `profile-link` 或 reply CTA |
| linkedin | `profile-link`, `dm`, 或评论领取 |
| pinterest | pin link / profile link |
| rednote | comment CTA / profile |
| douyin | profile / shop-or-form when available |

CTA 必须符合平台 norms;如果 Stage 2 risks 提示反营销风险,优先轻 CTA。

### Storyboard

视频类 post 产出 storyboard + caption;非视频类只产 caption。Storyboard scenes 必须至少包含 hook 和 CTA,且每个视频类 scene 不能让 `video_prompt`、`image_prompt`、`b_roll_hint` 三者全空。

### Media prompts

每个 `media_prompts.*` 对象必须:

- `trigger: "on-demand"`
- `injectable_prompt` >= 20 字符
- 包含主体、光线/氛围、构图/风格、aspect ratio 或 duration hint

Pipeline 不消费生成结果,上层负责用户点击后的图片/视频生成。

### A/B 变体

只对 high-confidence posts 生成 1 个 caption 变体。若 Stage 2 confidence 被 probe failure 或无证据 cap 到 medium,不要生成 high-confidence 变体。

## 自检前置

在交给 Stage 5 前检查:

- 没有 prohibited current-trend wording when `probe_status != usable`。
- 没有把 evidence brief 的少量样本写成 broad trend,也没有把 builder 自画像写成终端用户画像。
- 没有使用禁用字段或不可验证 demographics/buyer intent。
- 每个 media prompt 非占位。

## 输出交给下游

Stage 5 组装 Launch Pack,统计 injectable prompt,并执行 blocker/warning gate。

