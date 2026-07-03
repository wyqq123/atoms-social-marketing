---
name: platform-playbook-schema
type: template
description: 三大社媒平台(IG/TikTok/LinkedIn) playbook 的通用结构模板,所有平台 playbook 均按此结构撰写与更新,保证 skill 加载时结构一致、字段可预测。
version: 1.0
last_updated: 2026-07-01
---

# Platform Playbook Schema

## 使用说明

- 每个平台 playbook 严格按下列 10 个 section 编写,section 顺序、标题不变
- 数据来源必标注:每个数据点后跟 `[来源: xxx, 时间]`,便于后续复核
- 更新节奏:每 6 个月强制复核算法机制与内容格式规格章节;其他章节按需
- 目标读者:Skill 加载时的 Agent(用于生成内容决策)+ 人类维护者(用于校准与迭代)
- **不写什么**:不写产品营销案例的全文引用(占字段);只提炼可复用的结构化规律

---

## Section 1 — 平台定位与核心用户

**目标**:1-2 段话讲清"这个平台是什么,谁在上面,他们在这里做什么"

**必填字段**

- `platform_name`:平台名称
- `elevator_pitch`:一句话定位(该平台在社媒生态中的独特位置)
- `mau_and_geography`:月活规模 + 主要地域分布 + 数据来源
- `primary_use_cases`:用户使用该平台的核心场景(3-5 项)
- `builder_relevance`:该平台对 Atoms builder(SMB 创业者)的战略价值

---

## Section 2 — 用户画像三视图

**目标**:让 Agent 生成内容时能"想象读者是谁"

**必填字段**

- `demographics`:年龄分布 / 性别比例 / 收入区间 / 教育背景
- `psychographics`:核心心理动机(为什么打开这个平台)、内容偏好、消费决策链路
- `intent_layers`:平台上用户的意图分层(消遣 / 学习 / 购买 / 关注创作者 / 商业社交等)及各层大致占比
- `builder_target_segments`:结合 Atoms builder 业务类型(SaaS / ecommerce / creator),该平台适合触达哪些用户细分

---

## Section 3 — 算法机制(核心)

**目标**:让 Agent 生成内容时知道"什么样的内容会被推流"

**必填字段**

- `distribution_model`:分发逻辑总览(关注流 vs 推荐流 vs 混合)
- `ranking_signals`:排名信号权重(如 IG 是 saves > shares > comments > likes > time spent)
- `content_type_priorities`:不同内容类型的推流优先级(如 Reels vs Feed vs Story)
- `engagement_window`:内容表现关键窗口期(发布后多少小时决定后续推流)
- `algo_penalties`:哪些做法会被算法降权(如 IG 的 hashtag 滥用、外链跳转、重复内容)
- `recent_changes`:近 12 个月算法重大调整(附时间戳与来源)

---

## Section 4 — 内容格式规格

**目标**:硬性规格清单,供内容生成时直接引用

**必填字段**

- `post_types`:平台支持的内容类型全清单(如 IG:Feed Post / Reels / Story / Carousel / Live / Guide)
- `dimensions_and_ratios`:每种类型的尺寸 / 时长 / 比例硬性要求
- `caption_length_recommendation`:每种类型的 caption 长度建议(短 / 中 / 长各自适用场景)
- `hashtag_capacity`:hashtag 数量硬上限 + 有效数量建议
- `link_and_cta_rules`:外链 / CTA 位置规则(如 IG 主 feed 无法直接放外链,只能引导 bio link)

---

## Section 5 — 调性关键词与语言风格

**目标**:让 Agent 生成的文案"说话方式对味"

**必填字段**

- `tone_descriptors`:5-8 个调性形容词(如 IG:aspirational / aesthetic / authentic / community-driven)
- `voice_do`:该平台鼓励的语言风格(3-5 条)
- `voice_dont`:该平台会显得违和的语言风格(3-5 条)
- `emoji_and_emphasis`:emoji 使用密度、大小写强调、换行节奏等具体规范
- `hook_patterns`:高转化开头钩子的 3-5 种典型模式(附示例结构,非具体案例文案)

---

## Section 6 — Hashtag 策略

**目标**:hashtag 选择的决策框架

**必填字段**

- `optimal_count`:该平台的最优 hashtag 数量区间(附实测数据来源)
- `mix_strategy`:hashtag 组合策略(如 IG 的 golden mix:1-2 大 hashtag + 3-5 中等 + 3-5 小众 + 1 品牌 tag)
- `research_method`:如何为具体 caption 找到合适的 hashtag(工具 + 步骤)
- `banned_or_risky`:平台明令禁止或已知会导致 shadowban 的 hashtag 类别

---

## Section 7 — 发布节奏与频率

**目标**:发布时机建议(注意时区依赖,标注默认时区)

**必填字段**

- `best_posting_times`:该平台 SMB / Creator 类账号的最佳发布时段(按平日 / 周末分)
- `default_timezone`:上述时段基于的时区(默认 UTC-5 EST 或 UTC-8 PST)
- `frequency_recommendation`:各内容类型的建议发布频率
- `first_week_ramp_up`:新账号 / 冷启动阶段的发布策略(与稳态期不同)

---

## Section 8 — 业务类型 × 平台适配

**目标**:同一平台在 3 种 Atoms 业务类型下的差异化打法(直接对应 Template 矩阵的输入)

**必填字段**(每业务类型独立子节)

**8.1 SaaS / AI Tool**
- `fit_score`:该平台对 SaaS 业务的适配度评分(1-5)+ 一句话理由
- `content_angles`:该业务在该平台上有效的 3-4 种内容切入角度
- `visual_style`:视觉呈现建议
- `caption_focus`:文案重点(功能展示 vs 用户案例 vs 创始人叙事等)
- `cta_style`:该组合下的 CTA 表达方式
- `common_traps`:该业务在该平台上最常见的踩坑

**8.2 Ecommerce**
- 同上结构

**8.3 Creator**
- 同上结构

---

## Section 9 — 高转化模式(样本归纳,非案例引用)

**目标**:从大量高互动内容里归纳出可复用的结构模式

**必填字段**

- `sample_size_and_source`:归纳基于的样本数量 + 抓取时间 + 数据来源
- `winning_structures`:3-5 种反复出现的高转化结构骨架(纯结构,不含具体品牌 / 产品文案)
- `visual_patterns`:高转化视觉模式(封面 / 首帧 / 排版规律)
- `engagement_triggers`:反复推动 saves / shares 的元素类型(信息密度 / 教学价值 / 情感共鸣 / 反常识观点 / 视觉冲击 / 幽默等)

---

## Section 10 — 避坑清单 + 数据源

**必填字段**

- `avoid_list`:8-12 条明确的"不要做"清单(按严重程度排序:导致 shadowban > 降权 > 转化差 > 观感差)
- `references`:所有引用的官方资源 / 行业报告 / 抓取数据的详细来源(URL + 访问日期)
- `next_review_date`:下次强制复核日期(建议 6 个月后)

---

## Frontmatter Convention

每个平台 playbook 头部必须包含:

```yaml
---
name: <platform>-playbook
platform: <instagram | tiktok | linkedin>
version: <major.minor>
last_updated: <YYYY-MM-DD>
data_freshness_note: <关键数据的时效性说明>
review_by: <下次复核日期>
sources_summary: <数据源摘要,一句话>
---
```
