"""YouTube realtime demand probe adapter using official Data API only."""
from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from models import AdapterResult, Capability, EvidenceItem, PlatformQuery, ProbeExecutionReport, safe_int, truncate_excerpt, utc_now

SEARCH_ENDPOINT = "https://www.googleapis.com/youtube/v3/search"
VIDEOS_ENDPOINT = "https://www.googleapis.com/youtube/v3/videos"
USER_AGENT = "atoms-social-marketing/0.2 (+https://atoms.local)"


def preflight(env: dict[str, str] | None = None, registry_entry: dict[str, Any] | None = None) -> Capability:
    env = env or os.environ
    if env.get("YOUTUBE_API_KEY"):
        return Capability("youtube", True, "realtime_api", "available", "ready", "medium-high")
    return Capability("youtube", False, "realtime_api", "missing", "missing_YOUTUBE_API_KEY")


def _get_json(url: str, timeout: float) -> dict[str, Any]:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _iso8601_duration_to_seconds(value: str) -> int | None:
    match = re.match(r"^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$", value or "")
    if not match:
        return None
    hours, minutes, seconds = (int(part) if part else 0 for part in match.groups())
    return hours * 3600 + minutes * 60 + seconds


def _search(query: PlatformQuery, api_key: str, timeout: float) -> list[str]:
    published_after = (datetime.now(timezone.utc) - timedelta(days=90)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    params = {
        "part": "snippet",
        "type": "video",
        "q": query.query,
        "maxResults": min(max(query.limit, 1), 8),
        "key": api_key,
        "safeSearch": "none",
        "publishedAfter": published_after,
    }
    if query.market:
        params["regionCode"] = query.market[:2].upper()
    if query.language:
        params["relevanceLanguage"] = query.language[:2].lower()
    payload = _get_json(f"{SEARCH_ENDPOINT}?{urlencode(params)}", timeout)
    ids: list[str] = []
    for item in payload.get("items", []) or []:
        video_id = ((item.get("id") or {}).get("videoId") or "").strip()
        if video_id:
            ids.append(video_id)
    return ids


def _videos(video_ids: list[str], api_key: str, timeout: float) -> list[dict[str, Any]]:
    if not video_ids:
        return []
    params = {"part": "snippet,statistics,contentDetails,status", "id": ",".join(video_ids[:50]), "key": api_key}
    payload = _get_json(f"{VIDEOS_ENDPOINT}?{urlencode(params)}", timeout)
    return payload.get("items", []) or []


def normalize(raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    counters: dict[str, int] = {}
    for record in raw:
        query = record["query"]
        video = record["video"]
        video_id = str(video.get("id") or "")
        snippet = video.get("snippet", {}) or {}
        stats = video.get("statistics", {}) or {}
        content = video.get("contentDetails", {}) or {}
        counters[query.probe_id] = counters.get(query.probe_id, 0) + 1
        evidence_id = f"youtube:{query.probe_id}:v{counters[query.probe_id]:02d}"
        item = EvidenceItem(
            evidence_id=evidence_id,
            platform="youtube",
            probe_id=query.probe_id,
            surface=query.surface or "youtube_search",
            title=snippet.get("title", ""),
            url=f"https://www.youtube.com/watch?v={video_id}",
            published_at=snippet.get("publishedAt"),
            text_excerpt=truncate_excerpt(snippet.get("description", "")),
            metrics={
                "views": safe_int(stats.get("viewCount"), None),
                "likes": safe_int(stats.get("likeCount"), None),
                "comments": safe_int(stats.get("commentCount"), None),
                "duration_seconds": _iso8601_duration_to_seconds(content.get("duration", "")),
            },
            author_or_community_context={"channel_title": snippet.get("channelTitle"), "channel_id": snippet.get("channelId")},
            source_type="official_api",
            known_biases=["youtube_search_ranking_bias", "public_video_only", "no_viewer_demographic_ground_truth"],
        )
        items.append(item.as_dict())
    return items


def fetch(queries: list[dict[str, Any]], timeout_ms: int = 2500, max_items: int = 18, env: dict[str, str] | None = None) -> AdapterResult:
    started = time.monotonic()
    started_at = utc_now()
    capability = preflight(env)
    if not capability.can_run:
        report = ProbeExecutionReport("youtube", "skipped", started_at, 0, 0, 0, capability=capability.as_dict())
        return AdapterResult("youtube", "skipped", [], report.as_dict(), [capability.reason])
    env = env or os.environ
    api_key = env["YOUTUBE_API_KEY"]
    raw: list[dict[str, Any]] = []
    errors: list[str] = []
    attempted = 0
    budget = max(timeout_ms / 1000, 0.5)
    for q in queries:
        if len(raw) >= max_items:
            break
        elapsed = time.monotonic() - started
        if elapsed >= budget:
            errors.append("youtube_timeout_budget_exhausted")
            break
        query = PlatformQuery.from_dict(q)
        attempted += 1
        try:
            per_timeout = max(0.5, min(budget - elapsed, 2.0))
            ids = _search(query, api_key, per_timeout)
            for video in _videos(ids, api_key, per_timeout):
                raw.append({"query": query, "video": video})
                if len(raw) >= max_items:
                    break
        except Exception as exc:
            errors.append(f"{type(exc).__name__}:{str(exc)[:180]}")
    items = normalize(raw)
    latency_ms = int((time.monotonic() - started) * 1000)
    status = "success" if items else "error" if errors else "unavailable"
    report = ProbeExecutionReport("youtube", status, started_at, latency_ms, attempted, len(raw), len(items), errors, capability.as_dict())
    return AdapterResult("youtube", status, items, report.as_dict(), errors)


def skipped_brief() -> dict:
    from models import empty_brief
    capability = preflight()
    return empty_brief("youtube", "skipped", capability.reason)
