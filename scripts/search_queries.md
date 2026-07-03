# Search Queries — Instagram Playbook Research

## 使用方式

以 **Category B 博客案例** 为主链路,Category C 官方文档为辅助权威源。跑完汇总到 `data/ig_industry_urls.txt`,交给 WebFetch 逐篇提取。

**执行者**:Agent(通过 WebSearch 工具)
**执行时间**:P1.1 阶段
**目标产出**:15-20 篇高质量博客文章 URL + 5-8 篇官方文档

---

## ⚠️ Category A — 已废弃

原计划:site:instagram.com/p/ 定位 IG 原生公开 post → OG meta 抓取。

**废弃原因**:2026-07-02 实测,IG 对未登录请求剥离 OG meta。相关脚本(`extract_og_metadata.py`)与产物(`_deprecated_*`)保留作为证据,但不再使用。

**如需 IG 原生数据**:走 Category D(人工补齐,见 `data/ig_manual_supplements.md`)。

---

## Category B(主链路)— 行业博客案例分析

博客发布方通常公开"高转化 IG 案例"分析,含真实 engagement 数据 + 编辑视角的模式归纳。

### B1 — 通用 IG 数据 / benchmark 报告

```
Later blog instagram case study 2024 OR 2025
Later blog instagram engagement benchmark
Buffer blog instagram growth case study
Hootsuite instagram case study small business
Sprout Social instagram benchmark 2024 2025
RivalIQ instagram engagement benchmark 2024 2025
SocialInsider instagram carousel reel report 2024 2025
```

### B2 — 分业务类型深挖

```
Later blog SaaS instagram marketing case study
Buffer instagram ecommerce case study small brand
SocialInsider creator economy instagram 2024
Hootsuite instagram algorithm 2025 update ranking
Sprout Social instagram best practices SMB 2024
Later blog small business instagram case study
Buffer instagram growth story indie founder
```

### B3 — 具体机制(算法 / hashtag / caption)

```
instagram reels algorithm 2024 2025 change explained
instagram hashtag strategy 2025 small business
instagram caption length engagement study 2024 2025
instagram optimal posting time SMB 2024 2025
instagram carousel vs reel engagement comparison 2024
"instagram algorithm" ranking signals 2025
```

### B4 — 分渠道内容形式

```
instagram reels case study small brand growth
instagram carousel best practices SaaS 2024 2025
instagram story engagement rate benchmark 2024
instagram launch post format high conversion
```

**筛选标准**(执行后 Agent 手工筛):
- ✅ 保留:含具体品牌名 + 具体 engagement 数字 + 内容拆解
- ❌ 剔除:纯 SEO 灌水文、无具体案例的 tips list、pay-to-play 广告平台报告

---

## Category C — Meta 官方与 Instagram 官方资源

作为权威来源引用(algorithm、best practice 的官方说法)。

```
site:business.instagram.com playbook creator
site:business.instagram.com best practices small business
site:help.instagram.com algorithm ranking
site:creators.instagram.com content strategy
"Meta for Business" instagram best practices 2024 2025
"Instagram Creator" playbook 2024 2025
```

---

## Category D — 人工补齐(替代已废弃的 A)

用户提供样本,由 Agent 在 `data/ig_manual_supplements.md` 里按模板整理。

**优先补齐方向**:
- SaaS/AI 2025 launch post(博客大多覆盖 2024 及以前)
- Creator 类 solo builder / indie hacker 样本
- 中位表现样本(500-3000 likes,平衡博客的"高转化 bias")

---

## 执行 checklist

- [ ] Category B1:跑 5-7 条 query,收集 8-10 篇通用报告 URL
- [ ] Category B2/B3/B4:跑 10-15 条 query,收集 15-20 篇业务/机制 URL
- [ ] Category C:跑 4-6 条 query,收集 5-8 篇官方文档
- [ ] 输出:`data/ig_industry_urls.txt`(所有 URL,按 B1/B2/B3/B4/C 分组)
- [ ] 逐个 WebFetch → 按 `data/case_study_schema.json` 结构提取 → `data/ig_case_studies.json`
