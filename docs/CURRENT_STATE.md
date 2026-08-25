# CURRENT PROJECT STATE

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Release: `Phase50.A.1D — Sales Profiles + Hero Admin Public Media`
Status: `GITHUB CI TESTED / PRODUCTION DEPLOY REQUIRED`

## Production verified state
Owner deployment on 2026-08-25 succeeded at application commit `5c5c5e1e141fd3ff8df3c079abc55e4593feb41f`.
Production MySQL is `sfkilvrs_EmiAdmin_3dprinthub`; `store.0034_phase50_variant2_commerce` is applied; final migration plan had no pending operations; Home/Store/Admin/Product Admin/Imported Asset Admin/Hero Admin all returned HTTP 200; public Home contained no `/media/store/imported-models/` references. Rollback backup: `/home/sfkilvrs/3dprinthub-deploy-backups/20260825-205719`.

Known warnings remain CKEditor4 maintenance/security debt, `store.W026` in-memory realtime debt, and MySQL conditional-constraint warnings from third-party/account models. A prior `Too many connections` event was transient; later audit showed 26/151 total MySQL connections and only 3 for the application DB user.

## Windows Catalog Center
Latest immutable Windows release remains `8.8.1` (`BUILD_ID=2026.08.25.2`), GitHub Release `catalog-center-v8.8.1`, SHA256 `c32f37affcbd2c6ffacb803247daf804a490fecd7c8162bc37c2729a2197e990`.
Source after 8.8.1 additionally shows original image dimensions; that source delta is not yet in a newer released EXE.

## Phase50.A.1D implemented on GitHub
### Sales Profiles
- Product-level profile selection mode: full list, size, weight, build, size→build, build→size.
- optional Product selector label.
- ProductVariant sales profile name, stable profile key, display order and default flag.
- profile identity extends Variant uniqueness so otherwise-identical material/color/size/build rows can coexist when profile keys differ; this supports different weight/time/price profiles.
- Admin action `کپی پروفایل‌های فروش انتخاب‌شده` clones mature Variant settings and generates a new profile/code while leaving the source unchanged.
- Product Admin and Variant inline expose profile settings alongside size/build/material/color/weight/print-time/price/stock fields.
- Variant metadata endpoint now exposes profile label/key/default/order, selection mode, weight, print time, unit price and shipping/package data.
- migration `store.0035_phase50_sales_profiles` owns the new schema and is NOT deployed to Production yet.

### Hero Admin media integrity
Owner evidence showed `/admin/website/homepageheroslide/<id>/change/` loading product/album cards whose images failed because the legacy Hero Studio JSON endpoints emitted private `store/imported-models/...` working-media URLs.

Implemented final Admin endpoint boundary:
- Product browser thumbnails resolve Product-owned public media first.
- Album rows resolve matching Product gallery images; if no public match exists, row-specific HTTP(S) source media may be used instead of exposing private working-media.
- private imported Catalog paths are never returned by the replacement Hero Admin JSON endpoints.
- existing Hero selection IDs, SEO suggestions, cinematic controls and public Hero rendering remain unchanged.

## Verification
GitHub Actions `Phase50 Sales Profiles Hero Admin CI` run `32879712980` PASS on snapshot `405d2c1daa85828d1a0dc68210d201c85b6db7ba`:
- touched Python compile PASS,
- Django system check PASS,
- migration dry-run PASS,
- migration plan PASS,
- SQLite migration apply PASS,
- Sales Profile/Admin/Hero public-media regressions PASS.

## Exact next work
1. Read-only Production verify current HEAD/worktree/MySQL and confirm `0034` remains applied.
2. Fresh MySQL backup, deploy current approved GitHub snapshot, inspect/apply only `store.0035`, collectstatic and Passenger restart.
3. Manual QA: Hero Studio product cards/gallery images, Product profile copy/edit/default/order and selection mode.
4. Extend storefront selector UI to consume the new profile metadata and persist selected profile snapshots in checkout.
5. Continue Phase50.A.2 Shipping/Delivery, then secure Store ZarinPal, Torob Product API v3, then Phase50.B accounting core.
