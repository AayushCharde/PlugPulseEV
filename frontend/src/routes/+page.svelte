<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import "maplibre-gl/dist/maplibre-gl.css";
  import type {
    Map as MapLibreMap,
    GeoJSONSource,
    ExpressionSpecification,
    MapLayerMouseEvent,
  } from "maplibre-gl";
  import { env } from "$env/dynamic/public";
  import { DEFAULT_STATION_LIMIT, resolveApiBase, type BBox, type StationQuery } from "$lib/api";
  import { debounce } from "$lib/debounce";
  import { reliabilityHex } from "$lib/reliability";
  import { currentTheme, type Theme } from "$lib/theme";
  import {
    fetchStations,
    minPowerForTier,
    stationsToFeatureCollection,
    type PowerTier,
    type Station,
  } from "$lib/stations";
  import StationDetail from "$lib/StationDetail.svelte";

  const apiBase = resolveApiBase(env.PUBLIC_API_BASE_URL);

  const DEFAULT_CENTER: [number, number] = [78.45, 17.4];
  const DEFAULT_ZOOM = 11;

  let mapContainer: HTMLDivElement;
  let map: MapLibreMap | undefined;
  let inFlight: AbortController | undefined;
  let themeObserver: MutationObserver | undefined;

  let stationsById = new Map<Station["id"], Station>();
  let selectedStation: Station | undefined;
  let loadError: string | undefined;
  let loading = false;
  let loaded = false; // true after the first successful load

  $: showEmpty = loaded && !loading && !loadError && stationsById.size === 0;

  // Filters — changing either re-queries immediately.
  let connector = "";
  let powerTier: PowerTier = "any";

  const CONNECTORS = ["CCS (Type 2)", "Type 2", "CHAdeMO", "Type 1 (J1772)"];

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
      if (inFlight !== controller) return; // a newer request superseded this one
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

  onMount(() => {
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
        });
        m.addLayer({
          id: "station-circles",
          type: "circle",
          source: "stations",
          paint: {
            "circle-radius": ["interpolate", ["linear"], ["zoom"], 8, 4, 14, 8],
            "circle-color": colorExpr(currentTheme()),
            "circle-stroke-width": 1.5,
            "circle-stroke-color": "#ffffff",
          },
        });

        m.on("click", "station-circles", (e: MapLayerMouseEvent) => {
          const feature = e.features?.[0];
          if (!feature) return;
          const found = stationsById.get(feature.properties?.id);
          if (found) selectedStation = found;
        });
        m.on("mouseenter", "station-circles", () => {
          m.getCanvas().style.cursor = "pointer";
        });
        m.on("mouseleave", "station-circles", () => {
          m.getCanvas().style.cursor = "";
        });

        m.on("moveend", debouncedReload);
        void reload();
      });

      // Recenter on the user if allowed; otherwise keep the default view.
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (pos) => m.flyTo({ center: [pos.coords.longitude, pos.coords.latitude], zoom: 13 }),
          () => {},
          { enableHighAccuracy: true, timeout: 5000 },
        );
      }

      // Recolor circles when the user toggles the theme.
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

<div class="filters">
  <label>
    <span class="sr-only">Connector</span>
    <select class="field" bind:value={connector} on:change={() => void reload()}>
      <option value="">Any connector</option>
      {#each CONNECTORS as c}
        <option value={c}>{c}</option>
      {/each}
    </select>
  </label>
  <label>
    <span class="sr-only">Power</span>
    <select class="field" bind:value={powerTier} on:change={() => void reload()}>
      <option value="any">Any power</option>
      <option value="fast">Fast (≥22 kW)</option>
      <option value="rapid">Rapid (≥50 kW)</option>
    </select>
  </label>
</div>

{#if loading}
  <div class="loading-pill" role="status">Loading chargers…</div>
{/if}

{#if loadError}
  <div class="toast" role="alert">{loadError}</div>
{/if}

{#if showEmpty}
  <div class="empty" role="status">
    <img src="/img/ev-charger.webp" alt="" width="320" height="120" loading="lazy" decoding="async" />
    <div class="empty-body">
      <h2>No chargers in view</h2>
      <p>Try zooming out or panning to a populated area — chargers load automatically as you move the map.</p>
    </div>
  </div>
{/if}

{#if selectedStation}
  <StationDetail station={selectedStation} on:close={() => (selectedStation = undefined)} />
{/if}

<style>
  .map {
    position: absolute;
    inset: 0;
  }
  /* Keep MapLibre's controls clear of the floating header. */
  :global(.maplibregl-ctrl-top-right),
  :global(.maplibregl-ctrl-top-left) {
    top: 64px;
  }
  .filters {
    position: fixed;
    top: 68px;
    left: 16px;
    z-index: 8;
    display: flex;
    gap: 8px;
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
  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip: rect(0 0 0 0);
    white-space: nowrap;
  }
  .loading-pill {
    position: fixed;
    top: 68px;
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
  @media (max-width: 520px) {
    .empty img {
      width: 84px;
      height: 84px;
    }
  }
</style>
