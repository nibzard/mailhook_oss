"""Redis cache service for caching and distributed locking."""

import json
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import Any

import redis.asyncio as redis_async
from redis.asyncio import Redis
from redis.asyncio.lock import Lock

from mailhookoss.config import Settings


class RedisCacheService:
    """Service for Redis caching and distributed operations."""

    def __init__(self, settings: Settings) -> None:
        """Initialize Redis cache service.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.redis_client: Redis | None = None

    async def connect(self) -> None:
        """Connect to Redis."""
        if not self.redis_client:
            self.redis_client = await redis_async.from_url(
                self.settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None

    async def get_client(self) -> Redis:
        """Get Redis client (connect if needed).

        Returns:
            Redis client instance
        """
        if not self.redis_client:
            await self.connect()
        return self.redis_client  # type: ignore[return-value]

    async def get(self, key: str) -> str | None:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        client = await self.get_client()
        return await client.get(key)

    async def get_json(self, key: str) -> dict | list | None:
        """Get JSON value from cache.

        Args:
            key: Cache key

        Returns:
            Parsed JSON value or None if not found
        """
        value = await self.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None

    async def set(
        self,
        key: str,
        value: str,
        ttl: int | None = None,
    ) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (optional)
        """
        client = await self.get_client()
        if ttl:
            await client.setex(key, ttl, value)
        else:
            await client.set(key, value)

    async def set_json(
        self,
        key: str,
        value: dict | list,
        ttl: int | None = None,
    ) -> None:
        """Set JSON value in cache.

        Args:
            key: Cache key
            value: JSON-serializable value
            ttl: Time to live in seconds (optional)
        """
        json_value = json.dumps(value)
        await self.set(key, json_value, ttl)

    async def delete(self, key: str) -> None:
        """Delete value from cache.

        Args:
            key: Cache key
        """
        client = await self.get_client()
        await client.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists
        """
        client = await self.get_client()
        return bool(await client.exists(key))

    async def expire(self, key: str, ttl: int) -> None:
        """Set expiration time for a key.

        Args:
            key: Cache key
            ttl: Time to live in seconds
        """
        client = await self.get_client()
        await client.expire(key, ttl)

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment numeric value.

        Args:
            key: Cache key
            amount: Amount to increment by

        Returns:
            New value after increment
        """
        client = await self.get_client()
        return await client.incrby(key, amount)

    async def decrement(self, key: str, amount: int = 1) -> int:
        """Decrement numeric value.

        Args:
            key: Cache key
            amount: Amount to decrement by

        Returns:
            New value after decrement
        """
        client = await self.get_client()
        return await client.decrby(key, amount)

    @asynccontextmanager
    async def lock(
        self,
        lock_name: str,
        timeout: int = 10,
        blocking: bool = True,
        blocking_timeout: int = 10,
    ) -> AsyncGenerator[Lock, None]:
        """Acquire a distributed lock.

        Args:
            lock_name: Name of the lock
            timeout: Lock timeout in seconds
            blocking: Whether to block waiting for lock
            blocking_timeout: Max time to wait for lock

        Yields:
            Lock object

        Example:
            async with cache.lock("my-lock"):
                # Critical section
                pass
        """
        client = await self.get_client()
        lock = Lock(
            client,
            lock_name,
            timeout=timeout,
            blocking=blocking,
            blocking_timeout=blocking_timeout,
        )
        async with lock:
            yield lock

    async def cache_api_key(
        self,
        api_key_secret: str,
        api_key_data: dict,
        ttl: int = 3600,
    ) -> None:
        """Cache API key data.

        Args:
            api_key_secret: API key secret (hashed)
            api_key_data: API key data to cache
            ttl: Time to live in seconds (default 1 hour)
        """
        key = f"api_key:{api_key_secret}"
        await self.set_json(key, api_key_data, ttl)

    async def get_cached_api_key(self, api_key_secret: str) -> dict | None:
        """Get cached API key data.

        Args:
            api_key_secret: API key secret (hashed)

        Returns:
            Cached API key data or None
        """
        key = f"api_key:{api_key_secret}"
        return await self.get_json(key)

    async def invalidate_api_key(self, api_key_secret: str) -> None:
        """Invalidate cached API key.

        Args:
            api_key_secret: API key secret (hashed)
        """
        key = f"api_key:{api_key_secret}"
        await self.delete(key)

    async def store_idempotency_key(
        self,
        idempotency_key: str,
        response_data: dict,
        ttl: int = 86400,
    ) -> None:
        """Store idempotency key with response data.

        Args:
            idempotency_key: Idempotency key
            response_data: Response data to store
            ttl: Time to live in seconds (default 24 hours)
        """
        key = f"idempotency:{idempotency_key}"
        await self.set_json(key, response_data, ttl)

    async def get_idempotency_response(self, idempotency_key: str) -> dict | None:
        """Get cached response for idempotency key.

        Args:
            idempotency_key: Idempotency key

        Returns:
            Cached response data or None
        """
        key = f"idempotency:{idempotency_key}"
        return await self.get_json(key)

    async def rate_limit_check(
        self,
        identifier: str,
        limit: int,
        window: int,
    ) -> tuple[bool, int]:
        """Check rate limit for identifier.

        Args:
            identifier: Rate limit identifier (e.g., tenant_id, ip_address)
            limit: Maximum requests allowed in window
            window: Time window in seconds

        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        key = f"rate_limit:{identifier}"
        client = await self.get_client()

        # Increment counter
        current = await client.incr(key)

        # Set expiration on first request
        if current == 1:
            await client.expire(key, window)

        is_allowed = current <= limit
        remaining = max(0, limit - current)

        return is_allowed, remaining

    async def cache_domain_verification(
        self,
        domain: str,
        verification_data: dict,
        ttl: int = 3600,
    ) -> None:
        """Cache domain verification data.

        Args:
            domain: Domain name
            verification_data: Verification data
            ttl: Time to live in seconds (default 1 hour)
        """
        key = f"domain_verification:{domain}"
        await self.set_json(key, verification_data, ttl)

    async def get_cached_domain_verification(self, domain: str) -> dict | None:
        """Get cached domain verification data.

        Args:
            domain: Domain name

        Returns:
            Cached verification data or None
        """
        key = f"domain_verification:{domain}"
        return await self.get_json(key)

    async def publish_event(self, channel: str, message: dict) -> None:
        """Publish event to Redis pub/sub channel.

        Args:
            channel: Channel name
            message: Event message (JSON-serializable)
        """
        client = await self.get_client()
        await client.publish(channel, json.dumps(message))

    async def get_keys_pattern(self, pattern: str) -> list[str]:
        """Get all keys matching a pattern.

        Args:
            pattern: Key pattern (Redis glob pattern)

        Returns:
            List of matching keys
        """
        client = await self.get_client()
        return await client.keys(pattern)

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern.

        Args:
            pattern: Key pattern (Redis glob pattern)

        Returns:
            Number of keys deleted
        """
        keys = await self.get_keys_pattern(pattern)
        if not keys:
            return 0

        client = await self.get_client()
        return await client.delete(*keys)

    async def get_cache_stats(self) -> dict[str, Any]:
        """Get Redis cache statistics.

        Returns:
            Dictionary with cache stats
        """
        client = await self.get_client()
        info = await client.info("stats")

        return {
            "total_connections_received": info.get("total_connections_received", 0),
            "total_commands_processed": info.get("total_commands_processed", 0),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
            "evicted_keys": info.get("evicted_keys", 0),
            "expired_keys": info.get("expired_keys", 0),
        }

    async def ping(self) -> bool:
        """Ping Redis to check connectivity.

        Returns:
            True if Redis is reachable
        """
        try:
            client = await self.get_client()
            return await client.ping()
        except Exception:
            return False
