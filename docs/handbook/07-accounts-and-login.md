# 7. Accounts and login

**In short:** browsing the map needs **no login**. Login exists only so that *reports*
can be tied to a person (to keep them honest). We use **Authentik**, an open-source login
server you host yourself.

## Why login at all?

The map is public — anyone can look at chargers without an account. But when people start
**reporting** a charger's status (a later phase), we need to:

- attribute each report to *someone* (not anonymous spam),
- rate-limit abuse (one person can't spam 100 fake reports),
- build a light "trust score" over time.

That requires accounts. Reading stays open; *writing* reports needs you signed in.

## Who handles the login: Authentik

Rather than build password handling ourselves (risky), we use **Authentik** — a free,
open-source **identity provider**. It owns the "sign in" screen and the user accounts.
Our app just *trusts* it. [→ Glossary: identity provider, OIDC](09-glossary.md)

The standard it speaks is **OIDC** (OpenID Connect) — the same idea as "Sign in with
Google," except the login server is *yours*, not Google's. Keeps it open and private.

## How it works (simply)

```
You click "Sign in"
      ▼
Authentik shows its login page → you log in
      ▼
Authentik hands the app a signed "pass" (a token)
      ▼
The backend checks the pass is genuine, then knows who you are
```

The backend never sees your password — only the signed pass (a **JWT**), which it
verifies using Authentik's public keys. [→ Glossary: JWT](09-glossary.md)

## Important: it's optional

Login is **switched off by default**. If the backend isn't configured with Authentik
details, the map and chargers work exactly the same — the login button just isn't wired
up, and report-writing (a later phase) is disabled. So you can deploy and use the map
*without* setting up Authentik at all, and add it whenever you're ready.

**Learn more →** the Authentik setup (create the login provider, copy the keys) is in the
[`DEPLOYMENT.md`](../../DEPLOYMENT.md) authentication section.

---

Prev: [← 6. Deploy the backend](06-deploy-the-backend.md) ·
Next: [8. The reliability score →](08-the-reliability-score.md)
