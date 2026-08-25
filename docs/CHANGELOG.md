# PROJECT CHANGELOG

Record meaningful changes only. Older detailed entries remain available in Git history.

## 2026-08-25 — Phase49.3I.20 Visible Operator Panels

### Owner Evidence
49.3I.18/49.3I.19 controls were present in source but were not visible in normal Product Workspace use. The bulk-image panel and source-identity/AI rebuild panels were packed after large expandable gallery/content panes and could be pushed below the visible viewport.

### Root Fix
- add a layout-only final composition layer,
- keep the existing 49.3I.18/49.3I.19 controls and commands intact,
- move `عملیات گروهی همه تصاویر منتخب سایت` before the expandable image gallery,
- move `هویت واقعی محصول در منبع — قبل از ترجمه و SEO` to the top of Content/SEO,
- keep `اصلاح نام محصول و بازسازی متن / SEO` immediately below it,
- preserve mature toolbar/editor below both panels,
- add focused regression tests for final visible order and safe no-op behavior.

Implementation:
- `catalog_center/app/phase49_3i20_visible_operator_panels.py`,
- `catalog_center/tests/test_phase49_3i20_visible_operator_panels.py`,
- final wiring in `catalog_center/app/phase49_3i_pricing_modes.py`.

No migration. No AI provider/model change. No pricing/publish/FTP/Bridge change. Production untouched. Windows Local QA pending.

## 2026-08-23 — Phase49.3I.19 Canonical Source Identity Before AI

### Owner Evidence
A MakerWorld product with exact URL `2896217-ribbed-cake-stand-cookie-platter` entered Catalog with a generic model-number title. Image metadata, Persian title, descriptions and SEO were then generated from that wrong identity.

### Root Fix
- reject generic source titles such as `Model <id>`, `MakerWorld model <id>` and Persian equivalents,
- preserve a valid scraped/page title when available,
- use the exact MakerWorld model URL slug as deterministic fallback identity,
- canonicalize before candidate persistence and again before Add-to-Products,
- canonicalize legacy Product source context before AI,
- add Product Workspace actions to repair source title and optionally rebuild all AI text/SEO from the corrected source identity,
- keep 49.3I.18 manual authoritative Persian title and bulk image metadata editing unchanged.

Focused tests include:
- `2845731-cake-stand` → `Cake Stand`,
- `2896217-ribbed-cake-stand-cookie-platter` → `Ribbed Cake Stand Cookie Platter`,
- generic model-number placeholders never become authoritative.

Implementation anchor: `d9d3d617ed22dd3096379e668697f0f9fab87ca0`. Windows Local gate pending. No migration. Production untouched.

## 2026-08-23 — Phase49.3I.18 Operator Editing / Bulk Image Metadata / Authoritative AI Rebuild
- global Windows clipboard contract for editable Tk/Ttk fields,
- bulk image filename/Alt/Title/Caption operations using existing metadata contracts,
- explicit operator-authoritative Persian product name,
- replace wrong product name across generated editorial fields,
- full AI rebuild path for operator-confirmed identity,
- additive-only workspace composition; no DB migration; Production untouched.

## 2026-08-23 — Phase49.3I.17 Single Active AI Runtime

### Windows Evidence
Product Workspace AI could remain at `در حال اتصال به هوش مصنوعی`, appeared to enumerate many models/providers despite one saved active AI, sometimes required Task Manager, and a stale callback raised `TclError: invalid command name ...listbox`.

### Implemented
- Product AI now reads exactly one saved `ai_provider` and that provider's saved model,
- API key comes only from the secure slot for that exact provider,
- legacy cross-provider fallback based on whichever secret exists is rejected,
- hidden AI-on-open is disabled; Product AI requires explicit operator action,
- Product-bound connection preflight is local and no longer downloads `/models` before every content request,
- Google Product AI uses the exact saved model without a model-list preflight,
- explicit AI Settings model search/test remain live,
- stale destroyed-widget callbacks are logged/suppressed and Product busy flags are released,
- existing trace/schema repair/watchdog/Stop Waiting/stale-result/manual-override contracts remain.

### Validation / Merge
PR #63 merged into `epic/phase49-unified-product-slider-sync`.
- final runtime head `2917a3db5225abac71fc3e80b64ad439acd7a4d0`,
- merge commit `7f835f573b92e3aded6275c9421770c0c47d947a`.

Final runtime-head SUCCESS:
- 49.3I.17 `32649623837`,
- 49.3I `32649623808`,
- 49.3I.16 `32649623695`,
- 49.3I.15 `32649623705`,
- 49.3I.14 `32649623679`,
- 49.3H `32649623825`,
- 49.3G `32649623755`,
- Full Phase49 + Windows Catalog regressions + Full Django `32649623804`.

Django migration: NONE. Catalog schema migration: NONE. Production untouched.

## 2026-08-23 — Phase49.3I.16 Resilient Acquisition Fallback + Cached Candidate Reuse
- final discovery ladder: locator-safe Playwright → HTTP/HTML → attached Chrome 9222 → cached candidate DB,
- image fallback: locator-safe → HTTP → mature Classic DOM → Chrome 9222 → listing thumbnail,
- method trace persisted,
- cached correct candidates may be reused,
- no Rich Direct dependency returned,
- PR #62 merged; all required CI success; no migration; Production untouched.

## 2026-08-23 — Phase49.3I.15 Bulk Exact-Page Images + Add-to-Products
- product max 100 / image max 20,
- exact-page discovery + local image staging,
- no Rich Direct dependency in bulk flow,
- per-row staged image count,
- selected rows Add to Products without another network Full Fetch,
- local staging guard requires a real downloaded image,
- Archive/Block/dedupe and mature controls preserved,
- PR #61 merged; all required CI success; no migration; Production untouched.

## 2026-08-23 — Phase49.3I.14 Restore Mature Scan Controls + Single-Product Route
- restored mature top acquisition controls,
- compatibility single Product uses mature BaseApp scan path,
- Rich Direct remains optional,
- PR #60 merged; all required CI success; no migration; Production untouched.

## 2026-08-23 — Phase49.3I.13 Windows URL Paste + Batch Recovery
- explicit Windows paste actions,
- background batch behavior,
- selected candidate technical error exposed,
- PR #59 merged; all required CI success.

## Earlier Phase49.3I Foundations
Preserved: Product Workspace routing, contain-fit gallery, Fixed/Range/Formula independence, observable bounded AI, provider schema/trace, secure credentials, PS5.1 runner guard, live Git snapshot handoff, and Local/Production publish separation.
