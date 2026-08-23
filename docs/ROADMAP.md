# PROJECT ROADMAP

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Epic: `Phase49 — Unified Product / Slider / Catalog Sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.15 — Bulk Exact-Page Images + Add-to-Products`
Status: `PR #61 IN VALIDATION / WINDOWS QA NEXT`
Production: `UNTOUCHED / NOT APPROVED`

## Permanent Delivery Order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI → WINDOWS PULL --FF-ONLY → LOCAL GATE → MANUAL QA → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION BACKUP/DEPLOY/VERIFY`

## Immediate Business Priority
1. finish and merge 49.3I.15 only after final CI success,
2. focused Windows test of exact-page bulk acquisition,
3. exactly one Local Publish E2E,
4. explicit owner approval,
5. verify Production branch/path/MySQL/backup/rollback and deploy approved GitHub snapshot,
6. then Store-cart ZarinPal integration + Sandbox E2E.

## Phase49.3I Path
`Discovery Review → PS5.1 Guard → Gallery/AI First-Paint → Live Git Snapshot → Explorer/Routing → Selection Guard → Credential Persistence → Provider/Preview Recovery → Observable AI → SEO/Source → AI Trace → Provider Schema → Exact-Page UI/Image Fit → Paste/Batch Recovery → Mature Scan Restoration → Bulk Exact-Page Images/Add-to-Products`.

## 49.3I.15 — New Canonical Exact-Page Business Flow
Owner explicitly replaced the old one-thumbnail Preview→per-product Full Fetch acceptance for the exact-page operator workflow because the per-product Direct route is the recurring business blocker.

New flow:
`Exact Search/Listing URL → select 10/20/30/50/100 products → select 5/10/15/20 images per product → discover links → collect staged images with mature Classic browser helpers → display image count → select wanted rows → Add to Products → Archive unwanted`.

Contracts:
- product hard max 100,
- image hard max 20,
- no Rich Direct `extract_direct_link` dependency in the bulk path,
- per-candidate image manifest stored under persistent Catalog DATA without DB schema migration,
- Add-to-Products is local DB materialization from staged identity/title/images, not another network Full Fetch,
- existing/blocked dedupe remains,
- Stop between candidates,
- one candidate error does not abort the rest,
- restored mature top controls remain visible and untouched,
- AI/SEO/pricing/publish/FTP/Bridge/credentials unchanged.

## Feature Validation
PR `#61` head before documentation sync: `a7cb319c2723ae2f9cfe87a1a00c8b33e7fcf619`.
Observed SUCCESS:
- 49.3I.15 `32641268643`,
- 49.3I `32641268627`,
- 49.3I.14 `32641268644`,
- 49.3H `32641268659`,
- 49.3G `32641268651`.
Full Phase49 + Full Django `32641268645` must also be SUCCESS on the final feature head before merge.

Django migration: NONE in targeted CI.
Catalog schema migration: NONE.
Production: untouched.

## Focused Windows Gate After Merge
1. clean worktree + live fetch/ff-only,
2. `RUN_PHASE49_3I15_BULK_GATE.ps1 -LaunchApp`,
3. exact MakerWorld page with 10 products × 10 images first,
4. verify progress and image counts,
5. select 2–3 rows → Add to Products without Direct Full Fetch,
6. Archive one row,
7. open one added product and verify images.

If PASS, do one Local Publish E2E and move immediately to Production gate/deploy.

## Next Product Phase
Store checkout remains manual bank transfer. Next: ZarinPal request/callback/verify, Sandbox E2E, then one owner-approved low-value live payment.
