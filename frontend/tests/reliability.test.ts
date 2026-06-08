import { describe, it, expect } from "vitest";
import {
  describeReliability,
  evidenceLine,
  type Reliability,
} from "../src/lib/reliability";

describe("describeReliability", () => {
  it("maps likely_working to green", () => {
    const r: Reliability = { label: "likely_working", score: 0.9, confidence: 3 };
    expect(describeReliability(r)).toEqual({ text: "Likely working", color: "green" });
  });

  it("maps likely_down to red", () => {
    const r: Reliability = { label: "likely_down", score: 0.1, confidence: 3 };
    expect(describeReliability(r).color).toBe("red");
  });

  it("maps unknown to grey", () => {
    const r: Reliability = { label: "unknown", score: 0, confidence: 0 };
    expect(describeReliability(r).color).toBe("grey");
  });
});

describe("evidenceLine", () => {
  it("reports no recent data below the confidence floor", () => {
    const r: Reliability = { label: "unknown", score: 0, confidence: 0.2 };
    expect(evidenceLine(r)).toBe("No recent reports");
  });

  it("pluralizes correctly", () => {
    const one: Reliability = { label: "likely_working", score: 1, confidence: 1 };
    expect(evidenceLine(one)).toBe("1 recent confirmation");
    const many: Reliability = { label: "likely_working", score: 1, confidence: 4 };
    expect(evidenceLine(many)).toBe("4 recent confirmations");
  });
});
