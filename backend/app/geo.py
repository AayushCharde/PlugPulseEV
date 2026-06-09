"""Geographic helpers: the viewport bounding box and its parsing.

Kept in its own module so both the OCM client and the stations route can use
``BBox`` without importing each other.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BBox:
    """A geographic viewport: west/south/east/north in WGS84 degrees."""

    west: float
    south: float
    east: float
    north: float

    @property
    def area_deg2(self) -> float:
        """Rough area in square degrees — used to reject absurdly large queries."""
        return (self.east - self.west) * (self.north - self.south)

    def tile_key(self) -> str:
        """A coarse, stable cache key so panning within a tile reuses one sync."""
        return (
            f"ocm:synced:{round(self.west, 1)}:{round(self.south, 1)}:"
            f"{round(self.east, 1)}:{round(self.north, 1)}"
        )


def parse_bbox(raw: str) -> BBox:
    """Parse ``"west,south,east,north"`` into a validated :class:`BBox`.

    Raises ``ValueError`` on the wrong arity, non-numeric parts, out-of-range
    coordinates, or an inverted/degenerate box (west>=east or south>=north).
    """
    parts = raw.split(",")
    if len(parts) != 4:
        raise ValueError("bbox must have exactly 4 comma-separated values: west,south,east,north")
    try:
        west, south, east, north = (float(p) for p in parts)
    except ValueError as exc:
        raise ValueError("bbox values must be numbers") from exc

    if not (-180.0 <= west <= 180.0 and -180.0 <= east <= 180.0):
        raise ValueError("longitude (west/east) must be within [-180, 180]")
    if not (-90.0 <= south <= 90.0 and -90.0 <= north <= 90.0):
        raise ValueError("latitude (south/north) must be within [-90, 90]")
    if west >= east or south >= north:
        raise ValueError("bbox must satisfy west<east and south<north")

    return BBox(west=west, south=south, east=east, north=north)
