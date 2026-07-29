"""JSON CLI protocol for the conversation clarifier host integration."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from state_machine import answer, start


def _load(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def _write(path: str, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(request: dict[str, Any]) -> dict[str, Any]:
    action = request.get("action")
    if action == "start":
        return start(request.get("candidate_extraction") or {}, request.get("suggested_options") or {}, request.get("session_id"))
    if action == "answer":
        if not isinstance(request.get("session"), dict):
            raise ValueError("answer_requires_session")
        return answer(request["session"], request.get("operation") or {})
    raise ValueError("action_must_be_start_or_answer")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    _write(args.output, run(_load(args.request)))


if __name__ == "__main__":
    main()
