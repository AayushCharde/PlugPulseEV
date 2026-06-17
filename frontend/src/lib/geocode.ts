/**
 * Place search via Nominatim (OpenStreetMap) — open + free, no key.
 * Pure URL builder + a thin fetch wrapper (injectable) so it's unit-testable.
 */

export interface GeocodeResult {
  label: string;
  lat: number;
  lng: number;
}

const NOMINATIM_URL = "https://nominatim.openstreetmap.org/search";

/** Build the Nominatim search URL (JSON, capped results). */
export function geocodeUrl(query: string, limit = 5): string {
  const params = new URLSearchParams({
    q: query,
    format: "jsonv2",
    limit: String(limit),
    addressdetails: "0",
  });
  return `${NOMINATIM_URL}?${params.toString()}`;
}

type FetchLike = (input: string, init?: { signal?: AbortSignal; headers?: Record<string, string> }) => Promise<Response>;

interface NominatimItem {
  display_name?: string;
  lat?: string;
  lon?: string;
}

/** Parse Nominatim's JSON into our result shape (skips malformed rows). */
export function parseGeocode(items: unknown): GeocodeResult[] {
  if (!Array.isArray(items)) return [];
  const out: GeocodeResult[] = [];
  for (const raw of items as NominatimItem[]) {
    const lat = Number(raw?.lat);
    const lng = Number(raw?.lon);
    if (!Number.isFinite(lat) || !Number.isFinite(lng)) continue;
    out.push({ label: raw.display_name ?? `${lat}, ${lng}`, lat, lng });
  }
  return out;
}

/** Search for a place. Returns [] on a non-OK response; aborts propagate. */
export async function geocode(
  query: string,
  fetchImpl: FetchLike = fetch,
  signal?: AbortSignal,
): Promise<GeocodeResult[]> {
  if (!query.trim()) return [];
  const res = await fetchImpl(geocodeUrl(query), signal ? { signal } : undefined);
  if (!res.ok) return [];
  return parseGeocode(await res.json());
}
