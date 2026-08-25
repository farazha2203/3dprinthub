# CURRENT PROJECT STATE

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Base Epic: `epic/phase49-unified-product-slider-sync`
Current Release: `Phase50.A.1C — Admin media integrity + mobile Hero + homepage SEO + Windows image dimensions`
Status: `GITHUB CI TESTED / HOST READ-ONLY AUDIT + MANUAL QA REQUIRED`

## Windows Catalog Center release
Latest released Windows application remains `8.8.1` (`BUILD_ID=2026.08.25.2`), GitHub Release `catalog-center-v8.8.1`, asset `3DPrintHub-CatalogCenter-v8.8.1.exe`, SHA256 `c32f37affcbd2c6ffacb803247daf804a490fecd7c8162bc37c2729a2197e990`.

Phase50.A.1C source now additionally shows each Product image's original pixel dimensions (`W × H px`) on the Windows image card by extending the already-installed Phase49.3H workspace boundary. This has CI regression coverage but requires a future executable version bump/rebuild before it is present in the immutable released EXE.

## Production baseline / discrepancy to verify
Repository documentation previously recorded Production as Phase49 healthy with migrations through `store.0033` and Phase50 undeployed. Owner screenshots on 2026-08-25 now show Phase50-era Admin surfaces on `3dprinthub.ir`, plus `/admin/store/product/` returning HTTP 500. Therefore documentation and actual host state may differ.

Before any new Production deploy/migration, perform a read-only host audit of exact branch/HEAD, tracked worktree, MySQL vendor/name, `store.0034` migration state and migration plan. Do not infer the 500 root cause before that evidence.

Known verified Production paths remain:
- project `/home/sfkilvrs/3dprinthub`,
- venv `/home/sfkilvrs/virtualenv/3dprinthub/3.12`,
- MySQL `sfkilvrs_EmiAdmin_3dprinthub`,
- static `/home/sfkilvrs/public_html/static`, media `/home/sfkilvrs/public_html/media`, private media `/home/sfkilvrs/3dprinthub/private_media`.

## Phase50.A.1B baseline
Already CI tested:
- contain-fit Product main viewer,
- thumbnail-to-main switching + fullscreen lightbox,
- Variant 2.0 size/build profile/packaging weight/parcel dimensions,
- StoreOrderItem snapshot columns,
- `store.0034_phase50_variant2_commerce`,
- Variant Admin and public variant metadata endpoint.

`store.0034` must never be applied to Production without exact MySQL verification, migration plan, fresh successful backup and rollback target.

## Phase50.A.1C implemented
Owner evidence showed three distinct UX/data problems:
1. Imported Catalog/Admin image previews were pointing at `store/imported-models/...` working-media and returning 404 in Production.
2. mobile homepage Hero caption/title occupied too much of the viewport and hid the Product image.
3. imported-model Admin did not surface translated/commercial completeness clearly; homepage SEO controls were hard to audit; Windows image cards did not show pixel dimensions.

Implemented additively:
- `store/phase50_admin_media_integrity.py`: Admin previews never expose imported working-media as public image URLs; they prefer filename-matched Product gallery media, then Product main image, then HTTP(S) source image.
- ImportedPrintAsset changelist preserves all mature Phase35 editable/action contracts while adding safe preview and `4/4` completeness state.
- ImportedPrintAsset image inline adds safe public preview and source `W × H px`; working FileFields remain editable/auditable but are not rendered as public preview URLs.
- mobile Hero override reduces caption/title/buttons and hides description on very narrow phones so the Product image remains visible.
- existing `SiteSetting.meta_title` / `meta_description` are preserved as the homepage SEO source; Admin now adds SEO length health, search-result preview and active-Hero Alt/title audit instead of creating duplicate SEO fields.
- Windows Product image cards show original image pixel dimensions using the final installed workspace thumbnail boundary.
- no new migration was created by Phase50.A.1C.

## Automated verification
`Phase50 Admin Media Mobile CI` first run failed at Django system check because the initial patch replaced the mature ImportedPrintAsset `list_display` while Phase35 still owned `list_display_links/list_editable`. The failed condition was not repeated; the fix preserves the mature list and only inserts new readonly columns.

Second CI run `32875771848` on code snapshot `d74683cd54b18cc0f02c3c117515e1a34bc8ec83` PASS:
- Python compile PASS,
- `manage.py check` PASS,
- migration dry-run PASS,
- CI SQLite migrations PASS,
- Admin media + homepage/mobile regressions PASS,
- Windows image-dimension regression PASS.

Known warnings remain Google credentials intentionally empty in CI, CKEditor4 maintenance/security debt and `store.W026` in-memory realtime debt.

## Browser-console evidence
The reported `jewelry-tree-box-3d-print-01.webp/02.webp` HTTP 404 is a real media-path symptom covered by the safe Admin preview work above. The Chrome message `A listener indicated an asynchronous response...` is not yet attributed to application code; it should only be classified after reproduction with extensions disabled/incognito.

## Exact next work
1. Read-only Production audit to resolve actual host HEAD and whether `store.0034` is pending; inspect the Product Admin 500 based on real migration/runtime state.
2. If audit is safe: fresh DB backup, approved GitHub deploy, `store.0034` migration if pending, collectstatic, Passenger restart and Admin/Home/Product/mobile verification.
3. Rebuild/version the Windows executable only after source-side image-dimension/manual smoke is accepted.
4. Continue Phase50.A.2 Checkout & Delivery, then secure Store ZarinPal, Torob Product API v3, then Phase50.B accounting.
