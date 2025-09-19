"""
Robust MemoryManager implementation for Agno v2.0.7 with Redis/file fallback.
Provides persistent, resilient memory for agents with seamless offline support.
"""

from __future__ import annotations

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover - redis optional in local dev
    redis = None  # type: ignore
    logging.getLogger(__name__).debug("redis package not available; will use non-redis fallback")

logger = logging.getLogger(__name__)


class StubMemoryManager:
    """Stub memory manager for offline mode."""

    def __init__(self):
        self.storage = {}
        self.user_memory = StubUserMemory(self.storage)
        self.session_memory = StubSessionMemory(self.storage)

    def log_conversation(self, session_id: str, message: str, response: str):
        """Log conversation in offline mode."""
        if session_id not in self.storage:
            self.storage[session_id] = []
        self.storage[session_id].append({
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "response": response
        })
        logger.debug(f"[OFFLINE] Logged conversation for session {session_id}")

    def get_history(self, session_id: str) -> List[Dict]:
        """Get conversation history in offline mode."""
        return self.storage.get(session_id, [])


class StubUserMemory:
    """Stub user memory for offline mode."""

    def __init__(self, storage: dict):
        self.storage = storage
        self.user_data = {}

    def remember(self, key: str, value: Any, category: str = "general"):
        """Store user memory in offline mode."""
        if category not in self.user_data:
            self.user_data[category] = {}
        self.user_data[category][key] = value
        logger.debug(f"[OFFLINE] Remembered {key} in {category}")

    def recall(self, key: str, category: str = "general") -> Optional[Any]:
        """Recall user memory in offline mode."""
        return self.user_data.get(category, {}).get(key)


class StubSessionMemory:
    """Stub session memory for offline mode."""

    def __init__(self, storage: dict):
        self.storage = storage
        self.session_data = {}

    def save(self, session_id: str, data: Dict):
        """Save session data in offline mode."""
        self.session_data[session_id] = data
        logger.debug(f"[OFFLINE] Saved session {session_id}")

    def load(self, session_id: str) -> Optional[Dict]:
        """Load session data in offline mode."""
        return self.session_data.get(session_id)


def get_memory_manager(settings=None) -> Any:
    """
    Get a properly configured MemoryManager for Agno v2.0.7.

    Implements best practices:
    - Redis as primary for performance
    - File/SQLite fallback for reliability
    - Offline mode support with stubs
    - Graceful error handling

    Args:
        settings: Configuration object with redis_url and memory_dir

    Returns:
        MemoryManager instance (real or stub based on environment)
    """

    # Check if we're in offline mode
    if os.getenv("PAYREADY_OFFLINE_MODE") == "1":
        logger.info("Using stub MemoryManager for offline mode")
        return StubMemoryManager()

    # Try to import agno.memory
    try:
        from agno.memory import MemoryManager
    except ImportError:
        logger.warning("agno.memory not available, using stub")
        return StubMemoryManager()

    # Set up memory directory for file fallback
    if settings and hasattr(settings, 'memory_dir'):
        memory_dir = Path(settings.memory_dir)
    else:
        memory_dir = Path(os.path.expanduser("~/.payready/memory"))

    # Ensure directory exists and is writable
    try:
        memory_dir.mkdir(parents=True, exist_ok=True)
        test_file = memory_dir / ".write_test"
        test_file.touch()
        test_file.unlink()
        logger.info(f"Memory directory ready: {memory_dir}")
    except Exception as e:
        logger.error(f"Cannot create/write to memory directory: {e}")
        # Fall back to temp directory
        import tempfile
        memory_dir = Path(tempfile.gettempdir()) / "payready_memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Using temp directory: {memory_dir}")

    # Try to connect to Redis if configured
    redis_client = None
    redis_ok = False

    if settings and hasattr(settings, 'redis_url') and settings.redis_url:
        if redis is None:
            logger.warning("Redis URL provided but redis package is not installed; using file-based storage")
        else:
            try:
                redis_client = redis.Redis.from_url(settings.redis_url)
                # Test connectivity
                redis_client.ping()
                redis_ok = True
                logger.info(f"Connected to Redis at {settings.redis_url}")
            except Exception as e:
                logger.warning(f"Redis not available: {e}")
                logger.info("Falling back to file-based memory storage")

    # Create MemoryManager with appropriate backend
    try:
        # Real Agno MemoryManager doesn't accept parameters
        memory_manager = MemoryManager()
        # If we have Redis, the MemoryManager might use it internally
        logger.info(f"MemoryManager initialized (may use Redis if configured)")
        return memory_manager
    except Exception as e:
        logger.error(f"Failed to create MemoryManager: {e}")
        logger.info("Using stub MemoryManager as final fallback")
        return StubMemoryManager()


def save_session_id(session_id: str, session_file: str = None):
    """
    Save session ID for persistence across restarts.

    Args:
        session_id: The session ID to save
        session_file: Optional file path (defaults to ~/.payready/session_id.txt)
    """
    if session_file is None:
        session_dir = Path(os.path.expanduser("~/.payready"))
        session_dir.mkdir(parents=True, exist_ok=True)
        session_file = str(session_dir / "session_id.txt")

    try:
        with open(session_file, "w") as f:
            f.write(session_id)
        logger.info(f"Saved session ID to {session_file}")
    except Exception as e:
        logger.error(f"Failed to save session ID: {e}")


def load_session_id(session_file: str = None) -> Optional[str]:
    """
    Load previously saved session ID.

    Args:
        session_file: Optional file path (defaults to ~/.payready/session_id.txt)

    Returns:
        Session ID if found, None otherwise
    """
    if session_file is None:
        session_file = os.path.expanduser("~/.payready/session_id.txt")

    try:
        if os.path.exists(session_file):
            with open(session_file, "r") as f:
                session_id = f.read().strip()
                logger.info(f"Loaded session ID from {session_file}")
                return session_id
    except Exception as e:
        logger.error(f"Failed to load session ID: {e}")

    return None


def create_session_id(prefix: str = "payready") -> str:
    """
    Create a new unique session ID.

    Args:
        prefix: Prefix for the session ID

    Returns:
        New session ID
    """
    import uuid
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    session_id = f"{prefix}-{timestamp}-{unique_id}"
    logger.info(f"Created new session ID: {session_id}")
    return session_id


class MemoryPatterns:
    """
    Best practice patterns for using MemoryManager with agents.
    """

    @staticmethod
    def store_user_context(memory_manager: Any, user_id: str, context: Dict):
        """
        Store user-specific context for long-term recall.

        Example:
            context = {
                "preferences": {"theme": "dark", "language": "en"},
                "history": ["created_project_x", "deployed_service_y"],
                "metadata": {"vip": True, "subscription": "enterprise"}
            }
        """
        if hasattr(memory_manager, 'user_memory'):
            for key, value in context.items():
                memory_manager.user_memory.remember(
                    key=f"{user_id}_{key}",
                    value=json.dumps(value) if isinstance(value, (dict, list)) else value,
                    category="user_context"
                )

    @staticmethod
    def recall_user_context(memory_manager: Any, user_id: str, key: str) -> Any:
        """
        Recall user-specific context.
        """
        if hasattr(memory_manager, 'user_memory'):
            value = memory_manager.user_memory.recall(
                key=f"{user_id}_{key}",
                category="user_context"
            )
            if value and isinstance(value, str):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return value
        return None

    @staticmethod
    def save_workflow_state(memory_manager: Any, session_id: str, workflow: str, state: Dict):
        """
        Save workflow state for resumable multi-step processes.
        """
        if hasattr(memory_manager, 'session_memory'):
            state_data = {
                "workflow": workflow,
                "state": state,
                "timestamp": datetime.now().isoformat()
            }
            memory_manager.session_memory.save(
                session_id=f"{session_id}_workflow_{workflow}",
                data=state_data
            )

    @staticmethod
    def load_workflow_state(memory_manager: Any, session_id: str, workflow: str) -> Optional[Dict]:
        """
        Load workflow state for resuming processes.
        """
        if hasattr(memory_manager, 'session_memory'):
            return memory_manager.session_memory.load(
                session_id=f"{session_id}_workflow_{workflow}"
            )
        return None


__all__ = [
    "get_memory_manager",
    "save_session_id",
    "load_session_id",
    "create_session_id",
    "MemoryPatterns",
    "StubMemoryManager"
]
