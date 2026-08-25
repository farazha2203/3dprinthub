# PROJECT CHANGELOG

Record meaningful changes only. Older detailed entries remain available in Git history.

## 2026-08-25 — Phase49.3I.24 Runtime Observability + AvalAI URL Tools + Startup No-Network Guard

### Owner / Diagnostic Evidence
- Catalog Center can become slow or `(Not Responding)` around launch/AI/close.
- AvalAI Product jobs failed with `audit_event() got an unexpected keyword argument 'provider'`.
- startup diagnostics showed automatic AvalAI/OpenRouter/OpenAI model-list traffic before operator action.
- OpenRouter accepted a Lyria music model and returned non-JSON marker output after a long call.
- AvalAI successful jobs take tens of seconds; a Grok response reported `num_sources_used=0`, so a URL in normal chat was not proof of page browsing.

### Implemented
- fixed the invalid diagnostics function call so observability cannot abort AvalAI Product execution,
- AvalAI Product structured output prefers strict `json_schema`, with `json_object` / prompt JSON compatibility fallback,
- keeps deterministic app-side source fetch/sanitization and adds explicit supported AvalAI URL-tool evidence for sparse source data,
- rejects/filters obvious non-text Product AI models,
- blocks hidden Provider `/models` network calls during application construction until first Tk idle,
- leaves explicit operator model search live after first paint,
- adds runtime lifecycle JSONL, Tk heartbeat lag events and all-thread hang dumps,
- adds Dashboard Program Log / AI Log / log folder / safe GitHub-ready diagnostic export,
- safe export includes redacted runtime/main/hang-log tails,
- stops labeling generic AvalAI model rows as free solely because generic pricing metadata is zero/missing.

No Django migration. No Catalog schema migration. Production untouched. Windows Local QA pending.

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
