<script lang="ts">
  import { onMount } from "svelte";
  import { currentTheme, toggleTheme, type Theme } from "$lib/theme";

  let theme: Theme = "light";

  onMount(() => {
    theme = currentTheme();
  });

  function flip(): void {
    theme = toggleTheme();
  }
</script>

<header class="header">
  <a class="brand" href="/" aria-label="PlugPulse home">
    <svg class="bolt" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
      <path d="M13 2 4 14h6l-1 8 9-12h-6l1-8z" fill="currentColor" />
    </svg>
    <span class="word">PlugPulse</span>
  </a>

  <div class="actions">
    <button class="btn-icon" on:click={flip} aria-label="Toggle dark mode" title="Toggle theme">
      {#if theme === "dark"}
        <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
          <circle cx="12" cy="12" r="5" fill="currentColor" />
          <g stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M19.1 4.9l-1.4 1.4M6.3 17.7l-1.4 1.4" />
          </g>
        </svg>
      {:else}
        <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
          <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" fill="currentColor" />
        </svg>
      {/if}
    </button>
    <!-- auth control is added in PR-E -->
  </div>
</header>

<style>
  .header {
    position: fixed;
    inset: 0 0 auto 0;
    z-index: 10;
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 16px;
    background: color-mix(in srgb, var(--surface) 82%, transparent);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid var(--border);
  }
  .brand {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    text-decoration: none;
    color: var(--text);
    font-weight: 800;
    font-size: 18px;
    letter-spacing: -0.01em;
  }
  .bolt {
    color: var(--primary);
  }
  .word {
    color: var(--text);
  }
  .actions {
    display: flex;
    align-items: center;
    gap: 8px;
  }
</style>
