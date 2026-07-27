# Atoms Social Marketing Skill — 设计需求 PRD

> 版本:v0.1.0
> 首次落盘:2026-07-03
> 上游 Spec:`/Users/shendufuzhi2026/docs/superpowers/specs/2026-07-01-social-marketing-skill-design.md`
> Skill 落地:`/Users/shendufuzhi2026/.claude/skills/atoms-social-marketing/`

---

## 0. 文档定位

本 PRD 记录 `atoms-social-marketing` skill 的**完整设计策略**,覆盖:
1. Skill 目录结构与 progressive disclosure 分层
2. **Skill 运行完整流程**(从触发到产物交付的端到端时序)
3. **Skill 调起信号体系**(隐式关键词 / 显式 slash command / 生命周期 Chip 引导)
4. 5-Stage Pipeline 的输入输出、LLM 动作、上下游数据流
5. Template 体系(caption / storyboard / schedule)的作用与设计
6. Playbook 体系(IG/YT/TT 十节 schema)的作用与设计
7. 数据资产、媒体资产两级触发契约、自检与质量保障机制

读者对象:后续负责 skill 迭代、跨平台扩展(LinkedIn/X)、多语言支持、Session 记忆接入的产品与工程同学。

---

## 1. 产品目标与范围

### 1.1 目标

为 Atoms 平台上刚完成应用构建的 SMB 用户,**自动化生成一份可直接使用的首周社媒推广内容包**(Launch Pack),覆盖 Instagram / YouTube / TikTok 三大主流平台。

一次调用完成:
- 平台匹配度评估(打分 + 推荐)
- 每平台 3-5 个内容 angle
- 结构化 caption / video storyboard
- Hashtag 5-slot 组合
- 首周发布节奏表
- Media prompt 挂载点(供下游图片/视频工具消费)

### 1.2 明确不做的事(v0.1 边界)

| 范畴 | v0.1 是否覆盖 | 说明 |
|---|---|---|
| 长期(>1 周)运营节奏 | ❌ | 只出 week_1;month_1 由后续版本 |
| LinkedIn / X 平台 | ❌ | Playbook 未沉淀,输入校验直接拒绝 |
| 直接生成图片/视频 | ❌ | 见「媒体资产两级触发契约」 |
| 效果反馈闭环 | ❌ | v0.3+ 引入 Stage 6 |
| 多语言输出 | ❌ | 默认英文,v0.3 按 target_market 本地化 |
| 记忆/多轮迭代 | ❌ | v0.1 无状态,v0.2 引入 session_id |

### 1.3 v0.1 明确要做的事

- 输入契约、输出契约、pipeline stage 契约、playbook 契约全部落到 JSON Schema / Markdown 文件,可校验、可复现
- 5 阶段线性 pipeline,无状态,每次调用独立完成
- IG / YT / TT 三平台并列输出,不做过滤(即使 fit_score < 40 也留 1 条试水)
- 媒体资产**只挂载 prompt 字符串**,不触发生成
- 三级自检机制(Blocker / Warning / Info),blocker 出现时上层可决定是否阻塞

---

## 2. Skill 完整结构

### 2.1 目录树

```
atoms-social-marketing/
├── SKILL.md                             # 主入口(< 200 行,progressive disclosure 顶层)
├── data/                                # 契约与静态数据资产
│   ├── inputs_schema.json               # 输入契约(JSON Schema draft-07)
│   ├── ga4_snapshot_schema.json         # GA4 快照契约(MVP 补充数据)
│   ├── launch_pack_schema.json          # 输出契约
│   ├── tiktok_trend_snapshot.json       # TT Creative Center 快照(2-4 周刷新)
│   ├── tiktok_case_studies.json         # TT 案例
│   ├── ig_case_studies.json             # IG 案例
│   ├── youtube_case_studies.json        # YT 案例
│   └── {platform}_manual_supplements.md # 各平台人工补齐
├── references/
│   ├── pipeline/                        # 5 个 stage 的详细工作流
│   │   ├── stage-1-intent.md
│   │   ├── stage-2-fit.md
│   │   ├── stage-3-strategy.md
│   │   ├── stage-4-render.md
│   │   └── stage-5-pack.md
│   ├── templates/                       # 产物骨架模板
│   │   ├── caption.md
│   │   ├── storyboard.md
│   │   └── schedule.md
│   └── platform-playbooks/              # 平台知识
│       ├── _schema.md                   # 10-section 标准结构
│       ├── instagram.md
│       ├── youtube.md
│       └── tiktok.md
└── scripts/                             # 数据采集脚本(不在 pipeline 内)
    ├── oembed_fetch.py
    ├── youtube_data_api.py
    └── tiktok_creative_center_refresh.md
```

### 2.2 Progressive Disclosure 分层设计

严格遵守「顶层薄、按需下钻」原则,让 LLM 在最小上下文里做出正确路由:

**Layer 0 — SKILL.md(顶层,< 200 行)**
- Skill 调起信号要点(隐式关键词组合 / 显式 `/social-marketing-skills`;详见 PRD §4.3)
- 何时启用 / 不启用(明确拒绝 LinkedIn / X)
- Pipeline 5 阶段流程图与 stage 索引表
- 输入契约要点(必填 3 项 + 可选)
- 输出契约顶层字段
- **媒体资产两级触发契约**(核心设计决策)
- 各类文件的索引表(template / playbook / data / scripts)
- 扩展点与版本

**Layer 1 — Stage 文档(references/pipeline/stage-N-*.md,50-150 行/份)**
- 单一 stage 的 purpose / 输入 / 输出 / LLM 4-6 步动作 / 边界情况 / 上下游数据流
- 只在执行到该 stage 时加载

**Layer 2 — Template 与 Playbook**
- 只在 Stage 3/4/5 需要具体填充规则时加载
- Playbook 十节结构,stage 精确按需读取对应 section(不读全文)

**Layer 3 — 数据资产**
- JSON Schema:仅在校验时加载
- Case studies / Trend snapshot:仅在 Stage 3 生成 angles / hashtag 时加载

### 2.3 目录职责矩阵

| 目录 | 职责 | 是否契约 | 更新频率 |
|---|---|---|---|
| `SKILL.md` | 路由 + 契约声明 | ✅ | 版本迭代时 |
| `data/*_schema.json` | I/O 契约 | ✅ 强 | 版本迭代时 |
| `data/tiktok_trend_snapshot.json` | 时效数据 | ❌ | 2-4 周 |
| `data/*_case_studies.json` | 参考语料 | ❌ | 按需追加 |
| `references/pipeline/` | 工作流规范 | ✅ 中 | 迭代 |
| `references/templates/` | 骨架规范 | ✅ 中 | 迭代 |
| `references/platform-playbooks/` | 平台知识 | ✅ 中 | 版本迭代 + 新增平台 |
| `scripts/` | 数据采集 | ❌ | 按需 |

---

## 3. 输入 / 输出契约

### 3.1 输入契约(`data/inputs_schema.json`)

**必填字段**:

| 字段 | 类型 | 约束 | 用途 |
|---|---|---|---|
| `app_context.name` | string | 非空 | 应用名 |
| `app_context.description` | string | 非空 | 应用描述 |
| `app_context.category` | string | 非空 | 应用类别原文 |
| `builder_prompt` | string | ≥ 50 char | builder 阶段用户对应用的完整表达,Stage 1 抽隐含线索 |
| `positioning.promo_goal` | string | 非空 | 推广目标(冷启动/UA/品牌/转化) |
| `positioning.target_audience` | string | 非空 | 目标受众描述 |
| `positioning.key_selling_point` | string | 非空 | 核心卖点 |

**可选字段**:

| 字段 | 缺省行为 |
|---|---|
| `ga4_snapshot` | 若 null,pipeline 只用 positioning + builder_prompt;`_pipeline_meta.ga4_used = false`。见 §3.3 |
| `platform_scope` | 默认 `["ig", "yt", "tt"]`;不允许非该三元素 |
| `positioning.target_market` | 默认 `["US"]` |

### 3.3 GA4 应用访问快照(MVP 补充数据)

**定位**:Atoms 平台 analytics 即 GA4。仅当用户在 Atoms 应用内集成 GA4(`measurement_id`)且上层能经 GA4 Data API 拉取数据时,才注入 `ga4_snapshot`。**未集成 GA4 时为 null**,不阻塞 Launch Pack 生成。

**采集范围**(与 GA4 口径对齐,详见 `data/ga4_snapshot_schema.json` / `references/ga4-snapshot-contract.md`):

| 层级 | 字段 | GA4 来源 |
|---|---|---|
| 汇总 | new_users / returning_users / sessions / engaged_sessions | 标准 metrics |
| 实时 | active_users_30m | activeUsers,滚动近 **30 分钟** |
| 维度 | by_country[] | country × users/new_users/sessions/engaged_sessions |
| 维度 | by_channel[] | sessionDefaultChannelGroup(Direct / Cross-network / Paid Search / Unassigned 等) |
| 维度 | by_event[] | first_visit / page_view / scroll / session_start / user_engagement 的 sessions |

**时间窗口**:

| 用途 | 默认 | 说明 |
|---|---|---|
| `period` 汇总维度 | **`last_7d`** | 与首周 Launch Pack 对齐 |
| 可选扩展 | `last_30d` | post_launch 重跑或用户显式选择 |
| `active_users_30m` | 恒为近 30min | 与 `period` 无关 |

**拉取时机**:上层在 Intent Router 命中后、调用 skill 前 **同步**拉取;Pipeline 内只读快照,不请求 GA4。

**Stage 1 产出** `ga4_signals`:traffic_level / dominant_channel / confirmed_geo / engagement_rate / new_user_share / has_recent_activity → Stage 2 fit 微调。

### 3.2 输出契约(`data/launch_pack_schema.json`)

顶层结构(Launch Pack):

```
{
  "$schema_version": "0.1.0",
  "generated_at": "ISO 8601",
  "launch_brief": {},          // 精简摘要,展示层用
  "platform_fit": {},          // Stage 2 产物
  "strategies": {              // Stage 3 产物(每平台)
    "ig": PlatformStrategy,
    "yt": PlatformStrategy,
    "tt": PlatformStrategy
  },
  "deliverables": {            // Stage 4 产物(每平台)
    "ig": { posts, storyboards, ab_variants },
    "yt": { ... },
    "tt": { ... }
  },
  "schedule": { "week_1": [...], "notes": "" },
  "checks": { blocker, warning, info },
  "_pipeline_meta": {
    "playbook_versions": {},
    "trend_snapshot_last_refresh": "date | null",
    "confidence_summary": {},
    "ga4_used": bool,
    "media_generation_deferred": true,   // 恒 true,硬编码
    "injectable_prompts_count": { images, videos }
  }
}
```

关键 definitions:
- **PlatformStrategy**:angles[3-5] + hashtag_mix(5 slots) + posting_cadence + optional trend_borrow
- **Caption**:angle_id / hook / body / cta / hashtags[≥5] / confidence / media_prompts / _rationale
- **Storyboard**:total_duration_s + sound_ref + scenes[] + caption + _rationale
- **MediaPromptsCaption** / **MediaPromptsScene**:见「§ 9 媒体资产两级触发契约」

---

## 4. Skill 运行完整流程

本章描述 skill **从被触发到产物交付**的端到端时序,是理解 § 5 Pipeline 各 stage 内部实现的**上位视图**。

### 4.1 完整时序图

```
┌────────────────────── 上层 Atoms Builder ──────────────────────┐
│                                                                 │
│  用户在 Builder 完成应用构建                                    │
│      │                                                          │
│      ▼                                                          │
│  ①  Skill 调起信号检测(§4.3)                                   │
│      ├─ 隐式:关键词强信号组合命中                               │
│      ├─ 显式:用户输入 /social-marketing-skills                  │
│      ├─ Chip:用户点击生命周期 Chip 注入预设 prompt 后发送       │
│      └─ 结构化:Marketing tab「生成 Launch Pack」按钮            │
│      ※ Chip 本身不直接调 skill,仅注入预设 prompt               │
│      │                                                          │
│      ▼                                                          │
│  ②  上层收集 positioning 三要素                                 │
│      (promo_goal / target_audience / key_selling_point)         │
│      │                                                          │
│      ▼                                                          │
│  ③  上层组装 inputs 对象                                        │
│      { app_context, builder_prompt, positioning,                │
│        ga4_snapshot?, platform_scope? }                         │
│      │                                                          │
│      ▼                                                          │
│  ④  上层校验 inputs against inputs_schema.json                 │
│      ├─ 失败:返回错误给用户,不调 skill                        │
│      └─ 通过:调用 skill                                        │
│                                                                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌────────── atoms-social-marketing skill(无状态) ─────────────┐
│                                                                │
│  ⑤  SKILL.md 路由                                              │
│      ├─ 何时启用检查(是否已 builder / 三要素齐)              │
│      ├─ platform_scope 白名单(拒绝 LinkedIn / X)             │
│      └─ 加载 pipeline stage 索引                               │
│      │                                                         │
│      ▼                                                         │
│  ⑥  Stage 1 Intent & Positioning                              │
│      · 读:inputs(全量)                                      │
│      · 动作:抽 builder_prompt 隐含线索 → 与 positioning 对齐 │
│              → GA4 校准 → category 归一                        │
│      · 出:intent_profile                                      │
│      │                                                         │
│      ▼                                                         │
│  ⑦  Stage 2 Platform Fit                                      │
│      · 读:intent_profile + platform_scope                     │
│           + playbook §2 §4(每个 scope 平台)                  │
│      · 动作:4 维加权算 fit_score → ranking → 强弱项 →         │
│              recommended_focus                                 │
│      · 出:platform_fit                                        │
│      │                                                         │
│      ▼                                                         │
│  ⑧  Stage 3 Content Strategy(平台循环 · v0.1 串行)           │
│      For each platform ∈ platform_scope:                       │
│        · 读:intent_profile + platform_fit                     │
│             + playbook §5 §6 §7 §9                             │
│             + (仅 TT)tiktok_trend_snapshot.json               │
│        · 动作:                                                │
│            a. Angle 生成(3-5,按 fit_score)                  │
│            b. Hashtag 5-slot mix                              │
│            c. Posting cadence                                 │
│            d. (仅 TT)trend_borrow 校验时效                    │
│            e. _rationale                                      │
│        · 出:strategies[platform]                              │
│      │                                                         │
│      ▼                                                         │
│  ⑨  Stage 4 Deliverable Rendering(平台循环)                  │
│      For each platform:                                        │
│        Step a 骨架生成:                                       │
│          · 读:strategies[platform]                            │
│               + templates/caption.md                          │
│               + templates/storyboard.md                       │
│          · 每 angle 产出 caption(视频类同时产 storyboard)    │
│        Step b 挂载 media prompts:                             │
│          · 遍历 caption.media_prompts 与 scene.media_prompts │
│          · 填 injectable_prompt(四要素)+ trigger=on-demand   │
│          · **不触发任何图片/视频生成**                        │
│        Step c A/B 变体:                                       │
│          · 仅对 confidence=high posts 生成 1 个 variant       │
│        · 出:deliverables[platform]                            │
│      │                                                         │
│      ▼                                                         │
│  ⑩  Stage 5 Pack & Self-check                                 │
│      · 读:前置全部产物 + 原始 inputs + playbook frontmatter  │
│      · 动作:                                                  │
│         1. 组装 launch_brief                                  │
│         2. 引入 platform_fit / strategies / deliverables      │
│         3. 生成 schedule.week_1(读 templates/schedule.md)    │
│         4. 跑三级自检(Blocker / Warning / Info)             │
│         5. 填 _pipeline_meta(硬编码 media_generation_        │
│            deferred=true)                                     │
│         6. 填 generated_at(ISO 8601)                         │
│      · 校验:与 launch_pack_schema.json 匹配                   │
│      · 出:Launch Pack JSON                                    │
│                                                                │
└──────────────────────────┬─────────────────────────────────────┘
                           │
                           ▼
┌────────────────────── 上层 Atoms Builder ──────────────────────┐
│                                                                 │
│  ⑪  上层消费 Launch Pack                                        │
│      ├─ checks.blocker 展示(红色阻断卡片)                     │
│      ├─ checks.warning 展示(黄色提示)                         │
│      ├─ launch_brief → 顶部摘要卡                              │
│      ├─ platform_fit → 平台排位与打分                          │
│      ├─ strategies → 每平台策略页(angles / hashtag / cadence) │
│      ├─ deliverables → master-detail 浏览 posts / storyboards  │
│      └─ schedule → 时间轴视图                                  │
│      │                                                          │
│      ▼                                                          │
│  ⑫  用户按需触发 Media 生成(两级触发第二级)                  │
│      用户点击某 media_prompts 的「生成图片/视频」按钮:         │
│        ├─ 上层取 injectable_prompt 字符串                       │
│        ├─ 注入下游图片/视频工具会话                             │
│        ├─ 下游工具生成素材                                      │
│        └─ 上层管理生成状态与素材落地(skill 不介入)            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 执行属性总览

| 属性 | 值 | 说明 |
|---|---|---|
| 调起机制 | **Intent Router** | 隐式关键词组合 / 显式 slash / Chip 预设 prompt / 结构化表单;详见 §4.3 |
| 状态性 | **无状态** | 每次调用独立完成,不持久化中间产物;v0.2 引入 session_id |
| 阶段拓扑 | **线性 5 段** | 单向依赖,无 DAG / 无回退 |
| 平台处理 | **循环内串行** | Stage 3/4 for-each platform;v0.2 可评估并行 |
| Media 生成 | **两级触发** | Skill 只挂 prompt(第一级);上层用户点击触发生成(第二级) |
| 失败模型 | **产物先出,问题后报** | Blocker 触发仍完整出 Launch Pack,由上层决定是否阻塞发布 |
| 数据源 | **只读本地资产** | Playbook / trend_snapshot / case_studies 均 `data/` 落盘,不实时抓取 |
| I/O 契约 | **JSON Schema draft-07 双端校验** | 入口校验 inputs_schema、Stage 5 结束校验 launch_pack_schema |

### 4.3 Skill 调起信号体系

上层 Atoms Builder 在调用 skill 之前,先运行 **Intent Router** 检测用户输入是否命中调起信号。**命中以下任意一类信号,即进入 skill 调起流程**(仍须通过 §4.4 前置 gate 与 `inputs_schema.json` 校验)。

| 信号类型 | 机制 | 是否直接调 skill |
|---|---|---|
| **隐式信号** | 对用户 prompt 做关键词模块识别 + 强信号组合判定 | ✅ 组合命中即调起 |
| **显式信号** | 用户输入 slash command `/social-marketing-skills` | ✅ 无条件调起(仍过 gate) |
| **生命周期 Chip** | 对话框上方展示 Chip,点击注入预设 prompt | ❌ Chip 本身不调;**用户发送该预设 prompt 后**视同隐式/显式信号调起 |
| **结构化入口** | Marketing tab「生成 Launch Pack」按钮 | ✅ 表单提交即调起 |

**Skill 侧无差异**:所有入口最终都产生同一份符合 `inputs_schema.json` 的 inputs 对象;skill 不感知触发路径,只消费标准化 inputs。

**Router 执行顺序**(上层实现):

```
用户输入 / Chip 注入
  → ① 分流检测:仅命中「营销工具词」且无自有应用/App 推广词? → 路由至营销工具模板,不调本 skill
  → ② 显式信号:/social-marketing-skills → 调起
  → ③ 隐式信号:强信号组合命中 → 调起
  → ④ Chip 预设 prompt:发送后重新走 ②③
  → ⑤ 未命中 → 不调起,走通用 builder 对话
  → (命中后) §4.4 前置 gate → inputs_schema 校验 → 调用 skill
```

#### 4.3.1 隐式信号 — 关键词识别

隐式调起基于 **6 个信号模块** 对用户 prompt(及可选 builder 上下文)做关键词匹配。匹配不区分大小写;中英文同模块内 **OR** 关系;跨模块按下方组合规则判定。

##### 信号模块词表

| 模块 | 目的 | 典型信号(命中词,非穷举) |
|---|---|---|
| **平台词** | 识别社媒渠道与分发平台 | Instagram, IG, TikTok, TT, YouTube, YT, Facebook, LinkedIn, X, Twitter, Reddit, 小红书, 抖音, Pinterest, WhatsApp, Threads |
| **内容形式词** | 识别内容生产需求 | caption, headline, title, hashtag, video script, short video, carousel, thread, content calendar, 文案, 标题, 脚本, 封面, 图文, 选题, 口播 |
| **增长动作词** | 识别推广、获客、增长意图 | cold start, no users, get users, find users, get traffic, user acquisition, GTM, growth strategy, launch strategy, 推广, 引流, 获客, 冷启动, 投放, 找用户 |
| **自有应用词** | 判断是否可能是 builder 自己的应用 | my app, our app, my website, my product, my SaaS, I built, I created, 我的应用, 我的产品, 我的网站, 我的工具, 我开发的 |
| **App 推广词** | 识别直接推广意图 | promote my app, launch my app, market my product, help me launch, 推广我的, 宣传我的, 帮我推广 |
| **营销工具词** | 识别「构建营销工具」场景(分流用) | marketing platform, social media management, campaign dashboard, ad manager, SEO agent, content agent, 营销平台, 营销工具, 社媒工具, 排程工具, 发帖工具, 达人插件 |

##### 强信号组合命中规则

满足以下 **任意一条**,即判定隐式调起:

| 规则 ID | 条件 | 说明 |
|---|---|---|
| **I1** | `App 推广词` 命中 **≥ 1** | 直接推广意图,单独即可调起 |
| **I2** | (`增长动作词` **或** `自有应用词`) **且** (`内容形式词` **或** `平台词`) 各命中 **≥ 1** | 核心组合:意图/对象 + 内容/渠道 |
| **I3** | `平台词` **且** `内容形式词` 各命中 **≥ 1**,且 builder 上下文存在已构建 app(`app_context` 可用) | 无显式推广词但上下文可推断为 own_built_app |
| **I4** | 预设 prompt 来自生命周期 Chip(§4.3.3),且 Chip 已展示 | 视同 I1 或 I2(预设 prompt 内已编码组合) |

**不命中示例**(不调起本 skill):

- 仅 `平台词`:"Instagram 最近算法变了?" → 资讯/策略咨询,非内容包
- 仅 `内容形式词`:"帮我写一条 caption" → 单条 copy,非 Launch Pack(可走路由至轻量 copy 能力)
- 仅 `增长动作词`:"冷启动怎么做?" → 增长诊断,非内容包
- 仅 `营销工具词`:"帮我做一个社媒排程工具" → 分流至营销工具模板

##### 平台词 → `platform_scope` 映射

隐式命中后,上层从平台词推断 `platform_scope`(缺省 `["ig","yt","tt"]`):

| 用户提及 | 映射 |
|---|---|
| Instagram / IG | `ig` |
| TikTok / TT / 抖音 | `tt` |
| YouTube / YT | `yt` |
| LinkedIn / X / Facebook / 小红书 / Reddit / Pinterest / WhatsApp / Threads | **v0.1 不参与 scope**;Router 仍可调起 skill,但上层提示「当前仅支持 IG/YT/TT,将按此三平台生成」;用户若仅提 unsupported 平台且无 ig/yt/tt → 仍生成三平台默认 pack |

#### 4.3.2 显式信号 — Slash Command

| 字段 | 值 |
|---|---|
| **Command** | `/social-marketing-skills` |
| **行为** | 无条件进入 skill 调起流程(跳过隐式组合判定) |
| **仍须通过** | §4.4 前置 gate、`inputs_schema.json` 校验 |
| **platform_scope** | 若 slash 后附带平台参数(如 `/social-marketing-skills ig tt`)则解析;否则默认三平台 |
| **与 Chip 关系** | Chip 注入的预设 prompt **可**在开头携带 `/social-marketing-skills`,发送后走显式路径 |

#### 4.3.3 生命周期 Chip 引导(非直接调起)

生命周期信号 **不直接调用 skill**。上层根据 app 生命周期阶段,在 **Builder 对话框输入框上方** 展示社媒相关 Chip 组件;用户 **点击 Chip** 将预设 prompt **注入对话框**(不自动发送);用户确认发送后,预设 prompt 按 §4.3.1 / §4.3.2 触发 skill。

##### Chip 展示条件

| 生命周期阶段 | 展示 Chip | 依据 |
|---|---|---|
| `pre_launch` | ✅ | 强需求率 65.6%,发布前需首发包 |
| `launch` | ✅ | 强需求率 58.7%,上线窗口 |
| `post_launch` | ✅ | 强需求率 88.8%,「发布了没人用」高痛点 |
| `building`(后期,已有可演示 app) | ✅ 可选 | 强需求率 41.0%,可展示但优先级低于前三 |
| `idea` | ❌ | 强需求率 1.9%,缺 app 上下文,不调起 |

生命周期判定来源:`app_context.created_at` / `published_at` / builder 阶段状态机;具体规则由上层产品定义,skill 不感知 Chip 展示逻辑。

##### Chip 组件与预设 Prompt

| Chip 标签 | 生命周期 | 注入的预设 prompt(用户可编辑后发送) |
|---|---|---|
| **Prepare launch pack** | pre_launch | `/social-marketing-skills Help me prepare a launch-week social media pack for my app on Instagram, TikTok, and YouTube — captions, hashtags, video scripts, and a week-1 posting schedule.` |
| **Launch week content** | launch | `/social-marketing-skills My app is launching now. Generate a week-1 social launch pack for Instagram, TikTok, and YouTube with captions, storyboards, and posting schedule.` |
| **Cold-start content** | post_launch | `/social-marketing-skills My app launched but has no users yet. Help me create a cold-start social content pack for Instagram, TikTok, and YouTube to get my first users.` |
| **首周推广包** | pre_launch / launch | `/social-marketing-skills 帮我为我的应用生成 Instagram、TikTok、YouTube 三平台首周社媒推广内容包,包括文案、标签、视频脚本和发布节奏。` |
| **冷启动内容** | post_launch | `/social-marketing-skills 我的应用已经上线但没人用,帮我做 Instagram、TikTok、YouTube 的冷启动社媒内容包。` |

**Chip 交互契约**:

1. 点击 Chip → 预设 prompt 写入对话框输入框(不自动 send)
2. 用户可编辑 prompt 后发送
3. 发送后 Router 检测:预设 prompt 含 `/social-marketing-skills` → 显式调起;否则按隐式 I2/I4 判定
4. Chip 展示与 skill 调用 **解耦**:未点击 Chip 的用户仍可通过自然语言隐式/显式调起

#### 4.3.4 结构化产品入口

除信号 Router 外,保留结构化入口作为 **确定性调起路径**:

| 入口 | 场景 | 用户交互 | inputs 组装方式 |
|---|---|---|---|
| **Agent 对话** | 隐式/显式/Chip 预设 prompt 发送 | 自然语言或 slash | 上层 agent 从对话与 app 状态抽取,positioning 缺项时反问补齐 |
| **Marketing tab 表单** | 用户点「生成 Launch Pack」 | 结构化表单 | 表单字段直接映射 inputs;positioning 三要素为必填 |

#### 4.3.5 分流信号 — 营销工具词

| 条件 | 路由 |
|---|---|
| 命中 `营销工具词` **且** 未命中 `自有应用词` / `App 推广词` | **不调本 skill** → 路由至「营销工具模板 / marketing_tool_builder」能力 |
| 同时命中 `营销工具词` + `自有应用词` | 优先 `自有应用词` + 组合规则 → **可调本 skill**(用户可能在为自己的 app 找营销工具,需上层澄清或默认 app 推广) |

### 4.4 输入准备与前置校验(上层责任)

在调用 skill 之前,上层必须完成:

0. **Intent Router(§4.3)**:
   - 检测隐式强信号组合 / 显式 `/social-marketing-skills` / Chip 预设 prompt / Marketing tab 提交
   - 营销工具词分流:未命中自有应用/App 推广词 → 不调本 skill
   - 未命中任何调起信号 → 不进入后续步骤
1. **触发条件检查**:
   - 用户已在 Atoms builder 完成应用构建(app_context 三字段已存在)
   - builder_prompt 已保存(> 50 char)
2. **Positioning 三要素收集**:
   - `promo_goal` / `target_audience` / `key_selling_point` 缺任一 → 反问用户补齐,不调 skill
3. **可选字段拉取**:
   - `ga4_snapshot`:若用户 app 已集成 GA4(measurement id),上层调 skill 前经 GA4 Data API 拉取快照(默认 `period=last_7d`);未集成则不填
   - `platform_scope`:Router 从平台词推断(§4.3.1);表单勾选或对话中显式指定;缺省 `["ig", "yt", "tt"]`
4. **Schema 前置校验**:
   - 上层用 `inputs_schema.json` 校验 inputs;失败直接返错,不进入 skill
5. **平台 scope 约束(v0.1)**:
   - `platform_scope` 枚举仅允许 `ig` / `yt` / `tt`(见 `inputs_schema.json`)
   - 用户 prompt 仅提及 LinkedIn / X / 小红书等 unsupported 平台词 → Router 仍可调起 skill,`platform_scope` 默认 `["ig","yt","tt"]`,上层提示 v0.1 覆盖范围
   - 用户 **显式要求** 仅生成 LinkedIn/X 内容且拒绝 IG/YT/TT → 上层告知 v0.1 不支持并引导三平台或等待 v0.2

### 4.5 阶段间数据流(具体字段级)

以下示意数据在 stage 间的传递路径,便于理解**哪些字段由哪个 stage 首次生成、哪些字段被下游消费**:

```
inputs
  ├─ app_context ────────────┐
  ├─ builder_prompt ─────────┤
  ├─ positioning ────────────┼─→ Stage 1 ─→ intent_profile
  ├─ ga4_snapshot ───────────┤              ├─ app_summary
  └─ platform_scope ─────────┼─→ Stage 2   ├─ promo_intent
                             │              ├─ audience
                             │              ├─ value_prop
                             │              └─ ga4_signals
                             │                      │
                             │        ┌─────────────┘
                             │        ▼
                             │    Stage 2 ─→ platform_fit
                             │              ├─ ranking
                             │              └─ scores{ig,yt,tt}
                             │                      │
                             ▼                      ▼
                          Stage 3(per platform)
                            reads: intent_profile + platform_fit
                                  + playbook §5/6/7/9
                                  + tiktok_trend_snapshot(TT only)
                            ─→ strategies{ig,yt,tt}
                                  ├─ angles[3-5]
                                  ├─ hashtag_mix.slots{1..5}
                                  ├─ posting_cadence
                                  └─ trend_borrow(TT only)
                                          │
                                          ▼
                          Stage 4(per platform)
                            reads: intent_profile + strategies
                                  + templates/caption.md
                                  + templates/storyboard.md
                            ─→ deliverables{ig,yt,tt}
                                  ├─ posts[Caption]
                                  ├─ storyboards[Storyboard]
                                  └─ ab_variants[Caption]
                                          │
                                          ▼
                          Stage 5
                            reads: 前置全部 + inputs + playbook frontmatter
                                  + templates/schedule.md
                            ─→ Launch Pack
                                  ├─ launch_brief
                                  ├─ platform_fit(拷贝)
                                  ├─ strategies(拷贝)
                                  ├─ deliverables(拷贝)
                                  ├─ schedule.week_1
                                  ├─ checks{blocker,warning,info}
                                  └─ _pipeline_meta
```

**关键传递路径**:
- `positioning.key_selling_point` → `intent_profile.value_prop.key_selling_point` → 每个 caption.body(Blocker B1 grep 自检)
- `platform_fit.scores.{platform}.recommended_focus` → `strategies.{platform}.angles[].post_type`
- `strategies.{platform}.hashtag_mix.slots` 5 槽展平 → `caption.hashtags`(Blocker B6 校验)
- `strategies.{platform}.trend_borrow.sounds` → `storyboard.sound_ref`(仅 TT)
- 每个 stage 独立产出 `_rationale`,不清洗、原样透传到 Launch Pack

### 4.6 失败路径与降级策略

Skill 采用**产物先出、问题后报**原则 — 即使触发 blocker,Launch Pack 仍完整输出,由上层决定阻塞或放行。

| 失败类型 | 发生 stage | 处理方式 | 用户可见 |
|---|---|---|---|
| Inputs schema 校验失败 | 入口前 | 上层直接返错,不进入 skill | 表单/对话反问补齐 |
| 三平台 fit 全 < 40 | Stage 2 | 正常输出 ranking + Blocker B4 | 提示"平台匹配度都不高,建议重审 positioning" |
| Playbook `_schema_version` 缺失 | Stage 2 | `playbook_versions.{platform}=unknown` + W3 | 灰色提示,不阻断 |
| TT trend snapshot 过期(≥ 4 周) | Stage 3 | `trend_borrow=null` + W2 提示上游数据未刷新 | 黄色提示,建议刷新数据 |
| 某 caption.body 漏 key_selling_point | Stage 4 输出 → Stage 5 grep | Blocker B1 | 红色阻断,提示重跑或人工修改 |
| Injectable_prompt 占位/过短 | Stage 4 输出 → Stage 5 校验 | Blocker B2 | 红色阻断 |
| 视频类 scene 三字段全 null | Stage 4 输出 → Stage 5 校验 | Blocker B3 | 红色阻断 |
| CTA 与 promo_intent 不一致 | Stage 5 | Blocker B5 | 红色阻断 |
| Hashtag 展平不完整 | Stage 5 | Blocker B6 | 红色阻断 |
| Schedule < 3 条 | Stage 5 | Blocker B7 | 红色阻断 |
| `media_generation_deferred != true` | Stage 5 | Blocker B8(设计契约违反) | 红色阻断,不允许发布 |

**降级路径**:
- Stage 3 playbook §9 案例 < 3 → angles 降到 3,confidence 降到 medium
- Stage 3 primary_market 非 US 且 playbook §7 未覆盖 → fallback US 时段
- Stage 4 storyboard scenes 时长和 ≠ total_duration_s → 自动调整最后一 scene
- Stage 4 视频类 post_type 超平台上限 → 强制截到上限

### 4.7 产物交付与上层消费流程

Skill 输出 Launch Pack JSON 后,上层 Atoms builder 负责:

1. **Checks 优先展示**:
   - `checks.blocker` 非空 → 顶部红色阻断卡,不允许发布,提示重跑或修改
   - `checks.warning` → 各页面对应位置黄色提示
   - `checks.info` → 可折叠灰色提示

2. **主体展示**(master-detail 布局):
   - Master 侧:平台 tab(IG/YT/TT)+ 日期轴切换
   - Detail 侧:选中 post 的 caption / storyboard 全文 + media prompts

3. **Media 两级触发第二级**:
   - 每个 `media_prompts.*` 位置渲染「生成图片/视频」按钮
   - 用户点击:上层取 `injectable_prompt` 注入下游图片/视频工具会话
   - 下游生成成功:上层管理素材落地(缓存、缩略图、下载);skill 不介入
   - 下游生成失败:上层负责重试;不回写 Launch Pack

4. **Schedule 时间轴**:
   - 按 `schedule.week_1[].date_offset_from_launch` 排序展示
   - 每条挂 `post_ref` → 跳转到对应 post detail

5. **重跑入口**:
   - 用户修改 positioning、补齐 GA4、切换 platform_scope → 上层重新组装 inputs 调用 skill;pipeline 完全无状态重跑,不复用旧产物

### 4.8 无状态设计的影响

v0.1 skill 完全无状态,带来以下取舍:

**优势**:
- 实现简单,不依赖外部存储
- 每次调用独立可复现,便于测试与回归
- 无并发锁问题
- 无历史数据漂移风险

**代价**:
- 用户重跑必须重传完整 inputs(上层责任)
- 无法做二次生成的 diff(如"只改 TT 的 3 个 angles")
- 无法学习用户偏好(哪个 hook_pattern 上次被采纳)

**v0.2 演进方向**:引入 `session_id` 作为可选 inputs 字段,支持二次生成时 skill 侧读历史产物做 diff 输出。

---

## 5. Pipeline 设计

### 4.1 总览

5 阶段线性 pipeline,无状态,每次调用独立完成:

```
inputs
   ↓
Stage 1  Intent & Positioning   →  intent_profile
   ↓
Stage 2  Platform Fit           →  platform_fit
   ↓
Stage 3  Content Strategy       →  strategies[per platform]
   ↓
Stage 4  Deliverable Rendering  →  deliverables[per platform]
   ↓
Stage 5  Pack & Self-check      →  Launch Pack JSON
```

**为什么线性而非 DAG**:
- 每个 stage 有清晰单向依赖
- 无状态,便于测试与复现
- v0.1 完全 LLM in-context 执行,不引入编排引擎

**并行策略**:
- v0.1:三平台在 Stage 3/4 内串行处理(实现简单,总时长可接受)
- v0.2:评估是否并行(如延迟成为瓶颈)

### 4.2 Stage 1 — Intent & Positioning

**目的**:把 4 类原始输入(app_context / builder_prompt / positioning / ga4_snapshot)归一化为下游可直接消费的 `intent_profile`。

**输入**:符合 `inputs_schema.json` 的完整对象。

**输出结构** `intent_profile`:
- `app_summary`:name / one_liner(≤100 char) / category_normalized(枚举归一) / market_primary + market_secondary
- `promo_intent`:goal_type(cold-start / user-acquisition / brand-awareness / conversion) / goal_metric_hint / time_horizon
- `audience`:primary_persona / pain_points / tone_preference(casual / professional / build-in-public)
- `value_prop`:key_selling_point(原文承接) / supporting_points / differentiators
- `ga4_signals`:null 或 { traffic_level, dominant_channel, confirmed_geo, engagement_rate, new_user_share, has_recent_activity }
- `_rationale`

**LLM 动作(4 步)**:
1. **抽 builder_prompt 隐含线索**:tone、隐含受众、竞品/参考物、非功能诉求
2. **与 positioning 对齐**:key_selling_point 与 target_audience 原文灌入;promo_goal 分类到 4 种 goal_type;冲突时以 positioning 为准
3. **GA4 校准**(若 ga4_snapshot 非 null):从 summary / by_country / by_channel 抽取 ga4_signals;不覆盖 positioning(见 `references/ga4-snapshot-contract.md`)
4. **category_normalized 归一**:归到 saas / ecommerce / creator-tool / content-app / tool-utility / other

**边界情况**:
- builder_prompt 极短 → 隐含线索降级,tone 默认 casual,`_rationale` 标注
- positioning 与 builder_prompt 冲突 → 以 positioning 为准
- ga4_snapshot 为 null 或缺少 summary → 视为未使用
- promo_goal 无法归类 → 默认 cold-start
- target_market 空 → 默认 `["US"]`

**上下游**:
- Stage 2 读:`app_summary.category_normalized`、`audience.primary_persona`、`promo_intent.goal_type`、`ga4_signals`
- Stage 3 读:全量
- Stage 4 读:`audience.tone_preference`、`value_prop.*`

### 4.3 Stage 2 — Platform Fit

**目的**:对 `platform_scope` 内每个平台计算 fit_score(0-100),给出推荐排序。**不过滤**,scope 内平台全部进入 Stage 3-4。

**输入**:`intent_profile` + `platform_scope`。

**输出**:
```
{
  ranking: [platforms 按 fit_score 降序],
  scores: { platform: { fit_score, strengths[], weaknesses[], recommended_focus[] } },
  _rationale: string
}
```

**LLM 动作(4 步)**:
1. 读 `platform-playbooks/{platform}.md` §2 §4(受众画像 + 内容形式适配);playbook `_schema_version` 不匹配 → warning
2. **计算 fit_score**(加权):

   | 维度 | 权重 | 计算方式 |
   |---|---|---|
   | Audience overlap | 40 | primary_persona × playbook §2 主受众语义重叠 |
   | Goal-format fit | 30 | goal_type × playbook §4 平台优势形式匹配 |
   | Category leverage | 20 | category_normalized 在 playbook §9 案例密度 |
   | Time horizon | 10 | week-1 时 TT+10 / IG+5 / YT+2;month-1 平均 |

3. **生成 strengths/weaknesses/recommended_focus**:每平台 ≥2 strength + ≥2 weakness;recommended_focus 从 playbook §4 支持形式中选 1-3 个 post_type
4. **Ranking**:按 fit_score 降序;并列取 goal-format fit 更高者优先

**边界情况**:
- 三平台 fit_score 全 < 40 → 正常输出 ranking,`_rationale` 标记 "all platforms weak fit";Stage 5 触发 blocker B4
- Playbook `_schema_version` 缺失 → 该平台 confidence 降级到 medium;Stage 5 加 W3
- platform_scope 单平台 → ranking 单项,不做跨平台比较
- `ga4_signals.traffic_level == zero` → TT +3
- `ga4_signals.dominant_channel` ∈ {Organic Social, Cross-network} → TT +3, IG +2
- `tone_preference == build-in-public` → TT+3 / IG+3 / YT-3

**上下游**:Stage 3 读 `scores.{platform}.recommended_focus`;Stage 5 读 ranking 决定 schedule 平台占比。

### 4.4 Stage 3 — Content Strategy(per platform)

**目的**:为 scope 内每一个平台生成 `PlatformStrategy` — 3-5 个 angles + hashtag 5-slot mix + posting cadence + 可选 trend_borrow(仅 TT)。

**输入**:`intent_profile` + `platform_fit`;每平台读对应 playbook §5 §6 §7 §9;仅 TT 读 `tiktok_trend_snapshot.json`(校验 `$last_refresh` < 4 周)。

**输出**(每平台一份 `PlatformStrategy`):
```
{
  platform, angles[3-5], hashtag_mix { slots }, posting_cadence,
  trend_borrow: null | {...},   // 仅 TT
  _rationale
}
```

**LLM 动作(5 步)**:

1. **Angle 生成(3-5 个)**
   - 数量由 fit_score 决定:≥70 → 5、40-70 → 4、<40 → 3
   - 每 angle 必须含 key_selling_point(Stage 5 grep 自检)
   - hook_pattern 从 playbook §5 六种中选,优先该平台 top-2 pattern
   - post_type 从 `recommended_focus` 选;5 个 angles 尽量分散 hook_pattern
   - narrative_arc:三选一 `problem→solution→CTA` / `setup→payoff` / `before→after`

2. **Hashtag 5-slot mix**(读 playbook §6)
   - slot 1 broad:1-2 条最大流量
   - slot 2 mid-1:1-2 条中等热度、受众重叠
   - slot 3 mid-2:1-2 条另一维度中热度
   - slot 4 niche:1-2 条精准长尾
   - slot 5 brand:1-2 条品牌/产品
   - **TT 特有**:slot 2/3 优先从 `trend_snapshot.trending_hashtags[]` 选(需确认 atoms_relevance 匹配)

3. **Posting cadence**(读 playbook §7)
   - week_1_frequency:排位一 3-5 posts / 排位二 2-3 / 排位三 1-2
   - best_time_slots:3-5 条 primary_market 时区高活跃时段
   - rationale_ref:playbook §7 章节引用

4. **Trend borrow(仅 TT)**
   - snapshot 新鲜(< 4 周):填 trending_hashtags_slot_2 / trending_sounds_top_3(license commercial-safe + decay > 5 天) / snapshot_date
   - 过期或非 TT:`trend_borrow: null`

5. **_rationale**:3-5 句,说明 angle 数量、hook_pattern 分布、hashtag 组合逻辑、cadence 依据、TT trend 使用情况,引用具体 playbook 章节

**边界情况**:
- Playbook §9 案例 < 3 → angles 降到 3,confidence 降到 medium
- TT trend snapshot 过期 → `trend_borrow: null` + Stage 5 W2
- primary_market 非 US 且 playbook §7 未覆盖 → fallback US 时段并 `_rationale` 标注
- tone == professional 且 platform == tt → 禁 pov / suspense hook_pattern(调性冲突)
- 某 angle hook_pattern 无 §9 案例 → estimated_fit=low,confidence 下调

**上下游**:Stage 4 逐平台读 strategy 渲染;Stage 5 用 hashtag_mix 校验 caption 展平完整性、用 trend_borrow.snapshot_date 触发 W2。

### 4.5 Stage 4 — Deliverable Rendering(per platform)

**目的**:把 Stage 3 strategy 渲染成用户可直接使用的产物:captions / storyboards / ab_variants。分两步 — 骨架生成(a) + 挂载 media prompts(b)。

**核心契约**:不生成任何图片/视频素材,只挂载 `injectable_prompt` 字符串。

**输入**:`intent_profile` + `strategies`(全平台) + `templates/caption.md` + `templates/storyboard.md`。

**输出**(每平台):
```
{ posts: Caption[], storyboards: Storyboard[], ab_variants: Caption[] }
```

**LLM 动作 — Step a:骨架生成**

对每个 angle:
- 视频类(reels / short / tt-video-*):产出 storyboard + caption(caption 也放 posts 数组用于 schedule 引用)
- 非视频类(carousel / ig-static / yt-thumbnail-post):只产出 caption

**关键约束**:
- `caption.hashtags` 必须是 Stage 3 `hashtag_mix.slots` 按顺序展平的完整集合
- `caption.body` 必须显式含 `key_selling_point`(Stage 5 blocker B1 自检)
- `caption.cta.link_style` 按 platform 选:IG comment-pin(冷启动首选)/ bio-link;TT comment-pin;YT bio-link(video description)
- storyboard.scenes 首个 purpose 必须 `hook`,至少一个 `cta`
- scenes.duration_s 之和必须 = total_duration_s(不等则自动调整最后一 scene 补足)

**LLM 动作 — Step b:挂载 media prompts**

Injectable_prompt 撰写四要素:
1. 视觉主体(what)
2. 光线氛围(mood/lighting)
3. 构图/风格(composition/style)
4. aspect_ratio(明确)

Caption.media_prompts 规则:
- 视频类:cover_image=null, carousel_slides=null(视频首帧即封面)
- carousel:cover_image=null, carousel_slides=[3-10 slides]
- ig-static / yt-thumbnail-post:cover_image=填, carousel_slides=null

Storyboard.scenes[].media_prompts 规则(三字段互斥):
- 用户自拍/实拍素材:`video_prompt=null, image_prompt=null, b_roll_hint="..."`(非空)
- 需 AI 生成视频:填 `video_prompt`(含 duration_hint_s + 9:16 aspect_ratio)
- 静态图叠字幕:填 `image_prompt`

Video_prompt 四要素:镜别(close-up/medium/wide)+ 主体+动作 + 光线+场景 + 时长+aspect_ratio。

**违规硬约束(Stage 5 blocker)**:
- injectable_prompt 内容为 "TBD"/"..."/纯占位 → B2
- injectable_prompt 长度 < 20 字符 → B2
- 视频类 scene 三字段(video_prompt/image_prompt/b_roll_hint)全 null → B3

**LLM 动作 — A/B 变体**:
- **仅对 confidence=high 的 posts 生成变体**;每 high-confidence post 生成 1 个 variant
- 差异维度二选一:Hook 变体(换 hook_pattern)/ CTA 变体(换 cta.text)
- `angle_id` 后缀 `-v2`(如 `ig-01-v2`)
- 变体只做 caption,不重复生成 storyboard(即使原 post 是视频类)—— 变体主要测文案 CTR
- `_rationale` 说明变体维度选择

**边界情况**:
- Stage 3 只有 3 angles 且都 confidence != high → ab_variants 空数组
- storyboard scenes 总时长 ≠ total_duration_s → 自动调整最后一个 scene
- TT 但 trend_borrow=null → sound_ref.source="original"
- 视频类 post_type 但 total_duration_s 超平台上限 → 强制截到上限并 `_rationale` 标注

**上下游**:Stage 5 遍历 deliverables 计数 injectable_prompts、跑 B1/B2/B3/B6/W1 自检。

### 4.6 Stage 5 — Pack & Self-check

**目的**:组装 Launch Pack 顶层 JSON,跑自检规则,输出 checks(blocker/warning/info)与 `_pipeline_meta`。

**输入**:全部前置 stage 产物 + 原始 inputs + Playbook 版本信息。

**输出**:符合 `launch_pack_schema.json` 的完整 Launch Pack。

**LLM 动作(6 步)**:

1. **组装 launch_brief**:app_name / one_liner / promo_goal / target_audience / key_selling_point / primary_market 从 inputs + intent_profile 抽取

2. **引入前置产物**:platform_fit / strategies / deliverables 整体拷贝

3. **生成 schedule**(读 `templates/schedule.md` 骨架):
   - Launch day(offset=0)放 ranking 首位平台的 confidence=high angle
   - 覆盖 3-6 条,单日单平台不重复
   - 高 fit 平台占 ≥ 60%
   - 每 scope 内平台首周至少 1 条(fit < 40 也留 1 条试水)
   - 引用 playbook §7 时段
   - `notes` 填全周节奏综述

4. **跑自检规则**(见 § 7 完整清单)

5. **填 `_pipeline_meta`**:
   - `playbook_versions`:读每个 playbook `_schema_version` 或 frontmatter date
   - `trend_snapshot_last_refresh`:读 `tiktok_trend_snapshot.json.$last_refresh`(若 scope 含 tt);否则 null
   - `confidence_summary`:每平台 Stage 3 angles confidence 最低值 → 映射到 low / medium / medium-high / high
   - `ga4_used`:`inputs.ga4_snapshot != null && intent_profile.ga4_signals != null`
   - `media_generation_deferred`:**恒 true**(硬编码)
   - `injectable_prompts_count.images`:遍历 media_prompts.cover_image + carousel_slides[] + scenes[].image_prompt 非 null 计数
   - `injectable_prompts_count.videos`:遍历 scenes[].video_prompt 非 null 计数

6. **填 top-level `generated_at`**:ISO 8601 精度到秒

**边界情况**:
- 任一 blocker 触发 → Launch Pack 仍完整输出,顶层附加 "❌ Blocker present, launch pack not ready to ship";上层收到应提示用户修
- Playbook `_schema_version` 缺失 → `playbook_versions.{platform}` 填 "unknown",触发 W3
- trend_snapshot 文件不存在 → `trend_snapshot_last_refresh: null`,不 warning(未使用)

**上下游**:上层 Atoms builder 消费完整 Launch Pack;用户看到 posts/storyboards 后显式触发「生成图片/视频」,上层把 injectable_prompt 注入对话由下游图片/视频工具消费;上层根据 checks 决定是否阻塞发布或提示用户。

---

## 6. Template 体系

### 6.1 作用

Template 是 Stage 4/5 渲染产物时的**骨架规范**,不是自由生成模板。作用:
1. 确保 caption / storyboard / schedule 输出严格符合 `launch_pack_schema.json` definitions
2. 明确每个字段的填写规则、允许值、互斥关系
3. 降低 LLM 幻觉与漂移(如漏字段、hashtags < 5)
4. 提供参考示例减少 few-shot 依赖

### 6.2 三类模板与消费 stage

| 模板 | 消费 stage | 消费方式 | 核心作用 |
|---|---|---|---|
| `templates/caption.md` | Stage 4 | 每 angle 渲染 caption 时读 | Caption JSON 结构 + 字段规则 + 示例 |
| `templates/storyboard.md` | Stage 4 | 视频类 angle 渲染 storyboard 时读 | Scenes 骨架 + purpose 枚举 + 三字段互斥 |
| `templates/schedule.md` | Stage 5 | 生成 week_1 时读 | week_1 数组 + 分配规则 + 平台×时段速查表 |

### 6.3 Caption 模板设计要点

**JSON 严格结构**(见 launch_pack_schema.json definitions.Caption):
- 必填字段:angle_id / platform / post_type / hook / body / cta / hashtags / confidence
- CTA 结构:`{ text, link_style ∈ [bio-link, comment-pin, swipe-up, none] }`
- hashtags ≥ 5(对应 Stage 3 5-slot 展平)
- media_prompts 见 § 6

**关键约束**:
- body 必须显式包含 `key_selling_point`(Blocker B1 grep 自检)
- hook 长度受平台限制(W1):IG reels / tt-video hook > 15 char → warning;carousel / short > 20 char → warning
- link_style 与 platform 约定优先级:
  - IG 冷启动首选 comment-pin
  - TT 几乎总用 comment-pin
  - YT 用 bio-link(video description)

### 6.4 Storyboard 模板设计要点

**适用范围**:仅视频类 post_type(reels / short / tt-video-*)。

**核心结构**:
- `total_duration_s`(5-180 秒,按平台上限截断)
- `sound_ref: null | { source, sound_id, decay_window_days_left }`
- `scenes: [ { scene_id, duration_s, purpose, visual_note, text_overlay, voiceover_or_dialogue, b_roll_hint, media_prompts } ]`
- `caption`:嵌入完整 Caption 结构(可与 posts 数组同 angle_id 复用)

**Purpose 枚举(6 种)**:hook / context / reveal / proof / cta / loop
- 首个 scene 必须 `hook`(Stage 4 强约束)
- 至少一个 `cta` scene
- `loop` 用于 TT 循环起手

**Scene media_prompts 三字段互斥关系**:
| 场景 | video_prompt | image_prompt | b_roll_hint |
|---|---|---|---|
| 用户自拍/实际录屏 | null | null | 非空(说明素材类型) |
| AI 生成视频 | 填(injectable_prompt+duration_hint_s+aspect_ratio) | null | 可选 |
| 静态图叠字幕 | null | 填(injectable_prompt+aspect_ratio) | 可选 |

**Sound_ref 时效管理**:
- decay_window_days_left < 5 → Stage 5 W4
- TT 且 trend_borrow=null → source="original"

**Duration 一致性**:scenes[].duration_s 之和必须等于 total_duration_s;不等则自动调整最后一个 scene 并在 `_rationale` 标注。

### 6.5 Schedule 模板设计要点

**输出结构**:
```
{
  week_1: [
    { day, date_offset_from_launch, platform, post_ref, recommended_time, rationale }
  ],
  notes: string
}
```

**分配规则**:
- 覆盖 3-6 条(< 3 → Blocker B7)
- 单日单平台不重复
- 高 fit 平台占 ≥ 60%
- 每 scope 内平台首周至少 1 条(fit < 40 也留 1 条试水)
- Launch day(offset=0)放 ranking 首位平台的 confidence=high angle
- `recommended_time` 从对应 platform playbook §7 时段抽,匹配 primary_market 时区

**平台 × 时段速查表**(Schedule 模板内嵌):
- 提供 IG/YT/TT × 工作日/周末 的时段矩阵,减少 LLM 现场从 playbook 检索的成本

**post_ref 约定**:引用 `deliverables.{platform}.posts[].angle_id`,不重复内容。

### 6.6 Template 演进原则

- v0.1:三类固定模板,不允许用户自定义
- v0.2:预留 `references/templates/` 扩展,支持用户上传;需通过 schema 校验后加载
- Template 变更即产物结构变更,必须与 `launch_pack_schema.json` 同步升级

---

## 7. Playbook 体系

### 7.1 作用

Playbook 是**平台原生知识的沉淀载体**,让 LLM 无需实时抓取即可基于平台特性做决策:
1. 平台受众画像、算法机制、内容形式、调性、hashtag 策略、发布节奏、案例、避坑
2. 为 Stage 2 提供 fit_score 计算依据
3. 为 Stage 3 提供 angle / hashtag / cadence 生成依据
4. 为 Stage 5 提供 confidence 与 playbook_versions 元数据

### 7.2 10-Section 标准 Schema

见 `references/platform-playbooks/_schema.md`。所有平台 playbook 遵循同一结构:

| Section | 主题 | 关键内容 |
|---|---|---|
| §1 | 平台定位 | 用户量级、核心场景、竞争格局 |
| §2 | 用户画像 | 主受众人口特征、行为模式、消费能力、心智偏好 |
| §3 | 算法机制 | 推荐权重、冷启动规则、影响力衰减、跨平台差异 |
| §4 | 内容格式规格 | 允许 post_type、时长/尺寸/分辨率、素材要求 |
| §5 | 调性关键词 | 6 种 hook_pattern + 每种在该平台的适配度(top-2 标注) |
| §6 | Hashtag 策略 | 5-slot 组合逻辑、平台特殊规则(如 TT 关联趋势) |
| §7 | 发布节奏 | 频率建议、时段矩阵(工作日/周末)、时区差异 |
| §8 | 业务类型适配 | SaaS / ecommerce / creator-tool / content-app 等在该平台的差异化打法 |
| §9 | 高转化模式 | Winning structures 案例集(至少 3-12 条,含数据支撑) |
| §10 | 避坑清单 | 禁忌调性、违规 hashtag、算法惩罚触发点 |

### 7.3 Frontmatter 约定

每个 playbook 顶部含 YAML frontmatter:

```yaml
---
platform: ig | yt | tt
_schema_version: 0.1.0
last_updated: 2026-07-01
sources: [官方文档链接、第三方研报、Creative Center 快照 hash]
---
```

- Stage 2 读 `_schema_version` 校验兼容性,不匹配 → W3
- Stage 5 读 `_schema_version` 写入 `_pipeline_meta.playbook_versions`
- `last_updated` 用于人工评估是否需要刷新(≥ 3 个月建议 review)

### 7.4 Stage 消费映射

| Stage | 消费 section | 用途 |
|---|---|---|
| Stage 2 | §2 §4 | 计算 fit_score(Audience overlap / Goal-format fit) |
| Stage 3 | §5 §6 §7 §9 | 生成 hook_pattern / hashtag mix / cadence / 案例参考 |
| Stage 5 | frontmatter | 读 `_schema_version` 写入 playbook_versions |

**关键设计**:Stage 精确读对应 section,不加载全 playbook,减少 LLM 上下文压力。

### 7.5 Playbook 版本管理

- v0.1:IG / YT / TT 三份 playbook 由团队人工维护;每份约 200-500 行
- 更新触发:平台重大算法调整、新内容形式上线、Creative Center 快照重大偏差、每季度 review
- 变更影响面:
  - §2 §4 变更 → 影响 Stage 2 fit_score
  - §5 §6 §7 §9 变更 → 影响 Stage 3 生成质量
  - Schema 变更(§1-§10 结构增删) → `_schema_version` 升级,所有 playbook 同步升级

### 7.6 新平台扩展流程(v0.1 未覆盖 LinkedIn / X)

1. 按 `_schema.md` 补齐 10 section 内容
2. 在 `inputs_schema.json` 的 `platform_scope` 允许枚举中新增
3. 在 SKILL.md「何时启用」中移除拒绝该平台的表述
4. 若平台有专属数据源(类似 TT Creative Center),按 TT 模式补齐 `data/{platform}_trend_snapshot.json` + 采集脚本

---

## 8. 自检与质量保障机制

Stage 5 执行三级自检,输出到 `checks` 字段。

### 8.1 Blocker(阻断级,必须为空)

| ID | 规则 | 触发条件 |
|---|---|---|
| B1 | key_selling_point 覆盖 | 某个 caption.body 不含 positioning.key_selling_point 关键词(宽松语义匹配) |
| B2 | media prompt 非占位 | 任一 injectable_prompt == "TBD"/"..."/长度 < 20 char |
| B3 | 视频类 scene 三字段全空 | 某 storyboard.scenes[i] 的 video_prompt/image_prompt/b_roll_hint 全 null |
| B4 | 三平台 fit 全 < 40 | platform_fit.scores 中所有 fit_score < 40 |
| B5 | CTA 与 promo_intent 一致 | goal_type=cold-start/user-acquisition 但 cta.link_style=none 且 cta.text 无转化动作词 |
| B6 | hashtags 5-slot 展平完整 | 某 caption.hashtags 数组 < 5 条,或不能对应回 5-slot |
| B7 | schedule 覆盖不足 | schedule.week_1 长度 < 3 |
| B8 | media_generation_deferred 恒 true | `_pipeline_meta.media_generation_deferred != true`(设计契约不允许违反) |

### 8.2 Warning(告警级,记录不阻断)

| ID | 规则 | 触发条件 |
|---|---|---|
| W1 | Hook 长度 | IG reels / tt-video hook > 15 char,或 carousel / short hook > 20 char |
| W2 | TT trend snapshot 时效 | 使用了 trend_borrow 但 snapshot_date 距今 > 4 周(理论 Stage 3 已置 null) |
| W3 | Playbook `_schema_version` 不匹配 | 某 platform playbook 版本与 skill 期望不符 |
| W4 | Sound decay 临近 | 某 storyboard.sound_ref.decay_window_days_left < 5 |
| W5 | 变体缺失 | 有 confidence=high 的 post 但未生成 ab_variant |

### 8.3 Info(信息级)

| ID | 规则 | 触发条件 |
|---|---|---|
| I1 | GA4 未提供或未集成 | `_pipeline_meta.ga4_used == false`(info,非 blocker) |
| I2 | scope 不完整 | `platform_scope` 只含 1-2 个平台 |
| I3 | Fit 排位悬殊 | ranking 首末 fit_score 差 > 40 |

### 8.4 自检失败处理策略

- **Blocker 出现**:Launch Pack 仍完整输出(便于用户看到问题所在),顶层 warning 附加 "❌ Blocker present, launch pack not ready to ship";上层根据 checks.blocker 长度决定是否阻塞发布或提示用户修改后重跑
- **Warning 出现**:不阻断,展示给用户参考
- **Info**:仅记录,不必强提示

---

## 9. 媒体资产两级触发契约

### 9.1 契约表述

Pipeline 只挂载 `injectable_prompt` 字符串,**不生成任何图片/视频**。

- Stage 4 输出每个 `media_prompts.*` 对象含 `trigger: "on-demand"` 标记
- `injectable_prompt` 是可直接注入对话让下游 image/video 工具消费的完整 prompt(不做二次解析)
- `_pipeline_meta.media_generation_deferred == true` **恒成立**(硬编码,B8 blocker 强制)

### 9.2 责任划分

| 层级 | 负责 |
|---|---|
| Skill(pipeline) | 生成结构化 prompt 字符串,校验非空非占位,计数 |
| 上层 Atoms builder | (1) 展示挂载的 prompt(可折叠)<br>(2) 提供「生成图片」「生成视频」按钮<br>(3) 用户点击时把 `injectable_prompt` 注入对话由下游图片/视频工具生成<br>(4) 管理生成状态、失败重试、素材落地 |

**Pipeline 侧责任边界到此为止**,不管生成成功与否。

### 9.3 设计理由

1. **解耦职责**:内容策略与素材生成解耦,pipeline 快、稳定、可复现;素材生成成本高、失败率高、单独触发
2. **成本可控**:用户可能不需要所有 media 资产,按需触发节省 tokens 与生成成本
3. **多工具兼容**:injectable_prompt 是字符串,可路由到任何下游图片/视频工具(如 Midjourney / Sora / Runway 等)
4. **交互体验**:用户先看到完整内容策略再决定生成哪个,避免一次性大量素材淹没

### 9.4 Injectable_prompt 撰写四要素

Caption cover_image / carousel_slides / scene.image_prompt:
1. 视觉主体(what)
2. 光线氛围(mood / lighting)
3. 构图 / 风格(composition / style)
4. aspect_ratio(明确)

Scene.video_prompt:
1. 镜别(close-up / medium / wide)
2. 主体 + 动作
3. 光线 + 场景
4. 时长 + aspect_ratio(9:16 for TT/reels/shorts)

---

## 10. 数据资产

### 10.1 静态数据资产清单

| 文件 | 用途 | 更新频率 | 消费 stage |
|---|---|---|---|
| `data/inputs_schema.json` | 输入契约 | 版本迭代 | 入口校验 |
| `data/ga4_snapshot_schema.json` | GA4 快照契约 | 版本迭代 | 上层拉取 GA4 后校验 |
| `data/launch_pack_schema.json` | 输出契约 | 版本迭代 | Stage 5 校验 |
| `data/tiktok_trend_snapshot.json` | Creative Center 快照 | 2-4 周 | Stage 3 TT trend_borrow |
| `data/tiktok_case_studies.json` | TT 案例 | 按需追加 | Stage 3 定性引用 |
| `data/ig_case_studies.json` | IG 案例 | 按需追加 | Stage 3 定性引用 |
| `data/youtube_case_studies.json` | YT 案例 | 按需追加 | Stage 3 定性引用 |
| `data/*_manual_supplements.md` | 各平台人工补齐 | 按需 | Stage 3 定性引用 |

### 10.2 TT Trend Snapshot 时效管理

`tiktok_trend_snapshot.json` 顶层含 `$last_refresh` 字段(ISO 8601 date):

- **新鲜(< 4 周)**:Stage 3 允许 trend_borrow 使用其内容
- **过期(≥ 4 周)**:Stage 3 强制 `trend_borrow: null`(即使 scope 含 TT);Stage 5 W2 提示上游数据未刷新
- **Schema**:`trending_hashtags[]`(含 atoms_relevance 字段)、`trending_sounds[]`(含 license_type / decay_estimate)

### 10.3 采集脚本(不在 pipeline 内)

`scripts/` 目录含平台数据采集流程:
- `oembed_fetch.py`:IG / TikTok oEmbed 元数据抓取
- `youtube_data_api.py`:YouTube Data API 调用
- `tiktok_creative_center_refresh.md`:TT Creative Center 手动刷新流程(浏览器)

**关键约定**:Pipeline 只消费 `data/` 内已落盘产物,不实时抓取。采集脚本由团队定期运行,产物落盘到 `data/`。

---

## 11. 扩展点与版本演进

### 11.1 v0.1 明确不实现

| 扩展点 | 预留位置 | 演进路径 |
|---|---|---|
| Session / memory | inputs 顶层 `session_id` | v0.2 引入,支持二次生成 diff |
| 反馈闭环 | Stage 5 后接 Stage 6 | v0.3 接效果反馈,支持 angle 权重迭代 |
| LinkedIn / X | `platform_scope` 白名单扩展 | 补齐 playbook 后自动生效 |
| 自定义模板 | `references/templates/` | v0.2 用户可上传(需 schema 校验) |
| 多语言 | Stage 4 `locale_override` | v0.3 按 target_market 本地化 |
| Media 生成回填 | `_pipeline_meta.media_generation_deferred=false` 分支 | 上层负责,skill 不改契约 |

### 11.2 版本演进原则

1. **契约优先**:输入/输出 schema 变更即 major/minor 升级,`_schema_version` 与 skill 版本同步
2. **向后兼容**:v0.2 新增字段必须可选,v0.1 输出仍可解析
3. **Playbook 版本独立**:playbook `_schema_version` 与 skill 版本可解耦(内容更新不需 skill 升级)
4. **数据资产不进契约**:trend_snapshot / case_studies 变更不触发 skill 版本变更

### 11.3 版本演进路线

| 版本 | 核心特性 | 预计触发 |
|---|---|---|
| v0.1.0 | 首发,IG/YT/TT 三平台首周 pack | 已落盘 2026-07-03 |
| v0.2.0 | Session/memory + 自定义模板 + LinkedIn playbook | 二次生成需求验证后 |
| v0.3.0 | 效果反馈 Stage 6 + 多语言 + month_1 节奏 | 首批用户 30 天数据回收后 |

---

## 12. 附录

### 12.1 Schema 引用

- 输入:`data/inputs_schema.json`(JSON Schema draft-07)
- GA4 快照:`data/ga4_snapshot_schema.json` + `references/ga4-snapshot-contract.md`
- 输出:`data/launch_pack_schema.json`(JSON Schema draft-07)
- Playbook:`references/platform-playbooks/_schema.md`(Markdown 结构规范)

### 12.2 关键设计决策速查

| 决策 | 选择 | 理由 |
|---|---|---|
| Pipeline 结构 | 线性 5 阶段,非 DAG | 依赖单向,便于测试与复现,v0.1 无需编排引擎 |
| 平台过滤 | Stage 2 不过滤,scope 全进入 | 让用户看到全景 fit,自行判断;避免误杀 |
| 媒体生成 | Pipeline 只挂 prompt,不生成 | 成本可控 + 多工具兼容 + 交互体验 |
| A/B 变体范围 | 仅 confidence=high posts,每 post 1 variant | 避免变体爆炸,聚焦确定性收益 |
| Playbook 消费 | Stage 精确读 section 不加载全文 | 减少 LLM 上下文压力,提升准确性 |
| TT trend 时效 | 4 周新鲜度 + 过期自动降级 | 平衡数据新鲜度与采集成本 |
| Schedule 覆盖 | 3-6 条,每平台 ≥ 1 | 平衡冷启动强度与用户执行负担 |
| Skill 调起 | 隐式组合 + 显式 slash + Chip 预设 prompt | 生命周期 Chip 不直接调 skill;Router 在上层统一判定 |

### 12.3 上层集成要点

上层 Atoms builder 消费 Launch Pack 时应提供:
1. **Intent Router**:实现 §4.3 隐式/显式/分流规则;调起前跑 Router,未命中则不进入 skill
2. **生命周期 Chip 栏**:对话框输入框上方,按 §4.3.3 条件展示;点击注入预设 prompt(不自动发送)
3. **Slash command 注册**:`/social-marketing-skills` 在 builder 对话中可用
4. **展示层**:master-detail 布局(左侧平台/日期切换,右侧 post 详情)
5. **Media 触发按钮**:每个 media_prompts 位置提供「生成图片/视频」按钮,点击注入 `injectable_prompt` 到对话
6. **Checks 展示**:blocker 红色阻断 / warning 黄色提示 / info 灰色折叠
7. **重跑入口**:用户修改 positioning 或补齐 GA4 后可触发 pipeline 重跑

### 12.4 相关文档

- 上游战略:`/Users/shendufuzhi2026/docs/superpowers/specs/2026-07-01-social-marketing-skill-design.md`
- Skill 实现:`/Users/shendufuzhi2026/.claude/skills/atoms-social-marketing/`
- 需求分析:Notion「Atoms 社媒营销需求分析」

---

**PRD 版本**:0.1.0
**首次落盘**:2026-07-03
**维护者**:Atoms 产品团队
