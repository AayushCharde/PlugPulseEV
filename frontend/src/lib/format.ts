/**
 * Pure presentation helpers for the station detail view. No DOM — unit-tested.
 */

import type { Station } from "$lib/stations";

/** Human label for a data source code. */
export function sourceLabel(source: string): string {
  if (source === "osm") return "© OpenStreetMap";
  if (source === "ocm") return "Open Charge Map";
  return source;
}

/** "22 kW" or a fallback when power is unknown. */
export function formatPower(kw: number | null): string {
  if (kw == null || !Number.isFinite(kw) || kw <= 0) return "Unknown";
  // Trim trailing .0 (e.g. 22.0 -> "22", 3.7 -> "3.7").
  const rounded = Math.round(kw * 10) / 10;
  return `${rounded % 1 === 0 ? rounded.toFixed(0) : rounded} kW`;
}

/** "17.4432, 78.4953" rounded for display. */
export function formatCoords(lat: number, lng: number): string {
  return `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
}

/** A maps directions URL for a station's location (opens in a new tab). */
export function directionsUrl(lat: number, lng: number): string {
  return `https://www.openstreetmap.org/directions?to=${lat}%2C${lng}`;
}

/** Fallback display name for stations that only have a location. */
export function displayName(station: Pick<Station, "name">): string {
  const n = station.name?.trim();
  return n && n.length > 0 ? n : "Unnamed station";
}
