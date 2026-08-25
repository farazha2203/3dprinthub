# PROJECT CHANGELOG

Record meaningful changes only. Older detailed entries remain available in Git history.

## 2026-08-25 — Phase49.3I.21 Observable AI Jobs + Link-Grounded Full Refresh

### Owner Evidence
- `تکمیل هوشمند همه فیلدها با AI` and other AI actions could stay at `در حال اتصال به هوش مصنوعی` for a long period,
- source-title reread worked, while `اصلاح عنوان منبع + بازسازی کامل AI` could remain waiting,
- product `2896217-ribbed-cake-stand-cookie-platter` had the correct English source identity after reread but still retained a generic Persian model-number title because the AI rebuild did not complete.

### Verified Root Cause
The provider chat path used a 210-second timeout, exactly matching the 03:30 Task Center wait ceiling. This is a provider/network wait and observability problem, not evidence that the database refuses AI field edits.

### Implemented
- global provider request guard with default 75-second POST ceiling and 20..120-second environment override,
- request-start / finish / timeout / error events using the existing redacted diagnostics system,
- URL grounding for `AIContentService.enrich_product`,
- new Product Workspace panel `AI حرفه‌ای — تکمیل کامل از لینک + عیب‌یابی زنده`,
- one-click `تکمیل همه اطلاعات بر اساس لینک محصول`,
- source page fetch + parse + canonical identity + sanitized fact pack,
- AI receives URL and source facts rather than relying on a generic persisted title,
- live job dialog with elapsed time, stages, cancel and copy-report actions,
- response preview before any product update,
- explicit operator confirmation before unified content/SEO/image-metadata apply,
- cancellation guard prevents late response application and releases the local busy state,
- Diagnostics export remains secret-redacted and local.

No Django migration. No Catalog schema migration. No Production change. Windows Local QA pending.

Implementation files:
- `catalog_center/app/phase49_3i21_observable_ai_link_refresh.py`
- `catalog_center/app/phase49_3i21_cancel_guard.py`
- `catalog_center/app/phase49_3i_pricing_modes.py`
- `catalog_center/tests/test_phase49_3i21_observable_ai_link_refresh.py`
- `docs/phases/PHASE49_3I21_OBSERVABLE_AI_LINK_REFRESH.md`

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

## Earlier Phase49.3I Foundations
Preserved: Product Workspace routing, contain-fit gallery, Fixed/Range/Formula independence, provider schema/trace, secure credentials, PS5.1 runner guard, exact-page acquisition, Add-to-Products, archive/block/dedupe, and Local/Production publish separation.