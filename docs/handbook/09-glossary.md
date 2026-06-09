# 9. Glossary

Plain one-line definitions for words used across the handbook and docs.

- **Frontend** — the part of the app that runs in your browser (the map, buttons). Ours
  is SvelteKit + MapLibre.
- **Backend** — the server-side program that does the work behind the scenes. Ours is
  FastAPI (Python).
- **Framework** — a ready-made toolkit for building software (e.g. SvelteKit, FastAPI).
- **API** — a defined way for one program to ask another for data (e.g. the frontend asks
  the backend "chargers in this rectangle?").
- **Server** — a computer that stays on and answers requests over the internet.
- **Database** — long-term, organised storage. Ours is PostgreSQL.
- **PostGIS** — an add-on that makes PostgreSQL good at *map/location* questions.
- **bbox (bounding box)** — the rectangle of the map currently on screen; the app only
  asks about this area.
- **OCM (Open Charge Map)** — the open, community database of charger locations PlugPulse
  builds on. Requires a free API key.
- **Cache** — a small fast store of recent answers so work isn't repeated. Ours is Redis.
- **Docker image** — a packaged, ready-to-run snapshot of a program + its dependencies.
- **Container** — a running copy of an image (isolated from the rest of the machine).
- **docker compose** — a tool to run several containers together (our whole stack) with
  one command.
- **Reverse proxy** — a "front desk" program that receives web traffic and routes it to
  the right service. Ours is **Caddy**, which also gets HTTPS certificates automatically.
- **HTTPS / TLS** — encrypted (padlock) web traffic. Needed so browsers trust the site.
- **Mixed content** — when an `https://` page tries to call an insecure `http://` address;
  browsers block it. That's why the backend also needs HTTPS.
- **localhost** — "this very computer." On a visitor's browser, `localhost` means *their*
  machine, not your server — which is why a local backend can't serve other people.
- **DNS** — the internet's phone book: turns a name (`api.example.com`) into an IP address.
- **sslip.io** — a free DNS trick where the address contains the IP (e.g.
  `api.140-238-1-2.sslip.io` → `140.238.1.2`), so you need no domain signup.
- **IP address** — a computer's numeric address on the internet (e.g. `140.238.1.2`).
- **CGNAT** — when your ISP shares one public address among many homes, so your machine
  has no public address of its own — a reason home-hosting can be hard.
- **Port** — a numbered "door" on a server for a kind of traffic; **80** = web, **443** =
  secure web (HTTPS).
- **Tunnel** — software that connects a private machine to the public internet without a
  public address (e.g. Cloudflare Tunnel, frp).
- **CORS** — a browser safety rule; an API must explicitly allow which websites may call
  it. We allow the Vercel site via `CORS_ALLOW_ORIGINS`.
- **PaaS** — "Platform as a Service": a layer that makes deploying apps easy (e.g. Vercel,
  or self-hosted Coolify/Dokku).
- **VM (virtual machine)** — a rented/virtual computer in the cloud (e.g. the Oracle VM).
- **VPS** — "Virtual Private Server"; the same idea, usually paid.
- **Always Free vs Trial (Oracle)** — *Trial* is a 30-day credit for paid services;
  *Always Free* resources run free forever. Signing up gives both; pick "Always
  Free-eligible" resources to never be charged.
- **Identity provider (IdP)** — a service that handles login and accounts (ours is
  **Authentik**); apps trust it instead of storing passwords themselves.
- **OIDC (OpenID Connect)** — the standard for "log in via another service" (like "Sign in
  with Google", but our login server is self-hosted).
- **JWT** — a tamper-proof, signed "pass" the login server issues; the backend verifies it
  to know who you are without seeing your password.
- **Half-life** — the time for something to lose half its strength; PlugPulse reports
  halve in weight every 3 hours so fresh reports dominate.
- **Reliability score** — the 0–1 number (and green/amber/red/grey label) summarising
  whether a charger is working now. See [Chapter 8](08-the-reliability-score.md).

---

Prev: [← 8. The reliability score](08-the-reliability-score.md) ·
[Back to contents](README.md)
