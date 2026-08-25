# CURRENT PROJECT STATE

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Base Epic: `epic/phase49-unified-product-slider-sync`
Active Phase: `49.3I`
Active Hotfix: `49.3I.20 — Visible Operator Panels`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA REQUIRED`
Production: `UNTOUCHED / NOT APPROVED`

## Current Position
49.3I.18 additive operator editing and 49.3I.19 canonical source identity are implemented on the feature branch.

Owner Windows QA then exposed a UI-composition defect: the new bulk image panel and source-identity/AI rebuild panels existed in code, but they were packed after large `fill="both", expand=True` gallery/content panes. The controls could therefore be pushed below the visible viewport and appear to be missing from Product Workspace.

49.3I.20 is a layout-only hotfix that keeps the existing controls and commands intact and moves the already-created panels ahead of expandable content.

## Preserved 49.3I.19 Source Identity Contract
- generic English/Persian model-number titles are non-authoritative,
- valid scraped/page title is preferred,
- exact MakerWorld `/models/<id>-<slug>` URL provides deterministic fallback identity,
- candidate source title is canonicalized before candidate upsert,
- source title is canonicalized again before Add-to-Products persistence,
- Product AI source context canonicalizes legacy products before generation,
- Product Workspace can repair source title and rebuild AI content without delete/reimport.

Acceptance fixtures remain:
- `https://makerworld.com/en/models/2845731-cake-stand?...` → `Cake Stand`,
- `https://makerworld.com/en/models/2896217-ribbed-cake-stand-cookie-platter?...` → `Ribbed Cake Stand Cookie Platter`.

## Implemented 49.3I.20 Visible Layout Contract
### Stage 3 — Images
The panel `عملیات گروهی همه تصاویر منتخب سایت` is moved before the existing image toolbar/gallery so it is visible immediately when stage 3 opens.

### Stage 4 — Content / SEO
Visible order is:
1. `هویت واقعی محصول در منبع — قبل از ترجمه و SEO`,
2. `اصلاح نام محصول و بازسازی متن / SEO`,
3. existing content toolbar/editor.

49.3I.20 does not recreate or replace AI/metadata controls. It only reorders already-created pack-managed panels after 49.3I.18 and 49.3I.19 have mounted them.

## Git State
Verified feature branch remote HEAD before 49.3I.20 work:
- `6c9cb06a573f6251c55e491ce187bab27fd7ffd7`.

49.3I.20 implementation commits so far:
- `cf634206da426e6627cb47e9a860fd6591b169b9` — add layout-only visibility module,
- `74b7de97531dae5346c864f06665269ffd8d84a3` — add focused layout regression tests,
- `658311877a7d79b1a2d923e91054626728d2ae37` — wire 49.3I.20 after 49.3I.18/49.3I.19 composition,
- `b0017bf4ba2bb94f6b6466b05989994fb8b5208b` — add 49.3I.20 phase documentation.

Documentation commits may follow on the same branch. Always fetch the live remote HEAD before Local QA; do not rely on a stale chat-pinned SHA.

## Files Changed for 49.3I.20
- added `catalog_center/app/phase49_3i20_visible_operator_panels.py`,
- updated `catalog_center/app/phase49_3i_pricing_modes.py`,
- added `catalog_center/tests/test_phase49_3i20_visible_operator_panels.py`,
- added/updated Phase49.3I documentation.

## Database / Migration / Media / Secret Safety
- Django migration: `NONE`,
- Catalog schema migration: `NONE`,
- no reset/drop/truncate,
- no media/history deletion,
- no secret-storage change,
- no AI provider/model logic change,
- no pricing/publish/FTP/Bridge contract change,
- Production untouched.

## Test Status
GitHub implementation and focused unit test code are committed. Canonical Windows Local execution is still required before this hotfix can be marked Local Tested or Accepted.

## Exact Next Task — Windows 49.3I.20 Acceptance
1. close Catalog Center,
2. Local path is `D:\projects\3DPrintHub`,
3. verify worktree is clean before branch switch/pull,
4. fetch/prune, switch to `agent/phase49-3i18-operator-bulk-ai-rebuild`, ff-only pull live remote HEAD,
5. verify Local HEAD equals fetched remote HEAD,
6. compile 49.3I.20 + touched composition modules,
7. run 49.3I.20 + 49.3I.19 + 49.3I.18 focused tests,
8. run inherited 49.3I.16/15/discovery regressions,
9. run `catalog_center\launch.py --verify-only`,
10. launch Catalog Center and verify stage 3 bulk-image panel is visible at the top,
11. verify stage 4 source-identity and AI rebuild panels are visible above the editor,
12. open existing bad product `2896217`; repair source title and expect `Ribbed Cake Stand Cookie Platter`,
13. run source repair + full AI rebuild and inspect Persian title, descriptions, SEO, image Alt/Title/Caption,
14. verify `2845731` resolves to `Cake Stand`,
15. verify 49.3I.18 clipboard/bulk metadata/manual Persian authoritative-name paths still work,
16. chain the existing 49.3I.17 baseline gate.

## Release Gate After Windows PASS
- exactly one `LOCAL PUBLISH ONLY`,
- Local Django Store/Admin/Product/Media/SEO E2E,
- explicit owner approval,
- read-only Production path/branch/venv/MySQL/backup/rollback verification,
- deploy only the approved GitHub snapshot,
- Production HTTP/data/media verification.

## Next Product Phase
After Catalog Production verification: Store ZarinPal request/callback/verify + Sandbox E2E while retaining bank transfer.
