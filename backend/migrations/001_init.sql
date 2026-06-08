-- PlugPulse initial schema.
-- Mounted into the Postgres container's init dir so it runs on first boot.

CREATE EXTENSION IF NOT EXISTS postgis;

-- Charging stations, cached locally from Open Charge Map so we never hit the
-- upstream API on the hot path.
CREATE TABLE IF NOT EXISTS stations (
    id            BIGINT PRIMARY KEY,                 -- Open Charge Map POI id
    name          TEXT,
    operator      TEXT,
    max_power_kw  REAL,
    access_type   TEXT,
    connectors    JSONB,
    geom          geography(Point, 4326) NOT NULL,
    last_synced   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- THE key performance index: makes "stations within this map viewport" a fast
-- spatial lookup instead of a full-table scan. Without this, the map crawls.
CREATE INDEX IF NOT EXISTS stations_geom_gix
    ON stations USING GIST (geom);

-- Community status reports.
CREATE TABLE IF NOT EXISTS reports (
    id              BIGSERIAL PRIMARY KEY,
    station_id      BIGINT NOT NULL REFERENCES stations(id) ON DELETE CASCADE,
    user_id         BIGINT,
    status          TEXT NOT NULL
                    CHECK (status IN ('working', 'broken', 'occupied', 'ice_blocked')),
    actual_power_kw REAL,
    note            TEXT,
    geom            geography(Point, 4326),           -- reporter location (geofence)
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Scoring only reads recent reports per station; this composite index serves
-- that query directly (station_id filter + newest-first scan).
CREATE INDEX IF NOT EXISTS reports_station_recent_idx
    ON reports (station_id, created_at DESC);
