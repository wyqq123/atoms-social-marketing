# Stage 5 — Pack & Self-check

## Purpose

组装 Launch Pack 顶层 JSON,跑自检规则,输出 checks(blocker / warning / info)与 `_pipeline_meta`。

## 输入

- 全部前置 stage 产物(intent_profile / platform_fit / strategies / deliverables)
- 原始 inputs(用于 launch_brief 回填)
- Playbook 版本信息(从 `references/platform-playbooks/{platform}.md` 顶部 frontmatter 或 `_schema_version` 读)

## 输出

符合 `data/launch_pack_schema.json` 的完整 Launch Pack JSON。

## LLM 动作(6 步)

### 1. 组装 launch_brief
从 inputs + intent_profile 抽:
- `app_name` ← `inputs.app_context.name`
- `one_liner` ← `intent_profile.app_summary.one_liner`
- `promo_goal` ← `inputs.positioning.promo_goal`(原文)
- `target_audience` ← `inputs.positioning.target_audience`(原文)
- `key_selling_point` ← `inputs.positioning.key_selling_point`(原文)
- `primary_market` ← `intent_profile.app_summary.market_primary`

### 2. 引入前置产物
- `platform_fit` ← Stage 2 输出(整体拷贝)
- `strategies` ← Stage 3 输出(整体拷贝)
- `deliverables` ← Stage 4 输出(整体拷贝)

### 3. 生成 schedule
读 `references/templates/schedule.md` 骨架,按规则生成 week_1:
- Launch day(offset=0):放 ranking 首位平台的 confidence=high angle
- 覆盖 3-6 条,单日单平台不重复
- 高 fit 平台占 ≥ 60%
- 每 scope 内平台首周至少 1 条(fit_score < 40 的也留 1 条试水)
- 引用 playbook §7 时段
- `notes` 填全周节奏综述

### 4. 跑自检规则
按以下清单逐条检查,分级填入 `checks.blocker` / `checks.warning` / `checks.info`。

#### Blocker 级(必须为空,否则 Launch Pack 不可用)
| ID | 规则 | 触发条件 |
|---|---|---|
| B1 | key_selling_point 覆盖 | 存在某个 caption.body 不含 `positioning.key_selling_point` 关键词(可宽松语义匹配)|
| B2 | media prompt 非占位 | 任一 `injectable_prompt` == "TBD" / "..." / 长度 < 20 字符 |
| B3 | 视频类 scene 三字段全空 | 某 storyboard.scenes[i] 的 video_prompt/image_prompt/b_roll_hint 全 null |
| B4 | 三平台 fit 全 < 40 | `platform_fit.scores` 中所有 fit_score < 40 |
| B5 | CTA 与 promo_intent 一致 | goal_type=cold-start/user-acquisition 但 cta.link_style=none 且 cta.text 无转化动作词(如"关注" / "评论" / "点击")|
| B6 | hashtags 5-slot 展平完整 | 某 caption.hashtags 数组 < 5 条,或不能对应回 strategy.hashtag_mix.slots 五槽 |
| B7 | schedule 覆盖不足 | schedule.week_1 长度 < 3 |
| B8 | media_generation_deferred 恒 true | `_pipeline_meta.media_generation_deferred != true`(设计契约不允许违反)|

#### Warning 级(记录但不阻断)
| ID | 规则 | 触发条件 |
|---|---|---|
| W1 | Hook 长度 | IG reels / tt-video hook > 15 字符,或 carousel / short hook > 20 字符 |
| W2 | TT trend snapshot 时效 | 使用了 trend_borrow,但 snapshot_date 距今 > 4 周(实际此情况 Stage 3 应设 null,若走到这里说明上游未处理)|
| W3 | Playbook `_schema_version` 不匹配 | 某 platform playbook 版本与 skill 期望不符 |
| W4 | Sound decay 临近 | 某 storyboard.sound_ref.decay_window_days_left < 5 |
| W5 | 变体缺失 | 有 confidence=high 的 post 但未生成 ab_variant |

#### Info 级(信息性提示)
| ID | 规则 | 触发条件 |
|---|---|---|
| I1 | GA4 未提供 | `_pipeline_meta.ga4_used == false` |
| I2 | scope 不完整 | `platform_scope` 只含 1-2 个平台 |
| I3 | Fit 排位悬殊 | ranking 首末 fit_score 差 > 40 |

### 5. 填 `_pipeline_meta`
- `playbook_versions`:读每个 platform playbook 的 `_schema_version` 或顶部 frontmatter date
- `trend_snapshot_last_refresh`:读 `data/tiktok_trend_snapshot.json.$last_refresh`(若 platform_scope 含 tt);否则 null
- `confidence_summary`:每平台的 confidence 由 Stage 3 已隐含(取该平台 angles confidence 的最低值,再向上映射到 low/medium/medium-high/high)
- `ga4_used`:`inputs.ga4_snapshot != null && intent_profile.ga4_signals != null`
- `media_generation_deferred`:**恒 true**(硬编码)
- `injectable_prompts_count.images`:遍历 deliverables 数所有 `media_prompts.cover_image` + `media_prompts.carousel_slides[]` + `scenes[].media_prompts.image_prompt` 非 null 的
- `injectable_prompts_count.videos`:遍历 `scenes[].media_prompts.video_prompt` 非 null 的

### 6. 填 top-level `generated_at`
ISO 8601 时间戳,精度到秒。

## 输出示例(顶层结构)

```json
{
  "$schema_version": "0.1.0",
  "generated_at": "2026-07-03T10:32:00Z",
  "launch_brief": { "..." },
  "platform_fit": { "..." },
  "strategies": { "ig": {}, "yt": {}, "tt": {} },
  "deliverables": { "ig": {}, "yt": {}, "tt": {} },
  "schedule": { "week_1": [] },
  "checks": {
    "blocker": [],
    "warning": ["TT trend snapshot age = 21 days, still fresh"],
    "info": ["GA4 snapshot not provided"]
  },
  "_pipeline_meta": {
    "playbook_versions": { "ig": "2026-07-01", "yt": "2026-07-01", "tt": "2026-07-01" },
    "trend_snapshot_last_refresh": "2026-06-18",
    "confidence_summary": { "ig": "medium-high", "yt": "medium", "tt": "high" },
    "ga4_used": false,
    "media_generation_deferred": true,
    "injectable_prompts_count": { "images": 12, "videos": 8 }
  }
}
```

## 边界情况

| 场景 | 处理 |
|---|---|
| 任一 Blocker 触发 | Launch Pack 仍然完整输出,但顶层附加 warning "❌ Blocker present, launch pack not ready to ship";上层收到应提示用户修 |
| Playbook `_schema_version` 缺失 | `playbook_versions.{platform}` 填 "unknown",触发 W3 |
| trend_snapshot 文件不存在 | `trend_snapshot_last_refresh: null`,不 warning(未使用) |

## 输出交给下游(上层)

- 上层 Atoms builder 消费完整 Launch Pack
- 用户看到 posts / storyboards 后,针对某个 media_prompts 显式触发"生成图片/视频",上层负责把 injectable_prompt 注入对话
- 上层根据 checks 决定是否阻塞发布或提示用户
