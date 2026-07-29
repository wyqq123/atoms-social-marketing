"""Executable Stage 1: derive a conservative ICP vector and demand probes."""
from __future__ import annotations

from typing import Any

from .contracts import clean_text, utc_now
from .llm_gateway import StructuredLLMGateway


def _fallback(inputs: dict[str, Any]) -> dict[str, Any]:
    app = inputs["app_context"]
    positioning = inputs["positioning"]
    audience = clean_text(positioning["target_audience"])
    selling_point = clean_text(positioning["key_selling_point"])
    goal = clean_text(positioning["promo_goal"])
    market = (app.get("target_market") or ["US"])[0]
    language = "zh" if market == "CN" else "en"
    pain = f"struggling with {selling_point.lower()}" if language == "en" else f"需要更高效地获得{selling_point}"
    probes = []
    for index, (intent, query) in enumerate([
        ("pain_expression", f"{audience} {pain}"),
        ("jtbd_how_to", f"how to {selling_point.lower()} for {audience}"),
        ("alternative_comparison", f"{audience} alternatives to manual workflow"),
        ("desired_outcome", f"best way for {audience} to improve results"),
    ], start=1):
        probes.append({
            "probe_id": f"p{index:02d}", "intent": intent, "query": query,
            "query_variants": [{"type": "long_tail_precision", "query": query}],
            "language": language, "market": market,
            "source_terms": {"end_user_identity": [audience], "pain": [pain], "jtbd": [selling_point], "alternative": ["manual workflow"], "desired_outcome": [goal]},
            "priority": round(1 - index * 0.08, 2),
            "expected_evidence_type": "pain discussion | how-to search | workaround comparison",
            "must_not_include": [app["name"], "Atoms", "brand slogan"],
        })
    return {
        "intent_profile": {
            "app_summary": {"name": app["name"], "one_liner": clean_text(app["description"])[:100], "category_normalized": app["category"], "market_primary": [market]},
            "promo_intent": {"goal_type": "user-acquisition", "goal_metric_hint": goal, "time_horizon": "week-1"},
            "audience": {"primary_persona": audience, "pain_points": [pain], "tone_preference": "professional"},
            "value_prop": {"key_selling_point": selling_point, "supporting_points": [], "differentiators": []},
            "ga4_signals": None,
            "_rationale": "Derived from confirmed positioning; pain language remains a hypothesis until evidence is available.",
        },
        "app_icp_vector": {
            "icp_id": "runtime", "icp_subject": "built_app_end_users", "source_confidence": "medium",
            "geo_language": {"markets": [market], "languages": [language], "confidence": "medium"},
            "end_user_identity": {"roles": [{"value": audience, "source": "positioning.target_audience", "confidence": "high"}], "explicitly_not_builder_identity": True, "confidence": "high"},
            "app_capability_summary": {"core_capabilities": [selling_point], "source": ["app_context.description", "positioning.key_selling_point"], "confidence": "high"},
            "jtbd": {"primary_jobs": [{"value": selling_point, "source": "positioning.key_selling_point", "confidence": "medium"}], "confidence": "medium"},
            "pains": {"pain_points": [{"value": pain, "source": "synthetic_from_positioning", "confidence": "medium"}], "observed_pain_language_examples": [], "confidence": "medium"},
            "value_proposition": {"key_selling_point_raw": selling_point, "user_benefit": selling_point, "claim_risk": "medium"},
            "conversion_goal": {"goal_type": "signup", "desired_action": goal, "confidence": "medium"},
            "builder_context": {}, "production_constraints": inputs.get("production_context") or {},
        },
        "demand_probe_pack": {"app_id": "runtime", "probe_subject": "built_app_end_users", "generated_at": utc_now(), "icp_summary": audience, "probes": probes, "constraints": {"max_probes": 8, "avoid_product_keywords_only": True}},
    }


def validate_stage_1(output: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if output.get("app_icp_vector", {}).get("icp_subject") != "built_app_end_users":
        errors.append("icp_subject_must_be_built_app_end_users")
    probes = output.get("demand_probe_pack", {}).get("probes") or []
    if not 4 <= len(probes) <= 8:
        errors.append("probe_count_must_be_4_to_8")
    for probe in probes:
        if not clean_text(probe.get("query")) or not (probe.get("source_terms") or {}):
            errors.append("probe_requires_query_and_source_terms")
    return sorted(set(errors))


def run_stage_1(inputs: dict[str, Any], gateway: StructuredLLMGateway | None = None) -> dict[str, Any]:
    output = _fallback(inputs) if gateway is None else gateway.generate_json(prompt_id="atoms-social-marketing.stage-1", input=inputs, schema={"type": "object"})
    errors = validate_stage_1(output)
    if errors:
        raise ValueError("stage_1_invalid_output:" + ",".join(errors))
    return output
