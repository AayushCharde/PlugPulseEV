import { describe, it, expect } from "vitest";
import { nextTheme, resolveTheme } from "../src/lib/theme";

describe("nextTheme", () => {
  it("flips between light and dark", () => {
    expect(nextTheme("light")).toBe("dark");
    expect(nextTheme("dark")).toBe("light");
  });
});

describe("resolveTheme", () => {
  it("honors a stored choice over the OS preference", () => {
    expect(resolveTheme("dark", false)).toBe("dark");
    expect(resolveTheme("light", true)).toBe("light");
  });

  it("falls back to the OS preference when unset or invalid", () => {
    expect(resolveTheme(null, true)).toBe("dark");
    expect(resolveTheme(null, false)).toBe("light");
    expect(resolveTheme("bogus", true)).toBe("dark");
  });
});
