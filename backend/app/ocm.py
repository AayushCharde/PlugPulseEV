"""Open Charge Map (OCM) client.

The pure :func:`map_poi` (OCM POI dict -> :class:`StationRow`) has no I/O and is
unit-tested. :func:`fetch_pois` handles the network; the shared ``StationRow`` and
:func:`upsert_stations` live in :mod:`app.ingest`. Callers degrade gracefully on error.
"""

from __future__ import annotations

import json
from typing import Any

import httpx

from app.config import settings
from app.geo import BBox
from app.ingest import StationRow

OCM_API_URL = "https://api.openchargemap.io/v3/poi/"


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
        source="ocm",
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
