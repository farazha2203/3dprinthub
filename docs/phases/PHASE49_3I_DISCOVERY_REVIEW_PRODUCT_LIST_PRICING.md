# Phase49.3I — Discovery Review + Product Explorer + Pricing + Credential Persistence

Updated: 2026-08-22
Branch: `epic/phase49-unified-product-slider-sync`
Current Hotfix: `49.3I.6`
Status: `GITHUB IMPLEMENTED / FINAL CI PENDING / WINDOWS QA PENDING`
Production: `UNTOUCHED`

## Goal
Phase49.3I provides safe high-volume product discovery/review while Product Workspace remains the canonical detailed editor. It also owns the current Explorer interaction/routing fixes and the operator-visible persistence of securely stored Catalog Center credentials.

## Preserved Phase49.3I Contracts
### Discovery
- exact operator HTTP(S) Search/Listing/Category URL is authoritative,
- Preview Candidate first,
- Preview stores identity/title/one thumbnail only,
- Full Fetch only after approval,
- default image intake 10 / hard max 20,
- Archive/Not Needed stores blocked identity without Full Fetch,
- dedupe boundary: source code + external id + normalized URL,
- source text sanitation preserves URLs and Persian editorial fields.

### Products Explorer
- visual lightweight product browsing,
- Product Workspace owns detailed commercial/editorial/SEO/material/pricing editing,
- local-only thumbnails,
- Extra Large / Large / Medium / Small / List views,
- normal/Ctrl/Shift selection,
- Select All / Clear Selection,
- right-click Open / Preview / safe Remove From Publish Queue,
- queue removal only sets `upload_ready=0` and `workflow_status=review`,
- no product delete/block/Production operation,
- compact Product ID/state/source/image count/added date/publish state,
- Persian filters and sorting.

### Selection Stability
`ERR-49-022` feedback cycle is guarded:
`card -> hidden Treeview selection -> TreeviewSelect -> state-only callback`.
The callback never writes selection back, and repeated Product Workspace open actions are guarded.

### Product URL Routing
For a configured source with non-empty `model_url_pattern`:
- matching Product URL → direct single-product intake,
- other valid HTTP(S) Group/Category/Search URL → Preview Candidate first,
- Full Fetch only after approval.

Windows owner QA after 49.3I.5 confirms this routing/sub-branch issue is fixed.

### Pricing
Three independent modes remain:
- Fixed,
- Range,
- Formula/Dynamic.
Range never invokes Formula.

### AI
Immediate first-paint progress remains before synchronous preflight and hands off to the mature 49.3H progress/result/error/cost stack.

## Phase49.3I.6 — Secure Credential Field Persistence
### Owner report
Catalog Center 49.3I.5 launches, but Token/API Key/FTP credential fields appear empty again. The expected contract is that credentials saved once remain stable across restarts/releases.

### Root Cause — ERR-49-023
The secure storage backend itself already exists and uses Windows Credential Store under stable service name:
`3DPrintHub Catalog Intelligence`.

Runtime accessors already use secure fallback:
- provider key: field/environment → `get_provider_key()`,
- site connection: field/environment → `get_secret()`.

The UI lifecycle was inconsistent with that backend:
- `ai_key` started empty,
- FTP password and Bridge token fields hydrated only from environment/new input,
- mature secure Save handlers wrote to Credential Store and then cleared the widgets,
- restart did not put secure-store values back into the masked widgets.

Thus credentials could still exist securely while the UI looked as if they had vanished.

### Corrected Contract
New additive module:
`catalog_center/app/phase49_3i_secret_persistence.py`

It:
- keeps Credential Store/environment as the secure source of truth,
- hydrates FTP password and Bridge token into masked fields at startup when empty,
- hydrates selected AI Provider key into the masked field,
- rehydrates fields after successful mature Save clears them,
- reloads the stored key when Provider changes,
- preserves unsaved same-provider input during ordinary UI refresh,
- preserves explicit delete/clear actions,
- never stores secrets in SQLite, logs, source files, diagnostics or Git.

Composition occurs after the mature 49.3I Product Explorer installer. No older phase installer is modified.

## Runtime Surface — 49.3I.6
Added:
- `catalog_center/app/phase49_3i_secret_persistence.py`,
- `catalog_center/tests/test_epic49_phase49_3i_secret_persistence.py`.

Changed:
- `catalog_center/app/phase49_3i_product_list.py` for same-phase App87 composition,
- `RUN_PHASE49_3I_LOCAL_GATE.ps1` → v49.3I.6,
- `.github/workflows/phase49-3i-ci.yml`.

## Regression Coverage
Dedicated 49.3I.6 tests verify:
1. startup secure hydration without SQLite,
2. post-save secure rehydration after mature handlers clear widgets,
3. provider-specific stored key hydration on Provider switch,
4. unsaved newly typed key is not overwritten by normal same-provider refresh,
5. the hotfix source contains no SQLite `set_setting`, logger, file write or file-open secret persistence path.

CI additionally verifies:
- secret persistence installer composes after the mature Product Explorer,
- canonical runner is ASCII-only and v49.3I.6,
- previous Explorer/selection/routing tests,
- 49.3H/3G regressions,
- Django check / no migration drift,
- no destructive schema operations.

## Database / Migration / Secret Safety
- Django schema change: NONE intended; final CI pending,
- Catalog schema change: NONE,
- no reset/drop/truncate,
- no media rewrite/delete,
- no secret migration into SQLite/source/Git/logs,
- Production untouched.

## Must-Not-Touch
- Product Workspace detailed editor,
- mature secure keyring backend and explicit delete actions,
- Product-vs-Group routing,
- selection-loop guard,
- 49.3H AI result/error/cost behavior,
- image default 10 / hard max 20,
- Preview → Approve → Full Fetch,
- Fixed / Range / Formula independence,
- Product/Hero revision/idempotency,
- Production paths/DB/media,
- historical media.

## Windows Acceptance Gate After Final CI
Windows must verify:
- AI key remains populated as a masked value after secure Save,
- app restart restores the masked stored AI key,
- Provider switch restores that Provider's stored key,
- FTP password and Bridge token remain masked/populated after Save and restart,
- AI/FTP/Bridge connection tests use the secure credentials successfully,
- no secrets are written into SQLite/log/source,
- Product selection/open remains responsive,
- Product-vs-Group/Search routing remains correct,
- AI first-paint and Fixed/Range/Formula regressions still pass.

Only after that:
- one `LOCAL PUBLISH ONLY`,
- Local Django E2E,
- explicit owner acceptance,
- then Production verification/backup/deploy path may begin.

## Exact Next Step
Finish final GitHub CI validation for 49.3I.6 and close the CI-only marker PR without merge. Do not ask Windows to pull until all required workflows succeed. Production remains blocked.
