# Stage 4 — Deliverable Rendering(per platform)

## Purpose

把 Stage 3 每平台的 strategy 渲染成用户可直接使用的产物:captions / storyboards / ab_variants。分两步 —— 骨架生成(a) + 挂载 media prompts(b)。

**核心契约**:不生成任何图片/视频素材,只挂载 `injectable_prompt` 字符串。

## 输入

- `intent_profile`(Stage 1)
- `strategies`(Stage 3,全平台)
- 模板文件:
  - `references/templates/caption.md`
  - `references/templates/storyboard.md`

## 输出

对每个 platform ∈ platform_scope:

```json
{
  "posts": [ /* Caption[], 每 angle 一条 */ ],
  "storyboards": [ /* Storyboard[], 仅视频类 angle */ ],
  "ab_variants": [ /* Caption[], 见规则 */ ]
}
```

顶层:`deliverables = { "ig": {...}, "yt": {...}, "tt": {...} }`。

## LLM 动作 —— Step a:骨架生成

### 对每个 angle
1. 判断 post_type 是否视频类:
   - 视频类(reels / short / tt-video-*):同时产出 storyboard + caption(caption 嵌入 storyboard 内 `caption` 字段,同时 posts 数组也放一份用于 schedule 引用)
   - 非视频类(carousel / ig-static / yt-thumbnail-post):只产出 caption
2. 按 `references/templates/caption.md` 填 caption 骨架(hook / body / cta / hashtags / confidence / _rationale)
3. 视频类按 `references/templates/storyboard.md` 填 scenes 骨架(scene_id / duration_s / purpose / visual_note / text_overlay / voiceover_or_dialogue / b_roll_hint)

### 关键约束
- `caption.hashtags` 必须是 Stage 3 `hashtag_mix.slots` 展平的完整集合(1_broad → 2_mid_1 → 3_mid_2 → 4_niche → 5_brand 顺序)
- `caption.body` 必须显式含 `intent_profile.value_prop.key_selling_point`(Stage 5 grep 自检)
- `caption.cta.link_style` 按 platform 选:
  - IG:`comment-pin`(冷启动首选)/ `bio-link`
  - TT:`comment-pin`(几乎总选)
  - YT:`bio-link`(video description)
- storyboard.scenes 首个 purpose 必须 `hook`,至少一个 `cta`
- scenes.duration_s 之和必须等于 total_duration_s

## LLM 动作 —— Step b:挂载 media prompts

### 关键契约(重复强调)
- **不触发任何生成**
- 只填 `injectable_prompt` 字符串
- 每个 `media_prompts.*` 对象含 `trigger: "on-demand"` 标记

### Caption.media_prompts
- **视频类 caption**(post_type ∈ {reels, short, tt-video-*}):`cover_image: null`, `carousel_slides: null`(视频首帧即封面)
- **carousel**:`cover_image: null`, `carousel_slides: [ ...N slides ]`,N = 3-10
- **ig-static / yt-thumbnail-post**:`cover_image: {填}`, `carousel_slides: null`

Injectable_prompt 撰写四要素:
1. 视觉主体(what)
2. 光线氛围(mood/lighting)
3. 构图/风格(composition/style)
4. aspect_ratio(明确)

示例("A vibrant flat-lay of a MacBook showing a colorful landing page on screen, wooden desk, morning natural light, coffee cup blurred in corner, 1:1 aspect ratio, minimal aesthetic")。

### Storyboard.scenes[].media_prompts
对每个 scene:
- 若 scene 用用户自拍/现成素材(如"实际使用录屏"):`video_prompt: null, image_prompt: null, b_roll_hint: "..."`(非空)
- 若 scene 需要 AI 生成视频:填 `video_prompt`(injectable_prompt + duration_hint_s + aspect_ratio),`image_prompt: null`
- 若 scene 用静态图叠字幕:填 `image_prompt`,`video_prompt: null`

Injectable_prompt for video_prompt 撰写四要素:
1. 镜别(close-up / medium / wide)
2. 主体 + 动作
3. 光线 + 场景
4. 时长 + aspect_ratio(9:16 for TT/reels/shorts)

### 违规硬约束(Stage 5 会 blocker)
- `injectable_prompt` 内容为 "TBD" / "..." / 纯占位符 → blocker
- `injectable_prompt` 长度 < 20 字符 → blocker
- 视频类 scene 三字段(video_prompt / image_prompt / b_roll_hint)全为 null → blocker

## LLM 动作 —— A/B 变体(ab_variants)

- **仅对 `confidence == "high"` 的 posts 生成变体**
- 每 high-confidence post 生成 **1 个** variant
- 变体差异维度(选一):
  - **Hook 变体**:换一个 hook_pattern(如 number-promise → hot-take)
  - **CTA 变体**:换 cta.text(如"评论区扣 1"→"关注我看下一条")
- `angle_id` 后缀 `-v2` 区分(如 `ig-01-v2`)
- 变体不重复生成 storyboard,只做 caption(即使原 post 是视频类)—— 变体主要测文案 CTR
- `_rationale` 说明变体维度选择

## 边界情况

| 场景 | 处理 |
|---|---|
| Stage 3 strategy 只有 3 个 angles,且都 confidence != high | ab_variants 空数组 |
| storyboard scenes 总时长 ≠ total_duration_s | 自动调整最后一个 scene 的 duration_s 补足;`_rationale` 标注 |
| TT 平台但 `trend_borrow == null` | storyboard.sound_ref 走 `source: "original"`;`_rationale` 标注 "trend snapshot expired, falling back to original sound" |
| carousel post_type 但 Stage 3 未指定 slide 数量 | 默认 5 slides |
| 视频类 post_type 但 total_duration_s 超出平台上限(如 tt-video-15s 拿到 20 秒) | 强制截到平台上限;`_rationale` 标注 |

## injectable_prompt 契约要点(汇总)

- 每个 `injectable_prompt` 必须 ≥ 20 字符、非占位、含四要素
- 每个 `injectable_prompt` 挂载点必须带 `trigger: "on-demand"`
- `injectable_prompt` 是给下游图片/视频工具消费的完整字符串,不做二次解析
- Pipeline 不消费任何 `injectable_prompt` 生成结果 —— 生成状态归上层管理

## 输出交给下游

Stage 5 组装 launch pack 时:
- 从 deliverables 遍历所有 injectable_prompts,计数 → `_pipeline_meta.injectable_prompts_count`
- 校验每个 injectable_prompt 非空非占位 → checks.blocker/warning
- 校验 hashtags 5-slot 展平完整性 → checks.blocker
- 校验 body 含 key_selling_point → checks.blocker
