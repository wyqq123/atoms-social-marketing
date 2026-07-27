"""Cache/manual adapter that returns cached opportunity briefs when available."""
from __future__ import annotations

import argparse
from pathlib import Path

from cache_store import is_fresh
from models import empty_brief, load_json, write_json


def _brief_from_payload(platform: str, payload: dict) -> dict | None:
    if "briefs" in payload:
        for brief in payload.get("briefs") or []:
            if brief.get("platform") == platform:
                return brief
    if payload.get("platform") == platform:
        return payload
    return None


def load_cached(platform: str, cache_file: str | None, max_age_hours: int | None = None) -> dict:
    if cache_file and Path(cache_file).exists():
        if max_age_hours is not None and not is_fresh(cache_file, max_age_hours):
            brief = empty_brief(platform, "skipped", "cache_stale")
            brief["freshness"] = "cache_stale"
            return brief
        payload = load_json(cache_file)
        if isinstance(payload, dict):
            brief = _brief_from_payload(platform, payload)
            if brief:
                brief = dict(brief)
                if max_age_hours is not None:
                    brief.setdefault("freshness", "cache_fresh")
                return brief
    return empty_brief(platform, "skipped", "cache_miss")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", required=True)
    parser.add_argument("--cache-file")
    parser.add_argument("--max-age-hours", type=int)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    write_json(args.output, load_cached(args.platform, args.cache_file, args.max_age_hours))


if __name__ == "__main__":
    main()
