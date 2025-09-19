# Logging replaced print() calls — see ARCHITECTURE_AUDIT_REPORT.md
"""Unified memory system with Agno v2.0.7 integration and fallback chain."""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import redis

import logging
logger = logging.getLogger(__name__)

from agno.memory import MemoryManager, UserMemory

from cli.config_v2 import Settings, get_settings


class UnifiedMemory:
    """
    Unified memory system with multiple backends:
    1. Agno MemoryManager (primary)
    2. Redis (cache layer)
    3. File storage (fallback)
    """

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize with fallback chain."""
        self.settings = settings or get_settings()
        self.storage_type = "none"

        # Initialize Agno memory
        self.agno_memory = None
        if self.settings.use_memory:
            try:
                self.agno_memory = MemoryManager()
                self.storage_type = "agno"
            except Exception as e:
                # Optional backend failure - non-fatal; log for observability
                logger.warning("Agno memory initialization failed: %s", e)

        # Initialize Redis if available
        self.redis_client = None
        if self.settings.redis_url:
            try:
                self.redis_client = redis.from_url(self.settings.redis_url)
                self.redis_client.ping()
                if self.storage_type == "none":
                    self.storage_type = "redis"
            except Exception as e:
                # Redis is optional; log details for diagnostics
                logger.warning("Redis connection failed: %s", e)
                self.redis_client = None

        # File storage fallback (respect configured memory_dir)
        project_root = Path(self.settings.project_root).expanduser().resolve()
        configured_dir = Path(self.settings.memory_dir)
        if not configured_dir.is_absolute():
            configured_dir = project_root / configured_dir

        self.memory_dir = configured_dir
        try:
            self.memory_dir.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            fallback_dir = project_root / ".payready-memory"
            fallback_dir.mkdir(parents=True, exist_ok=True)
            # Log as warning — fallback to alternate directory
            logger.warning(
                "Memory dir '%s' not writable (%s); using '%s' instead.",
                self.memory_dir,
                exc,
                fallback_dir,
            )
            self.memory_dir = fallback_dir

        self.memory_file = self.memory_dir / "unified_memory.jsonl"
        self.conversation_file = self.memory_dir / "conversations.jsonl"

        if self.storage_type == "none":
            self.storage_type = "file"

        logger.info("UnifiedMemory initialized with %s backend", self.storage_type)

    def remember(
        self,
        key: str,
        value: Any,
        category: str = "general",
        metadata: Optional[Dict] = None
    ) -> bool:
        """Store information across all available backends."""
        success = False
        timestamp = datetime.now().isoformat()

        # Prepare data
        data = {
            "key": key,
            "value": value,
            "category": category,
            "metadata": metadata or {},
            "timestamp": timestamp
        }

        # Try Agno memory
        if self.agno_memory:
            try:
                # Agno uses add() method
                self.agno_memory.add(
                    messages=[{"content": str(value), "metadata": {"key": key, "category": category}}]
                )
                success = True
            except Exception as e:
                # Non-fatal storage failure for optional backend
                logger.warning("Agno memory store failed: %s", e)

        # Try Redis
        if self.redis_client:
            try:
                redis_key = f"memory:{category}:{key}"
                self.redis_client.setex(
                    redis_key,
                    3600,  # 1 hour TTL
                    json.dumps(data)
                )
                success = True
            except Exception as e:
                logger.warning("Redis store failed: %s", e)

        # Always store to file (backup)
        try:
            with self.memory_file.open("a", encoding="utf-8") as f:
                f.write(json.dumps(data) + "\n")
            success = True
        except Exception as e:
            # File persistence is a critical backup; surface as error
            logger.error("File store failed: %s", e)

        return success

    def recall(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search memory across all backends."""
        results = []

        # Try Agno memory
        if self.agno_memory:
            try:
                agno_results = self.agno_memory.search(
                    query=query,
                    limit=limit
                )
                for r in agno_results:
                    results.append({
                        "source": "agno",
                        "content": r.get("content", ""),
                        "metadata": r.get("metadata", {}),
                        "score": r.get("score", 0)
                    })
            except Exception as e:
                logger.warning("Agno search failed: %s", e)

        # Try Redis
        if self.redis_client and len(results) < limit:
            try:
                pattern = f"memory:{category or '*'}:*{query}*"
                keys = self.redis_client.keys(pattern)[:limit]
                for key in keys:
                    data = self.redis_client.get(key)
                    if data:
                        results.append({
                            "source": "redis",
                            **json.loads(data)
                        })
            except Exception as e:
                logger.warning("Redis search failed: %s", e)

        # Search file if needed
        if len(results) < limit and self.memory_file.exists():
            try:
                with open(self.memory_file) as f:
                    for line in f:
                        entry = json.loads(line)
                        if query.lower() in str(entry).lower():
                            if not category or entry.get("category") == category:
                                results.append({
                                    "source": "file",
                                    **entry
                                })
                                if len(results) >= limit:
                                    break
            except Exception as e:
                logger.warning("File search failed: %s", e)

        return results[:limit]

    def log_conversation(
        self,
        user_input: str,
        ai_response: str,
        model: str = "unknown",
        metadata: Optional[Dict] = None
    ) -> bool:
        """Log a conversation exchange."""
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "assistant": ai_response,
            "model": model,
            "metadata": metadata or {}
        }

        # Store as memory
        key = f"conversation_{int(time.time() * 1000)}"
        self.remember(key, conversation, "conversation", metadata)

        # Also append to conversation file
        try:
            with self.conversation_file.open("a", encoding="utf-8") as f:
                f.write(json.dumps(conversation) + "\n")
            return True
        except Exception as e:
            logger.error("Conversation logging failed: %s", e)
            return False

    def get_context(self, limit: int = 10) -> Dict[str, Any]:
        """Get current context from memory."""
        recent_conversations = self.recall("", "conversation", limit)

        context = {
            "timestamp": datetime.now().isoformat(),
            "storage_type": self.storage_type,
            "conversations": recent_conversations,
            "stats": {
                "total_memories": self._count_memories(),
                "backend": self.storage_type
            }
        }

        return context

    def _count_memories(self) -> int:
        """Count total memories stored."""
        count = 0

        if self.memory_file.exists():
            try:
                with open(self.memory_file) as f:
                    count = sum(1 for _ in f)
            except:
                pass

        return count

    def clear_category(self, category: str) -> bool:
        """Clear all memories in a category."""
        success = False

        # Clear from Redis
        if self.redis_client:
            try:
                pattern = f"memory:{category}:*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
                success = True
            except Exception as e:
                logger.warning("Redis clear failed: %s", e)

        # Note: File clearing would require rewriting the entire file
        # which we skip for now to preserve backup

        return success


# Singleton instance
_memory_instance = None


def get_memory(settings: Optional[Settings] = None) -> UnifiedMemory:
    """Get or create memory singleton."""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = UnifiedMemory(settings)
    return _memory_instance


# CLI interface functions
def remember_cli(key: str, value: str, category: str = "general") -> bool:
    """CLI interface for remembering."""
    memory = get_memory()
    return memory.remember(key, value, category)


def recall_cli(query: str, category: Optional[str] = None, limit: int = 5) -> List[Dict]:
    """CLI interface for recalling."""
    memory = get_memory()
    return memory.recall(query, category, limit)


def log_conversation_cli(user: str, assistant: str, model: str = "unknown") -> bool:
    """CLI interface for logging conversations."""
    memory = get_memory()
    return memory.log_conversation(user, assistant, model)


def get_context_cli() -> Dict[str, Any]:
    """CLI interface for getting context."""
    memory = get_memory()
    return memory.get_context()


__all__ = [
    "UnifiedMemory",
    "get_memory",
    "remember_cli",
    "recall_cli",
    "log_conversation_cli",
    "get_context_cli",
]
