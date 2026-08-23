# PROJECT_CONTEXT — 3DPrintHub

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.15 — Bulk Exact-Page Images + Add-to-Products`
Status: `PR #61 VALIDATED RUNTIME / WINDOWS QA PENDING`
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

Primary exact-page business path now is:
`Search/Listing URL → product limit (max 100) → images/product (max 20) → verified link discovery → staged image collection with mature Classic browser helpers → visible image count → select → Add to Products / Archive`.

For this exact-page bulk path:
- no Rich Direct `extract_direct_link` dependency,
- per-candidate staged image metadata lives under persistent Catalog DATA as JSON manifests,
- candidate DB schema is unchanged,
- Add-to-Products uses staged identity/title/images and creates a review-state Product without another network fetch,
- existing/blocked dedupe remains,
- one failure does not abort the whole batch,
- safe Stop is checked between candidates.

The older one-thumbnail-only Preview→approved Full Fetch requirement is superseded only for this owner-approved exact-page bulk path.

## Product Workspace / AI / Pricing
Images remain fixed contain-fit `228x171` in Product Workspace.
AI remains observable with sanitized request/response/error, 90s title / 210s All-Fields watchdog, stale-result protection, current Provider/Model retry, exact provider schema and manual-override protection.
Pricing remains Fixed / Range / Formula independent.
Credentials remain in Windows Credential Store/environment.

## Latest Validation
49.3I.15 runtime feature head: `a7cb319c2723ae2f9cfe87a1a00c8b33e7fcf619`.
PR: `#61`.

Successful runs:
- 49.3I.15 `32641268643`,
- 49.3I `32641268627`,
- 49.3I.14 `32641268644`,
- 49.3H `32641268659`,
- 49.3G `32641268651`,
- Full Phase49 + Full Django `32641268645`.

Runtime validation includes prior regression suites, no Rich Direct dependency in bulk flow, product limit 100, image limit 20, manifest/payload tests, compile, Django check/no-migration, Windows Catalog tests and Full Django suite.

Django migration: NONE.
Catalog schema migration: NONE.
Production untouched.

## Relevant Error/Request
- latest previous regression: `ERR-49-032`,
- new bulk business-flow correction: `ERR-49-033`,
- owner acceptance: `REQ-49I-022`.

## Employee Release Goal
After PR merge, Windows runs `RUN_PHASE49_3I15_BULK_GATE.ps1 -LaunchApp`. Focused QA starts with 10×10, selects 2–3 rows, Add-to-Products, Archive one row, and verifies one Product gallery. If PASS, employee batches may use 30/50/100 products and 10/20 images.

Then exactly one Local Publish E2E → owner approval → Host/MySQL/backup/rollback verification → GitHub-only Production deploy.

## Next Product Phase
After Catalog deploy: normal Store ZarinPal request/callback/verify + Sandbox E2E, preserving bank transfer.
