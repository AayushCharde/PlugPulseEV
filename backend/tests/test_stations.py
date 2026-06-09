"""Tests for pure station-route helpers (no network/DB): bbox parsing,
connector-title extraction, and reliability assembly."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.geo import parse_bbox
from app.stations import assemble_reliability, connector_titles


class TestParseBbox:
    def test_valid(self) -> None:
        box = parse_bbox("-0.2,51.45,-0.05,51.55")
        assert (box.west, box.south, box.east, box.north) == (-0.2, 51.45, -0.05, 51.55)

    @pytest.mark.parametrize(
        "raw",
        [
            "1,2,3",  # wrong arity
            "1,2,3,4,5",  # wrong arity
            "a,b,c,d",  # non-numeric
            "-200,0,10,10",  # lon out of range
            "0,-100,10,10",  # lat out of range
            "10,0,5,10",  # west >= east
            "0,10,10,5",  # south >= north
        ],
    )
    def test_rejects(self, raw: str) -> None:
        with pytest.raises(ValueError):
            parse_bbox(raw)


class TestConnectorTitles:
    def test_extracts_distinct_titles(self) -> None:
        raw = [
            {"ConnectionType": {"Title": "CCS (Type 2)"}},
            {"ConnectionType": {"Title": "Type 2"}},
            {"ConnectionType": {"Title": "CCS (Type 2)"}},  # dup
        ]
        assert connector_titles(raw) == ["CCS (Type 2)", "Type 2"]

    def test_accepts_json_string(self) -> None:
        assert connector_titles('[{"ConnectionType": {"Title": "CHAdeMO"}}]') == ["CHAdeMO"]

    def test_tolerates_garbage(self) -> None:
        assert connector_titles(None) == []
        assert connector_titles("not json") == []
        assert connector_titles([{"no": "type"}, 42, {"ConnectionType": {}}]) == []


class TestAssembleReliability:
    def test_no_reports_is_unknown(self) -> None:
        out = assemble_reliability([1, 2], [])
        assert out[1].label == "unknown"
        assert out[2].label == "unknown"

    def test_recent_working_is_likely_working(self) -> None:
        now = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
        rows = [{"station_id": 1, "status": "working", "created_at": now} for _ in range(3)]
        out = assemble_reliability([1], rows, now=now)
        assert out[1].label == "likely_working"
        assert out[1].score == 1.0

    def test_ignores_reports_for_unlisted_stations(self) -> None:
        now = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
        rows = [{"station_id": 99, "status": "working", "created_at": now}]
        out = assemble_reliability([1], rows, now=now)
        assert set(out) == {1}
        assert out[1].label == "unknown"

    def test_skips_unknown_status_values(self) -> None:
        now = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
        rows = [{"station_id": 1, "status": "bogus", "created_at": now}]
        out = assemble_reliability([1], rows, now=now)
        assert out[1].label == "unknown"
