# Just-in-time Demand Probe 实时轻量方案

## 1. 为什么要重做

上一版“趋势观测层”虽然概念完整，但对 skill 主链路来说过重：

- 用户触发 skill 时才知道 app 上下文，因此真正相关的话题必须 request-time 生成。
- 如果 request-time 再做多平台、多 query、多轮扩展、多指标归一，链路长、外部依赖多、失败概率高。
- 如果不做 request-time，只依赖离线趋势库，又很容易和具体 app ICP / JTBD 脱节。
- 如果只搜 app 功能关键词，又会落入“产品语言 ≠ 终端用户需求语言”的低召回问题。

所以这版方案改为：**主链路只做轻量实时需求探针，不做完整趋势采集。**

目标不是“实时理解全平台趋势”，而是在 5-10 秒内回答一个更小但更有用的问题：

> 对这个 app，当下是否能在 2-3 个最可能的平台上找到少量真实需求表达、活跃内容或社区入口，用来校准首发内容包？

## 2. 核心设计原则

1. **先选平台，再查数据**：不要全平台抓。先用稳定层选出最多 3 个候选平台，再对这些平台做轻量探针。
2. **先生成需求探针，不生成泛话题**：query 来自 built app end-user ICP / pain / JTBD / alternatives / trigger moments，而不是平台热榜。
3. **只拿最小证据包**：每个平台最多 2-3 个 query，每个 query 最多 5-8 条结果。
4. **硬超时、可降级**：实时探针失败不阻塞 Launch Pack，只降低 confidence。
5. **不追求完整趋势指标**：request-time 只做 relevance / activity / intent / surface viability 的轻量判断。
6. **后台趋势库是增强，不是主链路依赖**：离线数据只作为 cache / fallback / enrichment。

## 3. 新架构

```text
User inputs
  v
Stage 1 App Understanding
  - app_icp_vector
  - demand_probe_pack(max 8 probes)
  v
Stage 2a Platform Shortlist
  - stable platform matrix
  - max 3 platforms
  v
Stage 2b Just-in-time Probe(optional, hard timeout)
  - run 2-3 queries per selected platform
  - fetch top 5-8 lightweight results
  - summarize evidence only
  v
Stage 2c Fit Score
  - stable fit + realtime evidence adjustment
  - confidence and fallback state
  v
Stage 3/4 Generate Launch Pack
```

主路径即使完全没有实时数据，也能完成：

```text
no realtime evidence -> stable playbook strategy -> confidence <= medium -> no “current trend” wording
```

## 4. “话题”到底是什么

这版不再使用“话题”这个宽泛词，改成 **Demand Probe**。

Demand Probe 是一个小型检索意图，用来找“目标用户正在如何表达这个需求”。它不是：

- 平台所有热点
- 随机关键词
- app 功能词直接搜索
- LLM 编造的趋势

它是由 app 上下文生成的 6 类终端用户需求语言 seed：

| Probe 来源 | 示例 | 目的 |
|---|---|---|
| End-user identity | Shopify seller, freelancer, local shop owner, 小商家 | 找人群所在位置 |
| Pain | chasing invoices, manual admin, too many tools | 找真实问题表达 |
| JTBD | improve product page conversion, get paid faster, schedule posts | 找终端用户任务场景 |
| Alternative/workaround | spreadsheet, Notion template, Zapier, Canva | 找替代方案和迁移机会 |
| Trigger moment | product launch, first client, Black Friday, new store | 找发生时机 |
| Desired outcome | save time, get more leads, convert visitors | 找购买动机 |

最终生成的不是 50 个关键词，而是最多 8 个 probe，例如：

```json
{
  "probe_id": "p03",
  "intent": "problem_search",
  "user_language_query": "freelancers chasing invoices clients not paying",
  "icp_terms": ["freelancer", "solo business"],
  "pain_terms": ["chasing invoices", "clients not paying"],
  "platform_surfaces_hint": ["reddit_search", "youtube_search"],
  "must_not_include": ["product name", "brand slogan"]
}
```

## 5. 复杂度控制

### 5.1 Probe Budget

| 项 | 上限 |
|---|---:|
| Demand probes per request | 8 |
| Platforms probed | 3 |
| Queries per platform | 3 |
| Results per query | 5-8 |
| Total fetched items | 60 以内 |
| Hard timeout | 默认 8 秒,最大 12 秒 |
| LLM summarization calls | 1 次合并 summarizer |

### 5.2 平台短名单先于检索

先用稳定层打一个粗分，只选最可能的 2-3 个平台做实时探针。

```text
shortlist_score =
  ICP-platform stable overlap
+ content format feasibility
+ conversion path feasibility
+ market/platform availability
- production difficulty
```

例如：

- AI/SaaS/build-in-public：优先 X、Reddit、YouTube；TikTok 只在 demo 可视化强时加入。
- Ecom/visual product：优先 TikTok、Instagram、Pinterest、Rednote(CN)。
- B2B/professional buyer：优先 LinkedIn、YouTube、X；Reddit 只用于 problem validation。
- Local business：优先 Facebook、Instagram、Rednote/Douyin(CN)、Google/YouTube search。

## 6. 实时探针可用来源

### 6.1 MVP 只支持高稳定来源

| 平台 | 实时探针方式 | 可行度 | 说明 |
|---|---|---|---|
| YouTube | Data API `search.list` + `videos.list`,或 oEmbed fallback | 高 | 官方 API；适合教程/搜索意图/内容结构 |
| Reddit | Reddit API search + subreddit hot/top | 高 | 官方 API；适合痛点/社区/求助表达 |
| Web Search fallback | 搜索公开网页/平台页面摘要 | 中 | 用于没有平台 API 时找公开结果；只取摘要和 URL |
| X | X API recent search 或 manual import | 中低 | API 成本/权限不稳定；无 API 不进默认实时路径 |
| Pinterest | Trends/API 或 manual export | 中 | 适合后台/离线刷新，不建议每次实时查 |
| TikTok | Creative Center manual/cache | 中 | 不建议 request-time 抓 UI；用最近缓存 |
| Instagram/LinkedIn/Rednote | 授权/人工/cache | 低 | 不做 request-time 全站抓取 |

MVP 实时只建议自动跑：**YouTube + Reddit + Web Search fallback**。这已经能覆盖大量 SMB SaaS / creator tool / knowledge product 的真实需求表达。其他平台用 stable playbook + 最近 cache。

### 6.2 官方来源说明

实现时需按当日核验官方文档：

- YouTube Data API `search.list` / `videos.list`
- Reddit API docs / Reddit Data API Terms
- X API docs,仅在付费/授权可用时启用
- TikTok Creative Center,优先 cache/manual import,不作为 request-time 硬依赖
- Meta / LinkedIn / Rednote 只走授权或 manual/cache

## 7. 数据结构

### 7.1 `demand_probe_pack`

```json
{
  "app_id": "runtime",
  "generated_at": "2026-07-26T00:00:00Z",
  "icp_summary": "Shopify sellers improving product-page conversion",
  "probes": [
    {
      "probe_id": "p01",
      "intent": "pain_expression",
      "query": "Shopify seller product page traffic no sales",
      "language": "en",
      "market": "US",
      "source_terms": {
        "icp": ["Shopify seller"],
        "pain": ["landing page not converting"],
        "jtbd": ["launch product"],
        "alternative": ["Carrd", "Webflow", "Notion page"]
      },
      "priority": 0.92
    }
  ],
  "constraints": {
    "max_probes": 8,
    "avoid_product_keywords_only": true,
    "prefer_user_language": true
  }
}
```

### 7.2 `realtime_probe_result`

```json
{
  "platform": "reddit",
  "probe_id": "p01",
  "query": "Shopify seller product page traffic no sales",
  "status": "success | timeout | skipped | error",
  "results": [
    {
      "result_id": "r01",
      "surface": "subreddit_search",
      "title": "My landing page gets traffic but no signups",
      "url": "https://www.reddit.com/r/SaaS/...",
      "published_at": "2026-07-24T00:00:00Z",
      "metrics": {
        "score": 128,
        "comments": 47
      },
      "text_excerpt": "short excerpt only",
      "evidence_type": "official_api"
    }
  ],
  "latency_ms": 430,
  "known_biases": ["search_result_bias", "no_demographic_ground_truth"]
}
```

### 7.3 `opportunity_evidence_brief`

这是 Stage 2 真正读取的轻量对象。

```json
{
  "platform": "reddit",
  "status": "usable | weak | unavailable",
  "freshness": "realtime",
  "evidence_count": 9,
  "matched_probe_ids": ["p01", "p03"],
  "audience_clues": ["Shopify sellers", "store operators", "problem-aware users"],
  "pain_clues": ["traffic but no signups", "unclear positioning", "manual launch workflow"],
  "content_clues": ["specific problem title", "transparent founder answer", "comment-heavy discussion"],
  "distribution_clues": ["subreddit search", "comment-first entry", "anti-promotion norm"],
  "activity_clues": {
    "volume": "medium",
    "velocity": "fresh",
    "engagement": "high-comment-depth",
    "saturation": "medium"
  },
  "recommended_use": "calibrate angle and wording, not claim broad trend",
  "confidence": "medium-high",
  "evidence_refs": ["reddit:p01:r01", "reddit:p03:r02"],
  "warnings": ["sample limited to selected subreddits"]
}
```

注意：这里没有 `fit_verticals`、`fit_goal_types`、`relevance_to_atoms`。

## 8. 工程实现

### 8.1 新增脚本

```text
scripts/realtime_probe/
  build_demand_probe_pack.py
  select_platform_shortlist.py
  run_realtime_probe.py
  adapters/
    youtube_probe.py
    reddit_probe.py
    web_search_probe.py
    cached_platform_probe.py
  summarize_opportunity_brief.py
  validate_probe_output.py
```

### 8.2 主命令

```bash
python scripts/realtime_probe/run_realtime_probe.py \
  --app-context run_outputs/app_context.json \
  --intent-profile run_outputs/intent_profile.json \
  --platform-scope auto \
  --timeout-ms 8000 \
  --output run_outputs/opportunity_briefs.json
```

### 8.3 执行伪代码

```python
def run_realtime_probe(app_context, intent_profile, platform_scope=None):
    icp = build_app_icp_vector(app_context, intent_profile)
    probes = build_demand_probe_pack(icp, max_probes=8)

    platforms = select_platform_shortlist(
        icp=icp,
        platform_scope=platform_scope,
        max_platforms=3,
    )

    tasks = []
    for platform in platforms:
        adapter = get_probe_adapter(platform)
        if adapter.mode not in ["realtime_api", "cache"]:
            tasks.append(skipped(platform, reason="no stable realtime adapter"))
            continue
        tasks.append(adapter.probe(probes.top_for(platform, max_queries=3)))

    raw_results = run_parallel(tasks, timeout_ms=8000)
    briefs = summarize_opportunity_briefs(raw_results, icp)
    return validate_or_degrade(briefs)
```

## 9. Query 生成方法

### 9.1 不做多轮扩展

为了稳定，不做平台内递归扩展。只做一轮 query generation：

```text
input app -> 8 demand probes -> platform probe -> brief
```

不做：

```text
query -> related query -> related community -> more query -> clustering -> another fetch
```

这条链路看起来聪明，但工程稳定性很差。

### 9.2 Query 模板池与 variants

按 built app end-user ICP 生成模板池,但不要把模板当成唯一 query。每个 probe 保留兼容用 `query`,同时尽量输出 `query_variants`:

```text
{end_user_identity} {pain}
{end_user_identity} how to {jtbd}
{pain} {workaround_category}
best way to {desired_outcome} for {end_user_identity}
{trigger_moment} {pain}
{workaround_category} vs {desired_outcome}
```

Variant types:

| Variant | 作用 | 示例 |
|---|---|---|
| `long_tail_precision` | 找高相关痛点/任务证据 | `Shopify seller product page traffic no sales` |
| `keyword_recall` | 长尾召回不足时扩大相关结果池 | `product page conversion` + `traffic no sales` + `Shopify` |
| `platform_native` | 适配平台搜索习惯 | Reddit: `product page traffic no sales Shopify`; YouTube: `product page conversion Shopify tutorial`; Web: `site:reddit.com/r ecommerce product page traffic no sales` |

Planning rules:

- 每个平台最多 3 个 query 时,尽量混合 long-tail 和 keyword recall,不要全选相似长尾。
- Reddit 优先 pain / workaround / trigger moment;YouTube 优先 how-to / desired outcome / comparison;web_search 可作为 evidence locator。
- 宽召回 query 仍必须包含至少一个 end-user/pain/JTBD 线索,不得退化成 built app 功能词、品牌词或 Atoms 平台词。
- Named competitors 只能来自用户输入、cache、授权数据或 web evidence;没有证据时用 workaround category。

## 10. Fit Score 如何使用实时结果

Stage 2 不因实时结果缺失而崩溃。新的评分由两部分组成：

```text
stable_fit_score = stable platform matrix + playbook + app_icp_vector
realtime_adjustment = -5..+10 based on opportunity_evidence_brief
final_fit_score = clamp(stable_fit_score + realtime_adjustment, 0, 100)
```

实时探针只做小幅调整：

| 证据 | 调整 |
|---|---:|
| 找到 2+ 高相关需求表达,且互动活跃 | +6 到 +10 |
| 找到相关内容但活动弱 | +2 到 +5 |
| 找到内容但与 ICP 或 pain 弱相关 | 0 |
| 发现平台/社区强反营销或入口不适合 | -3 到 -5 |
| 探针失败/超时 | 0,但 confidence 降级 |

这样做的好处是：实时数据增强质量，但不会决定生死。

## 11. 缓存策略

### 11.1 缓存 Key

```text
platform + market + language + icp_cluster + demand_cluster + week
```

例如：

```text
reddit|US|en|solo-founder-saas|landing-page-conversion|2026-W31
```

### 11.2 TTL

| 数据 | TTL |
|---|---:|
| Reddit/YouTube realtime probe result | 24-72 小时 |
| Opportunity brief | 24 小时 |
| Platform stable matrix | 30-90 天 |
| Manual Rednote/LinkedIn/TikTok cache | 7-14 天 |

### 11.3 命中缓存时

如果 cache fresh，直接使用，不再实时探针。这样大幅降低失败率和成本。

## 12. 降级路径

| 情况 | 处理 |
|---|---|
| 全部实时探针失败 | 使用 stable playbook + platform matrix，`confidence <= medium` |
| 某个平台失败 | 该平台不加 realtime adjustment，不阻塞其它平台 |
| query 结果全低相关 | 保持 stable score，Stage 3 不写 trend/why-now |
| API rate limit | 读 cache；无 cache 则跳过 |
| 网络超时 | 8 秒硬停；输出 partial results |
| LLM summarizer 失败 | 使用规则摘要：title keywords + metrics + source refs |

## 13. 为什么这个方案更可行

| 旧重方案 | 新轻方案 |
|---|---|
| 多平台全量趋势采集 | 最多 3 平台轻量探针 |
| 多轮 query 扩展 | 单轮 8 个 demand probes |
| snapshot 是主路径依赖 | realtime evidence 是可选增强 |
| 指标归一和 audience 抽取都很重 | request-time 只做 brief,离线再做深处理 |
| 失败会影响整条链路 | 失败只降低 confidence |
| 试图覆盖所有平台 | MVP 只自动化 YouTube/Reddit/Web fallback |

## 14. MVP 落地计划

### Week 1: 主链路骨架

- `build_demand_probe_pack.py`
- `select_platform_shortlist.py`
- `opportunity_evidence_brief` schema
- cache 读写工具

### Week 2: 两个稳定 adapter

- `youtube_probe.py`: Data API / oEmbed fallback
- `reddit_probe.py`: Reddit API search + subreddit hot/top
- `web_search_probe.py`: 作为兜底，不依赖平台登录

### Week 3: Stage 2 接入

- `stable_fit_score` 与 `realtime_adjustment` 分离
- 输出 `probe_status`、`evidence_refs`、`confidence`
- Stage 3 只在 `brief.status == usable` 时使用实时内容语境

### Week 4: 质量评测

建立 20 个测试 app：

- 5 SaaS/AI tool
- 5 ecommerce
- 5 creator tool
- 5 local/service business

每个测试：

- 是否能在 8 秒内返回
- 失败时是否可降级
- query 是否像终端用户需求语言而不是产品语言
- 内容是否避免伪造“当前热门”
- 首发包是否比纯 playbook 更贴近需求表达

## 15. 验收标准

| 项 | 标准 |
|---|---|
| 稳定性 | 无实时数据时 100% 可生成 |
| 延迟 | realtime probe P95 <= 10 秒 |
| 复杂度 | 单次最多 3 平台、8 probes、60 fetched items |
| 质量 | 每个平台 brief 至少引用 2 条 evidence 才能 `usable` |
| 真实性 | 没有 evidence 不得写“当前趋势/最近大家都在” |
| 降级 | timeout/rate limit/API error 不阻塞 Launch Pack |
| 可维护 | 新平台默认走 cache/manual,只有 adapter 稳定后进入 realtime shortlist |

## 16. 推荐最终取舍

不要把实时趋势系统做成主链路大脑。主链路大脑应该是：

```text
built app end-user ICP + stable platform matrix + platform-native renderer
```

实时探针只承担一个轻量角色：

```text
找到少量当前真实用户表达,校准 wording / angle / surface / confidence
```

这样可以同时保住三件事：

- **可行性**：MVP 只依赖少数高可行数据源。
- **稳定性**：实时失败不阻塞生成。
- **质量**：有实时证据时，内容能更接近当下终端用户需求语言；无证据时，不伪造趋势。



