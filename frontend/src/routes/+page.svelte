<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import "maplibre-gl/dist/maplibre-gl.css";
  import type {
    Map as MapLibreMap,
    GeoJSONSource,
    ExpressionSpecification,
    FilterSpecification,
    MapLayerMouseEvent,
  } from "maplibre-gl";
  import { env } from "$env/dynamic/public";
  import { DEFAULT_STATION_LIMIT, resolveApiBase, type BBox, type StationQuery } from "$lib/api";
  import { debounce } from "$lib/debounce";
  import { reliabilityHex } from "$lib/reliability";
  import { currentTheme, type Theme } from "$lib/theme";
  import { geocode } from "$lib/geocode";
  import {
    fetchStations,
    minPowerForTier,
    stationsToFeatureCollection,
    type PowerTier,
    type Station,
  } from "$lib/stations";
  import StationDetail from "$lib/StationDetail.svelte";
  import Legend from "$lib/Legend.svelte";

  const apiBase = resolveApiBase(env.PUBLIC_API_BASE_URL);
  const DEFAULT_CENTER: [number, number] = [78.45, 17.4];
  const DEFAULT_ZOOM = 11;

  let mapContainer: HTMLDivElement;
  let map: MapLibreMap | undefined;
  let mapReady = false;
  let inFlight: AbortController | undefined;
  let themeObserver: MutationObserver | undefined;

  let stationsById = new Map<Station["id"], Station>();
  let selectedStation: Station | undefined;
  let loadError: string | undefined;
  let loading = false;
  let loaded = false;

  let connector = "";
  let powerTier: PowerTier = "any";
  const CONNECTORS = ["CCS (Type 2)", "Type 2", "CHAdeMO", "Type 1 (J1772)"];

  let searchQuery = "";
  let searchBusy = false;
  let searchCtl: AbortController | undefined;

  let showWelcome = false;

  $: showEmpty = loaded && !loading && !loadError && stationsById.size === 0;
  // Highlight the selected charger on the map (clears when none selected).
  $: if (map && mapReady) {
    const filter: FilterSpecification = selectedStation
      ? ["==", ["get", "id"], selectedStation.id]
      : ["==", ["get", "id"], "__none__"];
    map.setFilter("station-selected", filter);
  }

  function colorExpr(theme: Theme): ExpressionSpecification {
    return [
      "match",
      ["get", "reliabilityLabel"],
      "likely_working",
      reliabilityHex("likely_working", theme),
      "mixed",
      reliabilityHex("mixed", theme),
      "likely_down",
      reliabilityHex("likely_down", theme),
      reliabilityHex("unknown", theme),
    ] as unknown as ExpressionSpecification;
  }

  function bboxFromMap(m: MapLibreMap): BBox {
    const b = m.getBounds();
    return { west: b.getWest(), south: b.getSouth(), east: b.getEast(), north: b.getNorth() };
  }

  async function reload(): Promise<void> {
    if (!map) return;
    inFlight?.abort();
    const controller = new AbortController();
    inFlight = controller;
    const query: StationQuery = {
      bbox: bboxFromMap(map),
      connector: connector || undefined,
      minPowerKw: minPowerForTier(powerTier),
      limit: DEFAULT_STATION_LIMIT,
    };
    loading = true;
    try {
      const stations = await fetchStations(apiBase, query, fetch, controller.signal);
      if (inFlight !== controller) return;
      stationsById = new Map(stations.map((s) => [s.id, s]));
      const source = map.getSource("stations") as GeoJSONSource | undefined;
      source?.setData(stationsToFeatureCollection(stations));
      loadError = undefined;
      loaded = true;
    } catch (err) {
      if ((err as DOMException)?.name === "AbortError" || inFlight !== controller) return;
      loadError = err instanceof Error ? err.message : "Failed to load stations";
      loaded = true;
    } finally {
      if (inFlight === controller) loading = false;
    }
  }

  const debouncedReload = debounce(() => void reload(), 350);

  async function onSearch(e: Event): Promise<void> {
    e.preventDefault();
    if (!searchQuery.trim() || !map) return;
    searchCtl?.abort();
    const c = new AbortController();
    searchCtl = c;
    searchBusy = true;
    try {
      const results = await geocode(searchQuery, fetch, c.signal);
      if (searchCtl === c && results[0]) {
        map.flyTo({ center: [results[0].lng, results[0].lat], zoom: 13 });
      }
    } catch {
      /* ignore search errors */
    } finally {
      if (searchCtl === c) searchBusy = false;
    }
  }

  function dismissWelcome(): void {
    showWelcome = false;
    try {
      localStorage.setItem("pp-welcomed", "1");
    } catch {
      /* ignore */
    }
  }

  onMount(() => {
    try {
      showWelcome = !localStorage.getItem("pp-welcomed");
    } catch {
      /* ignore */
    }

    void (async () => {
      const { Map, NavigationControl, GeolocateControl } = await import("maplibre-gl");
      const m = new Map({
        container: mapContainer,
        style: "https://tiles.openfreemap.org/styles/liberty",
        center: DEFAULT_CENTER,
        zoom: DEFAULT_ZOOM,
      });
      map = m;
      m.addControl(new NavigationControl(), "top-right");
      m.addControl(
        new GeolocateControl({
          positionOptions: { enableHighAccuracy: true },
          trackUserLocation: true,
        }),
        "top-right",
      );

      m.on("load", () => {
        m.addSource("stations", {
          type: "geojson",
          data: { type: "FeatureCollection", features: [] },
          cluster: true,
          clusterRadius: 50,
          clusterMaxZoom: 13,
        });

        // Cluster bubbles (zoomed out).
        m.addLayer({
          id: "clusters",
          type: "circle",
          source: "stations",
          filter: ["has", "point_count"],
          paint: {
            "circle-color": ["step", ["get", "point_count"], "#86efac", 10, "#4ade80", 50, "#22c55e"],
            "circle-radius": ["step", ["get", "point_count"], 15, 10, 19, 50, 25],
            "circle-stroke-width": 2,
            "circle-stroke-color": "#ffffff",
          },
        });
        m.addLayer({
          id: "cluster-count",
          type: "symbol",
          source: "stations",
          filter: ["has", "point_count"],
          layout: {
            "text-field": ["get", "point_count_abbreviated"],
            "text-font": ["Noto Sans Bold"],
            "text-size": 12,
          },
          paint: { "text-color": "#06310f" },
        });

        // Individual chargers, colored by reliability.
        m.addLayer({
          id: "station-circles",
          type: "circle",
          source: "stations",
          filter: ["!", ["has", "point_count"]],
          paint: {
            "circle-radius": ["interpolate", ["linear"], ["zoom"], 8, 4, 14, 8],
            "circle-color": colorExpr(currentTheme()),
            "circle-stroke-width": 1.5,
            "circle-stroke-color": "#ffffff",
          },
        });
        // Selected-charger highlight ring (filtered to the selected id).
        m.addLayer({
          id: "station-selected",
          type: "circle",
          source: "stations",
          filter: ["==", ["get", "id"], "__none__"],
          paint: {
            "circle-radius": ["interpolate", ["linear"], ["zoom"], 8, 9, 14, 14],
            "circle-color": "rgba(132,204,22,0.18)",
            "circle-stroke-width": 3,
            "circle-stroke-color": "#84cc16",
          },
        });

        m.on("click", "clusters", (e: MapLayerMouseEvent) => {
          const f = e.features?.[0];
          if (!f) return;
          const clusterId = f.properties?.cluster_id as number;
          const src = m.getSource("stations") as GeoJSONSource;
          void src.getClusterExpansionZoom(clusterId).then((zoom) => {
            const geom = f.geometry;
            if (geom.type === "Point") {
              m.easeTo({ center: geom.coordinates as [number, number], zoom });
            }
          });
        });
        m.on("click", "station-circles", (e: MapLayerMouseEvent) => {
          const found = stationsById.get(e.features?.[0]?.properties?.id);
          if (found) selectedStation = found;
        });
        for (const layer of ["clusters", "station-circles"]) {
          m.on("mouseenter", layer, () => (m.getCanvas().style.cursor = "pointer"));
          m.on("mouseleave", layer, () => (m.getCanvas().style.cursor = ""));
        }

        mapReady = true;
        m.on("moveend", debouncedReload);
        void reload();
      });

      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (pos) => m.flyTo({ center: [pos.coords.longitude, pos.coords.latitude], zoom: 13 }),
          () => {},
          { enableHighAccuracy: true, timeout: 5000 },
        );
      }

      themeObserver = new MutationObserver(() => {
        if (map?.getLayer("station-circles")) {
          map.setPaintProperty("station-circles", "circle-color", colorExpr(currentTheme()));
        }
      });
      themeObserver.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ["data-theme"],
      });
    })();
  });

  onDestroy(() => {
    inFlight?.abort();
    searchCtl?.abort();
    themeObserver?.disconnect();
    map?.remove();
  });
</script>

<svelte:head>
  <title>PlugPulse — find EV chargers that actually work</title>
  <meta
    name="description"
    content="Community-verified EV charger reliability on an open map. See whether a charger actually works right now."
  />
</svelte:head>

<div class="map" bind:this={mapContainer}></div>

<div class="controls">
  <form class="search" on:submit={onSearch}>
    <input
      class="field"
      type="search"
      placeholder="Search a city or place…"
      bind:value={searchQuery}
      aria-label="Search for a place"
    />
    <button class="btn btn-primary" type="submit" disabled={searchBusy}>
      {searchBusy ? "…" : "Go"}
    </button>
  </form>
  <div class="filters">
    <select class="field" bind:value={connector} on:change={() => void reload()} aria-label="Connector">
      <option value="">Any connector</option>
      {#each CONNECTORS as c}<option value={c}>{c}</option>{/each}
    </select>
    <select class="field" bind:value={powerTier} on:change={() => void reload()} aria-label="Power">
      <option value="any">Any power</option>
      <option value="fast">Fast (≥22 kW)</option>
      <option value="rapid">Rapid (≥50 kW)</option>
    </select>
  </div>
</div>

<Legend />

{#if loading}<div class="loading-pill" role="status">Loading chargers…</div>{/if}
{#if loadError}<div class="toast" role="alert">{loadError}</div>{/if}

{#if showEmpty}
  <div class="empty" role="status">
    <img src="/img/ev-charger.webp" alt="" width="320" height="120" loading="lazy" decoding="async" />
    <div class="empty-body">
      <h2>No chargers in view</h2>
      <p>Try zooming out, searching a city, or panning to a populated area.</p>
    </div>
  </div>
{/if}

{#if selectedStation}
  <StationDetail station={selectedStation} on:close={() => (selectedStation = undefined)} />
{/if}

{#if showWelcome}
  <div class="welcome-backdrop" role="dialog" aria-label="Welcome to PlugPulse">
    <div class="welcome">
      <img src="/img/ev-charger.webp" alt="" width="420" height="150" loading="eager" decoding="async" />
      <div class="welcome-body">
        <h2>⚡ Find chargers that actually work</h2>
        <p>
          PlugPulse shows EV chargers from open data (Open Charge Map + OpenStreetMap) with a
          community-verified reliability score. Browse the map, search a city, and tap a charger
          for details.
        </p>
        <button class="btn btn-primary" on:click={dismissWelcome}>Explore the map</button>
      </div>
    </div>
  </div>
{/if}

<style>
  .map {
    position: absolute;
    inset: 0;
  }
  :global(.maplibregl-ctrl-top-right) {
    top: 64px;
  }
  .controls {
    position: fixed;
    top: 68px;
    left: 16px;
    z-index: 8;
    display: flex;
    flex-direction: column;
    gap: 8px;
    width: min(320px, calc(100vw - 32px));
  }
  .search {
    display: flex;
    gap: 6px;
  }
  .search .field {
    flex: 1;
    box-shadow: var(--shadow-sm);
  }
  .filters {
    display: flex;
    gap: 8px;
  }
  .filters .field {
    flex: 1;
    box-shadow: var(--shadow-sm);
  }
  .toast {
    position: fixed;
    bottom: 16px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 9;
    background: var(--rel-red);
    color: #fff;
    padding: 8px 14px;
    border-radius: var(--r-md);
    box-shadow: var(--shadow-md);
  }
  .loading-pill {
    position: fixed;
    top: 132px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 8;
    background: color-mix(in srgb, var(--surface) 88%, transparent);
    backdrop-filter: blur(8px);
    border: 1px solid var(--border);
    color: var(--text-muted);
    padding: 6px 14px;
    border-radius: 999px;
    box-shadow: var(--shadow-sm);
    font-size: 0.85rem;
  }
  .empty {
    position: fixed;
    bottom: 24px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 8;
    width: min(420px, calc(100vw - 32px));
    display: flex;
    gap: 14px;
    align-items: center;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r-lg);
    box-shadow: var(--shadow-lg);
    overflow: hidden;
    padding-right: 14px;
  }
  .empty img {
    width: 110px;
    height: 110px;
    object-fit: cover;
    flex: none;
  }
  .empty-body {
    padding: 12px 0;
  }
  .empty-body h2 {
    font-size: 1rem;
    margin: 0 0 4px;
  }
  .empty-body p {
    margin: 0;
    font-size: 0.88rem;
    color: var(--text-muted);
  }
  .welcome-backdrop {
    position: fixed;
    inset: 0;
    z-index: 20;
    display: grid;
    place-items: center;
    padding: 16px;
    background: rgb(0 0 0 / 0.45);
    backdrop-filter: blur(2px);
  }
  .welcome {
    width: min(440px, 100%);
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r-lg);
    box-shadow: var(--shadow-lg);
    overflow: hidden;
  }
  .welcome img {
    width: 100%;
    height: 150px;
    object-fit: cover;
    display: block;
  }
  .welcome-body {
    padding: 18px 20px 20px;
  }
  .welcome-body h2 {
    margin: 0 0 8px;
    font-size: 1.2rem;
  }
  .welcome-body p {
    margin: 0 0 16px;
    color: var(--text-muted);
    font-size: 0.92rem;
  }
  @media (max-width: 520px) {
    .empty img {
      width: 84px;
      height: 84px;
    }
  }
</style>
