/**
 * Auth.js (@auth/sveltekit) configured against the self-hosted Authentik IdP.
 * Server-only: secrets come from $env/dynamic/private and never reach the client.
 * The Authentik access token is surfaced on the session so API calls can send it
 * as a Bearer (used by Phase 2 reports).
 */

import { SvelteKitAuth } from "@auth/sveltekit";
import Authentik from "@auth/sveltekit/providers/authentik";
import { env } from "$env/dynamic/private";

export const { handle, signIn, signOut } = SvelteKitAuth({
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
});
