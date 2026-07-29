"""Single safe tool surface for a host agent."""
from __future__ import annotations

from typing import Any

from .llm_gateway import StructuredLLMGateway
from .orchestrator import SocialMarketingRuntime

_DEFAULT_RUNTIME = SocialMarketingRuntime()
_GATEWAY_RUNTIMES: dict[int, SocialMarketingRuntime] = {}


def run_social_marketing(request: dict[str, Any], session_id: str | None = None, gateway: StructuredLLMGateway | None = None) -> dict[str, Any]:
    """Return a HIL request, a completed Launch Pack, or an explicit block reason."""
    if gateway is None:
        runtime = _DEFAULT_RUNTIME
    else:
        runtime = _GATEWAY_RUNTIMES.setdefault(id(gateway), SocialMarketingRuntime(gateway=gateway))
    return runtime.run(request, session_id=session_id)
