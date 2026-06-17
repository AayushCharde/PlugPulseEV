import { describe, it, expect } from "vitest";
import {
  sourceLabel,
  formatPower,
  formatCoords,
  directionsUrl,
  displayName,
} from "../src/lib/format";
import { geocodeUrl, parseGeocode, geocode } from "../src/lib/geocode";

describe("format helpers", () => {
  it("sourceLabel", () => {
    expect(sourceLabel("osm")).toBe("© OpenStreetMap");
    expect(sourceLabel("ocm")).toBe("Open Charge Map");
    expect(sourceLabel("other")).toBe("other");
  });

  it("formatPower", () => {
    expect(formatPower(null)).toBe("Unknown");
    expect(formatPower(0)).toBe("Unknown");
    expect(formatPower(22)).toBe("22 kW");
    expect(formatPower(3.7)).toBe("3.7 kW");
    expect(formatPower(50.0)).toBe("50 kW");
  });

  it("formatCoords", () => {
    expect(formatCoords(17.443289, 78.495271)).toBe("17.4433, 78.4953");
  });

  it("directionsUrl", () => {
    expect(directionsUrl(17.44, 78.49)).toBe(
      "https://www.openstreetmap.org/directions?to=17.44%2C78.49",
    );
  });

  it("displayName falls back", () => {
    expect(displayName({ name: "Shell" })).toBe("Shell");
    expect(displayName({ name: null })).toBe("Unnamed station");
    expect(displayName({ name: "  " })).toBe("Unnamed station");
  });
});

describe("geocode", () => {
  it("geocodeUrl encodes the query + json format", () => {
    const url = geocodeUrl("Hyderabad");
    expect(url).toContain("q=Hyderabad");
    expect(url).toContain("format=jsonv2");
    expect(url).toContain("limit=5");
  });

  it("parseGeocode keeps valid rows, drops malformed, tolerates non-array", () => {
    const parsed = parseGeocode([
      { display_name: "London", lat: "51.5", lon: "-0.1" },
      { display_name: "bad", lat: "x", lon: "y" },
    ]);
    expect(parsed).toEqual([{ label: "London", lat: 51.5, lng: -0.1 }]);
    expect(parseGeocode("nope")).toEqual([]);
  });

  it("geocode returns [] on empty query and on non-OK", async () => {
    expect(await geocode("", async () => new Response())).toEqual([]);
    const notOk = async () => ({ ok: false }) as unknown as Response;
    expect(await geocode("x", notOk)).toEqual([]);
  });

  it("geocode parses an OK response", async () => {
    const ok = async () =>
      ({ ok: true, json: async () => [{ display_name: "Paris", lat: "48.85", lon: "2.35" }] }) as unknown as Response;
    expect(await geocode("Paris", ok)).toEqual([{ label: "Paris", lat: 48.85, lng: 2.35 }]);
  });
});
