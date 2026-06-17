"""OpenStreetMap (OSM) charging-station client via the Overpass API.

A second open data source (ODbL 1.0) alongside Open Charge Map. The pure
:func:`map_osm_element` (Overpass element -> :class:`StationRow`) has no I/O and is
unit-tested; it maps OSM tags into the *same* OCM-compatible ``connectors`` JSON
shape so all downstream code (connector filter, ``connector_titles``) is unchanged.
``upsert_stations`` is shared via :mod:`app.ingest`.
"""

from __future__ import annotations

import json
import re
from typing import Any

import httpx

from app.config import settings
from app.geo import BBox
from app.ingest import StationRow, osm_station_id

# OSM socket:<type> keys -> human-readable connector titles (others humanized).
_CONNECTOR_TITLES = {
    "type2": "Type 2",
    "type2_combo": "CCS (Type 2)",
    "type2_cable": "Type 2 (cable)",
    "type1": "Type 1 (J1772)",
    "type1_combo": "CCS (Type 1)",
    "chademo": "CHAdeMO",
    "tesla_supercharger": "Tesla Supercharger",
    "tesla_destination": "Tesla Destination",
    "nacs": "NACS (Tesla)",
    "type3": "Type 3",
    "type3c": "Type 3C",
    "schuko": "Schuko",
    "cee_blue": "CEE Blue",
    "cee_red_16a": "CEE Red 16A",
    "cee_red_32a": "CEE Red 32A",
}
_SOCKET_RE = re.compile(r"^socket:([a-z0-9_]+)$")
_EMPTY_SOCKET_VALUES = {"no", "0", "false", ""}


def _as_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_power(value: Any) -> float | None:
    """Best-effort kW from values like '22 kW', '22', '7400 W'."""
    if not isinstance(value, str):
        return _as_float(value)
    match = re.search(r"[-+]?\d*\.?\d+", value)
    if not match:
        return None
    try:
        num = float(match.group())
    except ValueError:
        return None
    low = value.lower()
    if "kw" in low:
        return num
    if "w" in low:  # watts, not kW
        return num / 1000.0
    return num  # bare number assumed to be kW


def _max_power_from_tags(tags: dict[str, Any]) -> float | None:
    candidates: list[float] = []
    for key, value in tags.items():
        if key.endswith(":output") or key in ("charging_station:output", "maxpower", "output"):
            power = _parse_power(value)
            if power is not None:
                candidates.append(power)
    return max(candidates) if candidates else None


def _connectors_from_tags(tags: dict[str, Any]) -> list[dict[str, Any]]:
    """Connector list in OCM-compatible shape, from present ``socket:*`` tags."""
    titles: list[str] = []
    for key, value in tags.items():
        match = _SOCKET_RE.match(key)
        if not match:
            continue
        if isinstance(value, str) and value.strip().lower() in _EMPTY_SOCKET_VALUES:
            continue
        socket = match.group(1)
        title = _CONNECTOR_TITLES.get(socket, socket.replace("_", " ").title())
        if title not in titles:
            titles.append(title)
    return [{"ConnectionType": {"Title": t}} for t in titles]


def map_osm_element(element: dict[str, Any]) -> StationRow | None:
    """Map one Overpass element to a :class:`StationRow`, or ``None`` if unusable.

    Coordinates come from the node itself or a way/relation ``center``; elements
    without coordinates are dropped (``geom`` is NOT NULL). Location-only elements
    (no tags beyond amenity) still map to a valid, renderable row.
    """
    el_type = element.get("type")
    el_id = element.get("id")
    if el_type not in ("node", "way", "relation"):
        return None
    if not isinstance(el_id, int) or isinstance(el_id, bool):
        return None

    if el_type == "node":
        lat = _as_float(element.get("lat"))
        lng = _as_float(element.get("lon"))
    else:
        center = element.get("center") or {}
        lat = _as_float(center.get("lat"))
        lng = _as_float(center.get("lon"))
    if lat is None or lng is None:
        return None

    tags = element.get("tags") or {}
    return StationRow(
        id=osm_station_id(el_type, el_id),
        source="osm",
        name=tags.get("name") or tags.get("operator") or tags.get("brand"),
        operator=tags.get("operator") or tags.get("brand"),
        max_power_kw=_max_power_from_tags(tags),
        access_type=tags.get("access"),
        connectors_json=json.dumps(_connectors_from_tags(tags)),
        lat=lat,
        lng=lng,
    )


async def fetch_osm_elements(bbox: BBox, *, timeout: float = 8.0) -> list[dict[str, Any]]:
    """Fetch charging-station elements from Overpass for a viewport.

    Overpass bbox order is ``south,west,north,east``. Raises on transport/HTTP error.
    """
    bb = f"{bbox.south},{bbox.west},{bbox.north},{bbox.east}"
    query = (
        "[out:json][timeout:25];"
        f'(node["amenity"="charging_station"]({bb});'
        f'way["amenity"="charging_station"]({bb}););'
        "out center tags;"
    )
    # Overpass etiquette: identify the client (a missing/default UA can be rejected).
    headers = {"User-Agent": "PlugPulse/1.0 (+https://github.com/AayushCharde/PlugPulseEV)"}
    async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
        resp = await client.get(settings.osm_overpass_url, params={"data": query})
        resp.raise_for_status()
        payload = resp.json()
    elements: list[dict[str, Any]] = payload.get("elements", [])
    return elements
