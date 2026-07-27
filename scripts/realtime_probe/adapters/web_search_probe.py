"""Web search fallback adapter using Google Custom Search JSON API."""
from __future__ import annotations

import json
import os
import re
import time
from typing import Any
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

from models import AdapterResult, Capability, EvidenceItem, PlatformQuery, ProbeExecutionReport, host_from_url, truncate_excerpt, utc_now

CSE_ENDPOINT = "https://www.googleapis.com/customsearch/v1"
USER_AGENT = "atoms-social-marketing/0.2 (+https://atoms.local)"
DOMAIN_HINT_RE = re.compile(r"\b(site:[^\s]+|reddit\.com|youtube\.com|pinterest\.com|linkedin\.com|tiktok\.com|instagram\.com)", re.I)


def preflight(env: dict[str, str] | None = None, registry_entry: dict[str, Any] | None = None) -> Capability:
    env = env or os.environ
    missing = [name for name in ["GOOGLE_CSE_API_KEY", "GOOGLE_CSE_ID"] if not env.get(name)]
    if missing:
        return Capability("web_search", False, "realtime_api", "missing", "missing_" + "_".join(missing))
    return Capability("web_search", True, "realtime_api", "available", "ready", "medium")


def _source_limited(query: str) -> bool:
    return bool(DOMAIN_HINT_RE.search(query or ""))


def _search(query: PlatformQuery, env: dict[str, str], timeout: float) -> list[dict[str, Any]]:
    if not _source_limited(query.query):
        raise ValueError("web_search_query_requires_source_or_site_filter")
    params = {"key": env["GOOGLE_CSE_API_KEY"], "cx": env["GOOGLE_CSE_ID"], "q": query.query, "num": min(max(query.limit, 1), 8)}
    if query.language:
        params["lr"] = f"lang_{query.language[:2].lower()}"
    req = Request(f"{CSE_ENDPOINT}?{urlencode(params)}", headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return payload.get("items", []) or []


def normalize(raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    counters: dict[str, int] = {}
    for record in raw:
        query = record["query"]
        result = record["result"]
        counters[query.probe_id] = counters.get(query.probe_id, 0) + 1
        evidence_id = f"web_search:{query.probe_id}:w{counters[query.probe_id]:02d}"
        url = result.get("link", "")
        source = host_from_url(url) or urlparse(url).netloc
        item = EvidenceItem(
            evidence_id=evidence_id,
            platform="web_search",
            probe_id=query.probe_id,
            surface=query.surface or "public_search_result",
            title=result.get("title", ""),
            url=url,
            published_at=None,
            text_excerpt=truncate_excerpt(result.get("snippet", "")),
            metrics={},
            author_or_community_context={"source": source},
            source_type="authorized_search_connector",
            known_biases=["search_result_bias", "snippet_only", "no_platform_internal_metrics", "no_demographic_ground_truth"],
        )
        items.append(item.as_dict())
    return items


def fetch(queries: list[dict[str, Any]], timeout_ms: int = 2500, max_items: int = 18, env: dict[str, str] | None = None) -> AdapterResult:
    started = time.monotonic()
    started_at = utc_now()
    capability = preflight(env)
    if not capability.can_run:
        report = ProbeExecutionReport("web_search", "skipped", started_at, 0, 0, 0, capability=capability.as_dict())
        return AdapterResult("web_search", "skipped", [], report.as_dict(), [capability.reason])
    env = env or os.environ
    raw: list[dict[str, Any]] = []
    errors: list[str] = []
    attempted = 0
    budget = max(timeout_ms / 1000, 0.5)
    for q in queries:
        if len(raw) >= max_items:
            break
        elapsed = time.monotonic() - started
        if elapsed >= budget:
            errors.append("web_search_timeout_budget_exhausted")
            break
        query = PlatformQuery.from_dict(q)
        attempted += 1
        try:
            for result in _search(query, env, max(0.5, min(budget - elapsed, 2.0))):
                raw.append({"query": query, "result": result})
                if len(raw) >= max_items:
                    break
        except Exception as exc:
            errors.append(f"{type(exc).__name__}:{str(exc)[:180]}")
    items = normalize(raw)
    latency_ms = int((time.monotonic() - started) * 1000)
    status = "success" if items else "error" if errors else "unavailable"
    report = ProbeExecutionReport("web_search", status, started_at, latency_ms, attempted, len(raw), len(items), errors, capability.as_dict())
    return AdapterResult("web_search", status, items, report.as_dict(), errors)


def skipped_brief() -> dict:
    from models import empty_brief
    capability = preflight()
    return empty_brief("web_search", "skipped", capability.reason)
