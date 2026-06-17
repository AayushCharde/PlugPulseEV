/**
 * Station data: the response shape from GET /stations, a small fetch wrapper,
 * and the pure transforms the map needs. Kept free of DOM / $env / MapLibre
 * imports so it's unit-testable in plain Node.
 */

import type { FeatureCollection, Point } from "geojson";
import { stationsUrl, type StationQuery } from "$lib/api";
import type { Reliability, ReliabilityLabel } from "$lib/reliability";

/** A station as returned by GET /stations (mirrors backend StationOut). */
export interface Station {
  id: number | string;
  source: string; // "ocm" | "osm" — data provenance
  name: string | null;
  operator: string | null;
  lat: number;
  lng: number;
  max_power_kw: number | null;
  access_type: string | null;
  connectors: string[];
  reliability: Reliability;
}

/** Minimal fetch signature so tests can inject a fake. */
export type FetchLike = (input: string, init?: { signal?: AbortSignal }) => Promise<Response>;

export class StationFetchError extends Error {
  readonly status: number;
  constructor(status: number, message: string) {
    super(message);
    this.name = "StationFetchError";
    this.status = status;
  }
}

/**
 * Fetch stations for a viewport. Throws {@link StationFetchError} on a non-OK
 * response; aborts surface as a DOMException("AbortError") for the caller to ignore.
 */
export async function fetchStations(
  apiBase: string,
  query: StationQuery,
  fetchImpl: FetchLike = fetch,
  signal?: AbortSignal,
): Promise<Station[]> {
  const url = stationsUrl(apiBase, query);
  const res = await fetchImpl(url, signal ? { signal } : undefined);
  if (!res.ok) {
    throw new StationFetchError(res.status, `GET /stations failed: ${res.status}`);
  }
  return (await res.json()) as Station[];
}

/** Properties carried on each map feature (kept minimal; full Station held separately). */
export interface StationFeatureProps {
  id: number | string;
  name: string;
  reliabilityLabel: ReliabilityLabel;
}

export type StationFeatureCollection = FeatureCollection<Point, StationFeatureProps>;

/** Convert stations to a GeoJSON FeatureCollection for the MapLibre source. */
export function stationsToFeatureCollection(stations: Station[]): StationFeatureCollection {
  return {
    type: "FeatureCollection",
    features: stations.map((s) => ({
      type: "Feature",
      geometry: { type: "Point", coordinates: [s.lng, s.lat] },
      properties: {
        id: s.id,
        name: s.name ?? "Unnamed station",
        reliabilityLabel: s.reliability.label,
      },
    })),
  };
}

/** UI power tiers. The API filters by a *minimum* power, so we expose min-based tiers. */
export type PowerTier = "any" | "fast" | "rapid";

/** Minimum power (kW) for a tier, or undefined for no filter. */
export function minPowerForTier(tier: PowerTier): number | undefined {
  switch (tier) {
    case "fast":
      return 22;
    case "rapid":
      return 50;
    default:
      return undefined;
  }
}
