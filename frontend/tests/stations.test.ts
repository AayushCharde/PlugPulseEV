import { describe, it, expect, vi } from "vitest";
import { resolveApiBase, DEFAULT_API_BASE } from "../src/lib/api";
import {
  fetchStations,
  minPowerForTier,
  stationsToFeatureCollection,
  StationFetchError,
  type FetchLike,
  type Station,
} from "../src/lib/stations";

const bbox = { west: 78.3, south: 17.3, east: 78.6, north: 17.5 };

function station(overrides: Partial<Station> = {}): Station {
  return {
    id: 1,
    source: "ocm",
    name: "Test",
    operator: "Acme",
    lat: 17.4,
    lng: 78.45,
    max_power_kw: 50,
    access_type: "Public",
    connectors: ["CCS (Type 2)"],
    reliability: { label: "unknown", score: 0, confidence: 0 },
    ...overrides,
  };
}

function okResponse(data: unknown): Response {
  return { ok: true, status: 200, json: async () => data } as unknown as Response;
}

describe("resolveApiBase", () => {
  it("falls back to the default when empty/undefined", () => {
    expect(resolveApiBase(undefined)).toBe(DEFAULT_API_BASE);
    expect(resolveApiBase("   ")).toBe(DEFAULT_API_BASE);
  });
  it("strips a trailing slash and keeps explicit values", () => {
    expect(resolveApiBase("https://api.example.com/")).toBe("https://api.example.com");
    expect(resolveApiBase("https://api.example.com")).toBe("https://api.example.com");
  });
});

describe("fetchStations", () => {
  it("returns parsed stations and hits the bbox URL", async () => {
    const calls: string[] = [];
    const fake: FetchLike = async (url) => {
      calls.push(url);
      return okResponse([station()]);
    };
    const result = await fetchStations("http://api", { bbox }, fake);
    expect(result).toHaveLength(1);
    expect(calls[0]).toContain("bbox=78.3%2C17.3%2C78.6%2C17.5");
  });

  it("throws StationFetchError on a non-OK response", async () => {
    const fake: FetchLike = async () => ({ ok: false, status: 500 }) as unknown as Response;
    await expect(fetchStations("http://api", { bbox }, fake)).rejects.toBeInstanceOf(
      StationFetchError,
    );
    await expect(fetchStations("http://api", { bbox }, fake)).rejects.toHaveProperty("status", 500);
  });

  it("forwards the abort signal and propagates AbortError", async () => {
    const controller = new AbortController();
    const fake = vi.fn(async (_url: string, init?: { signal?: AbortSignal }) => {
      expect(init?.signal).toBe(controller.signal);
      throw Object.assign(new Error("aborted"), { name: "AbortError" });
    });
    await expect(
      fetchStations("http://api", { bbox }, fake, controller.signal),
    ).rejects.toHaveProperty("name", "AbortError");
    expect(fake).toHaveBeenCalledOnce();
  });
});

describe("stationsToFeatureCollection", () => {
  it("maps to [lng, lat] points carrying the reliability label", () => {
    const fc = stationsToFeatureCollection([
      station({ id: 7, lat: 17.4, lng: 78.45, reliability: { label: "mixed", score: 0.5, confidence: 2 } }),
    ]);
    expect(fc.type).toBe("FeatureCollection");
    expect(fc.features[0].geometry.coordinates).toEqual([78.45, 17.4]);
    expect(fc.features[0].properties.reliabilityLabel).toBe("mixed");
  });

  it("falls back to a name for unnamed stations", () => {
    const fc = stationsToFeatureCollection([station({ name: null })]);
    expect(fc.features[0].properties.name).toBe("Unnamed station");
  });
});

describe("minPowerForTier", () => {
  it("maps tiers to a minimum power", () => {
    expect(minPowerForTier("any")).toBeUndefined();
    expect(minPowerForTier("fast")).toBe(22);
    expect(minPowerForTier("rapid")).toBe(50);
  });
});
