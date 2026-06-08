/**
 * Debounce: delay calling `fn` until `waitMs` has passed since the last call.
 *
 * Critical for the map: a pan/zoom fires dozens of "moveend"-like events. Without
 * debouncing we'd hammer the API; with it we make one request once the user stops.
 */
export function debounce<A extends unknown[]>(
  fn: (...args: A) => void,
  waitMs: number,
): (...args: A) => void {
  let timer: ReturnType<typeof setTimeout> | undefined;
  return (...args: A): void => {
    if (timer !== undefined) clearTimeout(timer);
    timer = setTimeout(() => fn(...args), waitMs);
  };
}
