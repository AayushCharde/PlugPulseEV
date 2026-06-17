<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import { describeReliability, evidenceLine } from "$lib/reliability";
  import type { Station } from "$lib/stations";

  export let station: Station;

  const dispatch = createEventDispatcher<{ close: void }>();

  $: display = describeReliability(station.reliability);
  $: evidence = evidenceLine(station.reliability);
  $: sourceLabel = station.source === "osm" ? "© OpenStreetMap" : "Open Charge Map";

  function onKeydown(e: KeyboardEvent): void {
    if (e.key === "Escape") dispatch("close");
  }
</script>

<svelte:window on:keydown={onKeydown} />

<aside class="panel" role="dialog" aria-label="Station details">
  <img
    class="banner"
    src="/img/ev-charger.webp"
    alt=""
    width="360"
    height="150"
    loading="lazy"
    decoding="async"
  />
  <button class="close btn-icon" on:click={() => dispatch("close")} aria-label="Close details">
    ✕
  </button>

  <div class="body">
    <h2>{station.name ?? "Unnamed station"}</h2>

    <p class="reliability">
      <span class="dot" style="background: var(--rel-{display.color})"></span>
      <strong>{display.text}</strong>
      <span class="muted">· {evidence}</span>
    </p>

    <dl>
      {#if station.operator}
        <dt>Operator</dt>
        <dd>{station.operator}</dd>
      {/if}
      <dt>Max power</dt>
      <dd>{station.max_power_kw ? `${station.max_power_kw} kW` : "Unknown"}</dd>
      {#if station.access_type}
        <dt>Access</dt>
        <dd>{station.access_type}</dd>
      {/if}
      {#if station.connectors.length}
        <dt>Connectors</dt>
        <dd class="chips">
          {#each station.connectors as connector}
            <span class="chip">{connector}</span>
          {/each}
        </dd>
      {/if}
    </dl>

    <p class="source muted">Source: {sourceLabel}</p>
  </div>
</aside>

<style>
  .panel {
    position: fixed;
    top: 72px;
    right: 16px;
    z-index: 9;
    width: min(360px, calc(100vw - 32px));
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r-lg);
    box-shadow: var(--shadow-lg);
    overflow: hidden;
  }
  .banner {
    display: block;
    width: 100%;
    height: 150px;
    object-fit: cover;
    background: var(--surface-2);
  }
  .close {
    position: absolute;
    top: 10px;
    right: 10px;
    background: color-mix(in srgb, var(--surface) 70%, transparent);
    backdrop-filter: blur(4px);
  }
  .body {
    padding: 16px;
  }
  h2 {
    font-size: 1.15rem;
    margin: 0 0 8px;
  }
  .reliability {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 0 0 12px;
  }
  .muted {
    color: var(--text-muted);
  }
  .source {
    margin: 12px 0 0;
    font-size: 0.78rem;
  }
  dl {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 6px 14px;
    margin: 0;
    font-size: 0.92rem;
  }
  dt {
    color: var(--text-muted);
  }
  dd {
    margin: 0;
  }
  .chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }
  .chip {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 2px 10px;
    font-size: 0.82rem;
  }
  @media (max-width: 520px) {
    .panel {
      top: auto;
      right: 0;
      left: 0;
      bottom: 0;
      width: 100%;
      border-radius: var(--r-lg) var(--r-lg) 0 0;
    }
  }
</style>
