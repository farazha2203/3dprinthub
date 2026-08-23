# PROJECT_CONTEXT — 3DPrintHub

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.14 — Mature Scan Controls + Single-Product Route Restoration`
Status: `PR #60 MERGED / ALL REQUIRED CI SUCCESS / FOCUSED WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Operating Rule
GitHub/Repository is the permanent source of truth.
Required flow:
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI → WINDOWS PULL --FF-ONLY → LOCAL GATE → MANUAL QA → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION BACKUP/DEPLOY/VERIFY`.

No direct Production source edits. No project ZIP/Patch/source delivery through Chat. Dirty Local/Host stops for inspection; no reset/stash/delete shortcut. New UI features are additive unless the owner explicitly approves replacing mature behavior.

## Canonical Paths
Windows project: `D:\projects\3DPrintHub`
Windows Catalog Center: `D:\projects\3DPrintHub\catalog_center`
Windows venv: `D:\projects\3DPrintHub\.venv`
Windows Django DB: `D:\projects\3DPrintHub\db.sqlite3`
Windows Catalog persistent root: `D:\projects\3dprinthub-catalog-manager`
Windows Catalog DB: `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`
Windows backups: `D:\projects\3dprinthub-backups`
Production project: `/home/sfkilvrs/3dprinthub`
Production venv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`
Production DB: MySQL `sfkilvrs_EmiAdmin_3dprinthub`

Always re-read `docs/PATHS.md` and `docs/HOST_CONSTRAINTS.md` before environment/deployment work.

## Acquisition Contract — 49.3I.14
Two acquisition paths intentionally coexist.

Mature path:
- source/mode/method/URL/query controls remain available,
- `شروع اسکن` routes to original BaseApp `start_scan/_scan_worker`,
- `توقف محترمانه`, `دریافت هوشمند از لینک`, `کشف جدیدها` remain available,
- manual `دریافت محصول تکی` validates Product URL and then uses mature `mode=single` scan,
- Rich Direct Intake remains optional.

Review path:
- explicit Search/Listing/Category URL authoritative,
- exact-page Preview remains one identity/title/thumbnail,
- Full Fetch only after approval,
- Archive/dedupe/paste/error-detail remain,
- image limit default 10 / hard max 20.

No new discovery control may hide or silently rebind healthy mature acquisition behavior.

## Product Workspace / AI / Pricing
- Product Workspace remains canonical editor,
- gallery images use fixed `228x171` contain/letterbox contract,
- mature All-Fields Task Center + immediate first-paint + sanitized trace + watchdog/stale-result safety preserved,
- provider exact schema + one repair preserved,
- Fixed / Range / Formula independent; Range never invokes Formula.

## Latest Validation
PR #60 MERGED.
Final PR head: `f12a25e1fe50fb16a03a1324c84912c830a2608e`.
Merge commit: `124662cf2436dfcce245282b01b2da694802aa55`.

Successful final PR-head workflows:
- Phase49.3I.14 `32636771174` — SUCCESS,
- Phase49.3I `32636771071` — SUCCESS,
- Phase49.3H `32636771154` — SUCCESS,
- Phase49.3G `32636771049` — SUCCESS,
- Full Phase49 + Full Django `32636771103` — SUCCESS.

Django migration: NONE.
Catalog schema migration: NONE.
Production untouched.

## Relevant Error Knowledge
Latest relevant error: `ERR-49-032`. Permanent rule: new controls are additive; healthy mature acquisition cannot be hidden/replaced/rebound without explicit owner approval. Test both visibility and command routing.

## Employee Release Goal
Run focused Windows QA only with `RUN_PHASE49_3I14_HOTFIX_GATE.ps1 -LaunchApp`. Confirm mature controls, mature single-product route and preserved Preview/Approve. After PASS run exactly one Local Publish E2E, obtain owner approval, then Production gate/deploy from GitHub.

## Next Product Phase
After Catalog acceptance/deploy, implement normal Store ZarinPal request/callback/verify + Sandbox E2E.
