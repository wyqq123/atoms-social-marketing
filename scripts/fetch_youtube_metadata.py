#!/usr/bin/env python3
"""
fetch_youtube_metadata.py

从 YouTube video URL 抓公开元数据。与已删除的 IG OG 抓取路线不同:
YT 公开暴露元数据接口,不会被剥离——因此这个脚本是**工作中的动态采集通路**,
不像 IG 老脚本已废弃。

两个模式:
  --mode oembed   (默认)—— 无需 API key,基础字段:title / author / thumbnail_url
  --mode api      —— 需 YOUTUBE_API_KEY 环境变量,完整字段:views / likes / comments /
                     duration / tags / categoryId / publishedAt / defaultLanguage /
                     caption(是否可用) / description

用法:
  python3 fetch_youtube_metadata.py --input references/research-data/youtube/industry_urls.txt \\
      --output references/research-data/youtube/video_samples.json

  python3 fetch_youtube_metadata.py --url https://www.youtube.com/watch?v=xxx --mode api

  # 用 API key:
  export YOUTUBE_API_KEY="AIzaSy..."
  python3 fetch_youtube_metadata.py --input references/research-data/youtube/industry_urls.txt --mode api

设计原则:
- 只调 YT 公开 API,不用 scraping、不用 login session
- 每请求间隔 0.5 秒(远宽松于 YT quota:10000 units/day)
- 失败样本记录到 errors.txt,不阻塞整体流程
- 输出去重(通过 video_id)
- API mode 支持 batch 50 支视频/请求(Data API v3 上限)

参考:
- oEmbed: https://oembed.com/
- YouTube Data API v3 videos.list: https://developers.google.com/youtube/v3/docs/videos/list
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qs, urlparse

try:
    import requests
except ImportError:
    print("需要 requests:", file=sys.stderr)
    print("  pip3 install --user requests", file=sys.stderr)
    sys.exit(1)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
REQUEST_TIMEOUT = 15
INTER_REQUEST_DELAY = 0.5
OEMBED_ENDPOINT = "https://www.youtube.com/oembed"
API_ENDPOINT = "https://www.googleapis.com/youtube/v3/videos"
API_BATCH_SIZE = 50  # Data API v3 videos.list 单次上限


def extract_video_id(url: str) -> Optional[str]:
    """
    从 YT URL 提取 video_id,兼容以下格式:
      https://www.youtube.com/watch?v=VIDEO_ID
      https://youtu.be/VIDEO_ID
      https://www.youtube.com/shorts/VIDEO_ID
      https://www.youtube.com/embed/VIDEO_ID
      https://www.youtube.com/v/VIDEO_ID
    """
    parsed = urlparse(url)
    host = parsed.netloc.lower()

    if host in ("youtu.be",):
        return parsed.path.lstrip("/").split("/")[0] or None

    if "youtube.com" not in host:
        return None

    if parsed.path == "/watch":
        v = parse_qs(parsed.query).get("v", [None])[0]
        return v

    m = re.match(r"^/(shorts|embed|v|live)/([^/?]+)", parsed.path)
    if m:
        return m.group(2)

    return None


def canonical_watch_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def fetch_oembed(url: str) -> dict:
    """无 API key,基础字段。"""
    params = {"url": url, "format": "json"}
    resp = requests.get(
        OEMBED_ENDPOINT,
        params=params,
        headers={"User-Agent": USER_AGENT},
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()
    vid = extract_video_id(url) or ""
    return {
        "video_id": vid,
        "url": canonical_watch_url(vid) if vid else url,
        "source": "oembed",
        "title": data.get("title", ""),
        "author_name": data.get("author_name", ""),
        "author_url": data.get("author_url", ""),
        "thumbnail_url": data.get("thumbnail_url", ""),
        "thumbnail_width": data.get("thumbnail_width"),
        "thumbnail_height": data.get("thumbnail_height"),
        "provider_name": data.get("provider_name", ""),
        "html_embed": data.get("html", ""),
    }


def fetch_api_batch(video_ids: list[str], api_key: str) -> list[dict]:
    """
    Data API v3 videos.list — 单次最多 50 支。
    返回结构化 list,与 oEmbed 输出对齐 + 更多字段。
    """
    params = {
        "id": ",".join(video_ids),
        "part": "snippet,statistics,contentDetails,status",
        "key": api_key,
    }
    resp = requests.get(
        API_ENDPOINT,
        params=params,
        headers={"User-Agent": USER_AGENT},
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    payload = resp.json()
    items = payload.get("items", [])

    results = []
    returned_ids = set()
    for item in items:
        vid = item.get("id", "")
        returned_ids.add(vid)
        snippet = item.get("snippet", {}) or {}
        stats = item.get("statistics", {}) or {}
        content = item.get("contentDetails", {}) or {}
        status = item.get("status", {}) or {}

        results.append({
            "video_id": vid,
            "url": canonical_watch_url(vid),
            "source": "api_v3",
            "title": snippet.get("title", ""),
            "description": snippet.get("description", ""),
            "channel_id": snippet.get("channelId", ""),
            "channel_title": snippet.get("channelTitle", ""),
            "published_at": snippet.get("publishedAt", ""),
            "tags": snippet.get("tags", []),
            "category_id": snippet.get("categoryId", ""),
            "default_language": snippet.get("defaultLanguage", ""),
            "default_audio_language": snippet.get("defaultAudioLanguage", ""),
            "thumbnail_url": (
                snippet.get("thumbnails", {}).get("maxres", {}).get("url")
                or snippet.get("thumbnails", {}).get("high", {}).get("url", "")
            ),
            "duration_iso8601": content.get("duration", ""),
            "duration_seconds": iso8601_duration_to_seconds(content.get("duration", "")),
            "definition": content.get("definition", ""),
            "caption_available": content.get("caption", "false") == "true",
            "view_count": int(stats.get("viewCount", 0)) if stats.get("viewCount") else None,
            "like_count": int(stats.get("likeCount", 0)) if stats.get("likeCount") else None,
            "comment_count": int(stats.get("commentCount", 0)) if stats.get("commentCount") else None,
            "made_for_kids": status.get("madeForKids"),
            "privacy_status": status.get("privacyStatus", ""),
            "license": status.get("license", ""),
        })

    # 记录 API 未返回的 id(可能私有 / 删除 / 未列出)
    missing = [v for v in video_ids if v not in returned_ids]
    for vid in missing:
        results.append({
            "video_id": vid,
            "url": canonical_watch_url(vid),
            "source": "api_v3",
            "error": "not_returned_by_api",
            "note": "video 可能私有、被删除、区域限制或 id 无效",
        })

    return results


def iso8601_duration_to_seconds(iso: str) -> Optional[int]:
    """PT#H#M#S → 秒。"""
    if not iso:
        return None
    m = re.match(r"^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$", iso)
    if not m:
        return None
    h, mm, s = (int(x) if x else 0 for x in m.groups())
    return h * 3600 + mm * 60 + s


def load_urls(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"input file not found: {path}")
    urls = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parsed = urlparse(line)
        if parsed.scheme not in ("http", "https"):
            continue
        if "youtube.com" not in parsed.netloc and "youtu.be" not in parsed.netloc:
            continue
        urls.append(line)
    return urls


def load_existing(path: Path) -> tuple[list, set]:
    if not path.exists():
        return [], set()
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return [], set()
    ids = {s.get("video_id") for s in data if s.get("video_id")}
    return data, ids


def run_oembed(urls: list[str], existing: list, existing_ids: set, errors: list) -> list:
    samples = list(existing)
    for i, url in enumerate(urls, 1):
        vid = extract_video_id(url)
        if not vid:
            errors.append(f"{url}\tinvalid_url\tno video_id extracted")
            continue
        if vid in existing_ids:
            print(f"[{i}/{len(urls)}] skip (already in output): {vid}")
            continue
        try:
            print(f"[{i}/{len(urls)}] oembed: {vid}")
            data = fetch_oembed(url)
            samples.append(data)
            existing_ids.add(vid)
        except Exception as e:
            print(f"  error: {e}", file=sys.stderr)
            errors.append(f"{url}\t{type(e).__name__}\t{e}")
        if i < len(urls):
            time.sleep(INTER_REQUEST_DELAY)
    return samples


def run_api(urls: list[str], api_key: str, existing: list, existing_ids: set, errors: list) -> list:
    samples = list(existing)
    ids_to_fetch = []
    for url in urls:
        vid = extract_video_id(url)
        if not vid:
            errors.append(f"{url}\tinvalid_url\tno video_id extracted")
            continue
        if vid in existing_ids:
            continue
        ids_to_fetch.append(vid)

    print(f"[api] {len(ids_to_fetch)} new video_ids to fetch ({len(urls) - len(ids_to_fetch)} already cached)")

    for batch_start in range(0, len(ids_to_fetch), API_BATCH_SIZE):
        batch = ids_to_fetch[batch_start:batch_start + API_BATCH_SIZE]
        print(f"[api] batch {batch_start // API_BATCH_SIZE + 1}: {len(batch)} ids")
        try:
            results = fetch_api_batch(batch, api_key)
            samples.extend(results)
            for r in results:
                existing_ids.add(r.get("video_id"))
        except requests.HTTPError as e:
            body = ""
            try:
                body = e.response.text[:500]
            except Exception:
                pass
            print(f"  http error: {e}\n  body: {body}", file=sys.stderr)
            errors.append(f"batch_{batch_start}\tHTTPError\t{e} {body}")
        except Exception as e:
            print(f"  error: {e}", file=sys.stderr)
            errors.append(f"batch_{batch_start}\t{type(e).__name__}\t{e}")
        time.sleep(INTER_REQUEST_DELAY)

    return samples


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch YouTube video metadata (oEmbed or Data API v3)")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--input", type=Path, help="File with one YT video URL per line")
    src.add_argument("--url", type=str, help="Single YT video URL")
    parser.add_argument(
        "--mode",
        choices=["oembed", "api"],
        default="oembed",
        help="oembed (default, no key) | api (requires YOUTUBE_API_KEY env var)",
    )
    parser.add_argument("--output", type=Path, default=Path("references/research-data/youtube/video_samples.json"))
    parser.add_argument("--errors", type=Path, default=Path("references/research-data/youtube/errors.txt"))
    args = parser.parse_args()

    if args.url:
        urls = [args.url]
    else:
        urls = load_urls(args.input)

    if not urls:
        print("no valid YouTube URLs to process", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    existing, existing_ids = load_existing(args.output)
    errors: list[str] = []

    if args.mode == "api":
        api_key = os.environ.get("YOUTUBE_API_KEY", "").strip()
        if not api_key:
            print("YOUTUBE_API_KEY env var required for --mode api", file=sys.stderr)
            print("Get one at https://console.cloud.google.com/ (enable YouTube Data API v3)", file=sys.stderr)
            return 2
        samples = run_api(urls, api_key, existing, existing_ids, errors)
    else:
        samples = run_oembed(urls, existing, existing_ids, errors)

    args.output.write_text(json.dumps(samples, ensure_ascii=False, indent=2))
    print(f"\n✓ wrote {len(samples)} samples to {args.output}")

    if errors:
        args.errors.write_text("\n".join(errors))
        print(f"⚠ {len(errors)} errors logged to {args.errors}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
