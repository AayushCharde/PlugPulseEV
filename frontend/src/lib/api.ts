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

/** Build the `/stations` request URL from a viewport query. */
export function stationsUrl(apiBase: string, q: StationQuery): string {
  const params = new URLSearchParams();
  params.set("bbox", `${q.bbox.west},${q.bbox.south},${q.bbox.east},${q.bbox.north}`);
  if (q.connector) params.set("connector", q.connector);
  if (q.minPowerKw !== undefined) params.set("min_power_kw", String(q.minPowerKw));
  params.set("limit", String(q.limit ?? DEFAULT_STATION_LIMIT));
  return `${apiBase}/stations?${params.toString()}`;
}
