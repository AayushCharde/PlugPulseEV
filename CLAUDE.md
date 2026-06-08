# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is PlugPulse

An open-source, community-verified EV charger reliability app. It layers freshness-weighted live status reports (Working/Broken/Occupied/ICE-blocked) on top of Open Charge Map station data, producing a trust score for each charger. Think "Waze for EV charger reliability."

## Commands

### Backend (FastAPI / Python 3.12)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

# Run dev server
uvicorn app.main:app --reload          # http://localhost:8000/health

# Checks (all must pass for CI)
ruff check .                           # lint
ruff format --check .                  # format check
mypy app                               # type check (strict mode)
pytest                                  # tests
pytest --cov=app --cov-report=term-missing  # tests with coverage
pytest tests/test_scoring.py           # single test file
```

### Frontend (SvelteKit + TypeScript)

```bash
cd frontend
npm install

# Run dev server
npm run dev                             # http://localhost:5173

# Checks (all must pass for CI)
npm run lint                            # eslint
npm run test                            # vitest
npm run build                           # production build
svelte-check --tsconfig ./tsconfig.json # type check
```

### Docker (full stack)

```bash
docker compose up --build               # starts db, redis, backend, frontend
```

DB credentials: `plugpulse:plugpulse@localhost:5432/plugpulse`. Redis at `localhost:6379`.

## Architecture

```
frontend/ (SvelteKit PWA)           backend/ (FastAPI)
  src/lib/api.ts      ←─ bbox queries ─→  app/main.py (routes)
  src/lib/reliability.ts               app/scoring.py (core algorithm)
  src/lib/debounce.ts                  app/config.py (env-based settings)
  src/lib/seo.ts                       app/cache.py (optional Redis wrapper)
                                       migrations/001_init.sql (PostGIS schema)
```

- **Viewport-only data flow**: Frontend sends bounding-box queries; backend returns stations within that bbox joined with live reliability scores. Never returns the full dataset.
- **Reliability scoring** (`backend/app/scoring.py`): Each report decays with a half-life (default 3h). Score = positive_weight / (positive + negative). OCCUPIED is neutral. Labels: ≥0.7 = "likely_working", 0.4–0.7 = "mixed", <0.4 = "likely_down", low confidence = "unknown".
- **Frontend reliability display** (`frontend/src/lib/reliability.ts`): Maps backend labels to UI text/colors. Must stay in sync with `scoring.py`.
- **Cache is optional**: Redis wraps get/set as no-ops when `REDIS_URL` is unset. The app works without it.
- **Database**: PostgreSQL + PostGIS. `stations` table has a GIST spatial index (`stations_geom_gix`). `reports` has a composite index on `(station_id, created_at DESC)` for efficient recent-report lookups.

## Key config (environment variables)

`DATABASE_URL`, `REDIS_URL` (optional), `OCM_API_KEY` (optional), `MAX_STATIONS_PER_REQUEST` (default 300), `RELIABILITY_CACHE_TTL` (default 60s), `RELIABILITY_LOOKBACK_HOURS` (default 24), `DB_POOL_MIN_SIZE`/`DB_POOL_MAX_SIZE`.

## Conventions

- **Commits**: Conventional Commits format — `feat(scoring):`, `fix(map):`, `docs:`, `chore:`, `refactor:`
- **Branches**: prefixed `feat/`, `fix/`, `docs/`, `chore/`, `ci/`, `refactor/`
- **Python**: ruff for linting+formatting (line-length 100, target py312); mypy strict mode; ruff lint rules: E, F, I, UP, B, SIM
- **License**: AGPL-3.0 for code, CC BY-SA 4.0 for community data. Attribution for Open Charge Map and OpenFreeMap/OSM must be preserved (see `ATTRIBUTION.md`).
- **Performance budgets**: `/stations` API <100ms warm / <300ms cold; initial JS bundle <200KB gzipped; FCP <1.8s; LCP <2.5s. See `PERFORMANCE.md` for full list.
- **No paid services in core path**: everything must run with free, open tools.
- Pre-commit hooks available via `pre-commit install` (ruff + hygiene checks).
