# Stage 3 — Content Strategy(per platform)

## Purpose

为 scope 内**每一个**平台(不过滤)生成 `PlatformStrategy` 结构:3-5 个 angles + hashtag 5-slot mix + posting cadence + 可选 trend_borrow(仅 TT)。

## 输入

- `intent_profile`(Stage 1)
- `platform_fit`(Stage 2)
- 对每平台:`references/platform-playbooks/{platform}.md` §5 §6 §7 §9
- 仅 TT:`data/tiktok_trend_snapshot.json`(校验 `$last_refresh` 距今 < 4 周)

## 输出

对每个 platform ∈ platform_scope,产出一个 `PlatformStrategy`(见 `data/launch_pack_schema.json` definitions.PlatformStrategy)。

顶层数组结构:`strategies = { "ig": {...}, "yt": {...}, "tt": {...} }`(缺席的平台缺席)。

## LLM 动作(每平台 5 步)

### 1. Angle 生成(3-5 个)
- 数量:参考 `platform_fit.scores.{platform}.fit_score`:
  - fit_score ≥ 70:5 angles
  - 40 ≤ fit_score < 70:4 angles
  - fit_score < 40:3 angles
- 每 angle 必须包含 `intent_profile.value_prop.key_selling_point`(Stage 5 会 grep 自检)
- hook_pattern 从 playbook §5 六种中选,优先该平台 §5 标注 top-2 的 pattern
- post_type 从 `platform_fit.scores.{platform}.recommended_focus` 中选
- 5 个 angles 尽量分散 hook_pattern(不允许 5 个都用同一种)
- narrative_arc:三选一 `problem → solution → CTA` / `setup → payoff` / `before → after`

### 2. Hashtag 5-slot mix
读 playbook §6,按五槽结构填:
- **slot 1 (broad)**:1-2 条最大流量 hashtag(如 #saas / #startup)
- **slot 2 (mid-1)**:1-2 条中等热度、受众重叠强(如 #indiehackers)
- **slot 3 (mid-2)**:1-2 条另一维度中热度(如 #buildinpublic)
- **slot 4 (niche)**:1-2 条精准长尾(如 #vibecoding)
- **slot 5 (brand)**:1-2 条品牌/产品 hashtag(如 #atomsdev)

**TT 特有**:slot 2 / slot 3 优先从 `tiktok_trend_snapshot.json.trending_hashtags[]` 选(当期热点),但必须 confirm `atoms_relevance` 与本 intent 匹配。

### 3. Posting cadence
- `week_1_frequency`:参考 playbook §7 + `platform_fit` 排位:
  - 该平台 fit ranking 排第一:3-5 posts
  - 排第二:2-3 posts
  - 排第三:1-2 posts
- `best_time_slots`:从 playbook §7 抽 primary_market 时区的高活跃时段(3-5 条)
- `rationale_ref`:填 playbook §7 章节引用

### 4. Trend borrow(仅 TT)
- 若 `tiktok_trend_snapshot.$last_refresh` 距今 < 4 周,填 `trend_borrow`:
  - `trending_hashtags_slot_2`:从 snapshot 挑 3-5 条已进入 hashtag_mix 的
  - `trending_sounds_top_3`:从 `trending_sounds[]` 挑 top 3(必须 `license_type == "commercial-safe"` 且 `decay_estimate` 剩余 > 5 天)
  - `snapshot_date`:填 snapshot 的 `$last_refresh`
- 若 snapshot 过期或 platform ≠ tt:`trend_borrow: null`

### 5. _rationale
- 必填,3-5 句
- 说明:angle 数量选择依据、hook_pattern 分布、hashtag 5-slot 组合逻辑、cadence 依据、(TT)trend 数据是否使用
- 引用具体 playbook 章节(§5 / §6 / §7 / §9)

## 边界情况

| 场景 | 处理 |
|---|---|
| playbook §9 winning structures 案例数 < 3 | angles 降到 3 个,confidence 降到 medium;`_rationale` 标注 |
| TT trend snapshot 过期(> 4 周)| `trend_borrow: null`;Stage 5 warning |
| primary_market 非 US(如 UK/DE)| best_time_slots 时区跟随,若 playbook §7 未覆盖该市场,fallback US 时段并在 `_rationale` 标注 |
| intent_profile.audience.tone_preference == "professional" 且 platform == tt | 只允许 `hook_pattern ∈ {number-promise, before-after, hot-take}`,避开 pov / suspense(与调性冲突)|
| angle 生成 5 个但某个 hook_pattern 无 §9 案例支撑 | 该 angle `estimated_fit: low`,confidence 相应下调 |

## 并行策略(v0.1)

v0.1:三平台串行(实现简单)。v0.2 可评估并行(若延迟明显)。

## 输出交给下游

Stage 4 逐平台读 strategy,渲染 angles → captions / storyboards。
Stage 5 用 hashtag_mix 校验 caption.hashtags 展平完整性;用 trend_borrow.snapshot_date 触发时效 warning。
