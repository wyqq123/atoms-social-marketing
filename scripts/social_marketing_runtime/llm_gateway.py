"""Boundary for host-provided structured LLM generation."""
from __future__ import annotations

from typing import Any, Protocol


class StructuredLLMGateway(Protocol):
    def generate_json(self, *, prompt_id: str, input: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
        """Generate JSON that conforms to the supplied schema."""
