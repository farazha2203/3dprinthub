# CURRENT PROJECT STATE

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Branch: `epic/phase49-unified-product-slider-sync`
Active Phase: `49.3I`
Active Hotfix: `49.3I.15 — Bulk Exact-Page Images + Add-to-Products`
Status: `MERGED TO EPIC / ALL REQUIRED PR CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Current Position
The owner-approved exact-page business flow is now merged into the Epic branch. It deliberately stops using per-candidate Rich Direct Full Fetch as the release path because exact Search/Listing discovery is the verified working boundary and the old per-product extraction path repeatedly blocked operations.

Canonical flow:
`Exact Search/Listing URL → choose product count → choose image count/product → discover links → stage local images → show image count → select wanted rows → Add to Products / Archive unwanted → Product Workspace → Local Publish E2E`.

The previous one-thumbnail Preview→per-product Full Fetch contract is superseded for this exact-page bulk workflow only. Mature compatibility controls restored in 49.3I.14 remain available.

## Phase49.3I.15 Runtime Contract
- product selector: 10 / 20 / 30 / 50 / 100, hard max 100,
- image selector: 5 / 10 / 15 / 20, hard max 20,
- exact page discovery reuses `discover_preview_candidates`,
- image acquisition reuses mature Classic browser/image helpers,
- bulk path has no `extract_direct_link` / Rich Direct Full Fetch dependency,
- per-candidate staged metadata is JSON under existing persistent Catalog DATA,
- candidate list exposes staged image count,
- selected rows use `اضافه کردن انتخاب‌شده‌ها به محصولات`,
- Add-to-Products materializes review-state Product rows from staged identity/title/images without another network Full Fetch,
- Archive/Block and source/external-id/normalized-URL dedupe remain,
- one candidate failure does not abort the rest; Stop is checked between candidates,
- Local staging guard requires at least one successfully downloaded local image before candidate readiness/Add-to-Products,
- Product Workspace/AI/pricing/publish/FTP/Bridge/credentials are unchanged.

## GitHub / CI Validation
PR `#61` merged successfully into the Epic branch.
- final PR head: `5f96d890b2e31e1f1d670c8afb716a1da4fc88d3`,
- merge commit: `953f975e883e6dfcbf61097ac8d324d68d4ca678`.

Final-head required workflows all SUCCESS:
- Phase49.3I.15 Bulk Discovery Images CI — `32641815323`,
- Phase49.3I Discovery Review Pricing CI — `32641815273`,
- Phase49.3I.14 Legacy Scan Restore CI — `32641815287`,
- Phase49.3H SEO Cost Image Limit CI — `32641815289`,
- Phase49.3G Workspace Usability CI — `32641815380`,
- Phase49 Epic Unified CI including Windows Catalog regressions + Full Django suite — `32641815270`.

Review follow-up verification:
- repository root `manage.py` exists, so the Django CI step using root working directory is valid,
- local staging guard fail-closes when image URLs exist but no image was actually downloaded.

## Database / Migration / Media / Secret Safety
- Django migration: `NONE`,
- Catalog candidate schema migration: `NONE`,
- staging files are additive under existing persistent Catalog DATA,
- no DB reset/drop/truncate,
- no existing candidate/history/media deletion,
- no credential changes,
- Production untouched.

## Exact Next Task — Windows Focused Acceptance
1. close Catalog Center and require clean Local worktree,
2. live fetch/prune + ff-only pull the current Epic remote HEAD; no Chat-pinned SHA,
3. run `RUN_PHASE49_3I15_BULK_GATE.ps1 -LaunchApp`, which chains prior Phase49.3I gates,
4. paste exact MakerWorld Search URL such as `https://makerworld.com/en/search/models?keyword=cake+stand`,
5. first QA batch: `10 products × 10 images`,
6. run `کشف + دریافت تصاویر`; verify visible progress and per-row staged image counts,
7. select 2–3 ready rows → `اضافه کردن انتخاب‌شده‌ها به محصولات`; no per-product Direct Full Fetch may start,
8. Archive one unwanted row and verify it stays blocked from rediscovery,
9. open one added Product and verify staged images in Product Workspace.

If this focused QA passes, operational batches may increase to 30/50/100 products and 10/20 images.

## Release Gate After Windows PASS
- exactly one `LOCAL PUBLISH ONLY`,
- Local Django Store/Admin/Product/Media/SEO E2E,
- explicit owner approval,
- read-only Production path/branch/venv/MySQL/backup/rollback verification,
- deploy the approved GitHub snapshot only,
- Production HTTP/data/media verification,
- final docs update.

## Next Product Phase
After Catalog Production verification: normal Store ZarinPal request/callback/verify + Sandbox E2E while retaining bank transfer.
