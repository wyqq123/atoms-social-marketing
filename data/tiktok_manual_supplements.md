# Manual Supplements — TikTok Samples

## 目的

补齐 Category B 博客案例覆盖不到的样本。TikTok 博客选样偏「爆款」+「大品牌」,人工补齐主要补:

- **Vibe coding / SMB solo builder 类样本**(博客几乎不覆盖,需重度补齐 ≥10 条)
- **2025 起最新样本**(博客案例多为 2024 及以前,TikTok trend 变化快,时效性关键)
- **Creator 类 indie hacker / solo builder TikTok 案例**(博客稀疏)
- **中位表现样本**(1K-30K views,平衡博客的"高转化 bias")
- **TikTok Shop 从 0 起量的 SMB 案例**(区别于博客的大品牌案例)

## 使用方式

**你(用户)**:按下面模板逐条填写(可粘贴 TikTok 视频截图 + caption + 主观点评)。
**我(Agent)**:整理成结构化数据,合并到 `tiktok_case_studies.json` 用于归纳。

无需填全每个字段——已知什么填什么,不确定的留空或写 `?`。

## 目标补齐量

- 10-20 条,分布:
  - **SaaS/AI: 3-5 条**(尤其 2025 launch post + AI demo 类)
  - **Ecommerce: 3-5 条**(尤其 TikTok Shop 从 0 起量的 SMB)
  - **Creator: 4-10 条**(solo builder / indie hacker 优先,是博客最缺的类别)

---

## 模板

```markdown
## Sample [编号]

- **Post URL**: https://www.tiktok.com/@xxx/video/XXXX
- **Business type**: saas | ecommerce | creator
- **Handle**: @xxx
- **Post date**: YYYY-MM(可选)
- **Video length**: XX 秒
- **Sound type**: trending | original | licensed | none
- **Hook pattern**(§5 六种之一): broken-hook | number-promise | before-after | pov | suspense | hot-take

**Caption**(粘贴或复述要点):
> ...

**Hashtags**: #tag1 #tag2 #tag3

**Text overlay 关键片段**(视频内文字):
> 前 3s:...
> 中段:...
> 结尾:...

**Engagement**(截图当时的数字):
- Views: X
- Likes: X
- Comments: X
- Shares: X
- Saves: X(如面板可见)

**FYP 表现**:
- 是否进入 FYP:yes | no | unsure
- 关注 vs 非关注观看比:如可见,填 X%

**Loop 设计**:视频结尾是否自然接回开头(为 rewatch)?yes | no

**Screenshot / 视频描述**(可选,若有本地路径也可以贴):
> ...

**为什么选它 / 你的观察**:
> ...

**期待学到什么**:
> ...
```

---

## 已补齐样本

<!-- Agent 会把用户提供的样本按 sample id 追加在下面。用户直接填在这里也行,Agent 会整理。 -->

## Sample 1

(空白,待用户填)

---

## Sample 2

(空白,待用户填)

---

## Sample 3

(空白,待用户填)

---

## 主动约定

- **动态更新触发**:每次新增 5 条样本或 Creative Center 快照更新时,提示 Agent 复核 playbook §9 winning structures 是否需要迭代
- **交叉验证**:样本填完后,与 `tiktok_trend_snapshot.json` 中当期 trending hashtag/sound 对照——若样本使用的 sound 已过时,标注"数据快照过期"caveat
