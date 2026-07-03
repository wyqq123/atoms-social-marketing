# Deprecated: IG OG Metadata Route

**Date**: 2026-07-02
**Reason**: Instagram 已对未登录 UA 请求剥离 Open Graph meta tags。抓取脚本(`scripts/extract_og_metadata.py`)返回 HTTP 200 + 614K HTML,但 `<meta og:*>` 全空。

**Deprecated files**:
- `_deprecated_ig_urls_raw.txt` — 14 个 SaaS/AI 类 IG post URL(WebSearch 收集,数据未验证)
- `_deprecated_ig_samples.json` — 14 个空样本(caption / engagement / image 全空)

**替代方案**:Category B 博客案例提取 + 人工补齐。详见 `scripts/README.md`。

**保留原因**:
- URL 列表在 IG 政策变更(如 oEmbed 恢复公开)或走商业化 scraping API 时可复用
- 失败样本作为"IG 已封锁 OG"的证据,避免未来重复踩坑
