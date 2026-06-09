"""The ``GET /stations`` endpoint: viewport query with on-demand OCM ingest.

Flow per request: optionally refresh the viewport from Open Charge Map (guarded
by a per-tile cache so we don't hammer OCM), then serve stations from PostGIS
joined with a freshness-weighted reliability score. Reuses
:func:`app.scoring.compute_reliability` so Phase 2 reports need no API change.
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

import asyncpg
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.cache import cache
from app.config import settings
from app.db import db
from app.geo import BBox, parse_bbox
from app.ocm import fetch_pois, map_poi, upsert_stations
from app.scoring import Report, ReportStatus, compute_reliability

logger = logging.getLogger(__name__)

router = APIRouter()

# Don't trigger an OCM ingest for absurdly large viewports — serve the DB only.
MAX_BBOX_DEG2 = 25.0

_SELECT_SQL = """
SELECT id, name, operator, max_power_kw, access_type, connectors,
       ST_Y(geom::geometry) AS lat, ST_X(geom::geometry) AS lng
FROM stations
WHERE ST_Intersects(geom, ST_MakeEnvelope($1, $2, $3, $4, 4326)::geography)
  AND ($5::text IS NULL OR connectors @> $6::jsonb)
  AND ($7::real IS NULL OR max_power_kw >= $7)
LIMIT $8
"""

_REPORTS_SQL = """
SELECT station_id, status, created_at
FROM reports
WHERE station_id = ANY($1::bigint[])
  AND created_at >= now() - make_interval(hours => $2)
"""


class ReliabilityOut(BaseModel):
    label: str
    score: float
    confidence: float


class StationOut(BaseModel):
    id: int
    name: str | None
    operator: str | None
    max_power_kw: float | None
    access_type: str | None
    connectors: list[str]
    lat: float
    lng: float
    reliability: ReliabilityOut


def connector_titles(connectors_raw: Any) -> list[str]:
    """Distinct connector-type titles from the raw OCM Connections array.

    Accepts either a parsed list or a JSON string (asyncpg returns JSONB as text).
    """
    if isinstance(connectors_raw, str):
        try:
            connectors_raw = json.loads(connectors_raw)
        except (TypeError, ValueError):
            return []
    if not isinstance(connectors_raw, list):
        return []
    titles: list[str] = []
    for conn in connectors_raw:
        if not isinstance(conn, dict):
            continue
        ctype = conn.get("ConnectionType")
        title = ctype.get("Title") if isinstance(ctype, dict) else None
        if isinstance(title, str) and title and title not in titles:
            titles.append(title)
    return titles


def assemble_reliability(
    station_ids: Sequence[int],
    report_rows: Sequence[Mapping[str, Any]],
    *,
    now: datetime | None = None,
) -> dict[int, ReliabilityOut]:
    """Group recent reports per station and compute reliability for each.

    Pure (no I/O): testable with plain dicts. Stations with no reports come back
    as ``"unknown"`` via :func:`compute_reliability`.
    """
    grouped: dict[int, list[Report]] = {sid: [] for sid in station_ids}
    for row in report_rows:
        sid = row["station_id"]
        if sid not in grouped:
            continue
        try:
            status = ReportStatus(row["status"])
        except ValueError:
            continue  # unknown status value — skip defensively
        grouped[sid].append(Report(status=status, created_at=row["created_at"]))

    result: dict[int, ReliabilityOut] = {}
    for sid, reports in grouped.items():
        rel = compute_reliability(reports, now=now)
        result[sid] = ReliabilityOut(label=rel.label, score=rel.score, confidence=rel.confidence)
    return result


# Keep references to background tasks so they aren't garbage-collected mid-flight.
_background_tasks: set[asyncio.Task[None]] = set()


async def _sync_ocm(box: BBox, maxresults: int) -> None:
    """Refresh this viewport from OCM unless recently synced or far too large.

    Never raises: on any OCM/DB error we log and serve whatever the DB has.
    """
    if box.area_deg2 > MAX_BBOX_DEG2:
        return
    key = box.tile_key()
    if await cache.get(key) is not None:
        return
    try:
        pois = await fetch_pois(box, maxresults=maxresults)
        rows = [row for poi in pois if (row := map_poi(poi)) is not None]
        await upsert_stations(rows)
    except (httpx.HTTPError, asyncpg.PostgresError) as exc:
        logger.warning("OCM sync failed for tile %s: %s", key, exc)
        return  # don't set the guard, so the next request retries
    await cache.set(key, "1", settings.ocm_sync_ttl_seconds)


def _schedule_background_sync(box: BBox, maxresults: int) -> None:
    """Fire-and-forget OCM refresh so a warm viewport isn't blocked by the network."""
    task = asyncio.create_task(_sync_ocm(box, maxresults))
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)


async def _fetch_rows(
    box: BBox, connector: str | None, min_power_kw: float | None, limit: int
) -> list[asyncpg.Record]:
    connector_filter = json.dumps([{"ConnectionType": {"Title": connector}}]) if connector else None
    return await db.fetch(
        _SELECT_SQL,
        box.west,
        box.south,
        box.east,
        box.north,
        connector,
        connector_filter,
        min_power_kw,
        limit,
    )


@router.get("/stations", response_model=list[StationOut])
async def list_stations(
    bbox: str,
    connector: str | None = None,
    min_power_kw: float | None = None,
    limit: int | None = None,
) -> list[StationOut]:
    try:
        box = parse_bbox(bbox)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    capped = min(limit or settings.max_stations_per_request, settings.max_stations_per_request)

    rows = await _fetch_rows(box, connector, min_power_kw, capped)
    if rows:
        # Warm viewport: refresh from OCM in the background so the response is fast.
        _schedule_background_sync(box, capped)
    else:
        # Cold/empty viewport: block on a sync, then re-query once.
        await _sync_ocm(box, capped)
        rows = await _fetch_rows(box, connector, min_power_kw, capped)

    station_ids = [row["id"] for row in rows]
    report_rows: list[Mapping[str, Any]] = []
    if station_ids:
        records = await db.fetch(_REPORTS_SQL, station_ids, settings.reliability_lookback_hours)
        report_rows = [
            {"station_id": r["station_id"], "status": r["status"], "created_at": r["created_at"]}
            for r in records
        ]
    reliability = assemble_reliability(station_ids, report_rows)

    return [
        StationOut(
            id=row["id"],
            name=row["name"],
            operator=row["operator"],
            max_power_kw=row["max_power_kw"],
            access_type=row["access_type"],
            connectors=connector_titles(row["connectors"]),
            lat=row["lat"],
            lng=row["lng"],
            reliability=reliability[row["id"]],
        )
        for row in rows
    ]
