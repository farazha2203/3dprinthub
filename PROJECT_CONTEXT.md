# PROJECT_CONTEXT — 3DPrintHub

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.16 — Resilient Acquisition Fallback + Cached Candidate Reuse`
Status: `MERGED / ALL REQUIRED CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Operating Rule
GitHub/Repository is permanent source of truth.
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI → WINDOWS PULL --FF-ONLY → LOCAL GATE → MANUAL QA → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION BACKUP/DEPLOY/VERIFY`.

No direct Production edits. Dirty Local/Host stops for inspection. New features are additive unless the owner explicitly changes the business contract.

## Canonical Paths
Windows project: `D:\projects\3DPrintHub`
Windows Catalog Center: `D:\projects\3DPrintHub\catalog_center`
Windows venv: `D:\projects\3DPrintHub\.venv`
Windows Django DB: `D:\projects\3DPrintHub\db.sqlite3`
Windows Catalog DATA: `D:\projects\3dprinthub-catalog-manager`
Windows Catalog SQLite: `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`
Production project: `/home/sfkilvrs/3dprinthub`
Production venv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`
Production DB: MySQL `sfkilvrs_EmiAdmin_3dprinthub`

## Acquisition Contract
Primary business path:
`Search/Listing URL → max 100 products → max 20 images/product → resilient discovery → resilient local image staging → visible image count → select → Add to Products / Archive → Product Workspace`.

Final discovery fallback:
`locator-safe → HTTP/HTML → attached Chrome 9222 → cached candidate DB`.

Final image fallback:
`locator-safe fresh → HTTP parse/downloader → mature Classic DOM → attached Chrome 9222 → listing thumbnail`.

Rules:
- one method failure triggers the next method,
- prior candidate discovery for the same listing is reusable,
- candidate manifests record method traces,
- at least one real local staged image is required before readiness/Add-to-Products,
- one candidate failure does not abort the batch,
- no Rich Direct Full Fetch dependency in the bulk path,
- Archive/Block/dedupe and mature top controls remain,
- AI/provider/SEO/pricing/publish/FTP/Bridge/credentials unchanged.

## Product Workspace / AI / Pricing
Images remain contain-fit `228x171`.
AI remains observable with sanitized request/response/error, 90s title / 210s All-Fields watchdog, stale-result protection, exact provider schema and manual-override protection.
Pricing remains Fixed / Range / Formula independent.

## Latest Validation / Merge
PR `#62` merged.
- final head `8f4fbe6d0264f673d0e6564a4ed1e383db023ab6`,
- merge commit `44216546162fead0b752d92cf6cae8d658f034f2`.

All final-head workflows SUCCESS: 49.3I.16 `32645660164`, 49.3I `32645660154`, 49.3I.15 `32645660045`, 49.3I.14 `32645660071`, 49.3H `32645660135`, 49.3G `32645660118`, Full Epic + Windows Catalog + Full Django `32645660123`.

Django migration: NONE. Catalog schema migration: NONE. Production untouched.

Relevant latest records: `ERR-49-034`, `REQ-49I-023`.

## Exact Next Gate
Windows: live ff-only pull current Epic → `RUN_PHASE49_3I16_FALLBACK_GATE.ps1 -LaunchApp` → MakerWorld cake+stand 10×10 → verify fallback/cached candidate reuse/image staging → Add 2–3 Products → Archive one → open one Product.

Then exactly one Local Publish E2E → owner approval → Host/MySQL/backup/rollback verification → GitHub-only Production deploy.

## Next Product Phase
After Catalog Production verification: normal Store ZarinPal request/callback/verify + Sandbox E2E, preserving bank transfer.
