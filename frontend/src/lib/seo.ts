/**
 * SEO helpers: build canonical URLs, social meta tags, and JSON-LD structured
 * data consistently across pages. Pure functions so they're easy to unit-test
 * and to render server-side (important — AI crawlers read server HTML).
 */

export const SITE = {
  name: "PlugPulse",
  // TODO: replace with your real production domain.
  url: "https://plugpulse.app",
  description:
    "Find EV chargers that actually work right now — community-verified reliability, open data, free.",
  defaultImage: "/og-default.png",
  twitter: "@plugpulse",
  locale: "en_US",
} as const;

export interface PageSeo {
  title: string;
  description?: string;
  /** Path beginning with "/", e.g. "/faq". */
  path: string;
  image?: string;
  type?: "website" | "article";
}

/** Absolute canonical URL for a path. */
export function canonical(path: string): string {
  const clean = path.startsWith("/") ? path : `/${path}`;
  return new URL(clean, SITE.url).toString();
}

/** Full page title with the site suffix (avoids duplicating the brand on home). */
export function pageTitle(title: string): string {
  return title === SITE.name ? title : `${title} · ${SITE.name}`;
}

export interface MetaTag {
  name?: string;
  property?: string;
  content: string;
}

/** Standard + OpenGraph + Twitter meta tags for a page. */
export function metaTags(p: PageSeo): MetaTag[] {
  const description = p.description ?? SITE.description;
  const url = canonical(p.path);
  const image = canonical(p.image ?? SITE.defaultImage);
  const type = p.type ?? "website";
  return [
    { name: "description", content: description },
    { property: "og:site_name", content: SITE.name },
    { property: "og:title", content: pageTitle(p.title) },
    { property: "og:description", content: description },
    { property: "og:type", content: type },
    { property: "og:url", content: url },
    { property: "og:image", content: image },
    { property: "og:locale", content: SITE.locale },
    { name: "twitter:card", content: "summary_large_image" },
    { name: "twitter:site", content: SITE.twitter },
    { name: "twitter:title", content: pageTitle(p.title) },
    { name: "twitter:description", content: description },
    { name: "twitter:image", content: image },
  ];
}

// --- JSON-LD structured data (helps both classic rich results and AI parsing) ---

export function organizationJsonLd(): Record<string, unknown> {
  return {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: SITE.name,
    url: SITE.url,
    logo: canonical("/logo.png"),
    sameAs: ["https://github.com/AayushCharde/plugpulse"],
  };
}

/** PlugPulse is a free web application — describe it for app rich results. */
export function webApplicationJsonLd(): Record<string, unknown> {
  return {
    "@context": "https://schema.org",
    "@type": "WebApplication",
    name: SITE.name,
    url: SITE.url,
    applicationCategory: "TravelApplication",
    operatingSystem: "Any (Progressive Web App)",
    description: SITE.description,
    offers: { "@type": "Offer", price: "0", priceCurrency: "USD" },
  };
}

export interface FaqItem {
  question: string;
  answer: string;
}

/** FAQPage schema — answer-first content is exactly what AI engines cite. */
export function faqJsonLd(items: FaqItem[]): Record<string, unknown> {
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: items.map((it) => ({
      "@type": "Question",
      name: it.question,
      acceptedAnswer: { "@type": "Answer", text: it.answer },
    })),
  };
}

/** Serialize a JSON-LD object for embedding in a <script type="application/ld+json">. */
export function jsonLdScript(data: Record<string, unknown>): string {
  // Escape "<" to avoid breaking out of the script tag.
  return JSON.stringify(data).replace(/</g, "\\u003c");
}
