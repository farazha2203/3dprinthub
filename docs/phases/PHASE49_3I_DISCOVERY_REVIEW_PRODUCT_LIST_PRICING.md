# Phase49.3I — Discovery Review + Product Explorer + Pricing + Observable AI Execution

Updated: 2026-08-23
Branch: `epic/phase49-unified-product-slider-sync`
Current Hotfix: `49.3I.8`
Status: `FINAL CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Goal
Provide a business-usable Catalog Center flow that can discover many source products cheaply, let the operator review lightweight candidates, full-fetch only approved products with an operator-selected image limit, prepare/edit with observable AI actions, publish locally, and only reach Production after explicit acceptance.

## Canonical Discovery State Machine
`Exact Search/Listing/Category URL → Preview Candidate → Approve/Archive → Approved Full Fetch → Product Workspace → LOCAL PUBLISH ONLY → Local Django E2E → Owner Approval → Production`

### Preview Candidate
Must contain only:
- source identity / external id,
- source URL,
- basic title,
- one thumbnail.

Must NOT:
- enter full product pages,
- download all images,
- create parallel full extraction,
- invoke Production.

### Approved Full Fetch
Only approved candidate(s) may enter the mature full extraction path.
Image limit is selectable `1..20`, default `10`; `20` is valid when the operator asks for 20 images.

### Archive / Not Needed
Archive keeps minimal blocked identity and prevents rediscovery until restore; it does not Full Fetch.

## Source URL Routing
For a source with `model_url_pattern`:
- Product URL match → mature Direct Product intake,
- valid non-product Group/Category/Search/Listing/sub-branch URL → Preview first.

Owner Windows QA already confirmed Product-vs-Group routing was corrected before 49.3I.7.

## Preview Recovery — ERR-49-024
MakerWorld exact Search URL had reached Preview correctly but failed with `Locator.evaluate_all: SyntaxError: Invalid or unexpected token`.

49.3I.7 corrected only the Stage-1 browser expression:
- raw Python JavaScript source preserves browser-side `\n`,
- existing `candidates_from_dom_rows()` remains the lightweight parser,
- no Direct/Full extraction is called by the recovery layer,
- mature Direct Product and approved Full Fetch remain untouched.

49.3I.8 preserves and regression-tests that recovery. Real Windows MakerWorld Preview acceptance is still required.

## AI Provider Hub Contract
Current provider cards remain:
- AvalAI,
- OpenRouter,
- Google Gemini Direct,
- OpenAI Direct.

49.3I.7 preserved Windows Credential Store/environment as the credential source of truth, hydrates the real per-provider `_ai_hub_key_vars`, and background-loads model catalogs through the existing mature provider adapters. No parallel provider client was introduced.

## Observable AI Execution — ERR-49-026
### Windows Incident
The exact bottom Product Workspace button `تکمیل هوشمند همه فیلدهای AI` stayed at AvalAI content generation for roughly five minutes with no durable execution window. The operator could not tell whether it was connected, waiting, failed or stuck.

### Verified Root Cause
That visible bottom action belongs to Phase49.3C `_phase49_3c_all_ai()` and still called legacy `ProductStudio.generate_ai("commerce")`.

The mature observable path is `_phase49_3e_run_ai()`. The legacy bottom-button path bypassed it, so it also bypassed:
- 49.3I immediate first-paint,
- Phase49.3F connection/send/receive progress,
- Phase49.3H result/error/cost visibility.

This was a command-path composition defect, not simply the earlier preflight first-paint defect from `ERR-49-018`.

### 49.3I.8 Corrected Contract
`catalog_center/app/phase49_3i_ai_execution_recovery.py`:
- routes real bottom All-Fields AI → `_phase49_3e_run_ai("all")`,
- routes non-Quick stage AI → mature Task Center, with image stage preserving image scope,
- preserves Quick/title-only action,
- adds no second AI client/network worker,
- keeps first-paint before synchronous preflight,
- exposes elapsed time continuously,
- adds `توقف انتظار`,
- uses a 210-second operator watchdog aligned with the existing single AI request upper-bound,
- generation-tags executions,
- cancel/timeout makes the generation stale,
- late stale full/image results are discarded and cannot modify product data,
- provider/network errors remain visible and the application remains open.

The underlying blocking urllib worker is not force-killed because that would be unsafe. It may finish later in the background; its result is non-applicable after cancel/timeout.

## Products Explorer
Preserved:
- local image + product name + compact ID/state/source/image-count/date/publish-state,
- Edit Product → canonical Product Workspace,
- large image preview,
- Extra Large / Large / Medium / Small / List,
- normal/Ctrl/Shift selection,
- Select All / Clear,
- right-click Open / Preview / safe Remove From Publish Queue,
- selection feedback-loop guard,
- Persian filters/sorts.

Safe queue removal only changes local queue state; no delete/block/Production operation.

## Pricing
Independent modes:
- Fixed,
- Range,
- Formula/Dynamic.
Range never invokes Formula.

## Runtime Surface — 49.3I.8
Added:
- `catalog_center/app/phase49_3i_ai_execution_recovery.py`,
- `catalog_center/tests/test_epic49_phase49_3i_ai_execution_recovery.py`.

Changed:
- `catalog_center/app/phase49_3i_local_qa_hotfix.py`,
- `RUN_PHASE49_3I_LOCAL_GATE.ps1` → v49.3I.8,
- `.github/workflows/phase49-3i-ci.yml`.

Preserved from 49.3I.7:
- Preview recovery,
- real Provider Hub secure hydration,
- Provider model catalog loading,
- Preview → Approve → mature Full Fetch.

## Final GitHub Validation — 49.3I.8
CI-only PR #53: `CLOSED / NOT MERGED`.
Validated runtime base: `3fdab5dc4a56204b6370f72df04ec0956e8ba6ce`.
Marker head: `0d05d0fb25f02daa07df93f9cf47d2ea0333b8b8` — not merged.

Successful runs:
- Phase49.3I `32620646603` — SUCCESS,
- Phase49.3H `32620646600` — SUCCESS,
- Phase49.3G `32620646605` — SUCCESS,
- Full Phase49 + Full Django `32620646657` — SUCCESS.

Validation includes:
- runner v49.3I.8 / ASCII-only Windows PS5.1,
- live Git snapshot guard,
- Python compile,
- exact visible All-Fields command → mature Task Center routing,
- non-Quick stage command routing,
- Quick/title-only preservation,
- elapsed/watchdog/stale-result contracts,
- no duplicate AI client/worker in recovery module,
- Preview recovery composition,
- Provider Hub/model-list regressions,
- Explorer/selection/routing regressions,
- Phase49.3H/3G regressions,
- Django no-migration contract,
- no destructive schema operation,
- Windows Catalog Epic49 tests,
- Full Django suite.

## Database / Migration / Secret Safety
- Django migration: `NONE` — CI verified,
- Catalog schema migration: `NONE`,
- no reset/drop/truncate,
- no historical data rewrite,
- no media rewrite/delete,
- no credential storage change,
- Production untouched.

## Windows Acceptance Gate — NEXT
1. close Catalog Center and require clean worktree,
2. live fetch/prune + ff-only pull current Epic,
3. run repository `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`,
4. Runner must be `49.3I.8` and Git snapshot marker OK,
5. open Product Workspace and click the **bottom** All-Fields AI action,
6. startup progress must appear immediately,
7. it must hand off to connection/send/wait/receive/save/result-error progress,
8. elapsed time + `توقف انتظار` must stay visible,
9. app must remain responsive while waiting,
10. errors must remain visible without closing the app,
11. Stop Waiting or 210s watchdog must prevent late result mutation,
12. exact MakerWorld Search URL must return Preview candidates without `Locator.evaluate_all` syntax error,
13. Preview remains one thumbnail/basic identity only,
14. approve one candidate with image limit 20; only then mature Full Fetch runs,
15. archive another candidate; no Full Fetch,
16. recheck Provider keys/model lists, FTP/Bridge credentials, Product selection/open and pricing modes.

Only after all above PASS:
- one `LOCAL PUBLISH ONLY`,
- Local Django E2E,
- explicit owner acceptance,
- then Production backup/deploy/verification may begin.
