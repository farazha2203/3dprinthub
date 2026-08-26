# PROJECT CHANGELOG

Record meaningful changes only. Older detailed entries remain available in Git history.

## 2026-08-26 — Phase50.A.1E Production Deployment Verified

### Deployment
- deployed active branch application snapshot `9cfbc54ed4196144864b5f4201976d8466a88134` to Production,
- Phase50.A.1E runtime remained the CI-tested code from snapshot `f34eaa3bbad965b2092279291ff8adf93f3d908e`; later commits through deployed HEAD were documentation/archive-only,
- fresh rollback backup created at `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-114327`,
- rollback source HEAD recorded as `8fbe3413cada1099745f4d17312b8eb519694379`,
- MySQL backup/source backup verification passed before source deployment.

### Production gates
- Production root/branch/worktree gate PASS,
- MySQL vendor/name gate PASS for `sfkilvrs_EmiAdmin_3dprinthub`,
- `store.0034_phase50_variant2_commerce` applied,
- `store.0035_phase50_sales_profiles` applied,
- post-deploy migration plan empty,
- no new migration executed,
- Django check PASS with known warnings only,
- migration drift NONE,
- unified Product Admin runtime section/inlines gate PASS,
- collectstatic PASS,
- Passenger restart completed,
- Home/Store/Admin login HTTP 200,
- public Homepage private imported-media references = 0,
- final Production worktree clean.

### Resolved deployment incident
- first deployment attempt stopped safely before source mutation because `git fetch --prune origin` did not advance the active branch remote-tracking ref,
- host `remote.origin.fetch` was configured only for tag `v0.33.0`; active branch had no upstream,
- corrected path explicitly fetched `refs/heads/agent/phase49-3i18-operator-bulk-ai-rebuild` to `FETCH_HEAD`, verified SHA/ancestry and used ff-only merge,
- incident recorded as `ERR-50-007`.

### Next
- owner manual QA of unified Product Admin + Hero Studio images,
- then Phase50.A.2 profile-aware storefront selector, checkout profile snapshots and shipping/delivery contract.

## 2026-08-26 — Phase50.A.1E Unified Product Admin Workspace

### Requested delta
Owner requested one professional Product Admin page organized exactly as:
`اطلاعات کالا | تصاویر | فروش و موجودی | پروفایل‌ها و سایز/وزن | قیمت‌گذاری | ارسال و بسته‌بندی | SEO | اسلایدر صفحه اول | منبع و لایسنس | همگام‌سازی ویندوز`.

### Implemented
- added `store/phase50_product_admin_workspace.py` as the final additive Product Admin composition boundary,
- kept mature Product, ProductCatalogProfile, ProductVariant and SEO models authoritative instead of copying state,
- reorganized Product edit fieldsets in the requested business order,
- preserved Product gallery and Variant/Profile inlines and relabeled them for operator clarity,
- added read-only operator control blocks linking to gallery, sales profiles, pricing, shipping/package data, Hero Studio, commercial license and Windows sync,
- SEO block exposes the real Product focus keyword/meta/canonical/robots/OpenGraph/schema fields plus existing SERP preview,
- pricing/slider/license/sync summaries read from the existing ProductCatalogProfile,
- shipping summary reads existing Variant 2.0 product/package/shipping weight and parcel dimensions,
- no new schema migration; workspace builds on `0034` and `0035`.

### Verification
- first CI run `32941533091` failed only a stale regression assertion about `seo_status`,
- working mature Admin behavior was preserved and the test was corrected,
- corrected `Phase50 Product Admin Workspace CI` run `32941662288` PASS on snapshot `f34eaa3bbad965b2092279291ff8adf93f3d908e`,
- compile PASS, Django check PASS with known warnings only, migration drift NONE, SQLite migrations through `store.0035` PASS, focused Product Admin regressions PASS.

## 2026-08-25 — Phase50.A.1C Admin Media Integrity / Mobile Hero / Homepage SEO / Windows Image Dimensions
- added safe ImportedPrintAsset Admin media resolver using Product-owned public media,
- preserved mature Phase35 editing/actions,
- compacted mobile Hero presentation,
- added homepage SEO health/preview audit,
- Windows image cards show original pixel dimensions,
- corrected CI run `32875771848` PASS.

## 2026-08-25 — Phase50.A.1B Product Gallery + Variant 2.0 Foundation
- upgraded Product gallery to contain-fit viewer + thumbnail switch + fullscreen lightbox,
- added Variant 2.0 size/build/material/color/quality/weight/package dimensions,
- added StoreOrderItem commerce snapshots,
- added migration `store.0034_phase50_variant2_commerce`,
- CI run `32872549545` PASS.

## 2026-08-25 — Catalog Center Windows v8.8.1 Final Portable Release
- released `3DPrintHub-CatalogCenter-v8.8.1.exe`, build `2026.08.25.2`,
- SHA256 `c32f37affcbd2c6ffacb803247daf804a490fecd7c8162bc37c2729a2197e990`,
- 92 regression tests, launcher verification, PyInstaller build, frozen self-verification, browser smoke and release publication PASS.

## 2026-08-25 — Phase50.A.1 Admin Storefront / Hero Parity
- Product/imported-asset Hero add/remove actions,
- 5/10 random Hero and deactivate-all,
- command-center Storefront/Checkout links,
- Coupon/Shipping/Pricing/address surfaces,
- CI PASS.

## 2026-08-25 — Phase50.A Admin Command Center
- added authenticated `/admin/command-center/`,
- organized Sales, Treasury, Accounting/Ledgers, Purchasing and Inventory/Production,
- added permission-aware links and live counters,
- no schema migration.

## 2026-08-25 — Phase49.3I.30 Production Hero Product-Media Ownership
- fixed Production Hero blank images by resolving imported selection to Product-owned public gallery/main media,
- imported working-media remained private,
- no migration.

## 2026-08-25 — Phase49.3I.29 Production Deployment Verified
- owner-approved Phase49 application deployed,
- MySQL verified and backup created,
- migrations/collectstatic/Passenger restart completed,
- Home/Store/Product HTTP checks returned 200,
- final Production worktree clean.

## 2026-08-25 — Phase49.3I.29 Structured Web Product Presentation
- replaced raw technical JSON-like output with customer-readable Product sections.

## 2026-08-25 — Phase49.3I.28 Exact-Link Canonical Title Call Contract
- fixed duplicate `current_title` binding while preserving mature source identity.

## 2026-08-25 — Phase49.3I.27 Exact-Link Category Provider Crash Fix
- bridged mature `App.get_all_categories()` provider into exact-link completion.

## 2026-08-25 — Phase49.3I.26 Unified Exact-Link Completion
- restored canonical Product stages, observable AI, vertical gallery and bulk archive/delete workflow.
