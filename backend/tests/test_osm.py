"""Tests for the pure OSM element mapping + id namespacing (no network/DB)."""

from __future__ import annotations

import json

from app.ingest import osm_station_id
from app.osm import map_osm_element


def _titles(connectors_json: str) -> list[str]:
    return [c["ConnectionType"]["Title"] for c in json.loads(connectors_json)]


def test_maps_a_full_node() -> None:
    el = {
        "type": "node",
        "id": 42,
        "lat": 17.44,
        "lon": 78.49,
        "tags": {
            "amenity": "charging_station",
            "name": "Tata Power",
            "operator": "Tata Power",
            "access": "public",
            "socket:type2": "2",
            "socket:type2:output": "22 kW",
            "socket:type2_combo": "1",
            "socket:type2_combo:output": "50 kW",
        },
    }
    row = map_osm_element(el)
    assert row is not None
    assert row.source == "osm"
    assert row.id == osm_station_id("node", 42)
    assert row.name == "Tata Power"
    assert row.operator == "Tata Power"
    assert row.access_type == "public"
    assert row.max_power_kw == 50.0  # max of 22 and 50
    assert (row.lat, row.lng) == (17.44, 78.49)
    assert _titles(row.connectors_json) == ["Type 2", "CCS (Type 2)"]


def test_maps_a_way_via_center() -> None:
    el = {
        "type": "way",
        "id": 7,
        "center": {"lat": 1.0, "lon": 2.0},
        "tags": {"amenity": "charging_station", "socket:chademo": "1"},
    }
    row = map_osm_element(el)
    assert row is not None
    assert row.id == osm_station_id("way", 7)
    assert (row.lat, row.lng) == (1.0, 2.0)
    assert _titles(row.connectors_json) == ["CHAdeMO"]


def test_location_only_element_is_kept() -> None:
    # Only coordinates, no tags beyond amenity — still a valid, renderable row.
    el = {"type": "node", "id": 9, "lat": 5.0, "lon": 6.0, "tags": {"amenity": "charging_station"}}
    row = map_osm_element(el)
    assert row is not None
    assert row.name is None
    assert row.operator is None
    assert row.max_power_kw is None
    assert json.loads(row.connectors_json) == []


def test_missing_coordinates_returns_none() -> None:
    assert map_osm_element({"type": "node", "id": 1, "tags": {}}) is None
    assert map_osm_element({"type": "way", "id": 1, "tags": {}}) is None  # no center


def test_power_parsing_handles_units() -> None:
    el = {
        "type": "node",
        "id": 3,
        "lat": 0.0,
        "lon": 0.0,
        "tags": {"socket:type2": "1", "socket:type2:output": "7400 W", "maxpower": "11 kW"},
    }
    row = map_osm_element(el)
    assert row is not None
    assert row.max_power_kw == 11.0  # max(7.4 from watts, 11 kW)


class TestOsmStationId:
    def test_node_and_way_dont_collide(self) -> None:
        assert osm_station_id("node", 100) != osm_station_id("way", 100)

    def test_no_overlap_with_small_ocm_ids(self) -> None:
        # OCM ids are small positives; OSM ids are pushed into a high range.
        assert osm_station_id("node", 1) > 1_000_000_000
        assert osm_station_id("way", 1) > 1_000_000_000
