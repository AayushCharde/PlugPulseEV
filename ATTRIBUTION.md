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

## Our own contributions

Reliability reports contributed by PlugPulse users are released under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), and where possible
are also submitted back upstream to Open Charge Map as check-ins / fault reports.
