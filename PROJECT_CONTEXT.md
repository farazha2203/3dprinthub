# PROJECT_CONTEXT — 3DPrintHub

Updated: 2026-08-22
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.5 — Selection Loop Guard + Compact Product Metadata`
Status: `FINAL CI SUCCESS / WINDOWS RERUN PENDING`
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
### Discovery
- explicit valid operator Search/Listing/Category URL is authoritative,
- Preview Candidate first,
- Preview stores identity/title/one thumbnail only,
- Full Fetch only after approval,
- image default 10 / hard max 20,
- Archive/Not Needed preserves blocked identity,
- duplicate boundary source + external id + normalized URL,
- source text sanitized while URLs and Persian editorial fields are preserved.

### Product Workspace
- canonical detailed editor,
- all commercial/editorial/SEO/material/pricing changes happen there,
- Products Explorer remains a lightweight browsing/selection surface.

### Products Explorer — 49.3I.5
Per product card:
- local image,
- product name,
- Product ID,
- Persian state,
- source,
- image count,
- added date,
- publish state,
- Edit Product action.

View modes:
- Extra Large,
- Large,
- Medium,
- Small,
- List.

Selection/context:
- normal/Ctrl/Shift selection,
- Select All / Clear Selection,
- right-click Open / Preview / Remove From Publish Queue,
- safe queue removal only: `upload_ready=0`, `workflow_status=review`,
- no delete/block/Production operation.

Friendly filters:
- کارهای من,
- جدید,
- نیازمند بروزرسانی,
- بدون تصویر,
- بدون محتوا,
- آماده انتشار,
- صف انتشار,
- منتشرشده,
- خطادار,
- همه محصولات.

Friendly sorting:
- اولویت کاری,
- جدیدترین,
- قدیمی‌ترین,
- آخرین بروزرسانی,
- بیشترین امتیاز,
- بیشترین دانلود.

### Selection Loop Prevention — ERR-49-022
49.3I.4 Windows manual QA found a freeze when selecting/opening products.

Root cause:
`card -> hidden Treeview selection_set -> <<TreeviewSelect>> -> load_product -> selection_set -> ...`

49.3I.5 contract:
- card → Treeview is one-way event-producing sync,
- re-entrancy guard,
- only write selection if it differs,
- Treeview callback is state-only,
- Product Open repeat-click guard,
- Tk paint/yield before Product Workspace construction.

### Source URL Routing
For configured source with `model_url_pattern`:
- matching product URL → direct single-product intake,
- other valid HTTP(S) URL → Preview Candidate first,
- Full Fetch only after approval.

### AI
- immediate first-paint progress before synchronous preflight,
- mature 49.3H progress/result/error/cost remains authoritative,
- no fabricated provider cost.

### Pricing
Three independent modes:
- Fixed,
- Range,
- Formula/Dynamic.
Range must not invoke Formula.

## Windows Delivery Contract
Canonical runner: `RUN_PHASE49_3I_LOCAL_GATE.ps1` v49.3I.5.

Runner rules:
- ASCII-only for Windows PowerShell 5.1,
- exact Epic branch,
- clean worktree,
- live `git fetch --prune origin`,
- Local HEAD must equal fetched Remote Epic HEAD,
- no Chat-pinned SHA as sole truth,
- no reset/stash/delete shortcut.

## Latest Verified State
### Windows 49.3I.4 local gate
- Local HEAD: `7330ad6d79d8061998b1fa143051173b558cefbd`,
- 137 Catalog tests PASS,
- 419 Django tests PASS, 2 skipped,
- no new migration,
- Production untouched,
- Explorer visual rendering fixed,
- selection/open feedback loop discovered in manual QA.

### GitHub 49.3I.5 final CI
CI-only PR #50: CLOSED / NOT MERGED.
Validated runtime base: `cdaac6680ea8545f52ece15ecaa3ce0a575eabe9`.
Marker head: `57813f47f649bb2c415aa0fae1481f4a2561ce1d` — not merged.

Successful runs:
- 49.3I `32580222694`,
- 49.3H `32580222686`,
- 49.3G `32580222682`,
- Full Phase49 + Full Django `32580222683`.

Django migration for 49.3I.5: NONE.

## Error Knowledge
Relevant latest records:
- `ERR-49-017` UX87 composition boundary,
- `ERR-49-018` AI first-paint,
- `ERR-49-019` stale Chat SHA handoff,
- `ERR-49-020` clipped thumbnail receiver,
- `ERR-49-021` Product-vs-Group URL routing,
- `ERR-49-022` hidden Treeview selection feedback loop.

Always inspect `docs/ERRORS.md` before troubleshooting.

## Current Acceptance Gate
Windows must pull and test 49.3I.5 before Local Publish:
1. select card without freeze,
2. Edit Product opens one Workspace,
3. right-click Open opens one Workspace,
4. card compact metadata readable,
5. Ready / Queue / Published filters work,
6. Newest / Oldest / Last Updated sorts work,
7. view modes + Ctrl/Shift + context queue removal still work,
8. direct Product vs Group/Search routing still works,
9. AI progress regression QA,
10. Fixed/Range/Formula regression QA.

Only then:
- one LOCAL PUBLISH ONLY,
- Local Django E2E,
- explicit owner approval,
- Production backup/deploy/verify.

## Production
Production is untouched and not approved. Before any Production step, re-verify host branch/commit, MySQL vendor/name, backup, rollback, host constraints and deploy method from repository docs and read-only server state.
