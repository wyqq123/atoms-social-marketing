"""JSON cache helper for social intelligence briefs and raw evidence."""
from __future__ import annotations

import argparse
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from models import load_json, write_json

DEFAULT_CACHE_ROOT = Path(".cache/social_intel")


def _safe(value: Any, limit: int = 80) -> str:
    return "-".join(str(value or "unknown").lower().replace("|", " ").split())[:limit] or "unknown"


def cache_key(platform: str, market: str, language: str, icp_cluster: str, demand_cluster: str, week: str) -> str:
    return "|".join([_safe(platform), _safe(market), _safe(language), _safe(icp_cluster), _safe(demand_cluster), _safe(week)])


def week_id(now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    year, week, _ = now.isocalendar()
    return f"{year}-W{week:02d}"


def demand_cluster_from_probes(probes: dict[str, Any]) -> str:
    parts: list[str] = []
    if probes.get("icp_summary"):
        parts.append(str(probes["icp_summary"]))
    for probe in probes.get("probes", [])[:3]:
        parts.append(str(probe.get("query") or probe.get("intent") or ""))
    digest = hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:12]
    label = _safe(parts[0] if parts else "runtime")[:40]
    return f"{label}-{digest}"


def icp_cluster_from_app_icp(app_icp: dict[str, Any]) -> str:
    identity = app_icp.get("end_user_identity", {})
    terms: list[str] = []
    for key in ["roles", "organization_context", "industry_context", "community_identities"]:
        for item in identity.get(key, []) or []:
            terms.append(str(item.get("value") if isinstance(item, dict) else item))
    if not terms:
        terms.append(app_icp.get("icp_id", "runtime"))
    digest = hashlib.sha1("|".join(terms).encode("utf-8")).hexdigest()[:10]
    return f"{_safe(terms[0])[:40]}-{digest}"


def cache_path(root: str | Path, kind: str, platform: str, market: str, language: str, key: str) -> Path:
    return Path(root) / kind / _safe(platform) / _safe(market) / _safe(language) / f"{_safe(key, 140)}.json"


def is_fresh(path: str | Path, max_age_hours: int) -> bool:
    target = Path(path)
    if not target.exists():
        return False
    modified = datetime.fromtimestamp(target.stat().st_mtime, tz=timezone.utc)
    age_hours = (datetime.now(timezone.utc) - modified).total_seconds() / 3600
    return age_hours <= max_age_hours


def read_fresh(path: str | Path, max_age_hours: int) -> dict[str, Any] | None:
    target = Path(path)
    if not is_fresh(target, max_age_hours):
        return None
    payload = load_json(target)
    return payload if isinstance(payload, dict) else None


def write_cache(path: str | Path, payload: Any) -> None:
    write_json(path, payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input")
    parser.add_argument("--output")
    parser.add_argument("--max-age-hours", type=int, default=24)
    parser.add_argument("--check-fresh", action="store_true")
    args = parser.parse_args()
    if args.check_fresh:
        print("fresh" if is_fresh(args.input, args.max_age_hours) else "stale")
        return
    if args.input and args.output:
        write_json(args.output, load_json(args.input))


if __name__ == "__main__":
    main()
