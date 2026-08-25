# PROJECT CHANGELOG

Record meaningful changes only. Older detailed entries remain available in Git history.

## 2026-08-25 — Phase49.3I.23 AvalAI Exact Chat Contract + Publish SEO Audit

### Owner Evidence
- exact MakerWorld product link works directly in AvalAI,
- Catalog Center `تکمیل همه اطلاعات بر اساس لینک محصول` did not reliably return/apply useful content,
- canonical source title could be correct while the Persian product identity remained the generic MakerWorld model number.

### Verified Request Defect
The generic non-OpenAI structured path performed hidden model discovery, serialized Responses-style content wrappers into chat text, and required schema-shaped JSON without actually including the schema in the prompt.

### Implemented
- product-bound AvalAI uses the exact operator-saved model without hidden `/models`,
- sends normal Chat Completions `model + messages`,
- sends real source/operator text instead of serialized Responses wrappers,
- embeds the actual requested JSON schema,
- does not serialize image placeholder objects,
- preserves same model/prompt when falling back from unsupported `response_format`,
- adds sanitized contract trace and regression tests.

### Publish SEO Audit
Confirmed existing core path for meta title/description, canonical, robots, OG, Product/ProductGroup/Offer/Breadcrumb/Review/FAQ JSON-LD, image Alt import, safe public slug/redirect and `/sitemap.xml`. Dedicated Twitter title/description/image and `og:image:alt` remain non-blocking enhancement debt.

No Django migration. No Catalog schema migration. Production untouched. Windows Local QA pending.

## 2026-08-25 — Phase49.3I.22 Tk Main-Thread AI Bridge + Scrollable Product Rail
Worker-originated Tk/Tcl calls were isolated behind a Python queue/main-thread pump; right Product rail gained real vertical scrolling. No migration. Production untouched.

## 2026-08-25 — Phase49.3I.21 Observable AI Jobs + Link-Grounded Full Refresh
Bounded AI wait, request diagnostics, exact-link grounding, preview/apply flow and cancellation guard. No migration. Production untouched.

## 2026-08-25 — Phase49.3I.20 Visible Operator Panels
Final layout layer keeps 49.3I.18/19 commands intact and moves bulk-image and source/operator AI panels above expandable gallery/content panes. No migration. Production untouched.

## 2026-08-23 — Phase49.3I.19 Canonical Source Identity Before AI
Reject generic model-number source titles, prefer valid page title, use exact MakerWorld URL slug as deterministic fallback, canonicalize before persistence and AI. No migration. Production untouched.

## 2026-08-23 — Phase49.3I.18 Operator Editing / Bulk Image Metadata / Authoritative AI Rebuild
Global clipboard support, bulk image filename/Alt/Title/Caption editing, operator-authoritative Persian title and full AI rebuild. No migration. Production untouched.

## 2026-08-23 — Phase49.3I.17 Single Active AI Runtime
One saved Provider/Model/key path, no hidden provider fallback or hidden AI-on-open, Product generation without `/models` preflight, stale Tk callback protection. PR #63 merged and required CI passed.

## 2026-08-23 — Phase49.3I.16 Resilient Acquisition
Discovery/image fallback ladders, cached candidate reuse, no Rich Direct dependency. PR #62 merged and required CI passed.
