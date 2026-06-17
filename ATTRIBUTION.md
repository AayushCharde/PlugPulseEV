# Attribution

PlugPulse is built on open data and open-source tooling. The attributions below are
**license conditions** — they must remain visible to end users in any deployment.

## Charging station data — Open Charge Map

Charging location data is provided by [Open Charge Map](https://openchargemap.org),
a non-profit, community-maintained open registry of EV charging locations.

- Community-contributed data is licensed under
  [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
- Each charging location may carry an additional per-operator / per-data-provider
  attribution, which must be shown to the end user where applicable.
- We request only open data via the `opendata=true` API parameter where possible.

## Charging station data — OpenStreetMap

Charging locations are also sourced from [OpenStreetMap](https://www.openstreetmap.org)
(`amenity=charging_station`), in addition to Open Charge Map.

- OSM data is licensed under the [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/).
- Attribution **© OpenStreetMap contributors** must remain visible to end users
  (the station detail panel shows the source per station).
- ODbL share-alike applies to any **redistributed derived database**, not to the
  application's source code (which is AGPL-3.0).

## Map tiles — OpenFreeMap & OpenStreetMap

Base map tiles are served by [OpenFreeMap](https://openfreemap.org) using
[OpenMapTiles](https://openmaptiles.org) schema and
[OpenStreetMap](https://www.openstreetmap.org) data.

Required attribution string:

> OpenFreeMap © OpenMapTiles Data from OpenStreetMap

(When using MapLibre GL, this attribution is added automatically.)

## Routing (Phase 2) — OpenRouteService / OSRM

Trip routing uses [OpenRouteService](https://openrouteservice.org) or a self-hosted
[OSRM](https://project-osrm.org) / [Valhalla](https://github.com/valhalla/valhalla)
instance, all built on OpenStreetMap data.

## Photography — Unsplash

Decorative imagery is from [Unsplash](https://unsplash.com) under the
[Unsplash License](https://unsplash.com/license) (free for commercial use; attribution
not required but credited here). Images are downloaded and self-hosted (`frontend/static/img/`).

- `ev-charger.webp` — photo by [Mohamed B.](https://unsplash.com/@bangscreative) on Unsplash.

## Our own contributions

Reliability reports contributed by PlugPulse users are released under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), and where possible
are also submitted back upstream to Open Charge Map as check-ins / fault reports.
