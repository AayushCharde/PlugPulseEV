"""Open Charge Map (OCM) client and station upsert.

The pure :func:`map_poi` (OCM POI dict -> :class:`StationRow`) has no I/O and is
unit-tested. :func:`fetch_pois` and :func:`upsert_stations` handle the network
and the database; callers degrade gracefully when either fails.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import httpx

from app.config import settings
from app.db import db
from app.geo import BBox

OCM_API_URL = "https://api.openchargemap.io/v3/poi/"

# Upsert one station; geom built from lat/lng. ST_MakePoint takes (x=lng, y=lat).
_UPSERT_SQL = """
INSERT INTO stations
    (id, name, operator, max_power_kw, access_type, connectors, geom, last_synced)
VALUES
    ($1, $2, $3, $4, $5, $6::jsonb,
     ST_SetSRID(ST_MakePoint($8, $7), 4326)::geography, now())
ON CONFLICT (id) DO UPDATE SET
    name         = EXCLUDED.name,
    operator     = EXCLUDED.operator,
    max_power_kw = EXCLUDED.max_power_kw,
    access_type  = EXCLUDED.access_type,
    connectors   = EXCLUDED.connectors,
    geom         = EXCLUDED.geom,
    last_synced  = now()
"""


@dataclass(frozen=True)
class StationRow:
    """A station ready to upsert into the ``stations`` table."""

    id: int
    name: str | None
    operator: str | None
    max_power_kw: float | None
    access_type: str | None
    connectors_json: str
    lat: float
    lng: float


def _as_float(value: Any) -> float | None:
    """Coerce a JSON value to float, or None if it isn't numeric (rejects bools)."""
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _max_power(connections: list[dict[str, Any]]) -> float | None:
    powers = [p for c in connections if (p := _as_float(c.get("PowerKW"))) is not None]
    return max(powers) if powers else None


def map_poi(poi: dict[str, Any]) -> StationRow | None:
    """Map one OCM POI to a :class:`StationRow`, or ``None`` if unusable.

    Drops POIs without an integer id or without coordinates (``geom`` is NOT NULL).
    """
    poi_id = poi.get("ID")
    if not isinstance(poi_id, int) or isinstance(poi_id, bool):
        return None

    address = poi.get("AddressInfo") or {}
    lat = _as_float(address.get("Latitude"))
    lng = _as_float(address.get("Longitude"))
    if lat is None or lng is None:
        return None

    operator_info = poi.get("OperatorInfo") or {}
    usage_type = poi.get("UsageType") or {}
    connections = poi.get("Connections") or []

    return StationRow(
        id=poi_id,
        name=address.get("Title"),
        operator=operator_info.get("Title"),
        max_power_kw=_max_power(connections),
        access_type=usage_type.get("Title"),
        connectors_json=json.dumps(connections),
        lat=lat,
        lng=lng,
    )


async def fetch_pois(bbox: BBox, *, maxresults: int, timeout: float = 4.0) -> list[dict[str, Any]]:
    """Fetch raw POIs from OCM for a viewport. Raises on transport/HTTP error.

    OCM's ``boundingbox`` is ``(topleft),(bottomright)`` = ``(north,west),(south,east)``.
    """
    params: dict[str, Any] = {
        "output": "json",
        "compact": "true",
        "verbose": "false",
        "maxresults": maxresults,
        "boundingbox": f"({bbox.north},{bbox.west}),({bbox.south},{bbox.east})",
    }
    if settings.ocm_api_key:
        params["key"] = settings.ocm_api_key

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.get(OCM_API_URL, params=params)
        resp.raise_for_status()
        data: list[dict[str, Any]] = resp.json()
        return data


async def upsert_stations(rows: list[StationRow]) -> None:
    """Upsert station rows, de-duplicated by id, into the ``stations`` table."""
    if not rows:
        return
    deduped = {r.id: r for r in rows}
    args = [
        (r.id, r.name, r.operator, r.max_power_kw, r.access_type, r.connectors_json, r.lat, r.lng)
        for r in deduped.values()
    ]
    await db.executemany(_UPSERT_SQL, args)
