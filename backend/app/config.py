"""Runtime settings, read from the environment.

Kept dependency-free (plain dataclass) so importing it is essentially free
and never blocks startup.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


def _int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    return int(raw) if raw else default


@dataclass(frozen=True)
class Settings:
    database_url: str = os.environ.get(
        "DATABASE_URL", "postgresql://plugpulse:plugpulse@localhost:5432/plugpulse"
    )
    redis_url: str | None = os.environ.get("REDIS_URL") or None
    ocm_api_key: str | None = os.environ.get("OCM_API_KEY") or None

    # --- performance knobs (tune without code changes) ---
    # Hard cap on stations returned per request — never ship the whole planet.
    max_stations_per_request: int = _int("MAX_STATIONS_PER_REQUEST", 300)
    # How long a computed reliability score stays warm in cache.
    reliability_cache_ttl_seconds: int = _int("RELIABILITY_CACHE_TTL", 60)
    # Connection pool sizing for the database.
    db_pool_min_size: int = _int("DB_POOL_MIN_SIZE", 2)
    db_pool_max_size: int = _int("DB_POOL_MAX_SIZE", 10)
    # Only score reports newer than this (older ones decay to ~0 anyway).
    reliability_lookback_hours: int = _int("RELIABILITY_LOOKBACK_HOURS", 24)


settings = Settings()
