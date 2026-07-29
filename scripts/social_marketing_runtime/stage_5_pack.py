"""Stage 5 assembly of a complete and internally consistent Launch Pack."""
from __future__ import annotations

from typing import Any

from .contracts import utc_now


def build_pack(inputs: dict[str, Any], stage_1: dict[str, Any], platform_fit: dict[str, Any], strategies: dict[str, Any], deliverables: dict[str, Any], probe_meta: dict[str, Any]) -> dict[str, Any]:
    platforms = platform_fit["publish_platforms"] or platform_fit["pilot_platforms"]
    posts = [(platform, deliverables[platform]["posts"][0]) for platform in platforms]
    schedule = []
    for index in range(max(3, len(posts))):
        platform, post = posts[index % len(posts)]
        schedule.append({"day": f"Day {index + 1}", "date_offset_from_launch": index, "platform": platform, "post_ref": post["post_id"], "recommended_time_local": "09:30", "timezone": "America/Los_Angeles", "objective": "problem recognition" if index == 0 else "product consideration", "rationale": "Use a stable first-week testing rhythm; no current-trend claim is implied.", "production_dependency": post["creative"].get("asset_requirements", [])})
    checks = {"blocker": [], "warning": [], "info": []}
    if not platform_fit["publish_platforms"]:
        checks["blocker"].append("B4: all platforms are below the publish threshold; returning a pilot pack.")
    for platform in platforms:
        if platform_fit["scores"][platform]["probe_status"] != "usable":
            checks["warning"].append(f"W1: {platform} uses stable evergreen strategy because no usable dynamic evidence was available.")
    return {"$schema_version": "0.3.0", "generated_at": utc_now(), "launch_brief": {"app_name": inputs["app_context"]["name"], "one_liner": stage_1["intent_profile"]["app_summary"]["one_liner"], "promo_goal": inputs["positioning"]["promo_goal"], "target_audience": inputs["positioning"]["target_audience"], "key_selling_point": inputs["positioning"]["key_selling_point"], "primary_market": inputs["app_context"].get("target_market") or ["US"]}, "platform_fit": platform_fit, "publish_platforms": platform_fit["publish_platforms"], "pilot_platforms": platform_fit["pilot_platforms"], "strategies": strategies, "deliverables": deliverables, "schedule": {"week_1": schedule, "notes": "Publish only after reviewing product claims and asset dependencies."}, "checks": checks, "_pipeline_meta": {"platform_registry_version": "0.2.0", "playbook_versions": {platform: "registry-only" for platform in platforms}, "probe_meta": probe_meta, "confidence_summary": {platform: platform_fit["scores"][platform]["score_confidence"] for platform in platforms}, "ga4_used": False, "media_generation_deferred": True, "injectable_prompts_count": {"images": sum(len(post["creative"].get("slides", [])) for _, post in posts), "videos": sum(len((post["creative"].get("storyboard") or {}).get("scenes", [])) for _, post in posts)}}}
