<script lang="ts">
  const items: { color: string; label: string }[] = [
    { color: "var(--rel-green)", label: "Likely working" },
    { color: "var(--rel-amber)", label: "Mixed reports" },
    { color: "var(--rel-red)", label: "Likely down" },
    { color: "var(--rel-grey)", label: "No recent reports" },
  ];
</script>

<aside class="legend" aria-label="Reliability legend">
  <span class="title">Reliability</span>
  {#each items as item}
    <span class="row"><span class="dot" style="background: {item.color}"></span>{item.label}</span>
  {/each}
</aside>

<style>
  .legend {
    position: fixed;
    bottom: 16px;
    left: 16px;
    z-index: 7;
    display: flex;
    flex-direction: column;
    gap: 5px;
    padding: 10px 12px;
    background: color-mix(in srgb, var(--surface) 88%, transparent);
    backdrop-filter: blur(10px);
    border: 1px solid var(--border);
    border-radius: var(--r-md);
    box-shadow: var(--shadow-sm);
    font-size: 0.78rem;
  }
  .title {
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    font-size: 0.68rem;
  }
  .row {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--text);
  }
  @media (max-width: 520px) {
    .legend {
      display: none;
    }
  }
</style>
