-- PlugPulse users — keyed to the OIDC subject from the identity provider
-- (Authentik). Created on first authenticated request (upsert by oidc_sub).

CREATE TABLE IF NOT EXISTS users (
    id          BIGSERIAL PRIMARY KEY,
    oidc_sub    TEXT UNIQUE NOT NULL,             -- OIDC `sub` claim
    handle      TEXT,                             -- from preferred_username / name
    email       TEXT,
    trust_score REAL NOT NULL DEFAULT 1.0,        -- nudged by report track record (Phase 2)
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Now that users exist, tie reports to them. reports.user_id was created in
-- 001_init.sql without a foreign key (users didn't exist yet); add it here.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'reports_user_id_fkey'
    ) THEN
        ALTER TABLE reports
            ADD CONSTRAINT reports_user_id_fkey
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;
    END IF;
END $$;
