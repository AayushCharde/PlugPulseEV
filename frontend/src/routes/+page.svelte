<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import "maplibre-gl/dist/maplibre-gl.css";
  import type { Map as MapLibreMap } from "maplibre-gl";

  // Phase 0 "hello map": a full-screen MapLibre map on free OpenFreeMap tiles
  // (no API key, no usage limits). Real station markers arrive once the
  // backend /stations bbox endpoint lands.

  let mapContainer: HTMLDivElement;
  let map: MapLibreMap | undefined;

  // Fallback view if geolocation is denied/unavailable. Roughly Hyderabad —
  // the same region the API unit tests exercise.
  const DEFAULT_CENTER: [number, number] = [78.45, 17.4];
  const DEFAULT_ZOOM = 11;

  onMount(() => {
    // Dynamic import keeps MapLibre out of the SSR bundle (it touches `window`).
    void (async () => {
      const { Map, NavigationControl, GeolocateControl } = await import("maplibre-gl");

      map = new Map({
        container: mapContainer,
        // OpenFreeMap "liberty" style — MIT, OSM data, no key required.
        style: "https://tiles.openfreemap.org/styles/liberty",
        center: DEFAULT_CENTER,
        zoom: DEFAULT_ZOOM,
      });

      map.addControl(new NavigationControl(), "top-right");
      map.addControl(
        new GeolocateControl({
          positionOptions: { enableHighAccuracy: true },
          trackUserLocation: true,
        }),
        "top-right",
      );

      // Recenter on the user if they allow it; otherwise keep the default view.
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (pos) => {
            map?.flyTo({
              center: [pos.coords.longitude, pos.coords.latitude],
              zoom: 13,
            });
          },
          () => {
            // Permission denied or timed out — the default center stays.
          },
          { enableHighAccuracy: true, timeout: 5000 },
        );
      }
    })();
  });

  onDestroy(() => {
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

<style>
  :global(html),
  :global(body) {
    margin: 0;
    height: 100%;
  }

  .map {
    position: absolute;
    inset: 0;
  }
</style>
