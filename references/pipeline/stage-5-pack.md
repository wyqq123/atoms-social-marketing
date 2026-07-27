# Stage 5 - Pack & Self-check

## Purpose

组装 Launch Pack 顶层 JSON,跑自检规则,输出 `checks` 与 `_pipeline_meta`。Stage 5 是真实性、概念边界和降级边界的最后闸门。

## 输入

- `intent_profile`, `app_icp_vector`, `demand_probe_pack`
- `platform_fit`, `strategies`, `deliverables`
- 原始 inputs
- `data/platform_registry.json`
- Playbook 版本信息(若平台有 playbook)

## 输出

符合 `data/launch_pack_schema.json` 的完整 Launch Pack JSON。

## LLM 动作

### 1. 组装 launch_brief

从 inputs + intent_profile 回填 app name、one liner、promo goal、target audience、key selling point、primary market。

### 2. 引入前置产物

整体拷贝 `platform_fit`、`strategies`、`deliverables`。不得在 Stage 5 重新计算 fit score。

### 3. 生成 schedule

- 覆盖 3-6 条。
- 高 fit 平台占主要权重。
- 低 fit 或 low-confidence 平台最多 1 条低风险试水。
- 单日单平台不重复。
- 若某平台 `probe_status != usable`,schedule rationale 不得写 why-now/current trend。

### 4. 自检规则

#### Blocker

| ID | 规则 | 触发条件 |
|---|---|---|
| B1 | key_selling_point 覆盖 | caption body 未覆盖核心卖点语义 |
| B2 | media prompt 非占位 | injectable_prompt 为 TBD/省略号/长度 < 20 |
| B3 | 视频 scene 空素材 | video_prompt/image_prompt/b_roll_hint 全空 |
| B4 | 全平台 fit 弱 | 所有发布平台 `fit_score < 40` |
| B5 | CTA 与目标冲突 | user-acquisition/conversion 目标下 CTA 无动作路径 |
| B6 | mix 展平不足 | caption hashtags/keywords 少于 5 或不能对应五槽 |
| B7 | schedule 覆盖不足 | week_1 少于 3 条 |
| B8 | media_generation_deferred | `_pipeline_meta.media_generation_deferred != true` |
| B9 | evidence 污染评分 | opportunity brief 含 `fit_verticals`、`fit_goal_types`、`relevance_to_atoms`、`fit_score`、`realtime_adjustment` |
| B10 | builder/end-user 混淆 | caption、strategy 或 app_icp_vector 把 builder 自我描述当作 built app 终端用户,且输入未明确说明 app 面向 builders |

#### Warning

| ID | 规则 | 触发条件 |
|---|---|---|
| W1 | 无动态证据 | 平台 `probe_status != usable`,但仍可用 stable strategy |
| W2 | why-now 越权 | `why_now` 非空但 refs < 2 或 status 非 usable |
| W3 | confidence cap | 无实时/授权证据时 confidence 高于 medium |
| W4 | registry/playbook 缺口 | 平台只有 registry 无 playbook,或 registry 缺关键字段 |
| W5 | 授权/cache-only 平台无 cache | Instagram/TikTok/LinkedIn/Rednote/Douyin 等只走 stable strategy |
| W6 | current-trend wording | deliverables 出现当前/近期/正在流行措辞但无 usable evidence |
| W7 | GA4 未提供 | `_pipeline_meta.ga4_used == false` |

#### Info

| ID | 规则 | 触发条件 |
|---|---|---|
| I1 | probe skipped | 缺凭证、no-network 或 cache miss |
| I2 | scope narrow | platform_scope 只有 1-2 个平台 |
| I3 | ranking gap | 首末 fit_score 差 > 40 |

### 5. 填 `_pipeline_meta`

- `playbook_versions`:按平台读取 playbook frontmatter;无 playbook 填 `registry-only`。
- `platform_registry_version`:读 `data/platform_registry.json.$schema_version`。
- `trend_snapshot_last_refresh`:若使用 manual/cache 样本则填日期,否则 null。
- `probe_meta`:记录 enabled、timeout、attempted platforms、usable brief count。
- `confidence_summary`:来自 Stage 2 `score_confidence`。
- `ga4_used`:输入和 intent_profile 均有可用 GA4 信号时 true。
- `media_generation_deferred`:恒 true。
- `injectable_prompts_count`:遍历 deliverables 统计。

## Wording Gate

Stage 5 必须全局扫描 `why_now`、strategy rationale、caption、storyboard、schedule rationale 和 `app_icp_vector`:

- 没有 usable evidence:只允许 evergreen strategy 表达。
- 有 usable evidence:可写“在本次轻量探针中观察到...”,不可写“平台整体正在流行...”。
- Web Search fallback:只可说“公开结果中存在相关入口”,不可说平台内热度。

## 输出交给上层

上层 Atoms builder 消费完整 Launch Pack,并根据 checks 决定是否提示用户补充素材、授权数据、刷新 cache 或调整平台范围。

