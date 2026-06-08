import { describe, it, expect } from "vitest";
import {
  canonical,
  pageTitle,
  metaTags,
  faqJsonLd,
  jsonLdScript,
  SITE,
} from "../src/lib/seo";

describe("canonical", () => {
  it("builds an absolute URL from a path", () => {
    expect(canonical("/faq")).toBe(`${SITE.url}/faq`);
  });
  it("tolerates a missing leading slash", () => {
    expect(canonical("faq")).toBe(`${SITE.url}/faq`);
  });
});

describe("pageTitle", () => {
  it("appends the brand", () => {
    expect(pageTitle("How it works")).toBe("How it works · PlugPulse");
  });
  it("does not duplicate the brand on home", () => {
    expect(pageTitle("PlugPulse")).toBe("PlugPulse");
  });
});

describe("metaTags", () => {
  it("emits OpenGraph and Twitter tags with absolute image URLs", () => {
    const tags = metaTags({ title: "Home", path: "/" });
    const byKey = (k: string) =>
      tags.find((t) => t.property === k || t.name === k)?.content;
    expect(byKey("og:url")).toBe(`${SITE.url}/`);
    expect(byKey("twitter:card")).toBe("summary_large_image");
    expect(byKey("og:image")?.startsWith("https://")).toBe(true);
  });
});

describe("faqJsonLd", () => {
  it("produces a FAQPage with question entities", () => {
    const data = faqJsonLd([{ question: "Is it free?", answer: "Yes." }]);
    expect(data["@type"]).toBe("FAQPage");
    const entities = data.mainEntity as Array<Record<string, unknown>>;
    expect(entities).toHaveLength(1);
    expect(entities[0]["@type"]).toBe("Question");
  });
});

describe("jsonLdScript", () => {
  it("escapes angle brackets to prevent script-tag breakout", () => {
    const out = jsonLdScript({ x: "</script>" });
    expect(out).not.toContain("</script>");
    expect(out).toContain("\\u003c");
  });
});
