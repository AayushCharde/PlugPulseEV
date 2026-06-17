/**
 * Station query contract. The client only ever asks for the current viewport
 * (a bounding box) with a hard result cap — never the whole dataset. This keeps
 * payloads small and responses fast no matter how far out the user zooms.
 */

export interface BBox {
  west: number;
  south: number;
  east: number;
  north: number;
}

export interface StationQuery {
  bbox: BBox;
  connector?: string;
  minPowerKw?: number;
  limit?: number;
}

export const DEFAULT_STATION_LIMIT = 300;

// Default to the deployed backend so the app works end-to-end everywhere
// (production, Vercel previews, shared links) even when PUBLIC_API_BASE_URL
// isn't set for that environment. Local dev overrides it via .env
// (PUBLIC_API_BASE_URL=http://localhost:8000).
export const DEFAULT_API_BASE = "https://plugpulse-backend-v5bu.onrender.com";

/** Normalize a configured API base URL: fall back to the default, strip trailing slash. */
export function resolveApiBase(raw: string | undefined): string {
  const base = (raw ?? "").trim() || DEFAULT_API_BASE;
  return base.replace(/\/+$/, "");
}

/** Build the `/stations` request URL from a viewport query. */
export function stationsUrl(apiBase: string, q: StationQuery): string {
  const params = new URLSearchParams();
  params.set("bbox", `${q.bbox.west},${q.bbox.south},${q.bbox.east},${q.bbox.north}`);
  if (q.connector) params.set("connector", q.connector);
  if (q.minPowerKw !== undefined) params.set("min_power_kw", String(q.minPowerKw));
  params.set("limit", String(q.limit ?? DEFAULT_STATION_LIMIT));
  return `${apiBase}/stations?${params.toString()}`;
}
