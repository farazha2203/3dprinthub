# CURRENT PROJECT STATE

Updated: 2026-08-22
Repository: `farazha2203/3dprinthub`
Branch: `epic/phase49-unified-product-slider-sync`
Active Phase: `49.3I`
Active Hotfix: `49.3I.5 — Selection Loop Guard + Compact Product Metadata`
Status: `GITHUB UPDATED / FINAL CI SUCCESS / WINDOWS RERUN PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Current Position
Windows successfully pulled and executed Phase49.3I.4 at local HEAD `7330ad6d79d8061998b1fa143051173b558cefbd`.

The repository-owned Windows gate passed end-to-end:
- 137 Catalog Center tests PASS,
- 419 Django tests PASS, 2 skipped,
- `makemigrations --check --dry-run` reports no changes,
- no planned migration operations,
- Production untouched.

Manual QA then proved the 49.3I.4 Explorer image/view correction visually, but exposed a new interaction regression: selecting/opening a product could freeze the UI as if it entered a loop. The owner also requested that the Explorer cards restore useful compact operational metadata and friendly sorting/filtering instead of being image/name-only.

Phase49.3I.5 fixes that regression and is final-CI validated. Windows has not yet pulled/tested 49.3I.5.

## Owner-Reported Windows QA — 49.3I.4
### Passed visually
- product thumbnail geometry/view rendering is corrected,
- Explorer-style display modes are usable.

### Failed interaction
- selecting/opening a product could freeze/hang before Product Workspace became usable.

### Additional operator requirement
The Products surface should remain lightweight, but cards must show useful detail:
- local Product ID,
- workflow/product state,
- source,
- image count,
- added date,
- publish state.

Explorer controls should expose human-readable Persian choices including:
- آماده انتشار,
- صف انتشار,
- منتشرشده,
- جدیدترین,
- قدیمی‌ترین,
- آخرین بروزرسانی.

Product Workspace remains the canonical detailed editor; parameter-heavy forms do not return to the Products surface.

## Verified Root Cause
### ERR-49-022 — Hidden Treeview selection feedback loop
The mature hidden Treeview has:
`<<TreeviewSelect>> -> load_product`.

49.3I.4 card selection called `_phase49_3i_select_product()`, which called `product_tree.selection_set(iid)`. The compatibility `load_product()` then called `_phase49_3i_select_product()` again, producing this feedback cycle:

`Explorer card -> selection_set -> <<TreeviewSelect>> -> load_product -> selection_set -> ...`

This matched the observed freeze.

## Phase49.3I.5 Implemented Delta
### Selection / open stability
- card → hidden Treeview selection sync is one-way and re-entrancy guarded,
- `selection_set()` runs only when the hidden selection actually differs,
- hidden Treeview `load_product()` updates current/card state only and never writes selection back,
- product open has a repeat-click guard,
- Tk gets an idle/layout paint opportunity before constructing Product Workspace,
- dedicated regression test uses a fake Treeview that immediately fires the selection callback from `selection_set()` and proves only one selection write occurs.

### Compact Explorer metadata
Each product card remains lightweight but now shows:
- `#Product ID`,
- Persian product/workflow state,
- source,
- image count,
- added date,
- publish state.

Detailed commercial/editorial/SEO/pricing fields remain in Product Workspace.

### Friendly Explorer filter / sort
Filter choices:
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

Sort choices:
- اولویت کاری,
- جدیدترین,
- قدیمی‌ترین,
- آخرین بروزرسانی,
- بیشترین امتیاز,
- بیشترین دانلود.

The old raw English filter/sort bar is hidden from the operator surface. Existing DB/filter semantics are reused; no schema migration is introduced.

## Preserved 49.3I.4 Explorer Contracts
- Extra Large / Large / Medium / Small / List views,
- persistent view preference,
- normal/Ctrl/Shift selection,
- Select All / Clear Selection,
- right-click Open / Preview / Remove From Publish Queue,
- safe queue removal only: `upload_ready=0`, `workflow_status=review`,
- no product delete/block/unpublish from Explorer,
- local-only thumbnail resolution,
- Product URL vs Group/Category/Search URL routing by source `model_url_pattern`,
- Preview-first for non-product URLs.

## Final GitHub Validation — 49.3I.5
CI-only PR: `#50`
State: `CLOSED / NOT MERGED`
Validated Epic runtime base: `cdaac6680ea8545f52ece15ecaa3ce0a575eabe9`
CI marker head: `57813f47f649bb2c415aa0fae1481f4a2561ce1d` — not merged.

Successful workflows:
- Phase49.3I Discovery Review Pricing CI — Run `32580222694` — SUCCESS.
- Phase49.3H SEO Cost Image Limit CI — Run `32580222686` — SUCCESS.
- Phase49.3G Workspace Usability CI — Run `32580222682` — SUCCESS.
- Phase49 Epic Unified CI / Full Django — Run `32580222683` — SUCCESS.

Validated inside CI:
- Runner v49.3I.5 ASCII-only Windows PowerShell 5.1 contract,
- live fetched Git snapshot guard,
- Python compile,
- fake-Treeview selection feedback-loop regression test,
- product open guard contract,
- compact card metadata contract,
- Persian filter/sort option contract,
- Explorer thumbnail/view/multi-select/context-menu regressions,
- Product-vs-Group URL routing regressions,
- Phase49.3H/3G regressions,
- Django checks,
- `makemigrations --check --dry-run` = no changes,
- no destructive schema operations,
- Full Django suite.

## Runtime Files Changed
- `catalog_center/app/phase49_3i_explorer_hotfix.py`
- `catalog_center/tests/test_epic49_phase49_3i_explorer_hotfix.py`
- `RUN_PHASE49_3I_LOCAL_GATE.ps1` — v49.3I.5
- `.github/workflows/phase49-3i-ci.yml`

## Database / Migration / Media Safety
- Django migration for 49.3I.5: `NONE` — CI verified.
- Catalog schema change: `NONE`.
- no DB reset/drop/truncate.
- no historical data rewrite.
- no media rewrite/delete.
- no Production DB/media/source operation.

## Error Knowledge Base
New record:
- `ERR-49-022` — hidden Treeview selection feedback loop.

Existing relevant records remain:
- `ERR-49-017` real UX87 composition boundary,
- `ERR-49-018` AI progress first-paint,
- `ERR-49-019` stale Chat SHA handoff,
- `ERR-49-020` clipped thumbnail receiver,
- `ERR-49-021` Product-vs-Group URL routing.

## Must-Not-Touch / Preserved Contracts
- Product Workspace detailed editor.
- Phase49.3H AI progress/result/error/cost ledger.
- image default 10 / hard max 20.
- Preview → Approve → Full Fetch.
- archive/blocked duplicate guards.
- Fixed / Range / Formula pricing independence.
- Persian editorial content.
- Local/Production publish separation.
- product/hero revision and idempotency.
- no direct Production source edit.

## Windows QA Required Before Local Publish
1. close Catalog Center.
2. verify clean worktree.
3. fetch/prune and fast-forward-only pull current Epic.
4. run repository-owned `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`.
5. verify Runner `49.3I.5` and `PHASE49_3I_GIT_SNAPSHOT=OK`.
6. select a product; UI must stay responsive.
7. click Edit Product; exactly one Product Workspace opens for one action.
8. close it and open via right-click → Open Product; no freeze/loop.
9. card shows ID/state/source/image count/added date/publish state.
10. verify filters: Ready / Publish Queue / Published.
11. verify sorts: Newest / Oldest / Last Updated.
12. verify Explorer view modes, Ctrl/Shift selection and right-click queue action still work.
13. verify one Product URL routes direct and one Group/Search URL routes Preview first.
14. AI first-paint/progress regression QA.
15. Fixed / Range / Formula pricing regression QA.

## Local Publish Gate
Do NOT perform Local Publish until the 49.3I.5 interaction/metadata QA above passes. After owner confirms:
- one `LOCAL PUBLISH ONLY`,
- Local Django E2E,
- verify image/product/pricing/provenance payload.

## Production State
Production is untouched. No Production deploy, migration, publish or media operation is approved.

## Remaining Work
1. Windows pull current Epic.
2. run v49.3I.5 local gate with `-LaunchApp`.
3. selection/open responsiveness QA.
4. compact metadata/filter/sort QA.
5. remaining Explorer/routing/AI/pricing regression QA.
6. only after QA passes: one LOCAL PUBLISH ONLY + Local Django E2E.
7. explicit owner approval.
8. only then Production backup/deploy/verification.

## Exact Next Task
Windows: clean worktree → live fetch/prune → fast-forward-only pull current Epic → run repository-owned Phase49.3I.5 gate with `-LaunchApp` → verify selection/open no longer loops and compact metadata/filter/sort are correct. Do not patch source locally and do not touch Production.
