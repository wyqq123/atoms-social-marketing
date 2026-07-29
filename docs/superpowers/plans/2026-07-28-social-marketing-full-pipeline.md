# Atoms Social Marketing Full Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让受控 agent 能从已完成 built app 的上下文开始，通过 HIL 收集定位信息，执行 Stage 1-5 和实时证据探针，并交付经校验的完整首发社媒内容包。

**Architecture:** 新增一个明确状态机的 `social_marketing_runtime`。LLM 只在 Stage 1、2c、3、4 执行受 JSON Schema 约束的内容推理；HIL、输入校验、实时探针调用、平台选择、证据/措辞门控、最终 schema 校验与降级全部由确定性代码控制。模型只调用一个受控 tool，不接触 shell、cache 路径和 API 凭证。

**Tech Stack:** Python 3.11+、现有标准库 probe adapters、`jsonschema`（Draft 7 验证）、宿主 agent 的 structured-output / tool-calling 接口、现有 `data/platform_registry.json` 与 playbooks。

---

## 1. 现状问题与目标行为

### 1.1 当前问题的具体表现

当前 Skill 文档定义了五个 stage，但脚本只运行 Stage 2b：

```text
现在：用户 prompt -> 模型自行阅读文档 -> 可能生成部分 Stage 1 JSON
      -> 可能运行 realtime_probe -> 模型自行想象 Stage 2c-5 -> 文本回答
```

这不是可执行 pipeline，实际会产生以下问题：

1. **触发不可靠。** `SKILL.md` 只在自然语言中规定“built app 已完成、定位三要素已收集”；没有状态、字段校验或确认步骤。模型可以在应用尚未完成、终端用户不清楚、或把 builder 当成 target audience 时继续。
2. **stage 输入输出断裂。** `run_realtime_probe.py` 需要两个已经成形的 JSON 文件；不存在把原始 app context 转成 `app_icp_vector` / `demand_probe_pack` 的执行器，也没有 Stage 2c 接收 evidence brief 的代码入口。
3. **模型输出不可验收。** `launch_pack_schema.json` 存在，但没有完整 Launch Pack validator 或 repair loop；任一 stage 可漏字段、混用别名、超出平台政策或丢失 post reference 而不被发现。
4. **内容交付不完整。** Stage 3 只提供 content angles；没有保证每个最终选择的平台都输出可直接发布的标题、正文、CTA、平台原生 discoverability 字段、图像/视频 prompt 和首周排期。
5. **事实性和时效性不可控。** evidence 是否新鲜、是否与 probe intent 匹配、是否能写入 `why_now` 都依赖模型遵守 prose，而不是由程序强制。
6. **失败无法解释或恢复。** 用户无法区分“缺少 HIL 字段”“API 无凭证”“探针超时”“模型格式不合格”“全部平台 fit 偏弱”，也无法只补充必要信息后继续。

### 1.2 目标体验

```text
用户请求推广已完成的应用
  -> runtime 检查 app readiness 与 intake 字段
  -> 缺字段时逐项 HIL 收集并回显确认
  -> Stage 1 structured generation + validate/repair
  -> Stage 2a shortlist -> Stage 2b probe -> Stage 2c score/select
  -> Stage 3 strategy -> Stage 4 full post/render prompt -> Stage 5 schedule/pack
  -> final validator + bounded repair -> 完整 Launch Pack JSON + 用户可读摘要
```

完成态必须满足：

- `publish_platforms` 是所有达到发布阈值且受 builder 生产能力约束的平台；不是 `web_search`，也不是仅因为排第一的平台。
- 每个平台至少有一个可直接发布的 post。每个 post 必须有 `title`、`hook`、完整 `body`、CTA 和适用的 hashtags 或 keywords。
- 图文平台必须有逐页 carousel/static creative brief 与每页 image prompt；视频平台必须有 storyboard、逐 scene video/image/B-roll prompt。
- `schedule.week_1` 覆盖所有 `publish_platforms`，至少三条内容，且 `post_ref` 真正指向交付物。
- 所有当前/近期措辞都可追溯到符合平台 freshness SLA 的 `usable` evidence；否则只输出 evergreen 策略。

## 2. 目标运行时与边界

### 2.1 对外唯一 tool

宿主给通用模型暴露一个 tool，而不是暴露脚本命令：

```python
def run_social_marketing(
    request: dict,
    session_id: str,
) -> dict:
    """Return either a HIL form request or a schema-valid LaunchPack result."""
```

返回包络：

```json
{
  "status": "needs_input | needs_confirmation | completed | blocked",
  "session_id": "opaque-id",
  "next_hil": {
    "fields": ["promo_goal", "target_audience", "key_selling_point"],
    "questions": [{"field": "promo_goal", "label": "本次首发最希望达成什么结果？", "required": true}],
    "draft": {}
  },
  "result": null,
  "checks": {"blocker": [], "warning": [], "info": []}
}
```

只有 runtime 进程可以读取环境变量及调用 `scripts/realtime_probe/run_realtime_probe.py` 的 Python API。LLM 不能看到 `YOUTUBE_API_KEY`、Reddit secret、Google CSE key，也不能自己拼 shell 命令。

### 2.2 HIL 状态机

状态和合法迁移：

```text
new -> validating_app -> collecting_positioning -> confirming_positioning
    -> stage_1 -> stage_2a -> stage_2b -> stage_2c -> stage_3
    -> stage_4 -> stage_5 -> validating_output -> completed
                                     |                 |
                                     -> needs_repair ---
任何阶段 -> blocked（缺失不可恢复的 built app context 或用户拒绝确认）
```

HIL 的必收集字段：

| 字段 | 何时必问 | 合格条件 | 不能由模型猜测的内容 |
|---|---|---|---|
| `promo_goal` | 无值或含糊 | 目标动作 + 时间范围，例如“首周获得 100 个注册” | 转化 KPI、目标动作 |
| `target_audience` | 无值或为 builder 身份 | built app 的终端用户角色 + 场景 | 终端用户身份、购买力、真实 demographics |
| `key_selling_point` | 无值或仅营销口号 | 产品机制 + 用户结果 | 不存在的功能、客户证明 |
| `target_market` | 未提供 | ISO 市场码，默认 US 需提示 | 市场定位 |
| `production_context` | 对视频/证明内容不足时 | 素材、能否录制、每周产能 | 创始人出镜/客户证言是否可用 |

收集完成后必须给用户一个简短确认卡；用户编辑或确认后才可进入 Stage 1。若 built app 未标记完成，返回 `blocked`，而不是继续生成营销包。

### 2.3 LLM 与确定性组件的职责

| 层 | 负责内容 | 禁止负责内容 |
|---|---|---|
| LLM Stage 1 | ICP hypothesis、JTBD、demand probes | 真实事实断言、平台评分、网络抓取 |
| Deterministic Stage 2a/2b | shortlist、API/cache 调用、证据归一、freshness | 文案与营销建议 |
| LLM Stage 2c | 对每个稳定评分维度给出有依据的解释草案 | 超范围数值、无证据的 why-now |
| Deterministic score gate | 计算/夹紧分数、confidence cap、选择 publish platforms | 主观营销创意 |
| LLM Stage 3/4 | strategy、完整 post 文案、storyboard、media prompts | 平台政策例外、当前热度断言 |
| Deterministic Stage 5 | schedule 配额、引用完整性、schema/wording/CTA 检查 | 重写整套创意 |

## 3. 新旧文件结构

```text
scripts/social_marketing_runtime/
  __init__.py
  orchestrator.py              # 状态机与总编排入口
  contracts.py                 # dataclasses/Pydantic-like typed envelope
  intake.py                    # HIL completeness, questions, confirmation
  llm_gateway.py               # 宿主 structured-output adapter interface
  stage_1.py                   # prompt payload + Stage 1 validation/repair
  stage_2_fit.py               # stable scoring, caps, publish platform selection
  stage_3_strategy.py          # LLM strategy request + validation/repair
  stage_4_render.py            # LLM post/storyboard/prompt request + validation/repair
  stage_5_pack.py              # assemble schedule/meta/checks
  validators.py                # JSON schema, semantic, wording, cross-ref validators
  policies.py                  # freshness, CTA, platform discoverability, wording policy
  prompts/
    stage_1.md
    stage_2c.md
    stage_3.md
    stage_4.md
data/
  social_marketing_runtime_schema.json
  stage_1_output_schema.json
  platform_content_policy.json
  launch_pack_schema.json      # v0.3.0, revised post contract
scripts/realtime_probe/
  ... existing files ...       # harden cache/freshness/relevance/timeout
tests/
  social_marketing_runtime/
    test_intake.py
    test_stage_1.py
    test_stage_2_fit.py
    test_stage_3.py
    test_stage_4.py
    test_stage_5.py
    test_orchestrator.py
    test_contracts.py
```

## 4. Final Launch Pack v0.3.0 Contract

### 4.1 Publish platform selection

保留 `platform_fit.ranking` 供解释，但新增 `publish_platforms`，由确定性规则选出：

```python
def select_publish_platforms(scores: dict[str, PlatformFitScore], capacity: str) -> list[str]:
    eligible = [
        platform for platform, score in scores.items()
        if score.fit_score >= 55 and score.score_confidence in {"medium", "medium-high", "high"}
    ]
    cap = {"low": 2, "medium": 3, "high": 4, "unknown": 2}[capacity]
    return sorted(eligible, key=lambda platform: scores[platform].fit_score, reverse=True)[:cap]
```

若无平台达到 55，选择最高分平台作为 `pilot_platforms`，输出 B4 blocker，不能伪装为“高匹配平台”。用户明确指定的平台可保留为 `user_requested_pilot`，但必须标示低 confidence。

### 4.2 每条 post 的必交付字段

取代当前只含 `hook/body/hashtags` 的 Caption，所有 post 采用完整且平台中立的结构：

```json
{
  "post_id": "instagram-carousel-01",
  "angle_id": "instagram-01",
  "platform": "instagram",
  "surface": "carousel",
  "format": "image_carousel | static_image | reel | youtube_short | reddit_post | linkedin_document | pin | note",
  "title": "产品能力与用户痛点组成的可发布标题/首图 headline",
  "hook": "首屏或前 3 秒文案",
  "body": "完整平台正文，不用省略号或内容 angles 代替",
  "cta": {"text": "具体行动", "link_style": "bio-link"},
  "discoverability": {
    "hashtags": ["#only-when-native"],
    "keywords": ["reddit/youtube/linkedin 可用关键词"],
    "placement_note": "title | caption | description | comment"
  },
  "creative": {
    "kind": "carousel | static | video | text",
    "slides": [],
    "storyboard": null,
    "asset_requirements": ["built_app_screenshot"]
  },
  "confidence": "medium",
  "evidence_refs": [],
  "why_this_copy": "仅引用 stable profile/playbook 或可用证据"
}
```

平台约束由 `platform_content_policy.json` 强制：

| 平台 | `title` 的含义 | discoverability | 正文/创意最低要求 |
|---|---|---|---|
| Instagram carousel/static | 首图 headline | 3-8 hashtags | `body` + 3-10 slides，每 slide 有文字和 image prompt |
| Instagram Reels/TikTok/Douyin/Rednote video | cover headline | 3-8 hashtags/keywords | 完整 caption + 3 秒节奏 storyboard |
| YouTube | video title | keywords + 最多 3 hashtags | description body + thumbnail prompt + storyboard |
| Reddit | post title | keywords，不要求 hashtags | 100+ 字符原生正文，轻 CTA，禁止硬广语气 |
| LinkedIn | opening headline | 3-6 keywords，0-3 hashtags | 150+ 字符观点正文；document 则逐页文案/prompt |
| Pinterest | Pin title | keyword list | Pin description + vertical image prompt |

`hashtags` 不再全局 `minItems: 5`；各平台由 policy 设定 `min/max`，并同时验证 `keywords`。模板中 `ig/yt/tt` 一律改为注册表全称。

### 4.3 多产物 prompt 最低质量

图文内容 `creative.slides[]`：

```json
{
  "slide_index": 1,
  "role": "cover | pain | mechanism | proof | cta",
  "on_image_copy": "不超过平台 policy 的文字长度",
  "speaker_notes": null,
  "image_prompt": {
    "trigger": "on-demand",
    "injectable_prompt": "主体、产品真实 UI/截图约束、画幅、构图、光线、文字留白、风格",
    "aspect_ratio": "4:5"
  }
}
```

视频内容 `creative.storyboard.scenes[]` 必须有 hook 与 CTA，scene duration 总和等于视频总时长，并且每场有一个可执行来源：`video_prompt`、`image_prompt` 或 `b_roll_requirement`。任何关于产品 UI 的 prompt 必须优先引用用户提供的截图/录屏，而不是要求模型编造功能界面。

### 4.4 Schedule

`schedule.week_1` 每项改为：

```json
{
  "day": "Day 1",
  "date_offset_from_launch": 0,
  "platform": "instagram",
  "post_ref": "instagram-carousel-01",
  "recommended_time_local": "09:30",
  "timezone": "America/Los_Angeles",
  "objective": "problem recognition",
  "rationale": "evergreen distribution rationale",
  "production_dependency": ["built_app_screenshot"]
}
```

验证器必须确认 `post_ref` 存在、每个 publish platform 至少有一项、同一平台同一日不重复、且低产能用户不会收到不可完成的发布数量。

## 5. 分阶段实施任务

### Task 1: Establish versioned runtime and intake contracts

**Files:**
- Create: `scripts/social_marketing_runtime/contracts.py`
- Create: `scripts/social_marketing_runtime/intake.py`
- Create: `data/social_marketing_runtime_schema.json`
- Create: `tests/social_marketing_runtime/test_intake.py`
- Modify: `data/inputs_schema.json`
- Modify: `SKILL.md`

- [ ] **Step 1: Write failing intake tests**

```python
def test_missing_positioning_returns_only_missing_hil_fields():
    result = assess_intake({"app_context": completed_app(), "builder_prompt": valid_prompt()})
    assert result.status == "needs_input"
    assert result.missing_fields == ["promo_goal", "target_audience", "key_selling_point"]

def test_builder_identity_is_not_accepted_as_target_audience():
    request = valid_request(target_audience="我是一个独立开发者")
    result = assess_intake(request)
    assert result.status == "needs_input"
    assert "target_audience" in result.missing_fields

def test_incomplete_app_blocks_run_before_llm_or_probe():
    result = assess_intake(valid_request(app_status="draft"))
    assert result.status == "blocked"
    assert result.reason == "built_app_not_ready"
```

- [ ] **Step 2: Implement typed session state and deterministic HIL questions**

```python
@dataclass
class IntakeAssessment:
    status: Literal["ready", "needs_input", "needs_confirmation", "blocked"]
    missing_fields: list[str]
    questions: list[dict[str, str]]
    normalized_inputs: dict[str, Any] | None
    reason: str | None = None

def assess_intake(request: dict[str, Any]) -> IntakeAssessment:
    # Validate app_status, normalize aliases, reject builder-only audience wording,
    # return deterministic questions without invoking an LLM.
```

- [ ] **Step 3: Add `app_status` and `positioning_confirmed` to input schema**

`app_status` enum must be `draft | building | completed`; runtime accepts only `completed`. `positioning_confirmed` is set only by HIL confirmation, not inferred from a long prompt.

- [ ] **Step 4: Run intake tests and schema fixture tests**

Run: `python -m unittest tests.social_marketing_runtime.test_intake -v`  
Expected: all tests pass and no LLM/network mock is called.

- [ ] **Step 5: Commit**

```text
feat: add social marketing intake state machine
```

### Task 2: Build structured LLM gateway and Stage 1 executable output

**Files:**
- Create: `scripts/social_marketing_runtime/llm_gateway.py`
- Create: `scripts/social_marketing_runtime/stage_1.py`
- Create: `scripts/social_marketing_runtime/prompts/stage_1.md`
- Create: `data/stage_1_output_schema.json`
- Create: `tests/social_marketing_runtime/test_stage_1.py`
- Modify: `references/pipeline/stage-1-intent.md`

- [ ] **Step 1: Write failing Stage 1 contract tests**

```python
def test_stage_1_repair_once_then_returns_structured_failure():
    gateway = FakeGateway(outputs=[{"bad": "shape"}, valid_stage_1_output()])
    result = run_stage_1(valid_inputs(), gateway)
    assert result.intent_profile["audience"]["primary_persona"]
    assert gateway.calls == 2

def test_stage_1_rejects_product_name_only_probe():
    output = valid_stage_1_output()
    output["demand_probe_pack"]["probes"][0]["query"] = "AcmeWriter"
    assert "product_name_only_query" in validate_stage_1(output)
```

- [ ] **Step 2: Define LLM gateway contract**

```python
class StructuredLLMGateway(Protocol):
    def generate_json(self, *, prompt_id: str, input: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]: ...
```

The host adapter must use provider-native JSON schema / structured output. It must receive only sanitized inputs and no credential/cache fields.

- [ ] **Step 3: Implement Stage 1 semantic validation and one bounded repair**

Validate JSON Schema plus: ICP subject equals built app end users, each probe has source terms, `must_not_include` is honored, no named competitor without allowed source, and 4-8 diversified probes. On first failure request a repair using only validation errors; on second failure stop with `stage_1_invalid_output`.

- [ ] **Step 4: Run tests**

Run: `python -m unittest tests.social_marketing_runtime.test_stage_1 -v`  
Expected: good output passes; malformed and builder-confused outputs do not proceed.

- [ ] **Step 5: Commit**

```text
feat: add structured stage one generation
```

### Task 3: Harden Stage 2a/2b evidence execution

**Files:**
- Modify: `scripts/realtime_probe/query_planner.py`
- Modify: `scripts/realtime_probe/run_realtime_probe.py`
- Modify: `scripts/realtime_probe/summarize_opportunity_brief.py`
- Modify: `scripts/realtime_probe/cache_store.py`
- Modify: `scripts/realtime_probe/adapters/cached_platform_probe.py`
- Create: `scripts/social_marketing_runtime/stage_2_fit.py`
- Create: `tests/social_marketing_runtime/test_stage_2_fit.py`
- Modify: `tests/test_realtime_probe.py`

- [ ] **Step 1: Write failing evidence boundary tests**

```python
def test_stale_cache_is_retained_as_fallback_but_network_is_attempted(): ...
def test_two_old_youtube_results_cannot_be_usable_under_72h_sla(): ...
def test_query_with_must_not_include_term_is_rejected_before_adapter(): ...
def test_invalid_evidence_item_is_excluded_before_summarization(): ...
def test_total_runtime_returns_at_deadline_when_adapter_never_finishes(): ...
```

- [ ] **Step 2: Enforce query constraints and evidence relevance**

`plan_queries` must reject a query that contains normalized `must_not_include` terms, has no end-user/pain/JTBD term, or duplicates another query. `summarize` must require a match to expected evidence type plus at least one source term; simple search-result lexical overlap is insufficient.

- [ ] **Step 3: Make freshness policy registry-driven**

Pass each platform's `freshness_sla` from registry into summarize. A brief can be `usable` only if at least two matched, fresh items meet relevance and engagement requirements. Expired items remain optional non-current wording evidence and never produce `why_now` eligibility.

- [ ] **Step 4: Correct stale cache and isolation behavior**

Use `cache_status` values `fresh_hit | stale_fallback | miss`. A fresh hit skips network; stale data is retained only if real-time fetch fails. Cache paths use `tenant_id/app_id` and opaque HMAC/SHA-256 keys, never readable audience strings.

- [ ] **Step 5: Enforce a real deadline**

Use one monotonic deadline. Adapter calls receive remaining seconds; executor shutdown must use `wait=False, cancel_futures=True` after deadline. Filter `validate_item` failures before summarize. Sanitize reported errors to stable error codes, not exception strings.

- [ ] **Step 6: Implement deterministic Stage 2c**

LLM returns only bounded subscore rationales with evidence refs. `stage_2_fit.py` validates the six numeric ranges, recomputes total, applies stable/realtime caps and returns `publish_platforms`/`pilot_platforms` with an explicit selection reason.

- [ ] **Step 7: Run tests**

Run: `python -m unittest discover -s tests -p "test_*.py"`  
Expected: stale cache refreshes, old evidence is not current, malformed evidence never reaches scoring, total fetch count remains <= 60.

- [ ] **Step 8: Commit**

```text
feat: harden realtime evidence and platform selection
```

### Task 4: Replace the post contract with complete publishable artifacts

**Files:**
- Modify: `data/launch_pack_schema.json`
- Create: `data/platform_content_policy.json`
- Modify: `references/templates/caption.md`
- Modify: `references/templates/storyboard.md`
- Create: `tests/social_marketing_runtime/test_contracts.py`
- Modify: `references/pipeline/stage-3-strategy.md`
- Modify: `references/pipeline/stage-4-render.md`

- [ ] **Step 1: Write failing contract tests**

```python
def test_reddit_post_requires_title_and_body_but_not_five_hashtags(): ...
def test_instagram_carousel_requires_title_body_and_three_slide_prompts(): ...
def test_video_storyboard_duration_and_scene_asset_sources_are_validated(): ...
def test_alias_platform_id_is_rejected_at_all_output_boundaries(): ...
```

- [ ] **Step 2: Version Launch Pack to 0.3.0**

Add required `publish_platforms`; replace `Caption` with `PostDeliverable`; move hashtags to `discoverability.hashtags`; add `discoverability.keywords`; require `post_id`, `title`, full `body`, `creative`, `evidence_refs`, and `why_this_copy`.

- [ ] **Step 3: Encode platform-specific policies as data**

`platform_content_policy.json` defines supported formats, title/body minimums, hashtag bounds, keyword bounds, CTA styles, asset requirements, aspect ratios, and prompt requirements. No platform-specific `if` chains should be introduced in the renderer.

- [ ] **Step 4: Align templates and examples**

Convert all `ig/yt/tt` examples to full IDs. Add complete examples for Instagram carousel, Reddit native post, YouTube Short, LinkedIn document and Pinterest Pin. Do not require five hashtags for Reddit/LinkedIn.

- [ ] **Step 5: Run schema and fixture tests**

Run: `python -m unittest tests.social_marketing_runtime.test_contracts -v`  
Expected: each native format validates; platform aliases and missing body/title/asset prompt fail clearly.

- [ ] **Step 6: Commit**

```text
feat: define complete cross-platform launch pack artifacts
```

### Task 5: Implement Stage 3 strategy and Stage 4 renderers

**Files:**
- Create: `scripts/social_marketing_runtime/stage_3_strategy.py`
- Create: `scripts/social_marketing_runtime/stage_4_render.py`
- Create: `scripts/social_marketing_runtime/prompts/stage_3.md`
- Create: `scripts/social_marketing_runtime/prompts/stage_4.md`
- Create: `tests/social_marketing_runtime/test_stage_3.py`
- Create: `tests/social_marketing_runtime/test_stage_4.py`

- [ ] **Step 1: Write failing renderer tests**

```python
def test_stage_3_only_strategizes_selected_publish_platforms(): ...
def test_stage_4_generates_full_body_not_only_angle_for_each_post(): ...
def test_stage_4_uses_evergreen_wording_when_probe_is_weak(): ...
def test_stage_4_carousel_has_one_prompt_per_slide_and_video_has_storyboard(): ...
```

- [ ] **Step 2: Implement Stage 3 constrained strategy call**

Input is only `publish_platforms`, score explanation, registry/playbook extract, production context and usable evidence. Output includes 3-5 angles only for each selected publish platform. Deterministic validator rejects `web_search`, unsupported surface, trend borrow without fresh usable evidence, and content volume above production capacity.

- [ ] **Step 3: Implement Stage 4 constrained render call**

For every selected platform, request the number of posts prescribed by policy/capacity, not merely angles. Require complete `PostDeliverable` objects. Render text first, then use a focused second call only for creative prompts if slide/scene prompt validation fails; maximum one repair per stage.

- [ ] **Step 4: Add semantic validators**

Validators must reject placeholder body/prompt, body lacking value proposition semantics, high confidence above score cap, missing CTA for acquisition goals, non-native hashtag policy, incorrect aspect ratio, missing carousel slides, scene duration mismatch, or prohibited current wording.

- [ ] **Step 5: Run tests**

Run: `python -m unittest tests.social_marketing_runtime.test_stage_3 tests.social_marketing_runtime.test_stage_4 -v`  
Expected: every publish platform receives full posts; weak/no evidence cannot create trend claims.

- [ ] **Step 6: Commit**

```text
feat: render complete platform-native launch content
```

### Task 6: Implement Stage 5 pack assembly and final validation

**Files:**
- Create: `scripts/social_marketing_runtime/stage_5_pack.py`
- Create: `scripts/social_marketing_runtime/validators.py`
- Create: `tests/social_marketing_runtime/test_stage_5.py`
- Modify: `data/launch_pack_schema.json`
- Modify: `references/pipeline/stage-5-pack.md`

- [ ] **Step 1: Write failing final-pack tests**

```python
def test_schedule_references_real_posts_and_covers_every_publish_platform(): ...
def test_current_wording_without_fresh_usable_evidence_is_a_blocker(): ...
def test_completed_pack_validates_against_json_schema_and_semantic_rules(): ...
def test_all_low_fit_platforms_returns_pilot_pack_with_blocker_b4(): ...
```

- [ ] **Step 2: Assemble schedule deterministically**

Create schedule slots from `publish_platforms`, score rank, content capacity, preferred registry time windows and local timezone. Do not ask LLM to invent `post_ref`; pass post IDs and only allow ordering/rationale suggestions.

- [ ] **Step 3: Implement two-layer final validator**

Layer 1 runs `jsonschema.Draft7Validator` on Launch Pack v0.3.0. Layer 2 checks cross references, evidence freshness, wording, CTA-goal mapping, confidence caps, prompt non-placeholder rules, duration sums, content coverage and `_pipeline_meta` consistency.

- [ ] **Step 4: Add one targeted repair route**

Schema errors from missing/invalid renderer fields return only the affected platform/post to Stage 4. Policy/evidence violations do not get “rephrased around”; they force deterministic downgrade/removal of unsupported claims.

- [ ] **Step 5: Run tests**

Run: `python -m unittest tests.social_marketing_runtime.test_stage_5 -v`  
Expected: final package cannot complete with dangling schedule posts, invalid freshness wording or incomplete visual prompts.

- [ ] **Step 6: Commit**

```text
feat: validate and assemble complete launch packs
```

### Task 7: Implement orchestrator, tool adapter, and end-to-end evaluation suite

**Files:**
- Create: `scripts/social_marketing_runtime/orchestrator.py`
- Create: `scripts/social_marketing_runtime/__init__.py`
- Create: `scripts/social_marketing_runtime/tool_adapter.py`
- Create: `tests/social_marketing_runtime/test_orchestrator.py`
- Create: `tests/fixtures/social_marketing_runtime/`
- Modify: `SKILL.md`
- Modify: `scripts/README.md`

- [ ] **Step 1: Write end-to-end tests using fake LLM and fake adapters**

```python
def test_prompt_to_hil_to_completed_pack(): ...
def test_missing_positioning_pauses_without_running_probe(): ...
def test_no_credentials_still_returns_evergreen_complete_pack(): ...
def test_youtube_usable_reddit_skipped_outputs_grounded_multiplatform_pack(): ...
def test_stage_failure_is_resumable_from_last_valid_artifact(): ...
```

- [ ] **Step 2: Implement artifact-backed state machine**

Persist a versioned `RunState` after every stage: normalized input, confirmation, Stage 1 output, evidence brief, fit, strategy, deliverables, pack, checks. Resume only from schema-valid artifacts. Use opaque session IDs and tenant-scoped storage interface; local development may use a temp JSON store.

- [ ] **Step 3: Provide the host tool adapter**

`tool_adapter.run_social_marketing` maps generic user prompt/app context into intake state, emits HIL questions, accepts confirmed form results, calls the orchestrator, and returns only a user-safe result envelope. API credentials remain process environment variables.

- [ ] **Step 4: Document runtime calling rules in SKILL.md**

Update trigger section to say the skill is callable only through `run_social_marketing`; list HIL pause conditions, completed output contract, fallback behavior and no direct shell/API-key access. Keep SKILL focused on agent behavior; move machine rules to schemas/policies.

- [ ] **Step 5: Run full verification**

Run:

```text
python -m unittest discover -s tests -p "test_*.py"
python -m py_compile scripts/social_marketing_runtime/*.py scripts/realtime_probe/*.py
```

Expected: all fixtures pass; no-network produces a valid evergreen pack; mock realtime produces only freshness-gated claims; all output validates against v0.3.0.

- [ ] **Step 6: Commit**

```text
feat: add end-to-end social marketing skill runtime
```

## 6. Evaluation and Acceptance Matrix

| Area | Required proof | Passing condition |
|---|---|---|
| Trigger | app draft / incomplete HIL integration tests | runtime returns HIL or blocked; no probe/LLM stage starts prematurely |
| Entity boundary | builder vs end-user adversarial fixtures | builder identity never enters ICP/probes unless app explicitly targets builders |
| Evidence | stale, old, irrelevant, malformed mock items | only fresh, relevant, valid evidence can be usable/current |
| Content completeness | one fixture per publish platform format | each post has title, body, CTA, native discoverability, and valid creative object |
| Image/video | carousel and short-video fixtures | slides/scenes have executable prompts or declared user asset dependency |
| Schedule | cross-reference validation | every selected platform is represented and every `post_ref` resolves |
| Degradation | no credentials/no network/all low fit | result is still schema-valid, evergreen, explicit about limits, and never claims current trends |
| Efficiency | timed fake adapters and runtime metrics | total probe fetch <= 60; deadline respected; LLM calls <= 6 normal path and <= 1 repair per stage |
| Security | fake secret/PII fixtures | no secrets in result/reports; cache keys are opaque and tenant-scoped |

## 7. Delivery Sequence and Non-goals

Implement Tasks 1-3 before Tasks 4-7. A Stage 2b-only release is acceptable only as an internal probe capability; it must not be exposed as “complete launch pack generation.” Tasks 4-7 are the minimum release boundary for the requested user-facing Skill.

Out of scope for this plan: direct image/video generation, autonomous publication, login-state scraping, long-term content calendar beyond week one, and platform-wide trend claims without authorized evidence.

## 8. Plan Self-Review

- Trigger, HIL, Stage 1-5 execution, API isolation, content body/title/hashtag/keyword outputs, image/video prompts, schedule, validation, fallback and tests are each covered by a task.
- All new LLM outputs have schema validation, semantic validation and at most one repair loop.
- All platform-specific variation is data-driven through registry/policy, avoiding an expanding renderer switch statement.
- The final acceptance boundary is a schema-valid, evidence-gated Launch Pack v0.3.0, not merely a successful realtime probe.
