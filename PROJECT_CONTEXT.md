# PROJECT_CONTEXT — 3DPrintHub

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.9 — AI Refresh + SEO/Source Completion`
Status: `FINAL CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Operating Rule
GitHub/Repository is the permanent source of truth.
Required flow:
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI → WINDOWS PULL --FF-ONLY → LOCAL GATE → MANUAL QA → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION BACKUP/DEPLOY/VERIFY`

No direct Production source edits. No ZIP/Patch/source delivery through Chat. Dirty Local/Host stops for inspection; no reset/stash/delete shortcut.

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

## Current Discovery Contract
- explicit Search/Listing/Category URL is authoritative,
- configured source `model_url_pattern` is Product-vs-Group boundary,
- Product URL → mature direct intake,
- Group/Category/Search/sub-branch → Preview Candidate first,
- Preview stores source identity/basic title/one thumbnail only,
- Full Fetch only after approval,
- image limit default 10 / hard max 20,
- Archive/Not Needed does not Full Fetch,
- dedupe: source + external id + normalized URL.

## AI Provider / Execution Contract
Current Provider cards:
- AvalAI,
- OpenRouter,
- Google Gemini Direct,
- OpenAI Direct.

Secrets remain in Windows Credential Store/environment, not SQLite/Git/logs.

49.3I.8 fixed the real bottom All-Fields button routing to mature Task Center and preserves:
- immediate first-paint,
- connection/send/wait/receive/save/result-error progress,
- elapsed timer,
- Stop Waiting,
- 210-second watchdog,
- stale late-result discard.

49.3I.9 extends that path:
- explicit All-Fields rerun refreshes AI-owned/generated content with the current Provider/Model,
- proven manual overrides remain protected,
- generic Persian product titles are refreshable and new generic AI titles are rejected,
- product-specific Persian ecommerce/SEO prompt is source-grounded,
- low-image products may offer mature source refetch before AI,
- source website remains publisher/source identity,
- Django Product meta/OG/source fields receive desktop SEO/source data after mature conversion/visibility layers.

## Products Explorer / Workspace / Pricing
Preserved:
- Product Workspace is canonical detailed editor,
- Explorer visual/lightweight,
- selection-loop guard,
- safe local queue actions,
- Fixed / Range / Formula-Dynamic are independent,
- Range never invokes Formula.

## Latest GitHub Validation — 49.3I.9
CI-only PR #55: `CLOSED / NOT MERGED`.
Validated runtime base: `390c1aba9aaf5282f44a1ec97955af4e987100ba`.
Marker head: `0e58324bfc87e39299b81b1fbe65f9cce21ec91e` — not merged.

Successful runs:
- Phase49.3I `32623618842` — SUCCESS,
- Phase49.3H `32623618854` — SUCCESS,
- Phase49.3G `32623618950` — SUCCESS,
- Full Phase49 + Full Django `32623618792` — SUCCESS.

Django migration: NONE.
Catalog schema migration: NONE.
Production untouched.

## Relevant Error Knowledge
Latest relevant:
- ERR-49-013 exact Search URL ignored,
- ERR-49-014 full fetch before review,
- ERR-49-018 AI first-paint,
- ERR-49-019 stale Chat SHA,
- ERR-49-020 clipped thumbnails,
- ERR-49-021 Product-vs-Group routing,
- ERR-49-022 Treeview selection loop,
- ERR-49-023 legacy secure-field hydration,
- ERR-49-024 Preview JavaScript escape regression,
- ERR-49-025 real Provider Hub key/model visibility,
- ERR-49-026 real All-Fields button bypassed mature Task Center,
- ERR-49-027 explicit All-Fields rerun could not refresh AI-owned values / generic titles persisted.

Always inspect `docs/ERRORS.md` before troubleshooting.

## Employee Release Goal — Today
Owner wants employees to begin Catalog entry today. The release gate is:
1. Windows clean worktree,
2. live fetch/prune + ff-only pull,
3. `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`,
4. verify runner `49.3I.9` and Git snapshot marker,
5. one real All-Fields AI product-specific title/SEO test,
6. one low-image warning/refetch test,
7. one MakerWorld Preview → Approve → Full Fetch test,
8. credential/model persistence,
9. Product open/selection + pricing regressions.

After this passes, employees can use Catalog Center for data entry. Publishing to Production remains separately gated.

## Local Publish / Production
Only after Windows QA:
- one `LOCAL PUBLISH ONLY`,
- Local Django E2E,
- verify title/SEO/source/images/pricing/visibility,
- explicit owner approval,
- then host read-only verification, MySQL/database/backup/rollback verification, GitHub-only deploy and Production smoke/data checks.

## Payment State
Repository payment support is split:
- Phase30 ZarinPal online gateway is implemented for accepted `Quote` payments (deposit/full/balance) with server-side amount, callback token, Authority match, server-to-server Verify, idempotent ledger/audit.
- normal Store cart checkout is still manual-payment only: active `CheckoutOperationsForm.payment_method` contains only `bank_transfer`, and active Store checkout redirects to `store:manual_payment`.
- `StorePayment` already has a semantic `gateway` method, but normal Store request/callback/verify wiring is not complete.

Current supported online provider in repository: ZarinPal only.

Therefore live Store payment must not be enabled merely by setting Phase30 environment flags. A narrow Storefront ZarinPal integration + Sandbox E2E is the next urgent implementation after the Catalog release gate.
