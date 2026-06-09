# 3. Where each part lives (and why)

**In short:** the **frontend** lives on **Vercel** (great for websites); the **backend**
needs its **own always-on server** (Vercel can't run it). They live in different places
on purpose.

## The split

| Part | Lives on | Why |
|---|---|---|
| Frontend (the map site) | **Vercel** (free Hobby tier) | Vercel is built for websites — it serves them fast worldwide and redeploys on every push. |
| Backend (the kitchen + pantry) | **A small always-on server** you control | It's a long-running program with a database; that needs a real server, not Vercel. |

## Why not put the backend on Vercel too?

Vercel runs **serverless functions** — tiny programs that wake up for one request, then
sleep. Our backend is different:

- It's a **long-running server** holding open connections to the database.
- It **needs a real database** (PostGIS) running continuously.
- It runs extra services (cache, optional login server) as containers.

Serverless can't host that well. So Vercel hosts the frontend (perfect fit), and the
backend lives on its own server. More on the backend options in
[Chapter 5](05-hosting-choices.md).

## Why can't the backend just run on my laptop?

It can — for *development*. But for *other people* to use the live site, the backend must
be reachable from their browsers. A laptop fails three tests:

1. **`localhost` isn't shared.** When the live site tells a visitor's browser to call
   `localhost:8000`, that means *their own machine*, not yours. Your laptop is only
   reachable from your laptop. [→ Glossary: localhost](09-glossary.md)
2. **No public address + it sleeps.** Home machines sit behind a router (no public
   address) and turn off. A server needs to be **always on** and **publicly reachable**.
3. **HTTPS rule.** The live site is `https://`. Browsers **refuse** to let an `https://`
   page call an insecure `http://` backend (called *mixed content*). So the backend must
   also be `https://` — which needs a real address and a certificate.
   [→ Glossary: HTTPS, mixed content](09-glossary.md)

That's why a deployed backend needs a proper **server + address + HTTPS** — which a tool
called **Caddy** sets up automatically for us.

**Learn more →** the deployment strategy is in [`DEPLOYMENT.md`](../../DEPLOYMENT.md).

---

Prev: [← 2. How it's built](02-how-its-built.md) ·
Next: [4. "Free" vs "open source" →](04-free-vs-open-source.md)
