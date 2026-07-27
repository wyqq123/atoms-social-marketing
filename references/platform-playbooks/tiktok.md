---
name: tiktok-playbook
platform: tiktok
version: 0.1
last_updated: 2026-07-02
data_freshness_note: 算法机制与格式规则基于 2025-Q4 / 2026-Q1 数据(SocialInsider 2026、Hootsuite 2026 Algorithm、TikTok Newsroom 2024-2025、Buffer/Later 2025 案例)。TikTok 相较 IG 数据衰减更快 —— trending sounds/hashtags 生命周期通常 7-14 天,§6 hashtag pool 与 §5 hook patterns 建议每 2-4 周从 TikTok Creative Center 刷新;算法机制与格式硬规则保持 6 个月复核节奏。
review_by: 2027-01-02
sources_summary: 4 篇 Category B 行业报告(SocialInsider/Hootsuite/Later/Buffer)+ TikTok Creative Center 公开趋势数据 + TikTok Newsroom / For Business 官方口径交叉;详见 §10。
---

# TikTok Playbook

> **服务对象**:Atoms builder（应用创建者）所构建应用的 TikTok 社媒运营(冷启动 + 长期)
> **规模假设**:Atoms builder（应用创建者） 90%+ 处于 0-10K followers,playbook 分级建议默认按此校准。TikTok 与 IG 不同,**follower 数不是 reach 的强门槛**——0 粉账号也可能单条 100K+ views(FYP 分发主导)。规模上到 100K+ 时切换到 tier 2 打法(见 §4 / §7)
> **动态更新**:TikTok trend 变化速度远高于 IG,§5 hook / §6 hashtag / §9 winning structures 三节需配合 `.cache/social_intel/manual/tiktok/{region}/{language}/{YYYY-Www}/creative-center.json` 每 2-4 周更新;算法机制与格式规格章节 6 个月复核

---

## §1 平台定位与核心用户

### `platform_name`
TikTok(ByteDance,Douglas 与国内抖音数据/算法分离,同源不同产品)

### `elevator_pitch`
TikTok 是全球最强的 **「算法驱动兴趣发现引擎」**——它把内容与用户匹配的效率推到了社媒极致,几乎完全绕过 follower graph。核心角色是**「零启动门槛的病毒发现层 + 娱乐/短教程消费入口」**——用户不选择 follow 谁,而是接受算法喂食,这让小账号也能单条爆发,但同时 **followers 与后续曝光的关联性远弱于 IG/LinkedIn**。它是 top-of-funnel 首选,不是私域承载层。

### `mau_and_geography`
- 全球 MAU:1.5B+(2024 官方披露);2025 多家 estimates 上探至 1.7B [来源: TikTok Newsroom 2024-04 / DataReportal 2025-01]
- 主要地域:美国 170M+(2024 disclosed to Congress)、印尼、巴西、墨西哥、俄罗斯;欧洲 175M(2024)
- **地缘政策风险**:美国 divest-or-ban 立法 2024-04 通过,后续多次延期;playbook 生成时对纯美国市场依赖 TikTok 的 builder 需提示分发风险 [来源: Reuters 2024-2025 rollup]
- 用户结构:2024 起 25-34 岁成为增速最快段(YoY +14%),18-24 岁核心占比下降至 ≈35%;**"aging up" 是过去 24 个月最重要的人口结构变化** [来源: Statista 2025 / TikTok For Business Q4 2024]

### `primary_use_cases`
1. 娱乐 scroll(entertainment-first,占用户时间的绝对主体)
2. 短教程消费(how-to / hacks / life optimization —— **"TikTok made me learn X"** 已成语言习惯)
3. 产品发现与购买决策(**TikTok Shop 2024 GMV $16B+,美国 2024-2025 快速起量**)
4. 兴趣社群参与(垂类 tag 生态:#BookTok / #CleanTok / #FinTok / #BuildInPublic 等)
5. 音乐/文化 trend 发现(Spotify 承认 60%+ Gen Z 通过 TikTok 发现新音乐)
6. 生活方式模仿与身份表达(Get Ready With Me / Day in the Life 类)

### `builder_relevance`

对 Atoms builder（应用创建者）的战略价值分为三层:

| 阶段 | TikTok 承担角色 | 关键动作 |
|------|----------------|---------|
| 0-1K followers | **借 FYP 打冷启动**(最高效率) | 拍 20-40 条低成本原生视频,让算法找到 audience;单条爆款 = 3-6 个月增长 |
| 1-10K | **确立可识别 niche + hook pattern** | 固定 2-3 种 hook 模板,建立算法 topic classification |
| 10K+ | **product-led content + shop/link integration** | 引流至 bio link / TikTok Shop / DM;开始复用高转化模板批量生产 |

**核心提醒**:TikTok 与 IG 的战略价值不同——
- IG 是「品牌可信度承载层」,follower 数 = 信任资产
- TikTok 是「病毒发现引擎」,follower 数 ≠ 后续曝光保证。**一个 500K 粉账号的新视频可能只有 2K views,而一个 300 粉账号的视频可能 500K views**——每条视频都在与全 TikTok 争夺 FYP 分发权 [来源: Hootsuite 2026 TikTok Algorithm]

对 Atoms builder 的战略含义:**TikTok 的 KPI 不应是 follower growth,而是「爆款率」+「单条 average view」+「view→ external CTR」**。

---

## §2 平台受众与使用心智三视图

### `demographics`
- **年龄**:2026 起结构显著变化——18-24 岁核心占比 ≈35%(2022 时超 50%);25-34 岁 ≈32%(增速最快);35-54 岁 ≈25%(2023-2025 翻倍);55+ ≈8% [来源: Statista 2025 / DataReportal 2026-01]
- **性别**:全球接近 5:5,美国略偏女性(≈53%);垂类差异极大(美妆/舞蹈偏女、科技/金融/汽车偏男、fitness 接近平衡)
- **地域**:美国用户日均使用时长 58 分钟(2024,superapp 最高之一,超 IG 30+)
- **收入**:覆盖全收入段,但**高购买意愿用户**在 18-34 中产段最集中;TikTok Shop 高频买家 skew 女性 25-34
- **教育**:大学在读 + 已毕业占比过半,但 non-college 用户互动率更高(平均视频 like rate 更高)

### `psychographics`
- **核心动机**:「让我笑 / 让我学 / 让我感 / 让我买」——四种情绪出口,不追求 IG 的「aspirational aesthetic」
- **反 IG 的关键特征**:**不追求"看起来完美",追求"看起来真实"**。Overproduction(过度制作)在 TikTok 是 negative signal——被算法与用户共同识别为「广告感」,完播率下降
- **决策链路**:发现(FYP)→ 复看(rewatch)→ profile deep-dive(看历史 2-4 条)→ 私域(comments/DM 或 bio link 跳转)→ 站外购买 / signup
- **反常识点 1**:TikTok 用户对**「广告」的容忍度显著高于 IG**——只要形式原生(native creative,不像广告),即使内容是明确 promo,依然有高互动。这与 IG 用户「广告疲劳」形成鲜明对比 [来源: TikTok For Business Native Ads Study 2024]
- **反常识点 2**:**Comments 是 discovery 的一部分**——用户会翻 comments 找有趣观点/延伸信息,好 comments 直接拉高 completion & dwell。playbook 生成内容时应主动埋 comment hook(见 §9)

### `intent_layers`
| 意图层 | 大致占比 | 触发内容类型 |
|--------|---------|-------------|
| 娱乐 scroll(passive) | ~55% | Skit / meme / trend dance / reaction |
| 学习 / 收藏(active but light) | ~20% | Tutorial / list / how-to / life hack |
| 兴趣社群参与 | ~12% | Niche tag community(BookTok/CleanTok/etc.) |
| 主动购物意图 | ~8% | Product review / haul / TikTok Shop |
| 关注创作者 / 粉丝互动 | ~5% | Q&A / Live / creator series |

**Atoms 生成内容时的意图定位**:**娱乐 > 学习 > 购物** 是默认优先级。SaaS/AI 类 builder 常见错误是「直接进入 tutorial 模式」——缺娱乐外壳,完播率崩,算法不推。**必须把 utility 内容包裹在娱乐/故事/反差骨架里**。

### `built_app_business_segments`

**SaaS / AI Tool**
- 核心受众:22-35 岁 solopreneur / creator / early-career pro(自己就是 TikTok 高频用户)
- 触达机会:#BuildInPublic / #IndieHacker / #AITools / #ProductivityTok 等 niche 社群 + trending audio 借势
- 挑战:**TikTok Shop 目前不支持 SaaS/digital 类 direct-checkout**(仅实物 + 部分 digital),SaaS 只能引流至 bio link → landing page,漏斗多一步转化成本较高
- **机会点**:AI 工具 demo 类("watch this AI do X in 15s")是 2024-2026 最稳的 SaaS TikTok 内容 pattern,与 X/Twitter 的 AI demo 生态互补

**Ecommerce**
- 核心受众:视觉与故事驱动买家(fashion / beauty / home / food / gadget / gift);skew 女性 25-34
- 触达机会:**TikTok Shop 直接闭环**——从 discovery 到 checkout 不出 app,是 2024-2026 电商增长第一渠道
- **关键机制**:UGC + 微影响者 + Shop 三位一体——单个 nano/micro influencer 视频可带出单品 $20K+ GMV(常见于美妆/家居)
- 挑战:高 CAC 品类需要靠**多样本(50-200 条 UGC)**才有稳定爆款率,不能靠单一品牌自制内容

**Creator(独立开发者 / indie hacker / solo builder / knowledge creator)**
- 核心受众:同类 builder + 潜在早期用户 + 想学"如何做 X"的观众
- 触达机会:**Build-in-public + AI/tech niche + edutainment** 三条主线;#IndieHacker / #BuildInPublic / #TechTok / #FinTok 等 niche tag 生态
- **挑战**:Creator 类在 TikTok 比在 X/Twitter 更难做——TikTok 用户不习惯"文字驱动的思考类内容",Creator 必须找到"可视化 vibe"(如屏幕录制 + facecam + 快剪 + 声音 hook)。**不能把 X thread 简单转成 TikTok**
- **机会点**:2024-2025 兴起的 **"CEO of X" / "Founder day-in-life"** 短视频形式(即使账号只有几百粉)已被证明在 TikTok 有独特红利

---

## §3 算法机制(核心)

### `distribution_model`
**TikTok 是 4 大主流平台中最纯粹的「推荐流」平台**——分发几乎 100% 由算法决定,follower graph 只是次级信号 [来源: TikTok Newsroom "How TikTok recommends content" 2020 / 官方多次公开重申至 2025]。

分发的宏观逻辑:
- **For You Page(FYP)**:面向所有用户的算法推荐流,~90%+ 的观看发生在这里
- **Following**:关注流,权重远低于 FYP;即使是死忠 follower 也主要在 FYP 遇到你
- **Search / Discover**:结合关键词 + trending tag + FYP 数据的搜索面
- **Live**:独立分发系统,与短视频算法解耦

### `ranking_signals`

**TikTok 官方公开 + 行业交叉验证的 Top signals(2024-2025 稳定口径)**:

| Signal | 权重级别 | 说明 |
|--------|---------|------|
| **Watch time / 完播率** | ⭐⭐⭐⭐⭐ | 最强信号。**≥85% 完播是所有 signal 中最锐利的 unconnected reach 触发器**(与 IG Explore 的 95% 完播门槛类似但更宽松) |
| **Rewatches** | ⭐⭐⭐⭐⭐ | **TikTok 独有的高权重信号**——同一视频观看多次是"高价值"的极强证明;是 loop/hook 设计的核心目标 |
| **Shares / Sends** | ⭐⭐⭐⭐ | 与 IG 的 "sends per view" 逻辑一致,share 权重系统性 > save > like |
| **Comments** | ⭐⭐⭐ | 权重稳定,尤其 **user-to-user comment 对话**(不只是与创作者对话)是 quality signal |
| **Follows post-view** | ⭐⭐⭐ | 看完关注 → 高价值 conversion 信号 |
| **Profile visits** | ⭐⭐⭐ | 看完点头像去主页,indicator of interest |
| **Likes** | ⭐⭐ | 权重最低的正向信号(与 IG 相反)——like 门槛太低 |
| **Skip / Scroll-past ratio** | ⭐⭐⭐⭐(负) | 强负信号,决定视频能否被推给下一批 audience |

**"Interest signals" 详解**(TikTok 官方分层公开):
- **Video information**:captions / sounds / hashtags / effects 用于 topic classification
- **User interactions**:用户历史 like/share/follow/completion,决定用户被推什么
- **Device / account settings**:语言、地域、设备类型(权重较低)

### `content_type_priorities`

**TikTok 只有一种主要内容类型:垂屏视频**——不像 IG 有 Feed/Reels/Story/Carousel 分化。但视频**时长**是关键分层维度:

| 时长档 | Sweet spot | 分发倾向 | Atoms 推荐场景 |
|--------|-----------|---------|---------------|
| **7-15s** | 15s | 娱乐/meme/trend——爆款率最高,但转化差 | trend piggyback(借势) |
| **21-34s** | **27-30s** | **完播率最高的黄金区间**(实测多份报告一致) | Atoms 默认首选 |
| **35-60s** | 45s | 教程/故事——完播率下降但 dwell 高,share 强 | tutorial / storytime |
| **1-3min** | — | 深度内容——完播率显著下降,但对高意图 audience 转化强 | deep dive / product demo |
| **3-10min** | — | 2024-2025 开放上限,但**主流 FYP 分发仍偏爱 <60s** | 谨慎使用,除非有明确 topic 优势 |

**为什么 21-34s 是 sweet spot?**——完播率与信息密度的最优平衡:
- 短于 15s:信息密度不足,rewatch 低
- 长于 60s:完播率断崖式下降

**Atoms playbook 硬默认**:除非有明确理由,视频长度默认 **21-34s**;超 45s 需在生成时给出"为什么这条需要更长"的判断。

### `engagement_window`

**关键窗口:发布后 1-3 小时决定 baseline,24-72 小时决定是否触发「viral momentum」,7-14 天决定「long tail」是否延续**。

TikTok 与 IG 的关键差异:
- IG 内容的"生命周期"通常 24-72 小时结束
- **TikTok 内容有 7-30 天甚至更长的 long tail**——一条视频发布 3 周后突然被算法再次推入 FYP 并二次爆发,是 TikTok 独有现象 [来源: SocialInsider 2026 TikTok Report / 多个 case study]

**Playbook 生成机制**:
1. **爆款接续机制**:与 IG 类似,单条 views 超过账号中位 3x 时,48h 内接续一帖同 topic/format
2. **Long tail 待机机制**:发布 2-3 周后如某条被二次推,应立刻用同 topic 再发一条 → 承接算法二次给的临时权重
3. **Trending sound 时效性**:借势 sound 的窗口通常 3-7 天,超过后 signal 迅速衰减

### `algo_penalties`

- ⚠️ **带水印跨平台搬运**(尤其从 IG Reels 直接搬)——TikTok 明确降权,官方多次警告
- ⚠️ **Community Guidelines 违规**——即使是软违规(dangerous acts / misleading claims / 未标注 sponsor)也会导致 FYP 屏蔽
- **Engagement bait / clickbait 明确降权**——"comment below if..." 类过度诱导,2024 起模型识别度显著提高
- **AI 生成内容未标注 disclosure**——2024 起 TikTok 要求 realistic AI content 必须标注,未标注可能被限流
- **重复内容**——同一素材(即使剪辑变化)多次发不会被推,需真实新素材
- **静音视频**——TikTok 是 sound-first 平台,无背景音/无 voice 的视频 baseline 分发显著较低
- **Excessive text overlay**——超过 30-40% 屏幕面积的文字会降低视觉信号,建议 text 集中在前 3s
- **Shadowban 风险**:多次报告 / spam-like 行为触发,可视性静默下降,无通知

### `recent_changes`(近 12-18 个月)

| 变更 | 时间 | 说明 | Playbook 含义 |
|------|-----|------|--------------|
| **视频时长上限扩至 10 分钟** | 2022-2024 逐步开放 | 上限已到 10min,60min 长视频测试中 | 硬默认仍 21-34s;长视频仅在"深度价值 + 高意图 audience"时使用 |
| **TikTok Photo Mode / carousel** | 2023-08 | 支持多图 + 文字轮播 | 目前对 FYP 权重远低于视频,不作为 Atoms 首推格式 |
| **AI Content Labels** | 2024-05 | Realistic AI content 需标注 disclosure | 未标注可能被限流;Atoms 生成 AI 视频建议默认加 label |
| **Creator Search Insights** | 2024-Q3 | 官方提供搜索热词工具 | 增加 SEO 层机会(见 §6) |
| **TikTok Shop 美国扩张** | 2023-09 起 | 直接闭环购物 | ecommerce 类 builder 分发-转化通路缩短;SaaS/digital 暂不支持 |
| **Symphony Creative Studio** | 2024-06 | TikTok 官方 AI 视频生成套件 | 观察其对 organic content 生态的长期影响;Atoms 不依赖但可辅助 |
| **Series(付费订阅内容)** | 2022-2024 | 长内容付费墙 | 对 Creator 类可能是变现渠道,但 Atoms builder（应用创建者）暂不作为主推 |
| **US divest-or-ban timeline** | 2024-04 立法 → 多次延期 | 美国市场分发存在结构性风险 | 建议纯美国依赖 builder 建立多渠道 backup |

---

## §4 内容格式规格

### `post_types`

TikTok 支持的完整内容类型:

| 类型 | 位置 | 主要用途 | Atoms 推荐权重 |
|------|-----|---------|---------------|
| **短视频(<60s)** | FYP + Profile + Following | 冷启动 + 长期主体 | ⭐⭐⭐⭐⭐(首选) |
| **中视频(1-3min)** | 同上 | 教程 / storytime / demo | ⭐⭐⭐ |
| **长视频(3-10min)** | 同上 | 深度内容 / podcast clip | ⭐⭐(谨慎) |
| **Photo Mode / Carousel** | FYP + Profile | 图文教程 / product showcase | ⭐(FYP 权重低,仅辅助) |
| **Story(24h)** | 顶部 tray | 日常 / behind-scenes | ⭐⭐(daily,类似 IG Stories) |
| **Live** | Live tab + Following | Q&A / product Live-selling | ⭐⭐(ecom 类可高频,其他偶尔) |

### `dimensions_and_ratios`

**硬性尺寸/时长要求**(截至 2026-07):

| 类型 | 宽高比 | 尺寸推荐 | 时长 | 硬规则 |
|------|-------|---------|------|-------|
| **Short-form Video** | 9:16(唯一推荐) | 1080×1920 | 7s-10min | **默认 21-34s;超 45s 需明确理由** |
| **Photo Mode** | 9:16 或 1:1 | 1080×1920 | — | 2-35 张图 |
| **Story** | 9:16 | 1080×1920 | 单帧 ≤15s | 24h 自动过期 |

**关键点**:
- **1:1 或 16:9 视频在 TikTok 是严重反模式**——上下留黑边/白边被算法识别为搬运,直接降权
- **音频不可缺失**——即使是无 voice 内容,也必须有 BGM 或 trending sound
- **文件上传上限**:单视频 ≤500MB;推荐编码 H.264 / MP4

### `caption_length_recommendation`

**核心原则**:TikTok caption 长度硬上限 2200 字符(2022 前 300)——但**实际最优 100-200 字符**。Caption 不承担讲故事职责,故事在视频里。

| 内容类型 | 建议长度 | 结构 |
|---------|---------|------|
| **Entertainment / Trend** | 极短(<80 字符) | 一句 hook + 1-3 tag |
| **Tutorial / How-to** | 短-中(100-200 字符) | Setup hook + payoff hint + tag |
| **Storytime / POV** | 短(<150 字符) | Hook + emotion cue + tag |
| **Product-focused** | 中(150-250 字符) | Hook + benefit + CTA + tag |

**Caption 双重角色**:
1. **SEO 层**:TikTok 2024 起明确将 caption 作为 search ranking 主要信号——**关键词必须自然嵌入 caption 前 100 字符**(而不是全放 hashtag)
2. **Comment 引导层**:好的 caption 直接激发评论(问句 / 反问 / 微争议观点)

### `hashtag_capacity`

**硬规则**:
- **总数无 platform-enforced 上限**(不同于 IG 2025 的 5-tag cap)
- **实测最优:3-5 个**——超过 8 个 signal 稀释,可能被判 spam
- **组合策略**:1-2 trending large tag(1M+ views)+ 2-3 niche mid-tag(10K-500K views)+ 1 branded 或 signature tag(见 §6 详细策略)

### `link_and_cta_rules`

- **Bio link**:所有账号可添加 1 个可点击 bio link(2024 起门槛下降至 0 followers);可用 Linktree / Beacons 聚合
- **视频内不可放可点击外链**——URL 明文写在 caption 里也不可点(与 IG 一致)
- **TikTok Shop link**(仅特定类目,主要实物商品):视频内可直接挂产品,一键跳转结算
- **Live 商品挂链**:Live 中可挂产品链接,ecommerce 类关键通路
- **DM 引导**:视频 CTA 引导「comment 关键词 → 我 DM 你」是 SaaS/Creator 类主流做法
- **TikTok Stories link**:目前对 verified / high-follower 账号开放,门槛尚未完全下沉

### **§4 Atoms 硬规则汇总**(生成 TikTok 内容时的 must-follow)

1. **视频长度默认 21-34s**——超过 45s 需明确理由
2. **必须 9:16 垂屏**——1:1 / 16:9 上传会被降权
3. **前 1-3s 必须有 hook**(视觉 + 声音双 hook,不能只是文字)
4. **视频必须有音频**(voice / BGM / trending sound 至少一项)
5. **关键词自然嵌入 caption 前 100 字符**(SEO 信号,不是靠 hashtag)
6. **Hashtag 3-5 个**(1-2 trending + 2-3 niche + 1 branded)
7. **禁跨平台带水印搬运**(尤其从 IG Reels)
8. **AI 生成 realistic content 需加 disclosure label**(2024 起官方要求)
9. **视频结尾必须有 loop 意图**(为 rewatch 埋点——见 §9)
10. **Bio link 必设**——TikTok Shop 之外唯一 organic 引流通路
11. **每条视频至少埋 1 个 comment hook**(问句 / 反差 / 争议点,激发 user-to-user comment 对话)
12. **静音上传是死刑**——即使是 screen recording 也要加 voiceover 或 BGM

### **§4 Brand-Size 分层格式配比**

| Tier | Regime | 目标 | 主要格式 | 配比建议 |
|------|--------|------|---------|---------|
| **Tier 1: 0-10K**(Atoms builder（应用创建者）主体) | 冷启动 + FYP 试错 | **短视频 21-34s** 打爆款率 | 短视频 90% / Photo Mode 5% / Story daily / Live 偶尔 | 目标:每 20-40 条产出 1 个爆款(views > 账号中位 5x) |
| **Tier 2: 10K-100K** | 建立 niche + 复用高转化模板 | 短视频 + 中视频 | 短视频 70% / 中视频 20% / Photo Mode 5% / Live 每周 1-2 | 目标:爆款率提升到 1/10,单条 average view 稳定 |
| **Tier 3: 100K+** | Product-led + 转化优化 | 全格式 + Shop/Live | 短视频 60% / 中视频 20% / Photo 5% / Live 每周 3-5(ecom) | 目标:视频 → external CTR(或 Shop GMV)持续增长 |

**注意**:Atoms builder（应用创建者） 90%+ 处于 Tier 1,playbook 默认按 Tier 1 生成——**核心 KPI 是"爆款率"而非稳态 view count**。

---

## §5 调性关键词与语言风格

### `tone_descriptors`

TikTok 平台调性 8 个关键词:

1. **Raw / Native**(粗糙原生,反工艺化)
2. **Entertainment-first**(先娱乐,再传递信息)
3. **Fast-paced**(节奏快,前 1s 抓人)
4. **Sound-driven**(声音主导,不只是画面)
5. **Trend-aware**(踩节奏借势,不做绝对原创)
6. **Vulnerable / Real**(创作者本人露脸 + 真实情绪 > 品牌 voice)
7. **Community-native**(用垂类社群黑话,不做 outsider)
8. **Loop-designed**(视频结构鼓励 rewatch)

**与 IG 的对比**:IG = aspirational / polished / community-driven;**TikTok 是几乎完全相反的方向**——越像广告越死,越像朋友随手拍越活。

### `voice_do`

1. **说人话**:口语化 / 断句短 / 有节奏感,像跟朋友说话
2. **前置反差或悬念**:第一句就是 pattern break("Nobody told me that..." / "I tried X for 30 days and...")
3. **有观点**:表达明确态度(哪怕是"我觉得")比中立客观 recap 强得多
4. **主动互动 cue**:"tell me in the comments" / "which one are you" / "am I the only one who..."
5. **借 trend 但加个人角度**:纯模仿 trend 不涨粉,加个人 remix 才有 signature

### `voice_dont`

1. **不要企业腔**:"we are excited to announce" / "our team is thrilled" —— TikTok 上是 death sentence
2. **不要过度 CTA**:"click the link!" / "buy now!" —— 明确降低完播
3. **不要用广告文案模板**:feature list / benefit bullets —— 立刻被识别为 promo
4. **不要"完美结尾"**:cleanly wrap 的视频反而 rewatch 低,应留 open loop(见 §9)
5. **不要长开场铺垫**:任何超过 2s 的 setup 都在被 skip

### `emoji_and_emphasis`

- **Emoji**:比 IG 用得**少**——TikTok caption 是 SEO 层,过多 emoji 稀释关键词权重;推荐 0-2 个,精挑
- **大小写强调**:全大写单词偶尔用于强调("this is INSANE"),但不密集
- **换行**:caption 短,通常 1-2 行,不做视觉排版
- **Text overlay**:视频内文字覆盖非常关键,但集中在前 3s 的 hook + 关键 payoff moment;超过 30-40% 屏幕面积会显得杂乱
- **字体选择**:TikTok native fonts(Classic / Serif / Neon / Handwriting)是被算法识别为原生的隐藏信号,第三方剪辑 App 的字体会显得像搬运

### `hook_patterns`

**Atoms 内容生成的 6 种标准 hook 模板**(前 1-3s 必用其一):

1. **反常识断言**:"Nobody talks about how X is actually..."
2. **数字承诺**:"3 things I wish I knew before..." / "I did X for 30 days"
3. **反差 / Before-After**:视觉直接对比(前 0.5s 展示 before,0.5-1s 展示 after)
4. **POV 代入**:"POV: you just discovered..." / "You when..."
5. **悬念 / open question**:"Wait, did you know that..." / "This is why X..."
6. **争议 / Take**:"Hot take: X is overrated" / "Unpopular opinion:..."

**核心原则**:前 3s 的 hook 是**视觉 hook + 声音 hook + 文字 hook 三层同时到位**;缺任何一层完播都会掉。

---

## §6 Hashtag 策略

### `optimal_count`

**3-5 个,超过 8 个 signal 稀释**——TikTok 无 IG 那种 5-tag hard cap,但实测最优区间稳定在 3-5 [来源: SocialInsider 2026 / Later 2025 交叉]。

### `mix_strategy`

**5-slot portfolio 框架**(与 IG 类似但组合逻辑不同):

| Slot | 类型 | 目标 | 示例 pattern |
|------|-----|------|-------------|
| 1 | **Trending large tag**(1M-100M+ views) | 借势曝光 | #FYP / #ForYou / #TikTokMadeMeBuyIt(仅 ecom) |
| 2 | **Niche mid-tag**(10K-500K views) | 主分类信号 | #BookTok / #CleanTok / #BuildInPublic / #AITools |
| 3 | **Niche mid-tag**(同上) | 二级分类 | 更细的垂类,如 #ProductivityHacks / #IndieMaker |
| 4 | **Long-tail small tag**(<10K views) | 精准 audience | 具体产品名 / 具体主题 |
| 5 | **Branded tag**(账号 signature) | 长期资产 | 品牌自建 tag,配合 series 内容 |

**避免的组合**:
- ❌ 全部 mega tag(#FYP + #ForYou + #Viral)—— 分类价值 ≈ 0,被判 gaming
- ❌ 全部 mid-niche —— 缺 discovery 层
- ❌ 与内容无关的 trending tag —— 主动损害 classification

### `research_method`

**Atoms 生成 hashtag 的 3 步方法**:

1. **确认 core niche tag**——从账号历史 3-5 条高转化视频反查其 tag 组合
2. **借 Creative Center 找 trending**——https://ads.tiktok.com/business/creativecenter → Trending → Hashtags,按行业/地域过滤;取当前周 rising tag 1-2 个
3. **长尾 tag 从 comments 反查**——目标 audience 在类似视频下的 comment 里用哪些自然 tag/短语

**TikTok SEO 补充层**(2024 起权重上升):
- 关键词自然嵌入 **caption 前 100 字符**(不只是 hashtag)
- 关键词嵌入 **text overlay** 与 **voiceover**(TikTok ASR 转录 → 可搜索)
- **Creator Search Insights**(2024-Q3 官方工具)可查询热门搜索词

### `banned_or_risky`

- ⚠️ 与内容完全无关的 mega tag(如内容是 SaaS demo 却挂 #dance / #comedy)——降权风险高
- ⚠️ Community Guidelines 敏感领域 tag(未成年 / 医疗 / 金融投资建议等)——严格审查
- ⚠️ Deprecated / merged tag —— TikTok 会定期合并同义 tag,过时 tag 无 reach
- ⚠️ Spam-like pattern(每条视频重复 30+ tag)—— 触发限流

---

## §7 发布节奏与频率

### `best_posting_times`

**基于 SocialInsider 2026 + Hootsuite 2026 交叉验证的 US audience 时段**(时区 UTC-5 EST,可按目标地域偏移):

| 时段 | 强度 | 说明 |
|------|-----|------|
| **平日 6-10 AM** | ⭐⭐⭐⭐ | 通勤/晨间刷 TikTok 高峰 |
| **平日 6-10 PM** | ⭐⭐⭐⭐⭐ | 单日最强时段,晚间 wind-down |
| **平日 12-3 PM** | ⭐⭐⭐ | 午休时段,次高峰 |
| **周末 9 AM-12 PM** | ⭐⭐⭐⭐ | 周末晨间 |
| **周末 7-11 PM** | ⭐⭐⭐⭐ | 周末夜间 |

**关键提醒**:TikTok 的 FYP 分发机制让"最佳时段"重要性**低于 IG 与 LinkedIn**——即使发在低谷时段,算法仍会在后续几天内持续测试并推送。**"发得对"远比"发得对时间"重要**。

### `default_timezone`

上述时段默认 UTC-5 EST(美国东部)——覆盖美国主要市场。若 builder 目标市场为其他地域,应相应偏移(如欧洲 UTC+0/+1;亚洲 UTC+8)。

### `frequency_recommendation`

| 阶段 | 频率 | 理由 |
|------|-----|------|
| **冷启动(0-1K)** | **1-3 条/天**,持续 30-60 天 | FYP 需要数据点才能匹配 audience;高频是唯一冷启动加速手段 |
| **稳态(1K-100K)** | **1 条/天** 或 **5-6 条/周** | 保持算法权重,允许每条精修 |
| **成熟(100K+)** | **3-5 条/周** | 质量优先,每条精心策划 + 高转化模板复用 |
| **Story** | Daily(如条件允许) | 与 followers 保持接触,不占 FYP 分发权重 |
| **Live** | Ecom 类 3-5 次/周;其他 1-2 次/月 | Live 是独立分发,不与短视频竞争权重 |

**关键对比**:
- IG 稳态推荐 4-5 posts/week(SocialInsider 2026)
- **TikTok 稳态推荐 5-7 posts/week**——高于 IG,反映 FYP 分发对"投递量"的依赖

### `first_week_ramp_up`

新账号 / 冷启动阶段(与稳态期差异明显):

1. **前 7 天**:每天发 1-3 条,同 niche,同 hook pattern 变体——目标是让 FYP 快速识别账号 topic
2. **前 30 天**:累计 30-60 条视频——FYP 需要充足样本来"训练"你的 audience match
3. **不要过早换 topic**——冷启动阶段横跳 topic 会让算法无法定位,分发效率显著下降
4. **每 5-7 条视频复盘**——找出 top 1-2 条,复制其 hook / 时长 / 音频 pattern,并测试变体
5. **前 2 周不追求 followers**——追求单条 view 突破 1K 起步,然后 10K,然后 100K

---

## §8 业务类型 × 平台适配

### 8.1 SaaS / AI Tool

- **`fit_score`**:**3/5** —— 有独特红利(AI demo / build in public),但转化路径长(bio link → landing → signup),且不支持 Shop 闭环
- **`content_angles`**
  1. **AI/product demo**:"Watch this AI do X in 15s" —— 2024-2026 最稳的 SaaS TikTok pattern
  2. **Behind-scenes / build in public**:"Day X of building [product]" —— 与 Twitter build-in-public 生态互补
  3. **User pain → aha moment**:"POV: you tried [manual way] vs [tool]"
  4. **Tutorial / hack**:利用 tool 完成一件观众关心的事(不主推 tool 而主推结果)
- **`visual_style`**:screen recording 打底 + facecam corner + 快剪 + trending sound;避免纯屏幕录制(缺人格)
- **`caption_focus`**:关键词自然嵌入前 100 字符 + 一个明确 payoff hint("built this in a weekend" / "no code needed")
- **`cta_style`**:"link in bio to try free" / "comment [关键词] and I'll DM you" —— 避免"buy now"
- **`common_traps`**
  - ❌ 直接进 tutorial mode,缺娱乐外壳 → 完播低,不推
  - ❌ 拍成 product marketing video(feature list / logo shot) → 立刻被识别为广告
  - ❌ 期望 follower growth 转化 → SaaS 的 KPI 应是 external CTR + signup,不是 follower

### 8.2 Ecommerce

- **`fit_score`**:**5/5** —— TikTok Shop 闭环 + UGC 生态 + 短视觉品类天然适配
- **`content_angles`**
  1. **Product-in-use / demo**:真实使用场景,反工艺化
  2. **UGC 转发 + reaction**:找 micro-influencer(1K-50K)真实 review
  3. **"TikTok made me buy it"** trend piggyback
  4. **Unboxing / haul**:观众高情绪投入的经典 format
  5. **Before-after transformation**:美妆/家居/健身品类必选
- **`visual_style`**:真实场景 + 手持感 + 自然光 > 影棚级制作
- **`caption_focus`**:产品名 + 场景关键词(SEO)+ 情绪 hook + 1 个 comment cue
- **`cta_style`**:视频内直接挂 TikTok Shop 链接(如支持)/ "link in bio" / "comment PRICE for the link"
- **`common_traps`**
  - ❌ 品牌自制"广告感"视频 → 完播差,不如批量 UGC
  - ❌ 只做单产品单视频 → 应该同一产品 20-50 个不同 angle 变体
  - ❌ 忽视 comment 中的问题 → TikTok comment 是二次销售场,回复率是转化关键

### 8.3 Creator(独立开发者 / knowledge creator)

- **`fit_score`**:**3.5/5** —— Build in public + edutainment 有红利,但 Creator 类内容需要"可视化 vibe"能力
- **`content_angles`**
  1. **Build in public**:show progress(截图 + facecam + voiceover)—— 建立"看你成长"的粉丝粘性
  2. **Founder day-in-life**:即使账号只有几百粉,day-in-life 类是低门槛高潜力
  3. **"I built X with Y"**:公开分享 tech stack / process,吸引同类 builder + 潜在早期用户
  4. **Edutainment(教育 + 娱乐)**:硬核知识 + 娱乐外壳(反差 hook + fast-paced)
  5. **Reaction / stitch**:回应 trend / 他人视频,借势拓宽 audience
- **`visual_style`**:facecam + screen recording split + 快剪 + 手写 doodle overlay(增加"手作感")
- **`caption_focus`**:观点鲜明 + 关键词 SEO + comment hook(诱导争论/追问)
- **`cta_style`**:"follow for part 2" / "comment [关键词] for the [resource]" —— TikTok 上比"link in bio"更有效
- **`common_traps`**
  - ❌ 把 X thread 简单转成 TikTok 语音朗读 → 视觉贫瘠,完播差
  - ❌ 试图在 15s 内讲复杂概念 → 应该拆成 series
  - ❌ 缺 signature 视觉/hook pattern → Creator 类粘性靠"可识别的 vibe"

---

## §9 高转化模式(样本归纳,非案例引用)

### `sample_size_and_source`

**归纳基于**:
- Category B 博客案例 20-30 条(计划 P1.3-P1.4 补齐,数据存 `references/research-data/tiktok/case_studies.json`)
- TikTok Creative Center 公开 Top Ads / Trending Sounds 每 2-4 周快照,存 `.cache/social_intel/manual/tiktok/{region}/{language}/{YYYY-Www}/creative-center.json`
- Atoms builder（应用创建者）人工补齐 10-20 条(vibe coding SMB 类样本,存 `references/research-data/tiktok/manual_supplements.md`)

**当前版本(v0.1)结构框架来源**:SocialInsider 2026 TikTok Benchmark + Hootsuite 2026 Algorithm + Later 2025 TikTok Strategy + Buffer TikTok case studies 交叉。

### `winning_structures`

**5 种反复验证的高转化结构骨架**(不含具体品牌/文案):

1. **Broken Hook**(悬念断裂式):
   - 0-1s:视觉/声音强反差("Wait, this shouldn't work..." 配合 unexpected visual)
   - 1-5s:setup(展示 unexpected setup)
   - 5-25s:payoff(揭示为什么可行)
   - 结尾:open loop 或问题("But this raises another question...")→ 引出下一条

2. **Before-After Transformation**:
   - 0-1s:before 状态(视觉/情绪低点)
   - 1-2s:清晰的 transition 视觉信号
   - 2-25s:process(show don't tell)
   - 25-30s:after 状态(视觉/情绪高点)+ CTA cue

3. **POV / Story 微剧**:
   - 0-2s:POV setup("POV: you just discovered...")
   - 2-15s:剧情推进(细节 + emotion)
   - 15-27s:reveal / punchline
   - 结尾:relatable 情绪落地 → 高 share

4. **List / Tutorial(3-step)**:
   - 0-3s:承诺("3 things I wish I knew...")
   - 3-25s:三个 step(每 step 5-7s,含 visual demo)
   - 25-30s:summary + CTA
   - 关键:每个 step 有独立的 mini-hook,避免中间脱落

5. **Loop-designed(为 rewatch)**:
   - 视频结尾自然接回开头(视觉/声音循环)
   - 观众看完自动开始第二遍(rewatch = TikTok 独有高权重信号)
   - 常见于 satisfying content / ASMR-adjacent / process video

### `visual_patterns`

- **前 0.5s 视觉必须"不同于普通 scroll"**——通过颜色、镜头运动、意外元素、字体等
- **快剪节奏**:平均镜头 <2s,越快 dwell 越高(但不能过快导致混乱)
- **Text overlay 只放关键信息**——不复述 voiceover,只补充/强调
- **色调 native TikTok**:略过饱和 / 高对比 / 手机原生质感 > 专业色彩校正
- **Face + screen split**——SaaS / Creator 类的黄金搭配(人格 + 内容)
- **Trending sound + native visual = 算法双信号触发**

### `engagement_triggers`

反复驱动 shares / rewatches / comments 的元素类型:

1. **可 relatable 的情绪 punchline**(为 share)
2. **反常识观点或 hot take**(为 comment 争论)
3. **信息密度高的 list / tutorial**(为 save / rewatch)
4. **视觉 satisfying / loop 结构**(为 rewatch)
5. **明确的 comment hook**("which one are you" / "am I the only one who...")
6. **数字承诺 + 结果展示**("30 days of X → this happened")
7. **借势 trend + 个人 remix**(为算法信号 + 差异化)
8. **Series / cliffhanger**("Part 2 tomorrow"/"tell me if I should do X next")

---

## §10 避坑清单 + 数据源

### `avoid_list`

**按严重程度排序**(shadowban > 降权 > 转化差 > 观感差):

1. ⛔ **Community Guidelines 违规**(即使轻微)—— shadowban 风险
2. ⛔ **多账号 spam / 自动化行为** —— 严重 shadowban 风险
3. ⚠️ **带水印跨平台搬运**(尤其从 IG Reels)—— 明确降权
4. ⚠️ **AI realistic content 未标注 disclosure**(2024 起要求)—— 限流风险
5. ⚠️ **Engagement bait 明显模板**("comment YES if...")—— 降权
6. ⚠️ **静音上传**(无 voice / 无 BGM)—— baseline 分发差
7. ⚠️ **1:1 或 16:9 尺寸**(非 9:16)—— 被识别为搬运,降权
8. ❌ **企业腔文案 / 品牌 voice**——完播率崩,不推
9. ❌ **过度制作 / 影棚级 look**——被识别为广告,skip 率高
10. ❌ **超过 45s 无强理由**——完播率下降,分发衰减
11. ❌ **前 3s 无 hook 直接进内容**——skip 率高
12. ❌ **caption 全塞 hashtag 无关键词**——SEO 分数低,搜索找不到
13. ❌ **重复上传同素材**——不会被推
14. ❌ **单一 CTA 类过度堆叠**("Buy!" "Click!" "Follow!")——降低完播

### `references`

**行业博客与 benchmark 报告**(Category B):
- SocialInsider — TikTok Organic Engagement Benchmarks 2025-2026 — https://www.socialinsider.io/blog/tiktok-benchmarks/
- Hootsuite — TikTok Algorithm 2026 — https://blog.hootsuite.com/tiktok-algorithm/
- Later — TikTok Marketing Strategy 2025 — https://later.com/blog/tiktok-marketing/
- Buffer — TikTok Growth Case Studies — https://buffer.com/resources/tiktok-case-studies/
- RivalIQ — TikTok Benchmark Report 2025 — https://www.rivaliq.com/blog/tiktok-benchmark-report/
- Sprout Social — TikTok Statistics 2025 — https://sproutsocial.com/insights/tiktok-stats/

**TikTok 官方**(Category C):
- TikTok Creative Center — https://ads.tiktok.com/business/creativecenter (Trending hashtags / sounds / top ads,公开可访问)
- TikTok Newsroom — How TikTok recommends content — https://newsroom.tiktok.com/en-us/how-tiktok-recommends-content
- TikTok For Business — Creative Best Practices — https://www.tiktok.com/business/en/blog
- TikTok Creator Portal — https://www.tiktok.com/creators/creator-portal/

**详细 URL 与检索路径**:见 `references/research-data/tiktok/industry_urls.txt`(结构化 URL 池)+ `scripts/search_queries.md`(TikTok 章节)

**动态数据快照**:
- Trending sounds / hashtags / top ads 每 2-4 周从 Creative Center 刷新 → `.cache/social_intel/manual/tiktok/{region}/{language}/{YYYY-Www}/creative-center.json`
- 案例样本增量 → `references/research-data/tiktok/case_studies.json`
- 人工补齐样本 → `references/research-data/tiktok/manual_supplements.md`

### `next_review_date`

- **算法机制(§3)+ 内容格式(§4)+ 业务适配(§8)**:2027-01-02(6 个月强制复核)
- **调性(§5)+ Hashtag(§6)+ Winning structures(§9)**:每 2-4 周结合 `.cache/social_intel/manual/tiktok/{region}/{language}/{YYYY-Www}/creative-center.json` 增量刷新;每 3 个月做完整章节复核

---

## §11 待补齐(v0.2 目标)

**素材待补**:
- §9 winning structures 需 20-30 条 Category B 博客案例 + 10-20 条人工补齐样本
- §6 hashtag pool 需首次 Creative Center 快照(初次抓取后进入 2-4 周刷新节奏)
- §8 各业务类型需 5-10 条 vibe coding SMB 匹配的具体案例

**v1.0 门槛**:需要 TikTok 官方文档交叉验证(algorithm / policy 章节)+ 40-60 条案例样本 + 至少 3 次 trending snapshot 迭代验证。

---

*maintained by: atoms-social-marketing skill maintainer | 数据管道见 `scripts/README.md` TikTok 章节*

