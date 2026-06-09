# 2. How it's built

**In short:** PlugPulse has three pieces — a **frontend** (the map you see), a
**backend** (the brain that answers questions), and a **database** (the memory that
stores chargers and reports).

## The three pieces (with a simple analogy)

Think of a restaurant:

- **Frontend = the dining room.** What you see and touch — the map, buttons, the charger
  details panel. It runs in *your browser*. Built with **SvelteKit** (a web framework)
  and **MapLibre** (the map). [→ Glossary: frontend, framework](09-glossary.md)
- **Backend = the kitchen.** You don't see it, but it does the work: fetching chargers,
  calculating the reliability colour, saving reports. Built with **FastAPI** (Python).
  [→ Glossary: backend, API](09-glossary.md)
- **Database = the pantry/notebook.** Where chargers and reports are stored so they're
  remembered. We use **PostgreSQL + PostGIS** — a database that's good at *map/location*
  questions like "what's inside this rectangle?" [→ Glossary: database, PostGIS](09-glossary.md)

There's also a small **cache** (Redis) — a fast scratchpad so the kitchen doesn't redo
the same work repeatedly.

## How they talk: the "viewport" idea

The map never downloads the whole planet. It only ever asks about the **rectangle you're
currently looking at** (called a *bounding box*, or **bbox**). [→ Glossary: bbox](09-glossary.md)

The round trip:

```
You pan/zoom the map
      │  "give me chargers in THIS rectangle"
      ▼
Frontend ──── request (bbox) ────▶ Backend
                                     │  looks in the database (and tops it up
                                     │  from Open Charge Map if needed)
                                     ▼
Frontend ◀──── chargers + colours ── Backend
      │
      ▼
Map draws the dots
```

Because it only asks about what's on screen, it stays fast no matter how far you zoom out.

## Why a backend at all?

Open Charge Map already has the charger locations — so why not call it directly from the
browser? Because PlugPulse's value is the **fast, fresh reliability layer**: storing
reports, scoring them, and serving them instantly. That needs our own kitchen + pantry,
which we also control for speed and privacy.

**Learn more →** the architecture diagram and data model are in
[`CLAUDE.md`](../../CLAUDE.md) and [`PlugPulse-Project-Spec.md`](../../PlugPulse-Project-Spec.md).

---

Prev: [← 1. What is PlugPulse?](01-what-is-plugpulse.md) ·
Next: [3. Where each part lives →](03-where-it-lives.md)
