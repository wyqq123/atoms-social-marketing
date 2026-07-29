"""Bridge the full runtime to the existing Stage 2b probe CLI."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PROBE_SCRIPT = ROOT / "scripts" / "realtime_probe" / "run_realtime_probe.py"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def run_probe(stage_1: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    """Execute Stage 2b without exposing credentials or shell syntax to the caller."""
    options = inputs.get("probe_options") or {}
    with tempfile.TemporaryDirectory(prefix="atoms-social-probe-") as directory:
        work = Path(directory)
        app_icp = work / "app_icp.json"
        demand_probes = work / "demand_probes.json"
        output = work / "briefs.json"
        _write(app_icp, stage_1["app_icp_vector"])
        _write(demand_probes, stage_1["demand_probe_pack"])
        command = [
            sys.executable, str(PROBE_SCRIPT), "--app-icp", str(app_icp),
            "--demand-probes", str(demand_probes), "--platform-registry", str(ROOT / "data" / "platform_registry.json"),
            "--timeout-ms", str(options.get("timeout_ms", 8000)),
            "--queries-per-platform", str(options.get("queries_per_platform", 3)),
            "--fresh-cache-max-age-hours", str(options.get("fresh_cache_max_age_hours", 24)),
            "--output", str(output),
        ]
        scope = inputs.get("platform_scope") or []
        if scope:
            command.extend(["--platform-scope", *scope])
        if options.get("no_network"):
            command.append("--no-network")
        try:
            subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True, timeout=max(2, int(options.get("timeout_ms", 8000)) // 1000 + 3))
            return json.loads(output.read_text(encoding="utf-8"))
        except (subprocess.SubprocessError, OSError, json.JSONDecodeError) as exc:
            return {"briefs": [], "platforms_attempted": [], "execution_reports": [{"platform": "runtime", "status": "unavailable", "errors": [type(exc).__name__]}]}
