---
name: instagram-playbook
platform: instagram
version: 0.1
last_updated: 2026-07-02
data_freshness_note: 算法机制与格式规则基于 2025-Q4 / 2026-Q1 数据(SocialInsider 35M posts、Hootsuite 2026 Algorithm、Later 2026 Hashtags、Buffer 2023 案例);Mosseri 直引经 2024-2025 多次公开发言交叉确认。所有格式硬规则短期不会变(Reels ≤90s、5-hashtag cap、Stories ≤5 slides 序列),算法信号权重可能季度性微调。
review_by: 2027-01-02
sources_summary: 4 篇 Category B 博客案例(Hootsuite / SocialInsider / Later / Buffer)+ Mosseri 公开发言直引;详见 §10。
---

# Instagram Playbook

> **服务对象**:Atoms 用户所构建应用的 IG 社媒运营(冷启动 + 长期)
> **规模假设**:Atoms 用户 90%+ 处于 0-5K followers,playbook 分级建议默认按此校准。规模上到 10K+ 时切换到 tier 2 打法(见 §4 / §9)

---

## §1 平台定位与核心用户

### `platform_name`
Instagram(Meta 系,与 Facebook / Threads / WhatsApp 数据打通)

### `elevator_pitch`
IG 是全球第二大视觉社媒(仅次于 TikTok),核心角色是**「视觉驱动的兴趣图谱 + 品牌可信度承载层」**——用户在这里发现产品、验证品牌真实性、通过 DM 建立私域关系。它同时是「发现渠道」和「转化前的信任层」,不是纯 top-of-funnel 也不是纯 bottom-of-funnel。

### `mau_and_geography`
- 全球 MAU:2B+(Meta 2024 官方披露)
- 主要地域:美国 / 印度 / 巴西为前三大市场;IG 2026 推 AI 翻译(Hindi/Portuguese/English/Spanish 互译),显式扩大跨语言 reach [来源: Hootsuite Instagram Algorithm 2026, 2026-07]
- 用户结构:18-34 岁占 ≈60%(2025 Meta advertiser data 转述,精确数据需另核)

### `primary_use_cases`
1. 视觉产品发现(ecommerce / lifestyle / D2C 品牌)
2. 创作者关注 + 教程消费(carousel 教育型内容 + Reel 娱乐)
3. 品牌真实性验证(用户在决定购买/使用前会先看品牌 IG)
4. 兴趣社群参与(niche community hashtag + DM 群聊)
5. 私域触达(Stories + DM 是「已存在关系」的高频交互层)

### `builder_relevance`

对 Atoms builder 的战略价值分为三层:

| 阶段 | IG 承担角色 | 关键动作 |
|------|------------|---------|
| 0-1K followers | 借注意力 + 冷启动 | UGC 合作、niche hashtag 曝光、Stories 与已有 followers 深链接 [来源: Sierra Winnow, SocialInsider 2026] |
| 1-10K | 差异化沉淀 | Carousel 教育型内容累积 views + 建立可识别 topic 定位 |
| 10K+ | 品牌资产复利 | Reels 主打 discovery + Carousel 深互动,进入 Sam Oliver 60-30-10 主流 mix |

**核心提醒**:2025 起 IG 增长已结构性放缓——**1-5K 阶段年增长中位仅 22%**,而非 2024 及以前博客常引的 38% [来源: SocialInsider 2026 Benchmarks, YoY drop -42%]。playbook 生成的 KPI 建议必须基于 2025 后的新基线,而非老数字。

---

## §2 用户画像三视图

### `demographics`
- **年龄**:18-34 岁核心(约 60%),35-54 岁快速增长(2024-2025);13-17 岁默认「Teen Account」限制,内容触达受严格过滤 [来源: Hootsuite 2026]
- **性别**:全球接近 5:5,美国略偏女性(≈54%);品类差异极大(美妆/时尚偏女、科技/汽车偏男)
- **地域**:美国用户日均使用时长 30+ 分钟(2024 eMarketer);IG 商业转化力最强的市场是 US / UK / DE / AU / CA
- **收入**:覆盖全收入段,但**高频购物用户**集中在中产及以上

### `psychographics`
- **核心动机**:「看点好看的 / 有用的 / 有趣的」——高美学期待 + 高信息密度期待并存
- **消费决策链路**:发现(Reels/Explore)→ 验证(profile grid + Stories + saves)→ 私域询问(DM)→ 站外购买
- **反常识点**:IG 用户 comments 意愿正在系统性下降(YoY -16%),但 **shares/saves/DM** 明显上升 [来源: Chloe Maguire (Leapsome), SocialInsider 2026]。「engagement hasn't disappeared, it's evolved」——从公开互动迁移到私域互动。playbook 生成内容时,评估目标要相应迁移。

### `intent_layers`
| 意图层 | 大致占比 | 触发内容类型 |
|--------|---------|-------------|
| 消遣 / 娱乐 scroll | ~45% | Reels(短、趣、无 CTA) |
| 学习 / 收藏 | ~20% | Carousel(教程 / checklist / infographic) |
| 关注创作者 / 品牌 | ~15% | Stories / grid 消费 |
| 主动购物意图 | ~10% | Search + Shop tab + product tags |
| 商业社交 / 建关系 | ~10% | DM + comments 深互动 |

**Atoms 生成内容时的意图定位默认**:一条帖子的目标层次要单一——不试图在同一帧同时讨好「消遣」+「学习」+「购物」。

### `builder_target_segments`

**SaaS / AI Tool**
- 核心受众:solopreneur / creator / SMB owner / marketer(自己就是 IG 高频用户)
- 触达机会:通过 productivity / marketing / AI-tool 类 niche community hashtag 曝光
- 挑战:B2B SaaS × influencer 失败样本(8K views / 400 likes / **仅 12 signups**)显示 —— IG 用户以个人身份而非组织身份浏览,选品必须 match ICP audience 而不是 follower 数 [来源: improvado.io SaaS case study]

**Ecommerce**
- 核心受众:视觉驱动买家(fashion / beauty / home / lifestyle 类最强);skew 女性偏中产
- 触达机会:Reels 打开发现 + Carousel 做产品 feature 拆解 + Stories 做促销/新品
- 挑战:高 CAC 品类需要靠 UGC + 微信影响者证明信任,不能纯品牌自制内容

**Creator(独立开发者 / indie hacker / solo builder)**
- 核心受众:同类 builder + 潜在早期用户 + 想学「build in public」的观众
- 触达机会:Carousel「learn in public」教程 + Reels 展示「build in public」瞬间
- 挑战:Creator 类样本在 IG 极稀疏(多数 solo builder 更活跃在 X / LinkedIn)——playbook 生成时需提示用户「IG 不一定是 Creator 类的首选平台」

---

## §3 算法机制(核心)

### `distribution_model`
**IG 不是单一算法,是 4 个独立 AI 排序系统**——Feed / Stories / Reels / Explore 分别有自己的 signal 权重和排序逻辑 [来源: Meta Transparency Center + Hootsuite 2026]。任何「IG 算法喜欢什么」的笼统说法都是错的,必须落到 surface 上讨论。

分发的宏观逻辑:
- **Feed / Stories**:关注流为主,推荐流为辅(算法根据历史互动决定排序)
- **Reels / Explore**:推荐流为主,面向非粉丝
- **混合逻辑**:一条 Reel 同时进关注流 + Reels tab + Explore,每个 surface 用独立信号排序

### `ranking_signals`

**Mosseri 直引(2024-2025 多次公开重复)**:
> Top 3 signals: **watch time**, **likes**, **sends per view**
> ——同时适用 connected reach(粉丝)与 unconnected reach(非粉)

**关键新概念:「sends per view」**——不是绝对 send 数,是 send/view ratio。Playbook 生成内容时的目标从「值得 save」迁移到「**值得 DM 给朋友**」。

#### 按 surface 拆解 signal 权重

**Feed**
- Top signals:10 秒 dwell 停留、creator profile click、comments 与 reshare、recency
- Negative signals:skip / scroll-past 太快、hide、report

**Stories**
- Top signals:viewing history(用户过去是否常看你 Stories)、engagement history(reply/react)、closeness score(IG 亲密度)
- **注意**:Stories 是 4 surface 中最依赖「已有关系」的——冷启动最难破圈,但老粉留存价值最高

**Reels**
- Top signals(Mosseri):**watch time**(#1)、**likes**(#2)、**sends/shares**(#3)
- 次级 signals:rewatch(完播 + 再看)、follow-up actions(看完 profile click / follow / DM)、audio 相关性

**Explore**
- Signal 总数:36 个(Meta Transparency Center 披露,4 surface 中最多)
- Top signals:follow likelihood、**5-second dwell**(比 Feed 10s 门槛低)、**95%+ video completion rate**
- **Explore 是唯一 100% 面向非粉的 surface**;95%+ 完播是所有 signal 中最锐利的 unconnected reach 触发器

### `content_type_priorities`

**按 brand size 分层的格式优先级(SocialInsider 2026 数据实证)**——与主流「Reels-first」建议直接冲突:

| Brand Size | Views 王者 | Comments 王者 | Saves 王者 | Atoms 推荐首要格式 |
|------------|-----------|--------------|-----------|-------------------|
| 1-5K | **Carousel 993** vs Reel 580 vs Image 417 | Reel 3 vs Carousel 2 vs Image 1 | 全部 = 1(无差异) | **Carousel** |
| 5-10K | **Carousel 2117** vs Image 1068 vs Reel 1000 | Reel 6 vs Carousel 4 vs Image 1 | Reel/Carousel 2, Image 1 | **Carousel** |
| 10-50K | **Carousel 4275** vs Image 2340 vs Reel 2460 | Reel 12 vs Carousel 10 vs Image 4 | Carousel 8 vs Reel 7 | Carousel + Reel 并重 |
| 50-100K | **Carousel 11597** vs Image 7405 vs Reel 6095 | Reel 22 vs Carousel 15 vs Image 10 | **Carousel 35** vs Reel 22 vs Image 10 | Carousel 主 + Reel 辅 |
| 100K-1M | **Carousel 35370** vs Image 22900 vs Reel 16035 | Reel 60 vs Carousel 40 vs Image 38 | Reel/Carousel 齐平 96/98 | Reels 主(接近 Sam Oliver 60-30-10 mix) |

**为什么 Carousel views 碾压 Reels?**——根本机制,非内容质量:
> IG 对未 engage 的 carousel 会 resurface,以第 2 slide 作为 cover 再次推入 feed。
> ——Nancy Oganezov (Senior Social Strategist, Dentsu Creative), SocialInsider 2026

这是 carousel「double exposure 特权」——每条 carousel 有 2 次进 feed 的机会。**这条对 Atoms playbook 的战略含义**:tiny brand(<10K)应做 Carousel-first,不是 Reels-first。

### `engagement_window`

**关键窗口:发布后 1-2 小时决定 baseline 分发,**48 小时**决定是否触发「viral momentum」**。

Mosseri 直引:
> If you have a viral post, follow up with another post in the next day or two.

Playbook 生成机制:**爆款接续机制**——单帖 views/engagement 超过账号中位 3x 时,48h 内必须接续一帖同 topic/format,承接算法给的临时权重。

### `algo_penalties`

- ⚠️ **跨平台带水印搬运**(2026 Creativity Priority)——从 TikTok 直接搬运带水印视频将被明确降权 [Mosseri]
- **Engagement bait**(如「double tap if you agree」/「comment YES if...」)——短期数据好看,但算法在识别并降权
- **Mega-hashtag 滥用**(#love / #instagood 等 1B+ posts 类)——分类信号价值 ≈ 0,被算法判 gaming
- **重复内容**——同一素材多次发不会被推;需要重新剪辑或加新 hook
- **不相关 trending tag**——为 reach 追 trending 但内容无关,主动损害 classification 精度
- **Shadowban 风险**:Spammy hashtag 模式 → 可视性静默下降,无通知

### `recent_changes`(近 12 个月)

| 变更 | 时间 | 说明 | Playbook 含义 |
|------|-----|------|--------------|
| **5-hashtag cap** | 2025-12 | Platform-enforced,caption + comments 合计 ≤5 | §6 hashtag 章节整章重写(5-slot portfolio 框架) |
| **Followed hashtags removed** | 2024-12 | 用户无法 follow #tag,hashtag reach 全部由算法中介 | hashtag 从「reach driver」→「classification signal」 |
| **Your Algorithm** | 2025-12 | 用户可主动选「多看/少看」某 topic | 品牌 niche 定位比以前更关键;引导用户建立**明确 topic 标签**而非模糊「lifestyle」类 |
| **AI Translations** | 2025-2026 | Hindi / Portuguese / English / Spanish 自动翻译 caption | Caption 里避免 heavy slang / 文化梗,给 AI 翻译留清晰语义 |
| **Shares > Saves 权重迁移** | 2026 起 | Mosseri 明确 shares 权重 > saves("brings people together") | 内容目标从 save-worthy(信息价值)迁移到 share-worthy(社交价值) |
| **Trial Reels** | 2025 | 对非粉先测,不影响主账号 metrics;数据好则全网推 | 新形式先跑 3-5 条 Trial,数据好再进主发布队列 |
| **Reels max length** | 2025-01 | 上调至 3 分钟(但 sweet spot 仍是 ≤90s) | §4 硬规则:默认 60-90s,超 90s 需明确理由 |
| **Teen Accounts** | late 2024 / early 2025 | 13-17 岁默认更严的内容过滤 | Gen Z targeting 品牌需审查合规(美妆/健身/心理健康) |

---

## §4 内容格式规格

### `post_types`

IG 支持的完整内容类型:

| 类型 | 位置 | 主要用途 | Atoms 推荐权重(1-5K brand) |
|------|-----|---------|---------------------------|
| **Feed Carousel** | 主 feed | 教育、产品拆解、故事 | ⭐⭐⭐⭐⭐(首选) |
| **Reels** | Reels tab + Feed + Explore | Discovery、娱乐、hook 测试 | ⭐⭐⭐(次选) |
| **Feed Single Image** | 主 feed | Culture、humanise、visual moment | ⭐⭐(仅 10% 配额) |
| **Stories** | 顶部 tray | Relationship layer、日常、UGC 转发 | ⭐⭐⭐⭐(daily,配合 Feed) |
| **Live** | Stories tray + Feed | 深互动、Q&A、发布会 | ⭐(偶尔,非常态) |
| **Guides** | Profile tab | 长文合集、精选内容 | 0(基本弃用) |

### `dimensions_and_ratios`

**硬性尺寸/时长要求**(截至 2026-07):

| 类型 | 宽高比 | 尺寸推荐 | 时长 | 硬规则 |
|------|-------|---------|------|-------|
| **Reel** | 9:16 | 1080×1920 | 15s-3min | **默认 60-90s;超 90s 需明确理由** [Hootsuite + Mosseri] |
| **Carousel** | 1:1(推荐)/ 4:5 | 1080×1080 或 1080×1350 | — | **2-10 slides**,推荐 5-7 |
| **Single Image** | 1:1 / 4:5 / 1.91:1 | 1080×1350(4:5 曝光最大) | — | — |
| **Story** | 9:16 | 1080×1920 | 单帧 ≤15s | **单序列 ≤ 5 slides**——超过 views 与 engagement 明确下降 [Eileen Kwok, Hootsuite Social Marketing Specialist] |

### `caption_length_recommendation`

**核心原则**:Hook + 关键 payoff 前置(前 125 字符,IG 默认截断前的可见范围),长文放 Stories/carousel。

| 类型 | 建议长度 | 结构 |
|------|---------|------|
| **Reel** | 短(50-125 字符) | Hook + 单一 payoff;不放长故事 |
| **Carousel** | 中(125-400 字符) | Hook + 「swipe →」暗示 + closing CTA |
| **Single Image** | 短-中(80-300 字符) | Culture-driven 类可短;story-driven 可稍长 |
| **Story** | 极短(overlay text ≤ 8 字) | Overlay text 而非 caption |

**长 caption 的双刃剑**——长文本可以拉 dwell,但也可能被 skip。生成时需评估内容是否有足够信息密度支撑;信息密度不足的长 caption 反而伤 engagement。

### `hashtag_capacity`

**硬规则(2025-12 起 platform-enforced)**:
- **总数上限:5 个**——caption + comments 合计计数,分开放不给额外 slot
- 超出:IG 要么阻止发布,要么自动删除超出部分
- 详细策略(5-slot portfolio 框架)见 §6

### `link_and_cta_rules`

- **Feed post 正文不可放可点击外链**——URL 明文写在 caption 里也不可点
- **Bio link**:唯一从 Feed 引流的官方通路;可用 Linktree / Beacons / 自建 landing 聚合多链接
- **Stories link sticker**:所有账号可用(不再需要 10K followers 门槛);**Story 是 Feed 之外唯一直接外链渠道**
- **Reels 无法加外链**——引导 CTA 只能是「link in bio」/「DM 关键词」
- **DM 自动化**(如 ManyChat)是 Reels/Feed 引流的间接通路——用「comment 关键词 → 自动 DM 发链接」绕开外链限制

### **§4 Atoms 硬规则汇总**(生成 IG 内容时的 must-follow)

1. **Reels ≤ 90 秒**(默认 60-90s)
2. **Stories 单序列 ≤ 5 slides**——长内容拆成 2 天发
3. **Carousel 首帧必带 hook copy**——不能纯图
4. **Carousel 第 2 slide 也要独立 hook**——因 IG 会用第 2 slide 作二次曝光封面(Nancy Oganezov 引 IG 算法特权)
5. **前 3 秒必须有 visual + text 双 hook**(Reels + Carousel 首帧)
6. **禁跨平台带水印搬运**(2026 Creativity Priority)
7. **Hashtag 总数 ≤ 5**(caption + comments 合计)
8. **Feed post 不放外链**——CTA 引导 bio link / Stories link / DM
9. **每 slide 独立成立**——Carousel 单帧被截图/转发时不失去含义
10. **格式优先级按 brand size 分层**(见 §3 表格)

### **§4 Brand-Size 分层格式配比**

| Tier | Regime | 目标 | Primary Format | 配比建议 |
|------|--------|------|---------------|---------|
| **Tier 1: 1-10K**(Atoms 用户主体) | Views + baseline exposure | **Carousel-first** | Carousel(views 优势 1.7x-2x Reels) | Carousel 50% / Reel 30% / Image 10% / Stories daily |
| **Tier 2: 10K-100K** | Engagement depth | Carousel(saves 反超) + Reel(comments 领先) | Carousel 40% / Reel 40% / Image 15% / Stories daily |
| **Tier 3: 100K+** | Algorithm favor + brand equity | Reel-first(接近 Sam Oliver 主流建议) | Reel 60-70% / Carousel 20-30% / Image 10% / Stories 高频 |

**注意**:Atoms 用户 90%+ 处于 Tier 1,playbook 默认按 Tier 1 生成,与主流媒体宣传的「Reels-first」建议直接冲突——这是数据背书的差异化定位。

---

## §5-§10 待补齐

<!-- P1.3 下一步:§5 调性 / §6 hashtag 完整章节(基于 Later 5-slot portfolio) / §7 cadence / §8 三种业务类型适配 / §9 winning structures / §10 avoid list + references -->

**素材已就位**:
- §5 调性:Buffer/Eizzy Baby 案例(反工艺化 / vulnerability driven)
- §6 hashtag:Later 5-slot portfolio 完整框架 + tier framework + format-specific advice
- §7 cadence:Hootsuite tactical tips + Sam Oliver 60-30-10
- §8 业务适配:Buffer/Eizzy Baby(ecom)+ improvado(SaaS 失败案例)+ manual supplements(Creator 类待补)
- §9 winning structures:Nancy Oganezov 的 Carousel 双 hook、Mosseri 爆款接续、Sierra Winnow 三段式增长
- §10 avoid list:Later mistakes(7 项)+ Hootsuite algo penalties(6 项)可合并

**待用户输入**:`data/ig_manual_supplements.md` 中的 Creator 类补齐样本(4-7 条),用于 §8.3

---

*次版本目标*:补齐 §5-§10 后进入 v0.2;v1.0 需要 Category C 官方文档交叉验证(distribution model / algorithm 章节)。
