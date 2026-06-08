import adapter from "@sveltejs/adapter-node";
import { vitePreprocess } from "@sveltejs/vite-plugin-svelte";

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    // Self-contained Node server in ./build; `node build` listens on PORT
    // (default 3000) — matches the frontend Dockerfile and docker-compose.
    adapter: adapter(),
  },
};

export default config;
