"""JSON CLI for host integrations that do not call the Python tool adapter directly."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

if __package__:
    from .tool_adapter import run_social_marketing
else:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from scripts.social_marketing_runtime.tool_adapter import run_social_marketing


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    request = json.loads(Path(args.request).read_text(encoding="utf-8-sig"))
    result = run_social_marketing(request, request.get("session_id"))
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
