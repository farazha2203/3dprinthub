# OWNER REQUESTS

Last Updated: 2026-08-26

Older detailed request history remains available in Git history. This file keeps active acceptance contracts.

## Preserved Phase49 contracts
- GitHub-first delivery; live branch/HEAD verification before Local/Host operations.
- Catalog Product Workspace remains canonical editor.
- exact Search/Listing URL remains authoritative.
- Product AI uses exactly one saved Provider/Model/key path and no hidden AI/model scan on open.
- fixed/range/formula pricing modes remain independent.
- Product/SEO/media/Bridge security and idempotency contracts remain intact.
- imported Catalog working-media is not a Production-public media namespace.

## REQ-REL-002 — Final Windows Catalog Center executable
Status: `8.8.1 RELEASED / SOURCE HAS NEW IMAGE-DIMENSION DELTA`
Released EXE remains `3DPrintHub-CatalogCenter-v8.8.1.exe`; a newer immutable Windows build is required only after pending desktop source changes pass smoke/release gates.

## REQ-50-001 — Complete business finance/accounting system
Status: `REQUESTED / PHASE50 ACTIVE`
Full GL/subledger, Treasury, Purchasing/Sales accounting, customer/supplier statements and management reports integrated with Store/service/inventory/production/payments.

## REQ-50-002 — Complete and reorganize Django Admin
Status: `ACTIVE / ADMIN V2 + SHELL STABILITY CI TESTED`
Admin must be a professional operator console, not legacy Django with cosmetic styling. Business navigation, unified Product workspace and Product 500 fix remain preserved. Current acceptance also requires:
- no permanent Filter column,
- full-width operational tables and on-demand filter drawer,
- Persian controls and modern Velzon cards/forms,
- footer never flashes across content on refresh,
- menu navigation must not scroll/jump the document viewport,
- right operator sidebar approximately 290px with readable Persian labels,
- purchased Velzon vendor assets remain private; only project-owned integration code is committed publicly.

Admin shell stability CI: `Phase50 Product Admin Workspace CI` run `32958276378` PASS on `27335832e90c35dd95bb8a686dd89d1efd46dc8f`.

## REQ-50-003 — Preserve healthy commerce while adding accounting
Status: `ACTIVE CONSTRAINT`
Existing StoreOrder, Quote, Payment, StorePayment, invoices, inventory movements, Product/media/Catalog history and payment idempotency/security remain compatible.

## REQ-50-004 — Dynamic delivery price
Status: `REQUESTED / 50.A.2 ACTIVE`
Shipping from chosen profile/product + packaging weight/dimensions/destination; Post/Tipax/Mahex only with verified current official API credentials/contracts; mature ShippingMethod fallback preserved.

## REQ-50-005 — Coupon + VAT checkout
Status: `BACKEND FOUNDATION PRESENT / ADMIN SURFACED`
Improve presentation/integration rather than duplicate current Coupon/VAT/packaging/shipping calculations.

## REQ-50-006 — Phishing-resistant comprehensive payment
Status: `REQUESTED / 50.A.3 PLANNED`
Reuse server-owned amount, DB locking, callback identity, exact Authority, server-to-server verify and idempotent ledger; never collect/store card/PIN/CVV.

## REQ-50-007 — Professional Product gallery
Status: `DEPLOYED FOUNDATION / OWNER QA CONTINUES`
Thumbnail-to-main contain-fit viewer and accessible fullscreen lightbox.

## REQ-50-008 — Variant 2.0 size/build/packaging parity
Status: `DEPLOYED BACKEND / STOREFRONT SELECTOR CI TESTED`
Multiple sales profiles may vary by size/build/material/color/quality/weight/time/price/package. `store.0034` and `store.0035` are the existing schema foundation. Customer Product page must expose these choices without creating duplicate Variant state.

## REQ-50-009 — Torob marketplace integration
Status: `REQUESTED / 50.A.4 PLANNED`
Current official Torob Product API v3, stable grouping, current price/availability, image-quality rules and verified attribution/webhooks.

## REQ-50-010 — ZarinPal Store checkout activation
Status: `REQUESTED / 50.A.3 PLANNED`
Connect StorePayment to mature secure service-payment architecture before Production merchant activation.

## REQ-50-011 — Imported-model Admin image/data integrity
Status: `PRODUCTION VERIFIED / OWNER QA CONTINUES`
Imported-model Admin/public Hero uses Product-owned public media or safe remote fallback; working-media remains private.

## REQ-50-012 — Mobile Hero product visibility
Status: `DEPLOYED / OWNER QA`
Product image must remain visible with compact responsive title/description/CTA behavior.

## REQ-50-013 — Homepage SEO operator controls
Status: `DEPLOYED ADMIN AUDIT / SOCIAL META ENHANCEMENT OPEN`
Existing SiteSetting SEO state stays canonical.

## REQ-50-014 — Windows Product image pixel dimensions
Status: `SOURCE IMPLEMENTED / CI TESTED / NEXT EXE VERSION AFTER SMOKE`
Each Product image card shows original width × height px.

## REQ-50-015 — Reconcile Production Product Admin 500
Status: `RESOLVED / PRODUCTION VERIFIED`
Real Product changelist renders 200 after `estimated_profit_admin` correction.

## REQ-50-016 — Reusable sales profiles per Product
Status: `BACKEND DEPLOYED / CUSTOMER SELECTOR CI TESTED`
Product can choose selection by full profile list, size, weight, build, size→build or build→size. ProductVariant profile identity/default/order remains authoritative; `store.0035_phase50_sales_profiles` is applied on Production.

## REQ-50-017 — Hero Studio images load on slide edit pages
Status: `PRODUCTION DEPLOYED / OWNER QA CONTINUES`
Never emit private imported working-media paths.

## REQ-50-018 — Unified Product Admin workspace
Status: `PRODUCTION FOUNDATION / VISUAL REFINEMENT ACTIVE`
Product edit keeps exact business order: `اطلاعات کالا | تصاویر | فروش و موجودی | پروفایل‌ها و سایز/وزن | قیمت‌گذاری | ارسال و بسته‌بندی | SEO | اسلایدر صفحه اول | منبع و لایسنس | همگام‌سازی ویندوز`.

## REQ-50-019 — Modern Velzon Admin interaction surface
Status: `GITHUB CI TESTED / PRODUCTION QA REQUIRED`
Full-width list, on-demand filter drawer, modern table/search/actions, section navigation, responsive/dark-mode friendly, native Django permission/action/query semantics preserved.

## REQ-50-020 — Product likes, saved/favorites, comments and verified-buyer reviews
Status: `REQUESTED / SEPARATE SCHEMA-BUSINESS PHASE`
Preserve existing ProductLike/ProductComment/ProductReview. Add Favorite/Save if absent, Product engagement counters/Admin visibility and qualifying-purchase checks for buyer feedback. Dedicated migration/tests/backup required.

## REQ-50-021 — Customer Product profile/size/weight/color/price selector
Status: `IMPLEMENTED / GITHUB CI TESTED / PRODUCTION DEPLOY NEXT`
Customer Product view must make the sales-profile foundation visible and easy to use. Acceptance:
- obey Product selection mode list/size/weight/build/size→build/build→size,
- expose available size/build/weight/material/color/quality choices,
- immediately show selected profile price and operational facts,
- keep canonical ProductVariant ID as the value submitted to the mature cart path,
- keep native select as progressive-enhancement fallback,
- use existing `/store/api/variant-commerce-options/`, Product/ProductVariant fields and current AddToCartForm rather than duplicate state,
- no migration for this presentation release.

Storefront CI: `Phase50 Variant2 Gallery CI` run `32958296546` PASS on `e3c57311c0c3980befeaf6012f3bb8fc502333bc`.

Full immutable profile snapshot/shipping quote completion remains subsequent 50.A.2 work.

## Change rule
New work extends/wraps mature behavior and must pass CI/Local tests before Production deployment. No schema migration reaches Production without exact MySQL verification, migration plan, successful backup and rollback target. Current host deployments must verify Git fetch refspec and use explicit live branch fetch to `FETCH_HEAD` when remote-tracking refs are stale.
