# Performance

PlugPulse is map-first and meant for the open web, including phones on patchy
connections at a charger. Speed is a feature. This doc states the budgets and the
strategy that keeps us inside them. PRs that risk a budget should say so.

## Budgets (targets, measured on a mid-range phone / 4G)

| Metric | Budget |
|---|---|
| `/stations` API response (warm cache) | < 100 ms server time |
| `/stations` API response (cold) | < 300 ms server time |
| Station payload per viewport | < 150 KB gzipped |
| First Contentful Paint | < 1.8 s |
| Largest Contentful Paint | < 2.5 s |
| Time to Interactive | < 3.5 s |
| Initial JS bundle (gzipped) | < 200 KB |
| Map interaction (pan/zoom) | 60 fps, no jank |

## Backend strategy

- **Spatial index.** Stations are stored as PostGIS `geography` with a GIST index
  (`stations_geom_gix`). Viewport queries are an indexed `ST_Intersects` against the
  bounding box — never a full scan. This is the single biggest win.
- **Bounded results.** Every station query is a bbox + a hard `limit`
  (`MAX_STATIONS_PER_REQUEST`, default 300). We never return the whole dataset; at low
  zoom we cluster server-side rather than ship thousands of points.
- **Local cache of OCM data.** Charging stations are synced from Open Charge Map into
  our own table on a schedule. The hot path never calls the upstream API.
- **Reliability score caching.** Computed scores are cached in Redis with a short TTL
  (`RELIABILITY_CACHE_TTL`, default 60 s). Cache is optional — absence just means more
  DB reads, never a failure.
- **Recent-only scoring.** Scoring reads only reports inside `RELIABILITY_LOOKBACK_HOURS`
  (default 24), served by the `reports_station_recent_idx` composite index.
- **Connection pooling.** asyncpg pool sized via `DB_POOL_MIN_SIZE` / `DB_POOL_MAX_SIZE`.
- **Compression.** gzip middleware on JSON responses (≈70-80% smaller over the wire).
- **Async everywhere.** FastAPI async handlers + asyncpg so slow I/O never blocks.

## Frontend strategy

- **Viewport-only loading.** The client requests just the visible bounding box
  (`stationsUrl`), refetching when the map settles.
- **Debounced fetches.** Map move/zoom events are debounced (`debounce`) so we make one
  request when the user stops, not dozens mid-gesture.
- **Marker clustering.** Cluster markers at low zoom to keep the DOM/canvas light and
  interactions at 60 fps.
- **Vector tiles.** MapLibre + OpenFreeMap vector tiles render client-side and zoom
  smoothly without re-downloading raster images.
- **PWA + service worker.** Cache the app shell and last-seen station data so the map is
  usable offline / on a weak signal at the charger.
- **Code splitting + lazy load.** Defer non-critical UI (trip planner, photo viewer).
- **No layout thrash.** Update marker sources, don't recreate the map or re-render all
  markers on every state change.

## Data transfer

- Return only the fields the map needs (id, position, power, connector, score) — detail
  fields are fetched lazily when a station is opened.
- Serve static assets and tiles over a CDN with long cache lifetimes.

## CI performance gates (to add once the UI exists)

These are intentionally not wired up yet (there's no UI to measure). Add them with the
first real frontend PR:

- **Bundle-size check** (e.g. `size-limit`) failing the build if the JS budget is exceeded.
- **Lighthouse CI** on a preview deploy, asserting the FCP/LCP/TTI budgets above.
- **API smoke/load test** (e.g. `k6`) asserting the `/stations` latency budget.
