# Stage 2 — Platform Fit

## Purpose

对 `inputs.platform_scope` 内每个平台计算 `fit_score`(0-100),给出推荐排序。**不过滤** —— 所有 scope 内平台都进入 Stage 3-4。

## 输入

- `intent_profile`(Stage 1 输出)
- `inputs.platform_scope`

## 输出

```json
{
  "ranking": ["tt", "ig", "yt"],
  "scores": {
    "ig": {
      "fit_score": 72,
      "strengths": ["string"],
      "weaknesses": ["string"],
      "recommended_focus": ["reels", "carousel"]
    },
    "yt": { "fit_score": 58, "..." },
    "tt": { "fit_score": 84, "..." }
  },
  "_rationale": "string"
}
```

## LLM 动作(4 步)

### 1. 读 playbook §2 §4
对每个 platform ∈ platform_scope:
- 读 `references/platform-playbooks/{platform}.md` 的 §2(平台受众画像)
- 读 §4(内容形式适配)
- 校验 playbook `_schema_version`,不匹配则 warning(不阻断)

### 2. 计算 fit_score(0-100)
按下述加权计算(v0.1 硬编码权重,v0.2 可参数化):

| 维度 | 权重 | 计算方式 |
|---|---|---|
| Audience overlap | 40 | `intent_profile.audience.primary_persona` 与 playbook §2 主受众画像的语义重叠度(LLM 判断 0-40)|
| Goal-format fit | 30 | `intent_profile.promo_intent.goal_type` × playbook §4 平台优势内容形式的匹配度(0-30)|
| Category leverage | 20 | `app_summary.category_normalized` 在该平台的历史 case study 密度(读 playbook §9 winning structures,0-20)|
| Time horizon | 10 | `time_horizon=week-1` 时冷启动快平台加分(TT +10 / IG +5 / YT +2);month-1 平均 |

### 3. 生成 strengths / weaknesses / recommended_focus
每平台至少 2 个 strengths + 2 个 weaknesses:
- **strengths**:引用 playbook §2 或 §4 具体表述("carousel engagement 是 reels 的 1.5x")
- **weaknesses**:诚实标注(如 YT week-1 冷启动难 → weakness)
- **recommended_focus**:从 playbook §4 支持形式中选与 intent 最匹配的 1-3 个 post_type,如 `["reels", "carousel"]`

### 4. Ranking
按 fit_score 降序;并列取 goal-format fit 更高者优先。

## 边界情况

| 场景 | 处理 |
|---|---|
| 三平台 fit_score 全 < 40 | 输出正常 ranking,同时在 `_rationale` 明确标记 "all platforms weak fit"。Stage 5 会据此填 blocker |
| 某平台 playbook `_schema_version` 缺失或不匹配 | 该平台按 playbook 内容跑,但 confidence 降级到 medium;Stage 5 加 warning |
| `platform_scope` 只含 1 个平台 | ranking 只有一项,scores 也只一项;不做跨平台比较文字 |
| `ga4_signals.traffic_source_bias == "producthunt-heavy"` | TT 加分 +5(PH 受众与 TT 冷启动人群重叠高)|
| `intent_profile.audience.tone_preference == "build-in-public"` | TT + IG 各加分 +3,YT 减分 -3(YT long-form 偏教程调性)|

## _rationale 填写规范

- 至少两句
- 第一句解释 ranking 首位的核心依据
- 第二句解释末位的核心 weakness(或说明三平台均衡时的分布逻辑)
- 若触发了任何加/减分调整规则(如 tone 调整),必须明说

示例:
> "TT 排第一因 goal_type=cold-start × primary_persona 是 SMB solo builder,与 §2 TT 受众重叠度极高;tone_preference=build-in-public 触发 +3。YT 末位因 week-1 time_horizon 与 YT §7 冷启动 3-6 个月周期错位,尽管教程类 category leverage 强(§9 有 12 个 case)。"

## 输出交给下游

Stage 3 每个平台的 strategy 都读 `scores.{platform}.recommended_focus` 决定 angles 的 post_type 分布。
Stage 5 用 `ranking` 决定 schedule 的平台占比。
