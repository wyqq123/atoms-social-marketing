"""Deterministic Stage 2 platform selection and safe evidence caps."""
from __future__ import annotations

from typing import Any

from .contracts import PUBLISHABLE_PLATFORMS, production_capacity

BASE_SCORES = {"reddit": 72, "youtube": 70, "instagram": 68, "tiktok": 66, "linkedin": 66, "pinterest": 62, "x": 58, "rednote": 64, "douyin": 63}


def _scope(inputs: dict[str, Any]) -> list[str]:
    requested = inputs.get("platform_scope") or ["instagram", "youtube", "tiktok", "reddit"]
    return [platform for platform in requested if platform in PUBLISHABLE_PLATFORMS]


def build_platform_fit(inputs: dict[str, Any], briefs: list[dict[str, Any]]) -> dict[str, Any]:
    brief_by_platform = {brief.get("platform"): brief for brief in briefs}
    scores: dict[str, Any] = {}
    for platform in _scope(inputs):
        brief = brief_by_platform.get(platform)
        adjustment = 4 if brief and brief.get("status") == "usable" else 0
        stable = BASE_SCORES[platform]
        scores[platform] = {
            "fit_score": max(0, min(100, stable + adjustment)), "stable_fit_score": stable,
            "realtime_adjustment": adjustment, "score_confidence": "medium-high" if adjustment else "medium",
            "probe_status": brief.get("status", "not_run") if brief else "not_run",
            "subscores": {"icp_reach_quality": 22, "mindset_intent_fit": 15, "value_expression_fit": 11, "distribution_feasibility": 10, "conversion_path_fit": 7, "production_feasibility": 5},
            "audience_intersection": {"matched_dimensions": ["confirmed_end_user_audience", "value_proposition"], "missing_dimensions": ["authorized_conversion_data"], "reachable_icp_scale": "unknown", "quality": "hypothesis_backed"},
            "recommended_surfaces": [], "why_this_platform": ["Stable platform profile supports the confirmed audience and launch goal."], "why_now": [],
            "risks": ["Use a small first-week test and validate conversion with UTM or GA4."], "_evidence_refs": (brief or {}).get("evidence_refs", []),
        }
    ranking = sorted(scores, key=lambda platform: scores[platform]["fit_score"], reverse=True)
    cap = {"low": 2, "medium": 3, "high": 4, "unknown": 2}[production_capacity(inputs)]
    publish = [platform for platform in ranking if scores[platform]["fit_score"] >= 55][:cap]
    return {"ranking": ranking, "publish_platforms": publish, "pilot_platforms": [] if publish else ranking[:1], "probe_shortlist": [brief.get("platform") for brief in briefs if brief.get("platform") != "web_search"], "scores": scores, "opportunity_evidence_briefs": briefs, "_rationale": "Scores use stable platform profiles; realtime evidence only applies a bounded adjustment when usable."}
