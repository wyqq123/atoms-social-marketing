"""Semantic validators for a complete Launch Pack."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator

from .contracts import TREND_TERMS


SCHEMA_PATH = Path(__file__).resolve().parents[2] / "data" / "launch_pack_runtime_schema.json"


def _schema_errors(pack: dict[str, Any]) -> list[str]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return [f"schema:{error.message}" for error in Draft7Validator(schema).iter_errors(pack)]


def validate_launch_pack(pack: dict[str, Any]) -> list[str]:
    errors: list[str] = _schema_errors(pack)
    platforms = pack.get("publish_platforms") or pack.get("pilot_platforms") or []
    posts: dict[str, dict[str, Any]] = {}
    for platform in platforms:
        platform_posts = ((pack.get("deliverables") or {}).get(platform) or {}).get("posts") or []
        if not platform_posts:
            errors.append(f"{platform}:missing_posts")
        for post in platform_posts:
            posts[post.get("post_id", "")] = post
            for field in ("post_id", "title", "body", "cta", "discoverability", "creative"):
                if not post.get(field):
                    errors.append(f"{platform}:missing_{field}")
            creative = post.get("creative") or {}
            if creative.get("kind") == "carousel" and len(creative.get("slides") or []) < 3:
                errors.append(f"{post.get('post_id')}:carousel_requires_three_slides")
            storyboard = creative.get("storyboard")
            if storyboard:
                scenes = storyboard.get("scenes") or []
                if sum(scene.get("duration_s", 0) for scene in scenes) != storyboard.get("total_duration_s"):
                    errors.append(f"{post.get('post_id')}:storyboard_duration_mismatch")
                if not {"hook", "cta"}.issubset({scene.get("purpose") for scene in scenes}):
                    errors.append(f"{post.get('post_id')}:storyboard_requires_hook_and_cta")
    schedule = ((pack.get("schedule") or {}).get("week_1") or [])
    if len(schedule) < 3:
        errors.append("schedule_requires_three_entries")
    for item in schedule:
        if item.get("post_ref") not in posts:
            errors.append(f"schedule_unknown_post_ref:{item.get('post_ref')}")
    serialized = str(pack).lower()
    if any(term.lower() in serialized for term in TREND_TERMS):
        errors.append("prohibited_current_trend_wording")
    return sorted(set(errors))
