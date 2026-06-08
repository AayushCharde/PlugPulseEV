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

Pushes to `main` then auto-deploy; PRs get preview URLs.

## Backend → self-hosted Docker (free + open)

The backend is **not** deployed yet. The free, open path is to run the container stack
yourself — no PaaS bill, no lock-in.

CI already publishes images to GHCR on every push to `main`:

- `ghcr.io/aayushcharde/plugpulseev/backend`
- `ghcr.io/aayushcharde/plugpulseev/frontend` (unused once the frontend is on Vercel)

### Option A — full self-host (one command)

Run the whole stack (backend + PostGIS + Redis) on any box you control — a VPS, a home
server, or a free-forever VM (e.g. Oracle Cloud Always Free):

```bash
docker compose up -d            # backend :8000, db :5432 (PostGIS), redis :6379
```

`docker compose` already applies [`backend/migrations/001_init.sql`](backend/migrations/001_init.sql)
on the database's first boot (mounted into the Postgres init dir). Put a free reverse proxy
(Caddy / nginx) in front for HTTPS, then point the Vercel `PUBLIC_API_BASE_URL` at it.

### Option B — backend container + free managed Postgres

If you'd rather not run the database yourself, use a durable **free-tier Postgres that
supports the PostGIS extension** — e.g. **Neon** or **Supabase** — and run only the backend
container. Required env: `DATABASE_URL` (the managed Postgres URL), optional `REDIS_URL`,
`OCM_API_KEY`. Run `CREATE EXTENSION postgis;` and apply
[`backend/migrations/001_init.sql`](backend/migrations/001_init.sql) once against that database.

## After both are live

Replace the `https://plugpulse.app` placeholder domain in
[`frontend/src/lib/seo.ts`](frontend/src/lib/seo.ts), `frontend/static/robots.txt`, and
`frontend/static/llms.txt` with the real domain.
