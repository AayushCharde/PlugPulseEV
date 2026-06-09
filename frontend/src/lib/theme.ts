/**
 * Light/dark theme handling. The pure helpers are unit-tested; the DOM glue
 * (localStorage + the <html data-theme> attribute) is thin and browser-only.
 */

export type Theme = "light" | "dark";

const STORAGE_KEY = "pp-theme";

/** The opposite theme — used by the header toggle. */
export function nextTheme(current: Theme): Theme {
  return current === "dark" ? "light" : "dark";
}

/**
 * Resolve the effective theme from a stored choice and the OS preference.
 * A stored value wins; otherwise fall back to the system preference.
 */
export function resolveTheme(stored: string | null, prefersDark: boolean): Theme {
  if (stored === "light" || stored === "dark") return stored;
  return prefersDark ? "dark" : "light";
}

/** Read the current effective theme in the browser. */
export function currentTheme(): Theme {
  if (typeof document === "undefined") return "light";
  const attr = document.documentElement.getAttribute("data-theme");
  if (attr === "light" || attr === "dark") return attr;
  const prefersDark =
    typeof matchMedia !== "undefined" && matchMedia("(prefers-color-scheme: dark)").matches;
  return prefersDark ? "dark" : "light";
}

/** Apply a theme: set <html data-theme> and persist the choice. */
export function setTheme(theme: Theme): void {
  if (typeof document === "undefined") return;
  document.documentElement.setAttribute("data-theme", theme);
  try {
    localStorage.setItem(STORAGE_KEY, theme);
  } catch {
    /* storage may be unavailable (private mode) — ignore */
  }
}

/** Flip light <-> dark from the currently applied theme. */
export function toggleTheme(): Theme {
  const next = nextTheme(currentTheme());
  setTheme(next);
  return next;
}
