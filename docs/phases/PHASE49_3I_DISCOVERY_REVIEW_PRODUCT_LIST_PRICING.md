# Phase49.3I — Discovery Review + Product Explorer + Pricing + Provider Recovery

Updated: 2026-08-22
Branch: `epic/phase49-unified-product-slider-sync`
Current Hotfix: `49.3I.7`
Status: `FINAL CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Goal
Provide a business-usable Catalog Center flow that can discover many source products cheaply, let the operator review lightweight candidates, full-fetch only approved products with an operator-selected image limit, prepare/edit/publish locally, and only reach Production after explicit acceptance.

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

Owner Windows QA already confirmed this routing problem is fixed.

## 49.3I.7 Preview Recovery — ERR-49-024
### Incident
MakerWorld exact Search URL routed to Preview correctly but failed with:
`Locator.evaluate_all: SyntaxError: Invalid or unexpected token`.

### Root Cause
The Stage-1 DOM expression was embedded in a normal Python triple-quoted string. An intended JavaScript `\n` escape became a literal newline inside a JavaScript single-quoted string before Playwright evaluated it.

### Fix
`catalog_center/app/phase49_3i_preview_recovery.py`:
- uses a raw Python JavaScript source string,
- keeps valid browser-side escaping,
- uses existing `candidates_from_dom_rows()`,
- patches only the Preview candidate function,
- never calls Direct/Full extraction.

Mature `classic_methods.discover_classic` and `collect_classic_exact` remain untouched.

## AI Provider Hub Contract
Registered current provider cards remain:
- AvalAI,
- OpenRouter,
- Google Gemini Direct,
- OpenAI Direct.

Provider model listing uses the existing mature `AIProviderClient` / Google adapter; no parallel client is introduced.

## 49.3I.7 Provider Recovery — ERR-49-025
### Incident
Stored AI keys still appeared empty in real Provider cards after 49.3I.6 and model lists were therefore not reliably visible.

### Root Cause
49.3I.6 hydrated legacy `ai_key`, FTP password and Bridge token. The real Phase49.3F AI Center uses `_ai_hub_key_vars` per Provider, and its secure Save handler clears those variables after persisting to Windows Credential Store.

### Fix
`phase49_3i_secret_persistence.py` now:
- hydrates the real per-provider `_ai_hub_key_vars`,
- rehydrates Provider cards after mature secure Save,
- preserves FTP password + Bridge token hydration,
- hydrates stored OpenRouter management/OpenAI admin masked fields,
- does not overwrite newly typed non-empty input,
- background-loads model catalogs for configured providers,
- fills existing Model ID combobox/cache/status,
- preserves manual model picker/API refresh,
- keeps secrets out of SQLite/Git/source/logs.

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

## AI Execution
Full AI autofill preserves immediate first-paint before synchronous preflight and the mature 49.3H progress/result/error/cost stack.

## Runtime Surface — 49.3I.7
Added:
- `catalog_center/app/phase49_3i_preview_recovery.py`
- `catalog_center/tests/test_epic49_phase49_3i_preview_recovery.py`

Changed:
- `catalog_center/app/phase49_3i_secret_persistence.py`
- `catalog_center/tests/test_epic49_phase49_3i_secret_persistence.py`
- `RUN_PHASE49_3I_LOCAL_GATE.ps1` → v49.3I.7
- `.github/workflows/phase49-3i-ci.yml`

## Final GitHub Validation
CI-only PR #52: `CLOSED / NOT MERGED`.
Validated runtime base: `4e0b1b7f0f8934a03ab74037bdce5f9abe55b425`.
Marker head: `5097f45f069e40af64d452ffaa8cd07399a977f2` — not merged.

Successful runs:
- Phase49.3I `32585956198` — SUCCESS
- Phase49.3H `32585956149` — SUCCESS
- Phase49.3G `32585956156` — SUCCESS
- Full Phase49 + Full Django `32585956155` — SUCCESS

Validation includes:
- runner v49.3I.7 / ASCII-only Windows PS5.1,
- live Git snapshot guard,
- Preview JavaScript escape test,
- Preview-only/no-full-fetch source contract,
- real Provider Hub key hydration,
- post-save rehydration,
- Provider model catalog scheduling/cache/combobox tests,
- prior 49.3I/3H/3G regressions,
- Django no-migration contract,
- no destructive schema operation,
- Full Django suite.

## Database / Migration / Secret Safety
- Django migration: `NONE` — CI verified.
- Catalog schema migration: `NONE`.
- no reset/drop/truncate.
- no historical data rewrite.
- no media rewrite/delete.
- secrets remain Windows Credential Store/environment only.
- Production untouched.

## Windows Acceptance Gate — NEXT
1. close Catalog Center and require clean worktree,
2. live fetch/prune + ff-only pull current Epic,
3. run repository `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`,
4. Runner must be `49.3I.7` and Git snapshot marker OK,
5. FTP password + Bridge token remain masked after Save/restart,
6. AvalAI/OpenRouter saved keys remain masked in real Provider cards after restart,
7. configured Provider model lists load into Model ID controls and model picker,
8. exact MakerWorld search URL returns Preview candidates without JavaScript syntax error,
9. Preview candidate shows one thumbnail/basic identity only,
10. approve one candidate with image limit 20; only then Full Fetch runs,
11. archive another candidate; no Full Fetch,
12. direct Product URL path still works,
13. Product selection/open, AI first-paint, Fixed/Range/Formula regressions pass.

Only after all above PASS:
- one `LOCAL PUBLISH ONLY`,
- Local Django E2E,
- explicit owner acceptance,
- then Production backup/deploy/verification may begin.
