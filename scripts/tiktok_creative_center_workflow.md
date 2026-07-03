# TikTok Creative Center Refresh Workflow

## 目的

TikTok 独有的官方开放趋势数据入口,是 TikTok playbook 相对 IG 的最大差异化能力。每 2-4 周走一次流程,把 4 类数据落到 `data/tiktok_trend_snapshot.json`,供 playbook §5 hook 建议 / §6 hashtag mix / §9 sound recommendation 引用。

---

## 前置约束

### 合规
- Creative Center 是 TikTok 官方公开工具,无登录门槛 → **合规,可直接抓**
- 不走任何第三方 scraping API / 不走登录 session / 不缓存视频原素材
- 引用具体 hashtag / sound 时用官方公开元数据(名字 + growth rate),不复述创作者具体作品

### 时效
- TikTok trending 生命周期 **7-14 天**
- Snapshot 数据超过 4 周 → 只作为 **历史 pattern 参考**,不再作为 "借势素材"(playbook §9 使用时必须核查 `$last_refresh`)
- 每次 refresh 更新 `$last_refresh` + `$last_refresh_scope` + `$next_refresh_due`

### 数据边界
- 只抓 trending 层 metadata(name / growth / video count)+ 结构 pattern(hook / length / visual)
- **不抓具体广告素材**、**不抓具体创作者 handle 名单**(Creative Center 有,但不是我们需要的)
- 广告结构 pattern 抓到 `top_ads_patterns[]` —— 归纳 pattern_name / hook_type / video_length_range / visual_style,而不是记录单个广告

---

## 主入口与子页地图

**入口**:https://ads.tiktok.com/business/creativecenter

| 数据类型 | Creative Center 路径 | Snapshot 字段 |
|----------|---------------------|---------------|
| Trending Hashtags | Inspiration → Popular → Hashtag | `trending_hashtags[]` |
| Trending Sounds | Inspiration → Popular → Song | `trending_sounds[]` |
| Top Ads(结构 pattern) | Top Ads Library | `top_ads_patterns[]` |
| Keyword Insights(SEO) | Keyword Insights | `keyword_insights[]` |

**核心过滤维度**(每个子页都支持):
- **Region**:US(必选)/ UK / DE / AU / CA —— Atoms 主要市场
- **Industry**:Tech / Ecommerce / Beauty / Food / Finance —— 按 SaaS / Ecom / Creator 三业务类型映射
- **Time window**:Last 7 days(borrow 素材首选)/ Last 30 days(pattern 归纳)/ Last 120 days(长期趋势对照,不作为借势素材)

---

## 抓取方式

### 首选:WebFetch

Creative Center 页面公开无登录,WebFetch 可直接读取。示例 prompt 模式:

```
Please read this TikTok Creative Center page and extract for me:
- The top 20 trending hashtags shown
- For each: the tag name, posts count, and growth rate (7d or 30d)
- Categorize by which industry filter is currently applied
- Skip any hashtag with < 10K posts (too niche/noise)

URL: https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag?period=7&region=US
```

**每类子页各跑一次 WebFetch,按 region × industry 组合可能需要 3-5 次 WebFetch(每个 region 一次,若 industry 有明显分层再拆)。**

### 兜底:Playwright(仅在 WebFetch 拿不到数据时启用)

若 Creative Center 页面加了动态渲染 / JS 门槛导致 WebFetch 空回,启用 playwright:

```javascript
// 伪代码,实际脚本按需扩展 — 目前不作为默认路径
await page.goto('https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag?period=7&region=US');
await page.waitForSelector('[data-testid="hashtag-item"]');
const items = await page.$$eval('[data-testid="hashtag-item"]', els =>
  els.slice(0, 20).map(el => ({
    tag: el.querySelector('.tag-name')?.innerText,
    posts_count: el.querySelector('.posts')?.innerText,
    growth: el.querySelector('.growth')?.innerText,
  }))
);
```

**注意**:playwright 兜底目前未预置脚本,首次遇到 WebFetch 失败时再决定是否值得投入(维护 selector 成本高,TikTok 前端结构变化频繁)。

---

## 4 类数据的抓取模板

### 1. Trending Hashtags

**URL**:`https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag?period=<7|30>&region=<US|UK|...>&industry=<optional>`

**抓取要点**:
- 取 top 15-25 条(过多噪音,过少不成 pattern)
- 每条记录:`tag / category / posts_count / growth_rate_7d / growth_rate_30d / region / industry / snapshot_date`
- **过滤**:posts_count < 10K 直接丢(太 niche 或伪 trending)
- **打标 atoms_relevance**:一句话说明对 SaaS / Ecom / Creator 哪类业务有价值,以及在 playbook §6 hashtag 5-slot mix 里适合哪个 slot

**目标产出条数**:每次 refresh 每 region 15-20 条,总计 40-80 条

### 2. Trending Sounds

**URL**:`https://ads.tiktok.com/business/creativecenter/inspiration/popular/song?period=<7|30>&region=<US|...>`

**抓取要点**:
- 取 top 15-20 条(sound 的选择成本远高于 hashtag,追求精而非多)
- 每条记录:`sound_id / title / artist / video_count / growth_rate_7d / category / region / license_type / snapshot_date`
- **过滤**:非 commercial-safe license 直接丢(SaaS / Ecom 商业账号用了会 muted)
- **打标 atoms_relevance**:说明适合哪类内容(tutorial / hook / transition)+ 建议节奏
- **必填 decay_estimate**:结合 growth rate + video_count 估计剩余窗口(5-10 天 / 10-20 天 / 已过峰)

**目标产出条数**:每次 refresh 每 region 10-15 条,总计 30-60 条

**重要**:sound 是 TikTok 独有的关键分发信号 —— 借势 trending sound 是冷启动加速核心手段。此层数据是 §5 §9 引用的高价值来源。

### 3. Top Ads Patterns

**URL**:`https://ads.tiktok.com/business/creativecenter/topads?region=<US|...>&industry=<optional>`

**抓取要点**:
- **不抓具体广告**,而是归纳 pattern
- 每条 pattern 记录:`pattern_name / hook_type / video_length_range / visual_style / industry / snapshot_date`
- **归纳方式**:浏览 top 30-50 个广告,聚类出 5-10 个通用 pattern(如 "before-after transformation" / "voice-over unboxing" / "founder-to-camera build-in-public")
- **打标 atoms_relevance**:说明哪类业务适用 + 制作难度提示

**目标产出条数**:每次 refresh 每 industry 5-8 个 pattern,总计 15-25 条

### 4. Keyword Insights

**URL**:`https://ads.tiktok.com/business/creativecenter/keyword-insights?region=<US|...>&industry=<optional>`

**抓取要点**:
- TikTok SEO 层数据 —— 用户实际搜索关键词
- 每条记录:`keyword / search_volume_relative / growth_7d / industry / region / snapshot_date`
- **过滤**:纯品牌名(如 "amazon" "nike")丢弃 —— 我们要的是 SaaS / Ecom / Creator 类目关键词
- **打标 atoms_relevance**:说明可以放在 caption 前 100 字符 / voiceover / hashtag 中的哪一层

**目标产出条数**:每次 refresh 每 industry 10-15 条,总计 30-50 条

---

## Workflow(每次 refresh 的完整步骤)

### Step 0 — 确认前置

- 检查 `data/tiktok_trend_snapshot.json` 的 `$last_refresh` 时间
- 若距今 < 2 周 → skip(数据还新)
- 若距今 > 6 周 → 全量重抓(旧数据无参考价值)
- 若距今 2-4 周 → 增量刷新(保留 60% 老数据 + 40% 新替换)

### Step 1 — WebFetch 4 类子页

按 region × industry 组合跑 WebFetch。US Tech / US Ecom / US Beauty 建议每次都跑,其他 region 按 sprint 需要拉。

**建议顺序**:hashtag → sound → keyword insights → top ads(top ads 归纳最费时,放最后)

### Step 2 — 结构化整理

- 每类抓取结果按 snapshot json 的 `$structure_ref` 格式化
- **必须给每条 entry 加 `atoms_relevance` 字段**(一句话,说清对 Atoms 用户场景的价值)
- 对 sound 类,**必须估 decay_estimate**

### Step 3 — 写入 snapshot json

- 更新 `$last_refresh`(ISO date)
- 更新 `$last_refresh_scope.regions` / `industries` / `time_window`
- 更新 `$next_refresh_due`(默认 +3 周)
- 覆盖或增量合并 `entries[]`(推荐覆盖,不做历史堆积)

### Step 4 — Log 记录

在 `scripts/README.md` TikTok 章节记录一行 log:

```
- YYYY-MM-DD: Creative Center refresh, regions=[US, UK], industries=[Tech, Ecom, Beauty], entries=[hashtag:32, sound:24, top_ads:12, keywords:38]
```

### Step 5 — 通知(可选)

若本次 refresh 出现明显趋势变化(如某个 hashtag 一周内 growth >200%,或某类 pattern 新出现),在对话中标注,提示是否需要立即用于内容创作 brief。

---

## 与 playbook 各节的引用关系

| Playbook 节 | 用 snapshot 的哪个字段 | 用法 |
|-------------|------------------------|------|
| §5 hook_patterns | `top_ads_patterns[].hook_type` | 具体 hook 建议时,结合当期热门 pattern |
| §6 mix_strategy | `trending_hashtags[]` | 5-slot mix 的 slot 2/3(niche mid-tag)从这里筛 |
| §6 hashtag SEO | `keyword_insights[]` | Caption 前 100 字符与 voiceover 关键词候选 |
| §9 winning structures | `trending_sounds[]` | 生成 content brief 时,若在 sound decay 窗口内,主动建议借势 sound |
| §9 winning structures | `top_ads_patterns[]` | Ads pattern 中反复出现的结构可下沉进 §9(需 2+ 次连续 refresh 验证) |

**核心原则**:snapshot 提供 **短期借势素材**,不提供 **长期结构**。长期结构走 case studies + manual supplements。

---

## Fallback 与失败处理

| 情况 | 处理方式 |
|------|----------|
| WebFetch 返回空 / 只读到 header 无 data | 走 playwright 兜底(需按需构建脚本) |
| Creative Center UI 改版导致提取失败 | 记录到 `scripts/README.md` TikTok changelog,人工在页面直接看后手填 5-10 条最关键的 |
| Region 数据缺失(如 DE 无 Tech 数据) | 跳过,不强填 —— snapshot 只覆盖有真实数据的 region × industry |
| Sound license 无法判断 | 标 `license_type: "unknown"`,不建议直接用 |

---

## 与其他数据文件的独立性

- `tiktok_case_studies.json`:长期结构模式,**12 个月刷新**
- `tiktok_manual_supplements.md`:人工补齐,**按增量**
- `tiktok_trend_snapshot.json`:短期素材,**2-4 周刷新** ← 本文档负责

三者互相独立,不做 merge。playbook §9 引用时按需分别取。

---

## v0.1 → v0.2 首次 refresh 目标

- [ ] Region:US(必)+ 至少 1 个次选 region
- [ ] Industry:Tech + Ecom + Beauty(SaaS / Ecom / Creator 三业务类型代表)
- [ ] Time window:Last 7 days(hashtag + sound)/ Last 30 days(pattern + keyword)
- [ ] 4 类数据全部产出,总计 entries ≥ 80 条
- [ ] snapshot json 三个 `$last_refresh` / `$last_refresh_scope` / `$next_refresh_due` 全部更新
- [ ] `scripts/README.md` TikTok 章节留 log
