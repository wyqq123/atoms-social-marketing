# 社媒趋势信号采集工程实现方案

## 1. 目标

本文回答一个具体问题：`audience_observed`、`content_consumption_observed`、`distribution_observed`、`trend_metrics`、`evidence`、`known_biases` 这些信号到底从哪里获取、怎么获取、如何落地到工程系统、如何定期执行，并如何服务 Stage 2 的 built app end-user ICP × trend audience 交集计算。

核心结论：**不要尝试做全平台、全自动、实时抓取。** 合规且高可行的方案是建立“多通道采集 + 统一归一 + 可追溯证据 + 置信度降级”的趋势观测系统。

## 2. 总体架构

```text
Platform source
  | official API / official tool export / authorized insight / public report / manual curation
  v
Raw collector or importer
  v
Normalizer
  v
Trend Observation Snapshot
  v
Validator + freshness checker
  v
Trend Brief Builder(built app end-user ICP aware)
  v
Stage 2 fit_score / Stage 3 strategy
```

新增建议目录：

```text
data/
  trend_observation_schema.json
  trend_snapshots/
    youtube/US/saas.json
    reddit/US/saas.json
    tiktok/US/creator-tool.json
  manual_imports/
    rednote/2026-07-26-cn-ecommerce.yaml
    linkedin/2026-07-26-us-b2b.yaml

references/
  trend-observation-contract.md
  audience-intersection-scoring.md
  trend-signal-acquisition-engineering-plan.md

scripts/
  trend_adapters/
    base.py
    youtube.py
    reddit.py
    pinterest.py
    tiktok_creative_center.py
    x_api.py
    instagram_authorized.py
    linkedin_manual.py
    rednote_manual.py
    report_importer.py
  refresh_trend_observations.py
  validate_trend_observation.py
  build_trend_brief.py
  audit_trend_sources.py
```

## 3. 信号字段与获取方法总表

| 字段 | 表示什么 | 高可行数据源 | 获取方法 | 自动化程度 | 主要限制 |
|---|---|---|---|---|---|
| `audience_observed` | 趋势附近的人是谁、他们的身份/社区/痛点/阶段线索 | Reddit subreddit、YouTube channel/video/comment title metadata、X recent search、Pinterest keyword/board、用户授权 IG/Threads/LinkedIn insights、人工 Rednote/LinkedIn 样本 | API 拉元数据 + LLM/规则抽取身份痛点；人工表单补齐难抓平台 | 中 | 多数平台拿不到真实人口属性，只能用社区/文本/账号/搜索词 proxy |
| `content_consumption_observed` | 这批人偏好什么内容形态、hook、叙事和互动方式 | 高互动帖子/视频/pin/note 样本、评论结构、标题/封面/首帧/描述、行业报告 | 样本采集 + 结构化抽取 + 人工校验 | 中 | 容易有幸存者偏差；需要 normalizer 标注 source bias |
| `distribution_observed` | 小账号如何触达这批人、入口和门槛是什么 | 平台规则文档、subreddit rules、API 暴露的 surface、官方算法说明、商业后台趋势工具 | 稳定层规则 + 动态入口数据 + 人工规则补齐 | 中高 | 推荐算法不透明，只能用公开机制和入口 proxy |
| `trend_metrics` | 热度、增长、互动、拥挤度 | YouTube Data API、Reddit API、Pinterest Trends/API、X API、TikTok Creative Center、手工导出 | 指标归一化到 0-100 index | 中高 | 不同平台 raw metric 不可横向比，必须平台内归一 |
| `evidence` | 每个判断的来源、时间、字段、可信度 | 所有 source | collector 自动写入 | 高 | 人工导入也必须写来源和观察日期 |
| `known_biases` | 数据偏差与不可知项 | adapter 固定规则 + validator 推断 + 人工补充 | 自动 + 人工 | 高 | 需要强制写，否则模型会过度相信数据 |

## 4. 数据源类型与落地优先级

### 4.1 Source Tier

| Tier | 来源类型 | 工程策略 | 可信度 | 示例 |
|---|---|---|---|---|
| A | 官方 API | 优先自动化 collector | high | YouTube Data API、Reddit API、Pinterest API、X API(付费)、Threads API(授权) |
| B | 官方公开趋势/商业工具 | 半自动导出或 Playwright 非登录读取；失败时人工导入 | medium-high | TikTok Creative Center、Pinterest Trends、Rednote 聚光/蒲公英、巨量算数 |
| C | 用户授权账号数据 | OAuth/平台后台授权后拉取自有账号 insights | high for own-account, low for platform-wide | Instagram insights、Threads insights、LinkedIn Page analytics |
| D | 公开报告/行业文章 | report importer + LLM 提取结构，不当作实时热点 | medium | Hootsuite、Later、SocialInsider、Buffer、平台官方博客 |
| E | 人工精选样本 | 标准表单导入，必须有来源和日期 | medium/low | Rednote 热门笔记结构、LinkedIn B2B post 样本 |

### 4.2 MVP 优先级

最先做这些，因为可行度最高：

1. **YouTube**：官方 Data API/oEmbed，适合拿 `trend_metrics` 和内容结构。
2. **Reddit**：官方 API + subreddit rules，适合拿 audience/pain/community intent。
3. **TikTok**：Creative Center 官方趋势工具，人工/半自动刷新即可，适合拿 hashtag/sound/keyword/top ads pattern。
4. **Pinterest**：Pinterest Trends + API，适合拿 keyword/visual search/evergreen intent。
5. **Rednote/LinkedIn/Instagram**：先走 manual importer + 官方/授权 insights，不承诺全站自动抓。

## 5. 各信号的具体获取方案

## 5.1 `audience_observed`

### 5.1.1 能获取什么

```json
{
  "observed_end_user_self_descriptions": ["Shopify seller", "small business owner"],
  "communities": ["r/SaaS", "r/productivity"],
  "geo_language_hints": ["US English"],
  "role_or_context_hints": ["operator", "knowledge worker"],
  "pain_point_hints": ["manual admin", "tool fragmentation"],
  "buying_stage_hints": ["problem-aware", "solution-exploring"],
  "confidence": "medium",
  "evidence_type": "community_context_plus_text_cues",
  "boundary_note": "These are observed platform audience self-descriptions, not Atoms builder identity. Only compare them with built app end-user ICP."
}
```

### 5.1.2 获取来源

| 平台 | 优先来源 | 获取方法 | 可得到的 audience proxy |
|---|---|---|---|
| Reddit | 官方 API + subreddit metadata/rules | 拉 subreddit hot/top/search posts；读取标题、正文摘要、subreddit 名称、评论数、score；LLM 抽取自称/痛点 | community identity、role hints、pain hints、buying stage |
| YouTube | Data API search/videos + channel metadata | 按 query 拉视频；读取 title、description、tags、channel title、category、view/comment count | search intent、creator niche、comment intensity proxy |
| X | X API recent search(若付费可用)或 curated public lists 手工导入 | 按 query/list 拉 post text、author metrics、engagement | founder/operator identity、topic cluster、build-in-public density |
| TikTok | Creative Center keyword/hashtag/top ads + 人工观察 | 导出 rising keywords/hashtags/top ads pattern；LLM 抽取受众语境 | interest/pain proxy，不是人口画像 |
| Pinterest | Pinterest Trends/API | 拉 keyword trend、pin/search surfaces、board/category | planning/shopping/search intent、visual interest |
| Instagram | 用户授权 insights + 行业报告 + manual samples | 自有账号 audience insights；公开全站趋势不抓 | own-account audience、format preference |
| LinkedIn | Page analytics/行业报告/manual | 授权组织页数据 + 人工精选 post | professional role、B2B topic、buyer intent proxy |
| Rednote | 聚光/蒲公英后台导出 + 人工样本 | 运营按关键词/类目导出或手填热门笔记 | consumption persona、种草阶段、痛点表达 |

### 5.1.3 实现方法

- Collector 只保存 raw title/body excerpt/metadata，不保存大段原文。
- Normalizer 用规则 + LLM 抽取：
  - 规则抽取社区、语言、地域、source surface。
  - LLM 抽取身份自称、痛点、购买阶段，但必须引用原始证据片段。
- 对没有人口属性的平台，不要伪造 age/gender/income；只写 `unknown` 或基于官方报告写到 stable layer。

## 5.2 `content_consumption_observed`

### 5.2.1 能获取什么

```json
{
  "dominant_intent": ["seeking advice", "comparing tools"],
  "preferred_content_forms": ["tool comparison", "transparent founder answer"],
  "successful_hook_structures": ["specific pain title", "before-after workflow"],
  "visual_or_aesthetic_markers": ["screen recording", "large result overlay"],
  "interaction_pattern": ["long comments", "skepticism toward promotional posts"]
}
```

### 5.2.2 获取来源与方法

| 来源 | 方法 | 抽取字段 |
|---|---|---|
| 高互动样本 | API 或人工导入 top/hot/rising 内容 | hook、标题结构、format、CTA、评论触发方式 |
| 评论/回复结构 | Reddit comments count、YouTube comment count、X replies、manual summaries | 是否偏讨论、求助、争论、案例补充 |
| 官方趋势工具 | TikTok Creative Center top ads、Pinterest Trends | visual style、关键词、创意结构 |
| 行业报告 | report_importer | 稳定内容消费结论，标注滞后性 |
| 人工标注 | manual_importer | 封面、首帧、图文结构、审美词 |

### 5.2.3 自动抽取规则

```text
if title contains "how to" / "tutorial" / "guide" -> dominant_intent += learning
if title contains "best" / "vs" / "alternative" -> dominant_intent += comparison
if Reddit post has high comment-to-score ratio -> interaction_pattern += discussion-heavy
if YouTube video duration <= 180s and title contains result promise -> preferred_content_forms += short explainer/demo
if Rednote manual sample has cover_text + checklist body -> preferred_content_forms += note/checklist
```

LLM 用于归纳 hook structure，但必须输出 `supporting_sample_ids`。

## 5.3 `distribution_observed`

### 5.3.1 能获取什么

```json
{
  "small_account_access": "medium-high",
  "gatekeepers": ["subreddit rules", "anti-promotion culture"],
  "recommended_surface": "subreddit_discussion",
  "entry_points": ["r/SaaS", "r/productivity search", "comment-first"],
  "policy_risk": "medium"
}
```

### 5.3.2 获取来源

| 平台 | 分发入口 | 获取方法 | 关键判断 |
|---|---|---|---|
| Reddit | subreddit hot/top/search/comment | API + subreddit rules | 小账号可进入，但反营销强；适合问题帖/评论先行 |
| YouTube | search/suggested/shorts/channel | Data API + stable playbook | 搜索意图强，长尾好；冷启动视频生产门槛较高 |
| TikTok | FYP/search/Creative Center trends | Creative Center + stable playbook | 小账号可触达，但内容完播/首秒强依赖高 |
| X | For You/follow graph/search/list | X API/manual | build-in-public、技术圈关系扩散强；噪声和时效高 |
| Pinterest | search/home feed/boards | Pinterest Trends/API | evergreen search 强；视觉和关键词质量决定分发 |
| LinkedIn | feed/network/company page | stable layer + Page analytics | B2B 信任强，小号需 founder credibility 或 network |
| Rednote | search/recommendation/note | manual/business tools | 搜索种草强，封面和标题决定点击，商业感过重会弱 |

### 5.3.3 实现方法

- `platform_registry` 存稳定的 `surface_capabilities` 和 `conversion_paths`。
- Adapter 动态补充 `entry_points`、`small_account_access`、`policy_risk`。
- `small_account_access` 用 proxy 估计：
  - 推荐流平台：是否存在低粉爆款样本。
  - 社区平台：是否允许新用户发帖、是否限制自促。
  - 搜索平台：关键词竞争是否低、是否 evergreen。

## 5.4 `trend_metrics`

### 5.4.1 为什么用 index

不同平台指标不可直接比较：Reddit upvote、YouTube views、TikTok hashtag views、Pinterest search trend、X repost 都不是同一种东西。因此统一转成平台内 0-100 index。

```json
{
  "volume_index": 72,
  "velocity_index": 64,
  "engagement_index": 58,
  "saturation_index": 41,
  "metric_basis": "normalized within platform-region-vertical snapshot"
}
```

### 5.4.2 指标来源

| Index | 含义 | 可用 proxy |
|---|---|---|
| `volume_index` | 当前声量/规模 | view count、post count、search volume、community size、hashtag video count |
| `velocity_index` | 增长速度 | 7d vs 30d 增长、rising rank、new posts/hour、trend rank delta |
| `engagement_index` | 互动质量 | comments/views、upvotes/post、saves/pins、reply depth、like/view |
| `saturation_index` | 拥挤/同质化程度 | 同关键词内容数量、广告密度、重复 hook 比例、top results concentration |

### 5.4.3 归一化方法

MVP 用简单稳健归一，不追求复杂模型：

```text
index = percentile_rank(metric_value within same platform + region + vertical + window)
```

没有足够样本时：

```text
index = bucketed_rank(low=25, medium=50, high=75) + confidence downgrade
```

例如 Reddit：

```text
volume_index = percentile(score + num_comments * 2) among collected posts
velocity_index = percentile(recency_weighted_score)
engagement_index = percentile(num_comments / max(score, 1))
saturation_index = percentile(number_of_posts_matching_same_keyword_cluster)
```

YouTube：

```text
volume_index = percentile(view_count)
velocity_index = percentile(view_count / days_since_publish)
engagement_index = percentile((like_count + comment_count * 3) / view_count)
saturation_index = percentile(count of search results in same query cluster)
```

TikTok Creative Center：

```text
volume_index = normalized hashtag/video_count or keyword volume
velocity_index = normalized growth_7d or rising rank
engagement_index = unavailable in public Creative Center -> null or manual/top_ads proxy
saturation_index = approximate by count of highly similar tags/ads patterns
```

## 5.5 `evidence`

### 5.5.1 必填结构

```json
{
  "source_type": "official_api",
  "source_name": "YouTube Data API videos.list",
  "source_url": "https://developers.google.com/youtube/v3/docs/videos/list",
  "observed_at": "2026-07-26T00:00:00Z",
  "raw_ref": "raw/youtube/US/saas/2026-07-26/search_ai_agent_demo.json",
  "metric_fields_available": ["viewCount", "likeCount", "commentCount", "publishedAt"],
  "license_or_access_note": "API key required; quota applies"
}
```

### 5.5.2 实现要求

- 每个 observation 至少有 1 条 evidence。
- 每个 LLM 抽取字段必须能追溯到 sample id 或 evidence ref。
- 人工导入必须填写 `source_url` 或 `source_description`，否则 validator 拒绝。
- 不存 API token，不存登录 cookie，不存用户隐私字段。

## 5.6 `known_biases`

### 5.6.1 自动生成规则

| 情况 | 自动写入 bias |
|---|---|
| 只采 top/hot 内容 | `success_case_bias` |
| 只采单一 subreddit/list/keyword | `surface_selection_bias` |
| 缺少评论/互动明细 | `engagement_context_missing` |
| 使用行业报告 | `report_lag_bias` |
| 使用人工标注 | `manual_judgement_bias` |
| 缺少人口属性 | `no_demographic_ground_truth` |
| 使用授权自有账号数据 | `own_account_bias` |

### 5.6.2 用途

- Stage 2 计算 Evidence Quality。
- Stage 3 限制措辞：不能说“当前平台用户都在……”，只能说“本次样本显示……”。
- Stage 5 输出 warning。

## 6. 平台级实现方案

## 6.1 YouTube

### 来源

- YouTube Data API `search.list`：按 query 找公开视频。
- YouTube Data API `videos.list`：拉 statistics、snippet、contentDetails。
- oEmbed：无 API key 的 fallback，只能拿 title/author/thumbnail。

### 获取信号

| 信号 | 获取方法 |
|---|---|
| audience_observed | query intent、channel niche、title/description/tags 的语义线索 |
| content_consumption_observed | 高 view/高 comment 视频标题、时长、description、thumbnail prompt 手工/LLM 标注 |
| distribution_observed | search query surface、Shorts vs long-form、publishedAt 与 views/day |
| trend_metrics | views、likes、comments、views/day、query result density |
| evidence | API response + docs URL + observed_at |
| known_biases | search ranking bias、public video only、no viewer demographics |

### MVP 执行

```bash
python scripts/trend_adapters/youtube.py collect \
  --region US \
  --vertical saas \
  --queries data/query_sets/youtube_saas.txt \
  --window 30d \
  --output data/trend_snapshots/youtube/US/saas.json
```

优先复用现有 `scripts/fetch_youtube_metadata.py`，再包一层 normalizer。

## 6.2 Reddit

### 来源

- Reddit API subreddit listing：hot/top/new/search。
- subreddit rules/about/wiki：规则与反营销门槛。
- 评论数量、score、created_utc、upvote ratio 等公开字段。

### 获取信号

| 信号 | 获取方法 |
|---|---|
| audience_observed | subreddit identity + title/body/comment snippets 中自称和痛点 |
| content_consumption_observed | hot/top post 的 title pattern、comment depth、discussion ratio |
| distribution_observed | subreddit rules、post removal risk、new account posting restrictions manual note |
| trend_metrics | score、num_comments、recency、keyword cluster density |
| evidence | API endpoint、subreddit、post ids、observed_at |
| known_biases | selected subreddit bias、moderation bias、no demographic truth |

### MVP 执行

```bash
python scripts/trend_adapters/reddit.py collect \
  --region US \
  --vertical saas \
  --subreddits SaaS,startups,smallbusiness,productivity,Entrepreneur \
  --keywords "automation,landing page,no code,AI agent" \
  --window 7d \
  --output data/trend_snapshots/reddit/US/saas.json
```

Reddit 是最适合做 built app end-user ICP × pain intersection 的平台之一，因为 community 和问题文本非常强。但内容生成必须强制 subreddit-native，不能广告腔。

## 6.3 TikTok

### 来源

- TikTok Creative Center：hashtags、songs、top ads、keyword insights。
- TikTok 官方 newsroom / business docs：稳定层算法和广告创意规则。
- 人工补充：Creator/SMB 样本。

### 获取信号

| 信号 | 获取方法 |
|---|---|
| audience_observed | hashtag/keyword/category 的兴趣语境；人工样本补身份和痛点 |
| content_consumption_observed | Creative Center top ads pattern、hook、时长、visual rhythm |
| distribution_observed | FYP/search/trending sound/hashtag 入口；商业安全 sound 标注 |
| trend_metrics | hashtag count、growth_7d、keyword volume、top ads pattern frequency |
| evidence | Creative Center URL、导出日期、截图/CSV ref |
| known_biases | ads sample bias、no organic post metrics、regional availability bias |

### MVP 执行

```bash
python scripts/trend_adapters/tiktok_creative_center.py import \
  --input data/manual_imports/tiktok/2026-07-26-US-saas.csv \
  --region US \
  --vertical saas \
  --output data/trend_snapshots/tiktok/US/saas.json
```

第一阶段建议做人工/半自动导入，不强行自动抓 UI。这样最稳，也规避 Creative Center UI 变化。

## 6.4 Pinterest

### 来源

- Pinterest Trends：关键词趋势。
- Pinterest API v5：pins/boards/analytics 等授权能力。
- Pinterest Predicts / 官方业务报告：稳定层趋势方向。

### 获取信号

| 信号 | 获取方法 |
|---|---|
| audience_observed | keyword/category/board interest proxy |
| content_consumption_observed | Pin 标题、描述、视觉层级、关键词结构 |
| distribution_observed | search/home feed/board evergreen discovery |
| trend_metrics | keyword trend rank、pin engagement、search volume proxy |
| evidence | Trends URL/API response/observed_at |
| known_biases | planning-heavy audience bias、seasonality bias |

### MVP 执行

```bash
python scripts/trend_adapters/pinterest.py import-trends \
  --input data/manual_imports/pinterest/2026-07-26-US-ecommerce.csv \
  --region US \
  --vertical ecommerce \
  --output data/trend_snapshots/pinterest/US/ecommerce.json
```

## 6.5 X / Twitter

### 来源

- X API recent search：如果有付费 API tier。
- Curated public lists/manual import：无 API 时的现实 fallback。
- 官方 developer docs：字段、权限、限制。

### 获取信号

| 信号 | 获取方法 |
|---|---|
| audience_observed | author bio/list/topic cluster/post text 中的 founder/dev/SMB 线索 |
| content_consumption_observed | high engagement posts/threads 的 hook、reply pattern、quote behavior |
| distribution_observed | follow graph、For You、reply/quote amplification proxy |
| trend_metrics | repost/like/reply/view(if available)、velocity、topic density |
| evidence | API query、post ids、list refs、observed_at |
| known_biases | API tier bias、elite-user bias、fast decay |

### MVP 执行

```bash
python scripts/trend_adapters/x_api.py collect \
  --region US \
  --vertical saas \
  --queries "AI agent small business,build in public SaaS,no code launch" \
  --window 7d \
  --output data/trend_snapshots/x/US/saas.json
```

如果没有 API：

```bash
python scripts/trend_adapters/x_api.py import-manual \
  --input data/manual_imports/x/2026-07-26-US-saas.yaml \
  --output data/trend_snapshots/x/US/saas.json
```

## 6.6 Instagram / Threads

### 来源

- Meta Instagram Platform / Graph API：授权业务账号和内容相关能力。
- Threads API：授权账号发布/insights 能力。
- Meta Content Library API：适用条件受限，通常不作为 SMB 生产默认依赖。
- 行业报告和人工样本。

### 获取信号

| 信号 | 获取方法 |
|---|---|
| audience_observed | 用户授权账号 audience insights；manual sample 的账号/内容语境 |
| content_consumption_observed | 自有账号 post/reels/story insights；行业高表现结构 |
| distribution_observed | stable layer + own-account reach/impression/save/share metrics |
| trend_metrics | 授权账号内容 metrics；manual trend brief |
| evidence | Graph API response、manual source、observed_at |
| known_biases | own account bias、no platform-wide trend access、report lag |

### MVP 执行

```bash
python scripts/trend_adapters/instagram_authorized.py import-insights \
  --input data/manual_imports/instagram/own_account_insights_2026-07-26.csv \
  --region US \
  --vertical creator-tool \
  --output data/trend_snapshots/instagram/US/creator-tool.json
```

不要恢复未登录 OG scraping，不要用第三方 scraping API。

## 6.7 LinkedIn

### 来源

- LinkedIn Marketing APIs：组织页、广告、analytics 等授权能力。
- 官方/行业 B2B report。
- 人工精选 post 样本。

### 获取信号

| 信号 | 获取方法 |
|---|---|
| audience_observed | Page analytics、manual sample 的 role/title/company context |
| content_consumption_observed | 高表现 B2B post 的结构、评论质量、document/carousel 使用 |
| distribution_observed | network/feed/company page/founder profile stable rules |
| trend_metrics | 授权 Page post metrics；manual rank |
| evidence | API/manual/report refs |
| known_biases | no full public post search、professional self-presentation bias |

### MVP 执行

```bash
python scripts/trend_adapters/linkedin_manual.py import \
  --input data/manual_imports/linkedin/2026-07-26-US-b2b-saas.yaml \
  --output data/trend_snapshots/linkedin/US/saas.json
```

## 6.8 Rednote / 小红书

### 来源

- 小红书聚光/蒲公英等官方商业/达人平台的人工导出。
- 小红书开放平台能力如可用则用于授权场景。
- 中文行业报告、运营人工精选笔记样本。

### 获取信号

| 信号 | 获取方法 |
|---|---|
| audience_observed | 类目/关键词/笔记评论语境/人工标注的人群和痛点 |
| content_consumption_observed | 标题、封面字、图文结构、测评/清单/教程/种草表达 |
| distribution_observed | 搜索 + 推荐流 + 类目词 + 封面点击逻辑 |
| trend_metrics | 后台关键词热度/人工 rank/互动数据如可见 |
| evidence | 后台导出文件、source URL、观察日期 |
| known_biases | manual sample bias、commercial platform bias、limited public API |

### MVP 执行

```bash
python scripts/trend_adapters/rednote_manual.py import \
  --input data/manual_imports/rednote/2026-07-26-CN-ecommerce.yaml \
  --output data/trend_snapshots/rednote/CN/ecommerce.json
```

Rednote 首期不要追求自动化。最可靠的是设计好人工导入模板：关键词、类目、标题样式、封面字、笔记结构、评论痛点、互动量级、观察日期、来源截图/链接。

## 7. Manual Import 模板

对难自动化平台，必须把人工观察标准化。

```yaml
platform: rednote
region: CN
language: zh
vertical: ecommerce
observed_from: 2026-07-19
observed_to: 2026-07-26
collector: ops_name
source_mix:
  - official_business_tool_export
  - manual_review
observations:
  - source_url: "https://www.xiaohongshu.com/..."
    source_description: "聚光关键词趋势 + 热门笔记人工观察"
    surface: "search_note"
    topic_label: "通勤包收纳"
    keywords: ["通勤包", "收纳", "打工人"]
    raw_metrics:
      likes: 1200
      comments: 83
      saves: 460
      rank_hint: "top 20 keyword result"
    audience_clues:
      explicit_self_descriptions: ["打工人", "通勤党"]
      pain_point_hints: ["包里太乱", "找东西慢", "想要体面但省钱"]
      buying_stage_hints: ["solution-aware", "comparison"]
    content_clues:
      hook: "通勤包这样收纳,早八不翻包"
      format: "multi-image note"
      cover_text: "早八通勤包收纳公式"
      structure: ["pain scene", "before-after", "item list", "purchase hint"]
    distribution_clues:
      entry_point: "keyword search"
      policy_risk: "low"
    limitations:
      - "manual sample, not platform-wide"
```

## 8. Normalizer 实现

### 8.1 输入

- raw API JSON
- official tool CSV/XLSX export
- manual YAML/CSV
- report extraction JSON

### 8.2 输出

统一输出 `trend_observation_snapshot`。

### 8.3 处理步骤

```text
1. Load raw records
2. Deduplicate by platform + source_url/post_id/topic keyword
3. Cluster topics by keyword + embedding/LLM semantic label
4. Extract audience clues
5. Extract content consumption clues
6. Compute trend_metrics index
7. Attach evidence refs
8. Attach known_biases
9. Validate schema and forbidden fields
10. Write snapshot
```

### 8.4 禁止字段校验

Validator 必须拒绝或清除：

```text
fit_verticals
fit_goal_types
relevance_to_atoms
recommended_for_app_type
should_use_for_cold_start
```

## 9. 调度与执行

### 9.1 刷新频率

| 平台/来源 | 刷新频率 | 执行方式 |
|---|---|---|
| YouTube API | 每周 | 自动 cron/GitHub Action/平台定时任务 |
| Reddit API | 每周，重点 subreddit 可每日 | 自动 |
| TikTok Creative Center | 1-2 周 | 人工导出 + importer；后续半自动 |
| Pinterest Trends | 2-4 周 | 人工导出 + importer；API 如授权则自动 |
| X API | 每日/每周 | 有 API 自动；无 API 人工 weekly brief |
| Instagram own-account insights | 每周 | 授权导出或 CSV import |
| LinkedIn | 每 2-4 周 | manual/API 授权导出 |
| Rednote | 1-2 周 | manual import 为主 |

### 9.2 推荐命令

```bash
python scripts/refresh_trend_observations.py --platform youtube --region US --vertical saas
python scripts/refresh_trend_observations.py --platform reddit --region US --vertical saas
python scripts/refresh_trend_observations.py --platform rednote --region CN --vertical ecommerce --mode manual --input data/manual_imports/rednote/latest.yaml
python scripts/validate_trend_observation.py data/trend_snapshots/reddit/US/saas.json
python scripts/build_trend_brief.py --snapshot data/trend_snapshots/reddit/US/saas.json --app-icp run_outputs/app_icp_vector.json --output run_outputs/trend_brief_reddit.json
```

### 9.3 生成链路不阻塞原则

- Launch Pack 生成时不强制实时抓取。
- 若 snapshot fresh，使用动态趋势。
- 若 snapshot stale，降级为 evergreen + warning。
- 若 snapshot missing，使用 stable playbook + registry，`score_confidence <= medium`。
- 用户点击“刷新趋势并重跑”时，最多等待 3-10 秒；超时使用旧数据并提示。

## 10. Storage 与版本管理

### 10.1 文件命名

```text
data/trend_snapshots/{platform}/{region}/{vertical}.json
```

每次刷新覆盖 latest，同时归档：

```text
data/trend_snapshots_archive/{platform}/{region}/{vertical}/{YYYY-MM-DD}.json
```

### 10.2 Snapshot 质量字段

```json
{
  "snapshot_quality": {
    "freshness": "fresh | stale | expired",
    "coverage": "high | medium | low",
    "source_confidence": "high | medium-high | medium | low",
    "known_biases": []
  }
}
```

### 10.3 Freshness 判断

```text
if now <= expires_at -> fresh
if expires_at < now <= expires_at + grace_period -> stale
else -> expired
```

## 11. 如何进入 Stage 2

Stage 2 不直接用 raw snapshot 给结论。执行顺序：

```text
1. Stage 1 生成 app_icp_vector
2. Load latest snapshot for platform-region-vertical
3. build_trend_brief.py 根据 built app end-user ICP 做 selected/rejected observations
4. Stage 2 计算 audience_opportunity / mindset / expression / distribution / conversion / evidence
5. Stage 3 只使用 selected_observations 生成平台原生内容策略
```

`build_trend_brief.py` 需要输出：

```json
{
  "selected_observations": [
    {
      "observation_id": "obs_001",
      "intersection_scores": {
        "end_user_identity_overlap": 8,
        "pain_overlap": 9,
        "mindset_fit": 7,
        "conversion_fit": 6
      },
      "selection_reason": "Observed SMB operators complain about manual admin; the built app promises automation setup in 15 minutes. This is end-user pain overlap, not builder identity overlap.",
      "content_constraints": ["lead with problem", "soft CTA", "no direct ad tone"],
      "confidence": "medium-high"
    }
  ],
  "rejected_observations": [
    {
      "observation_id": "obs_004",
      "reason": "high volume but entertainment audience and no pain overlap"
    }
  ]
}
```

## 12. MVP 实施路线

### Week 1：Schema + 骨架

- 新增 `trend_observation_schema.json`。
- 新增 `TrendAdapter` base class。
- 新增 `validate_trend_observation.py`。
- 新增 manual import schema。
- 把现有 TikTok trend snapshot 迁移为 observation snapshot。

### Week 2：YouTube + Reddit 自动化

- 包装现有 `fetch_youtube_metadata.py` 为 `trend_adapters/youtube.py`。
- 新增 `trend_adapters/reddit.py`。
- 实现 index normalization。
- 产出 `youtube/US/saas.json` 和 `reddit/US/saas.json` 样例。

### Week 3：Manual 高价值平台

- 新增 `rednote_manual.py`、`linkedin_manual.py`、`tiktok_creative_center.py import`。
- 完成 manual YAML 模板和 validator。
- 运营可以每周填 5-20 条高质量 observation。

### Week 4：接入 Stage 2/3

- 新增 `build_trend_brief.py`。
- Stage 2 读取 brief 计算 audience intersection。
- Stage 3 使用 selected observations 生成平台原生策略。
- Stage 5 输出 freshness / source confidence warning。

## 13. 验收标准

| 验收项 | 标准 |
|---|---|
| 可获取 | YouTube/Reddit 至少可自动产出 snapshot；Rednote/TikTok/LinkedIn 至少可 manual import |
| 可追溯 | 每个 observation 至少 1 条 evidence |
| 可降级 | snapshot missing/stale/expired 都能生成 Launch Pack，但 confidence 正确降低 |
| 不污染 | snapshot 不包含 `fit_verticals`、`fit_goal_types`、`relevance_to_atoms` |
| 可用于评分 | Stage 2 能从 snapshot + app_icp_vector 输出 audience_intersection 和 subscores |
| 合规 | 不登录抓取、不用第三方 scraping API、不落 token/cookie |
| 可维护 | 每个平台 adapter 写清 access mode、字段可得性、known_biases |

## 14. 官方/高可信来源清单

实现前需要按当日重新核验以下来源：

- YouTube Data API `search.list` / `videos.list`: https://developers.google.com/youtube/v3/docs/search/list , https://developers.google.com/youtube/v3/docs/videos/list
- Reddit API docs: https://www.reddit.com/dev/api/
- Reddit Data API Terms: https://www.redditinc.com/policies/data-api-terms
- TikTok Creative Center: https://ads.tiktok.com/business/creativecenter
- TikTok developer docs / Research API: https://developers.tiktok.com/products/research-api/
- X API docs: https://docs.x.com/x-api
- Instagram Platform docs: https://developers.facebook.com/docs/instagram-platform
- Meta Content Library API: https://developers.facebook.com/docs/content-library-api
- Threads API: https://developers.facebook.com/docs/threads
- LinkedIn Marketing APIs: https://learn.microsoft.com/en-us/linkedin/marketing/
- Pinterest API v5: https://developers.pinterest.com/docs/api/v5/
- Pinterest Trends: https://trends.pinterest.com/
- 小红书聚光平台: https://ad.xiaohongshu.com/
- 小红书蒲公英平台: https://pgy.xiaohongshu.com/

## 15. 关键取舍

- 能自动的先自动：YouTube、Reddit。
- 不能自动但有官方后台的，先做导入：TikTok、Pinterest、Rednote、LinkedIn。
- 没有授权就不抓：Instagram、LinkedIn、Rednote 不做未登录 scraping。
- 趋势数据永远只做 observation，不做 app fit 结论。
- 真正的适配判断发生在 built app end-user ICP 与 observation 的运行时交集计算。
