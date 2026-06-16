import type { LayoutServerLoad } from "./$types";
import { authEnabled } from "../auth";

// Expose the session (and whether auth is configured) to every page.
// When auth is disabled, locals.auth isn't set, so the session is just null.
export const load: LayoutServerLoad = async (event) => {
  const session = event.locals.auth ? await event.locals.auth() : null;
  return { session, authEnabled };
};
