# PROJECT_CONTEXT — 3DPrintHub

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.10 — AI Trace + Safe Title Retry Recovery`
Status: `FINAL CI SUCCESS / WINDOWS QA PENDING`
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

## Discovery Contract
- explicit Search/Listing/Category URL authoritative,
- source `model_url_pattern` is Product-vs-Group boundary,
- Product URL → mature direct intake,
- Group/Category/Search/sub-branch → lightweight Preview first,
- Preview = identity/basic title/one thumbnail,
- Full Fetch only after approval,
- image limit default 10 / hard max 20,
- Archive blocks rediscovery without Full Fetch,
- dedupe = source + external id + normalized URL.

## AI Provider / Credential Contract
Providers: AvalAI, OpenRouter, Google Gemini Direct, OpenAI Direct.
Secrets remain in Windows Credential Store/environment. Provider model lists, FTP password and Bridge token persistence are protected by regression tests.

## AI Execution Contract — 49.3I.10
49.3I.8 established mature All-Fields execution with first-paint, progress, Stop Waiting, 210-second watchdog and stale-result discard. 49.3I.9 added AI-owned rerun/manual override/source/SEO completion.

49.3I.10 fixes `ERR-49-028`:
- title/provider errors can no longer disappear behind delayed Tk callbacks that reference a cleared `except ... as exc` target,
- final AI progress has scrollable outgoing request / incoming response / error-diagnostics tabs,
- both vertical and horizontal scrollbars are present,
- OpenAI-compatible and Google Gemini HTTP payload/results are shown and written to existing JSONL in sanitized form,
- API key/token/Authorization header is not included in trace details,
- title translation reruns with the Provider/Model active at click time even if `title_fa` is already populated,
- title-only watchdog is 90 seconds,
- Stop Waiting/timeout/workspace close makes late title response stale and non-applicable,
- generic/non-Persian/too-short titles are rejected before DB write,
- All-Fields retains its 210-second stale-result watchdog,
- no second AI client/crawler/importer exists.

## Products / Pricing / SEO
Preserved:
- Product Workspace canonical detailed editor,
- visual/lightweight Explorer + selection-loop guard,
- Fixed / Range / Formula independent; Range never invokes Formula,
- AI-owned content refresh with manual override protection,
- source website as publisher/source identity,
- desktop SEO/source sync to real Product meta/OG/source fields,
- low-image mature refetch offer,
- local default price only when missing,
- legal license/sale approvals remain explicit operator actions.

## Latest Validation — 49.3I.10
PR #56 merged after CI.
Validated feature head: `8d1f6e02d6f722b8f047f5d7f7763a5a42516191`.
Merge commit: `256c130f179aaa4253898b0d5ec1ce2696ac4bb5`.

Successful workflows:
- Phase49.3I `32626758096`,
- Phase49.3H `32626758114`,
- Phase49.3G `32626758134`,
- Full Phase49 + Full Django `32626758119`.
All SUCCESS.

Django migration: NONE.
Catalog schema migration: NONE.
Production untouched.

## Relevant Error Knowledge
Latest relevant: ERR-49-013 exact URL; 014 Preview-before-Full-Fetch; 018 first-paint; 019 live Git snapshot; 020 thumbnails; 021 URL routing; 022 selection loop; 023/025 credentials; 024 Preview JS escape; 026 real All-Fields Task Center; 027 AI refresh/generic titles; 028 AI callback/trace/title retry.
Always inspect `docs/ERRORS.md` before troubleshooting.

## Employee Release Goal — Today
Windows acceptance requires runner 49.3I.10 plus title request/response diagnostics, Provider/Model retry, invalid-key/network error handling, Stop Waiting/90s stale-result behavior, All-Fields trace/210s behavior, low-image refetch, MakerWorld Preview→Approve→Full Fetch, credential/model persistence, Product open/selection and pricing regressions.

After Windows QA passes employees may use Catalog Center for controlled data entry. Production publishing remains gated by one Local Publish E2E and explicit owner approval.

## Payment State
Phase30 ZarinPal is implemented for accepted Quote payments with server-side amount, callback token, Authority match, server-to-server Verify and idempotent ledger/audit. Normal Store cart checkout still exposes only bank transfer/manual payment; Store gateway request/callback/verify wiring is incomplete.

Therefore the next urgent implementation after Catalog release is a narrow Storefront ZarinPal integration + Sandbox E2E. Existing Quote payment environment flags alone must not be used to claim Store checkout is live-payment ready.
