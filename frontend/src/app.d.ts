// See https://svelte.dev/docs/kit/types#app.d.ts
import type { Session } from "@auth/sveltekit";

declare global {
  namespace App {
    // interface Error {}
    interface Locals {
      // Set by Auth.js only when auth is configured; absent otherwise.
      auth?: () => Promise<Session | null>;
    }
    interface PageData {
      session?: Session | null;
      authEnabled?: boolean;
    }
    // interface PageState {}
    // interface Platform {}
  }
}

// Carry the Authentik access token through the session + JWT.
declare module "@auth/sveltekit" {
  interface Session {
    accessToken?: string;
  }
}

declare module "@auth/core/jwt" {
  interface JWT {
    accessToken?: string;
  }
}

export {};
