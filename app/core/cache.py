"""Redis cache configuration and utilities"""

import json
from typing import Optional, Any
import redis.asyncio as redis
from app.core.config import settings


class CacheManager:
    """Redis cache manager for application-wide caching"""

    def __init__(self):
        self.redis: Optional[redis.Redis] = None

    async def connect(self):
        """Connect to Redis"""
        self.redis = await redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis:
            return None

        value = await self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = settings.CACHE_TTL_SECONDS
    ) -> bool:
        """Set value in cache with optional TTL"""
        if not self.redis:
            return False

        try:
            serialized = json.dumps(value) if not isinstance(value, str) else value
            await self.redis.setex(key, ttl, serialized)
            return True
        except Exception:
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.redis:
            return False

        await self.redis.delete(key)
        return True

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.redis:
            return False

        return await self.redis.exists(key) > 0

    async def flush_pattern(self, pattern: str):
        """Delete all keys matching a pattern"""
        if not self.redis:
            return

        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(cursor, match=pattern)
            if keys:
                await self.redis.delete(*keys)
            if cursor == 0:
                break


# Global cache instance
cache = CacheManager()
