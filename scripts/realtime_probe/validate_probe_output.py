"""Validate opportunity evidence brief output and block score-field pollution."""
from __future__ import annotations

import argparse
import sys
from typing import Any

from models import ALLOWED_SOURCE_TYPES, MAX_EXCERPT_CHARS, contains_forbidden_fields, load_json

REQUIRED = {
    "platform", "status", "freshness", "evidence_count", "matched_probe_ids", "audience_clues",
    "pain_clues", "content_clues", "distribution_clues", "activity_clues", "recommended_use",
    "confidence", "evidence_refs", "known_biases",
}
ALLOWED_STATUS = {"usable", "weak", "unavailable", "timeout", "error", "skipped", "partial"}
ALLOWED_CONFIDENCE = {"low", "medium", "medium-high", "high"}
SENSITIVE_MARKERS = {"cookie", "authorization", "access_token", "refresh_token", "client_secret"}


def _briefs(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict) and "briefs" in payload:
        return payload["briefs"]
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        return [payload]
    return []


def _items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict) and "items" in payload:
        return payload["items"]
    if isinstance(payload, dict) and "raw_items" in payload:
        return payload["raw_items"]
    return []


def validate_brief(brief: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    platform = brief.get("platform", "<unknown>")
    missing = sorted(REQUIRED - set(brief))
    if missing:
        errors.append(f"{platform}: missing fields {missing}")
    if brief.get("status") not in ALLOWED_STATUS:
        errors.append(f"{platform}: invalid status {brief.get('status')}")
    if brief.get("confidence") not in ALLOWED_CONFIDENCE:
        errors.append(f"{platform}: invalid confidence {brief.get('confidence')}")
    refs = brief.get("evidence_refs") or []
    if brief.get("status") == "usable" and len(refs) < 2:
        errors.append(f"{platform}: usable requires at least 2 evidence_refs")
    if brief.get("evidence_count", 0) < len(refs):
        errors.append(f"{platform}: evidence_count less than evidence_refs length")
    activity = brief.get("activity_clues") or {}
    for key in ["volume", "velocity", "engagement", "saturation"]:
        if key not in activity:
            errors.append(f"{platform}: activity_clues missing {key}")
    forbidden = contains_forbidden_fields(brief)
    if forbidden:
        errors.append(f"{platform}: forbidden fields {forbidden}")
    serialized = str(brief).lower()
    leaked = sorted(marker for marker in SENSITIVE_MARKERS if marker in serialized)
    if leaked:
        errors.append(f"{platform}: possible sensitive marker(s) {leaked}")
    return errors


def validate_item(item: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    ref = item.get("evidence_id", "<unknown>")
    if item.get("source_type") not in ALLOWED_SOURCE_TYPES:
        errors.append(f"{ref}: invalid source_type {item.get('source_type')}")
    if len(str(item.get("text_excerpt", ""))) > MAX_EXCERPT_CHARS:
        errors.append(f"{ref}: text_excerpt too long")
    forbidden = contains_forbidden_fields(item)
    if forbidden:
        errors.append(f"{ref}: forbidden fields {forbidden}")
    serialized = str(item).lower()
    leaked = sorted(marker for marker in SENSITIVE_MARKERS if marker in serialized)
    if leaked:
        errors.append(f"{ref}: possible sensitive marker(s) {leaked}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    args = parser.parse_args()
    payload = load_json(args.input)
    errors: list[str] = []
    for brief in _briefs(payload):
        errors.extend(validate_brief(brief))
    for item in _items(payload):
        errors.extend(validate_item(item))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        raise SystemExit(1)
    print("valid")


if __name__ == "__main__":
    main()
