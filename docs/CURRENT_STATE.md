# CURRENT PROJECT STATE

Updated: 2026-08-22
Repository: `farazha2203/3dprinthub`
Branch: `epic/phase49-unified-product-slider-sync`
Active Phase: `49.3I`
Active Hotfix: `49.3I.4 — Explorer Product Gallery + Source URL Routing`
Status: `GITHUB IMPLEMENTED / CI PENDING / WINDOWS RERUN PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Current Position
The owner completed Windows local QA far enough to expose two additional operator-facing regressions in the Products/Discovery surfaces. The previous 49.3I.3 Git snapshot handoff guard remains valid and must not regress.

The new 49.3I.4 implementation is now present on the Epic branch. It has not yet passed the final CI probe and has not yet been pulled/tested on the owner's Windows machine. Production remains prohibited.

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

## Phase49.3I.4 Requested Delta
### Explorer-style Products surface
- Preserve the mature hidden Treeview/filter/sort backend.
- Preserve the lightweight gallery content contract: image + product name + Edit Product only.
- Render thumbnails in pixel-sized holder frames; image Labels carry no text-unit width/height.
- Add persistent view modes stored in the existing local Catalog settings table:
  - Extra Large Icons,
  - Large Icons,
  - Medium Icons,
  - Small Icons,
  - List.
- Add Windows-like multi-selection:
  - normal click = single selection,
  - Ctrl-click = toggle selection,
  - Shift-click = range selection,
  - Select All / Clear Selection controls.
- Right-click context menu:
  - Open Product,
  - Image Preview,
  - Remove From Publish Queue,
  - Select All,
  - Clear Selection.
- Right-click `Remove From Publish Queue` reuses the mature local semantics only:
  - `upload_ready=0`,
  - `workflow_status=review`.
- It does NOT delete a product, does NOT block a product and does NOT unpublish/delete anything on Production.
- Normal image click still opens the large local preview.

### Source-aware URL routing
For a configured source with a non-empty `model_url_pattern`:
- URL matches the source product regex → direct single-product intake.
- valid HTTP(S) URL does not match the product regex → Preview Candidate discovery first.
- sources without a product regex preserve the mature prior fallback behavior.

## Runtime Files Added/Changed
- `catalog_center/app/phase49_3i_explorer_hotfix.py` — new additive Explorer/routing hotfix.
- `catalog_center/app/phase49_3i_product_list.py` — composes the Explorer hotfix after the mature 49.3I gallery installer.
- `catalog_center/tests/test_epic49_phase49_3i_explorer_hotfix.py` — new regression coverage.
- `RUN_PHASE49_3I_LOCAL_GATE.ps1` — bumped to v49.3I.4 and includes Explorer regression coverage.
- `.github/workflows/phase49-3i-ci.yml` — compiles/tests 49.3I.4 and enforces runner contract.

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
- Django migration for 49.3I.4: `NONE` intended and must be verified by CI and Windows local gate.
- No Django model/schema change.
- No production DB operation.
- No local Catalog destructive schema operation.
- Existing Catalog `settings` table stores the chosen Explorer view mode; no schema migration required.
- No historical media rewrite/delete.
- No product delete/block operation in Explorer queue removal.

## Error Knowledge Base
New resolved-code / acceptance-pending records:
- `ERR-49-020` — image receiver clipping from Tk text-unit dimensions.
- `ERR-49-021` — group/category URL misclassified by incomplete URL-shape enumeration.

Previous critical records remain active prevention rules:
- `ERR-49-013` exact search URL ignored,
- `ERR-49-014` full extraction before review,
- `ERR-49-015` phantom pricing migration,
- `ERR-49-016` PowerShell 5.1 runner encoding,
- `ERR-49-017` wrong UX composition boundary,
- `ERR-49-018` AI progress first-paint gap,
- `ERR-49-019` stale Chat-pinned SHA.

## Git / Commit State
Branch: `epic/phase49-unified-product-slider-sync`
Latest runtime/CI implementation commit before this state-doc update: `95e321ba213287362674adf743702015187ceadb`.
Documentation synchronization is in progress; use a live fetched `origin/epic/phase49-unified-product-slider-sync` snapshot for Windows handoff, never a Chat-pinned SHA.

## Tests Required Before Acceptance
1. Phase49.3I dedicated GitHub CI.
2. Phase49.3H regression CI.
3. Phase49.3G regression CI.
4. Full Phase49 + Full Django CI.
5. `makemigrations --check --dry-run` = no changes.
6. Windows runner v49.3I.4 with `PHASE49_3I_GIT_SNAPSHOT=OK`.
7. Windows visual QA:
   - thumbnails show full image area, no thin strip,
   - switch all five view modes,
   - Ctrl/Shift multi-select,
   - right-click actions,
   - remove selected items from local publish queue without deleting products.
8. URL routing QA:
   - one real source Product URL → direct intake,
   - one real source Group/Category/Search URL → Preview first,
   - approved candidate only → Full Fetch.
9. AI first-paint/progress regression QA.
10. Fixed / Range / Formula pricing QA.
11. one `LOCAL PUBLISH ONLY` + Local Django E2E only after the visual/data QA above.

## Production State
Production is untouched. No production deployment, migration, publish or media operation is approved in 49.3I.4 at this time.

## Remaining Work
1. Finish repository documentation sync for 49.3I.4.
2. Run final GitHub CI probe and inspect every required workflow.
3. If CI passes, close the probe without merge.
4. On Windows: clean worktree → fetch/prune → `pull --ff-only` current Epic → run repository-owned v49.3I.4 gate with `-LaunchApp`.
5. Perform Explorer gallery + URL routing manual QA.
6. Only after manual QA: one LOCAL PUBLISH ONLY + Local Django E2E.
7. Obtain explicit owner approval.
8. Only then prepare Production backup/deploy/verification plan.

## Exact Next Task
Complete 49.3I.4 GitHub CI/docs closure. Do not issue Production commands and do not ask the owner to patch local source manually.
