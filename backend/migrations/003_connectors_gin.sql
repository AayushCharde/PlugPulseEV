-- Speed up the connector filter (`connectors @> '[{"ConnectionType":{"Title":...}}]'`).
-- jsonb_path_ops is the compact GIN variant optimized for the @> containment operator.
CREATE INDEX IF NOT EXISTS stations_connectors_gin
    ON stations USING GIN (connectors jsonb_path_ops);
