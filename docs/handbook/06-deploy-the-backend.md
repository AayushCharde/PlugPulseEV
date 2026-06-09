# 6. Deploy the backend, step by step

**In short:** make a free Oracle VM, get a free hostname from `sslip.io`, then run one
`docker compose` command. Caddy gives you HTTPS automatically.

> This is the friendly overview. The exact, canonical commands and env vars live in
> [`DEPLOYMENT.md`](../../DEPLOYMENT.md) — follow that when you actually run it.

## The address trick: `sslip.io` (no signup)

You need a web address for HTTPS, but you don't need to buy a domain. **`sslip.io`** is a
free service where the address *contains* the IP:

- If your server's IP is `140.238.1.2`, then `api.140-238-1-2.sslip.io` automatically
  points to it. No account, nothing to register.

So once you know the server's IP, your two addresses just exist:
`api.<ip>.sslip.io` (the API) and `auth.<ip>.sslip.io` (the login server).
(They're ugly; you can swap in a pretty domain later.) [→ Glossary: DNS](09-glossary.md)

## The steps

1. **Make the server.** On Oracle Cloud, create an **Ubuntu** VM with an **"Always
   Free-eligible"** shape (see [Chapter 5](05-hosting-choices.md)). Add your SSH key.
   Note its **public IP**.
2. **Open the doors.** In Oracle's "Security List," allow incoming traffic on ports
   **80** and **443** (web + secure web).
3. **Connect.** From your computer: `ssh ubuntu@<IP>`.
4. **Install Docker** on the server (one command — see `DEPLOYMENT.md`).
5. **Get the code:** `git clone` the repo onto the server.
6. **Fill in settings.** Copy `.env.prod.example` to `.env` and set:
   - `DOMAIN` = `api.<ip>.sslip.io`, `AUTH_DOMAIN` = `auth.<ip>.sslip.io`
   - `OCM_API_KEY` = your free Open Charge Map key ([Chapter 8](08-the-reliability-score.md)
     explains what it powers)
   - `CORS_ALLOW_ORIGINS` = `https://plugpulse.vercel.app` (lets the live site call the API)
   - a few random passwords (the file shows which)
7. **Launch:** `docker compose -f docker-compose.prod.yml up -d --build`.
8. **Check:** open `https://api.<ip>.sslip.io/health` — you should see `{"status":"ok"}`.
   Caddy fetches a real HTTPS certificate on its own.
9. **Connect the frontend:** in Vercel, set `PUBLIC_API_BASE_URL` to your API address and
   redeploy. The live map now shows real chargers.

## What "CORS" is doing here

Your site is on `plugpulse.vercel.app`; your API is on a different address. Browsers block
a page from calling a *different* site's API unless that API says "I allow this site."
That allow-list is **CORS** — that's what `CORS_ALLOW_ORIGINS` sets. [→ Glossary: CORS](09-glossary.md)

## About the Open Charge Map key

The charger data comes from Open Charge Map, which now requires a **free API key**
(sign up at openchargemap.org → "My Apps"). Without it you get blocked (HTTP 403) and the
map stays empty — but the app won't crash, it just shows no chargers until the key is set.

**Learn more →** exact commands, the Authentik login setup, and production notes are in
[`DEPLOYMENT.md`](../../DEPLOYMENT.md).

---

Prev: [← 5. Hosting choices](05-hosting-choices.md) ·
Next: [7. Accounts and login →](07-accounts-and-login.md)
