# PROJECT_CONTEXT — 3DPrintHub

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.15 — Bulk Exact-Page Images + Add-to-Products`
Status: `MERGED / ALL REQUIRED PR CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Operating Rule
GitHub/Repository is permanent source of truth.
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI → WINDOWS PULL --FF-ONLY → LOCAL GATE → MANUAL QA → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION BACKUP/DEPLOY/VERIFY`.

No direct Production edits. No project ZIP/Patch/source through Chat. Dirty Local/Host stops for inspection. New UI/features are additive unless the owner explicitly changes the business contract.

## Canonical Paths
Windows project: `D:\projects\3DPrintHub`
Windows Catalog Center: `D:\projects\3DPrintHub\catalog_center`
Windows venv: `D:\projects\3DPrintHub\.venv`
Windows Django DB: `D:\projects\3DPrintHub\db.sqlite3`
Windows Catalog DATA: `D:\projects\3dprinthub-catalog-manager`
Windows Catalog SQLite: `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`
Windows backups: `D:\projects\3dprinthub-backups`
Production project: `/home/sfkilvrs/3dprinthub`
Production venv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`
Production DB: MySQL `sfkilvrs_EmiAdmin_3dprinthub`

Always re-read PATHS/HOST_CONSTRAINTS before Local/Host operations.

## Acquisition Contract — 49.3I.15
Mature compatibility path remains available:
- source/mode/method/URL/query controls,
- `شروع اسکن` → original BaseApp worker,
- Stop / smart direct / discovery actions preserved.

Primary exact-page business path:
`Search/Listing URL → product limit (max 100) → images/product (max 20) → verified link discovery → local staged image collection with mature Classic browser helpers → visible image count → select → Add to Products / Archive`.

For this bulk path:
- no Rich Direct `extract_direct_link` dependency,
- candidate image manifests live under persistent Catalog DATA,
- candidate DB schema is unchanged,
- at least one local image download is required before readiness/Add-to-Products,
- Add-to-Products creates a review-state Product from staged identity/title/images without another network fetch,
- existing/blocked dedupe remains,
- one failure does not abort the batch,
- safe Stop is checked between candidates.

The older one-thumbnail Preview→approved Full Fetch requirement is superseded only for this owner-approved exact-page bulk path.

## Product Workspace / AI / Pricing
Images remain fixed contain-fit `228x171` in Product Workspace.
AI remains observable with sanitized request/response/error, 90s title / 210s All-Fields watchdog, stale-result protection, current Provider/Model retry, exact provider schema and manual-override protection.
Pricing remains Fixed / Range / Formula independent.
Credentials remain in Windows Credential Store/environment.

## Latest Validation / Merge
PR `#61` merged.
- final PR head `5f96d890b2e31e1f1d670c8afb716a1da4fc88d3`,
- merge commit `953f975e883e6dfcbf61097ac8d324d68d4ca678`.

Final-head required workflows SUCCESS:
- 49.3I.15 `32641815323`,
- 49.3I `32641815273`,
- 49.3I.14 `32641815287`,
- 49.3H `32641815289`,
- 49.3G `32641815380`,
- Full Phase49 + Windows Catalog regressions + Full Django `32641815270`.

Django migration: NONE.
Catalog schema migration: NONE.
Production untouched.

## Relevant Error/Request
- previous regression: `ERR-49-032`,
- bulk business-flow correction: `ERR-49-033`,
- owner acceptance: `REQ-49I-022`.

## Exact Next Gate
Windows runs `RUN_PHASE49_3I15_BULK_GATE.ps1 -LaunchApp` after a live ff-only pull of the current Epic remote HEAD. Focused QA starts with 10×10, selects 2–3 rows, Add-to-Products, Archive one row, and verifies one Product gallery. If PASS, employee batches may use 30/50/100 products and 10/20 images.

Then exactly one Local Publish E2E → owner approval → Host/MySQL/backup/rollback verification → GitHub-only Production deploy.

## Next Product Phase
After Catalog deploy: normal Store ZarinPal request/callback/verify + Sandbox E2E, preserving bank transfer.
