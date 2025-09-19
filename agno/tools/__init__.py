"""Toolbox helpers for stub Agno implementation."""

from __future__ import annotations

from typing import Callable, List


class Toolkit:
    """Collects callable tools and exposes them to agents."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._tools: List[Callable] = []

    def register(self, tool: Callable) -> None:
        self._tools.append(tool)

    @property
    def tools(self) -> List[Callable]:  # pragma: no cover - simple accessor
        return list(self._tools)


__all__ = ["Toolkit"]
