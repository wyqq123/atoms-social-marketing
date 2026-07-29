# Conversation Clarifier Protocol

Use this protocol when a generic model gathers positioning through conversation instead of the HIL form.

## Host Contract

The host owns session persistence, rendering, and tool permissions. Persist the JSON state returned by `scripts/positioning_intake/run_positioning_intake.py`; the script is intentionally stateless. Do not expose Stage 1 or Stage 2b tools until `route == "ready"` and `handoff` is present.

## Start

The model extracts candidates from the user prompt and built app context. Each candidate must declare `value`, `source`, `evidence_excerpt`, and `confidence`. Use only `user_prompt` or `app_context` for automatic quick confirmation. A builder identity is never an app end-user identity without explicit app context.

```json
{
  "action": "start",
  "session_id": "opaque-host-id",
  "candidate_extraction": {
    "promo_goal": {"value": "Get 100 week-one signups", "source": "user_prompt", "evidence_excerpt": "...", "confidence": "high"},
    "target_audience": {"value": null, "source": "unknown", "confidence": "low"},
    "key_selling_point": {"value": "Generate product-page copy from product details", "source": "app_context", "evidence_excerpt": "...", "confidence": "high"}
  },
  "suggested_options": {"target_audience": [{"id": "a1", "label": "Shopify independent sellers", "reason": "...", "source": "user_prompt"}]}
}
```

## Answer

Send the returned session unchanged with one operation: `confirm_all_candidates`, `confirm_candidate`, `select_options`, `submit_custom`, `switch_to_form`, or `submit_form`. Render the returned `question` as controls, not as a free-form model decision.

For `target_audience`, allow at most two selected options. Preserve custom text verbatim except whitespace trimming. After two invalid answers for any field, render the original HIL form with `form_prefill`.

## Handoff

When `route == "ready"`, pass `handoff.positioning` into the existing `inputs.positioning`. Preserve `handoff.intake_meta` for audit and evaluation. Do not use candidate values, cache them, or call external APIs before the user confirmation represented by this handoff.
