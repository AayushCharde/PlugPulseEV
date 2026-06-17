-- Provenance for multi-source ingest (Open Charge Map, OpenStreetMap, …).
-- Existing rows default to 'ocm'. OSM ids are namespaced (app/ingest.py) so the
-- single-column PRIMARY KEY on stations.id still holds across sources.
ALTER TABLE stations ADD COLUMN IF NOT EXISTS source TEXT NOT NULL DEFAULT 'ocm';
