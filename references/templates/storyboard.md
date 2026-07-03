# Storyboard Template

## Purpose

Stage 4(Render)在生成视频类 post(reels / short / tt-video)时使用此骨架。产物必须符合 `data/launch_pack_schema.json` 的 `Storyboard` definition。

## 输出结构(严格)

```json
{
  "angle_id": "<平台-序号>",
  "platform": "ig | yt | tt",
  "post_type": "reels | short | tt-video-15s | tt-video-25s | ...",
  "total_duration_s": 15,
  "sound_ref": {
    "source": "creative-center-trending | original | licensed | none",
    "sound_id": "<TikTok Creative Center sound_id 或 null>",
    "decay_window_days_left": 7
  },
  "scenes": [
    {
      "scene_id": 1,
      "duration_s": 3,
      "purpose": "hook | context | reveal | proof | cta | loop",
      "visual_note": "<镜头描述:镜别 / 场景 / 主体动作>",
      "text_overlay": "<屏幕上出现的文字,可 null>",
      "voiceover_or_dialogue": "<配音或对白,可 null>",
      "b_roll_hint": "<B-roll 建议,可 null>",
      "media_prompts": {
        "trigger": "on-demand",
        "video_prompt": {
          "injectable_prompt": "<完整可注入的视频生成 prompt>",
          "target_tool_hint": "runway | pika | sora | veo",
          "aspect_ratio": "9:16 | 16:9 | 1:1",
          "duration_hint_s": 3
        },
        "image_prompt": null
      }
    }
  ],
  "caption": { "<... Caption 结构 ...>": "同 caption.md" },
  "_rationale": "<引用 playbook §5 §9 + sound 选择理由>"
}
```

## 字段填充规则

### total_duration_s
- TikTok:15 / 25 / 30 / 60 秒常见,推荐 15-30(FYP 首选窗口)
- IG Reels:15 / 30 / 60 / 90 秒
- YT Shorts:≤ 60 秒(3 分钟 shorts 是 2026 新形式,若用需标注)

### sound_ref
- 仅 TT 平台可能填 `creative-center-trending`,IG/YT 一般填 `original` 或 `licensed`
- 若 `source == "creative-center-trending"`,必须包含 `sound_id` 和 `decay_window_days_left`
- `decay_window_days_left < 5` 时,Stage 5 自检 warning(避免推荐将过期的 sound)

### scenes[](数组)
- 长度:total_duration_s / 3 上下(3 秒一个 beat 是移动端节奏基准)
- 每个 scene `duration_s` 之和必须等于 `total_duration_s`
- **必须至少包含 purpose=hook 与 purpose=cta 各一个**
- **推荐**:结尾 scene 设计 loop hint(TT playbook §9 rewatch 信号)

### scene.purpose 六种含义
- `hook` — 前 1-3 秒抓注意力(number-promise / suspense / before-after 前半)
- `context` — 交代场景/主体
- `reveal` — 卖点/答案揭示
- `proof` — 数字 / 截图 / 真实使用
- `cta` — 引导评论/关注/点链接
- `loop` — 与开头呼应,鼓励重看

### scene.visual_note
- **必填**,是给拍摄/生成的镜头指令
- 格式:`<镜别> + <主体> + <动作>`,例如"特写,手持 iPhone,拇指滑动屏幕"
- 避免抽象("好看的场景")

### scene.media_prompts.video_prompt
- 若 scene 是纯 B-roll(用户自拍/现成素材),`video_prompt` 可为 null,但 `image_prompt` 也须为 null 时 scene 至少 `b_roll_hint` 非 null
- 若 `video_prompt` 存在:
  - `injectable_prompt` ≥ 20 字符,含"镜头类型 + 主体 + 光线 + 时长"四要素
  - `duration_hint_s` 与 scene `duration_s` 一致
  - `aspect_ratio` 与 post_type 一致(短视频 9:16,横屏 shorts 16:9,ig 1:1 罕见)

### scene.media_prompts.image_prompt
- 用于静态图叠字幕或 photo-mode 帧,通常与 `video_prompt` 互斥(一个 scene 二选一,或都 null 走 b_roll_hint)

### caption(必填)
- 完整嵌入一个符合 `caption.md` 规则的对象
- 视频描述文案,IG/TT 显示在视频下方,YT 显示在 description
- caption.media_prompts.cover_image 一般 null(视频首帧即封面),除非 platform=yt 需要单独 thumbnail

### _rationale
- 必填,至少两句
- 说明 hook 选择 + sound 选择 + scene 节奏的 playbook 依据

## 示例(完整合规 storyboard)

```json
{
  "angle_id": "tt-02",
  "platform": "tt",
  "post_type": "tt-video-15s",
  "total_duration_s": 15,
  "sound_ref": {
    "source": "creative-center-trending",
    "sound_id": "7XXXXXXXXX",
    "decay_window_days_left": 8
  },
  "scenes": [
    {
      "scene_id": 1,
      "duration_s": 3,
      "purpose": "hook",
      "visual_note": "特写,手写白板列 3 个痛点,红笔",
      "text_overlay": "SaaS founder 都会掉的 3 个坑",
      "voiceover_or_dialogue": null,
      "b_roll_hint": null,
      "media_prompts": {
        "trigger": "on-demand",
        "video_prompt": {
          "injectable_prompt": "Close-up shot, hands writing '3 mistakes SaaS founders make' on a white whiteboard with red marker, natural office light, documentary style, 9:16 vertical, 3 seconds",
          "target_tool_hint": "runway | pika | sora",
          "aspect_ratio": "9:16",
          "duration_hint_s": 3
        },
        "image_prompt": null
      }
    },
    {
      "scene_id": 2,
      "duration_s": 4,
      "purpose": "context",
      "visual_note": "中景,MacBook 屏幕,滚动老式 landing page builder 界面",
      "text_overlay": "以前:一周才能上线一个页面",
      "voiceover_or_dialogue": null,
      "b_roll_hint": null,
      "media_prompts": {
        "trigger": "on-demand",
        "video_prompt": {
          "injectable_prompt": "Medium shot, MacBook screen showing an old-school landing page builder with cluttered UI, hands scrolling through complex settings, warm desk light, 9:16 vertical, 4 seconds",
          "target_tool_hint": "runway | pika",
          "aspect_ratio": "9:16",
          "duration_hint_s": 4
        },
        "image_prompt": null
      }
    },
    {
      "scene_id": 3,
      "duration_s": 5,
      "purpose": "reveal",
      "visual_note": "屏幕录制,Atoms builder 一句 prompt → 页面生成过程",
      "text_overlay": "现在:15 分钟能收 Stripe 的落地页",
      "voiceover_or_dialogue": null,
      "b_roll_hint": "实际使用录屏(用户提供)",
      "media_prompts": {
        "trigger": "on-demand",
        "video_prompt": null,
        "image_prompt": null
      }
    },
    {
      "scene_id": 4,
      "duration_s": 3,
      "purpose": "cta",
      "visual_note": "特写,手指向下点评论区,微笑",
      "text_overlay": "评论区扣 1 发教程",
      "voiceover_or_dialogue": null,
      "b_roll_hint": null,
      "media_prompts": {
        "trigger": "on-demand",
        "video_prompt": {
          "injectable_prompt": "Close-up, index finger pointing downward toward camera, cheerful expression blurred in background, warm natural light, 9:16 vertical, 3 seconds",
          "target_tool_hint": "runway | pika",
          "aspect_ratio": "9:16",
          "duration_hint_s": 3
        },
        "image_prompt": null
      }
    }
  ],
  "caption": {
    "angle_id": "tt-02",
    "platform": "tt",
    "post_type": "tt-video-15s",
    "hook": "SaaS founder 3 个坑",
    "body": "看到第三个我拍大腿。\n\n#1 花一周做 landing page\n#2 接 Stripe 又要一周\n#3 上线才发现没人来\n\nAtoms 帮我把 1+2 压到 15 分钟。",
    "cta": { "text": "评论 1 发教程", "link_style": "comment-pin" },
    "hashtags": ["#tech", "#saas", "#buildinpublic", "#vibecoding", "#atomsdev"],
    "confidence": "high",
    "media_prompts": { "cover_image": null, "carousel_slides": null },
    "_rationale": "hook 用 pain-point-listing 变体(playbook §5),TT 上 3 秒内 promise 具体数量有效。"
  },
  "_rationale": "hook scene 3 秒抓 pain,scene 2 建立 before,scene 3 reveal 卖点(录屏最真实),scene 4 comment-pin CTA。Sound 从 Creative Center 拉当期 Tech 类 trending,decay 8 天在安全窗口(§9 sound 建议)。总 15 秒符合 TT FYP 优选窗口(§4)。"
}
```
