# Deployment

PlugPulse is two deployable units. They go to **different** places.

Everything here stays **free and open** (no paid services in the core path).

| Unit | Goes to | Why |
|---|---|---|
| `frontend/` (SvelteKit) | **Vercel** (free Hobby tier) | First-class SvelteKit support, no cost |
| `backend/` (FastAPI + PostGIS) | **Self-hosted Docker** — *not* Vercel | Long-running ASGI server + PostgreSQL/PostGIS; Vercel can't run it. The repo already ships a one-command stack. |

## Frontend → Vercel

The repo is already prepared. [`frontend/svelte.config.js`](frontend/svelte.config.js) picks the
adapter by environment: `@sveltejs/adapter-vercel` when `VERCEL=1` (Vercel sets this),
`@sveltejs/adapter-node` everywhere else (Docker, `docker compose`, CI). No code change is
needed to deploy.

One-time setup in the Vercel dashboard:

1. **New Project** → import the `AayushCharde/PlugPulseEV` GitHub repo.
2. **Root Directory:** set to `frontend` (this is a monorepo — Vercel must build the subdir).
   SvelteKit framework preset is auto-detected; leave build/install commands at defaults.
3. **Environment Variables:** add `PUBLIC_API_BASE_URL` = the deployed backend's URL
   (e.g. `https://api.plugpulse.app`). Until the backend is live this can point at a
   placeholder; the current "hello map" doesn't call the API yet.
4. Deploy. Vercel runs `npm install` (which runs `svelte-kit sync`) then `npm run build`.

Note the frontend's Vercel URL — the backend must allow it via CORS (see below).

Pushes to `main` then auto-deploy; PRs get preview URLs.

## Backend → self-hosted Docker (free + open)

The backend is **not** deployed yet. The free, open path is to run the container stack
yourself — no PaaS bill, no lock-in.

CI already publishes images to GHCR on every push to `main`:

- `ghcr.io/aayushcharde/plugpulseev/backend`
- `ghcr.io/aayushcharde/plugpulseev/frontend` (unused once the frontend is on Vercel)

### Option A — full self-host (recommended, one stack)

Run the whole backend stack (backend + PostGIS + Redis) behind **Caddy** (automatic HTTPS)
on any box you control — a VPS, a home server, or a free-forever VM (e.g. Oracle Cloud
Always Free). Use [`docker-compose.prod.yml`](docker-compose.prod.yml):

```bash
# 1. Point your API domain's DNS (A/AAAA) at this server first.
# 2. Configure secrets:
cp .env.prod.example .env        # then edit: DOMAIN, POSTGRES_PASSWORD, CORS_ALLOW_ORIGINS
# 3. Launch (Caddy gets a Let's Encrypt cert for $DOMAIN automatically):
docker compose -f docker-compose.prod.yml up -d --build
```

What this gives you over the dev `docker-compose.yml`:

- **Caddy** terminates HTTPS and proxies to the backend — no manual TLS.
- The database, Redis, and backend publish **no host ports** (only Caddy's 80/443 are open).
- `restart: unless-stopped` on every service.
- `POSTGRES_PASSWORD` is required (the stack refuses to start without it).

The schema in [`backend/migrations/001_init.sql`](backend/migrations/001_init.sql) is applied
on the database's first boot. Then set the Vercel `PUBLIC_API_BASE_URL` to `https://$DOMAIN`.

### Option B — backend container + free managed Postgres

If you'd rather not run the database yourself, use a durable **free-tier Postgres that
supports the PostGIS extension** — e.g. **Neon** or **Supabase** — and run only the backend
container. Required env: `DATABASE_URL` (the managed Postgres URL), optional `REDIS_URL`,
`OCM_API_KEY`, `CORS_ALLOW_ORIGINS`. Run `CREATE EXTENSION postgis;` and apply
[`backend/migrations/001_init.sql`](backend/migrations/001_init.sql) once against that database.

### Option C — Render + Supabase (managed, no server to run) — *recommended free path*

Everything stays free and there's no machine to maintain: frontend on Vercel, backend
(this FastAPI container) on **Render** free, database on **Supabase** free (Postgres +
PostGIS). A [`render.yaml`](render.yaml) blueprint is included.

**1. Supabase (database):**
- Create a project at [supabase.com](https://supabase.com) (free, no card).
- SQL Editor → enable PostGIS and apply the migrations, in order:
  `001_init.sql`, `002_users.sql`, `003_connectors_gin.sql` (paste each, or
  `psql "<conn>" -f backend/migrations/00X_*.sql`). `001` runs `CREATE EXTENSION postgis`.
- Project Settings → Database → copy the **Direct connection** string (or **Session**
  pooler). **Do not use the Transaction pooler** (port 6543) — asyncpg uses prepared
  statements, which it doesn't support. The string includes `sslmode=require`.

**2. Render (backend):**
- New → **Blueprint** → pick this repo; Render reads `render.yaml` (Docker, free plan,
  health check `/health`).
- Set the dashboard env vars: `DATABASE_URL` = the Supabase Direct string,
  `OCM_API_KEY` = your free OCM key. `CORS_ALLOW_ORIGINS` is preset to the Vercel origin.
  Leave `REDIS_URL` and `OIDC_*` unset (cache optional; auth deferred).
- Deploy → grab the service URL `https://<name>.onrender.com`.

**3. Connect the frontend:** in Vercel set `PUBLIC_API_BASE_URL` to the Render URL →
redeploy. Verify `https://<name>.onrender.com/health` and `/stations?bbox=...`.

**Heads-up (free-tier behaviour):** the Render service **sleeps after ~15 min idle**
(first request then takes ~1 min); Supabase **pauses after 7 days idle** (resume in the
dashboard, or hit it periodically). A simple uptime ping to `/health` keeps both warm.

> Auth on this path: defer it (the map is public), or later use **Supabase Auth** in place
> of Authentik — it issues verifiable JWTs, so the backend's existing OIDC verification can
> point at Supabase. Authentik is only needed for the self-host Option A.

## Authentication — Authentik (OIDC)

Auth is **self-hosted Authentik** (open source). The backend validates Authentik-issued JWTs;
the frontend logs in via OIDC. Auth is **optional** — with the `OIDC_*` env unset the public
map works unchanged and `/me` returns 503.

Authentik runs as part of both compose files (its own Postgres + Redis). In prod it's exposed
on `AUTH_DOMAIN` via Caddy (auto-HTTPS). One-time setup:

1. Bring up the stack (`docker compose up -d`, or prod). Point `AUTH_DOMAIN`'s DNS at the server.
2. Open Authentik (`http://localhost:9000` dev, or `https://$AUTH_DOMAIN` prod) and complete the
   initial admin flow at `/if/flow/initial-setup/`.
3. Create an **OAuth2/OpenID Provider** + an **Application** ("PlugPulse"). Set redirect URIs:
   - dev: `http://localhost:5173/auth/callback/authentik`
   - prod: `https://plugpulse.vercel.app/auth/callback/authentik`
4. Copy into your env:
   - `OIDC_ISSUER=https://$AUTH_DOMAIN/application/o/<app-slug>/`
   - `OIDC_JWKS_URL=https://$AUTH_DOMAIN/application/o/<app-slug>/jwks/`
   - `OIDC_AUDIENCE=<Client ID>` (backend) and the frontend `AUTH_AUTHENTIK_*` (see frontend env).
5. Restart the backend (and frontend). Verify: sign in, then `GET /me` returns your user.

`users` are created on first authenticated request (upsert by OIDC `sub`); the
[`002_users.sql`](backend/migrations/002_users.sql) migration runs on the DB's first boot.

## CORS (frontend ↔ backend are different origins)

Because the frontend is on Vercel and the backend on your own host, the browser blocks
cross-origin calls unless the API opts in. Set `CORS_ALLOW_ORIGINS` (comma-separated) to your
frontend origin(s), e.g. `https://plugpulse.vercel.app,https://plugpulse.app`. Leave it empty
and the API allows no cross-origin access.

## Secrets

For now secrets live in a gitignored `.env` (see `.env.prod.example`) — appropriate for the
two secrets in play (`POSTGRES_PASSWORD`, optional `OCM_API_KEY`). When secrets or
environments grow, the open-source upgrade path is **Infisical** (self-hosted or its free
tier): store secrets there and inject them at launch without changing the stack, e.g.
`infisical run -- docker compose -f docker-compose.prod.yml up -d`.

## Production domain

The frontend is live at **https://plugpulse.vercel.app** — this is the canonical domain,
set in [`frontend/src/lib/seo.ts`](frontend/src/lib/seo.ts) (`SITE.url`),
`frontend/static/robots.txt` (sitemap), and `frontend/static/llms.txt`. If you later move to a
custom domain (e.g. `plugpulse.app`), update those three places.
