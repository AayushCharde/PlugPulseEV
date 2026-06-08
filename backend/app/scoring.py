"""Reliability scoring for charging stations.

Implements the freshness-weighted score described in the project spec:
each report's influence decays by half every ``half_life_hours``.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum


class ReportStatus(str, Enum):
    WORKING = "working"
    BROKEN = "broken"
    OCCUPIED = "occupied"
    ICE_BLOCKED = "ice_blocked"


# Which statuses count as positive vs negative evidence of "works right now".
# OCCUPIED is intentionally neutral: the charger works, it's just busy.
_POSITIVE = {ReportStatus.WORKING}
_NEGATIVE = {ReportStatus.BROKEN, ReportStatus.ICE_BLOCKED}


@dataclass(frozen=True)
class Report:
    status: ReportStatus
    created_at: datetime


@dataclass(frozen=True)
class Reliability:
    label: str  # "likely_working" | "mixed" | "likely_down" | "unknown"
    score: float  # 0..1, share of positive weight (0.0 when no signal)
    confidence: float  # total decayed weight of recent reports
    positive_weight: float
    negative_weight: float


def _decayed_weight(age_hours: float, half_life_hours: float) -> float:
    """A report loses half its weight every ``half_life_hours``."""
    if age_hours < 0:
        age_hours = 0.0
    return float(0.5 ** (age_hours / half_life_hours))


def compute_reliability(
    reports: list[Report],
    *,
    now: datetime | None = None,
    half_life_hours: float = 3.0,
    min_confidence: float = 0.5,
) -> Reliability:
    """Compute a freshness-weighted reliability summary for one station.

    Args:
        reports: status reports for the station.
        now: current time (defaults to UTC now); injectable for tests.
        half_life_hours: how fast a report's influence decays.
        min_confidence: below this total weight we report "unknown".
    """
    now = now or datetime.now(UTC)

    positive = 0.0
    negative = 0.0
    for r in reports:
        age_hours = (now - r.created_at).total_seconds() / 3600.0
        w = _decayed_weight(age_hours, half_life_hours)
        if r.status in _POSITIVE:
            positive += w
        elif r.status in _NEGATIVE:
            negative += w
        # neutral statuses (e.g. OCCUPIED) add no positive/negative weight

    confidence = positive + negative

    if confidence < min_confidence:
        return Reliability("unknown", 0.0, confidence, positive, negative)

    score = positive / confidence
    if score >= 0.7:
        label = "likely_working"
    elif score >= 0.4:
        label = "mixed"
    else:
        label = "likely_down"

    return Reliability(label, score, confidence, positive, negative)
