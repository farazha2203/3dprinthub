# PROJECT CHANGELOG

Record meaningful changes only. Older detailed entries remain available in Git history.

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

### Production status
- no deployment is claimed from screenshots alone; the actual Host HEAD must be read-only verified before this combined no-migration deploy,
- next gate is Host branch/HEAD/worktree/MySQL/static/HTTP audit, then fresh backup + explicit `FETCH_HEAD` ff-only deploy + collectstatic + Passenger restart + visual/data QA.

## 2026-08-26 — Phase50.A.1G Velzon Operator Surface V2

### Owner QA / requested delta
- owner confirmed the `bc7b97f` Product Admin 500 fix and business navigation deployment,
- visual QA showed the legacy Django `#changelist-filter` remained permanently visible, squeezed the Product table and retained old English Filter/Action controls,
- owner re-supplied `master.zip` and requested a substantially more modern/professional Admin comparable to the best project Admin experience rather than another small CSS adjustment.

### Theme review
- reviewed owner-supplied Velzon Django Corporate `4.3.0` / Bootstrap `5.3.6` package,
- reused Velzon design/composition patterns for cards, off-canvas controls, tables/forms and responsive operator UI,
- purchased vendor assets remain private/gitignored under `static/velzon_master/` and are not published to the public GitHub repository,
- project-owned adapter CSS/JS/templates are committed normally.

### Implemented
- added `static/admin/phase50-admin-console-v2.css`,
- added `static/admin/phase50-admin-console-v2.js`,
- loaded V2 assets from `templates/admin/base.html`,
- default changelist is now full-width; the native Django filter node is moved into an on-demand `فیلترها` drawer rather than reserving a permanent column,
- added backdrop, close/Escape, reset filters and active-filter count,
- normalized legacy Filter/Search/Action labels to the Persian operator UI,
- modernized search toolbar, bulk actions, result table and pagination as Velzon card surfaces,
- added sticky result headers, controlled horizontal table scrolling and row hover,
- long change forms gain sticky horizontal section navigation and card fieldsets,
- preserved native Django ModelAdmin actions, permissions, filters, query semantics and business models,
- no migration/schema change.

### Verification
- added static/UI contract regressions to `store/test_phase50_admin_http_regression.py`,
- CI workflow validates the V2 JavaScript with `node --check`,
- GitHub Actions `Phase50 Product Admin Workspace CI` run `32955310832` PASS on runtime snapshot `3687d0922959fca53f2118be6dacd32639159346`.

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
