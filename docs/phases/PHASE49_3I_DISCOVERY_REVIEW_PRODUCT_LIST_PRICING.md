# Phase49.3I — Discovery Review + Product Explorer + Pricing + Observable AI

Updated: 2026-08-23
Branch: `epic/phase49-unified-product-slider-sync`
Current Hotfix: `49.3I.10`
Status: `FINAL CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Goal
Provide a business-usable Catalog Center flow that discovers source products cheaply, previews before full acquisition, prepares Persian ecommerce/SEO content, supports explicit pricing, exposes every AI execution result/error to the operator, protects manual edits and publishes only through verified Local/Production gates.

## Canonical State Machine
`Exact Search/Listing/Category URL → Preview Candidate → Approve/Archive → Approved Full Fetch → Product Workspace → LOCAL PUBLISH ONLY → Local Django E2E → Owner Approval → Production`

## Discovery / Full Fetch Contract
Preview contains only source identity/external id, source URL, basic title and one thumbnail. Preview must not full-fetch every product, download all images or invoke Production.

Configured source `model_url_pattern` remains authoritative:
- real Product URL → mature direct intake,
- Group/Category/Search/Listing/sub-branch → Preview first.

Approved Full Fetch uses the mature extractor only after operator approval. Image limit remains `1..20`, default `10`. Archive keeps minimal blocked identity and prevents rediscovery until restore.

## Provider / Credential Contract
Provider cards:
- AvalAI,
- OpenRouter,
- Google Gemini Direct,
- OpenAI Direct.

Windows Credential Store/environment remains credential source of truth. API keys, FTP password and Bridge token remain outside Git/SQLite/log payloads. Provider model catalogs continue loading through the mature provider adapters.

## Observable AI Contract
49.3I.8 established the real All-Fields Task Center path:
- immediate first-paint,
- connection/send/wait/receive/save/result-error visibility,
- elapsed timer + Stop Waiting,
- 210-second All-Fields watchdog,
- cancel/timeout stale-result discard.

49.3I.9 added explicit AI-owned refresh/manual-override/source/SEO completion.

### 49.3I.10 — AI Trace + Safe Title Retry
Owner runtime evidence exposed `ERR-49-028`: an AI provider could return HTTP 200 and the UI could still fail because a delayed Tk callback referenced a Python exception variable after `except ... as exc` had cleared it. Title-only retry also lacked the mature observable trace/timeout contract.

49.3I.10 adds:
- final AI progress window with scrollable `ارسالی`, `دریافتی`, `خطا / Diagnostics` tabs,
- vertical + horizontal scrollbars for large payload/result/error data,
- sanitized OpenAI-compatible and Google Gemini HTTP payload/result trace in UI and existing Phase49 JSONL,
- no API key/token/Authorization header in the trace details,
- title retry that always uses the Provider/Model active when clicked,
- title retry allowed even when a previous/wrong `title_fa` exists,
- 90-second title-only watchdog,
- Stop Waiting/timeout/workspace close makes title result stale/non-applicable,
- generic/non-Persian/too-short title rejection before persistence,
- targeted Tk `after()` exception-closure freezing for live exception objects,
- no second AI client/crawler/importer,
- preserved 210-second All-Fields watchdog and 49.3I.9 refresh/manual override/source/SEO behavior.

## Products Explorer / Pricing
Preserved:
- Product Workspace is canonical detailed editor,
- Explorer is visual/lightweight,
- selection-loop guard,
- safe local queue actions,
- Fixed / Range / Formula-Dynamic independent,
- Range never invokes Formula.

## Runtime / Test Surface — 49.3I.10
Added:
- `catalog_center/app/phase49_3i_ai_trace_recovery.py`,
- `catalog_center/tests/test_epic49_phase49_3i_ai_trace_recovery.py`.

Changed:
- `catalog_center/app/phase49_3i_local_qa_hotfix.py`,
- `RUN_PHASE49_3I_LOCAL_GATE.ps1` → v`49.3I.10`,
- `.github/workflows/phase49-3i-ci.yml`.

No Django migration and no Catalog schema migration.

## Final GitHub Validation — 49.3I.10
Implementation PR `#56`: MERGED.
Validated feature head: `8d1f6e02d6f722b8f047f5d7f7763a5a42516191`.
Epic merge commit: `256c130f179aaa4253898b0d5ec1ce2696ac4bb5`.

Successful runs:
- Phase49.3I `32626758096` — SUCCESS,
- Phase49.3H `32626758114` — SUCCESS,
- Phase49.3G `32626758134` — SUCCESS,
- Full Phase49 + Full Django `32626758119` — SUCCESS.

Validation includes runner/ASCII/live-Git guard, compile, title retry/watchdog/generic-title tests, Tk exception callback safety, sanitized scrollable trace contract, stale-result guards, 49.3I.9 refresh/source/SEO, prior Preview/provider/Explorer/pricing regressions, Django no-migration contract, Windows Catalog tests and Full Django suite.

## Database / Migration / Secret Safety
- Django migration: `NONE`,
- Catalog schema migration: `NONE`,
- no reset/drop/truncate,
- no historical data/media rewrite,
- no credential storage change,
- Production untouched.

## Employee Release Acceptance Gate — NEXT
1. Catalog Center closed; Local worktree clean,
2. live fetch/prune + ff-only pull current Epic,
3. run `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`,
4. verify runner `49.3I.10` + Git snapshot marker,
5. open a product with a known wrong Persian title,
6. press Translate Title and verify request/response/error tabs + scrollbars,
7. verify current Provider/Model and source title are visible,
8. verify sanitized outgoing request and incoming response/result are visible,
9. retry after changing Provider/Model,
10. test invalid key/network error: error stays visible and app stays open,
11. test Stop Waiting and 90-second title timeout; late response must not mutate title,
12. bottom All-Fields AI shows the same trace UI and preserves its 210-second stale-result guard,
13. low-image warning/refetch,
14. MakerWorld Preview → Approve → Full Fetch,
15. Provider/model/FTP/Bridge persistence,
16. Product selection/open + Fixed/Range/Formula.

If these pass, employees may begin controlled Catalog data entry.

## Local Publish / Production Gate
After Windows acceptance: exactly one `LOCAL PUBLISH ONLY` → Local Django E2E → verify title/SEO/source/images/pricing/visibility → explicit owner acceptance. Only then verify host branch/path/MySQL/backup/rollback and deploy the approved GitHub snapshot.

## Payment Note
Phase30 ZarinPal covers accepted Quote payments. Normal Store cart checkout is still manual bank transfer; Store request/callback/verify wiring is not complete. Storefront ZarinPal integration + Sandbox E2E is the next urgent implementation after Catalog release QA.
