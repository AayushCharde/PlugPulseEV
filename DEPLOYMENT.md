# Deployment

PlugPulse is two deployable units. They go to **different** places.

| Unit | Goes to | Why |
|---|---|---|
| `frontend/` (SvelteKit) | **Vercel** | Static + serverless, first-class SvelteKit support |
| `backend/` (FastAPI + PostGIS) | **Not Vercel** — a container host (Fly.io / Railway / VPS) | Long-running ASGI server + PostgreSQL/PostGIS; Vercel can't run it |

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

## Backend → container host (TODO)

Not yet deployed. The CI Docker workflow already publishes images to GHCR:

- `ghcr.io/aayushcharde/plugpulseev/backend`
- `ghcr.io/aayushcharde/plugpulseev/frontend` (unused if the frontend is on Vercel)

To run the backend you need a host that can run the container **and** a PostgreSQL database
with the PostGIS extension. Suggested: Fly.io or Railway (both offer managed Postgres).
Required env: `DATABASE_URL`, optional `REDIS_URL`, `OCM_API_KEY`. Apply
[`backend/migrations/001_init.sql`](backend/migrations/001_init.sql) on first boot.

## After both are live

Replace the `https://plugpulse.app` placeholder domain in
[`frontend/src/lib/seo.ts`](frontend/src/lib/seo.ts), `frontend/static/robots.txt`, and
`frontend/static/llms.txt` with the real domain.
