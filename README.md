# PlugPulse

> Community-verified EV charger reliability — the open trust layer on top of the map.

PlugPulse doesn't just show you where EV chargers are; it tells you whether they
**actually work right now**, using one-tap reports from the community with a
freshness-weighted reliability score. Built entirely on open data and open source,
so the whole ecosystem can reuse it.

## Why

Finding chargers is a solved problem — closed aggregators cover it. **Trusting** them
isn't. Apps show stale "availability" from operator feeds, so drivers arrive at
chargers that are broken, occupied, or blocked. No one owns an open, real-time,
community-verified source of truth. PlugPulse is that layer.

See [`PlugPulse-Project-Spec.md`](./PlugPulse-Project-Spec.md) for the full design.

New here? The [Handbook](./docs/handbook/README.md) explains the project and how to
deploy it in plain language, chapter by chapter.

## Stack

| Layer | Tech | Notes |
|---|---|---|
| Frontend | SvelteKit + TypeScript (PWA) | MapLibre GL for the map |
| Map tiles | OpenFreeMap | No API key, no limits |
| Charger data | Open Charge Map API | Real global stations |
| Backend | FastAPI (Python 3.12) | Reliability scoring + API |
| Database | PostgreSQL + PostGIS | Geo queries (GIST spatial index) |
| Cache | Redis (optional) | Warm reliability scores |
| Packaging | Docker + docker-compose | One-command self-host |

## Quick start (development)

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload      # http://localhost:8000/health

# Frontend
cd frontend
npm install
npm run dev                         # http://localhost:5173

# Or run everything with Docker
docker compose up --build
```

## Running checks (same as CI)

```bash
# Backend
cd backend && ruff check . && ruff format --check . && mypy app && pytest

# Frontend
cd frontend && npm run lint && npm run test && npm run build
```

## Performance

PlugPulse is map-first and built for the open web. Speed targets and the strategy
that keeps us inside them (spatial indexing, viewport-only loading, debounced fetches,
caching) are documented in [`PERFORMANCE.md`](./PERFORMANCE.md).

## Discoverability (SEO & AI SEO)

How PlugPulse gets found by both search engines and generative engines (ChatGPT, Claude,
Perplexity, Gemini) — server-side rendering, structured data, `robots.txt` AI-crawler
rules, and `llms.txt` — is documented in [`SEO.md`](./SEO.md). Reusable meta-tag and
JSON-LD helpers live in [`frontend/src/lib/seo.ts`](./frontend/src/lib/seo.ts).

## Contributing

PRs welcome — please read [`CONTRIBUTING.md`](./CONTRIBUTING.md) first. Every PR runs
lint, type-check, tests, and security scanning before it can merge.

## License

Source code is licensed under **AGPL-3.0** (see [`LICENSE`](./LICENSE)).
Community-contributed reliability data is **CC BY-SA 4.0**.
Data-source attributions are in [`ATTRIBUTION.md`](./ATTRIBUTION.md) and must be preserved.
