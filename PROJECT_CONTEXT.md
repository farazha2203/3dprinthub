# PROJECT_CONTEXT — 3DPrintHub

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.11 — Provider Schema + Trace/Busy Runtime Recovery`
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
- Group/Category/Search → lightweight Preview first,
- Preview = identity/basic title/one thumbnail,
- Full Fetch only after approval,
- image limit default 10 / hard max 20,
- Archive blocks rediscovery without Full Fetch,
- dedupe = source + external id + normalized URL.

## Provider / Secret Contract
Providers: AvalAI, OpenRouter, Google Gemini Direct, OpenAI Direct.
Secrets remain in Windows Credential Store/environment. Provider model lists, FTP password and Bridge token persistence are regression-protected.

## AI Execution Contract — 49.3I.11
Preserved:
- mature All-Fields Task Center,
- immediate first-paint,
- scrollable sanitized request/response/error tabs,
- title retry with current Provider/Model,
- title watchdog 90 seconds,
- full-AI watchdog 210 seconds,
- Stop Waiting/cancel/timeout stale-result discard,
- AI-owned refresh with manual override protection,
- generic title rejection,
- source-grounded Persian/SEO content.

49.3I.11 fixes `ERR-49-029` from real owner trace:
- HTTP-success JSON is not accepted unless it matches the exact Catalog schema,
- AvalAI/OpenRouter receive the actual JSON Schema,
- aliases such as `seo_title` cannot silently replace required `seo_title_fa`,
- one bounded repair request may correct a schema-invalid response,
- second schema failure is shown precisely and not persisted,
- explicit selected model is used directly,
- model catalog is cached within request window,
- `/models` UI trace is compacted,
- Stop Waiting/watchdog immediately releases Workspace busy state,
- operator may change Provider/Model and retry immediately,
- late old result stays stale and cannot mutate product.

## Products / Pricing / SEO
Preserved:
- Product Workspace canonical detailed editor,
- visual/lightweight Explorer + selection-loop guard,
- Fixed / Range / Formula independent; Range never invokes Formula,
- source website as publisher/source identity,
- desktop SEO/source sync to real Product meta/OG/source fields,
- low-image mature refetch offer,
- legal license/sale approvals remain explicit operator actions.

## Latest Validation — 49.3I.11
PR #57 merged after CI.
Validated feature head: `9bdcfb3c7997cc9570d2d94e1bafd4f7bfad5651`.
Merge commit: `41d37d56437765119b9bb274037e9af7a5defbbe`.

Successful workflows:
- Phase49.3I `32628666588` — SUCCESS,
- Phase49.3H `32628666600` — SUCCESS,
- Phase49.3G `32628666558` — SUCCESS,
- Full Phase49 + Full Django `32628666582` — SUCCESS.

Django migration: NONE.
Catalog schema migration: NONE.
Production untouched.

## Relevant Error Knowledge
Latest relevant: ERR-49-013, 014, 018, 019, 020, 021, 022, 023, 024, 025, 026, 027, 028, 029. Always inspect `docs/ERRORS.md` before troubleshooting.

## Employee Release Goal — Today
Windows acceptance requires runner 49.3I.11 plus exact formerly failing AvalAI schema case, one-repair behavior, compact model trace, Stop Waiting → immediate Provider/Model retry, title/All-Fields watchdogs, low-image refetch, MakerWorld Preview→Approve→Full Fetch, credential persistence, Product open/selection and pricing regressions.

After Windows QA passes employees may use Catalog Center for controlled entry. Production remains gated by one Local Publish E2E and explicit owner approval.

## Payment State
Phase30 ZarinPal is implemented for accepted Quote payments. Normal Store cart checkout is still bank-transfer/manual-payment only; Store gateway request/callback/verify integration + Sandbox E2E remains the next urgent implementation after Catalog release.
