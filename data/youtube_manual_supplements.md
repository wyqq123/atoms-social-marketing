# Manual Supplements — YouTube Samples

## 目的

补齐 Category A(直抓)和 Category B(博客二手)覆盖不到的样本。YT 的 A 通道虽然工作,但仍存在以下 gap:
- **失败案例**:Data API 只能拿到发布视频,拿不到"发了没起来"的具体教训
- **未 index 的小样本**:1K-5K view 的真实 SMB 视频不容易通过 top search 挖到
- **正在实验的形式**(如 Shorts 3min 上限刚上调,样本极少)
- **中文/其他语言市场**:英语中心的博客 case 覆盖偏西方,非英语 SMB 需要用户补齐
- **Atoms 用户自身频道** —— builder 自己的频道数据是最贴合的样本

## 使用方式

**你(用户)**:按下面模板逐条填写(可以粘贴 YT URL + 主观点评)。
**我(Agent)**:整理成结构化数据,合并到 `youtube_case_studies.json` 或 `youtube_video_samples.json`。

无需填全每个字段——已知什么填什么,不确定的留空或写 `?`。

## 目标补齐量

- **6-12 条**,分布:
  - SaaS/AI:2-4 条(尤其 2025 launch / demo 视频)
  - Ecommerce:2-3 条(unboxing / review / dupe)
  - Creator/Indie:2-5 条(build-in-public + solo builder 优先)

## 优先补齐方向(vs 已有采集)

- **失败/中位样本**:1K-5K views 的真实 SMB 视频,平衡博客的 top 5% bias
- **Shorts 3min 新形式实验**(2024-10 后上传的 >60s Shorts)
- **中文/日文/西语 SMB 频道**(英文博客盲区)
- **Atoms 用户本身频道**(如已有 builder 起步 YT 运营)

---

## 模板

```markdown
## Sample [编号]

- **Video URL**: https://www.youtube.com/watch?v=xxx (或 shorts URL)
- **Channel URL**: https://www.youtube.com/@xxx
- **Business type**: saas | ecommerce | creator
- **Video type**: long_form | short | live | community_post
- **Post date**: YYYY-MM(可选)
- **Duration**: X min / X sec

**Title**:
> 完整 title

**Description(前 100-200 字)**:
> 粘贴 description 前段

**Thumbnail 描述**(不用贴图,文字描述即可):
> 例:founder face + 大字 "1000 subs in 60 days"

**Hashtags**: #tag1 #tag2 #tag3

**Engagement**(YT Studio 后台或公开数据):
- Views: X
- Likes: X
- Comments: X
- AVD: X seconds(如可见)
- AVP: X %(如可见)
- CTR: X %(如可见)

**为什么选它 / 你的观察**:
> 例:"这是我朋友的 SaaS launch 视频,虽然只有 800 views 但 CTR 12% 显著高于平均,应该是 title + 缩略图对了..."

**期待学到什么 / 想印证的假设**:
> 例:"想验证 'founder face + 数字缩略图' 对 SaaS 冷启动的实际效果"
```

---

## 已补齐样本

<!-- Agent 会把用户提供的样本按 sample id 追加在下面。用户直接填在这里也行,Agent 会整理。 -->

## Sample 1

(空白,待用户填)

---

## Sample 2

(空白,待用户填)
