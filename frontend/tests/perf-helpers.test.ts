import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { debounce } from "../src/lib/debounce";
import { stationsUrl, type StationQuery } from "../src/lib/api";

describe("debounce", () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  it("calls only once after rapid calls", () => {
    const fn = vi.fn();
    const debounced = debounce(fn, 200);
    debounced();
    debounced();
    debounced();
    expect(fn).not.toHaveBeenCalled();
    vi.advanceTimersByTime(200);
    expect(fn).toHaveBeenCalledTimes(1);
  });

  it("passes the latest arguments through", () => {
    const fn = vi.fn();
    const debounced = debounce(fn, 100);
    debounced("a");
    debounced("b");
    vi.advanceTimersByTime(100);
    expect(fn).toHaveBeenCalledWith("b");
  });
});

describe("stationsUrl", () => {
  const bbox = { west: 78.3, south: 17.3, east: 78.6, north: 17.5 };

  it("encodes the bbox and default limit", () => {
    const q: StationQuery = { bbox };
    const url = stationsUrl("http://api", q);
    expect(url).toContain("bbox=78.3%2C17.3%2C78.6%2C17.5");
    expect(url).toContain("limit=300");
  });

  it("includes optional filters when set", () => {
    const q: StationQuery = { bbox, connector: "ccs2", minPowerKw: 50, limit: 100 };
    const url = stationsUrl("http://api", q);
    expect(url).toContain("connector=ccs2");
    expect(url).toContain("min_power_kw=50");
    expect(url).toContain("limit=100");
  });
});
