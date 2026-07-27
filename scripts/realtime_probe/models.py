"""Shared helpers for lightweight realtime demand probe scripts."""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

FORBIDDEN_FIELDS = {"fit_verticals", "fit_goal_types", "relevance_to_atoms", "fit_score", "realtime_adjustment"}
CONFIDENCE_ORDER = {"low": 0, "medium": 1, "medium-high": 2, "high": 3}
ALLOWED_SOURCE_TYPES = {
    "official_api", "public_web_summary", "authorized_search_connector", "cache", "manual_cache",
    "authorized_insight", "official_business_tool_export",
}
MAX_EXCERPT_CHARS = 360


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path: str | Path, data: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def truncate_excerpt(value: Any, limit: int = MAX_EXCERPT_CHARS) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)].rstrip() + "..."


def safe_int(value: Any, default: int | None = 0) -> int | None:
    if value is None or value == "":
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def host_from_url(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def get_platforms(registry: dict[str, Any]) -> dict[str, Any]:
    return registry.get("platforms", registry)


def contains_forbidden_fields(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in FORBIDDEN_FIELDS:
                found.append(key)
            found.extend(contains_forbidden_fields(nested))
    elif isinstance(value, list):
        for item in value:
            found.extend(contains_forbidden_fields(item))
    return sorted(set(found))


def empty_brief(platform: str, status: str, reason: str) -> dict[str, Any]:
    return {
        "platform": platform,
        "status": status,
        "freshness": "not_run",
        "evidence_count": 0,
        "matched_probe_ids": [],
        "audience_clues": [],
        "pain_clues": [],
        "content_clues": [],
        "distribution_clues": [],
        "activity_clues": {"volume": "none", "velocity": "none", "engagement": "none", "saturation": "unknown"},
        "recommended_use": "Use stable platform strategy only; do not claim current demand or trend.",
        "confidence": "medium" if status in {"skipped", "unavailable", "timeout"} else "low",
        "evidence_refs": [],
        "known_biases": [reason],
        "warnings": [reason],
    }


@dataclass(frozen=True)
class PlatformQuery:
    platform: str
    probe_id: str
    query: str
    surface: str
    market: str = "US"
    language: str = "en"
    intent: str | None = None
    variant_type: str | None = None
    expected_evidence_type: str | None = None
    limit: int = 6

    @classmethod
    def from_dict(cls, value: dict[str, Any], default_limit: int = 6) -> "PlatformQuery":
        limit = safe_int(value.get("limit"), default_limit) or default_limit
        return cls(
            platform=str(value.get("platform", "")),
            probe_id=str(value.get("probe_id", "p00")),
            query=str(value.get("query", "")).strip(),
            surface=str(value.get("surface", "")),
            market=str(value.get("market", "US")),
            language=str(value.get("language", "en")),
            intent=value.get("intent"),
            variant_type=value.get("variant_type"),
            expected_evidence_type=value.get("expected_evidence_type"),
            limit=limit,
        )

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EvidenceItem:
    evidence_id: str
    platform: str
    probe_id: str
    surface: str
    title: str
    url: str
    published_at: str | None = None
    text_excerpt: str = ""
    metrics: dict[str, int | None] = field(default_factory=dict)
    author_or_community_context: dict[str, Any] = field(default_factory=dict)
    source_type: str = "official_api"
    observed_at: str = field(default_factory=utc_now)
    known_biases: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["title"] = truncate_excerpt(data["title"], 180)
        data["text_excerpt"] = truncate_excerpt(data["text_excerpt"])
        if data["source_type"] not in ALLOWED_SOURCE_TYPES:
            data["source_type"] = "public_web_summary"
            data["known_biases"] = sorted(set(data["known_biases"] + ["source_type_normalized"]))
        return data


@dataclass
class ProbeExecutionReport:
    platform: str
    status: str
    started_at: str
    latency_ms: int
    queries_attempted: int
    items_fetched: int
    items_after_dedupe: int = 0
    errors: list[str] = field(default_factory=list)
    capability: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AdapterResult:
    platform: str
    status: str
    items: list[dict[str, Any]]
    report: dict[str, Any]
    errors: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Capability:
    platform: str
    can_run: bool
    runtime_access_mode: str
    credential_status: str
    reason: str
    confidence_cap: str = "medium"

    def as_dict(self) -> dict[str, Any]:
        return {
            "platform": self.platform,
            "can_run": self.can_run,
            "runtime_access_mode": self.runtime_access_mode,
            "credential_status": self.credential_status,
            "reason": self.reason,
            "confidence_cap": self.confidence_cap,
        }
