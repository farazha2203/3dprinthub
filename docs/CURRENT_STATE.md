# CURRENT PROJECT STATE

Updated: 2026-08-22
Repository: `farazha2203/3dprinthub`
Branch: `epic/phase49-unified-product-slider-sync`
Active Phase: `49.3I`
Active Hotfix: `49.3I.7 — Preview + Provider Hub Recovery`
Status: `GITHUB UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Current Position
Windows 49.3I.5/49.3I.6 QA established two facts:
- Product URL vs Group/Category/Search/sub-branch routing is corrected.
- the latest operator run still exposed two regressions: Preview candidate extraction failed with Playwright JavaScript syntax error, and real AI Provider Hub key fields/model lists were not staying visible.

Phase49.3I.7 fixes only those broken boundaries and preserves the mature direct/full source extraction path.

## Owner Evidence From Windows
MakerWorld exact URL:
`https://makerworld.com/en/search/models?keyword=cake+stand`

Observed log:
- `PHASE49_3I_URL_ROUTE=preview_listing`
- `PHASE49_3I_PREVIEW_TARGET=...cake+stand`
- `Locator.evaluate_all: SyntaxError: Invalid or unexpected token`
- `candidates=0 failed=1 full_fetch=0`

This proves URL routing was correct and the failure was inside the new Stage-1 Preview DOM evaluator.

## ERR-49-024 — Preview JavaScript Escape Regression
Verified Root Cause:
- Stage-1 Preview passed a normal Python triple-quoted JavaScript expression to `Locator.evaluate_all()`.
- the JavaScript contained `+'\n'+` at Python source level.
- Python converted it into a literal newline before Playwright evaluated the expression.
- the browser therefore received an invalid newline inside a JavaScript single-quoted string and raised `SyntaxError: Invalid or unexpected token`.

Correct Solution:
- new `catalog_center/app/phase49_3i_preview_recovery.py`,
- raw Python JavaScript string preserves the browser-side `\n` escape,
- reuses existing lightweight `candidates_from_dom_rows()`,
- only Stage-1 Preview is replaced,
- mature `classic_methods.discover_classic` / `collect_classic_exact` and approved Full Fetch are untouched.

Required workflow remains:
`Search/Listing → Preview candidate + one thumbnail → operator approval → mature full product fetch → selected image limit (e.g. 20)`.

## ERR-49-025 — Real Provider Hub Keys Were Not Hydrated
Verified Root Cause:
- 49.3I.6 hydrated legacy `ai_key`, FTP password and Bridge token,
- the real Phase49.3F AI Center uses `_ai_hub_key_vars` per Provider,
- mature Provider Save writes the key to Windows Credential Store then clears `_ai_hub_key_vars[provider]`,
- therefore the current visible AvalAI/OpenRouter/OpenAI/Google cards still looked empty and model picker could behave as if no key existed.

Correct Solution in 49.3I.7:
- hydrate real per-provider card variables from Windows Credential Store,
- rehydrate them after mature secure Save,
- hydrate OpenRouter management/OpenAI admin masked fields when stored,
- keep FTP password + Bridge token hydration,
- background-load model catalogs for configured Providers into the existing Model ID combobox/cache,
- keep manual model search/API refresh,
- no credential moves into SQLite/Git/source/logs.

## Provider Model Contract
Existing mature `AIProviderClient` remains authoritative:
- AvalAI → authenticated `/v1/models`,
- OpenRouter → `/api/v1/models`,
- OpenAI direct → provider models endpoint,
- Google Gemini direct → existing Gemini adapter.

49.3I.7 does not create a parallel AI client. It only makes the existing Provider Hub secure state visible and loads its existing model catalog automatically when a stored key exists.

## Runtime Files Added/Changed
Added:
- `catalog_center/app/phase49_3i_preview_recovery.py`
- `catalog_center/tests/test_epic49_phase49_3i_preview_recovery.py`

Changed:
- `catalog_center/app/phase49_3i_secret_persistence.py`
- `catalog_center/tests/test_epic49_phase49_3i_secret_persistence.py`
- `RUN_PHASE49_3I_LOCAL_GATE.ps1` → `49.3I.7`
- `.github/workflows/phase49-3i-ci.yml`

## Final GitHub Validation — 49.3I.7
CI-only PR: `#52`
State: `CLOSED / NOT MERGED`
Validated Epic runtime base: `4e0b1b7f0f8934a03ab74037bdce5f9abe55b425`
CI marker head: `5097f45f069e40af64d452ffaa8cd07399a977f2` — not merged.

Successful workflows:
- Phase49.3I Discovery Review Pricing CI — Run `32585956198` — SUCCESS.
- Phase49.3H SEO Cost Image Limit CI — Run `32585956149` — SUCCESS.
- Phase49.3G Workspace Usability CI — Run `32585956156` — SUCCESS.
- Phase49 Epic Unified CI / Full Django — Run `32585956155` — SUCCESS.

Validated:
- runner v49.3I.7 ASCII-only Windows PowerShell 5.1 contract,
- live fetched Git snapshot guard,
- Python compile,
- Preview JavaScript escape regression,
- Preview recovery never calls full product extraction,
- real Provider Hub secure hydration,
- Provider post-save rehydration,
- configured Provider model catalog scheduling/cache/combobox population,
- prior Explorer/selection/routing regressions,
- 49.3H/3G regressions,
- Django checks,
- `makemigrations --check --dry-run` = no changes,
- migration plan safe,
- Windows Catalog Epic49 tests,
- Full Django suite.

Post-validation changes after runtime base are documentation-only.

## Database / Migration / Media / Secret Safety
- Django migration for 49.3I.7: `NONE` — CI verified.
- Catalog schema migration: `NONE`.
- no DB reset/drop/truncate.
- no historical data rewrite.
- no media rewrite/delete.
- secrets remain in Windows Credential Store/environment only.
- Production DB/media/source untouched.

## Preserved Contracts
- Product Workspace remains canonical detailed editor,
- Product-vs-Group routing by source `model_url_pattern`,
- Preview → Approve → Full Fetch,
- archive/blocked duplicate guard,
- image default 10 / hard max 20,
- mature direct/full source extraction,
- AI progress/result/error/cost stack,
- Fixed / Range / Formula independence,
- Explorer selection-loop guard and view modes,
- Local/Production publish separation,
- live fetched GitHub snapshot handoff.

## Windows QA Required Now
1. close Catalog Center,
2. clean worktree,
3. fetch/prune + ff-only pull current Epic,
4. run repository `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`,
5. verify Runner `49.3I.7` and `PHASE49_3I_GIT_SNAPSHOT=OK`,
6. confirm FTP password + Bridge token remain masked after Save and restart,
7. confirm AvalAI/OpenRouter stored keys appear masked in their real Provider cards after restart,
8. open AI Center and confirm configured Provider model lists load and are selectable,
9. run exact MakerWorld search URL and confirm Preview produces candidates instead of `Locator.evaluate_all` syntax error,
10. verify each Preview candidate is lightweight with one thumbnail/basic identity,
11. approve one candidate with image limit 20 and verify only then mature full fetch runs,
12. archive another candidate and verify no full fetch,
13. verify direct Product URL path still works,
14. regression-check Product open responsiveness, AI first-paint and Fixed/Range/Formula.

## Local Publish Gate
Still blocked until the Windows 49.3I.7 visual/data/credential QA above passes. Then exactly one `LOCAL PUBLISH ONLY` + Local Django E2E is required before explicit Production approval.

## Exact Next Task
Windows must fast-forward from GitHub and run the repository-owned 49.3I.7 gate. No Local source patch, no reset/stash/delete shortcut, no Production action.
