# Phase49.3I — Discovery Review + Product Explorer + Pricing + Observable AI

Updated: 2026-08-23
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Hotfix: `49.3I.19 — Canonical Source Identity Before AI`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA REQUIRED`
Production: `UNTOUCHED / NOT APPROVED`

## Goal
Deliver a business-usable Catalog Center that can bulk-acquire products from exact listing pages, preserve the real product identity before AI, survive source/browser method failures, edit products with deterministic AI, publish locally for E2E verification, then deploy only an approved GitHub snapshot.

## Canonical Acquisition Paths — Preserved
1. Mature compatibility path: `Top Scan Controls → BaseApp start_scan/_scan_worker → Product Workspace`.
2. Primary exact-page path: `Exact Search/Listing URL → product/image limits → resilient discovery → canonical source identity → resilient local image staging → review counts → Add selected to Products / Archive unwanted → Product Workspace`.

49.3I.16 remains authoritative for acquisition technique fallback:
- discovery: locator-safe → HTTP/HTML → attached Chrome 9222 → cached candidate DB,
- images: locator-safe → HTTP → mature Classic DOM → Chrome 9222 → listing thumbnail,
- product max 100 / image max 20,
- one candidate failure does not abort the batch,
- local image staging required,
- no Rich Direct `extract_direct_link` dependency in exact-page bulk intake.

## Source Identity Contract — 49.3I.19
### Trigger
Owner evidence showed MakerWorld product `2896217-ribbed-cake-stand-cookie-platter` represented by a generic model-number title. AI then correctly followed the wrong input and generated incorrect Persian title, descriptions, image metadata and SEO.

### Verified cause
49.3I.16 link-only fallback rows use placeholder `Model <external_id>`. The old candidate-title helper treated that placeholder as a valid title, and 49.3I.15 persisted it as Product `source_title` before AI.

### Runtime rule
- generic English/Persian model-number placeholders are rejected,
- valid scraped/page title wins,
- MakerWorld exact model URL slug is deterministic fallback,
- candidate upsert is canonicalized,
- Add-to-Products canonicalizes again before Product persistence,
- Product AI source context canonicalizes legacy products too,
- existing bad products get additive source-title repair + full AI rebuild controls,
- 49.3I.18 operator-authoritative Persian name and bulk image editing remain preserved.

Acceptance examples:
- `2845731-cake-stand` → `Cake Stand`,
- `2896217-ribbed-cake-stand-cookie-platter` → `Ribbed Cake Stand Cookie Platter`,
- `Model 2896217`, `MakerWorld model 2896217`, `مدل میکرورلد 2896217` are not authoritative.

## Operator Editing Contract — 49.3I.18 Preserved
- Ctrl+C/V/X/A and Windows clipboard behavior across editable Tk/Ttk fields,
- bulk image SEO filename / Alt / Title / Caption operations,
- operator-confirmed Persian product identity replacement across editorial fields,
- explicit full AI rebuild for operator-confirmed identity,
- additive-only UI changes.

## Product AI Runtime Contract — 49.3I.17 Preserved
- one explicitly saved Provider + Model,
- secure key only for that provider,
- no cross-provider fallback,
- no hidden AI-on-open,
- no Product `/models` preflight before generation,
- explicit Settings model search/test remain live,
- stale destroyed-widget callbacks do not crash Product Workspace,
- request/response/error trace, schema repair, watchdog/Stop Waiting and stale-result guards remain.

## Implementation Surfaces
- `catalog_center/app/phase49_3i19_source_identity.py`,
- `catalog_center/app/phase49_3i12_runtime_bridge.py`,
- `catalog_center/app/phase49_3i_pricing_modes.py`,
- `catalog_center/tests/test_phase49_3i19_source_identity.py`,
- 49.3I.18 existing operator editing module/tests,
- 49.3I.16/15 acquisition modules/tests preserved.

## Git / Validation State
Verified base of the feature branch against `epic/phase49-unified-product-slider-sync`: base commit `eb17847d7669d8a07e857a6e7acc4a8012a94991`; the branch was ahead and not behind before 49.3I.19 changes.

49.3I.19 implementation anchor: `d9d3d617ed22dd3096379e668697f0f9fab87ca0`; following commits update required project documentation.

Django migration: NONE. Catalog schema migration: NONE. Production untouched.

## Focused Windows Acceptance — Current Gate
1. close Catalog Center and verify clean Local worktree,
2. fetch/prune, switch to `agent/phase49-3i18-operator-bulk-ai-rebuild`, ff-only pull,
3. compile the touched modules,
4. run focused 49.3I.19 + 49.3I.18 + 49.3I.16 + 49.3I.15 + discovery-review tests,
5. run `catalog_center/launch.py --verify-only`,
6. launch Catalog Center,
7. open existing bad product `2896217` and use `بازخوانی و اصلاح عنوان منبع`; expect `Ribbed Cake Stand Cookie Platter`,
8. use `اصلاح عنوان منبع + بازسازی کامل AI`; verify Persian product title/text/SEO/image metadata follow the corrected cake-stand identity,
9. verify `2845731-cake-stand` resolves to `Cake Stand`,
10. verify global clipboard + bulk image metadata + manual Persian authoritative-name workflows from 49.3I.18 still work,
11. chain existing 49.3I.17 baseline gate before release.

## Release / Production Gate
Focused Windows PASS → exactly one `LOCAL PUBLISH ONLY` → Local Store/Admin/Product/Media/SEO E2E → explicit owner approval → read-only Host path/branch/venv/MySQL/backup/rollback verification → GitHub-only Production deploy → HTTP/data/media verification.

## Next Phase
Normal Store checkout: ZarinPal request/callback/verify + Sandbox E2E while bank transfer remains available.