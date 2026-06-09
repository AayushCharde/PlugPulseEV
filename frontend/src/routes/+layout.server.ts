import type { LayoutServerLoad } from "./$types";

// Expose the session to every page (the header shows sign-in / sign-out).
export const load: LayoutServerLoad = async (event) => {
  return { session: await event.locals.auth() };
};
