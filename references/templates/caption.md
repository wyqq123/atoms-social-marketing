# Caption Template

## Purpose

Stage 4(Render)在生成文本类 post 时使用此骨架。产物必须符合 `data/launch_pack_schema.json` 的 `Caption` definition。

## 输出结构(严格)

```json
{
  "angle_id": "<平台-序号,如 ig-01>",
  "platform": "ig | yt | tt",
  "post_type": "reels | carousel | short | tt-video | ig-static | ...",
  "hook": "<前 15 字符必须完成钩子>",
  "body": "<正文,3-6 行,含 key_selling_point>",
  "cta": {
    "text": "<行动号召文案>",
    "link_style": "bio-link | comment-pin | swipe-up | none"
  },
  "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
  "confidence": "low | medium | high",
  "media_prompts": {
    "cover_image": {
      "trigger": "on-demand",
      "injectable_prompt": "<可直接注入下游生图工具的完整 prompt>",
      "target_tool_hint": "midjourney | dall-e | ideogram",
      "aspect_ratio": "1:1 | 9:16 | 16:9 | 4:5"
    },
    "carousel_slides": null
  },
  "_rationale": "<引用 playbook 章节 + 选择依据>"
}
```

## 字段填充规则

### hook(必填)
- 长度上限:IG reels/tt-video ≤ 15 字符,carousel/short 可放宽到 20 字符
- 必须命中 `intent_profile.audience.pain_points` 之一
- Hook pattern 六种(引用 playbook §5):number-promise / broken-hook / before-after / pov / suspense / hot-take
- **不允许**:纯问句无信息量("Hi guys, ever wondered...")、通用套话

### body(必填)
- 3-6 行,每行不超过 30 字符(移动端断行考虑)
- **必须显式包含 key_selling_point**(Stage 5 自检会 grep)
- narrative_arc 推荐:problem → solution → CTA / setup → payoff / before → after

### cta.link_style 选择规则
- `bio-link` — IG 常用,平台不允许 feed 内外链
- `comment-pin` — IG/TT 用于评论区置顶引导,冷启动首选(算法加权)
- `swipe-up` — 仅 IG story / YT
- `none` — 品牌向内容,不做转化

### hashtags(数组,至少 5 条)
- 严格对应 Stage 3 `hashtag_mix.slots` 展平:1_broad → 2_mid_1 → 3_mid_2 → 4_niche → 5_brand
- 顺序:broad 在前,brand 在末尾
- IG:最多 30 个 hashtag;TT:最多 100 字符 hashtag 总长;YT:hashtag 放 description 前 3 行 + 视频标题

### media_prompts.cover_image
- **只当 post_type ∈ {carousel, ig-static, short(封面)} 时填** —— 视频类走 storyboard 的 media_prompts
- `injectable_prompt` 必须:
  - 至少 20 字符
  - 包含视觉主体、光线氛围、构图、风格三要素
  - 明确 aspect_ratio 与 post_type 匹配(carousel 1:1 或 4:5,IG story 9:16)
- **禁止**:占位符("TBD"/"...")、纯品类词("a picture of a landing page")
- `target_tool_hint` 二选一或多选:midjourney / dall-e / ideogram

### media_prompts.carousel_slides
- 仅 `post_type == "carousel"` 时填,长度 = 轮播 slide 数(3-10)
- 每 slide 一个 injectable_prompt,视觉连贯性由 prompt 序列表述(如"slide 1: hero shot; slide 2: same product from side angle")

### confidence
- `high` — playbook §5/§6/§9 有直接匹配的 pattern 且 case study 存在
- `medium` — playbook 支持但需要 LLM 组合
- `low` — 冷启动新品类,主要靠泛化规则

### _rationale
- 必填,非空
- 至少一句引用 playbook 章节(如 "hook 采用 number-promise,依据 §5 stop-rate 排 top-2")
- 若用了 TT Creative Center 数据,标注 snapshot_date

## 示例(完整合规 caption)

```json
{
  "angle_id": "ig-01",
  "platform": "ig",
  "post_type": "reels",
  "hook": "15 分钟做完能收钱的落地页",
  "body": "过去我要花一周搭 landing page。\n设计、切图、部署、接支付,坑一个不落。\n用 Atoms 后:一句 prompt,15 分钟拿到能收 Stripe 的页面。\n真实项目截图放下方 →",
  "cta": {
    "text": "评论区扣 1 我发详细教程",
    "link_style": "comment-pin"
  },
  "hashtags": ["#saas", "#indiehackers", "#buildinpublic", "#vibecoding", "#atomsdev"],
  "confidence": "high",
  "media_prompts": {
    "cover_image": null,
    "carousel_slides": null
  },
  "_rationale": "hook 采用 number-promise pattern(playbook §5 IG 该模式 stop-rate 排 top-2);CTA comment-pin 匹配 IG 冷启动评论加权算法(§7);hashtag 5-slot 完整覆盖 saas broad → atomsdev brand。reels 不需要 cover_image,靠视频首帧即封面。"
}
```
