"""PlugPulse API — minimal skeleton.

Real routes (stations, reports, sync with Open Charge Map) land in later PRs.
This gives CI a runnable app and a health check to build on.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel

from app.config import settings

app = FastAPI(title="PlugPulse API", version="0.1.0")

# Compress JSON responses. Station lists are repetitive and compress well,
# typically cutting transfer size by ~70-80% over the wire.
app.add_middleware(GZipMiddleware, minimum_size=500)


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
