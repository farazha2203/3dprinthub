# PROJECT CHANGELOG

Record meaningful changes only. Older detailed entries remain available in Git history.

## 2026-08-25 — Phase49.3I.30 Production Hero Product-Media Ownership

### Owner Evidence
- first real Catalog Site Publish produced a healthy Product page on Production,
- homepage Hero slide text rendered but selected images were blank,
- browser console showed HTTP 404 for `/media/store/imported-models/gallery/...`,
- Local `127.0.0.1:8000` rendered the same Hero correctly.

### Verified Root Cause
- Production non-DEBUG media routing intentionally exposes public Product/category/SEO media, not the imported Catalog working-gallery namespace,
- Phase49 Hero Studio preferred `ImportedPrintAssetImage.image.url`, so public Hero HTML referenced an internal media path,
- Local DEBUG served all media and masked the production-only ownership mismatch.

### Implemented
- added `website/phase49_3i30_hero_media_ownership.py` as the final Hero media resolver,
- public Hero now maps the selected imported-image basename to the Product-owned gallery copy under `/media/store/products/gallery/`,
- if the exact Product gallery image is unavailable, Product main image is used,
- remote source image is only a final fallback,
- imported working-media paths are never returned as the public Hero image,
- public media routing was not widened,
- focused regression test added at `website/test_phase49_3i30_hero_media_ownership.py`.

No migration. Production still runs the previously verified application commit until this hotfix passes Windows Local QA and is explicitly approved for deploy.

## 2026-08-25 — Phase49.3I.29 Production Deployment Verified

### Production Result
- owner-approved application commit `d27489f1c2e1d36e75fdadfa8ab24660d8bec720` deployed to Production,
- Production database verified as MySQL `sfkilvrs_EmiAdmin_3dprinthub`,
- rollback backup created successfully before migrations,
- pending Phase49 migrations `store.0030..0033` and `website.0020..0023` applied successfully,
- post-migration plan reported no pending operations,
- `collectstatic --noinput` completed,
- Passenger restart completed,
- public Home/Store/Product HTTP checks returned 200,
- Product presentation sanitization passed; raw Catalog JSON and internal AI/source-hash fields were not exposed,
- final Production worktree verified clean.

### Host Git Recovery
- explicit feature fetch succeeded but `git switch --track` rejected the fetched ref as a branch,
- the interrupted switch left the approved target tree staged while HEAD stayed on old `main`,
- recovery first proved staged index exactly matched the approved commit and worktree exactly matched index,
- local feature ref/HEAD were then completed without destructive reset/stash/delete,
- four historical host-only untracked files were backed up and removed only after successful deploy verification.

Known non-blocking warnings remain: CKEditor4 maintenance/security debt, `store.W026` in-memory realtime, and MySQL conditional unique-constraint warnings.

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

## 2026-08-25 — Phase49.3I.28 Exact-Link Canonical Title Call Contract
- fixed exact-link canonical source title adapter after Windows QA exposed duplicate `current_title` binding,
- preserved mature 49.3I.19 canonical source identity contract,
- no provider/model/image-upload behavior changed,
- focused regression and Windows gate updated.

## 2026-08-25 — Phase49.3I.27 Exact-Link Category Provider Crash Fix
- fixed `Database.categories` crash by bridging the mature `App.get_all_categories()` provider into exact-link completion,
- no schema change.

## 2026-08-25 — Phase49.3I.26 Unified Exact-Link Completion + Canonical Wizard + Vertical Gallery + Product Archive
- restored canonical Basic Info → Commerce → Images → Content/SEO → Source/License → Slider → Review/Publish order,
- free stage navigation with publish-only readiness gate,
- 0–100% observable exact-link Product AI, 120-second ceiling, text-only AI input and one-shot Product/image text metadata,
- five-column vertical Images layout,
- Product full-screen toggle,
- bulk archive and identity-preserving block/delete,
- default five images plus source-page screenshot.

## 2026-08-25 — Phase49.3I.25 Product-First Workflow + Persistent Diagnostics + Startup No-AI
- removed broad save storm from exact-link preparation,
- strengthened process-lifetime no-hidden-model-scan behavior,
- isolated diagnostics SQLite connection and serialized common DB operations,
- append-only runtime logs,
- source weight/print-time preservation.

## 2026-08-25 — Phase49.3I.24 Runtime Observability + AvalAI URL Tools + Startup No-Network Guard
- fixed invalid diagnostics call,
- schema-first AvalAI structured output,
- runtime lifecycle/heartbeat/hang diagnostics,
- non-text Product model rejection.

## 2026-08-25 — Phase49.3I.23 AvalAI Exact Chat Contract + Publish SEO Audit
Exact saved AvalAI model, no hidden Product model scan, real source/operator text, actual JSON schema and sanitized contract trace.

## 2026-08-25 — Phase49.3I.22 Tk Main-Thread AI Bridge + Scrollable Product Rail
Worker-originated Tk/Tcl calls isolated behind main-thread handoff; right Product rail gained vertical scrolling.

## 2026-08-25 — Phase49.3I.21 Observable AI Jobs + Link-Grounded Full Refresh
Bounded AI wait, request diagnostics, exact-link grounding, preview/apply flow and cancellation guard.

## 2026-08-25 — Phase49.3I.20 Visible Operator Panels
Final layout keeps mature controls visible while preserving existing Product actions.

## 2026-08-23 — Phase49.3I.19 Canonical Source Identity Before AI
Canonical source identity is resolved before persistence and AI.

## 2026-08-23 — Phase49.3I.18 Operator Editing / Bulk Image Metadata / Authoritative AI Rebuild
Global clipboard support, bulk image metadata editing and operator-authoritative Product AI rebuild.
