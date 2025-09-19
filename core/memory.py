#!/usr/bin/env python3
"""Compatibility shim that forwards legacy ``core.memory`` calls to unified memory."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover - redis optional in local dev
    class _RedisModule:  # pylint: disable=too-few-public-methods
        """Fallback object so tests can patch ``core.memory.redis``."""

        pass

    redis = _RedisModule()  # type: ignore

from cli.config_v2 import Settings
from core.unified_memory import UnifiedMemory


class MemoryManager(UnifiedMemory):
    """Thin wrapper that keeps the legacy constructor signature."""

    def __init__(
        self,
        project_root: Optional[str] = None,
        settings: Optional[Settings] = None,
    ) -> None:
        settings = settings or Settings()
        if project_root:
            settings.project_root = project_root
        super().__init__(settings)


_memory_singleton: Optional[MemoryManager] = None


def get_memory(settings: Optional[Settings] = None) -> MemoryManager:
    """Return shared memory instance, mirroring legacy behaviour."""
    global _memory_singleton
    if settings is not None or _memory_singleton is None:
        _memory_singleton = MemoryManager(settings=settings)
    return _memory_singleton


def remember_cli(key: str, value: str, category: str = "general") -> bool:
    """CLI helper for storing memories."""
    return get_memory().remember(key, value, category)


def recall_cli(query: str, category: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
    """CLI helper for retrieving memories."""
    return get_memory().recall(query, category, limit)


def log_conversation_cli(user: str, assistant: str, model: str = "unknown") -> bool:
    """CLI helper for logging conversational exchanges."""
    return get_memory().log_conversation(user, assistant, model)


def get_context_cli(limit: int = 10) -> Dict[str, Any]:
    """CLI helper for retrieving context."""
    return get_memory().get_context(limit)


def main() -> None:
    """Minimal command-line interface retained for backwards compatibility."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python core/memory.py <remember|recall|context> ...")
        raise SystemExit(1)

    command = sys.argv[1]
    memory = get_memory()

    if command == "remember" and len(sys.argv) >= 4:
        key = sys.argv[2]
        value = sys.argv[3]
        category = sys.argv[4] if len(sys.argv) > 4 else "general"
        success = memory.remember(key, value, category)
        print("✓ Remembered" if success else "✗ Failed")
    elif command == "recall" and len(sys.argv) >= 3:
        query = sys.argv[2]
        category = sys.argv[3] if len(sys.argv) > 3 else None
        results = memory.recall(query, category)
        print(results)
    elif command == "context":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        context = memory.get_context(limit)
        print(context)
    else:
        print(f"Unknown command: {command}")
        raise SystemExit(1)


__all__ = [
    "MemoryManager",
    "get_memory",
    "remember_cli",
    "recall_cli",
    "log_conversation_cli",
    "get_context_cli",
    "redis",
    "Path",
]


if __name__ == "__main__":  # pragma: no cover - CLI passthrough
    main()
