# CURRENT PROJECT STATE

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Branch: `epic/phase49-unified-product-slider-sync`
Active Phase: `49.3I`
Active Hotfix: `49.3I.15 — Bulk Exact-Page Images + Add-to-Products`
Status: `IMPLEMENTED ON PR #61 / TARGETED + PRIOR CI SUCCESS / FULL EPIC CI FINALIZING / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Current Position
Owner changed the business acceptance contract after repeated MakerWorld single-product/approved Full-Fetch failures. The exact Search/Listing page discovery already finds correct candidate links, so the release path must now use that working boundary directly instead of depending on per-candidate Rich Direct Full Fetch.

New operator flow:
`Exact Search/Listing URL → choose product count → choose image count/product → discover links → collect staged images → show image count → select wanted rows → Add to Products / Archive unwanted → Product Workspace → Local Publish E2E`.

The old Preview-one-thumbnail-only rule is superseded for this exact-page bulk operator workflow by explicit owner request. Mature top scan controls restored in 49.3I.14 remain available and untouched.

## Phase49.3I.15 Delta
- product count selector: 10 / 20 / 30 / 50 / 100, hard cap 100,
- image count selector: 5 / 10 / 15 / 20, hard cap 20,
- exact-page link discovery still uses the verified `discover_preview_candidates` path,
- after link discovery, each candidate image set is collected with the mature Classic browser/image helpers (`launch_fresh_browser`, `_dom_image_urls`, `_download_context_images`),
- no `extract_direct_link` / Rich Direct dependency in this bulk flow,
- per-candidate staged metadata persists as JSON under the existing persistent Catalog DATA root; no candidate-table migration,
- candidate list gains image-count visibility,
- primary review action becomes `اضافه کردن انتخاب‌شده‌ها به محصولات`,
- Add-to-Products materializes source identity/title/images into the existing Product row contract without another network Full Fetch,
- Archive/Block and existing-product dedupe remain unchanged,
- Stop is checked between candidates and one candidate failure does not abort the entire batch,
- Product Workspace/AI/pricing/publish/FTP/Bridge/credential behavior is not changed.

## GitHub Validation — PR #61 Feature Head
Feature branch: `agent/phase49-3i15-bulk-discovery-images`.
Implementation head before documentation sync: `a7cb319c2723ae2f9cfe87a1a00c8b33e7fcf619`.

Successful runs already observed:
- Phase49.3I.15 Bulk Discovery Images CI — Run `32641268643` — SUCCESS,
- Phase49.3I Discovery Review Pricing CI — Run `32641268627` — SUCCESS,
- Phase49.3I.14 Legacy Scan Restore CI — Run `32641268644` — SUCCESS,
- Phase49.3H SEO Cost Image Limit CI — Run `32641268659` — SUCCESS,
- Phase49.3G Workspace Usability CI — Run `32641268651` — SUCCESS.

Full Phase49 + Full Django Run `32641268645` was still finishing the full Django suite at this documentation commit; all earlier steps had passed. Do not merge until that run is SUCCESS on the final feature head.

## Database / Migration / Media / Secret Safety
- Django migration: `NONE` in targeted CI,
- Catalog schema migration: `NONE`,
- candidate image staging uses files under existing persistent Catalog DATA,
- no DB reset/drop/truncate,
- no candidate/history/media deletion,
- no credential changes,
- Production untouched.

## Focused Windows Acceptance After Merge
1. close Catalog Center; require clean worktree,
2. live fetch/prune + ff-only pull current Epic,
3. run `RUN_PHASE49_3I15_BULK_GATE.ps1 -LaunchApp`, which chains all prior 49.3I gates,
4. paste exact MakerWorld Search URL such as `https://makerworld.com/en/search/models?keyword=cake+stand`,
5. choose first a small real QA batch: 10 products × 10 images,
6. run `کشف + دریافت تصاویر`; verify visible live progress and per-row image counts,
7. select 2–3 ready rows and use `اضافه کردن انتخاب‌شده‌ها به محصولات`; no per-product Direct Full Fetch may run,
8. Archive one unwanted row and confirm it remains blocked from rediscovery,
9. open one added Product and confirm staged images are available in Product Workspace.

After this focused PASS, increase operational batches to 30/50/100 as needed. No broad unrelated QA is required unless a regression appears.

## Release Gate Immediately After PASS
- exactly one `LOCAL PUBLISH ONLY`,
- Local Django Store/Admin/product/media/SEO verification,
- explicit owner approval,
- read-only Production path/branch/MySQL/backup/rollback verification,
- GitHub-only Production deploy and HTTP/data verification.

## Next Product Phase
After Catalog deploy, implement normal Store ZarinPal request/callback/verify + Sandbox E2E while retaining bank transfer.
