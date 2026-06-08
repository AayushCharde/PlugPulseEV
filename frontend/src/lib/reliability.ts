/**
 * Maps a backend reliability result to the text + color the UI shows.
 * Keep this in sync with backend/app/scoring.py.
 */

export type ReliabilityLabel =
  | "likely_working"
  | "mixed"
  | "likely_down"
  | "unknown";

export interface Reliability {
  label: ReliabilityLabel;
  score: number; // 0..1
  confidence: number; // total decayed weight of recent reports
}

export interface ReliabilityDisplay {
  text: string;
  color: "green" | "amber" | "red" | "grey";
}

export function describeReliability(r: Reliability): ReliabilityDisplay {
  switch (r.label) {
    case "likely_working":
      return { text: "Likely working", color: "green" };
    case "mixed":
      return { text: "Mixed reports", color: "amber" };
    case "likely_down":
      return { text: "Likely down", color: "red" };
    default:
      return { text: "No recent reports", color: "grey" };
  }
}

/** Human-friendly evidence line, e.g. "≈4 confirmations recently". */
export function evidenceLine(r: Reliability): string {
  if (r.confidence < 0.5) return "No recent reports";
  const approx = Math.round(r.confidence);
  return `${approx} recent confirmation${approx === 1 ? "" : "s"}`;
}
