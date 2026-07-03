---
name: youtube-playbook
platform: youtube
version: 0.1
last_updated: 2026-07-02
data_freshness_note: 平台机制与格式规则基于 2024-2026 官方公开信息(Google/YouTube Blog、Creator Insider 官方频道、Think with Google、YouTube Data API v3 文档)+ Category B 行业分析(Tubebuddy / VidIQ / Backlinko / Hootsuite 2026 Report)。核心 hard rules(Shorts ≤ 3min、CTR & AVD 首要信号、Description 前 100 字符规则)短期不会变;算法微调可能季度性发生,尤其 Shorts 独立算法与 AI 内容政策条线。
review_by: 2027-01-02
sources_summary: YouTube 官方(Blog / Creator Insider)+ Data API v3 结构性支持(直接抓取公开元数据可用,与 IG 关键差异) + Category B 行业博客待补齐(Backlinko / VidIQ / Tubebuddy 2025-2026 分析)。§5-§10 需 Category B 研究补齐,scripts/youtube_search_queries.md 已就位。
---

# YouTube Playbook

> **服务对象**:Atoms 用户所构建应用的 YT 社媒运营(冷启动 discovery + 长期 authority build)
> **规模假设**:Atoms 用户 90%+ 处于 0-1K subscribers,playbook 分级建议默认按此校准。到 1K/4K watch hours(YPP 门槛)或 10K subs 时切换到更高 tier 打法(见 §4 / §7 / §9)
> **关键差异 vs IG**:YouTube 是**搜索 + 会话双引擎平台**,不是纯推荐 feed。SEO(title / description / thumbnail)权重 ≥ 单条 engagement——**这个基本事实决定了 YT playbook 与 IG playbook 结构上的最大差异**。

---

## §1 平台定位与核心用户

### `platform_name`
YouTube(Alphabet/Google 系,与 Google Search、Google Ads、Chrome 数据打通)

### `elevator_pitch`
YouTube 是全球**第二大搜索引擎**(仅次于 Google Search)+ **最大长视频平台** + **Shorts 双引擎**。核心角色是**「搜索意图 + 会话 watch time 双驱动的深度学习/娱乐/评估层」**——用户来这里主要做三件事:学一个技能、评估一个产品、消磨一段完整时间。YT 不是纯 top-of-funnel(用户会主动搜),也不是纯 bottom-of-funnel(购买决策前会来看第三方 review)。**对 Atoms 用户,YT 是最强的「demo + 教程 + 品牌信任」承载层**。

### `mau_and_geography`
- 全球 MAU:2.5B+ logged-in monthly(YouTube Press 官方 2024)+ 数亿匿名浏览
- 主要地域:美国 / 印度(2 亿+ 用户,YT 最大市场) / 巴西 / 印尼 / 日本 / 德国 / 英国前七
- YT 是**唯一同时具备「全球 reach + 精细语言字幕/dubbing」**的社媒平台;YouTube 自动翻译字幕 + 2023-2024 起 AI dubbing(通过 Aloud → Creator Music 系)已覆盖 8+ 语种 [来源: Google Blog "Aloud", 2023]
- 用户结构:18-34 岁核心占约 50-55%(Pew Research 2024);**35-54 岁增长最快**;13-17 岁 US teens 中 **95% 使用 YT,更 15% 说 YT 是"最爱 app"**(Pew Research Teens & Tech 2023)

### `primary_use_cases`
1. **教育/教程消费**——YT 是全球最大免费教育平台;how-to / tutorial / DIY / dev 类占比最高
2. **产品评估与 review**——购买前 40-60% 用户会先看 YT review(Google Consumer Insights);unboxing / comparison / long-form review
3. **娱乐 & 消磨时间**——Shorts + long-form entertainment(vlogs / gaming / 讲故事)
4. **live 与社群参与**——Live streaming(gaming / podcast / 发布会)+ Community posts + Super Chat
5. **音乐消费**——YT Music 是全球第二大音乐平台(仅次 Spotify);背景音乐 + MV
6. **品牌信任层验证**——B2B/SaaS 采购决策链路里,YT 是"是否值得信任"的关键触点(比 IG 的 profile grid 权重更高,因为长视频承载 depth)

### `builder_relevance`

对 Atoms builder 的战略价值分为三层:

| 阶段 | YT 承担角色 | 关键动作 |
|------|-----------|---------|
| 0-1K subs | Discovery + 搜索意图接入 | **Shorts + 高搜索意图 how-to 长视频**;标题命中 keyword;缩略图 + hook 前 30s 决定生死 |
| 1K-10K subs | Authority build + 差异化 topic | 稳定 upload cadence(每周 1-2 支);建立可识别的 topic niche;chapters + description SEO |
| 10K+ subs | 商业化 + 长尾流量复利 | YPP 开启(广告分成);Shopping affiliates;老视频长尾流量;live + Community post 深化关系 |

**核心提醒**:YT 是**长尾流量复利 vs IG 短尾曝光**的结构性差异——一条优秀 how-to 视频可能连续 3 年持续带流量(通过 Search / Suggested 推荐),而 IG post 的 attention 窗口通常只有 48-72 小时。对 Atoms 用户,**YT 的 ROI 时间轴更长,但底层 SEO 投入更硬核**。

**YPP 门槛必须让 builder 知道(直接影响商业化预期)**:
- 标准通道:**1000 subs + 4000 有效公共观看小时(过去 12 个月)** [YouTube Help, 2024]
- Shorts 通道:**1000 subs + 1000 万 Shorts 观看数(过去 90 天)** [YouTube Help, 2024]
- 部分商业化通道(2023 扩展):500 subs + 3000 watch hours OR 300 万 Shorts views —— 可用 Super Thanks / Channel Memberships / Shopping,但不含广告分成
- Atoms 用户默认路径:先冲 subs + Shorts views,再解锁长视频广告分成

---

## §2 用户画像三视图

### `demographics`
- **年龄**:18-34 岁核心(约 50-55%);35-54 岁快速增长(2022-2024 各年 +10%+);**13-17 岁**是最活跃的 US teen 平台(Pew 2023:95% 使用,超过 IG 62% / TikTok 67%)
- **性别**:全球 5.4 男 / 4.6 女(YT 略偏男,与 IG 相反);游戏/科技/汽车/工具品类 skew 男;beauty/lifestyle/vlog 平衡或偏女
- **地域**:全球分布均衡,但**美国 / 印度**双龙头;印度是 YT 唯一"用户量 > 该国 Facebook + IG 合计"的市场
- **收入**:覆盖全收入段,但**长视频消费者(尤其教育/评估类)偏中产及以上**;Shorts 用户年龄更年轻、收入更宽

### `psychographics`
- **核心动机**——3 大主要:
  1. **「学一样东西」**(主动搜索,教程/how-to/教育占 YT 总观看时长的 top segment)
  2. **「评估一个决策」**(购买/工具选择/研究,长视频 review + comparison)
  3. **「消磨或放松」**(entertainment browse,Home 页 + Shorts 无终止 feed)
- **消费决策链路**(product research 场景):Search "X vs Y" → 长视频 review → creator profile 检查 → Description 里的 affiliate link / 官网 → 转化
- **反常识点 1**:YT 用户**不像 IG 用户随手 like/comment**——engagement rate 数字看起来低,但**session watch time + return visits 才是 YT 真正的 engagement metric**。行业惯性用 like/comment 衡量 YT 表现是错的。
- **反常识点 2**:**Shorts 与 long-form 是两套完全不同的用户心智**——同一个人在 Shorts 是 lean-back scroll,在 long-form 是 lean-forward learn。**同一 topic 分别为两种 mode 生产内容,不要试图用一个格式打通两个心智**。

### `intent_layers`

| 意图层 | 大致占比 | 触发内容类型 |
|--------|---------|-------------|
| **学习/技能 acquisition** | ~30% | 长视频 tutorial / how-to / educational series |
| **产品/工具评估** | ~15% | Long-form review / comparison / unboxing |
| **娱乐 browse(session)** | ~25% | Home / Suggested / Shorts feed(算法推荐) |
| **订阅内容消费** | ~15% | Subscriptions tab(已建立关系) |
| **音乐/背景** | ~10% | YT Music / MV / 播放列表 |
| **live + 社群** | ~5% | Live streams / Community posts / Premieres |

**Atoms 生成内容时的意图定位默认**:每条视频**必须锁定单一意图层**——试图同时讨好"学习"+"娱乐"+"购买"的视频,通常在 CTR 阶段就失败(标题+缩略图无法同时讨好三种心智)。

### `builder_target_segments`

**SaaS / AI Tool** —— **YT 对 SaaS 是最强的 owned-media 平台**(比 IG 强得多)
- 核心受众:developer / marketer / SMB decision maker / creator-turned-buyer;主动搜索"how to X"、"best tool for Y"、"X vs Y"
- 触达机会:
  - **Tutorial-driven**:"How to build/use/integrate X"——搜索意图直接触发,长尾复利
  - **Product demo + walkthrough**:5-15 分钟完整功能展示,替代 landing page 深度
  - **Comparison / vs 类**:"X vs Y in 2026" —— 高购买意图流量
  - **Founder / build-in-public 系列**:小规模但高 conversion,配合 X/Twitter 联动
- 挑战:YT SaaS 内容与 landing page 的 conversion 链路依赖 description link + pinned comment link + card,builder 需要显式引导(不是天然发生);**不要期望 YT 视频 followers 直接付费,是"信任层"而非"结账层"**

**Ecommerce** —— **YT 对 Ecommerce 是「购买前决策」的关键层**,配合 YT Shopping 是完整闭环
- 核心受众:购买评估阶段的消费者(在 Amazon/Google 搜过关键词后来 YT 验证);unboxing / comparison / review 品类
- 触达机会:
  - **Unboxing / first impression**:高开放式购买意图流量
  - **Long-form review**:5-10 分钟深度评测,含使用场景 + 缺陷坦诚
  - **YT Shopping 集成**(2023-2024 扩展):在视频里直接挂产品链接,配合 Description 与 pinned comment
  - **Dupe / alternative 类**:"[热门产品] dupe" —— TikTok/IG 起势后 YT 承接购买决策
- 挑战:Ecommerce 类 YT 视频需要**真实使用感 + 缺陷坦诚**——纯营销宣传型视频在 YT audience 中 CTR 尚可、AVD 立刻崩溃;Atoms Template 需要引导 builder"至少讲一个缺陷"

**Creator(独立开发者 / indie hacker / solo builder)** —— **YT 对 Creator 是最长回报的复利平台**,但也是硬核门槛平台
- 核心受众:同类 builder + 潜在用户 + 想学"how to build X"的开发者
- 触达机会:
  - **"Build in public" 系列** —— 每 1-2 周 update 一支;stack decisions / 决策失败 / MRR 增长
  - **Tutorial "How I built X"** —— 详细技术拆解;YT SEO 强命中"how to build [tool]"关键词
  - **Live coding stream** —— 建立"这个人真的会写代码"的 credibility
  - **Interview 交叉推荐** —— 与其他 indie hacker 互访,拉 subscriber overlap
- 挑战:solo builder 类**YT 从 0 到 1 冷启动比 X/Twitter 慢 3-5 倍**(制作门槛高、cadence 要求硬);但**一旦过 1K subs 后长尾复利与商业化上限比 X 高得多**——**Atoms playbook 应明确告知 builder 这个 tradeoff**,而不是给出"YT 从 0 到 1 也快"的错误预期

---

## §3 算法机制(核心)

### `distribution_model`

**YT 不是单一算法,是 2 套独立系统 + 6 个 surface**——Long-form 与 Shorts 各有独立排序机制,长视频与 Shorts 的信号权重完全不同 [来源: Creator Insider 官方频道多期节目 + YouTube Blog "How YouTube Works", 2024-2025]。

**长视频算法**(Home / Search / Suggested / Subscriptions):
- 核心逻辑:**personalized ranking per user × session-based optimization**——不是"这条视频好不好",而是"这条视频给这个用户当下这个 session 好不好"
- 关键概念:**session watch time**——YT 不只优化单条视频观看时长,而是优化"用户在 YT 停留的整个 session 时长"。这意味着 YT 更愿意推**能让用户看完后继续看下一条 YT 内容**的视频(即使单条稍短)

**Shorts 算法**(独立于长视频):
- 核心逻辑:**per-swipe engagement**——用户是否 swipe 走 vs 看完 vs loop vs like/share
- 关键概念:**"viewed" 定义**——Shorts 只需 1 秒观看即计入 view(与 long-form 定义完全不同);因此**绝对 view 数不是好指标**,swipe-through rate + loop rate 才是

**6 个 surface 的分发角色**:
- **Home**:算法推荐 + 订阅混合;个性化程度最高
- **Search**:关键词 + 用户画像;YT SEO 主战场
- **Suggested**(右侧栏 / mobile 下方):基于当前视频的 topic + 该用户历史;冷启动视频的最大流量来源
- **Subscriptions**:相对纯 chronological + 频道 relevance 微调;不是 YT 主要推荐面
- **Shorts feed**:独立算法,与 long-form 无耦合
- **Trending**:强人工 curation + 数据,SMB 极难触达,不作 KPI

### `ranking_signals`

**YouTube 官方公开的核心排名信号**(YouTube Blog + Creator Insider 多次确认):

**长视频排名 top signals**(按权重顺序):
1. **CTR(Click-Through Rate)** —— 缩略图 + 标题的点击率;首要门槛信号
2. **AVD(Average View Duration)** —— 平均观看时长(绝对秒数)
3. **AVP(Average View Percentage)** —— 平均观看百分比(相对时长)
4. **Session Watch Time** —— 用户观看该视频后是否继续留在 YT
5. **Engagement**:like / comment / share / subscribe follow-through
6. **User satisfaction signals**(2018 起加权):survey response + "not interested" click + 完成率

**Shorts 排名 top signals**:
1. **Watched vs Swiped-away** —— 是否看完 vs 立即划走
2. **Loop rate** —— 是否重复观看(YT Shorts 自动 loop)
3. **Share rate** —— 分享传播权重高于 like
4. **Follow-through**:看完后是否 profile visit / subscribe / 看该频道下一支

**关键新概念 vs IG**:
- **"CTR + AVD" 双门槛**——CTR 低,视频不被推给更多人;CTR 高但 AVD 低,视频"被推出去然后被撤回"。**Atoms Agent 生成缩略图 prompt / 标题时,必须评估「点进去后 30 秒内 payoff 是否兑现」**——只讨好 CTR 而不管 AVD 是自杀
- **Session watch time** —— YT 独有信号;这是"YT 为什么推荐这么多同 creator 的视频"的算法基础
- **"Ready to watch" 概念**(Creator Insider 2024)——YT 会评估"这个用户当下这一刻是否 ready to watch 这个 topic",不 ready 时即使内容好也不推

### `content_type_priorities`

**Shorts vs Long-form 的战略选择框架**——这是 YT 独有的 dual algorithm 决策,与 IG 的 Reels/Feed/Carousel 完全不同:

| 目标 | 首选格式 | 理由 |
|------|---------|------|
| **Discovery(冷启动)** | Shorts | Shorts 算法对新账号更友好;单条 viral 概率 > long-form |
| **Authority build** | Long-form(8-15min) | AVD 累积 + Search SEO 命中 + subscribe 转化率高 |
| **搜索意图接入** | Long-form | Search surface 只推长视频;Shorts 不进 Search 结果 |
| **购买决策转化** | Long-form review(5-15min) | 需要 depth 才建立 trust;Shorts 传达深度受限 |
| **快速试内容方向** | Shorts | 制作成本低;数据反馈快;测试完再长视频化 |

**Atoms 用户默认建议**(0-1K subs 冷启动阶段):
- **Shorts 主打 discovery**(每周 2-3 支)
- **长视频主打 SEO + authority**(每周 1 支,10-15 分钟目标)
- **Shorts 到 long-form 的 funnel**:Shorts 里明确 CTA "完整教程在长视频"

**为什么不 Shorts-only?**——虽然 Shorts 冷启动更容易,但**Shorts 的 subscriber → viewer 转化极低**(YT 官方多次讨论),Shorts-only 频道很难穿越 10K subs 门槛。Atoms builder 目标是长期 authority + 商业化,必须 dual-format。

### `engagement_window`

**关键窗口**:
- **前 24 小时**:决定 CTR baseline + 是否触发算法 second-tier 试探
- **48-72 小时**:AVD 数据成熟,决定是否进入 "steady long-tail push"
- **前 7 天**:算法评估 subscriber follow-through + session watch time,决定长尾权重
- **长尾窗口**:YT 视频寿命远长于其他平台——**Search + Suggested 会持续 3-24 个月带流量**,一支好的 tutorial 视频可能 6 个月后单日流量超过发布首日

**爆款接续机制**(与 IG 类似但更宽容窗口):
- 单支视频 view/AVD 显著超过频道中位时,YT 会打开"试推"窗口
- **7 天内接续同 topic/format 视频**可以承接算法给的 topic-level 权重(YT 是 topic-based ranking,不是纯 creator-based)
- 与 IG 的 48h 窗口相比,YT 的 topic 权重窗口更长,给 solo builder 更多接续时间

### `algo_penalties`

- ⚠️ **AI-generated content 未 disclose**(2024 起 hard rule)——AI 生成或 substantially altered 的内容必须在 upload 时标注 "altered/synthetic";不标注可能面临下架 + 视频降权 [来源: YouTube Blog "Our approach to responsible AI", 2024-03]
- **Made-for-advertising (MFA) 内容**——低质量 AI 快产内容、SEO 堆砌无实质、reused content(仅编辑 minor 无 substantial value)会被去货币化 + 降推(2024 大规模执行)
- **Misleading thumbnails/titles**(clickbait)——缩略图与视频实际内容严重不符,长期会降 CTR baseline + audience trust score
- **Reused content policies**(2024 tightening)——"substantially transformed" 门槛提高;单纯 aggregator / compilation / TTS 类频道大量被 demonetized
- **Copyright claim / Content ID**——即使不侵权也可能被 mute audio 或分成给版权方
- **Community Guidelines strikes** —— 3 次 strike 在 90 天内直接删频道
- **"Not Suitable For All Advertisers"(YPP 黄标)**——不是 penalty 但直接影响 ad revenue;敏感话题 / 争议政治 / 极端语言触发
- **Kids content 合规**(COPPA)——"Made for Kids" 标记会关闭 comments / personalized ads / community post,商业化收窄;误标可能面临罚款

### `recent_changes`(近 12-18 个月)

| 变更 | 时间 | 说明 | Playbook 含义 |
|------|-----|------|--------------|
| **Shorts 时长上调至 3 分钟** | 2024-10 | 从 60s → 180s;仅新上传适用,老 Shorts 保留 60s | §4 硬规则调整:Shorts 建议默认 45-60s(sweet spot 未变),但可测试 90-120s 深度内容 |
| **AI content disclosure required** | 2024-03 | Upload 时必须标注 "altered/synthetic content" 若属实 | Atoms Agent 生成 script/prompt 涉及 AI 演绎时,提示 builder 必须 disclose |
| **YPP 门槛降低(部分商业化)** | 2023-06 | 500 subs + 3K watch hours OR 3M Shorts views —— 可用 Super Thanks / Memberships / Shopping | Atoms builder 商业化起点提前;playbook 修改早期激励叙事 |
| **YouTube Shopping 扩展** | 2023-2024 | Affiliate program 门槛降低;creator 可在视频内挂产品链接;不是 dropshipper 也能加入 | Ecommerce Atoms Template 加入 shopping tag 建议;SaaS Template 关注 affiliate revenue 增量 |
| **AI 自动 dubbing** | 2024 | Aloud 集成到 YT Studio,自动多语言 dubbing 支持 8+ 语种 | 英文 SMB builder 立即扩展 non-English reach,不需要重新拍摄 |
| **"Reused content" 政策收紧** | 2024 | 单纯 compilation / TTS narration / minor edit 大规模去货币化 | Atoms 用户若走 aggregator 路线警告风险 |
| **Video chapters SEO 权重加强** | 2023-2024 | Chapters 影响 Search snippet 与 key moments 功能 | §4 硬规则:>5min 视频必须加 chapters |
| **Community posts 扩至所有频道** | 2023 | 门槛从 500 subs 降至任意 | Atoms builder 可从 day 1 用 Community post 与早期 subs 互动 |
| **Product tag/YT Shopping in Shorts** | 2024 | Shorts 内可挂产品 tag | Ecommerce 类 Shorts 转化路径缩短 |
| **AI content detection + labeling** | 2024-2025 | YT 自主检测部分 AI 内容并 label(不是 100% 覆盖) | 不要指望"不 disclose 就能瞒过"——labeling 会影响 unaware users 的 trust |

---

## §4 内容格式规格

### `post_types`

YouTube 支持的完整内容类型:

| 类型 | 位置 | 主要用途 | Atoms 推荐权重(0-1K subs) |
|------|-----|---------|--------------------------|
| **Long-form video**(>60s) | Home / Search / Suggested / Subscriptions | Tutorial / review / build-in-public / demo | ⭐⭐⭐⭐⭐(首选,SEO + Authority 主战场) |
| **Shorts**(≤180s) | Shorts feed + Home + Subscriptions | Discovery / hook 测试 / snippet 分发 | ⭐⭐⭐⭐(Discovery 主力,配合 long-form) |
| **Live stream** | Home + notification + Subscriptions | Q&A / coding session / launch event | ⭐⭐(阶段性使用,不作日常) |
| **Community post** | 频道 tab + Subscriptions feed | 与已有 subs 的低摩擦互动 / poll / update | ⭐⭐⭐(subs > 100 后启用) |
| **Premiere** | 同长视频 + 首播 chat | 高预期视频的定时首播 | ⭐(仅特殊事件) |
| **Playlists** | 频道 tab + Search + Suggested | Topic 聚合 + session watch time booster | ⭐⭐⭐⭐(结构性重要,不发新内容也要维护) |

### `dimensions_and_ratios`

**硬性尺寸/时长要求**(截至 2026-07):

| 类型 | 宽高比 | 尺寸推荐 | 时长 | 硬规则 |
|------|-------|---------|------|-------|
| **Long-form** | 16:9 | 1920×1080(1080p)或 3840×2160(4K) | 无上限(实测 8-15min 是 SEO + AVD sweet spot) | Atoms builder 目标 8-15min;<3min 除非 Shorts 转长视频过渡产物 |
| **Shorts** | 9:16 | 1080×1920 | ≤3 分钟(2024-10 上调);sweet spot 45-60s | ≤60s 是最优 loop 长度;60-180s 需要更强内容支撑 |
| **Live** | 16:9(推荐 1080p) | 1920×1080 | 15min - 12hr | 直播录像自动进 long-form 系统,同 SEO 规则 |
| **Thumbnail** | 16:9 | 1280×720 | — | <2MB;JPG/PNG/GIF;应清晰、独立成立、含 face 或 bold text |

### `caption_length_recommendation`

**核心原则**:YT description **前 100-150 字符**(即 mobile 折叠前可见)决定 CTR 与 SEO snippet;后半部分承担 SEO 长尾关键词 + link 结构。

| 类型 | 建议 title 长度 | 建议 description 长度 | 结构 |
|------|---------------|---------------------|------|
| **Long-form** | 40-70 字符(含核心关键词) | 200-500 字 | Hook(前 100 字符含关键词)+ 视频 summary + timestamps/chapters + link block + hashtag |
| **Shorts** | 40-80 字符 | 100-200 字 | Hook + 1-2 hashtag + 简短 CTA |
| **Live** | 40-70 字符(含 "Live" 标记 或事件名) | 200-500 字 | 类似 long-form + live-specific 时间/嘉宾/topic |
| **Community post** | 无 title | 1-500 字 | Text-only 或含 image/poll;可以是 update/question/behind-scenes |

**长 description 的策略**:与 IG 相反,**YT description 越长越有利于 SEO**(在保持有意义前提下)——前 100 字符抓 CTR,100-500 字符抓 Search index 与 relevance signal。

### `hashtag_capacity`

**YT hashtag 与 IG hashtag 是两种不同机制**:
- **上限**:最多 15 个 hashtag / description;超过 YT 会**忽略全部**(不是只删多余的——是整帖 hashtag 失效)[来源: YouTube Help 官方]
- **有效数量建议**:**3-5 个 hashtag**(SEO 收益递减,前 3 个权重最高;前 1 个显示在 title 上方作为 topic link)
- **Hashtag 的显示位置**:第 1 个 description hashtag 显示在 title 上方(超链)——**这是 topic 定位的关键位**,不是随便放
- **详细策略**(3-5 tag 与 IG 5-slot 不同的 portfolio 逻辑)见 §6

### `link_and_cta_rules`

**YT 是唯一支持 description clickable link 的主流社媒——这是 vs IG 的关键优势**:
- **Description clickable link**:全 clickable;可放多个;推荐首行放主 CTA link + 折叠区放次要 links
- **Pinned comment**:置顶评论支持 clickable link;是"Description 折叠后的第二 link 机会",Atoms 用户应默认使用
- **Cards**(视频内浮层):可挂 link / playlist / channel;适合中长视频推荐相关内容
- **End screens**(最后 5-20s):可挂 subscribe / next video / external link(需 YPP + 白名单);对 subscriber growth 贡献显著
- **YouTube Shopping tags**(产品链接):视频内 shoppable 挂载,Ecommerce 用户直接闭环
- **Community post links**:纯 clickable,不 tokenized

**Atoms 硬建议**:每条视频 description **第一行**放最重要的 CTA link(app / product / documentation),配 **pinned comment** 重复关键 link——这两处覆盖 mobile 折叠 + 用户 comment scroll 场景,是 YT clickable link 与 IG bio-link 相比的直接优势最大化。

### **§4 Atoms 硬规则汇总**(生成 YouTube 内容时的 must-follow)

1. **Thumbnail 是首要 lever**——90% 的 CTR 由缩略图决定;必须清晰独立成立,含 face 或 bold text
2. **前 30 秒必须有 hook + payoff preview**——AVD 首要 drop-off 点是 15-30s,过不去后面全崩
3. **Title 前 40 字符含核心关键词**——mobile 会截断超出部分
4. **Description 前 100-150 字符必须含 keyword + hook**——影响 CTR 与 Search snippet
5. **≥5 分钟视频必须加 chapters**——Search snippet 呈现 + key moments 功能依赖
6. **AI 生成内容必须 disclose**(upload 时勾选 "altered/synthetic")—— 2024 hard rule
7. **Shorts ≤180s,sweet spot 45-60s**;超 60s 需要真实内容支撑,不做拉长充数
8. **Hashtag ≤ 15,有效 3-5**;第 1 个 hashtag = topic 定位,慎选
9. **Description 首行放主 CTA link + Pinned comment 重复关键 link**——mobile 折叠 + comment scroll 双覆盖
10. **禁 reused/aggregator/pure-TTS 内容**——2024 policy 收紧,直接影响 monetization + 推荐
11. **Playlist 必须维护**——即使不发新内容,老视频归类到 playlist 能拉 session watch time
12. **格式选择按目标而非平台惯性**——discovery 用 Shorts、authority 用 long-form,不要 all-in 一种

### **§4 Brand-Size 分层格式配比**

| Tier | Regime | 目标 | Primary Format | 配比建议 |
|------|--------|------|---------------|---------|
| **Tier 0: 0-500 subs**(Atoms 用户起点) | Discovery + 找 topic-market fit | Shorts + 长视频试 topic | Shorts 主(每周 2-3)+ Long-form 1/week 测 topic |
| **Tier 1: 500-1K subs** | 冲部分商业化 + 建立 topic identity | Shorts + 长视频稳定 topic | Shorts 2/week + Long-form 1/week;开始命中 500 subs 部分商业化 |
| **Tier 2: 1K-10K subs**(通过 YPP 门槛) | Authority + 长尾 SEO 累积 | **Long-form 主(SEO + AVD)** + Shorts 补 discovery | Long-form 1-2/week + Shorts 2-3/week + Community post 每周;playlist 结构化 |
| **Tier 3: 10K+ subs** | 商业化最大化 + 长尾复利 | Long-form 主 + live + membership | Long-form 2/week + Shorts 3-5/week + Live monthly + Community post 3-5/week |

**注意**:Atoms 用户 90%+ 处于 Tier 0/1,playbook 默认按此校准。**与主流"YT 直接做长视频"建议冲突的地方**:Atoms 建议 Tier 0 阶段**优先用 Shorts 做 topic-market fit 测试**,而不是一开始就投入长视频制作——因为长视频制作成本是 Shorts 的 5-10 倍,试错成本对 SMB 太高。

### **§4 Shorts vs Long-form 决策矩阵**

| 场景 | 首选 |
|------|------|
| "怎么用这个工具" - 5 分钟内可讲完 | Shorts + 长视频"完整教程"双发 |
| "怎么用这个工具" - 需要 10+ 分钟 depth | Long-form(Shorts 只做 hook 引流) |
| 产品 launch announcement | Shorts(discovery)+ Long-form(demo)双发 |
| Build-in-public update | Long-form 5-10min(narrative depth) |
| 快速 tip / life hack | Shorts(单一 payoff)|
| Product comparison | Long-form(depth required)|
| Behind-the-scenes | Shorts 或 Community post(不作 long-form)|
| Q&A / community engagement | Community post 或 Live |

---

## §5 调性关键词与语言风格 [待补齐 - Category B research required]

<!-- P1.4 下一步:基于 Backlinko/VidIQ 2025-2026 的 title/description 调性分析 + 高转化 Shorts 结构归纳,填充 §5 -->

**素材已就位**:
- YT SEO 与 title 语言风格文献(Backlinko YT SEO Guide 2025)
- Creator Insider 官方对 title/thumbnail 调性建议
- TubeBuddy / VidIQ 高转化 title pattern 数据

**基本框架占位**:

### `tone_descriptors`(初稿,待数据验证)
- **educational / practical**(教程/how-to 类):具体 / 步骤化 / 无营销腔
- **honest / transparent**(review 类):承认 tradeoff / 不神化产品
- **excited-but-credible**(demo / launch):有热情但不 hype
- **conversational** (build-in-public):第一人称 / 分享失败与决策

### `voice_do`(占位)
- Title 具体到"教一件事"(如"How to X in 5 minutes",而不是"Tips for X")
- Description 前段用第二人称 "you'll learn / you'll build",拉参与感
- Shorts hook 前 3 秒直接给 payoff preview

### `voice_dont`(占位)
- Title 过度 clickbait("You won't believe...")—— 短期 CTR 高但 audience trust 崩
- Description 全部大写 / emoji spam —— 触发 low-quality 信号
- Long-form 开头 30s "Hey guys welcome back to my channel..." —— AVD 立即崩塌

### `emoji_and_emphasis`(占位)
- Title:0-1 emoji(用于 vibe signal,如 🚀 / 🔥),不放开头(占用关键 keyword slot)
- Description:视 vibe 使用;工具/教程类偏少,vlog/entertainment 偏多
- Chapters:清晰标点分隔,不用 emoji 作为 chapter marker

### `hook_patterns`(3-5 种典型模式,占位待数据填充)
- **Contrast hook**:"I built X in 30 days. Here's what went wrong."
- **Result-first hook**:"Here's how I got 1K subs in 60 days."
- **Question hook**:"Should you use X or Y? I tested both."
- **Number-driven hook**:"5 ways to X"(经典 listicle,YT SEO 友好)
- **Stakes hook**:"If you're building X, don't make this mistake."

---

## §6 Hashtag 策略 [待补齐 - Category B research required]

<!-- P1.4 下一步:基于 YT 官方 + Backlinko / VidIQ 2025-2026 hashtag data,替代 IG 5-slot 框架建立 YT 3-5 tag portfolio -->

**基本框架占位**:

### `optimal_count`
- **3-5 个 hashtag**(不是 15 上限);第 1 个权重最高,显示于 title 上方
- 超过 5 个 SEO 收益递减,15+ 触发 YT 全量忽略

### `mix_strategy`(占位:3-5 tag portfolio 框架)
- **1 个 topic anchor**(如 #ProductivityTips, 显示于 title 上方作为频道 topic 定位)
- **1-2 个 niche community**(如 #IndieHacker, #BuildInPublic)
- **1 个 format tag**(如 #Tutorial, #Shorts —— 后者已内建但可显式)
- **1 个 branded tag**(如频道名 hashtag,长期社群累积)

### `research_method`(占位)
- VidIQ / TubeBuddy 的 keyword research 工具查 search volume
- YT 自动推荐 tag(search bar 输入时)
- 竞品频道 top 视频 description 中提取的 hashtag 频次

### `banned_or_risky`
- **Hashtag 数超 15 → 全量忽略**(硬规则)
- Misleading hashtag(与视频内容严重不符)→ 触发 "misleading metadata" 检测
- 侵权 hashtag(品牌名滥用)→ Content ID + 平台干预

---

## §7 发布节奏与频率 [待补齐 - Category B research required]

<!-- P1.4 下一步:基于 SocialBlade / TubeBuddy 2025-2026 posting cadence 数据 + Atoms Template 的 3 业务类型分别建议 -->

### `best_posting_times`(占位)
- **Long-form**:UTC-5(EST)工作日 15:00-17:00 或 20:00-22:00(下班到睡前);周末 09:00-11:00
- **Shorts**:全天分布更均匀;峰值 12:00-14:00 + 19:00-22:00
- **注意**:YT 的发布时间敏感度**低于 IG/TikTok** —— 因为长尾流量占比高,单日 timing 影响相对小

### `default_timezone`
UTC-5 EST(美东);多语言频道按目标市场时区

### `frequency_recommendation`(按 Tier)
- **Tier 0/1**:Shorts 2-3/week + Long-form 1/week(consistency > frequency)
- **Tier 2**:Long-form 1-2/week + Shorts 2-3/week + Community post 1-2/week
- **Tier 3**:Long-form 2/week + Shorts 3-5/week + Live monthly

### `first_week_ramp_up`(冷启动策略)
- 频道开启后 **48 小时内发首支 Shorts + 首支长视频**,避免"空频道"信号
- 前 2 周 daily Shorts 冲初始曝光(单发失败无所谓,量在)
- Long-form 稳定 weekly cadence 更重要于起量早期就 daily

---

## §8 业务类型 × 平台适配 [待补齐 - Category B research required]

<!-- P1.4 下一步:结合 SaaS/Ecommerce/Creator 三类 Atoms 用户的 YT 案例研究,填充每类的 content angles / visual style / caption focus / CTA / traps -->

### 8.1 SaaS / AI Tool

**框架占位**:

- `fit_score`:**5/5** —— YT 是 SaaS 最强的 owned-media 平台(教程 + demo + review 三重覆盖)
- `content_angles`:
  - Tutorial-driven("How to X with [tool]")—— 搜索意图触发,长尾复利
  - Product demo + full walkthrough(5-15 分钟)—— 替代 landing page depth
  - Use case / customer story —— 具体行业应用 driver
  - Comparison vs 类("X vs Y in 2026")—— 高购买意图
- `visual_style`:
  - Screen recording + face-cam PIP(picture-in-picture)—— 提升 AVD
  - Cursor / text highlight 强调,不要纯 UI 无解说
  - Thumbnail 含 product screenshot + 大字标语
- `caption_focus`:
  - Description 前 100 字符含 "how to [具体 task]" 关键词
  - Chapters 拆解:Setup / Feature 1 / Feature 2 / Result / Next steps
  - Pinned comment 挂 free trial / documentation link
- `cta_style`:
  - Description 首行 → free trial link
  - 视频结尾 → "Try it here (link in description) or star on GitHub"
  - Card / end screen → 相关 tutorial 视频接续
- `common_traps`:
  - 只讲功能不讲 job-to-be-done —— AVD 崩塌
  - Feature marathon(20 分钟一次讲完所有功能)—— 应拆分成多支视频
  - 忽视 Shorts,只做 long-form —— 冷启动 discovery 大幅慢

### 8.2 Ecommerce

**框架占位**:

- `fit_score`:**4/5** —— 强(unboxing + review + comparison + YT Shopping 直挂)
- `content_angles`:
  - Unboxing / first impression —— 高开放式购买意图
  - Long-form review with pros/cons —— 建立 trust
  - Dupe / alternative comparison —— 承接 TikTok/IG 起势后的深度评估
  - Behind-the-scenes / brand story —— 高 loyalty 品类(如 D2C)
- `visual_style`:
  - 产品在真实使用场景(不是纯白背景棚拍)
  - 缩略图含产品 + 使用场景 + face 反应
- `caption_focus`:
  - Description 前段 "Where to buy" + affiliate/self-link
  - YT Shopping tag 挂产品
  - 时间戳 chapters:开箱 / 使用 / 评价 / 对比
- `cta_style`:
  - Description 首行 shopping link
  - Pinned comment 重复 shopping link + discount code
  - End screen → 相关产品 review 接续
- `common_traps`:
  - 纯营销宣传型无缺陷坦诚 —— AVD 立刻崩溃
  - 忽视 Shorts unboxing 短视频 —— 冷启动流量丢失
  - Description 不挂 shopping tag —— 直接损失 conversion

### 8.3 Creator(indie hacker / solo builder)

**框架占位**:

- `fit_score`:**4/5** —— 长回报最强的平台,但制作门槛与冷启动难度高于 X/Twitter
- `content_angles`:
  - "Build in public" 系列 —— 每 1-2 周 update;MRR / decisions / failures
  - "How I built X" tutorial —— 详细技术拆解;YT SEO 命中 "how to build [tool]"
  - Live coding stream —— 建立"这个人真的会写代码"credibility
  - Interview cross-pollination —— 与其他 indie hacker 互访拉 subscriber overlap
- `visual_style`:
  - Face-cam + screen recording split
  - Terminal / code editor 清晰可读(font size 24+)
  - Thumbnail 含 face + MRR 数字或核心 metric
- `caption_focus`:
  - Description 前 100 字符含 "how I built" / "$X MRR" / "day X of building"
  - Chapters:Idea / Stack / Build / Launch / Metrics
  - Pinned comment 挂 tool / GitHub / newsletter
- `cta_style`:
  - Description 首行 → newsletter / X / GitHub
  - End screen → "Join me next week for [next update]"
  - Community post → daily/weekly text updates 拉留存
- `common_traps`:
  - 期待 YT 从 0 到 1 也快 —— 现实 X/Twitter 更快,YT 是长期复利
  - Live coding 超 2 小时 —— 剪辑 highlight 出 Shorts 与 long-form 双发更 ROI
  - 不同 topic 混发(有时讲 SaaS、有时讲创业、有时讲生活)—— 稀释 topic ranking signal

---

## §9 高转化模式 [待补齐 - Category B research required]

<!-- P1.4 下一步:基于 40-60 个 YT case sample(Backlinko / VidIQ / SocialBlade / Ahrefs YT SEO Guide),归纳跨业务/跨格式的高转化结构 -->

### `sample_size_and_source`(目标 40-60,现有 0,待收集)
- **收集 pipeline**:`scripts/youtube_search_queries.md` → `data/youtube_industry_urls.txt` → WebFetch → `data/youtube_case_studies.json` + `scripts/fetch_youtube_metadata.py` 直取 YT 数据
- **人工补齐**:`data/youtube_manual_supplements.md`

### `winning_structures`(初稿占位,待 sample 归纳验证)

**结构 1 — "Result-first hook + step reveal"**(Tutorial 类主流)
- 前 30s:显示 result / final outcome
- 30s-60s:承诺"how"路径
- 60s-末尾:step-by-step 展开
- 结尾:CTA + related content

**结构 2 — "Contrast comparison"**(Review / Comparison 类)
- 前 30s:两个 option 都展示 + 承诺"which one wins"
- 30s-中段:分维度对比(price / feature / UX 各 1-2 min)
- 中后段:showdown / real-use test
- 结尾:verdict + 具体使用建议

**结构 3 — "Journey narrative"**(Build-in-public / Solo builder 类)
- 前 30s:current status + hook(如 MRR 数字 / user count)
- 30s-中段:回溯 origin + 关键决策与失败
- 中后段:当前挑战 + 下一步
- 结尾:互动邀请 + 下期预告

**结构 4 — "Problem-solution-proof"**(SaaS demo 类)
- 前 30s:现实场景中的痛点演绎(不是抽象讲)
- 30s-中段:solution 展开
- 中段-末尾:实际使用 demo
- 结尾:trial CTA + how-to-start

**结构 5 — "Listicle countdown"**(SEO-driven listicle)
- Title:"X ways/tools/tips to Y"
- 前 30s:预告全部 X 个 item + 高潮 tease
- 每 item 1-2 min,清晰 chapters
- 结尾:pick 一个作为 winner + related content CTA

### `visual_patterns`(占位)
- Thumbnail:face + bold text + high contrast(不是 flat design)
- 首帧:直接进内容,不用"welcome back"缓冲
- Screen recording zoom + highlight cursor
- Split screen(A/B 对比)配 review 类

### `engagement_triggers`(占位)
- **AVD triggers**:step-by-step chapters + "we're going to X next" 明确预告
- **CTR triggers**:number + specificity(不是 "tips",是 "5 tips")
- **Subscribe triggers**:系列承诺 + 具体价值主张("weekly Y for X audience")
- **Comment triggers**:开放式问题 + 请求 audience specific input("which one would you pick?")

---

## §10 避坑清单 + 数据源 [待补齐 - Category B research required]

### `avoid_list`(初稿,按严重程度排序)

**严重(可能删频道 / 大幅降权)**:
1. **未 disclose AI 生成 substantially altered 内容** —— 2024 hard rule,可能 removal
2. **Reused/aggregator/pure-TTS 频道** —— 2024 policy 收紧,批量 demonetization
3. **Community Guidelines 3 strikes in 90 days** —— 直接删频道
4. **误标 "Made for Kids"(反之亦然)** —— COPPA 合规 + FTC 罚款

**中等(降推 / 商业化受限)**:
5. **Misleading thumbnail/title(clickbait)** —— 长期 CTR baseline 降 + audience trust 崩
6. **Hashtag 超 15 个** —— 全部 hashtag 失效
7. **Description spam(全大写 / emoji flood / 无意义 keyword stuffing)** —— low-quality signal
8. **视频开头 30s 无 payoff preview** —— AVD 崩塌,连锁触发 CTR baseline 下降

**观感差(不 penalize 但转化差)**:
9. **"Hey guys welcome back to my channel..."** —— AVD 首要 drop-off 点,浪费黄金 30s
10. **Feature marathon(单支视频塞入所有功能)** —— AVD 崩 + 不利于 SEO 长尾
11. **不写 chapters(视频 >5min)** —— Search snippet 缺失 + 用户 skim 体验差
12. **Description 首行不放 CTA link** —— 浪费 mobile 折叠前唯一显式 conversion 机会

### `references`(现有已收集 + 待补齐)

**Category C — 官方**(权威 quote 来源):
- YouTube Blog "How YouTube Works" section — https://blog.youtube/how-youtube-works/
- YouTube Creator Academy — https://creatoracademy.youtube.com/(部分内容迁移到 YouTube Help)
- Creator Insider(官方 YouTube channel)—— 算法 / policy update 首发地
- YouTube Help(YPP 门槛、AI content policy、hashtag rules)
- YouTube Data API v3 documentation — 直接支持元数据采集(与 IG 关键差异)

**Category B — 待跑 Search 补齐**:
- Backlinko YouTube SEO Guide 2025
- VidIQ Blog(algorithm + CTR 分析)
- TubeBuddy Blog(creator growth benchmarks)
- Hootsuite YouTube Report 2026
- SocialBlade(频道 growth benchmarks)
- Ahrefs YouTube SEO(keyword research 方法论)

### `next_review_date`
2027-01-02(6 个月后强制复核算法与格式规则;AI content policy 与 Shorts 上限属高变动章节,可能提前触发局部更新)

---

## §11 与 IG playbook 的关键差异(Atoms 内部使用)

**为方便 Skill 生成时的平台切换判断,以下列出 YT vs IG 在 playbook 层面必须记住的核心差异**(不属于 _schema 的 10 sections,是 Atoms 内部使用的判断锚点):

| 维度 | IG | YT |
|------|----|----|
| **主要发现机制** | 推荐 feed 为主 | 搜索 + 推荐 + Suggested 三足鼎立 |
| **单条内容寿命** | 48-72 小时短尾 | 3-24 个月长尾复利 |
| **算法数量** | 4 个 surface(Feed/Stories/Reels/Explore) | 2 大算法(Long-form / Shorts)× 6 surface |
| **顶级信号** | Watch time / Likes / Sends per view | CTR + AVD + Session watch time |
| **Hashtag** | 5 上限 hard-enforced;5-slot portfolio | 15 上限(超即忽略);有效 3-5 |
| **Description clickable link** | ❌(bio link only) | ✅(全 clickable + pinned comment) |
| **Thumbnail 权重** | 中(feed 中被自动截取) | **首要**(90% 决定 CTR) |
| **数据采集可行性** | OG 被剥离,靠博客二手 + 人工 | ✅ oEmbed + Data API v3 直取(见 scripts/fetch_youtube_metadata.py) |
| **AI content policy** | 通用社区规则 | **hard disclose 要求**(2024 起) |
| **冷启动难度(0-1K)** | 低-中(Reels 单 viral 相对容易) | 中-高(需要 SEO 结构 + Shorts 双引擎) |
| **长期复利上限** | 中(engagement 面向 followers) | **高**(SEO 长尾 + 商业化多元:广告 / 会员 / Shopping) |

**Skill 决策含义**:
- 平台化文案单点应答时,YT 需要生成 title + description + thumbnail concept + hashtag 四件套,不是只 caption + hashtag
- 首发内容包 Template `saas_youtube` / `ecom_youtube` / `creator_youtube` 需增加 `thumbnail_prompt` 段(与 IG `image_prompt` 独立字段)
- 增长诊断在 YT 场景下,GA4 traffic source 里的 "youtube" 拆分 organic search vs suggested vs direct 三源诊断价值高

---

*次版本目标*:补齐 §5-§10 后进入 v0.2;v1.0 需要 Category B(至少 40-60 case)与 Data API v3 实抓样本(至少 20-30 支 Atoms 目标业务视频)交叉验证。scripts/fetch_youtube_metadata.py 就位后可直接接管样本数据层。
