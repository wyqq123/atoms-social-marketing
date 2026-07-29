"""Stage 3 platform-native strategy generation."""
from __future__ import annotations

from typing import Any

from .llm_gateway import StructuredLLMGateway

SURFACES = {"instagram": "carousel", "youtube": "youtube_short", "reddit": "reddit_post", "tiktok": "short_video", "linkedin": "linkedin_document", "pinterest": "pin", "x": "thread", "rednote": "note", "douyin": "short_video"}


def build_strategies(stage_1: dict[str, Any], platform_fit: dict[str, Any], gateway: StructuredLLMGateway | None = None) -> dict[str, Any]:
    if gateway is not None:
        generated = gateway.generate_json(
            prompt_id="atoms-social-marketing.stage-3",
            input={"stage_1": stage_1, "platform_fit": platform_fit},
            schema={"type": "object"},
        )
        if isinstance(generated, dict) and generated:
            return generated
    value = stage_1["intent_profile"]["value_prop"]["key_selling_point"]
    audience = stage_1["intent_profile"]["audience"]["primary_persona"]
    strategies: dict[str, Any] = {}
    for platform in platform_fit["publish_platforms"] or platform_fit["pilot_platforms"]:
        score = platform_fit["scores"][platform]
        strategies[platform] = {
            "platform": platform,
            "angles": [{"angle_id": f"{platform}-01", "core_message": value, "hook_pattern": "before-after", "post_type": SURFACES[platform], "narrative_arc": f"Show {audience} the problem, the mechanism, and a low-friction next step."}],
            "discoverability": {"hashtags": [], "keywords": [audience, value]},
            "posting_cadence": {"week_1_frequency": "1-2 posts", "best_time_slots": ["09:30 local time"], "rationale_ref": "stable_platform_profile"},
            "trend_borrow": None,
            "_rationale": "Uses evergreen platform strategy because no fresh usable evidence is available." if score["probe_status"] != "usable" else "Uses bounded wording calibration from usable evidence.",
        }
    return strategies
