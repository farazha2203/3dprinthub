# CURRENT PROJECT STATE

Updated: 2026-08-22
Repository: `farazha2203/3dprinthub`
Branch: `epic/phase49-unified-product-slider-sync`
Active Phase: `49.3I`
Active Hotfix: `49.3I.4 — Explorer Product Gallery + Source URL Routing`
Status: `GITHUB UPDATED / FINAL CI SUCCESS / WINDOWS LOCAL QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Current Position
The owner's Windows QA exposed two additional operator-facing regressions and both are now fixed on GitHub and validated by the final CI probe.

Phase49.3I.4 is ready for a clean Windows pull and local visual/data QA. It is NOT yet approved for Local Publish acceptance or Production.

## Owner-Reported Local QA Findings
1. Product images in the gallery rendered as thin horizontal strips instead of full thumbnails.
2. Products browsing must behave more like Windows Explorer:
   - configurable view size,
   - multi-selection,
   - right-click context actions,
   - safe removal from the local publish queue.
3. Direct product URL intake versus source group/category/search URL intake must be routed correctly.

## Verified Root Causes
### ERR-49-020 — Clipped product thumbnails
`phase49_3i_product_list.py` created a 260x190 `PhotoImage` but assigned it to a `tk.Label` that still had `width=32` and `height=12`. Tk Label width/height are text-unit dimensions and clipped the image receiver.

### ERR-49-021 — Group/category URL routing weakness
The prior route classifier recognized a finite list of listing/search URL shapes. A source category/group/collection URL outside those shapes could reach direct full extraction. Configured sources already expose an authoritative `model_url_pattern`, which is now used as the product-vs-listing boundary.

## Phase49.3I.4 Implemented Delta
### Explorer-style Products surface
- Mature hidden Treeview/filter/sort backend preserved.
- Lightweight gallery content preserved: image + product name + Edit Product only.
- Thumbnails render inside explicit pixel-sized holder frames; image Labels have no text-unit width/height.
- persistent view modes through the existing local Catalog settings table:
  - Extra Large Icons,
  - Large Icons,
  - Medium Icons,
  - Small Icons,
  - List.
- normal/Ctrl/Shift product selection.
- Select All / Clear Selection and selected count.
- right-click context menu:
  - Open Product,
  - Image Preview,
  - Remove From Publish Queue,
  - Select All,
  - Clear Selection.
- Remove From Publish Queue uses only:
  - `upload_ready=0`,
  - `workflow_status=review`.
- It does NOT delete/block a product and does NOT unpublish/delete anything on Production.
- Normal image click still opens the large local preview.

### Source-aware URL routing
For a configured source with a non-empty `model_url_pattern`:
- URL matches the source product regex → mature direct single-product intake.
- valid HTTP(S) URL does not match the product regex → Preview Candidate discovery first.
- source without product regex preserves the mature previous fallback behavior.

## Runtime Files Added/Changed
- `catalog_center/app/phase49_3i_explorer_hotfix.py`
- `catalog_center/app/phase49_3i_product_list.py`
- `catalog_center/tests/test_epic49_phase49_3i_explorer_hotfix.py`
- `RUN_PHASE49_3I_LOCAL_GATE.ps1` — v49.3I.4
- `.github/workflows/phase49-3i-ci.yml`

## Final GitHub Validation
CI-only PR: `#49`
State: `CLOSED / NOT MERGED`
Validated Epic base: `f792fd01d643a7b3d071234a4237f2d6932679b3`
CI marker head: `3bb010414c55e62a5b09c3b2f0e123870980c0e5` — not merged.

Successful workflows:
- Phase49.3I Discovery Review Pricing CI — Run `32577907763` — SUCCESS.
- Phase49.3H SEO Cost Image Limit CI — Run `32577907755` — SUCCESS.
- Phase49.3G Workspace Usability CI — Run `32577907768` — SUCCESS.
- Phase49 Epic Unified CI / Full Django — Run `32577907801` — SUCCESS.

Validated inside CI:
- Runner v49.3I.4 contract.
- Windows PowerShell 5.1 ASCII-only runner.
- live fetched Git snapshot guard.
- Python compile.
- dedicated Explorer thumbnail/view/multi-select/context-menu tests.
- source Product-vs-Group URL routing tests.
- previous 49.3I/3H/3G regressions.
- Django checks.
- `makemigrations --check --dry-run` = no changes.
- migration plan contract.
- no destructive schema operations.
- Windows Catalog Epic49 tests.
- Full Django suite.

## Must-Not-Touch / Preserved Contracts
- Product Workspace detailed editor.
- Phase49.3H AI progress/result/error/cost ledger.
- Phase49.3H image default 10 / hard max 20.
- Preview → Approve → Full Fetch acquisition contract.
- Archive/blocked duplicate guards.
- Fixed / Range / Formula pricing modes.
- Persian editorial content.
- Local/Production publish separation.
- Product/Hero revision/idempotency.
- 49.3I.3 live-fetched GitHub snapshot handoff guard.
- no direct Production source edit.

## Database / Migration / Media Safety
- Django migration for 49.3I.4: `NONE` — CI verified.
- no Django model/schema change.
- no Production DB operation.
- no destructive local Catalog schema operation.
- existing Catalog `settings` table stores Explorer view preference; no schema migration required.
- no historical media rewrite/delete.
- no product delete/block operation in Explorer queue removal.

## Git / Commit State
Branch: `epic/phase49-unified-product-slider-sync`.
CI-validated runtime/docs base: `f792fd01d643a7b3d071234a4237f2d6932679b3`.
Post-validation commits are documentation-only status closure. Windows handoff must still resolve the live fetched Remote Epic HEAD inside the same execution; never use a Chat-pinned SHA as sole truth.

## Windows QA Required Before Local Publish
1. Close Catalog Center.
2. verify clean Windows worktree.
3. `git fetch --prune origin`.
4. `git pull --ff-only origin epic/phase49-unified-product-slider-sync`.
5. run repository-owned `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`.
6. verify Runner `49.3I.4` and `PHASE49_3I_GIT_SNAPSHOT=OK`.
7. Products:
   - full thumbnails, no thin strip,
   - all five Explorer view modes,
   - Ctrl-click / Shift-click,
   - Select All / Clear Selection,
   - right-click context menu,
   - Remove From Publish Queue does not delete product,
   - image click large preview,
   - Edit Product opens Product Workspace.
8. URL routing:
   - one real Product URL → direct intake,
   - one real Group/Category/Search URL → Preview first,
   - Full Fetch only after approval.
9. AI first-paint/progress regression QA.
10. Fixed / Range / Formula pricing regression QA.

## Local Publish Gate
Do NOT perform Local Publish until the Explorer/routing visual/data QA above passes. After owner confirms visual/data QA:
- one `LOCAL PUBLISH ONLY`,
- Local Django E2E,
- verify image/product/pricing/provenance payload.

## Production State
Production is untouched. No production deployment, migration, publish or media operation is approved.

## Remaining Work
1. Windows clean pull of current Epic.
2. run v49.3I.4 local gate with `-LaunchApp`.
3. Explorer gallery visual QA.
4. Product-vs-Group URL routing QA.
5. AI/pricing regression QA.
6. only after those pass: one LOCAL PUBLISH ONLY + Local Django E2E.
7. explicit owner approval.
8. only then Production backup/deploy/verification.

## Exact Next Task
Pull the current Epic on Windows using live GitHub snapshot verification and run `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`. Do not patch source locally and do not touch Production.
