# Phase50 — Finance, Commerce & Admin Command Center

Updated: 2026-08-26
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Subphase: `50.A.2 Checkout & Delivery`
Status: `50.A.1H + 50.A.2A PRODUCTION_VERIFIED / OWNER VISUAL QA NEXT / 50.A.2B NEXT`

Current Production application commit: `c283864290f9c989a9fcdf24ee8eef519560e917`.
Production MySQL `sfkilvrs_EmiAdmin_3dprinthub` has both `store.0034_phase50_variant2_commerce` and `store.0035_phase50_sales_profiles` applied. Fresh rollback backup: `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-143650`.

## Owner request
Complete storefront/Admin commerce before accounting core. Admin must be a professional operator console. Product management keeps the business sequence:
`اطلاعات کالا | تصاویر | فروش و موجودی | پروفایل‌ها و سایز/وزن | قیمت‌گذاری | ارسال و بسته‌بندی | SEO | اسلایدر صفحه اول | منبع و لایسنس | همگام‌سازی ویندوز`.

Current owner priorities also include visible customer Product selection for price/profile/size/build/weight/color, Product engagement, shipping/VAT/coupon, secure ZarinPal and Torob.

## Preserved foundation
- Product/Catalog/Bridge/Hero public media ownership remains Product-owned; imported Catalog working-media remains private.
- Product, ProductCatalogProfile and ProductVariant remain authoritative.
- StoreOrder/StorePayment/StoreInvoice and mature Coupon/VAT/packaging/shipping calculations remain authoritative.
- StoreAddress + Iran location data remain intact.
- no direct Production source edits.
- purchased/private Velzon vendor assets and fonts remain private/gitignored; public GitHub contains project-owned integration code only.

## Production foundation through 50.A.1G
- Admin command center and Hero controls,
- Product gallery/lightbox,
- Variant2 size/build/weight/package fields and StoreOrderItem snapshots,
- `store.0034` applied,
- Sales Profiles and Hero public-media resolver, `store.0035` applied,
- unified Product business workspace,
- Product changelist 500 fix and business-oriented Admin navigation,
- Velzon V2 full-width changelists, on-demand filter drawer, modern controls and section navigation.

## 50.A.1H — Admin Shell Stability — PRODUCTION VERIFIED
### Owner QA finding
- footer line/text could appear across Admin content during refresh/navigation,
- menu navigation could feel like the whole page jumped,
- 250px sidebar was too narrow for long Persian labels.

### Root cause
- Velzon 4.3.0 absolute `.footer`,
- dynamic Django/SimpleBar layout,
- project active-menu `scrollIntoView({behavior:'smooth'})`,
- Velzon default 250px vertical menu.

### Deployed fix
- `static/admin/phase50-admin-shell-stability.css`,
- footer normal/static flow,
- stable flex/min-height shell,
- sidebar 290px,
- broad geometry transitions disabled,
- active-menu centering uses internal SimpleBar/sidebar `scrollTop` only,
- document `scrollIntoView` removed,
- V2 filter drawer and mature Django Admin behavior preserved,
- no migration.

### Verification
- Admin CI `32958276378` PASS on `27335832e90c35dd95bb8a686dd89d1efd46dc8f`,
- deployed at `c283864290f9c989a9fcdf24ee8eef519560e917`,
- new Admin static HTTP 200,
- Django/migration gates PASS,
- final browser refresh/menu visual acceptance remains owner QA.

## 50.A.2 — Checkout & Delivery — ACTIVE
### 50.A.2A — Storefront Sales Profile Selector — PRODUCTION VERIFIED
Authoritative existing contracts:
- Product `sales_profile_selection_mode` + optional selector label,
- ProductVariant profile key/name/default/order, size, build, material, color, quality, weights, print time, price and package dimensions,
- public `/store/api/variant-commerce-options/`,
- native `variant-select`, existing `store.js`, and `AddToCartForm` Variant ID remain canonical.

Deployed behavior:
- `static/store/css/phase50-profile-selector.css`,
- `static/store/js/phase50-profile-selector.js`,
- assets loaded in `templates/store/base.html`,
- list / size / weight / build / size→build / build→size modes,
- additional material/color/quality dimensions when meaningful,
- selected profile summary for price/profile/size/build/material/color/quality/part weight/shipping weight/print time/package dimensions,
- native select retained as fallback,
- chosen customer combination resolves to canonical ProductVariant ID and dispatches existing change event,
- endpoint failure leaves mature native selection usable,
- no migration.

Verification:
- Storefront CI `32958296546` PASS on `e3c57311c0c3980befeaf6012f3bb8fc502333bc`,
- deployed at `c283864290f9c989a9fcdf24ee8eef519560e917`,
- Product detail HTTP 200,
- selector CSS/JS HTTP 200 and present in Product HTML,
- native fallback present,
- Variant API parsed successfully for Product 1 / Variant 1,
- Home private imported-media refs 0,
- no migration executed.

### 50.A.2B — Checkout immutable profile/shipping snapshot — NEXT
The selector alone does not complete checkout/shipping. Remaining work:
- make selected sales-profile identity/customer-visible choice explicit in final immutable order state where needed while preserving existing Variant2 snapshots,
- effective product + packaging shipping weight,
- parcel dimensions and insured value,
- normalized carrier quote + immutable order snapshot,
- Post/Tipax/Mahex only after verified official API credentials/contracts,
- preserve mature ShippingMethod fallback.

## Product Engagement — OWNER REQUESTED SEPARATE SCHEMA PHASE
Preserve ProductLike/ProductComment/ProductReview. Add real Favorite/Save if absent, Product counters/Admin visibility and qualifying purchased/paid Product verification for buyer-feedback reviews/comments. Dedicated migration/tests/Production backup required.

## 50.A.3 — Secure Store ZarinPal
Reuse server-owned amount/currency, random callback identity, exact Authority, server-to-server verify and idempotency. Trusted redirect-host allowlist; never capture/store card/PIN/CVV.

## 50.A.4 — Torob
Official current Torob Product API v3 using stable Product/profile identifiers, price/availability and image-quality contract.

## Remaining Phase50
- 50.B Accounting core: کل / معین / تفصیلی, fiscal periods, balanced vouchers, immutable posting/reversal.
- 50.C Treasury: bank/cash, receipts/payments, allocations/refunds/reconciliation.
- 50.D Purchasing: suppliers, purchase orders/invoices/receiving/payables/returns.
- 50.E Sales accounting: receivables, payment allocation, tax/discount/shipping, credit notes.
- 50.F Reports/close: GL/subledger, trial balance, aging, cashflow, profitability, VAT/tax, fiscal close.

## Current deployment evidence
- Production HEAD `c283864290f9c989a9fcdf24ee8eef519560e917`, clean worktree,
- fresh backup `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-143650`,
- exact MySQL verified; `0034`/`0035` applied,
- migration drift NONE and plan empty,
- no migration executed,
- collectstatic + Passenger restart completed,
- Home/Store/Admin/Product/new static HTTP 200,
- Product selector HTML/native fallback/API PASS,
- public Home private imported-media refs 0.

Deployment-script incidents now canonical:
- `ERR-50-007`: stale remote-tracking ref; explicit branch fetch to `FETCH_HEAD` required,
- `ERR-50-010`: avoid Bash `/dev/fd` process substitution on this cPanel host,
- `ERR-50-011`: JSON verifier data must be parsed as data via `python -`, never executed as Python source.

## Must not touch
- no direct Production source edit,
- no public exposure of imported working-media,
- no destructive historical order/payment/ledger reset,
- no guessed carrier/gateway endpoint,
- no Production migration without exact DB/plan/backup/rollback verification,
- no purchased/private Velzon/font assets committed to public GitHub.
