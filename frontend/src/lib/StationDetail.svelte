<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import { fly } from "svelte/transition";
  import { describeReliability, evidenceLine } from "$lib/reliability";
  import { sourceLabel, formatPower, formatCoords, directionsUrl, displayName } from "$lib/format";
  import type { Station } from "$lib/stations";

  export let station: Station;

  const dispatch = createEventDispatcher<{ close: void }>();

  $: display = describeReliability(station.reliability);
  $: evidence = evidenceLine(station.reliability);

  function onKeydown(e: KeyboardEvent): void {
    if (e.key === "Escape") dispatch("close");
  }
</script>

<svelte:window on:keydown={onKeydown} />

<aside class="panel" role="dialog" aria-label="Station details" transition:fly={{ y: 24, duration: 180 }}>
  <div class="banner">
    <img src="/img/ev-charger.webp" alt="" width="380" height="150" loading="lazy" decoding="async" />
    <div class="banner-grad"></div>
    <h2 class="title">{displayName(station)}</h2>
    <button class="close" on:click={() => dispatch("close")} aria-label="Close details">✕</button>
  </div>

  <div class="body">
    <span class="badge badge-{display.color}">
      <span class="dot"></span>{display.text}
    </span>
    <p class="evidence">{evidence}</p>

    <dl>
      <dt>Operator</dt>
      <dd>{station.operator ?? "Unknown"}</dd>

      <dt>Max power</dt>
      <dd>{formatPower(station.max_power_kw)}</dd>

      <dt>Access</dt>
      <dd>{station.access_type ?? "Unknown"}</dd>

      <dt>Connectors</dt>
      <dd>
        {#if station.connectors.length}
          <span class="chips">
            {#each station.connectors as connector}<span class="chip">{connector}</span>{/each}
          </span>
        {:else}
          <span class="muted">Not reported</span>
        {/if}
      </dd>
    </dl>

    <div class="actions">
      <a
        class="btn btn-primary"
        href={directionsUrl(station.lat, station.lng)}
        target="_blank"
        rel="noopener noreferrer"
      >
        ➜ Get directions
      </a>
      <button class="btn btn-ghost" disabled title="Community reports — coming soon">
        Report status
      </button>
    </div>

    <p class="meta muted">
      {sourceLabel(station.source)} · {formatCoords(station.lat, station.lng)}
    </p>
  </div>
</aside>

<style>
  .panel {
    position: fixed;
    top: 72px;
    right: 16px;
    z-index: 9;
    width: min(380px, calc(100vw - 32px));
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r-lg);
    box-shadow: var(--shadow-lg);
    overflow: hidden;
  }
  .banner {
    position: relative;
    height: 132px;
  }
  .banner img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    background: var(--surface-2);
  }
  .banner-grad {
    position: absolute;
    inset: 0;
    background: linear-gradient(180deg, rgb(0 0 0 / 0.05) 30%, rgb(0 0 0 / 0.72));
  }
  .title {
    position: absolute;
    left: 16px;
    right: 48px;
    bottom: 10px;
    margin: 0;
    color: #fff;
    font-size: 1.15rem;
    line-height: 1.25;
    text-shadow: 0 1px 4px rgb(0 0 0 / 0.5);
  }
  .close {
    position: absolute;
    top: 10px;
    right: 10px;
    width: 30px;
    height: 30px;
    border: none;
    border-radius: 50%;
    background: rgb(0 0 0 / 0.45);
    color: #fff;
    cursor: pointer;
    backdrop-filter: blur(4px);
  }
  .close:hover {
    background: rgb(0 0 0 / 0.65);
  }
  .body {
    padding: 14px 16px 16px;
  }
  .evidence {
    margin: 8px 0 14px;
    font-size: 0.85rem;
    color: var(--text-muted);
  }
  dl {
    display: grid;
    grid-template-columns: 92px 1fr;
    gap: 8px 14px;
    margin: 0 0 16px;
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
  .muted {
    color: var(--text-muted);
  }
  .actions {
    display: flex;
    gap: 8px;
  }
  .actions .btn {
    flex: 1;
    justify-content: center;
    text-decoration: none;
  }
  .btn[disabled] {
    opacity: 0.5;
    cursor: not-allowed;
  }
  .meta {
    margin: 14px 0 0;
    font-size: 0.76rem;
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
