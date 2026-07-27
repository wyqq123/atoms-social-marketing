"""Rule-based summarizer from EvidenceItem[] to OpportunityEvidenceBrief."""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from models import empty_brief, load_json, safe_int, write_json


def _term_values(values: list[Any]) -> list[str]:
    terms: list[str] = []
    for value in values or []:
        if isinstance(value, dict):
            value = value.get("value")
        text = str(value or "").strip()
        if text:
            terms.append(text)
    return terms


def _probe_terms(probe: dict[str, Any]) -> dict[str, list[str]]:
    source = probe.get("source_terms", {}) or {}
    return {key: _term_values(source.get(key, [])) for key in ["end_user_identity", "identity", "pain", "jtbd", "alternative", "trigger_moment", "desired_outcome"]}


def _days_old(value: str | None) -> int | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return int((datetime.now(timezone.utc) - parsed).total_seconds() // 86400)


def _engagement(item: dict[str, Any]) -> int:
    metrics = item.get("metrics", {}) or {}
    score = 0
    for key, weight in [("comments", 3), ("score", 1), ("likes", 1), ("views", 0)]:
        value = safe_int(metrics.get(key), 0) or 0
        score += min(value // 1000, 20) if key == "views" else value * weight
    return score


def summarize(items: list[dict[str, Any]], probes: dict[str, Any], platform: str) -> dict[str, Any]:
    if not items:
        return empty_brief(platform, "unavailable", "no_evidence_items")
    probe_by_id = {p.get("probe_id"): p for p in probes.get("probes", [])}
    matched_refs: list[str] = []
    matched_probe_ids: set[str] = set()
    clues: dict[str, set[str]] = defaultdict(set)
    biases: set[str] = set()
    total_engagement = 0
    fresh_items = 0
    seen_ref: set[str] = set()
    for item in items:
        if item.get("platform") != platform:
            continue
        probe_id = item.get("probe_id")
        probe = probe_by_id.get(probe_id, {})
        haystack = " ".join(str(item.get(k, "")) for k in ["title", "text_excerpt", "url"]).lower()
        hit = False
        for bucket, values in _probe_terms(probe).items():
            for term in values:
                if term.lower() in haystack:
                    hit = True
                    if bucket in {"end_user_identity", "identity"}:
                        clues["audience"].add(term)
                    elif bucket == "pain":
                        clues["pain"].add(term)
                    else:
                        clues["content"].add(term)
        if not hit and probe.get("query") and str(probe.get("query")).lower() in haystack:
            hit = True
            clues["content"].add(str(probe.get("query")))
        if hit:
            ref = item.get("evidence_id") or f"{platform}:{probe_id}:unknown"
            if ref not in seen_ref:
                seen_ref.add(ref)
                matched_refs.append(ref)
            if probe_id:
                matched_probe_ids.add(probe_id)
            total_engagement += _engagement(item)
            age = _days_old(item.get("published_at") or item.get("observed_at"))
            if age is not None and age <= 7:
                fresh_items += 1
        for bias in item.get("known_biases", []) or []:
            biases.add(str(bias))
    if not matched_refs:
        return empty_brief(platform, "unavailable", "no_probe_term_match")
    if len(matched_refs) >= 2 and total_engagement > 0:
        status = "usable"
        confidence = "medium-high" if platform != "web_search" else "medium"
    elif len(matched_refs) >= 2:
        status = "weak"
        confidence = "medium"
    else:
        status = "weak"
        confidence = "medium" if platform != "web_search" else "low"
    volume = "low" if len(matched_refs) < 4 else "medium" if len(matched_refs) < 8 else "high"
    engagement = "present" if total_engagement > 0 else "unknown"
    if total_engagement >= 100:
        engagement = "medium-high"
    if total_engagement >= 500:
        engagement = "high"
    velocity = "fresh" if fresh_items >= 2 else "recent_or_unknown" if fresh_items else "unknown"
    distribution = {
        "reddit": ["subreddit search", "comment-depth proxy", "community norm risk"],
        "youtube": ["youtube search", "title/description demand language", "public video metrics"],
        "web_search": ["public search result", "snippet-only evidence locator"],
    }.get(platform, ["cache_or_manual_evidence"])
    return {
        "platform": platform,
        "status": status,
        "freshness": "realtime" if platform in {"reddit", "youtube", "web_search"} else "cache_or_manual",
        "evidence_count": len(matched_refs),
        "matched_probe_ids": sorted(matched_probe_ids),
        "audience_clues": sorted(clues["audience"]),
        "pain_clues": sorted(clues["pain"]),
        "content_clues": sorted(clues["content"]),
        "distribution_clues": distribution,
        "activity_clues": {"volume": volume, "velocity": velocity, "engagement": engagement, "saturation": "unknown"},
        "recommended_use": "Calibrate angle and wording; do not claim broad platform trend.",
        "confidence": confidence,
        "evidence_refs": matched_refs[:8],
        "known_biases": sorted(biases | {"keyword_match_bias", "no_demographic_ground_truth"}),
        "warnings": [] if status == "usable" else ["evidence_is_limited_or_weak"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--items", required=True)
    parser.add_argument("--demand-probes", required=True)
    parser.add_argument("--platform", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    payload = load_json(args.items)
    items = payload.get("items", payload) if isinstance(payload, dict) else payload
    write_json(args.output, summarize(items, load_json(args.demand_probes), args.platform))


if __name__ == "__main__":
    main()
