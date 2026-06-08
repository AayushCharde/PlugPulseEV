# SEO & AI SEO (GEO)

PlugPulse needs to be found two ways in 2026: by classic search engines **and** by
generative engines (ChatGPT, Claude, Perplexity, Gemini / Google AI Overviews). The two
share a foundation; we do both together. This doc is the playbook.

## Principle

Strong technical SEO is the foundation; AI SEO (GEO/AEO) layers on top. The single most
important technical requirement for both — and the one our stack must respect — is that
**important content is server-rendered**, because AI crawlers read server HTML, not
client-side JavaScript.

## Technical foundation (classic SEO)

- **Server-side render / prerender** the landing page and all content/marketing pages.
  In SvelteKit, prerender static pages (`export const prerender = true`) and SSR the
  rest. Keep the *interactive map* client-side, but the pages that should rank/be cited
  must ship real HTML.
- **Fast & mobile.** We already have performance budgets (see `PERFORMANCE.md`); Core
  Web Vitals (LCP/CLS/INP) are ranking and quality signals.
- **Clean URLs & canonicals.** One canonical URL per page (`canonical()` in `lib/seo.ts`).
- **Sitemap** at `/sitemap.xml` (generate from routes) and **`robots.txt`** at the root
  (already in `static/robots.txt`).
- **Heading hierarchy:** one `<h1>` per page, logical `<h2>/<h3>`, one topic per section.

## Structured data (JSON-LD)

Emit JSON-LD via `lib/seo.ts` helpers. Priority types:

- **Organization** — site-wide identity (`organizationJsonLd`).
- **WebApplication** — PlugPulse is a free PWA; describe it for app rich results
  (`webApplicationJsonLd`).
- **FAQPage** — on the FAQ and where relevant; answer-first Q&A is exactly what AI
  engines extract and cite (`faqJsonLd`).
- Add **BreadcrumbList** and **Article** for any blog/guide content later.

## AI SEO (GEO / AEO)

- **Let AI crawlers in.** `robots.txt` explicitly allows GPTBot, ChatGPT-User,
  OAI-SearchBot, ClaudeBot, PerplexityBot, and Google-Extended. Blocking any of them
  means PlugPulse can't be cited in that engine's answers. (If you put the site behind
  Cloudflare, double-check its bot settings don't silently block them.)
- **Answer-first writing.** Lead each section with a direct, self-contained answer, then
  context. AI systems pull short, standalone passages — write them that way.
- **Verifiable facts + recency.** Include concrete facts and a visible "Last updated"
  date on cornerstone pages; generative engines weight freshness.
- **`llms.txt`** is included at the root (`static/llms.txt`) as a curated index. Honest
  caveat: it's low-cost but **unproven** — a 300k-domain study found no correlation
  between having it and being cited, and Google says it doesn't use such files. Treat it
  as a cheap maybe-upside, not a priority. The real wins are SSR, schema, speed, and
  answer-first content.

## Social sharing

`metaTags()` emits OpenGraph + Twitter Card tags (`summary_large_image`). Ship a default
`/og-default.png` (1200×630) and per-page images where it helps.

## Measurement

- **GA4 (or a privacy-friendly analytics):** isolate AI-referral traffic in a custom
  channel; watch for `ChatGPT-User` and similar referrers/user-agents in logs.
- **AI visibility:** periodically prompt-test PlugPulse against a fixed list of important
  queries ("reliable EV charger near me", "is this charger working") across ChatGPT,
  Perplexity, Claude, and Gemini, and track whether/how you're mentioned.

## Launch checklist

- [ ] Landing + content pages are SSR/prerendered (real HTML in view-source)
- [ ] `<title>`, meta description, canonical on every page (via `lib/seo.ts`)
- [ ] Organization + WebApplication JSON-LD on home; FAQPage on FAQ
- [ ] `robots.txt` deployed with the real domain in the `Sitemap:` line
- [ ] `/sitemap.xml` generated and submitted to Google Search Console + Bing
- [ ] `/og-default.png` (1200×630) present; social cards preview correctly
- [ ] Core Web Vitals green on mobile
- [ ] "Last updated" dates on cornerstone content
