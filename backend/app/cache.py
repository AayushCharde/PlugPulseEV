"""Thin async cache wrapper.

Caching is a performance optimization, not a correctness requirement: if Redis
isn't configured the methods become no-ops and the app still works (just hits the
database more). This keeps local dev simple while letting production stay fast.
"""

from __future__ import annotations

from typing import Any

from app.config import settings


class Cache:
    def __init__(self) -> None:
        self._client: Any | None = None

    async def connect(self) -> None:
        if not settings.redis_url:
            return
        import redis.asyncio as redis  # lazy import; only needed when configured

        # redis-py's from_url isn't fully typed; ignore the strict untyped-call check.
        self._client = redis.from_url(  # type: ignore[no-untyped-call]
            settings.redis_url, decode_responses=True
        )

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def get(self, key: str) -> str | None:
        if self._client is None:
            return None
        result: str | None = await self._client.get(key)
        return result

    async def set(self, key: str, value: str, ttl_seconds: int) -> None:
        if self._client is None:
            return
        await self._client.set(key, value, ex=ttl_seconds)


cache = Cache()
