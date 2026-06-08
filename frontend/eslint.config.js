import js from "@eslint/js";
import ts from "typescript-eslint";
import svelte from "eslint-plugin-svelte";
import globals from "globals";

export default ts.config(
  // Never lint generated/build output or deps.
  {
    ignores: ["build/", ".svelte-kit/", "dist/", "node_modules/"],
  },
  js.configs.recommended,
  ...ts.configs.recommended,
  ...svelte.configs["flat/recommended"],
  {
    languageOptions: {
      globals: { ...globals.browser, ...globals.node },
    },
  },
  {
    // Svelte files are parsed by svelte-eslint-parser; <script lang="ts"> blocks
    // are handed off to the TypeScript parser.
    files: ["**/*.svelte"],
    languageOptions: {
      parserOptions: { parser: ts.parser },
    },
  },
);
