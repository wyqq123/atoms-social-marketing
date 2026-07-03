#!/usr/bin/env python3
"""
extract_og_metadata.py

从 Instagram post URL 抓 Open Graph 元数据(caption 前段、发布账号、图片 URL)。
用于 atoms-social-marketing skill 的 IG playbook 调研(P1.1)。

用法:
  python3 extract_og_metadata.py --input data/ig_urls_raw.txt --output data/ig_samples.json
  python3 extract_og_metadata.py --url https://www.instagram.com/p/xxx/

设计原则:
- 只抓 OG meta tags,不绕过 login wall,不违反 IG ToS
- 每请求间隔 2 秒
- 失败样本记录到 errors.txt,不阻塞整体流程
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("需要 requests + beautifulsoup4:", file=sys.stderr)
    print("  pip3 install --user requests beautifulsoup4", file=sys.stderr)
    sys.exit(1)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
REQUEST_TIMEOUT = 15
INTER_REQUEST_DELAY = 2.0


def fetch_og_metadata(url: str) -> dict:
    """抓单个 URL 的 OG meta。返回结构化 dict。失败时 raise。"""
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    og = {}
    for tag in soup.find_all("meta"):
        prop = tag.get("property") or tag.get("name")
        if not prop:
            continue
        if prop.startswith("og:") or prop.startswith("twitter:") or prop == "description":
            content = tag.get("content", "").strip()
            if content:
                og[prop] = content

    caption_raw = og.get("og:description") or og.get("description") or ""
    caption, engagement_hint = parse_ig_description(caption_raw)

    return {
        "url": url,
        "post_id": extract_post_id(url),
        "og_title": og.get("og:title", ""),
        "caption": caption,
        "engagement_hint": engagement_hint,
        "image_url": og.get("og:image", ""),
        "site_name": og.get("og:site_name", ""),
        "raw_og_description": caption_raw,
    }


def parse_ig_description(desc: str) -> tuple[str, dict]:
    """
    IG OG description 常见格式:
      "13K likes, 234 comments - username on July 3, 2024: \"caption text...\""
    尝试拆出 engagement 数字与账号名。
    """
    engagement = {}
    caption = desc

    m = re.match(
        r"^([\d.,KMkm]+)\s+likes?,\s*([\d.,KMkm]+)\s+comments?\s*-\s*(\S+)\s+on\s+([^:]+):\s*[\"']?(.*?)[\"']?$",
        desc,
        re.DOTALL,
    )
    if m:
        engagement = {
            "likes_raw": m.group(1),
            "comments_raw": m.group(2),
            "author_handle": m.group(3).strip("@"),
            "post_date_hint": m.group(4).strip(),
        }
        caption = m.group(5).strip()

    return caption, engagement


def extract_post_id(url: str) -> str:
    """IG post URL: https://www.instagram.com/p/<id>/ or /reel/<id>/"""
    m = re.search(r"/(p|reel|tv)/([^/?]+)", url)
    return m.group(2) if m else ""


def load_urls(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"input file not found: {path}")
    urls = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parsed = urlparse(line)
        if parsed.scheme in ("http", "https") and "instagram.com" in parsed.netloc:
            urls.append(line)
    return urls


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract Instagram OG metadata")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--input", type=Path, help="File with one IG URL per line")
    src.add_argument("--url", type=str, help="Single IG URL")
    parser.add_argument("--output", type=Path, default=Path("data/ig_samples.json"))
    parser.add_argument("--errors", type=Path, default=Path("data/ig_errors.txt"))
    args = parser.parse_args()

    if args.url:
        urls = [args.url]
    else:
        urls = load_urls(args.input)

    if not urls:
        print("no valid IG URLs to process", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)

    existing = []
    if args.output.exists():
        try:
            existing = json.loads(args.output.read_text())
        except json.JSONDecodeError:
            existing = []
    existing_ids = {s.get("post_id") for s in existing if s.get("post_id")}

    samples = list(existing)
    errors = []

    for i, url in enumerate(urls, 1):
        pid = extract_post_id(url)
        if pid and pid in existing_ids:
            print(f"[{i}/{len(urls)}] skip (already in output): {pid}")
            continue

        try:
            print(f"[{i}/{len(urls)}] fetching {url}")
            data = fetch_og_metadata(url)
            samples.append(data)
            existing_ids.add(data["post_id"])
        except Exception as e:
            print(f"  error: {e}", file=sys.stderr)
            errors.append(f"{url}\t{type(e).__name__}\t{e}")

        if i < len(urls):
            time.sleep(INTER_REQUEST_DELAY)

    args.output.write_text(json.dumps(samples, ensure_ascii=False, indent=2))
    print(f"\n✓ wrote {len(samples)} samples to {args.output}")

    if errors:
        args.errors.write_text("\n".join(errors))
        print(f"⚠ {len(errors)} errors logged to {args.errors}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
