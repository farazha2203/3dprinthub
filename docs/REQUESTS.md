# OWNER REQUESTS

Last Updated: 2026-08-26

Older detailed request history remains available in Git history. This file keeps active acceptance contracts.

## Preserved project contracts
- GitHub-first delivery; live branch/HEAD verification before Host operations.
- Product/SEO/media/Bridge security/idempotency and Product-owned public media remain intact.
- imported Catalog working-media is not a public Production namespace.
- healthy StoreOrder/Payment/Invoice/inventory/coupon/VAT behavior is extended rather than duplicated.
- no guessed carrier/gateway endpoint or tariff.

## REQ-50-001 — Complete business finance/accounting system
Status: `REQUESTED / PHASE50 ACTIVE`
Full GL/subledger, Treasury, Purchasing/Sales accounting, customer/supplier statements and management reports integrated with Store/service/inventory/production/payments.

## REQ-50-002 — Complete and reorganize Django Admin
Status: `PRODUCTION VERIFIED / VISUAL QA CONTINUES`
Professional Velzon operator console with business navigation, full-width lists, on-demand filters, Persian controls, stable footer, no document jump and approximately 290px readable right sidebar.

## REQ-50-003 — Preserve healthy commerce while adding accounting
Status: `ACTIVE CONSTRAINT`
StoreOrder, StorePayment, invoices, inventory, coupon/VAT, Product/Profile/Variant history and payment security remain compatible.

## REQ-50-004 — Dynamic delivery price
Status: `50.A.2B GITHUB CI TESTED / PRODUCTION MIGRATION NEXT`
Shipping calculation must use the chosen profile/product effective shipping weight, packaging weight/dimensions and destination. Current ShippingMethod/rate rules remain the explicit fallback. Post/Tipax/Mahex adapters are allowed only after verified official current contracts/credentials.

## REQ-50-005 — Coupon + VAT checkout
Status: `PRESERVED / INCLUDED IN 50.A.2B REGRESSION BOUNDARY`
Do not duplicate current Coupon/VAT logic; shipping snapshot finalization must preserve discount, packaging, tax and payment totals.

## REQ-50-006 — Phishing-resistant comprehensive payment
Status: `REQUESTED / 50.A.3 PLANNED`
Server-owned amount, DB locking, callback identity, exact Authority, server-to-server verification and idempotency; never collect/store card/PIN/CVV.

## REQ-50-008 — Variant 2.0 size/build/packaging parity
Status: `PRODUCTION VERIFIED FOUNDATION`
`store.0034` and `store.0035` are applied; customer selector uses canonical ProductVariant state.

## REQ-50-009 — Torob marketplace integration
Status: `REQUESTED / 50.A.4 PLANNED`
Official Product API v3 with stable Product/Profile grouping, price/availability and image-quality rules.

## REQ-50-010 — ZarinPal Store checkout activation
Status: `REQUESTED / 50.A.3 PLANNED`
Connect StorePayment to mature secure payment architecture before merchant activation.

## REQ-50-014 — Windows Product image pixel dimensions
Status: `SOURCE IMPLEMENTED / CI TESTED / NEXT EXE VERSION AFTER SMOKE`
Each Product image card shows original width × height px.

## REQ-50-018 — Unified Product Admin workspace
Status: `PRODUCTION VERIFIED / VISUAL QA CONTINUES`
Product edit business order remains: `اطلاعات کالا | تصاویر | فروش و موجودی | پروفایل‌ها و سایز/وزن | قیمت‌گذاری | ارسال و بسته‌بندی | SEO | اسلایدر صفحه اول | منبع و لایسنس | همگام‌سازی ویندوز`.

## REQ-50-019 — Modern Velzon Admin interaction surface
Status: `PRODUCTION VERIFIED / VISUAL QA CONTINUES`
Full-width list, on-demand filter drawer, modern table/search/actions, section navigation, stable footer and internal-only sidebar scrolling.

## REQ-50-020 — Product likes, saved/favorites, comments and verified-buyer reviews
Status: `REQUESTED / NEXT SCHEMA-BUSINESS PACKAGE AFTER 50.A.2B`
Preserve ProductLike/ProductComment/ProductReview. Add Favorite/Save if absent, engagement counters/Admin visibility and qualifying purchased/paid Product checks for buyer feedback. Dedicated migration/tests/backup required.

## REQ-50-021 — Customer Product profile/size/weight/color/price selector
Status: `PRODUCTION VERIFIED`
Customer Product view obeys list/size/weight/build/size→build/build→size selection, exposes available profile dimensions and price/facts, keeps canonical ProductVariant ID and native fallback, and reuses `/store/api/variant-commerce-options/`.

## REQ-50-022 — Immutable selected-profile checkout and shipping snapshot
Status: `IMPLEMENTED / GITHUB CI TESTED / PRODUCTION MIGRATION NEXT`
Acceptance:
- finalized order item freezes profile name/key/label and the customer-visible selection mode/value,
- finalized order item freezes size/build/material/color/quality, final weight, packaging weight, effective shipping weight, print time and package dimensions,
- Cart/checkout effective weight includes packaging when there is no explicit shipping-weight override,
- order freezes `insured_value` and normalized `shipping_quote_snapshot`,
- ShippingMethod/rate rules remain current fallback and quote source is explicit; no external carrier claim,
- do not invent combined parcel geometry from multiple units/items; preserve per-line package facts and require final packing,
- coupon/VAT/inventory/payment/notification behavior remains mature and authoritative,
- snapshot stays unchanged after later ProductVariant edits,
- migration `store.0036_phase50_checkout_snapshot` requires exact Production MySQL verification, fresh backup and rollback before apply.

CI: `Phase50 Variant2 Gallery CI` run `32966720475` PASS on `fba0631e60bce1f6e3f622317b70c2f7f35d978f`.

## Change rule
New work extends/wraps mature behavior and must pass CI/Local gate before Production. No schema migration reaches Production without exact MySQL verification, migration plan, successful backup and rollback target. Production uses explicit live branch fetch to `FETCH_HEAD` because host remote-tracking refspec is stale/tag-only. Avoid `/dev/fd` process substitution on this cPanel host.
