# PROJECT_CONTEXT — 3DPrintHub

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.12 — Observable Exact-Page Discovery + Single-Product Intake + Workspace Image Fit`
Status: `PR MERGED / FINAL CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Operating Rule
GitHub/Repository is the permanent source of truth.
Required flow:
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI → WINDOWS PULL --FF-ONLY → LOCAL GATE → MANUAL QA → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION BACKUP/DEPLOY/VERIFY`.

No direct Production source edits. No project ZIP/Patch/source delivery through Chat. Dirty Local/Host stops for inspection; no reset/stash/delete shortcut.

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

## Discovery Contract — 49.3I.12
- explicit Search/Listing/Category URL authoritative,
- source `model_url_pattern` is Product-vs-Page boundary,
- exact-page action scans the pasted page and exposes live running/stopping/done state,
- direct Product URL has a separate manual action,
- visible badge/progress/elapsed/current URL/detail,
- Preview = identity/basic title/one thumbnail,
- Full Fetch only after approval,
- image limit default 10 / hard max 20,
- Archive blocks rediscovery without Full Fetch,
- dedupe = source + external id + normalized URL,
- mature candidate thumbnail/status/title/source/external/url renderer reused.

## Product Workspace Image Contract — 49.3I.12
- canonical detailed editor preserved,
- gallery thumbnails use fixed `228x171` pixel viewports,
- `ImageOps.contain` with letterbox background,
- no crop/stretch,
- no Tk text-unit sizing for pixel image labels.

## Provider / Secret Contract
Providers: AvalAI, OpenRouter, Google Gemini Direct, OpenAI Direct.
Secrets remain in Windows Credential Store/environment. Provider model lists, FTP password and Bridge token persistence are regression-protected.

## AI Execution Contract — Preserved Through 49.3I.12
- mature All-Fields Task Center,
- immediate first-paint,
- scrollable sanitized request/response/error tabs,
- title retry with current Provider/Model,
- title watchdog 90 seconds,
- full-AI watchdog 210 seconds,
- Stop Waiting/cancel/timeout stale-result discard,
- AI-owned refresh with manual override protection,
- generic title rejection,
- source-grounded Persian/SEO content,
- exact JSON Schema delivery/validation for compatible providers,
- one bounded schema repair,
- compact model catalog trace,
- abort releases busy state immediately.

## Pricing / SEO
Preserved:
- Fixed / Range / Formula independent; Range never invokes Formula,
- source website as publisher/source identity,
- desktop SEO/source sync to real Product meta/OG/source fields,
- low-image mature refetch offer,
- legal license/sale approvals remain explicit operator actions.

## Latest Validation — 49.3I.12
PR #58 merged after CI.
Validated feature head: `2a9442055d33777f675ccd3ebe11de8419bfb2b3`.
Merge commit: `24d5b8fdddb97fbcc4c07efa7d6f1d78a0ffb225`.

Successful workflows:
- Phase49.3I `32631604990` — SUCCESS,
- Phase49.3H `32631604930` — SUCCESS,
- Phase49.3G `32631604945` — SUCCESS,
- Full Phase49 + Full Django `32631604928` — SUCCESS.

Django migration: NONE.
Catalog schema migration: NONE.
Production untouched.

## Relevant Error Knowledge
Latest relevant: ERR-49-013 through ERR-49-030, especially ERR-49-017/020/030 for current UX/discovery/image behavior and 026–029 for current AI behavior. Always inspect `docs/ERRORS.md` before troubleshooting.

## Employee Release Goal — Today
Windows acceptance requires runner 49.3I.12 plus exact MakerWorld page discovery with visible live status/candidates, approved Full Fetch, direct Product URL intake, Stop feedback, Product Workspace image fit, and AI/provider/image-limit/pricing regressions.

After Windows QA passes employees may use Catalog Center for controlled entry. Production remains gated by one Local Publish E2E and explicit owner approval.

## Next Product Phase
Phase30 ZarinPal exists for accepted Quote payments. Normal Store cart checkout is still bank-transfer/manual-payment only; Store gateway request/callback/verify integration + Sandbox E2E is the next implementation track immediately after Catalog acceptance.
