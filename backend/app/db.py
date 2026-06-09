"""Async PostgreSQL access via a shared asyncpg connection pool.

A module-level ``db`` singleton mirrors the ``cache`` pattern: the app's
lifespan connects it on startup and closes it on shutdown, and request handlers
import ``db`` directly rather than threading a pool through every call.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import asyncpg

from app.config import settings

if TYPE_CHECKING:
    from collections.abc import Sequence


class Database:
    """Thin wrapper around an asyncpg pool with lazy lifecycle."""

    def __init__(self) -> None:
        self._pool: asyncpg.Pool[asyncpg.Record] | None = None

    async def connect(self) -> None:
        """Open the connection pool. Call once on startup."""
        self._pool = await asyncpg.create_pool(
            dsn=settings.database_url,
            min_size=settings.db_pool_min_size,
            max_size=settings.db_pool_max_size,
        )

    async def close(self) -> None:
        """Close the pool (no-op if never connected)."""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    @property
    def pool(self) -> asyncpg.Pool[asyncpg.Record]:
        if self._pool is None:
            raise RuntimeError("Database pool is not initialized; call connect() first")
        return self._pool

    async def fetch(self, query: str, *args: Any) -> list[asyncpg.Record]:
        async with self.pool.acquire() as conn:
            rows: list[asyncpg.Record] = await conn.fetch(query, *args)
            return rows

    async def executemany(self, query: str, args: Sequence[Sequence[Any]]) -> None:
        async with self.pool.acquire() as conn:
            await conn.executemany(query, args)


db = Database()
