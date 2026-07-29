"""Stage 4 renderer for complete posts and deferred multi-asset prompts."""
from __future__ import annotations

from typing import Any

from .llm_gateway import StructuredLLMGateway


def _prompt(subject: str, aspect_ratio: str) -> dict[str, str]:
    return {"trigger": "on-demand", "injectable_prompt": f"Clean editorial product marketing visual for {subject}, show authentic product workflow rather than invented UI, clear hierarchy, natural light, generous text-safe space, {aspect_ratio} aspect ratio", "aspect_ratio": aspect_ratio}


def _carousel(title: str, value: str) -> dict[str, Any]:
    roles = [("cover", title), ("pain", "The manual workflow takes too long."), ("mechanism", value), ("cta", "Try the workflow with one product today.")]
    return {"kind": "carousel", "slides": [{"slide_index": index, "role": role, "on_image_copy": copy, "speaker_notes": None, "image_prompt": _prompt(copy, "4:5")} for index, (role, copy) in enumerate(roles, start=1)], "storyboard": None, "asset_requirements": ["built_app_screenshot"]}


def _video(title: str, value: str) -> dict[str, Any]:
    scenes = [(1, 3, "hook", title), (2, 4, "context", "Show the manual product-page copy workflow."), (3, 5, "reveal", value), (4, 3, "cta", "Open the product and try one workflow today.")]
    return {"kind": "video", "slides": [], "storyboard": {"total_duration_s": 15, "scenes": [{"scene_id": index, "duration_s": duration, "purpose": purpose, "visual_note": text, "text_overlay": text, "voiceover_or_dialogue": text, "b_roll_requirement": "Use a provided product screenshot or screen recording when available.", "media_prompts": {"video_prompt": _prompt(text, "9:16"), "image_prompt": None}} for index, duration, purpose, text in scenes]}, "asset_requirements": ["built_app_demo_recording"]}


def build_deliverables(stage_1: dict[str, Any], platform_fit: dict[str, Any], strategies: dict[str, Any], gateway: StructuredLLMGateway | None = None) -> dict[str, Any]:
    if gateway is not None:
        generated = gateway.generate_json(
            prompt_id="atoms-social-marketing.stage-4",
            input={"stage_1": stage_1, "platform_fit": platform_fit, "strategies": strategies},
            schema={"type": "object"},
        )
        if isinstance(generated, dict) and generated:
            return generated
    audience = stage_1["intent_profile"]["audience"]["primary_persona"]
    value = stage_1["intent_profile"]["value_prop"]["key_selling_point"]
    goal = stage_1["intent_profile"]["promo_intent"]["goal_metric_hint"]
    deliverables: dict[str, Any] = {}
    for platform, strategy in strategies.items():
        title = f"A faster product-page copy workflow for {audience}"
        surface = strategy["angles"][0]["post_type"]
        is_video = surface in {"youtube_short", "short_video"}
        body = f"For {audience}: stop starting every product page from a blank document. {value}. Start with one live product, review the output against your product facts, then publish the version that makes the customer benefit clearer. {goal}."
        if platform == "reddit":
            body = f"If you are {audience}, manual product-page copy can become a bottleneck. {value}. I would test it on one product first, compare the draft with the current page, and keep only changes that make the benefit clearer. {goal}."
        post = {"post_id": f"{platform}-01", "angle_id": strategy["angles"][0]["angle_id"], "platform": platform, "surface": surface, "format": "video" if is_video else "text" if platform == "reddit" else "image_carousel", "title": title, "hook": title, "body": body, "cta": {"text": "Try it with one product today.", "link_style": "description-link" if platform == "youtube" else "comment-pin" if platform in {"instagram", "tiktok"} else "profile-link"}, "discoverability": {"hashtags": ["#ecommerce", "#shopify", "#productcopy"] if platform in {"instagram", "tiktok", "rednote", "douyin"} else [], "keywords": ["product page copy", "ecommerce conversion", "Shopify seller"], "placement_note": "Use keywords in the title and opening paragraph."}, "creative": _video(title, value) if is_video else _carousel(title, value) if platform != "reddit" else {"kind": "text", "slides": [], "storyboard": None, "asset_requirements": []}, "confidence": "medium", "evidence_refs": platform_fit["scores"][platform]["_evidence_refs"], "why_this_copy": "Evergreen copy derived from confirmed positioning and stable platform profile."}
        deliverables[platform] = {"posts": [post], "storyboards": [], "ab_variants": []}
    return deliverables
