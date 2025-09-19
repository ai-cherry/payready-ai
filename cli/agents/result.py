"""Shared result dataclass for agent adapters."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass(slots=True)
class AgentResult:
    """Normalized agent response metadata returned to the CLI."""

    output: str
    metadata: Dict[str, Any]
    run_dir: Path


__all__ = ["AgentResult"]
