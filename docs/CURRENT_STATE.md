# CURRENT PROJECT STATE

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Base Epic: `epic/phase49-unified-product-slider-sync`
Active Phase: `49.3I`
Active Hotfix: `49.3I.19 — Canonical Source Identity Before AI`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA REQUIRED`
Production: `UNTOUCHED / NOT APPROVED`

## Current Position
49.3I.18 additive operator editing is present on the feature branch: global editable-widget clipboard support, bulk image metadata operations, operator-authoritative Persian identity replacement, and explicit full AI rebuild.

Owner QA then exposed a deeper upstream defect: MakerWorld acquisition could persist a generic fallback title such as `Model 2896217` / `MakerWorld model 2896217`. AI was not inventing the wrong product from nothing; it was receiving the wrong persisted source identity and generating title/SEO/image text from it.

49.3I.19 repairs that source-identity boundary before AI.

## Verified Root Cause
- 49.3I.16 classic-link and HTTP discovery fallbacks create `Model <external_id>` placeholder row text,
- mature candidate-title selection rejected only the bare ID, not the placeholder,
- 49.3I.15 Product payload copied candidate `source_title` directly,
- therefore generic placeholder identity could be persisted before AI,
- 49.3I.18 manual Persian correction fixed symptoms for one product but did not prevent bad source identity from entering Catalog.

## Implemented 49.3I.19 Contract
- generic English/Persian model-number titles are non-authoritative,
- valid scraped/page title is preferred,
- exact MakerWorld `/models/<id>-<slug>` URL provides deterministic fallback identity,
- candidate source title is canonicalized before candidate upsert,
- source title is canonicalized again before Add-to-Products persistence,
- Product AI source context canonicalizes legacy products before generation,
- Product Workspace now has `↻ بازخوانی و اصلاح عنوان منبع`,
- Product Workspace now has `🌐 اصلاح عنوان منبع + بازسازی کامل AI`,
- combined rebuild first repairs/persists source title, then regenerates Persian title/content/SEO/image metadata from the repaired identity,
- 49.3I.18 manual authoritative Persian name and bulk image operations remain available.

## Acceptance Fixtures
- `https://makerworld.com/en/models/2845731-cake-stand?...` → `Cake Stand`,
- `https://makerworld.com/en/models/2896217-ribbed-cake-stand-cookie-platter?...` → `Ribbed Cake Stand Cookie Platter`,
- `Model 2896217`, `MakerWorld model 2896217`, `مدل میکرورلد 2896217` must never be authoritative source titles.

## Git State
Before 49.3I.19 implementation, feature branch comparison against the Epic verified:
- base commit `eb17847d7669d8a07e857a6e7acc4a8012a94991`,
- feature ahead,
- feature behind `0`.

49.3I.19 code implementation anchor: `d9d3d617ed22dd3096379e668697f0f9fab87ca0`.
Required documentation commits follow that anchor on the same branch.

## Files Changed for 49.3I.19
- added `catalog_center/app/phase49_3i19_source_identity.py`,
- updated `catalog_center/app/phase49_3i12_runtime_bridge.py`,
- updated `catalog_center/app/phase49_3i_pricing_modes.py`,
- added `catalog_center/tests/test_phase49_3i19_source_identity.py`,
- added/updated required Phase49.3I documentation.

## Database / Migration / Media / Secret Safety
- Django migration: `NONE`,
- Catalog schema migration: `NONE`,
- no reset/drop/truncate,
- no media/history deletion,
- no secret-storage change,
- no pricing/publish/FTP/Bridge contract change,
- Production untouched.

## Test Status
GitHub code and focused test implementation are complete. This Chat runtime cannot substitute for the canonical Windows Catalog environment. Do not mark the hotfix complete until the exact Local Windows gate below passes.

## Exact Next Task — Windows Source Identity Acceptance
1. close Catalog Center,
2. Local path is `D:\projects\3DPrintHub`,
3. verify worktree/branch/HEAD before pull,
4. fetch/prune, switch to `agent/phase49-3i18-operator-bulk-ai-rebuild`, ff-only pull,
5. compile new/touched modules,
6. run focused 49.3I.19 + 49.3I.18 + 49.3I.16 + 49.3I.15 + discovery-review tests,
7. run `catalog_center\launch.py --verify-only`,
8. launch Catalog Center,
9. open existing bad product `2896217`, press `بازخوانی و اصلاح عنوان منبع`, expect `Ribbed Cake Stand Cookie Platter`,
10. press `اصلاح عنوان منبع + بازسازی کامل AI`; inspect Persian title, descriptions, SEO, image Alt/Title/Caption,
11. verify product `2845731` resolves to `Cake Stand`,
12. verify 49.3I.18 clipboard, bulk image metadata and manual Persian authoritative-name paths still work,
13. chain the existing 49.3I.17 baseline gate.

## Release Gate After Windows PASS
- exactly one `LOCAL PUBLISH ONLY`,
- Local Django Store/Admin/Product/Media/SEO E2E,
- explicit owner approval,
- read-only Production path/branch/venv/MySQL/backup/rollback verification,
- deploy only the approved GitHub snapshot,
- Production HTTP/data/media verification.

## Next Product Phase
After Catalog Production verification: Store ZarinPal request/callback/verify + Sandbox E2E while retaining bank transfer.