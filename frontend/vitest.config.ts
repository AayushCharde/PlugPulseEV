import { defineConfig } from "vitest/config";

// Standalone Vitest config (takes precedence over vite.config.ts) so the unit
// tests run in a plain Node environment without booting the SvelteKit plugin.
// The lib helpers under test are pure functions — no DOM or $app imports.
export default defineConfig({
  test: {
    include: ["tests/**/*.test.ts"],
  },
});
