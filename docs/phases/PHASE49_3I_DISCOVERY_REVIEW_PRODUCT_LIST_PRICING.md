# Phase49.3I — Discovery Review + Product Gallery + Explicit Pricing Modes

Updated: 2026-08-22
Branch: `epic/phase49-unified-product-slider-sync`
Current Hotfix: `49.3I.4`
Status: `IMPLEMENTED ON GITHUB / FINAL CI PENDING / WINDOWS QA PENDING`
Production: `UNTOUCHED`

## Goal
Phase49.3I makes Catalog Center safe and efficient for high-volume product discovery/review while keeping Product Workspace as the canonical detailed editor.

The phase now owns:
1. exact operator-supplied Search/Listing URL handling,
2. Preview Candidate → Approve → Full Fetch,
3. archive/not-needed + blocked identity dedupe,
4. source-script sanitation,
5. lightweight Products gallery and Product Workspace routing,
6. explicit Fixed / Range / Formula pricing modes,
7. immediate AI progress first paint,
8. deterministic GitHub→Windows snapshot handoff,
9. Windows-Explorer-style product browsing,
10. source-aware Product URL vs Group/Category/Search URL routing.

## Requested Delta
### A. Discovery Preview First
- Operator supplies an exact HTTP(S) Search/Listing/Category URL.
- Explicit valid seed is authoritative.
- Discovery opens only the listing/group surface and collects lightweight candidates.
- Preview candidate stores only source identity, title and one thumbnail.
- Product page full extraction is forbidden before operator approval.

### B. Approval Before Full Fetch
- Operator can select one or many preview candidates.
- Only approved candidates are fully extracted.
- Canonical image limit remains default 10 / hard max 20.
- Full fetch preserves source identity and sanitized source data.

### C. Archive / Not Needed / Dedupe
- Archive before full fetch creates only minimal blocked identity.
- Blocked source identity must not reappear as a new candidate.
- Existing curated product must never be silently blocked merely because discovery saw it again.
- Duplicate protection remains source code + external id + normalized URL.

### D. Source Text Safety
- URLs and source identity are preserved.
- English/Latin technical source text is preserved.
- Persian editorial `_fa` fields are preserved.
- Unexpected CJK/Cyrillic/emoji source garbage is removed from scraped text fields.

### E. Product Gallery
Base 49.3I gallery contract remains:
- legacy detailed Products editor/Treeview remains alive only as compatibility backend,
- operator surface shows product image + product name + Edit Product only,
- click image opens large local preview,
- Edit Product opens canonical Product Workspace,
- thumbnail source is local only: strict mapping → `page_extract.json` → local `images/`,
- no network fetch occurs during Products gallery thumbnail rendering.

### F. Phase49.3I.4 Explorer Gallery Hotfix
Owner local QA exposed `ERR-49-020` where real images were clipped to a thin strip.

Corrected contract:
- thumbnail PhotoImage is rendered inside a pixel-sized holder frame,
- holder uses `pack_propagate(False)`,
- child image Label fills the holder and has no text-unit width/height,
- view size changes also regenerate the PhotoImage for the requested pixel dimensions.

Explorer-style view modes:
- Extra Large Icons,
- Large Icons — default,
- Medium Icons,
- Small Icons,
- List.

The chosen view is stored in existing local Catalog `settings`; no schema migration is introduced.

Selection behavior:
- normal click → single selection,
- Ctrl-click → toggle item,
- Shift-click → contiguous range,
- Select All,
- Clear Selection,
- selected-count display,
- selected cards receive a visual border.

Right-click context menu:
- Open Product,
- Image Preview,
- Remove From Publish Queue,
- Select All,
- Clear Selection.

`Remove From Publish Queue` safety contract:
- applies to the selected local products,
- sets `upload_ready=0`,
- sets `workflow_status=review`,
- does not delete product data,
- does not block the product,
- does not call Production,
- does not unpublish/delete an already-live site record.

### G. Product URL vs Group/Category/Search URL Routing
Owner local QA requested verification of direct-link versus group intake and exposed `ERR-49-021`.

49.3I.4 routing contract:
- every configured source with non-empty `model_url_pattern` uses that product regex as its authoritative single-product boundary,
- matching URL → mature direct single-product intake,
- other valid HTTP(S) URL → Preview Candidate discovery first,
- no Full Fetch for a non-product URL before review,
- source without a product regex preserves mature fallback routing.

For MakerWorld, a model URL such as:
`https://makerworld.com/en/models/2834255-cake-stand-small-table-great-for-cakes-cupcakes?from=search#profileId-3158565`
must route as Direct Product.

A Search/Group URL such as:
`https://makerworld.com/en/search/models?keyword=cake+stand`
must route as Preview Candidate discovery.

### H. Explicit Pricing Modes
Three independent operator modes remain:
- Fixed — exact final price,
- Range — explicit minimum/maximum,
- Formula — dynamic cost formula based on material/time/supervision/extras.

Range must never invoke Formula calculations.
No migration-owned Django field choices are mutated at runtime.

### I. AI First Paint
Full AI autofill must paint immediate startup progress before synchronous preflight, then hand off to the mature 49.3H connection/send/receive/result/error/cost UI.

### J. GitHub → Windows Handoff
Runner v49.3I.4 preserves 49.3I.3 live snapshot semantics:
- clean worktree required,
- exact Epic branch required,
- `git fetch --prune origin`,
- Local HEAD must equal fetched Remote Epic HEAD,
- stale Chat-pinned SHA is not authoritative,
- no reset/stash/delete shortcut.

## Runtime Surface
Added:
- `catalog_center/app/phase49_3i_explorer_hotfix.py`
- `catalog_center/tests/test_epic49_phase49_3i_explorer_hotfix.py`

Changed:
- `catalog_center/app/phase49_3i_product_list.py`
- `RUN_PHASE49_3I_LOCAL_GATE.ps1`
- `.github/workflows/phase49-3i-ci.yml`

Preserved mature Phase49.3I runtime:
- `catalog_center/app/phase49_3i_discovery_review.py`
- `catalog_center/app/phase49_3i_source_safety.py`
- `catalog_center/app/phase49_3i_local_qa_hotfix.py`
- `catalog_center/app/phase49_3i_pricing_modes.py`
- `store/phase49_3i_pricing_modes.py`

## Must-Not-Touch
- Product Workspace detailed editing contract.
- Phase49.3H SEO Execution Console.
- Phase49.3H result/error drawer and AI cost ledger.
- default 10 / hard max 20 image policy.
- manual override/provenance behavior.
- dual product/portfolio publish targets.
- product revision + idempotency.
- homepage slider/revision contracts.
- production paths, DB and media.
- historical local media.
- secrets.

## Regression Tests
49.3I.4 dedicated tests must prove:
1. five Explorer view modes exist and default to Large.
2. unknown view mode normalizes safely.
3. MakerWorld product URL matches source product regex.
4. MakerWorld Group/Search URL does not match source product regex.
5. malformed/empty product regex fails closed as non-product.
6. thumbnail image Label has no text-unit width/height.
7. explicit pixel holder and `pack_propagate(False)` exist.
8. Ctrl/Shift multi-selection contract exists.
9. right-click context menu contract exists.
10. queue removal mutates only `upload_ready=0` and `workflow_status=review` and contains no delete/block call.
11. Explorer view persists through existing Catalog settings.
12. direct-link wrapper reads source `model_url_pattern` before selecting Direct vs Preview.
13. Explorer hotfix composes after the mature 49.3I gallery installer.
14. previous 49.3I/3H/3G tests continue to pass.
15. Django `makemigrations --check --dry-run` reports no changes.

## Database / Migration Safety
- Django schema change: NONE.
- Intended Django migration: NONE.
- Catalog local schema change: NONE.
- existing `settings` key-value table stores only view preference.
- no destructive schema operation.
- no media rewrite/delete.

## Error Records
- `ERR-49-020` — Product thumbnails clipped by Tk text-unit Label geometry.
- `ERR-49-021` — Group/category URL could bypass Preview because URL-shape classifier was incomplete.

See `docs/ERRORS.md` for Root Cause / Solution / Prevention.

## Acceptance Gate
Phase49.3I.4 is not complete until all of the following pass:
1. Phase49.3I GitHub CI.
2. Phase49.3H regression CI.
3. Phase49.3G regression CI.
4. Full Phase49 + Full Django CI.
5. Windows clean pull + runner v49.3I.4.
6. visual proof that real images occupy their full thumbnail area.
7. all five Explorer view modes.
8. Ctrl and Shift multi-selection.
9. right-click menu and safe local queue removal.
10. real Direct Product URL routes direct.
11. real Group/Category/Search URL routes Preview first.
12. AI first-paint/progress regression QA.
13. pricing Fixed/Range/Formula regression QA.
14. one LOCAL PUBLISH ONLY + Local Django E2E after visual/data QA.
15. explicit owner acceptance.
16. only then Production backup/deploy/verification.

## Current State
GitHub implementation exists. Final CI probe is pending. Windows has not yet pulled 49.3I.4. Production is untouched.

## Exact Next Step
Finish repository documentation sync, run the CI-only final validation probe, close it without merge on success, then hand the owner a live-snapshot Windows pull + v49.3I.4 local gate. No Production action yet.
