"""Typed constants and JSON-safe helpers for positioning intake."""
from __future__ import annotations

from typing import Any

FIELDS = ("promo_goal", "target_audience", "key_selling_point")
FIELD_LABELS = {
    "promo_goal": "promo_goal",
    "target_audience": "target_audience",
    "key_selling_point": "key_selling_point",
}
ALLOWED_SOURCES = {"user_prompt", "app_context", "builder_prompt", "user_custom", "user_selected", "form", "unknown"}
ALLOWED_CONFIDENCE = {"low", "medium", "high"}


def empty_field() -> dict[str, Any]:
    return {
        "value": None,
        "source": "unknown",
        "evidence_excerpt": None,
        "confidence": "low",
        "status": "missing",
        "user_confirmed": False,
    }


def normalize_candidate(value: Any) -> dict[str, Any]:
    value = value if isinstance(value, dict) else {}
    text = str(value.get("value") or "").strip()
    source = str(value.get("source") or "unknown")
    confidence = str(value.get("confidence") or "low")
    excerpt = str(value.get("evidence_excerpt") or "").strip()[:160] or None
    if source not in ALLOWED_SOURCES:
        source = "unknown"
    if confidence not in ALLOWED_CONFIDENCE:
        confidence = "low"
    field = empty_field()
    field.update({
        "value": text or None,
        "source": source,
        "evidence_excerpt": excerpt,
        "confidence": confidence,
        "status": "candidate" if text else "missing",
    })
    return field


def copy_positioning(fields: dict[str, dict[str, Any]]) -> dict[str, str]:
    return {field: str(fields[field].get("value") or "").strip() for field in FIELDS}
