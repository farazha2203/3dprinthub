# Phase49.3I — Discovery Review + Product Gallery + Explicit Pricing Modes

Updated: 2026-08-22
Branch: `epic/phase49-unified-product-slider-sync`
Current Hotfix: `49.3I.5`
Status: `FINAL CI SUCCESS / WINDOWS RERUN PENDING`
Production: `UNTOUCHED`

## Goal
Phase49.3I makes Catalog Center safe and efficient for high-volume discovery/review while Product Workspace remains the canonical detailed editor.

The phase owns:
1. exact operator Search/Listing URL handling,
2. Preview Candidate → Approve → Full Fetch,
3. archive/not-needed + blocked identity dedupe,
4. source-script sanitation,
5. visual Products Explorer + Product Workspace routing,
6. explicit Fixed / Range / Formula pricing,
7. immediate AI first paint,
8. deterministic GitHub→Windows snapshot handoff,
9. Explorer-style product browsing,
10. Product URL vs Group/Category/Search URL routing,
11. stable selection/open interaction and compact operational card metadata.

## A. Discovery Preview First
- explicit valid HTTP(S) Search/Listing/Category seed is authoritative,
- Preview only stores lightweight identity/title/thumbnail,
- full product extraction is forbidden before approval.

## B. Approval Before Full Fetch
- one or many candidates may be approved,
- Full Fetch only approved candidates,
- image default 10 / hard max 20,
- source identity and sanitized source payload preserved.

## C. Archive / Not Needed / Dedupe
- archive before Full Fetch creates minimal blocked identity,
- blocked identity does not reappear,
- existing curated product is not silently blocked,
- duplicate boundary is source code + external id + normalized URL.

## D. Source Text Safety
- preserve URLs/source identity,
- preserve English/Latin technical source text,
- preserve Persian editorial `_fa` fields,
- remove unexpected scraped CJK/Cyrillic/emoji garbage.

## E. Products Explorer Contract
The Products surface is visual/lightweight, not a parameter-heavy editor.

Per card:
- product image,
- product name,
- compact operator metadata:
  - Product ID,
  - product/workflow state,
  - source,
  - image count,
  - added date,
  - publish state,
- one Edit Product action.

Detailed editorial, SEO, material, pricing, commercial and publish editing stays in Product Workspace.

Image click opens large local preview.
Thumbnail source remains local-only:
`strict local mapping → page_extract.json → local images/`.

## F. Explorer Visual / Selection Features — 49.3I.4 Preserved
View modes:
- Extra Large,
- Large — default,
- Medium,
- Small,
- List.

View preference is stored in existing local Catalog settings; no schema migration.

Selection:
- normal click single,
- Ctrl-click toggle,
- Shift-click contiguous range,
- Select All,
- Clear Selection,
- selected count,
- selected-card border.

Right-click:
- Open Product,
- Image Preview,
- Remove From Publish Queue,
- Select All,
- Clear Selection.

Safe queue removal only sets:
- `upload_ready=0`,
- `workflow_status=review`.

It does not delete/block/unpublish a product and never touches Production.

## G. Product URL vs Group/Category/Search Routing — 49.3I.4 Preserved
For a configured source with non-empty `model_url_pattern`:
- matching Product URL → mature direct single-product intake,
- valid HTTP(S) non-product URL → Preview Candidate first,
- Full Fetch only after approval,
- no product regex → preserve mature fallback behavior.

MakerWorld Product example:
`https://makerworld.com/en/models/2834255-cake-stand-small-table-great-for-cakes-cupcakes?from=search#profileId-3158565`

MakerWorld Search example:
`https://makerworld.com/en/search/models?keyword=cake+stand`

## H. Explicit Pricing Modes
Independent operator modes:
- Fixed,
- Range,
- Formula/Dynamic.

Range never invokes Formula.
No runtime mutation of migration-owned Django field choices.

## I. AI First Paint
Full AI autofill paints immediate progress before synchronous preflight, then hands off to the mature 49.3H connection/send/receive/result/error/cost UI.

## J. GitHub → Windows Handoff
Runner v49.3I.5 preserves the live snapshot contract:
- clean worktree,
- exact Epic branch,
- `git fetch --prune origin`,
- Local HEAD equals fetched Remote Epic HEAD,
- stale Chat SHA is not authoritative,
- no reset/stash/delete shortcut,
- ASCII-only PowerShell 5.1 runner.

## K. Phase49.3I.5 — Selection Loop Guard
### Windows incident
49.3I.4 automated local gate passed and Explorer visual rendering was corrected, but manual QA found selecting/opening a product could freeze.

### Root cause — ERR-49-022
The hidden mature Treeview is bound:
`<<TreeviewSelect>> -> load_product`.

The Explorer card used `_phase49_3i_select_product() -> tree.selection_set(iid)`. The 49.3I compatibility `load_product()` called `_phase49_3i_select_product()` again, which wrote selection again, forming:

`card -> selection_set -> TreeviewSelect -> load_product -> selection_set -> ...`

### Corrected interaction contract
- card → hidden Treeview is the event-producing direction,
- re-entrancy guard blocks recursive callback handling,
- `selection_set()` only when selection actually differs,
- Treeview `load_product()` is state-only and never writes selection,
- repeated Product Open clicks are guarded,
- Tk receives an idle/layout paint opportunity before Product Workspace construction.

### Regression test
A fake Treeview immediately invokes `load_product()` from `selection_set()` and raises if multiple writes occur. Expected/validated selection write count is exactly one.

## L. Phase49.3I.5 — Friendly Filter / Sort + Compact Metadata
Persian filters:
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

Persian sorting:
- اولویت کاری,
- جدیدترین,
- قدیمی‌ترین,
- آخرین بروزرسانی,
- بیشترین امتیاز,
- بیشترین دانلود.

The raw legacy filter/sort UI is hidden, while mature DB/filter semantics remain the backend.

## Runtime Surface
Changed for 49.3I.5:
- `catalog_center/app/phase49_3i_explorer_hotfix.py`,
- `catalog_center/tests/test_epic49_phase49_3i_explorer_hotfix.py`,
- `RUN_PHASE49_3I_LOCAL_GATE.ps1`,
- `.github/workflows/phase49-3i-ci.yml`.

Preserved mature runtime:
- `catalog_center/app/phase49_3i_discovery_review.py`,
- `catalog_center/app/phase49_3i_source_safety.py`,
- `catalog_center/app/phase49_3i_product_list.py`,
- `catalog_center/app/phase49_3i_local_qa_hotfix.py`,
- `catalog_center/app/phase49_3i_pricing_modes.py`,
- `store/phase49_3i_pricing_modes.py`.

## Must-Not-Touch
- Product Workspace detailed editing,
- 49.3H SEO execution/result/error/cost,
- image default 10 / hard max 20,
- manual override/provenance,
- dual product/portfolio targets,
- product/hero revision/idempotency,
- Production path/DB/media/source,
- historical media,
- secrets.

## Database / Migration Safety
- Django schema change: NONE,
- Django migration: NONE — CI verified,
- Catalog local schema change: NONE,
- no destructive schema operation,
- no media rewrite/delete.

## Error Records
- `ERR-49-017` — wrong UX87 composition boundary,
- `ERR-49-018` — AI progress after synchronous preflight,
- `ERR-49-019` — stale Chat SHA handoff,
- `ERR-49-020` — clipped thumbnail receiver,
- `ERR-49-021` — Product-vs-Group URL routing,
- `ERR-49-022` — hidden Treeview selection feedback loop.

## Final GitHub Validation — 49.3I.5
CI-only PR `#50`: `CLOSED / NOT MERGED`.
Validated Epic runtime base: `cdaac6680ea8545f52ece15ecaa3ce0a575eabe9`.
Marker head: `57813f47f649bb2c415aa0fae1481f4a2561ce1d` — not merged.

Successful runs:
- Phase49.3I `32580222694` — SUCCESS,
- Phase49.3H `32580222686` — SUCCESS,
- Phase49.3G `32580222682` — SUCCESS,
- Full Phase49 + Full Django `32580222683` — SUCCESS.

CI verified:
1. runner 49.3I.5 + ASCII-only + live Git snapshot contract,
2. fake-Treeview feedback-loop regression,
3. product open guard/Tk yield contract,
4. compact metadata contract,
5. friendly filter/sort contract,
6. Explorer view/image/multi-select/context-menu regressions,
7. Product-vs-Group source routing,
8. 49.3H/3G regressions,
9. Django no-new-migration contract,
10. no destructive schema operation,
11. Full Django suite.

## Windows Acceptance Gate Still Pending
49.3I.5 is not owner-accepted until Windows proves:
1. clean pull + runner 49.3I.5,
2. selecting one product never freezes,
3. Edit Product opens exactly one Workspace,
4. right-click Open Product opens exactly one Workspace,
5. compact card metadata is useful/readable,
6. Ready / Publish Queue / Published filters work,
7. Newest / Oldest / Last Updated sorts work,
8. Explorer view modes and Ctrl/Shift selection still work,
9. safe queue removal still works,
10. Product URL direct vs Group/Search Preview routing still works,
11. AI first-paint/progress regression passes,
12. Fixed/Range/Formula regression passes,
13. only after all above: one LOCAL PUBLISH ONLY + Local Django E2E,
14. explicit owner acceptance,
15. only then Production backup/deploy/verify.

## Current State
GitHub final CI for 49.3I.5 is successful. Windows has not yet pulled/tested 49.3I.5. Production is untouched.

## Exact Next Step
Windows clean worktree → live fetch/prune → fast-forward-only pull current Epic → repository-owned v49.3I.5 gate with `-LaunchApp` → selection/open + compact metadata/filter/sort manual QA. No local source patch and no Production action.
