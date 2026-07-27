"""Select up to three platforms for optional demand probing."""
from __future__ import annotations

import argparse
from typing import Any

from models import get_platforms, load_json, write_json

REALTIME_PRIORITY = {"reddit": 5, "youtube": 5, "web_search": 3}
CACHE_PRIORITY = {"tiktok": 2, "pinterest": 2, "instagram": 1, "x": 1, "linkedin": 1, "rednote": 1, "douyin": 1}
PUBLISHABLE = {"instagram", "youtube", "tiktok", "reddit", "x", "linkedin", "pinterest", "rednote", "douyin"}


def _intersects(left: list[str], right: list[str]) -> bool:
    return bool({x.lower() for x in left} & {x.lower() for x in right})


def shortlist(registry: dict[str, Any], app_icp: dict[str, Any], platform_scope: list[str] | None, max_platforms: int = 3) -> list[str]:
    platforms = get_platforms(registry)
    markets = app_icp.get("geo_language", {}).get("markets", ["US"])
    languages = app_icp.get("geo_language", {}).get("languages", ["en"])
    candidates = list(platform_scope or PUBLISHABLE)
    if "web_search" not in candidates:
        candidates.append("web_search")

    scored: list[tuple[int, str]] = []
    for platform in candidates:
        entry = platforms.get(platform)
        if not entry:
            continue
        coverage = entry["platform_coverage_registry"]
        access = entry["data_access_profile"]
        mode = access["runtime_access_mode"]
        score = 0
        score += REALTIME_PRIORITY.get(platform, CACHE_PRIORITY.get(platform, 0))
        score += 2 if _intersects(markets, coverage.get("supported_markets", [])) else -2
        score += 2 if _intersects(languages, coverage.get("supported_languages", [])) else -2
        score += 2 if mode == "realtime_api" else 1 if mode in {"cache_only", "authorized_only"} else 0
        if coverage.get("realtime_probe_mode") == "unsupported":
            score -= 4
        scored.append((score, platform))

    scored.sort(key=lambda item: (item[0], REALTIME_PRIORITY.get(item[1], 0)), reverse=True)
    return [platform for _, platform in scored[:max_platforms]]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--app-icp", required=True)
    parser.add_argument("--platform-scope", nargs="*")
    parser.add_argument("--max-platforms", type=int, default=3)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    selected = shortlist(load_json(args.registry), load_json(args.app_icp), args.platform_scope, args.max_platforms)
    write_json(args.output, {"probe_shortlist": selected})


if __name__ == "__main__":
    main()
