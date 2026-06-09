import type { Handle } from "@sveltejs/kit";
import { env } from "$env/dynamic/private";

const authConfigured = Boolean(
  env.AUTH_SECRET && env.AUTH_AUTHENTIK_ID && env.AUTH_AUTHENTIK_SECRET && env.AUTH_AUTHENTIK_ISSUER,
);

async function loadHandle(): Promise<Handle> {
  if (!authConfigured) {
    return ({ event, resolve }) => {
      event.locals.auth = async () => null;
      return resolve(event);
    };
  }
  const { handle } = await import("./auth");
  return handle;
}

const handlePromise = loadHandle();

export const handle: Handle = async (input) => {
  const h = await handlePromise;
  return h(input);
};
