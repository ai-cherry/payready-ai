"""Stub Anthropic model."""

from __future__ import annotations


class Claude:
    """Stores metadata for compatibility with the agent factory."""

    def __init__(self, id: str, api_key: str | None = None) -> None:
        self.id = id
        self.api_key = api_key

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"Claude(id={self.id!r})"


__all__ = ["Claude"]
