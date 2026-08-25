# PROJECT CHANGELOG

Record meaningful changes only. Older detailed entries remain available in Git history.

## 2026-08-25 — Phase49.3I.29 Structured Web Product Presentation

### Owner Evidence
- Local Publish succeeded, but the Product detail page exposed `technical_notes` as a large raw JSON dump.
- customer-facing content included duplicated Catalog payloads, `-` placeholders and internal AI/audit fields that were not meaningful to buyers.

### Implemented
- added `store/templatetags/store_product_presentation.py` as a presentation-only compatibility layer,
- legacy Catalog JSON is parsed server-side and filtered through an explicit customer-safe allowlist,
- public Product page no longer renders `product.technical_notes|linebreaks`,
- organized highlights, technical/build facts, materials, colors, category path and source attribution into storefront sections,
- missing designer/license placeholders are suppressed,
- internal AI provider/model, fingerprint/hash, batch UUID and workflow fields are never returned to the template,
- existing AI-generated Persian Product description/use-description/technical features/sales bullets are reused without any web-time AI request,
- added focused regression tests for legacy JSON parsing, internal-field suppression and template non-exposure.

No Django migration. No Catalog schema migration. Production untouched. Windows Web QA required before deploy.

## 2026-08-25 — Phase49.3I.28 Exact-Link Canonical Title Call Contract
- fixed exact-link canonical source title adapter after Windows QA exposed duplicate `current_title` binding,
- preserved mature 49.3I.19 canonical source identity contract,
- no provider/model/image-upload behavior changed,
- focused regression and Windows gate updated.

No migration. Production untouched.

## 2026-08-25 — Phase49.3I.27 Exact-Link Category Provider Crash Fix

### Owner Evidence
- pressing `تکمیل همه اطلاعات بر اساس لینک محصول` immediately raised `AttributeError: 'Database' object has no attribute 'categories'` before source/AI progress could start.

### Root Cause / Fix
- 49.3I.26 called `workspace.db.categories()` although the mature Catalog category contract lives on `App.get_all_categories()` and `Database` intentionally has no category repository API.
- added a final additive workspace bridge that exposes the existing App category rows to the exact-link 49.3I.26 path without schema/database changes.
- removed the ineffective `if hasattr(Database, "categories")` normalization assumption from the composition comment/path.
- added focused regression coverage proving a Workspace with a Database that has no `categories` attribute can still start the exact-link action through the App category provider.
- Windows local gate now compiles/tests 49.3I.27 first.

No Django migration. No Catalog schema migration. Production untouched. Windows Local QA required.

## 2026-08-25 — Phase49.3I.26 Unified Exact-Link Completion + Canonical Wizard + Vertical Gallery + Product Archive

### Owner / Diagnostic Evidence
- 49.3I.25 Content-first ordering still produced a stage-lock popup and did not remove the practical Basic Info prerequisite.
- the old 49.3G after-idle horizontal gallery layout overrode the later five-column intention.
- exact-link completion still left Image SEO/Metadata work for a second AI action.
- fresh diagnostic hang dump captured an 8.110s UI lag while image finalization was blocked in SSL/HTTP download code.
- Product operator requested 0–100% progress/current stage, a two-minute AI ceiling, no image upload to AI, bulk archive/delete-block actions, default five images and one source-page screenshot.

### Implemented
- restored canonical stage order: Basic Info, Commerce, Images, Content/SEO, Source/License, Slider, Review/Publish.
- all stages remain manually navigable; readiness blocks publish rather than browsing/editing stages.
- exact-link completion shows determinate progress and explicit stages; timeout is 120 seconds and timeout handling rechecks the source URL separately.
- AI receives textual source/Product facts only; no selected image URL/file is sent to AI.
- one exact-link action now applies Product content/SEO plus image SEO text fields (filename/Alt/Title/Caption/Keywords).
- physical image SEO finalization runs only when selected source images already exist locally; unified AI never starts hidden network image downloads just to finish metadata.
- final gallery composition overrides 49.3G horizontal layout with five cards per row and vertical scrolling.
- Product Workspace adds maximize/full-screen toggle.
- Products gallery adds per-card/group selection, bulk archive and identity-preserving delete/block. Published/synced cards use white border treatment.
- delete/block preserves source identity through existing blocked Product contract so the URL is not reacquired.
- new acquisition default is five source images; one full-page source screenshot is added as an extra local, non-selected gallery reference.
- focused 49.3I.26 regression tests and Windows runner added.

No Django migration. No Catalog schema migration. Production untouched. Windows Local QA pending.

## 2026-08-25 — Phase49.3I.25 Product-First Workflow + Persistent Diagnostics + Startup No-AI

### Owner / Diagnostic Evidence
- Product workflow required Persian name before reaching the existing Content/SEO AI tools.
- Images were visually crowded rather than a simple five-card vertical grid.
- repeated Product edits/AI attempts involved many save/update groups and frequent reopen/hang cycles.
- fresh diagnostics proved hidden OpenAI `/models` still started after `startup_first_idle`, with HTTP 401 and UI lag.
- diagnostics recorded `cannot commit - no transaction is active` during overlapping worker/UI activity.
- exact-link source facts omitted weight even though the source parser already supports weight/time.
- historical logs must survive repeated application sessions.

### Implemented
- Product Stage 1 is Content/SEO; Basic Info is Stage 2; all stage buttons remain freely navigable.
- Basic Info exposes `🌐 تکمیل همه اطلاعات بر اساس لینک محصول`; legacy Product-data-send actions are redirected to the same workflow where present.
- exact-link preparation no longer calls the broad layered Product save chain.
- source facts carry available weight/print time; MakerWorld exact `profileId` weight is preferred when present.
- Images uses a single vertically scrollable gallery with five cards per row while preserving existing card controls/metadata.
- publish preflight shows missing items and can launch exact-link AI for AI-fillable gaps.
- model discovery is process-lifetime operator-explicit; startup/opening Product does not test provider connectivity.
- diagnostics use a dedicated SQLite connection with WAL/busy timeout; common Catalog DB operations are serialized.
- runtime text logging is append-only and no longer deletes old archives through finite rotation.
- focused 49.3I.25 regression tests added.

No Django migration. No Catalog schema migration. Production untouched. Windows Local QA pending.

## 2026-08-25 — Phase49.3I.24 Runtime Observability + AvalAI URL Tools + Startup No-Network Guard
- fixed invalid diagnostics call that could abort AvalAI execution,
- structured output uses schema-first bounded compatibility handling,
- deterministic source fetch and supported URL evidence preserved,
- obvious non-text Product AI models rejected,
- runtime lifecycle/heartbeat/hang diagnostics and Dashboard log controls added,
- initial constructor-time provider scan guard added; 49.3I.25 later strengthened it after diagnostics proved post-idle leakage.

## 2026-08-25 — Phase49.3I.23 AvalAI Exact Chat Contract + Publish SEO Audit
Exact saved AvalAI model, no hidden Product model scan, real source/operator text, actual JSON schema and sanitized contract trace. Core publish SEO path audited. No migration. Production untouched.

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
