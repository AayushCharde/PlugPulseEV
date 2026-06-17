"""The ``GET /stations`` endpoint: viewport query with on-demand ingest.

Per request: optionally refresh the viewport from each open source (Open Charge
Map + OpenStreetMap), each guarded by its own per-tile cache so we don't hammer
them, then serve stations from PostGIS joined with a freshness-weighted
reliability score. Reuses :func:`app.scoring.compute_reliability` so Phase 2
reports need no API change.
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Awaitable, Callable, Mapping, Sequence
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
from app.ingest import StationRow, upsert_stations
from app.ocm import fetch_pois, map_poi
from app.osm import fetch_osm_elements, map_osm_element
from app.scoring import Report, ReportStatus, compute_reliability

logger = logging.getLogger(__name__)

router = APIRouter()

# Don't trigger an ingest for absurdly large viewports — serve the DB only.
MAX_BBOX_DEG2 = 25.0

_SELECT_SQL = """
SELECT id, source, name, operator, max_power_kw, access_type, connectors,
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
    source: str
    name: str | None
    operator: str | None
    max_power_kw: float | None
    access_type: str | None
    connectors: list[str]
    lat: float
    lng: float
    reliability: ReliabilityOut


def connector_titles(connectors_raw: Any) -> list[str]:
    """Distinct connector-type titles from the connectors array.

    Accepts either a parsed list or a JSON string (asyncpg returns JSONB as text).
    Both OCM and OSM store the same ``[{"ConnectionType":{"Title": …}}]`` shape.
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


# --- on-demand ingest, one guarded sync per source ---

# Keep references to background tasks so they aren't garbage-collected mid-flight.
_background_tasks: set[asyncio.Task[None]] = set()

# A producer fetches + maps a source's raw data for a viewport into StationRows.
Producer = Callable[[BBox, int], Awaitable[list[StationRow]]]


async def _produce_ocm(box: BBox, maxresults: int) -> list[StationRow]:
    pois = await fetch_pois(box, maxresults=maxresults)
    return [row for poi in pois if (row := map_poi(poi)) is not None]


async def _produce_osm(box: BBox, maxresults: int) -> list[StationRow]:
    elements = await fetch_osm_elements(box)
    return [row for el in elements if (row := map_osm_element(el)) is not None]


async def _sync_source(
    box: BBox, maxresults: int, *, source: str, produce: Producer, ttl: int
) -> None:
    """Refresh one source for a viewport unless recently synced or too large.

    Never raises: on any network/DB error we log and serve whatever the DB has.
    """
    if box.area_deg2 > MAX_BBOX_DEG2:
        return
    key = box.tile_key(source)
    if await cache.get(key) is not None:
        return
    try:
        rows = await produce(box, maxresults)
        await upsert_stations(rows)
    except (httpx.HTTPError, asyncpg.PostgresError) as exc:
        logger.warning("%s sync failed for tile %s: %s", source, key, exc)
        return  # don't set the guard, so the next request retries
    await cache.set(key, "1", ttl)


async def _sync_ocm(box: BBox, maxresults: int) -> None:
    await _sync_source(
        box, maxresults, source="ocm", produce=_produce_ocm, ttl=settings.ocm_sync_ttl_seconds
    )


async def _sync_osm(box: BBox, maxresults: int) -> None:
    await _sync_source(
        box, maxresults, source="osm", produce=_produce_osm, ttl=settings.osm_sync_ttl_seconds
    )


def _schedule_background_sync(box: BBox, maxresults: int) -> None:
    """Fire-and-forget refresh of all sources so a warm viewport isn't blocked."""
    for coro in (_sync_ocm(box, maxresults), _sync_osm(box, maxresults)):
        task = asyncio.create_task(coro)
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
        # Warm viewport: refresh sources in the background so the response is fast.
        _schedule_background_sync(box, capped)
    else:
        # Cold/empty viewport: block on syncing all sources in parallel, then re-query.
        await asyncio.gather(_sync_ocm(box, capped), _sync_osm(box, capped))
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
            source=row["source"],
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
