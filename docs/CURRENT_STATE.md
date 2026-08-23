# CURRENT PROJECT STATE

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Branch: `epic/phase49-unified-product-slider-sync`
Active Phase: `49.3I`
Active Hotfix: `49.3I.10 — AI Trace + Safe Title Retry Recovery`
Status: `GITHUB UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Current Position
49.3I.10 is merged into the active Epic after CI validation. The immediate business goal remains to release Catalog Center to employees today for controlled catalog/product entry, then complete one Local Publish E2E, obtain explicit owner approval, deploy the verified GitHub snapshot, and continue with Storefront ZarinPal integration.

Canonical release order remains:
`GitHub → Windows ff-only pull → Local automated gate → Manual visual/data/interaction QA → one LOCAL PUBLISH ONLY → Local Django E2E → explicit owner approval → Production backup/deploy/verify`.

## New Runtime Incident — ERR-49-028
Owner runtime evidence showed an AI request could return HTTP 200 successfully and still appear broken because the delayed Tk error callback itself failed with `NameError: cannot access free variable 'exc'`.

Verified root cause:
- several Tk `after(...)` callbacks captured the `except ... as exc` variable in a lambda,
- Python clears the exception target when the `except` block exits,
- the delayed UI callback could therefore crash after the provider/network operation had already completed,
- the title-only quick action also had no mature request/response trace, no bounded operator wait and no stale-result protection.

## Phase49.3I.10 Implemented Delta
New additive module:
`catalog_center/app/phase49_3i_ai_trace_recovery.py`

Behavior:
- the AI progress dialog now exposes scrollable `ارسالی`, `دریافتی`, and `خطا / Diagnostics` tabs,
- vertical and horizontal scrollbars are present for high-volume request/response data,
- OpenAI-compatible provider and Google Gemini HTTP payload/response details are shown in sanitized form,
- API keys/tokens/Authorization headers are never included in the visible trace payload,
- the same sanitized trace is written to the existing Phase49 runtime JSONL diagnostics,
- title-only translation can always be retried using the currently active Provider/Model even when `title_fa` is already populated,
- title-only translation has a 90-second operator watchdog,
- Stop Waiting/cancel and timeout make the title execution stale so a late response cannot overwrite the product,
- closing/staling the Workspace prevents a late title result from applying,
- generic/non-Persian/too-short Persian titles are rejected before persistence,
- a targeted Tk `after()` exception-closure guard freezes live exception objects before Python clears them,
- the mature 210-second All-Fields watchdog and stale-result safety remain preserved,
- no second AI client/crawler/importer was created.

## GitHub Validation — 49.3I.10
Implementation PR: `#56` — MERGED after all required workflows succeeded.
Validated feature head: `8d1f6e02d6f722b8f047f5d7f7763a5a42516191`.
Epic merge commit: `256c130f179aaa4253898b0d5ec1ce2696ac4bb5`.

Successful workflows:
- Phase49.3I Discovery Review Pricing CI — Run `32626758096` — SUCCESS.
- Phase49.3H SEO Cost Image Limit CI — Run `32626758114` — SUCCESS.
- Phase49.3G Workspace Usability CI — Run `32626758134` — SUCCESS.
- Phase49 Epic Unified CI / Full Django — Run `32626758119` — SUCCESS.

Validated:
- runner `49.3I.10` and ASCII-only Windows PowerShell 5.1 contract,
- live fetched GitHub snapshot guard,
- Python compile,
- dedicated title watchdog/retry/generic-title tests,
- Tk exception-callback closure regression,
- sanitized request/response trace contract,
- scrollable diagnostics UI contract,
- stale/cancelled title result discard,
- existing 49.3I.9 refresh/manual override/source/SEO behavior,
- prior Preview/provider/Explorer/pricing regressions,
- Django check and no-migration contract,
- Windows Catalog Epic49 tests,
- Full Django suite.

## Database / Migration / Media / Secret Safety
- Django migration for 49.3I.10: `NONE` — CI verified.
- Catalog schema migration: `NONE`.
- no DB reset/drop/truncate.
- no historical data/media rewrite/delete.
- no credential storage change.
- Production DB/media/source untouched.

## Windows QA Required Now — Employee Release Gate
1. close Catalog Center completely,
2. verify Local worktree is clean,
3. fetch/prune and ff-only pull the live Epic branch,
4. run `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`,
5. verify Runner `49.3I.10` and `PHASE49_3I_GIT_SNAPSHOT=OK`,
6. open a product with a deliberately wrong Persian title and press Translate Title,
7. verify request/response/error tabs appear immediately and are scrollable,
8. verify active Provider/Model, source title, sanitized outgoing request and incoming response/result are visible,
9. test invalid key/network/provider error: error remains visible and Workspace stays open,
10. test Stop Waiting and verify any late result cannot change the product,
11. verify title watchdog stops waiting at 90 seconds,
12. run bottom All-Fields AI and verify the same trace visibility plus the preserved 210-second stale-result guard,
13. test low-image warning/refetch once,
14. test MakerWorld Preview → Approve → Full Fetch once,
15. verify Provider keys/model lists + FTP/Bridge credentials remain available,
16. verify Product open/selection and Fixed/Range/Formula remain healthy.

If those pass, employees may use Catalog Center for controlled data entry. Production publishing remains separately gated.

## Local Publish / Production Gate
After Windows QA passes:
- exactly one `LOCAL PUBLISH ONLY`,
- Local Django E2E,
- verify title/SEO/images/pricing/source attribution in Local Store/Admin,
- explicit owner approval,
- then host read-only verification, MySQL/database/backup/rollback verification, GitHub-only deploy and Production smoke/data checks.

## Payment Track — Verified Gap
Mature Phase30 ZarinPal exists for accepted Quote payments, but normal Store cart checkout still exposes only `bank_transfer` and redirects to the manual-payment flow. `StorePayment` has a `gateway` semantic value, but Store request/callback/verify wiring is incomplete.

Therefore live Store payments must not be enabled by environment switches alone. The next urgent implementation after Catalog release is a narrow Storefront ZarinPal integration that reuses the mature server-side amount, Authority match, callback/Verify and idempotency security contracts, followed by Sandbox E2E before any live money.

## Exact Next Task
Windows must pull the current Epic with ff-only live snapshot semantics and run the repository-owned 49.3I.10 gate. No direct Local source patch, no Production deploy and no live payment activation before the acceptance gates pass.
