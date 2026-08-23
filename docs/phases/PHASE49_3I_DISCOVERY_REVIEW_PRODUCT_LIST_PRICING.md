# Phase49.3I — Discovery Review + Product Explorer + Pricing + Observable AI

Updated: 2026-08-23
Branch: `epic/phase49-unified-product-slider-sync`
Current Hotfix: `49.3I.15 — Bulk Exact-Page Images + Add-to-Products`
Status: `MERGED / ALL REQUIRED PR CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Goal
Deliver a business-usable Catalog Center that acquires products from exact source listing pages in bulk, stages the requested image count, lets the operator select wanted products, prepares them in Product Workspace and publishes only after verified Local/Production gates.

## Canonical Acquisition Paths
Two paths coexist:

1. Mature compatibility path:
`Top Scan Controls → BaseApp start_scan/_scan_worker → Product Workspace`

2. Primary exact-page business path:
`Exact Search/Listing/Category URL → choose product limit + image limit → discover product links → stage local images → review image counts → Add selected to Products / Archive unwanted → Product Workspace`.

The previous one-thumbnail-only Preview→per-product Direct Full Fetch rule is superseded **for path 2 only**. Exact-page bulk acquisition does not depend on `extract_direct_link`.

## Preserved Contracts
- explicit Search/Listing/Category URL is authoritative,
- source `model_url_pattern` remains Product-vs-Page boundary,
- dedupe by source + external id + normalized URL,
- Archive/Block prevents unwanted rediscovery without destructive deletion,
- Product Workspace remains canonical detailed editor,
- AI/provider/schema/trace/manual-override contracts unchanged,
- image hard max 20,
- Fixed / Range / Formula remain independent,
- mature top scan actions restored in 49.3I.14 stay available,
- Local Publish and Production remain separate gates.

## 49.3I.15 — Bulk Exact-Page Images + Add-to-Products

### Owner Acceptance Change
Exact-page link discovery is verified working, while individual Product/Rich Direct Full Fetch repeatedly blocks operations. The listing-page discovery itself is therefore the business acquisition workflow:
- choose up to 100 products,
- choose up to 20 images per product,
- discover links from the exact page,
- collect public product images with mature Classic browser/image helpers,
- show staged image count before selection,
- selected rows are added directly to Products from staged data,
- unwanted rows are archived/blocked,
- no Product-tile Direct Full Fetch is required.

### Implementation
Added `catalog_center/app/phase49_3i15_bulk_discovery_images.py`:
- `normalize_product_limit()` hard caps at 100,
- candidate image manifests persist under existing Catalog DATA (`discovery_manifests/<source>/<external>.json`),
- image collection reuses `launch_fresh_browser`, `_dom_image_urls`, `_download_context_images`,
- exact-page discovery reuses `discover_preview_candidates`,
- each candidate continues independently on failure,
- Stop is respected between candidates,
- UI adds product/image selectors and image-count column,
- `اضافه کردن انتخاب‌شده‌ها به محصولات` creates review-state Product rows from staged identity/title/images without network Full Fetch,
- existing/blocked dedupe and history remain.

Added `catalog_center/app/phase49_3i15_staging_guard.py` to fail closed when image URLs are visible but no local image download succeeds. At least one staged local image is required before readiness/Add-to-Products.

Runtime composition installs 49.3I.15 and its staging guard after 49.3I.13/14 in `phase49_3i12_runtime_bridge.py`.

Added:
- `RUN_PHASE49_3I15_BULK_GATE.ps1`, chaining `RUN_PHASE49_3I14_HOTFIX_GATE.ps1`,
- `.github/workflows/phase49-3i15-bulk-discovery-images-ci.yml`,
- focused bulk and staging-guard tests.

## GitHub Validation / Merge
PR `#61` merged.
- final PR head `5f96d890b2e31e1f1d670c8afb716a1da4fc88d3`,
- merge commit `953f975e883e6dfcbf61097ac8d324d68d4ca678`.

Final-head workflows SUCCESS:
- Phase49.3I.15 Bulk Discovery Images `32641815323`,
- Phase49.3I `32641815273`,
- Phase49.3I.14 Legacy Scan Restore `32641815287`,
- Phase49.3H `32641815289`,
- Phase49.3G `32641815380`,
- Full Phase49 + Windows Catalog regressions + Full Django `32641815270`.

Repository root `manage.py` was explicitly verified; the Django CI step is valid. Staging guard behavior is also CI-covered.

## Database / Media / Secret Safety
- Django migration: `NONE`,
- Catalog candidate schema migration: `NONE`,
- staging files are additive under existing persistent Catalog DATA,
- no reset/drop/truncate,
- no existing media/history deletion,
- no secret/credential change,
- Production untouched.

## Focused Windows Acceptance — Current Gate
1. close Catalog Center and require clean Local worktree,
2. live fetch/prune + ff-only pull current Epic remote HEAD,
3. run `RUN_PHASE49_3I15_BULK_GATE.ps1 -LaunchApp`,
4. use exact MakerWorld Search URL and first test `10 products × 10 images`,
5. verify live progress and per-candidate staged image count,
6. select 2–3 ready rows → `اضافه کردن انتخاب‌شده‌ها به محصولات`,
7. verify no Rich Direct/per-product Full Fetch action is invoked,
8. Archive one unwanted row,
9. open one added Product and verify staged images in Product Workspace.

If PASS, operational batches may use 30/50/100 products and 10/20 images.

## Release / Production Gate
Immediately after Windows PASS: exactly one `LOCAL PUBLISH ONLY` → Local Django Store/Admin/Product/Media/SEO E2E → explicit owner approval → read-only Production path/branch/venv/MySQL/backup/rollback verification → GitHub-only deploy → HTTP/data/media verification.

## Next Phase
Normal Store checkout: ZarinPal request/callback/verify + Sandbox E2E while bank transfer remains available.
