# PROJECT ROADMAP

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Epic: `Phase49 — Unified Product / Slider / Catalog Sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.15 — Bulk Exact-Page Images + Add-to-Products`
Status: `MERGED / ALL REQUIRED PR CI SUCCESS / WINDOWS QA NEXT`
Production: `UNTOUCHED / NOT APPROVED`

## Permanent Delivery Order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI → WINDOWS PULL --FF-ONLY → LOCAL GATE → MANUAL QA → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION BACKUP/DEPLOY/VERIFY`

## Immediate Business Priority
1. focused Windows test of merged 49.3I.15 exact-page bulk acquisition,
2. exactly one Local Publish E2E after focused QA PASS,
3. explicit owner approval,
4. verify Production branch/path/venv/MySQL/backup/rollback,
5. deploy approved GitHub snapshot and verify Production,
6. then Store ZarinPal integration + Sandbox E2E.

## Phase49.3I Path
`Discovery Review → PS5.1 Guard → Gallery/AI First-Paint → Live Git Snapshot → Explorer/Routing → Selection Guard → Credential Persistence → Provider/Preview Recovery → Observable AI → SEO/Source → AI Trace → Provider Schema → Exact-Page UI/Image Fit → Paste/Batch Recovery → Mature Scan Restoration → Bulk Exact-Page Images/Add-to-Products`.

## 49.3I.15 — Canonical Exact-Page Business Flow
Owner explicitly replaced the old one-thumbnail Preview→per-product Full Fetch acceptance for the exact-page operator workflow because the per-product Direct route repeatedly blocked operations.

Flow:
`Exact Search/Listing URL → select 10/20/30/50/100 products → select 5/10/15/20 images per product → discover links → collect locally staged images with mature Classic browser helpers → display image count → select wanted rows → Add to Products → Archive unwanted`.

Contracts:
- product hard max 100,
- image hard max 20,
- no Rich Direct `extract_direct_link` dependency in the bulk path,
- per-candidate image manifest under persistent Catalog DATA without DB schema migration,
- readiness requires at least one successfully staged local image,
- Add-to-Products materializes staged identity/title/images into review-state Product rows without another network Full Fetch,
- existing/blocked dedupe remains,
- Stop between candidates,
- one candidate error does not abort the batch,
- restored mature top controls remain available,
- AI/SEO/pricing/publish/FTP/Bridge/credentials unchanged.

## GitHub Validation / Merge
PR `#61` merged into the Epic branch.
- final PR head `5f96d890b2e31e1f1d670c8afb716a1da4fc88d3`,
- merge commit `953f975e883e6dfcbf61097ac8d324d68d4ca678`.

Final-head SUCCESS:
- 49.3I.15 `32641815323`,
- 49.3I `32641815273`,
- 49.3I.14 `32641815287`,
- 49.3H `32641815289`,
- 49.3G `32641815380`,
- Full Phase49 + Windows Catalog regressions + Full Django `32641815270`.

Django migration: NONE.
Catalog candidate schema migration: NONE.
Production: untouched.

## Focused Windows Gate
1. Catalog Center closed; Local worktree must be clean,
2. live `git fetch --prune` + `git pull --ff-only` against current Epic remote HEAD,
3. `RUN_PHASE49_3I15_BULK_GATE.ps1 -LaunchApp`,
4. exact MakerWorld Search page with `10 products × 10 images`,
5. verify progress and per-row staged image count,
6. select 2–3 ready rows → Add to Products with no Direct Full Fetch,
7. Archive one unwanted row,
8. open one added Product and verify images.

If PASS, proceed immediately to exactly one Local Publish E2E; operational batches may then use 30/50/100 products and 10/20 images.

## Next Product Phase
After Catalog Production verification: Store checkout ZarinPal request/callback/verify, Sandbox E2E, then one owner-approved low-value live payment while bank transfer remains available.
