# PlugPulse — Project Specification

> *Working name. An open-source, community-verified EV charging reliability map and trip planner.*

---

## 1. One-line pitch

A free, open-source app that doesn't just show you where EV chargers are — it tells you whether they actually **work right now**, using one-tap reports from the community, built entirely on open data so anyone can reuse it.

---

## 2. The problem (researched)

EV charger **location** is now a solved problem in India. Closed aggregators already cover it well:

- **eHUB by MG** lists 22,500+ charging points across 40 charge-point operators (Jio-bp, Tata Power, Shell, ChargeZone, BPCL, etc.), works for MG *and* non-MG cars, and already has trip planning, reviews, and CarPlay/Android Auto.
- **Bolt.Earth** runs India's largest single network with 30,000+ points, QR-code session start, wallet payments, and a peer-to-peer host model.

Cloning that is pointless — you can't match their operator partnerships as a solo developer, and the map itself is a commodity now.

**What is still broken:**

1. **Trust, not location.** Aggregators show "availability" pulled from each operator's own feed, which is notoriously stale or wrong. Drivers routinely arrive to find a charger that the app called "available" is actually broken, offline, ICE-blocked (a petrol car parked in the bay), or occupied with a long queue. Reviews/ratings describe a station's *overall* quality — not its *live* status.
2. **Everything is closed.** No source code, no open dataset, no community ownership. Every app privately rebuilds the same map, and none of the reliability knowledge flows back to a commons.
3. **No open reliability layer exists anywhere.** This is the structural gap. Closed apps *won't* build it, because their value is the walled garden.

**Problem statement:**
> EV drivers can find chargers but cannot trust them. There is no open, real-time, community-verified source of truth for whether a given charger is actually working — and no open dataset anyone can build on.

---

## 3. The solution

PlugPulse is the **trust layer on top of the map** — think "Waze for EV charger reliability," or "OpenStreetMap applied to charger status."

It starts with real charger locations from open data, then layers community-reported live status on top, with a freshness-weighted confidence score. Reports flow *back* into the open commons so the whole ecosystem improves.

This is differentiated, buildable solo, fully open, and solves a pain even the largest commercial app hasn't cracked.

### What makes it distinct from eHUB / Bolt.Earth

| | eHUB / Bolt.Earth | PlugPulse |
|---|---|---|
| Core value | Find + pay across networks | Trust: is it working *now*? |
| Source | Closed operator feeds | Open data + crowd verification |
| Code | Proprietary | Open source (AGPL-3.0) |
| Data | Locked in | Open, reusable, contributed back |
| Status info | Operator-reported "availability" | Community-verified, freshness-scored |
| Reach | India-only | Global (OCM is worldwide) |

---

## 4. Core features

### MVP (build this first)

1. **Cross-network charger map** — all chargers from Open Charge Map, rendered with MapLibre + OpenFreeMap tiles. Filter by connector type, power (slow / fast / rapid), and access type.
2. **One-tap live status reports** — at any station: `Working` / `Broken` / `Occupied` / `ICE-blocked`. The headline feature.
3. **Freshness-weighted reliability score** — e.g. "Likely working — 4 confirmations in the last 90 min." Old reports decay; recent ones dominate (see §7).
4. **Station detail panel** — connectors, power, operator, access notes, recent reports timeline, and photos.
5. **Personal garage** — save your EV model + connector; the map auto-filters to compatible chargers.
6. **Offline-capable PWA** — installs to a phone home screen and still shows the last-loaded map/reports when signal is poor at a charger.

### Phase 2

7. **Trip planner** — start + destination + range; suggests charging stops along the route (OpenRouteService / OSRM), preferring high-reliability stations.
8. **"Actual vs rated power"** reports — users log the kW they really got, exposing chargers that under-deliver.
9. **Queue / wait-time reports** — "2 cars ahead, ~20 min."
10. **Contribute upstream** — push verified reports back to Open Charge Map as check-ins/fault reports, enriching the global commons.
11. **Open public API** — let others consume the reliability layer (the OpenStreetMap philosophy).

---

## 5. The open stack (verified — zero paid API keys)

Everything below is free and open; nothing requires a billing account.

| Layer | Choice | License / cost | Why |
|---|---|---|---|
| Charger data | **Open Charge Map API** | Free key; crowd data is CC BY-SA 4.0 | Real global stations; supports reading *and* submitting comments/check-ins, incl. a "Fault Report" category |
| Map rendering | **MapLibre GL JS** | BSD (open source) | Community fork of Mapbox GL, fully free |
| Map tiles | **OpenFreeMap** | MIT; OSM data; **no API key, no limits, no cookies** | Removes the usual map-billing trap entirely |
| Geocoding (search) | **Nominatim** (OSM) | Open | Address/place search without Google |
| Routing (Phase 2) | **OpenRouteService** (free key) or self-hosted **OSRM/Valhalla** | Open | Trip planning with charging stops |
| Frontend | **SvelteKit** or **Next.js** (PWA) | Open | Pick one; SvelteKit is lighter, Next.js more familiar |
| Backend | **FastAPI** (Python) or **Node/Express** | Open | Hosts the reliability layer + API |
| Database | **PostgreSQL + PostGIS** | Open | Geo queries ("reports near this point") |
| Cache | **Redis** (optional) | Open | Fast reads of hot stations |
| Packaging | **Docker + docker-compose** | Open | One-command self-hosting |

> **Why a backend at all if OCM has the data?** OCM stores stations and slow-moving check-ins. PlugPulse's value is the *fast, freshness-scored live layer* — that needs your own store so scoring is instant and you control the UX, then you sync notable reports back to OCM.

---

## 6. Architecture

```
                ┌─────────────────────────────┐
                │   PlugPulse PWA (frontend)  │
                │  MapLibre + OpenFreeMap UI  │
                └──────────────┬──────────────┘
                               │ HTTPS / JSON
                ┌──────────────▼──────────────┐
                │      PlugPulse Backend       │
                │   FastAPI / Node + REST API  │
                │  - reliability scoring       │
                │  - report ingest + validate  │
                │  - station cache             │
                └───────┬───────────────┬─────┘
                        │               │
          ┌─────────────▼───┐   ┌───────▼───────────┐
          │ PostgreSQL +    │   │ Open Charge Map   │
          │ PostGIS         │   │ API (stations +   │
          │ (reports, users,│   │ upstream sync)    │
          │ cached stations)│   └───────────────────┘
          └─────────────────┘
                        │
                  ┌─────▼─────┐
                  │  Redis    │ (optional hot cache)
                  └───────────┘
```

Data flow for the core loop:

1. Frontend asks backend for stations in the current map bounds.
2. Backend returns OCM stations **joined with** the live reliability score from PostGIS.
3. User taps a status (`Working`/`Broken`/etc.); frontend POSTs it to the backend.
4. Backend stores the report, recomputes the station's score, and (Phase 2) forwards it to OCM as a check-in.

---

## 7. The reliability score (the core IP)

This is the heart of the product. A simple, defensible model:

**Each report has a decaying weight.** A report's influence halves every *H* hours (start with H = 3). So a report's weight is:

```
weight = 0.5 ^ (age_in_hours / H)
```

**Score = weighted balance of positive vs negative reports:**

```
positive = sum(weight) for Working reports
negative = sum(weight) for Broken / ICE-blocked reports
confidence = positive + negative          # how much recent signal exists
status_score = positive / (positive + negative)   # 0..1
```

**Translate to a human label:**

| Conditions | Label |
|---|---|
| confidence < 0.5 | "No recent reports" (fall back to OCM operator status) |
| status_score ≥ 0.7 | "Likely working" (green) |
| 0.4–0.7 | "Mixed reports" (amber) |
| < 0.4 | "Likely down" (red) |

Always show the evidence: *"4 confirmations in the last 90 min."* Trust comes from transparency, not a black box.

**Anti-abuse (important):** rate-limit reports per user per station per hour; require a rough geofence match (the reporter should be near the station); weight reports from accounts with a track record slightly higher. Keep it light at MVP, harden later.

---

## 8. Data model (starting schema)

```
users
  id, handle, created_at, trust_score

stations            -- cached from OCM, refreshed periodically
  id (ocm_id), name, lat, lng, operator,
  connectors (jsonb), max_power_kw, access_type,
  last_synced_at

reports
  id, station_id -> stations.id, user_id -> users.id,
  status ENUM('working','broken','occupied','ice_blocked'),
  actual_power_kw (nullable), note (nullable),
  lat, lng,                 -- reporter location for geofence check
  created_at

photos
  id, station_id, user_id, url, created_at

-- reliability score is computed on read (or cached in Redis),
-- not stored as a stale column
```

PostGIS adds a spatial index on `stations(lat,lng)` so "stations in this map view" is fast.

---

## 9. Licensing plan

- **Source code:** **AGPL-3.0.** Because this is a community-data project, AGPL forces anyone who *hosts* a modified version to also publish their changes — keeping forks open. (Use **MIT/Apache-2.0** instead only if you'd rather maximize commercial reuse over keeping forks open.)
- **Your community-contributed reliability data:** publish under **CC BY-SA 4.0** (matches OCM, keeps it a true commons).
- **Mandatory attributions (do not skip — these are license conditions):**
  - Open Charge Map data + per-operator attribution, visible to the end user.
  - "OpenFreeMap © OpenMapTiles Data from OpenStreetMap" (MapLibre adds this automatically).
- Ship a clear `LICENSE`, `README.md`, `CONTRIBUTING.md`, and `ATTRIBUTION.md`.

---

## 10. Build roadmap

**Phase 0 — Setup (week 1)**
Repo, license, README, docker-compose skeleton, OCM API key, "hello map" with MapLibre + OpenFreeMap centered on the user.

**Phase 1 — Read-only map (weeks 2–3)**
Fetch OCM stations for map bounds, render markers, build the station detail panel, filters (connector / power / access).

**Phase 2 — The reliability layer (weeks 4–6)**
Backend + PostGIS, report endpoints, one-tap status UI, the scoring function (§7), the freshness-weighted label on markers and detail panel. **This is the MVP that proves the idea.**

**Phase 3 — Polish + PWA (weeks 7–8)**
Personal garage, offline caching, install prompt, photos, basic anti-abuse, great empty/loading states.

**Phase 4 — Give back + grow (later)**
Sync reports upstream to OCM, public read API, trip planner with reliability-aware routing.

---

## 11. Why this is a strong project

- **Real, validated problem** the biggest commercial apps haven't solved.
- **Genuinely open** end-to-end: open code, open data, open map, no paid keys, self-hostable.
- **Scoped for one person** — the MVP is a map + a report button + a scoring function.
- **Portfolio gold** — geo queries, PWA/offline, a real algorithm, and a clear product story.
- **Network-effect potential** — every report makes it more useful, and contributing back to OCM means you're improving a global commons, not a silo.

---

*Next step suggestion: build the core screen (map + station detail + the live reliability widget) as an interactive prototype to lock in the "great UI" before wiring real data.*
