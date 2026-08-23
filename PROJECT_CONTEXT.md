# PROJECT_CONTEXT — 3DPrintHub

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.13 — Windows URL Paste + Approved Batch Full-Fetch Recovery`
Status: `PR MERGED / FINAL CI SUCCESS / WINDOWS RERUN PENDING`
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

## Discovery Contract — 49.3I.13
- explicit Search/Listing/Category URL authoritative,
- source `model_url_pattern` is Product-vs-Page boundary,
- exact-page action scans the pasted page and exposes live running/stopping/done state,
- direct Product URL has a separate manual action,
- URL field supports explicit Windows Ctrl+V/Shift+Insert/right-click Paste plus visible Paste Link,
- Preview = identity/basic title/one thumbnail,
- Full Fetch only after approval,
- approved multi-candidate Full Fetch reuses mature RichPageExtractor in background/headless mode,
- direct single-product intake keeps configured headed behavior,
- original direct-link browser mode is restored after approved batch completion/cancel/error,
- candidate stored `last_error` is directly inspectable,
- image limit default 10 / hard max 20,
- Archive blocks rediscovery without Full Fetch,
- dedupe = source + external id + normalized URL.

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

## Latest Validation — 49.3I.13
PR #59 merged after CI.
Validated feature head: `b47793c42d807285efbd8d3e005f9979856c4878`.
Merge commit: `3ad097fb3c5ccd2aed82b2dab38f3c8951e00e51`.

Successful workflows:
- Phase49.3I `32633932308` — SUCCESS,
- Phase49.3H `32633932302` — SUCCESS,
- Phase49.3G `32633932340` — SUCCESS,
- Full Phase49 + Full Django `32633932224` — SUCCESS.

Django migration: NONE.
Catalog schema migration: NONE.
Production untouched.

## Relevant Error Knowledge
Latest relevant: ERR-49-013 through ERR-49-031. Current Windows blocker/fix is ERR-49-031. Always inspect `docs/ERRORS.md` before troubleshooting.

## Employee Release Goal — Today
Windows acceptance requires runner 49.3I.13, reliable paste, exact MakerWorld Preview, 2+ approved candidates Full Fetch without visible per-candidate browsers, inspectable failure reason if any, direct Product URL intake, image fit and AI/provider/image-limit/pricing regressions.

After Windows QA passes employees may use Catalog Center for controlled entry. Production remains gated by exactly one Local Publish E2E and explicit owner approval.

## Next Product Phase
Phase30 ZarinPal exists for accepted Quote payments. Normal Store cart checkout is still bank-transfer/manual-payment only; Store gateway request/callback/verify integration + Sandbox E2E is next after Catalog acceptance.
