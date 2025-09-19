"""Agent adapter exports for the unified CLI."""

from __future__ import annotations

from .agno import run as run_agno
from .claude import run as run_claude
from .codex import run as run_codex
from .result import AgentResult

__all__ = [
    "AgentResult",
    "run_agno",
    "run_claude",
    "run_codex",
]
