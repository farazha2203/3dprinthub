# PROJECT_CONTEXT — 3DPrintHub

Updated: 2026-08-22
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.4 — Explorer Product Gallery + Source URL Routing`
Production: `UNTOUCHED / NOT APPROVED`

## Operating Rule
Repository/GitHub is the permanent source of truth. Do not infer branch, commit, paths, versions, database, migrations or deploy state from Chat memory.

Required flow:
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI → WINDOWS PULL --FF-ONLY → LOCAL GATE → MANUAL QA → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION BACKUP/DEPLOY/VERIFY`

No direct Production source edits. No ZIP/patch/source delivery through Chat. No destructive reset/stash/delete shortcut for a dirty Windows worktree.

## Canonical Paths
Windows project: `D:\projects\3DPrintHub`
Windows Catalog Center: `D:\projects\3DPrintHub\catalog_center`
Windows venv: `D:\projects\3DPrintHub\.venv`
Windows Catalog persistent root: `D:\projects\3dprinthub-catalog-manager`
Windows Catalog DB: `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`
Production project: `/home/sfkilvrs/3dprinthub`
Production venv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`
Production DB: MySQL `sfkilvrs_EmiAdmin_3dprinthub`

See `docs/PATHS.md` and `docs/HOST_CONSTRAINTS.md` before any environment or deployment work.

## Current Phase49.3I Contracts
### Discovery
- explicit valid operator HTTP(S) Search/Listing/Category URL is authoritative.
- discovery is Preview Candidate first.
- Preview takes basic identity/title/one thumbnail only.
- Full Fetch is allowed only after operator approval.
- image acquisition default 10 / hard max 20.
- Archive/Not Needed stores minimal blocked identity without full fetch.
- duplicate guard uses source + external id + normalized URL.
- source scraped text is sanitized; URLs and Persian editorial fields are preserved.

### Product Workspace
- canonical location for detailed product editing.
- Product list/gallery must not duplicate detailed editor fields.

### Products Gallery
Base contract:
- hidden mature Treeview/filter/sort remains compatibility backend.
- operator cards expose only image, product name and Edit Product.
- local thumbnail resolution: strict local image mapping → `page_extract.json` → local `images/`.
- no network request during Products gallery rendering.
- image click opens large local preview.

### Phase49.3I.4 Explorer Hotfix
Owner Windows QA showed real product images as thin strips.
Verified cause (`ERR-49-020`): a 260x190 PhotoImage was assigned to a `tk.Label(width=32,height=12)`, clipping the receiver.

49.3I.4 behavior:
- explicit pixel-sized image holder + `pack_propagate(False)`,
- child image Label fills holder and has no text-unit width/height,
- view-specific PhotoImage sizing,
- view modes: Extra Large, Large, Medium, Small, List,
- default view: Large,
- view preference stored in existing local Catalog settings table,
- normal click single-select,
- Ctrl-click toggle,
- Shift-click range,
- Select All / Clear Selection,
- selected-count UI,
- right-click: Open, Preview, Remove From Publish Queue, Select All, Clear Selection.

Safe right-click queue removal:
- `upload_ready=0`,
- `workflow_status=review`,
- no product delete,
- no product block,
- no Production unpublish/delete.

Runtime:
- `catalog_center/app/phase49_3i_explorer_hotfix.py`
- composed after the mature `phase49_3i_product_list.install()` boundary.

### Source URL Routing
Verified weakness (`ERR-49-021`): the old listing classifier enumerated only selected URL shapes and could misclassify a source Group/Category URL as a direct product.

49.3I.4 fail-safe contract:
- configured source with non-empty `model_url_pattern` uses that regex as the authoritative product URL boundary,
- matching URL → mature direct single-product intake,
- other valid HTTP(S) URL → Preview Candidate discovery first,
- source without product regex → mature prior fallback behavior.

MakerWorld Direct Product example:
`https://makerworld.com/en/models/2834255-cake-stand-small-table-great-for-cakes-cupcakes?from=search#profileId-3158565`

MakerWorld Search example:
`https://makerworld.com/en/search/models?keyword=cake+stand`

### AI
- first-paint progress appears before synchronous preflight.
- mature 49.3H progress/result/error/cost UI remains source of truth.
- provider/model/network/request implementation is not duplicated.

### Pricing
Three independent modes:
- Fixed,
- Range,
- Formula/Dynamic.
Range must never invoke Formula.
No runtime mutation of migration-owned Django choices.

### Git Handoff
Runner: `RUN_PHASE49_3I_LOCAL_GATE.ps1` v49.3I.4.
- ASCII-only for Windows PowerShell 5.1.
- clean worktree required.
- exact Epic branch required.
- live `git fetch --prune origin`.
- Local HEAD must equal fetched Remote Epic HEAD.
- no Chat-pinned SHA as sole handoff truth.

## Current Validation State
49.3I.4 implementation and documentation are on GitHub.
Final CI-only validation probe is pending.
Windows has not yet pulled/tested 49.3I.4.
No Local Publish acceptance has occurred for 49.3I.4.
Production is untouched.

## Required CI
- Phase49.3I dedicated CI.
- Phase49.3H regression CI.
- Phase49.3G regression CI.
- Full Phase49 + Full Django CI.
- runner ASCII/live-snapshot contract.
- `makemigrations --check --dry-run` = no changes.
- no destructive schema operations.

## Required Windows QA After CI
1. pull current Epic with clean worktree and `--ff-only`.
2. run v49.3I.4 repository gate with `-LaunchApp`.
3. full thumbnails, no thin strips.
4. all five Explorer view modes.
5. Ctrl/Shift multi-select.
6. right-click menu and safe local queue removal.
7. large image preview.
8. Edit Product → Product Workspace.
9. Direct Product URL → direct intake.
10. Group/Category/Search URL → Preview first.
11. approved-only Full Fetch and image cap <=20.
12. AI first-paint regression QA.
13. Fixed/Range/Formula QA.
14. only then one LOCAL PUBLISH ONLY + Local Django E2E.

## Production Gate
No Production commands until:
- CI success,
- Windows automated gate success,
- visual/data QA success,
- LOCAL PUBLISH E2E success,
- explicit owner approval,
- verified production path/branch/commit/DB vendor/name,
- backup and rollback readiness.

## Exact Next Step
Run final GitHub CI validation for 49.3I.4, close the CI-only probe without merge on success, then issue a live-snapshot Windows pull/local-gate handoff. Do not patch local source manually and do not touch Production.
