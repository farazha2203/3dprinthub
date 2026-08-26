# PROJECT CHANGELOG

Record meaningful changes only. Older detailed entries remain available in Git history.

## 2026-08-26 — Phase50.A.2B Immutable Checkout/Profile/Shipping Snapshot — GitHub CI Tested
- added migration `store.0036_phase50_checkout_snapshot`,
- StoreOrderItem now has immutable sales-profile name/key/label, selection mode/value, final weight, effective shipping weight and print-time snapshots,
- existing `0034` StoreOrderItem size/build/packaging-weight/package-dimension fields are now populated during successful checkout finalization,
- StoreOrder now has `insured_value` and normalized `shipping_quote_snapshot`,
- added `store/phase50_checkout_snapshot.py` following the existing additive runtime-field pattern rather than rewriting mature `store/models.py`,
- Cart summary now uses `ProductVariant.effective_shipping_weight_grams`, including packaging when no explicit shipping-weight override exists,
- mature Phase6 checkout remains authoritative for form validation, coupon, inventory reservation, address, notifications, payment creation and redirect,
- successful checkout is wrapped in an outer atomic boundary and finalized before commit; finalizer failure restores the session cart and rolls back DB writes,
- normalized shipping snapshot uses current `ShippingMethod`/rate rules as explicit `shipping_method_fallback`; no external carrier API is claimed,
- insured value is frozen as merchandise value after order discount,
- per-line/unit package dimensions are preserved; combined carton geometry is deliberately not invented,
- pending StorePayment amount is synchronized if effective shipping weight changes the final fallback shipping fee,
- added integration regressions proving profile/package/weight snapshotting, packaging-aware shipping weight, payment synchronization and immutability after later Variant changes,
- GitHub Actions `Phase50 Variant2 Gallery CI` run `32966720475` PASS on snapshot `fba0631e60bce1f6e3f622317b70c2f7f35d978f`, including compile, Django check, migration drift/plan, SQLite migration through `0036`, Variant2/gallery/profile-selector tests and checkout snapshot tests,
- Production remains at `c283864290f9c989a9fcdf24ee8eef519560e917`; `0036` is not yet applied and requires a fresh Production backup/migration gate.

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
- owner reported Admin footer flash, whole-page menu jump and narrow 250px sidebar,
- added normal-flow footer/stable shell, 290px sidebar and internal-only sidebar scrolling,
- added customer sales-profile selector using existing ProductVariant/API/cart contracts,
- Admin CI `32958276378` PASS on `27335832e90c35dd95bb8a686dd89d1efd46dc8f`,
- Storefront CI `32958296546` PASS on `e3c57311c0c3980befeaf6012f3bb8fc502333bc`.

## 2026-08-26 — Phase50.A.1G Velzon Operator Surface V2
- replaced permanent legacy Django filter column with on-demand drawer and full-width lists,
- added Persian modern table/search/action/form surfaces while preserving Django Admin semantics,
- CI `32955310832` PASS on `3687d0922959fca53f2118be6dacd32639159346`.

## 2026-08-26 — Phase50.A.1F Business Admin Navigation / Product Admin 500 Fix — Production Verified
- fixed Product changelist 500 caused by SafeString numeric formatting,
- reorganized Admin by business domains,
- deployed/verified at `bc7b97f9c63432b8105f52f61cf5cdae1369689b` with backup `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-125848`.

## 2026-08-26 — Phase50.A.1E Production Deployment Verified
- deployed `9cfbc54ed4196144864b5f4201976d8466a88134`,
- backup `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-114327`,
- `0034`/`0035` applied and HTTP/private-media gates PASS,
- stale remote-tracking incident fixed through explicit `FETCH_HEAD` (`ERR-50-007`).

## 2026-08-26 — Phase50.A.1E Unified Product Admin Workspace
- added business-ordered Product workspace preserving mature Product/Profile/Variant/SEO contracts,
- CI `32941662288` PASS on `f34eaa3bbad965b2092279291ff8adf93f3d908e`.

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
