"""Shared runtime constants and JSON-safe helpers."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

PUBLISHABLE_PLATFORMS = (
    "instagram", "youtube", "tiktok", "reddit", "x", "linkedin", "pinterest", "rednote", "douyin",
)
TREND_TERMS = ("currently trending", "recently everyone", "当前热门", "近期大家都在讨论", "正在流行")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def clean_text(value: Any, fallback: str = "") -> str:
    return " ".join(str(value or fallback).split()).strip()


def production_capacity(inputs: dict[str, Any]) -> str:
    constraints = ((inputs.get("production_context") or {}).get("creator_constraints") or {})
    value = constraints.get("weekly_content_capacity", "unknown")
    return value if value in {"low", "medium", "high"} else "unknown"
