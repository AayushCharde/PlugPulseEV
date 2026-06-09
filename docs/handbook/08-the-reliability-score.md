# 8. The reliability score, in plain words

**In short:** each charger's colour comes from recent driver reports, where **newer
reports count more than older ones**. More "working" → green; more "broken" → red; not
enough recent reports → grey.

## The idea

A charger that worked 5 minutes ago is probably still working. A report from 2 days ago
tells you almost nothing. So PlugPulse weighs reports by **freshness**.

## Freshness fades (the "half-life")

Every report starts at full strength and **loses half its weight every 3 hours**. So:

- just now → counts as **1.0**
- 3 hours ago → **0.5**
- 6 hours ago → **0.25**
- a day ago → almost nothing

This is called a *half-life* (the same idea as a fading echo). [→ Glossary: half-life](09-glossary.md)

## Adding it up

- "**Working**" reports add to the **positive** pile.
- "**Broken**" and "**ICE-blocked**" (a petrol car in the bay) add to the **negative** pile.
- "**Occupied**" is **neutral** — the charger works, it's just busy.

Then:

```
score      = positive ÷ (positive + negative)      → a number from 0 to 1
confidence = positive + negative                   → how much recent signal exists
```

## Turning the number into a colour

| Situation | Label | Colour |
|---|---|---|
| Not enough recent reports (low confidence) | "No recent reports" | grey |
| score ≥ 0.7 | "Likely working" | green |
| 0.4 – 0.7 | "Mixed reports" | amber |
| below 0.4 | "Likely down" | red |

The app also shows the *evidence* (e.g. "4 recent confirmations") — trust comes from
showing the working, not a mystery number.

## Right now: everything is grey

Until the reports feature is live, there are no reports yet — so every charger reads
**"unknown" (grey)**. That's expected and correct; the colours come alive once drivers
start reporting.

**Learn more →** the exact formula is in
[`PlugPulse-Project-Spec.md`](../../PlugPulse-Project-Spec.md) (§7) and the code is
[`backend/app/scoring.py`](../../backend/app/scoring.py).

---

Prev: [← 7. Accounts and login](07-accounts-and-login.md) ·
Next: [9. Glossary →](09-glossary.md)
