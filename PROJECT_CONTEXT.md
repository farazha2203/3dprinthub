# PROJECT_CONTEXT — 3DPrintHub

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Base Epic: `epic/phase49-unified-product-slider-sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.24 — Runtime Observability + AvalAI URL Tools + Startup No-Network Guard`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA REQUIRED`
Production: `UNTOUCHED / NOT APPROVED`

## Operating Rule
GitHub/Repository is permanent source of truth.
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → WINDOWS PULL --FF-ONLY → LOCAL GATE → MANUAL QA → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION BACKUP/DEPLOY/VERIFY`.

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

## Product AI Contract — Current
- AI Center owns exactly one saved Provider + Model for Product AI,
- key comes only from that Provider's secure secret slot,
- Product open does not start hidden AI,
- Product generation does not run hidden `/models`,
- application startup does not run Provider model-catalog network calls before first Tk idle,
- explicit Model Search/Test remains live after first paint,
- Product editorial generation rejects obvious non-text models,
- AvalAI structured output prefers strict JSON schema,
- exact source page is fetched/sanitized by the application; supported AvalAI URL tools may add explicit evidence when source extraction is sparse,
- a bare URL in chat is never treated as proof that the model browsed the page,
- Tk worker completions use the main-thread bridge,
- bounded job/cancel/stale-result/manual-override protections remain.

## Runtime / Diagnostics Contract — 49.3I.24
- runtime JSONL starts before wrapped App construction,
- Program/AI logs are available from Dashboard,
- Tk heartbeat records recovered lag,
- extended heartbeat stall writes an all-thread hang dump,
- safe diagnostic export includes redacted runtime/main/hang-log tails,
- no API key/password/token/full Authorization header is exported.

## Current Evidence / Open Gate
Latest owner diagnostic identified ERR-49-040/041/042: invalid AvalAI audit call, hidden startup Provider scans and non-text Product model selection. These are implemented/fixed on the feature branch but have not yet passed the Windows Local gate.

Django migration: NONE. Catalog schema migration: NONE. Production untouched.

## Exact Next Gate
Windows: close app → clean worktree → live fetch/prune + ff-only pull feature branch → Local HEAD == Remote HEAD → compile + focused 49.3I.24/23/22/21/20/19/18 tests → `launch.py --verify-only` → launch → verify Dashboard diagnostics/no startup `/models` → explicit model search → MakerWorld 2896217 link completion → explicit AvalAI URL tool or app-fetch fallback + structured output → hang export if needed → normal close/reopen.

Then exactly one Local Publish E2E → owner approval → read-only Host/MySQL/backup/rollback verification → GitHub-only Production deploy.

## Next Product Phase
After Catalog Production verification: normal Store ZarinPal request/callback/verify + Sandbox E2E, preserving bank transfer.
