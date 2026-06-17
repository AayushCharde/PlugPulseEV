"""Shared station ingest: the source-neutral ``StationRow`` and the UPSERT.

Both the Open Charge Map (:mod:`app.ocm`) and OpenStreetMap (:mod:`app.osm`)
adapters produce ``StationRow`` objects and persist them via
:func:`upsert_stations`. Each row carries a ``source`` so we know its provenance,
and OSM ids are namespaced (see :func:`osm_station_id`) into a BIGINT range that
can't collide with OCM's small ids — so both sources share one ``stations`` table
keyed on ``id`` without touching the ``reports`` foreign key.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.db import db

# Disjoint BIGINT ranges so OSM ids never collide with OCM (small) ids or each
# other. OCM ids are < ~1e9; these offsets (7–9 x 10^15) are far below the
# BIGINT max (9.22 x 10^18), leaving room for OSM ids (currently ~1e10).
_OSM_ID_OFFSETS = {
    "node": 7_000_000_000_000_000,
    "way": 8_000_000_000_000_000,
    "relation": 9_000_000_000_000_000,
}


def osm_station_id(element_type: str, element_id: int) -> int:
    """Namespace an OSM element into the shared ``stations.id`` space."""
    offset = _OSM_ID_OFFSETS.get(element_type)
    if offset is None:
        raise ValueError(f"unsupported OSM element type: {element_type!r}")
    return offset + element_id


@dataclass(frozen=True)
class StationRow:
    """A station ready to upsert into the ``stations`` table."""

    id: int
    source: str  # "ocm" | "osm"
    name: str | None
    operator: str | None
    max_power_kw: float | None
    access_type: str | None
    connectors_json: str
    lat: float
    lng: float


# geom is built from lat/lng; ST_MakePoint takes (x=lng, y=lat).
_UPSERT_SQL = """
INSERT INTO stations
    (id, source, name, operator, max_power_kw, access_type, connectors, geom, last_synced)
VALUES
    ($1, $2, $3, $4, $5, $6, $7::jsonb,
     ST_SetSRID(ST_MakePoint($9, $8), 4326)::geography, now())
ON CONFLICT (id) DO UPDATE SET
    source       = EXCLUDED.source,
    name         = EXCLUDED.name,
    operator     = EXCLUDED.operator,
    max_power_kw = EXCLUDED.max_power_kw,
    access_type  = EXCLUDED.access_type,
    connectors   = EXCLUDED.connectors,
    geom         = EXCLUDED.geom,
    last_synced  = now()
"""


async def upsert_stations(rows: list[StationRow]) -> None:
    """Upsert station rows, de-duplicated by id, into the ``stations`` table."""
    if not rows:
        return
    deduped = {r.id: r for r in rows}
    args: list[tuple[Any, ...]] = [
        (
            r.id,
            r.source,
            r.name,
            r.operator,
            r.max_power_kw,
            r.access_type,
            r.connectors_json,
            r.lat,
            r.lng,
        )
        for r in deduped.values()
    ]
    await db.executemany(_UPSERT_SQL, args)
