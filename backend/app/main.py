"""PlugPulse API — minimal skeleton.

Real routes (stations, reports, sync with Open Charge Map) land in later PRs.
This gives CI a runnable app and a health check to build on.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel

from app.config import settings

app = FastAPI(title="PlugPulse API", version="0.1.0")

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
