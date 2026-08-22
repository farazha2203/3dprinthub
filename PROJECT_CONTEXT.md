# PROJECT_CONTEXT — 3DPrintHub

Updated: 2026-08-22
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.6 — Secure Credential Field Persistence`
Status: `FINAL CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Operating Rule
GitHub/Repository is the permanent source of truth. Do not infer branch, commit, paths, runtime versions, database, migrations or deployment state from Chat memory.

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

## Current Phase49.3I Contracts
### Discovery / Routing
- explicit valid operator Search/Listing/Category URL is authoritative,
- Preview Candidate first,
- Preview stores identity/title/one thumbnail only,
- Full Fetch only after approval,
- image default 10 / hard max 20,
- Archive/Not Needed preserves blocked identity,
- duplicate boundary source + external id + normalized URL,
- source text sanitized while URLs and Persian editorial fields are preserved,
- configured `model_url_pattern` distinguishes Product URL from Group/Category/Search URL.

Owner Windows QA after 49.3I.5 confirms the Product-vs-Group/sub-branch routing problem is fixed.

### Product Workspace / Products Explorer
- Product Workspace is canonical detailed editor,
- Products Explorer stays visual/lightweight,
- cards include local image, name, ID, state, source, image count, added date, publish state and Edit Product,
- Extra Large / Large / Medium / Small / List views,
- normal/Ctrl/Shift selection,
- Select All / Clear Selection,
- right-click Open / Preview / safe Remove From Publish Queue,
- safe queue removal only: `upload_ready=0`, `workflow_status=review`,
- no delete/block/Production operation,
- Persian filters/sorts remain available.

### Selection Loop Prevention — ERR-49-022
49.3I.5 makes card → hidden Treeview synchronization one-way, re-entrancy guarded and state-only on the reverse callback. Product Open also has repeat-click guard and Tk paint/yield before Workspace construction.

### Secure Credential Persistence — ERR-49-023
Windows Credential Store service `3DPrintHub Catalog Intelligence` remains the secure source of truth.

49.3I.6:
- hydrates stored FTP password + Bridge token into masked fields at startup,
- hydrates selected AI Provider key,
- rehydrates fields after mature Save handlers clear them,
- Provider switch loads that Provider's stored key,
- same-provider routine refresh does not overwrite unsaved input,
- explicit delete/clear remains authoritative,
- no credential is persisted in SQLite, Git, source, diagnostics or logs.

### AI / Pricing
- immediate AI first-paint before synchronous preflight,
- mature 49.3H progress/result/error/cost remains authoritative,
- no fabricated provider cost,
- Fixed / Range / Formula remain independent,
- Range never invokes Formula.

## Windows Delivery Contract
Canonical runner: `RUN_PHASE49_3I_LOCAL_GATE.ps1` v49.3I.6.

Runner rules:
- ASCII-only for Windows PowerShell 5.1,
- exact Epic branch,
- clean worktree,
- live `git fetch --prune origin`,
- Local HEAD must equal fetched Remote Epic HEAD,
- no Chat-pinned SHA as sole truth,
- no reset/stash/delete shortcut.

## Latest Verified State
### Windows
- 49.3I.5 launched successfully,
- Product URL vs Group/Category/Search/sub-branch routing confirmed corrected by owner,
- 49.3I.6 credential persistence not yet pulled/tested.

### GitHub 49.3I.6 final CI
CI-only PR #51: CLOSED / NOT MERGED.
Validated Epic base: `f1e92f8f42a6ed90bf1001dc14a15638828ee341`.
Marker head: `fa8e4bcf5f7795983434f7cfd34c88918273bae6` — not merged.

Successful runs:
- 49.3I `32583277412`,
- 49.3H `32583277584`,
- 49.3G `32583277406`,
- Full Phase49 + Full Django `32583277418`.

Django migration for 49.3I.6: NONE.

## Relevant Error Knowledge
- `ERR-49-017` UX87 composition boundary,
- `ERR-49-018` AI first-paint,
- `ERR-49-019` stale Chat SHA handoff,
- `ERR-49-020` clipped thumbnail receiver,
- `ERR-49-021` Product-vs-Group URL routing,
- `ERR-49-022` hidden Treeview selection feedback loop,
- `ERR-49-023` secure credentials not hydrated into masked fields.

Always inspect `docs/ERRORS.md` before troubleshooting.

## Current Acceptance Gate
Windows must pull/test 49.3I.6 before Local Publish:
1. AI key stays masked/populated after Save,
2. restart restores stored AI key,
3. Provider switch restores that Provider's key,
4. FTP password + Bridge token stay masked/populated after Save/restart,
5. live AI/FTP/Bridge tests use secure credentials,
6. selection/open remains responsive,
7. Product-vs-Group/Search routing remains correct,
8. AI progress regression QA,
9. Fixed/Range/Formula regression QA.

Only then:
- one LOCAL PUBLISH ONLY,
- Local Django E2E,
- explicit owner approval,
- Production backup/deploy/verify.

## Production
Production is untouched and not approved. Before any Production step, re-verify host branch/commit, MySQL vendor/name, backup, rollback, host constraints and deploy method from repository docs and read-only server state.
