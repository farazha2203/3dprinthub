# CURRENT PROJECT STATE

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Branch: `epic/phase49-unified-product-slider-sync`
Active Phase: `49.3I`
Active Hotfix: `49.3I.8 — Observable AI Execution Recovery`
Status: `GITHUB UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Current Position
The latest Windows Product Workspace screenshot exposed a new execution-path bug in the bottom operator action `✨ تکمیل هوشمند همه فیلدهای AI`.

The visible status stayed on `avalai ... در حال تولید محتوا...` for roughly five minutes with no durable progress window. The operator had no reliable indication of connection/send/receive/save state and eventually had to close the Workspace.

Repository inspection proved this was not the same bug as `ERR-49-018`.

## ERR-49-026 — Bottom All-Fields AI Button Bypassed The Mature Task Center
Verified Root Cause:
- the exact bottom button is created by `phase49_3c_operator_recovery.py`,
- `_phase49_3c_all_ai()` still called legacy `ProductStudio.generate_ai("commerce")`,
- that legacy worker only changed a status string and later opened the old preview dialog,
- it did **not** call the mature Phase49.3E/3F/3H `_phase49_3e_run_ai()` path,
- therefore the existing 49.3I first-paint progress handoff, connection/send/receive progress, 49.3H result/error drawer and execution observability never applied to this real operator button.

This explains why earlier AI-progress tests could pass while the screenshot button still looked frozen.

## Phase49.3I.8 Implemented Delta
New additive module:
`catalog_center/app/phase49_3i_ai_execution_recovery.py`

Behavior:
- routes the real bottom `all fields` operator button into `_phase49_3e_run_ai("all")`,
- routes non-Quick `AI this stage` actions into the same mature Task Center (`images` keeps image scope),
- preserves the existing Quick/title-only path,
- does not create another AI client or network worker,
- preserves 49.3I immediate first-paint before synchronous preflight,
- then uses the mature 49.3H progress/result/error/cost stack,
- adds an always-visible elapsed timer,
- adds `توقف انتظار`,
- adds a 210-second operator watchdog matching the existing single AI request upper-bound contract,
- Stop/timeout invalidates the execution generation,
- a late network result from a cancelled/timed-out run is discarded and cannot mutate the product,
- an error remains visible; the application is not closed.

The existing blocking network worker is not force-killed from Tk/Python. It may finish in the background, but after cancellation/timeout its result is explicitly stale and cannot be applied.

## Source Reference / MakerWorld State
The 49.3I.7 Preview recovery remains active and was regression-tested again:
- explicit Search/Listing URL remains authoritative,
- Preview uses the escaped raw JavaScript evaluator,
- Preview remains one-thumbnail/basic-identity only,
- approved candidate Full Fetch still calls the mature `extract_direct_link()` path only after approval,
- image limit remains 1..20,
- Direct Product path remains mature/unchanged.

No source-crawler/full-fetch code was rewritten in 49.3I.8.

Real Windows MakerWorld QA is still required after pulling 49.3I.8; code/CI success is not being treated as Windows acceptance.

## Runtime Files Added/Changed
Added:
- `catalog_center/app/phase49_3i_ai_execution_recovery.py`
- `catalog_center/tests/test_epic49_phase49_3i_ai_execution_recovery.py`

Changed:
- `catalog_center/app/phase49_3i_local_qa_hotfix.py` for same-phase runtime composition,
- `RUN_PHASE49_3I_LOCAL_GATE.ps1` → `49.3I.8`,
- `.github/workflows/phase49-3i-ci.yml`.

No Django model/migration, Catalog schema, media or Production change.

## Final GitHub Validation — 49.3I.8
CI-only PR: `#53`
State: `CLOSED / NOT MERGED`
Validated Epic runtime base: `3fdab5dc4a56204b6370f72df04ec0956e8ba6ce`
CI marker head: `0d05d0fb25f02daa07df93f9cf47d2ea0333b8b8` — not merged.

Successful workflows:
- Phase49.3I Discovery Review Pricing CI — Run `32620646603` — SUCCESS.
- Phase49.3H SEO Cost Image Limit CI — Run `32620646600` — SUCCESS.
- Phase49.3G Workspace Usability CI — Run `32620646605` — SUCCESS.
- Phase49 Epic Unified CI / Full Django — Run `32620646657` — SUCCESS.

Validated:
- Windows runner v49.3I.8 / ASCII-only contract,
- live fetched GitHub snapshot guard,
- Python compile,
- real legacy all-fields button → mature Task Center routing,
- non-Quick stage assistant routing,
- Quick/title-only behavior preserved,
- observable elapsed-progress/watchdog source contract,
- no second AI worker/client in the recovery module,
- stale/cancelled full and image AI results cannot apply,
- 49.3I.7 Preview evaluator recovery still composed,
- provider credential/model-catalog regressions,
- Explorer/selection/routing regressions,
- 49.3H/3G regressions,
- Django checks,
- `makemigrations --check --dry-run` = no changes,
- safe migration plan,
- Windows Catalog Epic49 tests,
- Full Django suite.

## Database / Migration / Media / Secret Safety
- Django migration for 49.3I.8: `NONE` — CI verified.
- Catalog schema migration: `NONE`.
- no DB reset/drop/truncate.
- no data/media rewrite/delete.
- no secret storage change.
- Production DB/media/source untouched.

## Windows QA Required Now
1. close Catalog Center completely,
2. verify clean worktree,
3. fetch/prune + ff-only pull current Epic,
4. run repository `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`,
5. verify Runner `49.3I.8` + `PHASE49_3I_GIT_SNAPSHOT=OK`,
6. open one Product Workspace and press the **bottom** `تکمیل هوشمند همه فیلدهای AI`,
7. immediate startup progress must appear before preflight,
8. it must hand off to connection/send/receive/save/result progress,
9. elapsed time + `توقف انتظار` must remain visible and the app must remain responsive,
10. on provider/network error, the error must stay visible and the app must remain open,
11. Stop Waiting or 210s timeout must prevent any late result from modifying the product,
12. exact MakerWorld Search URL must produce Preview candidates without `Locator.evaluate_all` syntax error,
13. Preview stays lightweight; approve one with image limit 20 and verify Full Fetch starts only after approval,
14. recheck stored Provider keys/model lists + FTP/Bridge credentials,
15. recheck Product open/selection and Fixed/Range/Formula.

## Local Publish Gate
Still blocked. Only after the Windows interaction/data QA above passes:
- exactly one `LOCAL PUBLISH ONLY`,
- Local Django E2E,
- verify product/image/pricing/provenance payload,
- explicit owner approval.

## Exact Next Task
Windows must fast-forward the live GitHub snapshot and run repository-owned Runner 49.3I.8. No direct Local source patch, no reset/stash/delete shortcut, no Local Publish yet, no Production action.
