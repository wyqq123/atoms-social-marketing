# GA4 Snapshot 采集契约

## 定位

- Atoms 平台 analytics **即 GA4 数据**:用户在 Atoms 构建的应用内集成 GA4(measurement id)后,上层可通过 GA4 Data API 拉取该应用的真实访问数据。
- 在 social-marketing skill 中,GA4 属于 **补充数据(MVP)**:未集成 GA4 → `ga4_snapshot: null`,pipeline 仅依赖 `positioning` + `builder_prompt`。
- **不做**:竞品 SEO 排名、行业 benchmark、设备拆分、页面路径明细等 MVP 范围外字段。

## 采集前置条件

1. 用户 app 已在 Atoms 内配置 GA4 `measurement_id`(格式 `G-XXXXXXXX`)
2. Atoms 平台持有或有权限调用 GA4 Data API 读取该 property 数据
3. 在 **调用 skill 前**由上层 Builder 同步拉取快照并写入 `inputs.ga4_snapshot`

Pipeline Stage 1–5 **不再**请求 GA4;只消费已注入的快照。

## 时间窗口

| 字段 / 指标 | 窗口 | 默认 | 说明 |
|---|---|---|---|
| `period` | `last_7d` / `last_30d` | **`last_7d`** | 与首周 Launch Pack 对齐;`post_launch` 重跑可选 `last_30d` |
| `summary.new_users` 等 | 同 `period` | last_7d | GA4 标准汇总 |
| `by_country` / `by_channel` / `by_event` | 同 `period` | last_7d | 与 summary 同窗口 |
| `summary.active_users_30m` | **滚动近 30 分钟** | 恒此窗口 | 反映「此刻是否有人正在访问」,与 `period` 无关 |

**拉取时机**:Intent Router 命中、用户点击「生成 Launch Pack」或「刷新数据并重跑」时,上层 **同步**拉取(目标 P95 < 3s);失败则 `ga4_snapshot: null`,不阻塞 skill 调起。

## GA4 指标与维度映射

### Summary(必填)

| 契约字段 | GA4 metric | 说明 |
|---|---|---|
| `new_users` | `newUsers` | 窗口内新用户 |
| `returning_users` | `totalUsers - newUsers`(或 `returningUsers` 若 API 直接提供) | 回访用户 |
| `active_users_30m` | `activeUsers` | date range = 近 30 分钟 |
| `sessions` | `sessions` | 浏览会话数 |
| `engaged_sessions` | `engagedSessions` | 活跃会话:>10s 或转化或 PV≥2 |

### by_country(可选,建议 top 10)

| 契约字段 | GA4 dimension / metric |
|---|---|
| `country` | `country` |
| `users` | `totalUsers` |
| `new_users` | `newUsers` |
| `sessions` | `sessions` |
| `engaged_sessions` | `engagedSessions` |

### by_channel(可选)

| 契约字段 | GA4 dimension / metric |
|---|---|
| `channel` | `sessionDefaultChannelGroup` |
| `users` / `new_users` / `sessions` / `engaged_sessions` | 同上 |

MVP 常见渠道值(与 GA4 默认分组一致):

- `Direct`
- `Cross-network`
- `Paid Search`
- `Paid Social`
- `Organic Search`
- `Organic Social`
- `Unassigned`
- (其余见 `data/ga4_snapshot_schema.json` enum)

### by_event(可选)

| 契约字段 | GA4 dimension / metric |
|---|---|
| `event_name` | `eventName` |
| `sessions` | `sessions`(按事件) |

MVP 事件白名单:

- `first_visit`
- `page_view`
- `scroll`
- `session_start`
- `user_engagement`

## 数据充足性判定

上层写入 `ga4_snapshot` 前校验;Pipeline Stage 1 二次校验:

| 条件 | 处理 |
|---|---|
| 未集成 GA4 / API 失败 | `ga4_snapshot: null` |
| `summary.sessions == 0` 且 `active_users_30m == 0` | 仍传入快照;Stage 1 产出 `traffic_level: zero`(有效信号) |
| 缺少 `summary` 或 `fetched_at` | 视为 null |
| `engaged_sessions > sessions` | 上层修正或丢弃快照 |

## Pipeline 消费摘要

Stage 1 从快照抽取 `intent_profile.ga4_signals`(见 `references/pipeline/stage-1-intent.md`):

- `traffic_level` — 由 sessions / active_users_30m 推断
- `dominant_channel` — by_channel 按 sessions 取 top 1
- `confirmed_geo` — by_country 按 sessions 取 top 3
- `engagement_rate` — engaged_sessions / sessions
- `new_user_share` — new_users / (new_users + returning_users)
- `has_recent_activity` — active_users_30m > 0

**不覆盖** `positioning.target_audience` / `target_market`;仅补充 `_rationale` 与 Stage 2 fit 微调。

## Schema 引用

- 完整 JSON Schema:`data/ga4_snapshot_schema.json`
- 嵌入 inputs:`data/inputs_schema.json` → `ga4_snapshot`

## 示例

```json
{
  "fetched_at": "2026-07-26T03:15:00Z",
  "measurement_id": "G-ABC123XY",
  "period": "last_7d",
  "summary": {
    "new_users": 128,
    "returning_users": 34,
    "active_users_30m": 5,
    "sessions": 210,
    "engaged_sessions": 89
  },
  "by_country": [
    { "country": "US", "users": 95, "new_users": 72, "sessions": 140, "engaged_sessions": 58 }
  ],
  "by_channel": [
    { "channel": "Direct", "users": 80, "new_users": 55, "sessions": 120, "engaged_sessions": 45 },
    { "channel": "Cross-network", "users": 40, "new_users": 38, "sessions": 55, "engaged_sessions": 28 },
    { "channel": "Unassigned", "users": 22, "new_users": 20, "sessions": 35, "engaged_sessions": 16 }
  ],
  "by_event": [
    { "event_name": "page_view", "sessions": 205 },
    { "event_name": "session_start", "sessions": 210 },
    { "event_name": "user_engagement", "sessions": 89 },
    { "event_name": "first_visit", "sessions": 128 },
    { "event_name": "scroll", "sessions": 62 }
  ]
}
```
