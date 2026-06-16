/**
 * Auth.js (@auth/sveltekit) against the self-hosted Authentik IdP — OPTIONAL.
 *
 * Auth is only enabled when its env vars are present. Otherwise we export a
 * pass-through handle so the public map renders with no auth configured —
 * SvelteKitAuth would otherwise throw `MissingSecret` on every request.
 * Server-only: secrets come from $env/dynamic/private.
 */

import { SvelteKitAuth } from "@auth/sveltekit";
import Authentik from "@auth/sveltekit/providers/authentik";
import { env } from "$env/dynamic/private";
import type { Handle } from "@sveltejs/kit";

export const authEnabled = Boolean(
  env.AUTH_SECRET && env.AUTH_AUTHENTIK_ISSUER && env.AUTH_AUTHENTIK_ID && env.AUTH_AUTHENTIK_SECRET,
);

const passthrough: Handle = ({ event, resolve }) => resolve(event);

export const handle: Handle = authEnabled
  ? SvelteKitAuth({
      trustHost: true,
      secret: env.AUTH_SECRET,
      providers: [
        Authentik({
          clientId: env.AUTH_AUTHENTIK_ID,
          clientSecret: env.AUTH_AUTHENTIK_SECRET,
          issuer: env.AUTH_AUTHENTIK_ISSUER,
        }),
      ],
      callbacks: {
        async jwt({ token, account }) {
          // Persist the provider access token on first sign-in.
          if (account?.access_token) token.accessToken = account.access_token;
          return token;
        },
        async session({ session, token }) {
          session.accessToken = token.accessToken;
          return session;
        },
      },
    }).handle
  : passthrough;
