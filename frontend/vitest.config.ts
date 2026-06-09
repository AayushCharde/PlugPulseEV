import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";

// Standalone Vitest config (takes precedence over vite.config.ts) so the unit
// tests run in a plain Node environment without booting the SvelteKit plugin.
// We map the `$lib` alias ourselves so source modules can use it (SvelteKit
// provides it at build time; here we resolve it for tests).
export default defineConfig({
  test: {
    include: ["tests/**/*.test.ts"],
  },
  resolve: {
    alias: {
      $lib: fileURLToPath(new URL("./src/lib", import.meta.url)),
    },
  },
});
