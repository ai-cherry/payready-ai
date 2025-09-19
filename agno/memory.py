"""Simplified memory primitives compatible with the upstream interface."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional


@dataclass
class UserMemory:
    """Lightweight record used by the stub memory manager."""

    content: str
    metadata: Dict[str, str]
    score: float = 0.0


class MemoryManager:
    """In-memory storage used by the local test harness."""

    def __init__(self) -> None:
        self._store: List[UserMemory] = []

    def add(self, messages: Iterable[Dict[str, object]]) -> None:
        for message in messages:
            content = str(message.get("content", ""))
            metadata = dict(message.get("metadata", {}) or {})
            self._store.append(UserMemory(content=content, metadata=metadata, score=1.0))

    def search(self, query: str, limit: int = 5) -> List[Dict[str, object]]:
        query_lower = query.lower()
        results: List[Dict[str, object]] = []
        for memory in self._store:
            if query_lower in memory.content.lower() or not query_lower:
                results.append(
                    {
                        "content": memory.content,
                        "metadata": memory.metadata,
                        "score": memory.score,
                    }
                )
            if len(results) >= limit:
                break
        return results


__all__ = ["MemoryManager", "UserMemory"]
