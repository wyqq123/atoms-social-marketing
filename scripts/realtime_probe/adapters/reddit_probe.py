"""Reddit realtime demand probe adapter using OAuth Data API."""
from __future__ import annotations

import base64
import json
import os
import re
import time
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from models import AdapterResult, Capability, EvidenceItem, PlatformQuery, ProbeExecutionReport, safe_int, truncate_excerpt, utc_now

TOKEN_ENDPOINT = "https://www.reddit.com/api/v1/access_token"
API_BASE = "https://oauth.reddit.com"


def preflight(env: dict[str, str] | None = None, registry_entry: dict[str, Any] | None = None) -> Capability:
    env = env or os.environ
    required = ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USER_AGENT"]
    missing = [name for name in required if not env.get(name)]
    if missing:
        return Capability("reddit", False, "realtime_api", "missing", "missing_" + "_".join(missing))
    return Capability("reddit", True, "realtime_api", "available", "ready", "medium-high")


def _get_token(env: dict[str, str], timeout: float) -> str:
    auth = f"{env['REDDIT_CLIENT_ID']}:{env['REDDIT_CLIENT_SECRET']}".encode("utf-8")
    body = urlencode({"grant_type": "client_credentials"}).encode("utf-8")
    req = Request(
        TOKEN_ENDPOINT,
        data=body,
        headers={
            "Authorization": "Basic " + base64.b64encode(auth).decode("ascii"),
            "User-Agent": env["REDDIT_USER_AGENT"],
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    with urlopen(req, timeout=timeout) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return payload["access_token"]


def _subreddit_hint(query: str) -> str | None:
    match = re.search(r"(?:^|\s)(?:r/|site:reddit\.com/r/)([A-Za-z0-9_]+)", query)
    return match.group(1) if match else None


def _search(query: PlatformQuery, token: str, user_agent: str, timeout: float) -> list[dict[str, Any]]:
    subreddit = _subreddit_hint(query.query)
    params = {"q": query.query, "limit": min(max(query.limit, 1), 8), "sort": "relevance", "t": "month", "raw_json": "1"}
    if subreddit:
        path = f"/r/{quote(subreddit)}/search"
        params["restrict_sr"] = "1"
    else:
        path = "/search"
    req = Request(f"{API_BASE}{path}?{urlencode(params)}", headers={"Authorization": f"Bearer {token}", "User-Agent": user_agent})
    with urlopen(req, timeout=timeout) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return [child.get("data", {}) for child in (payload.get("data", {}).get("children", []) or [])]


def _published_at(created_utc: Any) -> str | None:
    value = safe_int(created_utc, None)
    if value is None:
        return None
    return datetime.fromtimestamp(value, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize(raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    counters: dict[str, int] = {}
    for record in raw:
        query = record["query"]
        post = record["post"]
        counters[query.probe_id] = counters.get(query.probe_id, 0) + 1
        evidence_id = f"reddit:{query.probe_id}:r{counters[query.probe_id]:02d}"
        permalink = post.get("permalink") or ""
        url = permalink if permalink.startswith("http") else f"https://www.reddit.com{permalink}"
        item = EvidenceItem(
            evidence_id=evidence_id,
            platform="reddit",
            probe_id=query.probe_id,
            surface=query.surface or "subreddit_search",
            title=post.get("title", ""),
            url=url,
            published_at=_published_at(post.get("created_utc")),
            text_excerpt=truncate_excerpt(post.get("selftext") or post.get("selftext_html") or ""),
            metrics={"score": safe_int(post.get("score"), 0), "comments": safe_int(post.get("num_comments"), 0)},
            author_or_community_context={"community": f"r/{post.get('subreddit', '')}".rstrip("/"), "author_public_context": None},
            source_type="official_api",
            known_biases=["reddit_search_result_bias", "selected_subreddit_bias", "no_demographic_ground_truth"],
        )
        items.append(item.as_dict())
    return items


def fetch(queries: list[dict[str, Any]], timeout_ms: int = 2500, max_items: int = 18, env: dict[str, str] | None = None) -> AdapterResult:
    started = time.monotonic()
    started_at = utc_now()
    capability = preflight(env)
    if not capability.can_run:
        report = ProbeExecutionReport("reddit", "skipped", started_at, 0, 0, 0, capability=capability.as_dict())
        return AdapterResult("reddit", "skipped", [], report.as_dict(), [capability.reason])
    env = env or os.environ
    raw: list[dict[str, Any]] = []
    errors: list[str] = []
    attempted = 0
    budget = max(timeout_ms / 1000, 0.5)
    try:
        token = _get_token(env, min(2.0, budget))
    except Exception as exc:
        error = f"oauth:{type(exc).__name__}:{str(exc)[:160]}"
        report = ProbeExecutionReport("reddit", "error", started_at, int((time.monotonic() - started) * 1000), 0, 0, errors=[error], capability=capability.as_dict())
        return AdapterResult("reddit", "error", [], report.as_dict(), [error])
    for q in queries:
        if len(raw) >= max_items:
            break
        elapsed = time.monotonic() - started
        if elapsed >= budget:
            errors.append("reddit_timeout_budget_exhausted")
            break
        query = PlatformQuery.from_dict(q)
        attempted += 1
        try:
            posts = _search(query, token, env["REDDIT_USER_AGENT"], max(0.5, min(budget - elapsed, 2.0)))
            for post in posts:
                raw.append({"query": query, "post": post})
                if len(raw) >= max_items:
                    break
        except Exception as exc:
            errors.append(f"{type(exc).__name__}:{str(exc)[:180]}")
    items = normalize(raw)
    latency_ms = int((time.monotonic() - started) * 1000)
    status = "success" if items else "error" if errors else "unavailable"
    report = ProbeExecutionReport("reddit", status, started_at, latency_ms, attempted, len(raw), len(items), errors, capability.as_dict())
    return AdapterResult("reddit", status, items, report.as_dict(), errors)


def skipped_brief() -> dict:
    from models import empty_brief
    capability = preflight()
    return empty_brief("reddit", "skipped", capability.reason)
