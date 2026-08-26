# PROJECT CHANGELOG

Record meaningful changes only. Older detailed entries remain available in Git history.

## 2026-08-26 — Phase50.A.1H + Phase50.A.2A Production Verified
- Production fast-forwarded from `0f7f22fdcef4b8e288e0530bfe74f5b2411599dc` to `c283864290f9c989a9fcdf24ee8eef519560e917` using explicit verified branch fetch to `FETCH_HEAD` because the Host refspec still tracks only tag `v0.33.0`,
- fresh rollback backup created at `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-143650`, containing tracked source archive + SHA256, copied `.env*` files, MySQL dump + SHA256 and deploy metadata,
- MySQL `sfkilvrs_EmiAdmin_3dprinthub` verified; `store.0034_phase50_variant2_commerce` and `store.0035_phase50_sales_profiles` applied; migration plan empty; no migration executed,
- deployed Admin shell stability: normal-flow footer, stable shell, 290px right sidebar, internal-only active-menu scrolling,
- deployed Storefront sales-profile selector using existing Product/ProductVariant/API/cart contracts,
- `collectstatic` deployed `phase50-admin-shell-stability.css`, `phase50-profile-selector.css` and `phase50-profile-selector.js`,
- Home/Store/Admin/Product/new static resources HTTP 200,
- Product HTML selector contract PASS and native `variant-select` fallback preserved,
- Variant commerce API parsed and verified for Product ID 1 / Variant ID 1 (`selection_mode=size_build`, profile `استاندارد`, build `standard`, material `PLA`, unit price `2131170`),
- public Home private imported-media refs = 0,
- final Production worktree clean at `c283864...`.

### Deployment-verifier incidents
- first recovery attempt stopped before mutation because cPanel Bash process substitution depended on `/dev/fd`; corrected by enumerating/copying `.env*` files with Python (`ERR-50-010`),
- first post-deploy Variant API verifier passed a JSON file as the Python script, causing JSON `false` to be parsed as Python; corrected with `python - <json-path> <variant-id>` + `json.load` (`ERR-50-011`).

## 2026-08-26 — Phase50.A.1H Admin Shell Stability + Phase50.A.2A Storefront Profile Selector

### Owner QA
- owner confirmed the new on-demand filter/full-width Product table direction but reported a footer line/text flashing or appearing across the Admin viewport during refresh,
- right Admin menu navigation felt like the page jumped,
- 250px sidebar remained too narrow for Persian business labels,
- owner asked to activate the already-designed Product price/color/weight/profile selection experience at the same time.

### Admin root cause / implementation
- Velzon 4.3.0 vendor CSS positions `.footer` absolutely; dynamic Django/SimpleBar initialization can therefore paint the footer across content before final height settles,
- project `master-django.js` used `scrollIntoView({behavior:'smooth'})` for the active menu, which can scroll the document rather than only the sidebar,
- added `static/admin/phase50-admin-shell-stability.css`,
- footer is now normal-flow/static inside a stable flex-column shell,
- right sidebar width increased from 250px to 290px with larger Persian spacing/readability,
- broad shell geometry transitions removed,
- active-menu centering now changes only the internal sidebar/SimpleBar `scrollTop`; document-level `scrollIntoView` removed,
- no schema migration.

### Storefront selector implementation
- existing Product sales-profile modes and ProductVariant metadata remain authoritative,
- added `static/store/css/phase50-profile-selector.css` and `static/store/js/phase50-profile-selector.js`,
- `templates/store/base.html` loads the selector assets,
- Product detail progressively enhances the mature `variant-select` using `/store/api/variant-commerce-options/`,
- supports configured list/size/weight/build/size→build/build→size selection plus available material/color/quality distinctions,
- selected profile summary shows price, profile, size, build, material, color, quality, part/shipping weight, print time and parcel dimensions,
- native select remains available as fallback,
- canonical Variant ID is synchronized back into the existing select/change event, preserving current price/cart/AddToCartForm behavior,
- no schema migration.

### Regression/CI
- Admin shell tests assert static footer flow, 290px sidebar, internal-only active-menu scrolling and absence of `best.scrollIntoView`,
- Product selector tests assert existing variant endpoint/native select integration and selector asset contract,
- Admin CI `Phase50 Product Admin Workspace CI` run `32958276378` PASS on `27335832e90c35dd95bb8a686dd89d1efd46dc8f`,
- Storefront CI `Phase50 Variant2 Gallery CI` run `32958296546` PASS on `e3c57311c0c3980befeaf6012f3bb8fc502333bc`,
- JS syntax, Django checks, migration drift, CI migrations and focused regressions PASS.

## 2026-08-26 — Phase50.A.1G Velzon Operator Surface V2
- owner rejected the permanent legacy Django `#changelist-filter` column and requested a substantially more modern/professional Admin,
- reviewed owner-supplied Velzon Django Corporate `4.3.0` / Bootstrap `5.3.6`,
- reused Velzon design/composition patterns while keeping purchased vendor assets private/gitignored,
- added V2 CSS/JS, full-width changelists, on-demand filter drawer, Persian controls, modern search/actions/results/pagination and sticky change-form section navigation,
- preserved native Django ModelAdmin actions/permissions/filters/query semantics,
- no migration,
- CI run `32955310832` PASS on `3687d0922959fca53f2118be6dacd32639159346`.

## 2026-08-26 — Phase50.A.1F Business Admin Navigation / Product Admin 500 Fix — Production Verified
- fixed Product changelist 500 caused by formatting a SafeString with numeric format code in `estimated_profit_admin`,
- added real-row Product changelist regression,
- reorganized Admin navigation around Store, Orders, Finance, Production, Windows/Catalog, Homepage, Content, Engagement, Support, Affiliate and System groups,
- deployed and verified at `bc7b97f9c63432b8105f52f61cf5cdae1369689b`,
- fresh rollback backup at `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-125848`,
- Product Admin render 200, Velzon business navigation PASS, Home/Store/Admin login 200, private imported-media refs 0, no migration.

## 2026-08-26 — Phase50.A.1E Production Deployment Verified
- deployed application snapshot `9cfbc54ed4196144864b5f4201976d8466a88134`,
- fresh rollback backup `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-114327`,
- MySQL `0034`/`0035` applied, migration plan empty, Django/product/HTTP/private-media gates PASS,
- first stale remote-tracking fetch stopped safely and was corrected through explicit `FETCH_HEAD`; incident `ERR-50-007`.

## 2026-08-26 — Phase50.A.1E Unified Product Admin Workspace
- added business-ordered Product workspace while preserving mature Product/ProductCatalogProfile/ProductVariant/SEO data,
- no new migration,
- corrected CI run `32941662288` PASS on `f34eaa3bbad965b2092279291ff8adf93f3d908e`.

## 2026-08-25 — Phase50.A.1C Admin Media / Mobile / SEO / Windows Dimensions
- safe ImportedPrintAsset Admin public-media resolver, compact mobile Hero, homepage SEO audit and Windows image dimensions; CI PASS.

## 2026-08-25 — Phase50.A.1B Product Gallery + Variant 2.0 Foundation
- Product gallery/lightbox, Variant2 size/build/package fields, StoreOrderItem snapshots, `store.0034`; CI PASS.

## 2026-08-25 — Catalog Center Windows v8.8.1 Final Portable Release
- released `3DPrintHub-CatalogCenter-v8.8.1.exe`, build `2026.08.25.2`, SHA256 `c32f37affcbd2c6ffacb803247daf804a490fecd7c8162bc37c2729a2197e990`.

## 2026-08-25 — Phase50.A.1 Admin Storefront / Hero Parity
- Product/imported-asset Hero controls and Storefront/Coupon/Shipping/Pricing/address Admin surfaces.

## 2026-08-25 — Phase50.A Admin Command Center
- authenticated `/admin/command-center/` organized around Sales, Treasury, Accounting/Ledgers, Purchasing and Inventory/Production.

## 2026-08-25 — Phase49.3I Production closeout
- Product-owned public Hero media, structured web Product presentation and verified Production deploy; imported Catalog working-media remained private.
