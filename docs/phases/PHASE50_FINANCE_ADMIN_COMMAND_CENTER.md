# Phase50 — Finance, Commerce & Admin Command Center

Updated: 2026-08-26
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Subphase: `50.A.1H Admin Shell Stability + 50.A.2A Storefront Sales Profile Selector`
Status: `GITHUB CI TESTED / HOST READ-ONLY VERIFY NEXT`

Last terminal-verified Production application commit recorded in docs: `bc7b97f9c63432b8105f52f61cf5cdae1369689b`. Owner screenshots subsequently showed newer V2 visuals without a terminal HEAD transcript, so the actual Host HEAD must be re-verified before deployment.

Production MySQL last verified with both `store.0034_phase50_variant2_commerce` and `store.0035_phase50_sales_profiles` applied.

## Owner request
Complete storefront/Admin commerce before accounting core. Admin must be a genuinely professional operator console. Product management keeps the business sequence:
`اطلاعات کالا | تصاویر | فروش و موجودی | پروفایل‌ها و سایز/وزن | قیمت‌گذاری | ارسال و بسته‌بندی | SEO | اسلایدر صفحه اول | منبع و لایسنس | همگام‌سازی ویندوز`.

Current owner priorities also include a visible customer Product selector for price/profile/size/build/weight/color, Product engagement, shipping/VAT/coupon, secure ZarinPal and Torob.

## Preserved foundation
- Product/Catalog/Bridge/Hero public media ownership remains Product-owned; imported Catalog working-media remains private.
- Product, ProductCatalogProfile and ProductVariant remain authoritative.
- StoreOrder/StorePayment/StoreInvoice and mature Coupon/VAT/packaging/shipping calculations remain authoritative.
- StoreAddress + Iran location data remain intact.
- no direct Production source edits.
- purchased/private Velzon vendor assets and fonts remain private/gitignored; public GitHub contains project-owned integration code only.

## Deployed foundation through 50.A.1F
- Admin command center and Hero controls,
- Product gallery/lightbox,
- Variant2 size/build/weight/package fields and StoreOrderItem snapshots,
- `store.0034` applied,
- Sales Profiles and Hero public-media resolver, `store.0035` applied,
- unified Product business workspace,
- Product changelist 500 fix and business-oriented Admin navigation,
- latest terminal-verified backup for that deployment: `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-125848`.

## 50.A.1G — Velzon Operator Surface V2
Owner rejected the permanent legacy Django Filter column. Implemented a full-width changelist, on-demand filter drawer, Persian controls, modern Velzon search/actions/results/pagination, sticky result headers and long-form section navigation.

Initial V2 regression gate: `Phase50 Product Admin Workspace CI` run `32955310832` PASS on snapshot `3687d0922959fca53f2118be6dacd32639159346`.

## 50.A.1H — Admin Shell Stability
### Owner QA finding
- Velzon footer line/text could appear across the visible Admin page during refresh/navigation,
- menu navigation felt like the entire page jumped,
- 250px right sidebar was too narrow for long Persian business labels.

### Root cause
- Velzon 4.3.0 vendor `.footer` uses absolute positioning and assumes stable page height,
- Django Admin/SimpleBar changes layout after initial paint,
- project active-menu code used `scrollIntoView({behavior:'smooth'})`, which could scroll the document instead of only the sidebar,
- Velzon default vertical menu width is 250px.

### Implemented
- `static/admin/phase50-admin-shell-stability.css`,
- footer forced into normal/static document flow,
- main Admin shell uses stable flex/min-height composition,
- sidebar widened to 290px with improved Persian spacing,
- broad shell geometry transitions disabled,
- `master-django.js` now centers an off-screen active link by changing only internal SimpleBar/sidebar `scrollTop`,
- `scrollIntoView` removed from active-menu handling,
- V2 filter drawer and mature Django Admin behavior preserved,
- no migration.

### Verification
`Phase50 Product Admin Workspace CI` run `32958276378` PASS on snapshot `27335832e90c35dd95bb8a686dd89d1efd46dc8f`:
- Python compile PASS,
- Admin JavaScript syntax PASS,
- Django check PASS,
- migration drift NONE,
- CI SQLite migrations PASS,
- Product/representative Admin regressions PASS.

Incident knowledge is recorded as `ERR-50-009`.

## 50.A.2 — Checkout & Delivery — ACTIVE
### 50.A.2A — Storefront Sales Profile Selector
The schema/backend was already present; this subphase surfaces it for customers without a migration.

Authoritative existing contracts:
- Product `sales_profile_selection_mode` + optional selector label,
- ProductVariant profile key/name/default/order, size, build, material, color, quality, weights, print time, price and package dimensions,
- public `/store/api/variant-commerce-options/`,
- native `variant-select`, existing `store.js`, and `AddToCartForm` Variant ID remain the canonical cart boundary.

Implemented:
- `static/store/css/phase50-profile-selector.css`,
- `static/store/js/phase50-profile-selector.js`,
- assets loaded in `templates/store/base.html`,
- modern choice controls respect list / size / weight / build / size→build / build→size Product mode,
- additional material/color/quality dimensions appear when meaningful,
- selected profile summary updates price, profile, size, build, material, color, quality, part/shipping weight, print time and parcel dimensions,
- native select is retained inside a fallback details surface,
- chosen customer combination resolves back to the canonical ProductVariant ID and dispatches the existing change event, preserving current price/cart behavior,
- endpoint failure leaves mature native selection available,
- no schema migration.

Verification:
`Phase50 Variant2 Gallery CI` run `32958296546` PASS on snapshot `e3c57311c0c3980befeaf6012f3bb8fc502333bc`:
- Storefront JS syntax PASS,
- Django check PASS,
- migration drift NONE,
- migration plan/CI migrations PASS,
- Variant2/gallery/profile-selector regressions PASS.

### 50.A.2B — Checkout immutable profile/shipping snapshot — NEXT
The customer selector alone does not complete checkout/shipping. Remaining work:
- make selected sales-profile identity/customer-visible choice explicit in final immutable order state where needed while preserving existing Variant2 snapshots,
- effective product + packaging shipping weight,
- parcel dimensions and insured value,
- normalized carrier quote + immutable order snapshot,
- Post/Tipax/Mahex only after verified official API credentials/contracts,
- preserve mature ShippingMethod fallback.

## Product Engagement — OWNER REQUESTED SEPARATE SCHEMA PHASE
Preserve ProductLike/ProductComment/ProductReview. Add real Favorite/Save if absent, Product counters/Admin visibility and qualifying purchased/paid Product verification for buyer-feedback reviews/comments. Dedicated migration/tests/Production backup required; do not mix this schema work into current no-migration UI deploy.

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

## Current deployment gate
1. read-only verify actual Host root/branch/HEAD/worktree and live GitHub SHA,
2. verify host `remote.origin.fetch` and use explicit branch fetch to `FETCH_HEAD` per ERR-50-007,
3. re-verify exact MySQL vendor/name and applied `0034`/`0035`,
4. Django check + no model drift + empty migration plan,
5. verify private Velzon runtime assets exist,
6. fresh source/.env/MySQL backup and rollback HEAD,
7. verify target is ff descendant and contains no migration-file delta,
8. ff-only deploy, collectstatic, Passenger restart,
9. Home/Store/Admin/new static assets/private-media gates,
10. owner browser QA: footer stable on refresh, no whole-page menu jump, 290px readable sidebar, Product selector choices/price/cart synchronization.

## Must not touch
- no direct Production source edit,
- no public exposure of imported working-media,
- no destructive historical order/payment/ledger reset,
- no guessed carrier/gateway endpoint,
- no Production migration without exact DB/plan/backup/rollback verification,
- no purchased/private Velzon/font assets committed to public GitHub.
