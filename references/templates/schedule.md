# Schedule Template

## Purpose

Stage 4(Render)最后一步 / Stage 5 组装时生成首周发布节奏表。产物落在 Launch Pack 的 `schedule.week_1`。

## 输出结构(严格)

```json
{
  "week_1": [
    {
      "day": "Mon | Tue | Wed | Thu | Fri | Sat | Sun",
      "date_offset_from_launch": 0,
      "platform": "ig | yt | tt",
      "post_ref": "<angle_id, 如 tt-02>",
      "recommended_time": "<本地时区 12h 格式,如 '9am ET'>",
      "rationale": "<为什么选此日/此时段>"
    }
  ],
  "notes": "<全周节奏综述,可空字符串>"
}
```

## 填充规则

### 覆盖天数
- **week_1 至少 3 条发布**,不上限;推荐 4-6 条(避免刷屏但保证 momentum)
- 单日单平台最多 1 条,避免用户重复看到同 caption

### day / date_offset_from_launch
- `date_offset_from_launch=0` 是发射日
- day 字段是可读周几,offset 是与 launch 的相对天数
- 首发日建议放**最高 fit_score 平台**的**旗舰 angle**(fit 排第一 + confidence=high)

### platform 分布
- 高 fit_score 平台占 60% 以上频次
- 每平台首周至少 1 条(不放弃任何 scope 内平台,除非 fit_score < 40 且已 blocker)

### recommended_time 时段选择
- 每平台参照对应 playbook §7 中 target_market 时区的高活跃时段
- 若 `primary_market == ["US"]`,默认时区 ET;若跨市场,选主市场时区并在 rationale 标注

### 平台 × 时段速查(默认 US ET,仅 v0.1 硬编码;v0.2 参数化)

| 平台 | 工作日推荐 | 周末推荐 | 依据 |
|---|---|---|---|
| IG | Tue 9am / Thu 12pm | Sat 10am | playbook §7 |
| YT (Shorts) | Wed 3pm / Fri 5pm | Sun 11am | playbook §7 |
| TT | Mon 6am / Wed 7pm | Sat 8am / Sun 3pm | playbook §7 |

**注意**:playbook §7 若给出与上表不一致的时段,以 playbook 为准。上表仅为 fallback。

### rationale
- 必填,一句以上
- 关联 platform playbook §7 + angle 选择依据(如"周二 IG 用户 return-visit 高,首发放 confidence=high 的 problem-solution 类 reels")

### notes 全周综述(可选)
- 若首周节奏有特殊安排(如故意跳过某天等 sound decay 过峰),此处说明
- 若三平台节奏有交叉引流设计(如 TT 首发后 3 天 IG 转发),此处说明

## 边界情况

- **scope 只含 1 个平台**:首周 3-5 条集中该平台,间隔 1-2 天
- **scope 含 3 个平台但某平台 fit_score < 40**:该平台首周只放 1 条 low-cost 试水(如 IG 一条 carousel),不投主力
- **positioning.promo_goal 含明确 deadline**:节奏应前重后轻(前 3 天 3 条,后 4 天 1-2 条)
- **positioning.promo_goal == "brand-awareness"**:节奏平均(每 2 天一条,持续覆盖)

## 示例

```json
{
  "week_1": [
    {
      "day": "Mon",
      "date_offset_from_launch": 0,
      "platform": "tt",
      "post_ref": "tt-01",
      "recommended_time": "6am ET",
      "rationale": "TT fit_score 84 最高,launch day 首发放旗舰 hook(number-promise),周一早时段 US 用户通勤刷 TT 高活跃(§7)"
    },
    {
      "day": "Tue",
      "date_offset_from_launch": 1,
      "platform": "ig",
      "post_ref": "ig-01",
      "recommended_time": "9am ET",
      "rationale": "IG fit_score 72,周二 9am 是 IG feed 高 return-visit 时段(§7),放 problem-solution reels 承接 TT launch 的注意力"
    },
    {
      "day": "Wed",
      "date_offset_from_launch": 2,
      "platform": "tt",
      "post_ref": "tt-02",
      "recommended_time": "7pm ET",
      "rationale": "TT 第二击,选 sound-borrow 类 angle(decay 窗口内),对冲 launch 波动"
    },
    {
      "day": "Fri",
      "date_offset_from_launch": 4,
      "platform": "yt",
      "post_ref": "yt-01",
      "recommended_time": "5pm ET",
      "rationale": "YT fit_score 58,首周只投 1 条 shorts 试水,选 evergreen 教程型 angle 走 SEO 长尾"
    },
    {
      "day": "Sat",
      "date_offset_from_launch": 5,
      "platform": "tt",
      "post_ref": "tt-03",
      "recommended_time": "8am ET",
      "rationale": "TT 周末早高活跃,收尾放 founder-story 类 angle,建立品牌记忆"
    }
  ],
  "notes": "首周 3 TT + 1 IG + 1 YT,TT 集中在周一/三/六三个峰值;IG 补一条承接;YT 单条试水 SEO。若 launch 日 TT tt-01 表现好(24h 播放 > 10K),周四可加一条 IG tt-01 剪辑同款作为交叉引流。"
}
```
