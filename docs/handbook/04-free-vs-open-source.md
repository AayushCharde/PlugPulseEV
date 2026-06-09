# 4. "Free" vs "open source"

**In short:** these are **two different things**. PlugPulse's *software* is fully open
source. *Hosting* (whose computer runs it) is a separate question — and there's no such
thing as a free, open-source cloud, because a host is always someone's physical computer.

## Two separate axes

People say "free and open source" in one breath, but they mean different things:

- **Open source** = the *code/recipe* is public, anyone can read, run, and change it.
- **Free** = it doesn't *cost money*.

Something can be one without the other:

| | Free | Not free |
|---|---|---|
| **Open source** | PostgreSQL, Caddy, our app | (rare) |
| **Closed source** | Vercel/Oracle free tiers | Most paid SaaS |

## Our software is 100% open source

Everything PlugPulse *runs* is open source: SvelteKit, MapLibre, FastAPI, PostgreSQL +
PostGIS, Redis, Caddy, Authentik. The charger data (Open Charge Map) and map tiles
(OpenFreeMap/OpenStreetMap) are open too. That box is fully checked, wherever it runs.

## But hosting is a different story

A "host" is always **someone's physical computer**. There is **no free, open-source
cloud provider** — every free public host (Vercel, Oracle, Fly, Render…) is a
**proprietary company** giving away a slice of *their* hardware.

So "I want open-source hosting" really resolves to one of:

1. **Run it on a computer you own** (home server, Raspberry Pi, spare laptop). The
   hardware is yours and the software is open — the most "open" option. (Trade-off: it
   must stay on and be reachable; see [Chapter 5](05-hosting-choices.md).)
2. **Use a proprietary host's free tier** (e.g. Oracle Always Free). The *software* stays
   open; the *computer* underneath belongs to a company. This is the easiest "always-on +
   free" path.

Neither is "wrong" — it's just useful to know that **keeping the stack open source does
not require an open-source host**, because no such free cloud exists.

## What this means for PlugPulse

We deliberately use **only free, open tools** in the core path — no paid API keys, no
locked-in services. The one practical choice left is *where the backend computer lives*,
which is the next chapter.

---

Prev: [← 3. Where each part lives](03-where-it-lives.md) ·
Next: [5. Hosting choices →](05-hosting-choices.md)
