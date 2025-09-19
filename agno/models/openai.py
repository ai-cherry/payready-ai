"""Stub OpenAI-compatible chat model."""

from __future__ import annotations


class OpenAIChat:
    """Stores configuration for compatibility with the factory code."""

    def __init__(self, id: str, api_key: str | None = None, base_url: str | None = None) -> None:
        self.id = id
        self.api_key = api_key
        self.base_url = base_url or "https://openrouter.ai/api/v1"

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"OpenAIChat(id={self.id!r})"


__all__ = ["OpenAIChat"]
