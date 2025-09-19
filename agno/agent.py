"""Minimal Agent implementation for offline tests."""

from __future__ import annotations

import asyncio
from typing import Iterable, List, Optional


class Agent:
    """Simple stand-in for the real Agno Agent class."""

    def __init__(
        self,
        name: str,
        role: str,
        model: object | None = None,
        tools: Optional[Iterable] = None,
        memory_manager: object | None = None,
        instructions: Optional[List[str]] = None,
        markdown: bool = True,
        debug_mode: bool = False,
        show_tool_calls: bool = False,
    ) -> None:
        self.name = name
        self.role = role
        self.model = model
        self.tools = list(tools or [])
        self.memory_manager = memory_manager
        self.instructions = instructions or []
        self.markdown = markdown
        self.debug_mode = debug_mode
        self.show_tool_calls = show_tool_calls

    async def arun(self, prompt: str, **_: object) -> str:
        """Async execution stub that echoes the prompt."""
        await asyncio.sleep(0)  # allow context switch in tests
        return f"{self.name} processed: {prompt}"

    def run(self, prompt: str, **_: object) -> str:
        """Sync execution stub that mirrors arun."""
        return f"{self.name} processed: {prompt}"


__all__ = ["Agent"]
