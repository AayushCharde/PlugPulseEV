"""Tests for the reliability scoring algorithm."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.scoring import Report, ReportStatus, compute_reliability

NOW = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


def _ago(hours: float) -> datetime:
    return NOW - timedelta(hours=hours)


def test_no_reports_is_unknown() -> None:
    result = compute_reliability([], now=NOW)
    assert result.label == "unknown"
    assert result.score == 0.0
    assert result.confidence == 0.0


def test_recent_working_reports_are_likely_working() -> None:
    reports = [
        Report(ReportStatus.WORKING, _ago(0.1)),
        Report(ReportStatus.WORKING, _ago(0.5)),
        Report(ReportStatus.WORKING, _ago(1.0)),
    ]
    result = compute_reliability(reports, now=NOW)
    assert result.label == "likely_working"
    assert result.score > 0.9


def test_recent_broken_reports_are_likely_down() -> None:
    reports = [
        Report(ReportStatus.BROKEN, _ago(0.2)),
        Report(ReportStatus.ICE_BLOCKED, _ago(0.4)),
        Report(ReportStatus.BROKEN, _ago(0.6)),
    ]
    result = compute_reliability(reports, now=NOW)
    assert result.label == "likely_down"
    assert result.score < 0.4


def test_decay_lets_recent_reports_outweigh_old_ones() -> None:
    # One fresh "working" should outweigh one very old "broken".
    reports = [
        Report(ReportStatus.BROKEN, _ago(24.0)),  # heavily decayed
        Report(ReportStatus.WORKING, _ago(0.1)),  # fresh
    ]
    result = compute_reliability(reports, now=NOW)
    assert result.label == "likely_working"


def test_occupied_is_neutral() -> None:
    # OCCUPIED means it works but is busy: no negative weight.
    reports = [
        Report(ReportStatus.WORKING, _ago(0.2)),
        Report(ReportStatus.OCCUPIED, _ago(0.3)),
    ]
    result = compute_reliability(reports, now=NOW)
    assert result.negative_weight == 0.0
    assert result.label == "likely_working"


def test_half_life_halves_weight() -> None:
    # A report exactly one half-life old should weigh ~0.5.
    reports = [Report(ReportStatus.WORKING, _ago(3.0))]
    result = compute_reliability(reports, now=NOW, half_life_hours=3.0, min_confidence=0.0)
    assert abs(result.positive_weight - 0.5) < 1e-9
