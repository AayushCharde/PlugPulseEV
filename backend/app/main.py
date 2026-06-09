"""PlugPulse API.

Serves the viewport-scoped stations endpoint (with on-demand Open Charge Map
ingest) on top of the reliability scoring layer. Report writing + live scoring
land in a later phase.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel

from app.auth import router as auth_router
from app.cache import cache
from app.config import settings
from app.db import db
from app.stations import router as stations_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Open the DB pool + cache on startup; close them on shutdown."""
    await db.connect()
    await cache.connect()
    try:
        yield
    finally:
        await cache.close()
        await db.close()


app = FastAPI(title="PlugPulse API", version="0.1.0", lifespan=lifespan)

# Compress JSON responses. Station lists are repetitive and compress well,
# typically cutting transfer size by ~70-80% over the wire.
app.add_middleware(GZipMiddleware, minimum_size=500)

# Allow the browser frontend (a different origin, e.g. Vercel) to call the API.
# Opt-in via CORS_ALLOW_ORIGINS — no cross-origin access unless configured.
if settings.cors_allow_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_allow_origins),
        allow_methods=["*"],
        allow_headers=["*"],
    )


class Health(BaseModel):
    status: str
    version: str
    max_stations_per_request: int


@app.get("/health", response_model=Health)
def health() -> Health:
    return Health(
        status="ok",
        version=app.version,
        max_stations_per_request=settings.max_stations_per_request,
    )


app.include_router(stations_router)
app.include_router(auth_router)
