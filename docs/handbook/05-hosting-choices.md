# 5. Hosting choices

**In short:** the backend needs an always-on computer with a public address. Your options,
cheapest-effort to most-control: a **free cloud VM** (Oracle Always Free), your **own
machine**, or an **open-source PaaS** on top of either.

## The options at a glance

| Option | Cost | Always on? | Open host? | Effort |
|---|---|---|---|---|
| **Oracle Cloud Always Free VM** | $0 | ✅ | ❌ (proprietary company) | Medium (one-time setup) |
| **Your own machine** (Pi / mini-PC / old laptop) | $0 (you own it) | Only if you keep it on | ✅ | Medium–High (expose to internet) |
| **Paid VPS** (Hetzner, etc.) | ~€4/mo | ✅ | ❌ | Low |
| **Open-source PaaS** (Coolify, Dokploy…) | cost of the host | depends on host | ✅ tool, host varies | adds a nice UI on top |

Whatever the host, **the software we run on it is the same open-source `docker compose`
stack.**

## Oracle Cloud "Always Free" — trial vs free

Our recommended free path. One thing confuses everyone at signup: you see a **"Trial"**
banner. Here's the truth:

- Signing up gives you **two things at once**: a **30-day $300 trial** (to test *paid*
  services) **and** the **Always Free** resources (free *forever*, no time limit — e.g.
  up to 4 ARM cores + 24 GB RAM).
- When the 30-day trial ends, your account becomes an **Always Free** account, and your
  Always-Free resources **keep running at $0**. They are *not* deleted.
- The rule to stay at $0: only create resources marked **"Always Free-eligible."** Oracle
  won't charge your card unless *you* explicitly upgrade to "Pay As You Go."

So the "Trial" label is normal and harmless — just pick the Always-Free-eligible VM.
[→ Glossary: Always Free vs trial](09-glossary.md)

## Your own machine

The most "open" option (your hardware, open software). The catch is **exposing it to the
internet** so the public frontend can reach it:

- **Port-forward** on your router + a free hostname — fully open, but home ISPs often
  block the needed ports or use **CGNAT** (no public address). [→ Glossary: CGNAT](09-glossary.md)
- A **tunnel** — software that pokes a safe hole out to the internet. `cloudflared`
  (Cloudflare Tunnel) is easy and free (client is open source, service is Cloudflare's);
  fully open-source tunnels like **frp** / **rathole** exist but need a small relay host.

Either way, the machine must **stay on** — a laptop that sleeps won't serve.

## Open-source PaaS (optional convenience layer)

Tools like **Coolify**, **Dokploy**, **Dokku**, and **CapRover** give you a friendly
web dashboard (like a self-hosted Vercel/Heroku) to deploy Docker apps. They're free and
open source — but they still **run on a host you provide** (a VM or your machine). Nice if
you want a UI; not required, since our `docker compose` works directly.
[→ Glossary: PaaS](09-glossary.md)

## Our pick

For "free + always-on + least effort": the **Oracle Always Free VM** running the
`docker compose` stack. For "fully self-owned": **your own always-on machine** + a tunnel.
The deploy steps are the same once the machine exists — see the next chapter.

---

Prev: [← 4. "Free" vs "open source"](04-free-vs-open-source.md) ·
Next: [6. Deploy the backend →](06-deploy-the-backend.md)
