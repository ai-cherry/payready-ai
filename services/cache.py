"""Redis caching service for PayReady AI."""

import os
import json
import redis
from typing import Any, Optional
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

class RedisCache:
    """Redis cache for PayReady services."""

    def __init__(self):
        # Get Redis URL from environment
        redis_url = os.getenv("REDIS_URL")

        if redis_url:
            self.client = redis.from_url(redis_url, decode_responses=True)
            self.enabled = True
            logger.info("Redis cache connected")
        else:
            self.client = None
            self.enabled = False
            logger.warning("Redis not configured - caching disabled")

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.enabled:
            return None

        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL in seconds."""
        if not self.enabled:
            return False

        try:
            json_value = json.dumps(value)
            return self.client.setex(key, ttl, json_value)
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.enabled:
            return False

        try:
            return bool(self.client.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.enabled:
            return False

        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False

    def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for a key."""
        if not self.enabled:
            return False

        try:
            return bool(self.client.expire(key, ttl))
        except Exception as e:
            logger.error(f"Cache expire error: {e}")
            return False

    def get_or_compute(self, key: str, compute_fn, ttl: int = 3600) -> Any:
        """Get from cache or compute and cache."""
        # Try cache first
        value = self.get(key)
        if value is not None:
            return value

        # Compute value
        value = compute_fn()

        # Cache it
        self.set(key, value, ttl)

        return value

    def flush(self) -> bool:
        """Flush all keys (use with caution)."""
        if not self.enabled:
            return False

        try:
            return self.client.flushdb()
        except Exception as e:
            logger.error(f"Cache flush error: {e}")
            return False

# Global cache instance
cache = RedisCache()