"""Tests for the pure OCM POI mapping (no network/DB)."""

from __future__ import annotations

import json

from app.ocm import map_poi

_FULL_POI = {
    "ID": 123,
    "AddressInfo": {"Title": "Test Station", "Latitude": 51.5, "Longitude": -0.1},
    "OperatorInfo": {"Title": "Acme Charging"},
    "UsageType": {"Title": "Public"},
    "Connections": [
        {"ConnectionType": {"Title": "CCS (Type 2)"}, "PowerKW": 50},
        {"ConnectionType": {"Title": "Type 2"}, "PowerKW": 22},
    ],
}


def test_maps_a_full_poi() -> None:
    row = map_poi(_FULL_POI)
    assert row is not None
    assert row.id == 123
    assert row.name == "Test Station"
    assert row.operator == "Acme Charging"
    assert row.access_type == "Public"
    assert row.max_power_kw == 50.0
    assert (row.lat, row.lng) == (51.5, -0.1)
    assert json.loads(row.connectors_json) == _FULL_POI["Connections"]


def test_missing_coordinates_returns_none() -> None:
    poi = {"ID": 1, "AddressInfo": {"Title": "No coords"}}
    assert map_poi(poi) is None


def test_missing_id_returns_none() -> None:
    assert map_poi({"AddressInfo": {"Latitude": 1.0, "Longitude": 2.0}}) is None


def test_null_operator_and_usage_are_tolerated() -> None:
    poi = {
        "ID": 7,
        "AddressInfo": {"Title": "Bare", "Latitude": 1.0, "Longitude": 2.0},
        "OperatorInfo": None,
        "UsageType": None,
        "Connections": [],
    }
    row = map_poi(poi)
    assert row is not None
    assert row.operator is None
    assert row.access_type is None
    assert row.max_power_kw is None
    assert json.loads(row.connectors_json) == []


def test_power_ignores_missing_or_null_powerkw() -> None:
    poi = {
        "ID": 9,
        "AddressInfo": {"Latitude": 0.0, "Longitude": 0.0},
        "Connections": [{"PowerKW": None}, {"PowerKW": 7.4}, {}],
    }
    row = map_poi(poi)
    assert row is not None
    assert row.max_power_kw == 7.4


def test_bool_id_is_rejected() -> None:
    # JSON has no bools as ids, but guard against bool-is-int surprises.
    assert map_poi({"ID": True, "AddressInfo": {"Latitude": 1.0, "Longitude": 2.0}}) is None
