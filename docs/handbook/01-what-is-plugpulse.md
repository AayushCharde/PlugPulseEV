# 1. What is PlugPulse?

**In short:** PlugPulse is a free, open map that doesn't just show you *where* EV
chargers are — it tells you whether they **actually work right now**, based on quick
reports from other drivers.

## The problem it solves

Finding a charger is already easy — lots of apps show them on a map. The real pain is
**trust**. You drive to a charger the app says is "available," and it's broken, offline,
or blocked by a petrol car. The map was right about the *location* and wrong about the
*reality*.

PlugPulse is the missing **trust layer**: think *"Waze for EV charger reliability."*
Just as Waze drivers report traffic, PlugPulse drivers tap a charger's status
(Working / Broken / Occupied / ICE-blocked), and everyone sees a fresh, honest picture.

## What makes it different

- **Trust, not just location.** The headline question is "does it work *now*?"
- **Open data, open code.** Charger locations come from [Open Charge Map](https://openchargemap.org)
  (a community database), the map tiles are free and open, and the whole app is open source.
  No locked-in data, no paid keys in the core path.
- **Community-powered.** Every report makes the map more useful for the next driver, and
  reports can flow back to the open commons.

## How a normal visit goes

1. Open the map → see chargers near you.
2. Each charger has a colour: green ("likely working"), amber ("mixed"), red ("likely
   down"), or grey ("no recent reports").
3. Tap one → see details and recent reports.
4. (Later phase) Tap a status to add your own report.

That colour is the heart of the product — see [Chapter 8](08-the-reliability-score.md)
for how it's calculated.

**Learn more →** the full product thinking is in
[`PlugPulse-Project-Spec.md`](../../PlugPulse-Project-Spec.md).

---

Next: [2. How it's built →](02-how-its-built.md)
