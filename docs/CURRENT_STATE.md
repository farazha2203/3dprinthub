# CURRENT PROJECT STATE

Updated: 2026-08-26
Repository: `farazha2203/3dprinthub`
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Release: `Phase50.A.1E — Unified Product Admin Workspace`
Status: `GITHUB CI TESTED / PRODUCTION DEPLOY REQUIRED`

## Production verified state
Production baseline remains the owner-verified Phase50.A.1C deployment at application commit `5c5c5e1e141fd3ff8df3c079abc55e4593feb41f`.
Production MySQL is `sfkilvrs_EmiAdmin_3dprinthub`; `store.0034_phase50_variant2_commerce` is applied; Home/Store/Admin/Product Admin/Imported Asset Admin/Hero Admin were HTTP 200; rollback backup exists at `/home/sfkilvrs/3dprinthub-deploy-backups/20260825-205719`.

Known warnings remain CKEditor4 maintenance/security debt, `store.W026` in-memory realtime debt, and MySQL conditional-constraint warnings. A prior `Too many connections` event was transient; later audit showed 26/151 total MySQL connections and only 3 for the application DB user.

## Windows Catalog Center
Latest immutable Windows release remains `8.8.1` (`BUILD_ID=2026.08.25.2`), GitHub Release `catalog-center-v8.8.1`, SHA256 `c32f37affcbd2c6ffacb803247daf804a490fecd7c8162bc37c2729a2197e990`.
Source after 8.8.1 additionally shows original image dimensions; that source delta is not yet in a newer released EXE.

## Phase50.A.1D — Sales Profiles + Hero Admin Public Media
Implemented and CI-tested on GitHub:
- Product-level profile selection mode: list / size / weight / build / size→build / build→size,
- ProductVariant profile name/key/default/order,
- copy-profile Admin action,
- Hero Studio Product/album media resolver that avoids private `store/imported-models/...` URLs,
- migration `store.0035_phase50_sales_profiles`.

`store.0035` is still not recorded as Production-applied in the repository state and must pass the normal MySQL/backup/migration gate before deployment.

## Phase50.A.1E — Unified Product Admin Workspace
Implemented as the final Product Admin composition boundary without replacing mature models or creating a new schema migration.

The Product change page is now organized in this exact business order:
1. اطلاعات کالا
2. تصاویر
3. فروش و موجودی
4. پروفایل‌ها و سایز/وزن
5. قیمت‌گذاری
6. ارسال و بسته‌بندی
7. SEO
8. اسلایدر صفحه اول
9. منبع و لایسنس
10. همگام‌سازی ویندوز
11. آمار و وضعیت

Behavior:
- core Product fields stay on the Product model,
- Product gallery and ProductVariant inlines are preserved and relabeled professionally,
- sales profile selection and copy/edit remain on the mature Variant/Profile contract,
- pricing section links to the existing Product Catalog Profile instead of duplicating pricing state,
- shipping section summarizes profile-level product/package/shipping weight and parcel dimensions,
- SEO section exposes the real Product meta/canonical/robots/OpenGraph/schema fields and existing SERP preview,
- Hero section links to Catalog slider settings and Hero Studio,
- source/license section combines Product source fields with Catalog commercial-license status,
- Windows sync section surfaces Desktop ID, revision, last modified source and last sync from Product Catalog Profile.

No new migration is introduced by 50.A.1E; it builds on existing `0034` and pending/approved `0035` schema.

## Verification
GitHub Actions `Phase50 Product Admin Workspace CI` run `32941662288` PASS on snapshot `f34eaa3bbad965b2092279291ff8adf93f3d908e`:
- Python compile PASS,
- Django system check PASS with known warnings only,
- `makemigrations --check --dry-run` => no drift,
- CI SQLite migrations through `store.0035` PASS,
- unified Product Admin regression suite PASS.

The first workspace CI run `32941533091` failed only because the regression test incorrectly assumed the final mature Product list still contained `seo_status`; actual mature list fields were preserved and the test was corrected rather than changing working Admin behavior.

## Exact next work
1. Host read-only verify exact Production HEAD/worktree/MySQL and actual `0035` state.
2. Fresh backup; deploy approved GitHub snapshot; inspect/apply only `store.0035` if pending; collectstatic; Passenger restart.
3. Manual Admin QA of the unified Product page and Hero Studio images.
4. Build storefront profile-aware selector and persist selected profile snapshots in checkout.
5. Continue Phase50.A.2 Shipping/Delivery → secure Store ZarinPal → Torob Product API v3 → accounting core.
