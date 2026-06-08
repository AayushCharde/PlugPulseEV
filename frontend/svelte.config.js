import adapterNode from "@sveltejs/adapter-node";
import adapterVercel from "@sveltejs/adapter-vercel";
import { vitePreprocess } from "@sveltejs/vite-plugin-svelte";

// Vercel sets VERCEL=1 in its build environment. Use its serverless adapter
// there; everywhere else (Docker, docker-compose, `node build`, CI) keep the
// self-contained Node server in ./build. One config, two targets.
const onVercel = Boolean(process.env.VERCEL);

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    adapter: onVercel ? adapterVercel() : adapterNode(),
  },
};

export default config;
