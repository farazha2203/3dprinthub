# PROJECT_CONTEXT — 3DPrintHub

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.14 — Mature Scan Controls + Single-Product Route Restoration`
Status: `IMPLEMENTED / PR #60 OPEN / ALL REQUIRED CI SUCCESS / WINDOWS QA PENDING`
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
- `شروع اسکن` must route to original BaseApp `start_scan/_scan_worker`,
- `توقف محترمانه`, `دریافت هوشمند از لینک`, `کشف جدیدها` remain available,
- manual `دریافت محصول تکی` validates Product URL and then uses mature `mode=single` scan,
- Rich Direct Intake remains optional, not mandatory.

Review path:
- explicit Search/Listing/Category URL authoritative,
- exact-page Preview remains one identity/title/thumbnail,
- Full Fetch only after approval,
- Archive/dedupe/paste/error-detail remain,
- image limit default 10 / hard max 20.

No new discovery control may hide or silently rebind healthy mature acquisition behavior.

## Product Workspace Image Contract
- canonical detailed editor preserved,
- gallery thumbnails use fixed `228x171` pixel viewports,
- `ImageOps.contain` with letterbox background,
- no crop/stretch or Tk text-unit sizing.

## Provider / Secret Contract
Providers: AvalAI, OpenRouter, Google Gemini Direct, OpenAI Direct.
Secrets remain in Windows Credential Store/environment. Provider model lists, FTP password and Bridge token persistence are regression-protected.

## AI Execution Contract
- mature All-Fields Task Center,
- immediate first-paint,
- scrollable sanitized request/response/error tabs,
- title watchdog 90 seconds / full-AI watchdog 210 seconds,
- Stop Waiting/cancel/timeout stale-result discard,
- AI-owned refresh with manual override protection,
- generic title rejection,
- source-grounded Persian/SEO content,
- exact JSON Schema delivery/validation + one repair,
- compact model catalog trace,
- abort releases busy state immediately.

## Pricing / SEO
- Fixed / Range / Formula independent; Range never invokes Formula,
- source website remains publisher/source identity,
- final Product meta/OG/source fields synced,
- low-image mature refetch offer,
- legal license/sale approvals remain explicit operator actions.

## Latest Validation — 49.3I.14 Feature Runtime
PR #60 open at documentation time.
Runtime fix commit: `bb6f456b50c1e12bbf6fc5c6b6cc3289f35ee6c8`.

Successful workflows:
- Phase49.3I.14 Legacy Scan Restore `32636391530` — SUCCESS,
- Phase49.3I `32636391489` — SUCCESS,
- Phase49.3H `32636391571` — SUCCESS,
- Phase49.3G `32636391563` — SUCCESS,
- Full Phase49 + Full Django `32636391518` — SUCCESS.

Initial targeted CI had failed because the resolver selected an intermediate Preview override. It was corrected before a fresh successful run. Canonical incident: `ERR-49-032`.

Django migration: NONE.
Catalog schema migration: NONE.
Production untouched.

## Relevant Error Knowledge
Latest relevant error: `ERR-49-032`. Always inspect `docs/ERRORS.md` before troubleshooting. Its permanent rule is: add new controls beside mature ones; do not hide/replace healthy acquisition without explicit approval, and test both visibility and command routing.

## Employee Release Goal
After PR merge, run focused Windows QA only:
- hotfix gate passes,
- mature top acquisition controls visible,
- known MakerWorld Product URL works via `single + auto + شروع اسکن`,
- new manual single-product action uses the same mature path instead of forcing Rich Direct HTTP 403,
- Preview/Approve remains present.

After PASS: exactly one Local Publish E2E, Store/Admin verification, owner approval, then Production gate/deploy from GitHub.

## Next Product Phase
Phase30 ZarinPal exists for accepted Quote payments. Normal Store cart checkout is still bank-transfer/manual-payment only; Store gateway request/callback/verify integration + Sandbox E2E is next after Catalog acceptance.
