"""Stateful executable pipeline for the Atoms social-marketing skill."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
from typing import Any, Callable

# The existing intake CLI uses sibling imports. Keep that CLI contract intact
# while making its state machine reusable by the runtime package.
INTAKE_DIR = Path(__file__).resolve().parents[1] / "positioning_intake"
if str(INTAKE_DIR) not in sys.path:
    sys.path.insert(0, str(INTAKE_DIR))
from scripts.positioning_intake.state_machine import answer, start

from .contracts import utc_now
from .llm_gateway import StructuredLLMGateway
from .probe_runner import run_probe
from .stage_1 import run_stage_1
from .stage_2_fit import build_platform_fit
from .stage_3_strategy import build_strategies
from .stage_4_render import build_deliverables
from .stage_5_pack import build_pack
from .validators import validate_launch_pack


class SocialMarketingRuntime:
    def __init__(
        self,
        gateway: StructuredLLMGateway | None = None,
        probe_runner: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]] | None = None,
    ) -> None:
        self.gateway = gateway
        self.probe_runner = probe_runner
        self._sessions: dict[str, dict[str, Any]] = {}

    def _candidates(self, request: dict[str, Any]) -> dict[str, Any]:
        positioning = request.get("positioning") or {}
        source = "user_prompt" if request.get("positioning_confirmed") else "unknown"
        confidence = "high" if request.get("positioning_confirmed") else "low"
        return {field: {"value": positioning.get(field), "source": source, "confidence": confidence} for field in ("promo_goal", "target_audience", "key_selling_point")}

    def _intake_response(self, session_id: str, session: dict[str, Any]) -> dict[str, Any]:
        return {"status": "needs_confirmation" if session.get("route") == "quick_confirm" else "needs_input", "session_id": session_id, "next_hil": session.get("question"), "result": None, "checks": {"blocker": [], "warning": [], "info": []}}

    def run(self, request: dict[str, Any], session_id: str | None = None) -> dict[str, Any]:
        session_id = session_id or request.get("session_id") or f"runtime-{len(self._sessions) + 1}"
        app = request.get("app_context") or {}
        if app.get("status") and app.get("status") != "completed":
            return {"status": "blocked", "session_id": session_id, "next_hil": None, "result": None, "checks": {"blocker": ["built_app_not_ready"], "warning": [], "info": []}}
        session = self._sessions.get(session_id)
        if session is None:
            session = start(self._candidates(request), session_id=session_id)
            if request.get("positioning_confirmed") and session.get("route") == "quick_confirm":
                session = answer(session, {"action": "confirm_all_candidates"})
        if request.get("intake_operation"):
            session = answer(session, request["intake_operation"])
        self._sessions[session_id] = session
        if session.get("route") != "ready":
            return self._intake_response(session_id, session)
        inputs = deepcopy(request)
        inputs["positioning"] = session["handoff"]["positioning"]
        return self._execute(inputs, session_id, session)

    def _execute(self, inputs: dict[str, Any], session_id: str, intake: dict[str, Any]) -> dict[str, Any]:
        stage_1 = run_stage_1(inputs, self.gateway)
        probe_options = inputs.get("probe_options") or {}
        enabled = probe_options.get("enable_realtime_probe", True)
        runner = self.probe_runner or run_probe
        probe_payload = runner(stage_1, inputs) if enabled else {"briefs": [], "platforms_attempted": []}
        briefs = probe_payload.get("briefs") or []
        probe_meta = {"enabled": bool(probe_options.get("enable_realtime_probe", True)), "global_timeout_ms": probe_options.get("timeout_ms", 8000), "platforms_attempted": probe_payload.get("platforms_attempted") or [], "briefs_usable_count": sum(brief.get("status") == "usable" for brief in briefs), "generated_at": utc_now()}
        platform_fit = build_platform_fit(inputs, briefs)
        strategies = build_strategies(stage_1, platform_fit, self.gateway)
        deliverables = build_deliverables(stage_1, platform_fit, strategies, self.gateway)
        pack = build_pack(inputs, stage_1, platform_fit, strategies, deliverables, probe_meta)
        errors = validate_launch_pack(pack)
        if errors:
            return {"status": "blocked", "session_id": session_id, "next_hil": None, "result": None, "checks": {"blocker": errors, "warning": [], "info": []}}
        self._sessions[session_id] = {"state": "completed", "intake": intake, "stage_1": stage_1, "result": pack}
        return {"status": "completed", "session_id": session_id, "next_hil": None, "result": pack, "checks": pack["checks"]}


def run_social_marketing(request: dict[str, Any], session_id: str | None = None, gateway: StructuredLLMGateway | None = None) -> dict[str, Any]:
    return SocialMarketingRuntime(gateway=gateway).run(request, session_id=session_id)
