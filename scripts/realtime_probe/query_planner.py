"""Plan platform-native queries from a Stage 1 demand_probe_pack."""
from __future__ import annotations

import argparse
import shlex
from typing import Any

from models import load_json, write_json

REDDIT_INTENTS = {"pain_expression", "problem_search", "alternative_comparison", "trigger_moment"}
YOUTUBE_INTENTS = {"jtbd_how_to", "problem_search", "alternative_comparison", "desired_outcome"}

VARIANT_ORDER = {
    "platform_native": 0,
    "long_tail_precision": 1,
    "keyword_recall": 2,
    "primary_query": 3,
}


def _probes(pack: dict[str, Any]) -> list[dict[str, Any]]:
    return sorted(pack.get("probes", []), key=lambda p: p.get("priority", 0), reverse=True)


def _quote(text: str) -> str:
    return shlex.quote(text).replace("'", '"') if " " in text else text


def _first(terms: dict[str, list[Any]], key: str) -> str | None:
    values = terms.get(key) or []
    if not values:
        return None
    value = values[0]
    if isinstance(value, dict):
        value = value.get("value")
    return str(value) if value else None


def _end_user_identity(terms: dict[str, list[Any]]) -> str | None:
    return _first(terms, "end_user_identity") or _first(terms, "identity")


def _variant_candidates(probe: dict[str, Any], platform: str) -> list[tuple[str, str]]:
    variants: list[tuple[str, str]] = []
    for variant in probe.get("query_variants") or []:
        variant_type = variant.get("type")
        if variant_type == "platform_native":
            native = (variant.get(platform) or "").strip()
            if native:
                variants.append((native, "platform_native"))
        elif variant_type == "long_tail_precision":
            query = (variant.get("query") or "").strip()
            if query:
                variants.append((query, "long_tail_precision"))
        elif variant_type == "keyword_recall":
            terms = [str(term).strip() for term in variant.get("terms") or [] if str(term).strip()]
            if terms:
                variants.append((" ".join(terms), "keyword_recall"))

    primary = (probe.get("query") or "").strip()
    if primary:
        variants.append((primary, "primary_query"))
    return variants


def _fallback_platform_query(platform: str, probe: dict[str, Any], query: str) -> str:
    terms = probe.get("source_terms", {})
    intent = probe.get("intent")

    if platform == "youtube":
        jtbd = _first(terms, "jtbd")
        identity = _end_user_identity(terms)
        return f"how to {jtbd} for {identity}" if jtbd and identity else query

    if platform == "web_search":
        identity = _end_user_identity(terms)
        domain_hint = "site:reddit.com/r" if intent in REDDIT_INTENTS else "site:youtube.com"
        native_query = f"{domain_hint} {_quote(query)}"
        if identity:
            native_query = f"{native_query} {_quote(identity)}"
        return native_query

    return query


def _surface_for(platform: str) -> str:
    if platform == "reddit":
        return "subreddit_search"
    if platform == "youtube":
        return "youtube_search"
    return "public_search_result"


def _intent_allowed(platform: str, intent: str | None) -> bool:
    if platform == "reddit":
        return intent in REDDIT_INTENTS
    if platform == "youtube":
        return intent in YOUTUBE_INTENTS
    return platform == "web_search"


def plan_queries(platform: str, demand_probe_pack: dict[str, Any], limit: int = 3) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for probe in _probes(demand_probe_pack):
        intent = probe.get("intent")
        if not _intent_allowed(platform, intent):
            continue
        market = probe.get("market", "US")
        language = probe.get("language", "en")
        probe_id = probe.get("probe_id", "p00")
        priority = float(probe.get("priority", 0) or 0)

        for raw_query, variant_type in _variant_candidates(probe, platform):
            query = raw_query if variant_type == "platform_native" else _fallback_platform_query(platform, probe, raw_query)
            candidates.append({
                "platform": platform,
                "probe_id": probe_id,
                "query": query,
                "surface": _surface_for(platform),
                "market": market,
                "language": language,
                "intent": intent,
                "variant_type": variant_type,
                "expected_evidence_type": probe.get("expected_evidence_type"),
                "limit": 6,
                "_priority": priority,
            })

    candidates.sort(key=lambda c: (-c["_priority"], VARIANT_ORDER.get(c["variant_type"], 9)))

    planned: list[dict[str, Any]] = []
    seen_queries: set[str] = set()
    seen_intents: set[str] = set()
    seen_variant_types: set[str] = set()

    def add(candidate: dict[str, Any]) -> None:
        query_key = candidate["query"].lower()
        if query_key in seen_queries or len(planned) >= limit:
            return
        seen_queries.add(query_key)
        seen_intents.add(candidate.get("intent") or "")
        seen_variant_types.add(candidate.get("variant_type") or "")
        candidate.pop("_priority", None)
        planned.append(candidate)

    for candidate in candidates:
        if candidate.get("variant_type") not in seen_variant_types:
            add(candidate)
    for candidate in candidates:
        if candidate.get("intent") not in seen_intents:
            add(candidate)
    for candidate in candidates:
        add(candidate)

    return planned


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--demand-probes", required=True)
    parser.add_argument("--platform", required=True)
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    write_json(args.output, {"queries": plan_queries(args.platform, load_json(args.demand_probes), args.limit)})


if __name__ == "__main__":
    main()
