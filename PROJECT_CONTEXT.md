# PROJECT_CONTEXT — 3DPrintHub

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.17 — Single Active AI Runtime`
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

## Acquisition Contract — Preserved 49.3I.16
Primary path:
`Search/Listing URL → max 100 products → max 20 images/product → resilient discovery → resilient local image staging → visible image count → select → Add to Products / Archive → Product Workspace`.

Discovery fallback: `locator-safe → HTTP/HTML → attached Chrome 9222 → cached candidate DB`.
Image fallback: `locator-safe → HTTP → mature Classic DOM → attached Chrome 9222 → listing thumbnail`.
No Rich Direct Full Fetch dependency is part of bulk intake.

## Product AI Contract — 49.3I.17
- AI Center is the authority for selecting/saving one active Provider and Model,
- Product AI reads only that saved Provider and its saved Model,
- key comes only from that Provider's secure secret slot,
- no fallback to another Provider because another key happens to exist,
- Product open does not start AI automatically,
- normal Product AI does not fetch `/models` before generation,
- Google Product AI with exact saved Model skips model-list preflight,
- explicit Settings Model Search/Test remains live,
- stale destroyed-widget Tk callbacks are non-fatal and logged,
- existing sanitized trace, schema repair, 90s title / 210s All-Fields watchdog, Stop Waiting, stale-result and manual-override protection remain.

## Latest Validation / Merge
PR `#63` merged.
- final runtime head `2917a3db5225abac71fc3e80b64ad439acd7a4d0`,
- merge commit `7f835f573b92e3aded6275c9421770c0c47d947a`.

All required runtime-head workflows SUCCESS: 49.3I.17 `32649623837`, 49.3I `32649623808`, 49.3I.16 `32649623695`, 49.3I.15 `32649623705`, 49.3I.14 `32649623679`, 49.3H `32649623825`, 49.3G `32649623755`, Full Epic + Windows Catalog + Full Django `32649623804`.

Django migration: NONE. Catalog schema migration: NONE. Production untouched.

Relevant latest records: `ERR-49-035`, `REQ-49I-024`.

## Exact Next Gate
Windows: live ff-only pull current Epic → `RUN_PHASE49_3I17_SINGLE_AI_GATE.ps1 -LaunchApp` → save one active Provider/Model → open Product without hidden AI → run All-Fields once and verify only saved Provider/Model/no `/models` preflight → test Stop/failure responsiveness → optionally save one other Provider/Model and confirm exact switch.

Then complete any remaining short acquisition acceptance → exactly one Local Publish E2E → owner approval → Host/MySQL/backup/rollback verification → GitHub-only Production deploy.

## Next Product Phase
After Catalog Production verification: normal Store ZarinPal request/callback/verify + Sandbox E2E, preserving bank transfer.
