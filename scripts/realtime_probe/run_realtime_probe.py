"""Run lightweight Stage 2b demand probe with safe degradation."""
from __future__ import annotations

import argparse
import importlib
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed
from pathlib import Path
from typing import Any

from adapters.cached_platform_probe import load_cached
from cache_store import DEFAULT_CACHE_ROOT, cache_path, demand_cluster_from_probes, icp_cluster_from_app_icp, week_id, write_cache
from models import AdapterResult, empty_brief, get_platforms, load_json, utc_now, write_json
from query_planner import plan_queries
from select_platform_shortlist import shortlist
from summarize_opportunity_brief import summarize
from validate_probe_output import validate_brief, validate_item

REALTIME_ADAPTERS = {"reddit": "adapters.reddit_probe", "youtube": "adapters.youtube_probe", "web_search": "adapters.web_search_probe"}


def _platform_access(registry: dict[str, Any], platform: str) -> str:
    entry = get_platforms(registry).get(platform, {})
    return entry.get("data_access_profile", {}).get("runtime_access_mode", "unsupported")


def _markets_languages(app_icp: dict[str, Any]) -> tuple[str, str]:
    geo = app_icp.get("geo_language", {}) or {}
    return (geo.get("markets") or ["US"])[0], (geo.get("languages") or ["en"])[0]


def cache_key_for_runtime(platform: str, market: str, language: str, app_icp: dict[str, Any], probes: dict[str, Any]) -> str:
    from cache_store import cache_key
    return cache_key(platform, market, language, icp_cluster_from_app_icp(app_icp), demand_cluster_from_probes(probes), week_id())


def _compatible_cache_path(args: argparse.Namespace, platform: str, app_icp: dict[str, Any], probes: dict[str, Any]) -> Path | None:
    if not args.cache_root:
        return None
    market, language = _markets_languages(app_icp)
    key = cache_key_for_runtime(platform, market, language, app_icp, probes)
    return cache_path(args.cache_root, "briefs", platform, market, language, key)


def _load_any_cache(platform: str, args: argparse.Namespace, app_icp: dict[str, Any], probes: dict[str, Any]) -> dict[str, Any]:
    direct = load_cached(platform, args.cache_file, args.fresh_cache_max_age_hours)
    if direct.get("status") != "skipped" or "cache_miss" not in direct.get("known_biases", []):
        return direct
    runtime_path = _compatible_cache_path(args, platform, app_icp, probes)
    if runtime_path and runtime_path.exists():
        return load_cached(platform, str(runtime_path), args.fresh_cache_max_age_hours)
    return direct


def _run_adapter(platform: str, queries: list[dict[str, Any]], args: argparse.Namespace, registry: dict[str, Any]) -> AdapterResult:
    module = importlib.import_module(REALTIME_ADAPTERS[platform])
    entry = get_platforms(registry).get(platform, {})
    capability = module.preflight(registry_entry=entry)
    if args.no_network:
        return AdapterResult(platform, "skipped", [], {
            "platform": platform, "status": "skipped", "started_at": utc_now(), "latency_ms": 0,
            "queries_attempted": 0, "items_fetched": 0, "items_after_dedupe": 0,
            "errors": ["no_network_enabled"], "capability": capability.as_dict(),
        }, ["no_network_enabled"])
    if not capability.can_run:
        return AdapterResult(platform, "skipped", [], {
            "platform": platform, "status": "skipped", "started_at": utc_now(), "latency_ms": 0,
            "queries_attempted": 0, "items_fetched": 0, "items_after_dedupe": 0,
            "errors": [capability.reason], "capability": capability.as_dict(),
        }, [capability.reason])
    return module.fetch(queries, timeout_ms=args.per_platform_timeout_ms, max_items=args.results_per_query * max(1, len(queries)))


def _dedupe_items(items: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for item in items:
        key = item.get("url") or item.get("evidence_id")
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
        if len(deduped) >= limit:
            break
    return deduped


def _brief_from_result(platform: str, result: AdapterResult, probes: dict[str, Any]) -> dict[str, Any]:
    if result.items:
        return summarize(result.items, probes, platform)
    reason = result.errors[0] if result.errors else result.status
    status = "timeout" if "timeout" in reason else "skipped" if result.status == "skipped" else "unavailable"
    return empty_brief(platform, status, reason)


def _validate_or_degrade(brief: dict[str, Any], warnings: list[str]) -> dict[str, Any]:
    errors = validate_brief(brief)
    if errors:
        warnings.extend(errors)
        return empty_brief(brief.get("platform", "unknown"), "unavailable", "validation_failed")
    return brief


def run(args: argparse.Namespace) -> dict[str, Any]:
    registry = load_json(args.platform_registry)
    app_icp = load_json(args.app_icp)
    probes = load_json(args.demand_probes)
    selected = shortlist(registry, app_icp, args.platform_scope, args.max_platforms)
    warnings: list[str] = []
    briefs_by_platform: dict[str, dict[str, Any]] = {}
    reports: list[dict[str, Any]] = []
    raw_items: list[dict[str, Any]] = []
    realtime_jobs: dict[str, list[dict[str, Any]]] = {}

    for platform in selected:
        cached = _load_any_cache(platform, args, app_icp, probes)
        if cached.get("status") != "skipped" or "cache_miss" not in cached.get("known_biases", []):
            briefs_by_platform[platform] = cached
            reports.append({"platform": platform, "status": "cache_hit", "items_fetched": cached.get("evidence_count", 0), "capability": {"runtime_access_mode": _platform_access(registry, platform), "source": "cache"}})
            continue
        access_mode = _platform_access(registry, platform)
        if platform not in REALTIME_ADAPTERS or access_mode in {"cache_only", "manual_only", "authorized_only", "unsupported"}:
            reason = f"{access_mode}_requires_cache_or_authorization" if access_mode != "realtime_api" else "no_adapter"
            briefs_by_platform[platform] = empty_brief(platform, "skipped", reason)
            reports.append({"platform": platform, "status": "skipped", "items_fetched": 0, "capability": {"runtime_access_mode": access_mode}})
            continue
        queries = plan_queries(platform, probes, args.queries_per_platform)
        for query in queries:
            query["limit"] = args.results_per_query
        realtime_jobs[platform] = queries

    if realtime_jobs:
        with ThreadPoolExecutor(max_workers=len(realtime_jobs)) as executor:
            futures = {executor.submit(_run_adapter, platform, queries, args, registry): platform for platform, queries in realtime_jobs.items()}
            try:
                completed = as_completed(futures, timeout=max(args.timeout_ms / 1000, 1))
                for future in completed:
                    platform = futures[future]
                    try:
                        result = future.result()
                    except Exception as exc:
                        error = f"runner:{type(exc).__name__}:{str(exc)[:160]}"
                        result = AdapterResult(platform, "error", [], {"platform": platform, "status": "error", "started_at": utc_now(), "latency_ms": 0, "queries_attempted": len(realtime_jobs.get(platform, [])), "items_fetched": 0, "items_after_dedupe": 0, "errors": [error], "capability": {"runtime_access_mode": _platform_access(registry, platform)}}, [error])
                    result.items = _dedupe_items(result.items, args.results_per_query * args.queries_per_platform)
                    result.report["items_after_dedupe"] = len(result.items)
                    raw_items.extend(result.items)
                    reports.append(result.report)
                    briefs_by_platform[platform] = _brief_from_result(platform, result, probes)
            except TimeoutError:
                unfinished = set(realtime_jobs) - set(briefs_by_platform)
                for platform in unfinished:
                    briefs_by_platform[platform] = empty_brief(platform, "timeout", "global_timeout_budget_exhausted")
                    reports.append({"platform": platform, "status": "timeout", "items_fetched": 0, "capability": {"runtime_access_mode": _platform_access(registry, platform)}})

    raw_items = _dedupe_items(raw_items, 60)
    for item in raw_items:
        warnings.extend(validate_item(item))
    briefs = [_validate_or_degrade(briefs_by_platform[p], warnings) for p in selected]

    if args.write_raw_cache:
        market, language = _markets_languages(app_icp)
        for platform in selected:
            brief = briefs_by_platform.get(platform)
            if brief:
                key = cache_key_for_runtime(platform, market, language, app_icp, probes)
                write_cache(cache_path(args.cache_root, "briefs", platform, market, language, key), brief)
        safe_stamp = utc_now().replace(":", "").replace("-", "")
        write_cache(Path(args.cache_root) / "raw" / f"runtime-{safe_stamp}.json", {"items": raw_items})

    return {
        "generated_at": utc_now(),
        "global_timeout_ms": args.timeout_ms,
        "platforms_attempted": selected,
        "demand_probe_pack_ref": probes.get("app_id", "runtime"),
        "briefs": briefs,
        "execution_reports": reports,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--app-icp", required=True)
    parser.add_argument("--demand-probes", required=True)
    parser.add_argument("--platform-registry", default="data/platform_registry.json")
    parser.add_argument("--platform-scope", nargs="*")
    parser.add_argument("--max-platforms", type=int, default=3)
    parser.add_argument("--timeout-ms", type=int, default=8000)
    parser.add_argument("--per-platform-timeout-ms", type=int, default=2500)
    parser.add_argument("--queries-per-platform", type=int, default=3)
    parser.add_argument("--results-per-query", type=int, default=6)
    parser.add_argument("--fresh-cache-max-age-hours", type=int, default=24)
    parser.add_argument("--cache-file")
    parser.add_argument("--cache-root", default=str(DEFAULT_CACHE_ROOT))
    parser.add_argument("--write-raw-cache", action="store_true")
    parser.add_argument("--web-provider", choices=["google_cse"], default="google_cse")
    parser.add_argument("--no-network", action="store_true")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    write_json(args.output, run(args))


if __name__ == "__main__":
    main()
