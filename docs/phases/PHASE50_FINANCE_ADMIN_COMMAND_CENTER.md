# Phase50 — Finance, Commerce & Admin Command Center

Updated: 2026-08-25
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Subphase: `50.A.1B — Product Gallery + Variant 2.0 foundation`
Status: `GITHUB CI TESTED / MANUAL QA REQUIRED`
Production: `PHASE49 WEB HEALTHY / PHASE50 UNDEPLOYED`

## Owner request
Complete the business back-office and storefront commerce before accounting core.

Current explicit priorities:
- professional product gallery: thumbnail -> main viewer -> full-screen zoom,
- professional Admin parity for Product/Hero/catalog/front-end controls,
- sellable size/build variants such as 20/24/26/28/30 cm with hollow/standard/solid weight profiles,
- one server/Windows contract for price, material, color, size, weight and sellable variants,
- package weight/dimensions for delivery calculation,
- Post/Tipax/Mahex rate integration only from verified current official contracts,
- coupon + VAT + shipping in checkout,
- secure Store ZarinPal payment,
- Torob integration before accounting core.

## Verified existing foundation
- StoreOrder / StoreOrderItem / StorePayment / StoreInvoice / Shipment / ReturnRequest,
- Coupon validation/discount application,
- PricingSetting VAT and packaging fee,
- ShippingMethod fixed and weight-rule pricing,
- StoreAddress plus IranProvince/IranCounty/IranCity,
- service Order / Quote / Payment and immutable PaymentLedgerEntry,
- mature online payment engine with server-owned amounts, locking, random callback tokens, exact Authority matching and server-to-server verification,
- Production HTTPS/HSTS/Secure-cookie/SameSite/HttpOnly/nosniff/DENY framing,
- ProductVariant material/quality/color/weight/time/price/inventory foundation.

## 50.A.1 — Admin Storefront / Hero parity
Implemented and CI tested:
- authenticated `/admin/command-center/`,
- Product and Imported Catalog add/remove Hero actions,
- Hero 5-random / 10-random / deactivate-all,
- permission-aware links to Product, Hero, Coupon, ShippingMethod, PricingSetting, StoreAddress and Iran location data,
- non-destructive Hero changes.

## 50.A.1B — Product Gallery + Variant 2.0
### Requested Delta
Fix the owner-reported product gallery UX and introduce first-class sellable size/build/package attributes without rewriting the mature Product/Cart architecture.

### Touched surfaces
- `store/phase50_variant2.py`,
- `store/phase50_variant_admin.py`,
- `store/phase50_variant_views.py`,
- `store/apps.py`,
- `store/urls.py`,
- `store/migrations/0034_phase50_variant2_commerce.py`,
- `store/test_phase50_variant2_gallery.py`,
- `static/store/js/store.js`,
- `static/store/css/store.css`,
- `.github/workflows/phase50-variant2-gallery-ci.yml`.

### Implemented
- contain-fit Product main viewer,
- thumbnail click/keyboard selection replaces the main image,
- full-screen lightbox with close, previous/next, Escape and arrow keys,
- `ProductVariant.size_label`,
- `ProductVariant.build_profile`: standard/hollow/reinforced/solid/custom,
- packaging weight and package length/width/height,
- StoreOrderItem snapshot columns for size/build/package history,
- Variant uniqueness now includes size/build profile,
- Admin list/filter/inline exposure of new commerce fields,
- safe public Variant metadata endpoint for the current product selector,
- effective shipping-weight helper using explicit shipping weight when present or product/final weight + packaging otherwise.

### Migration
`store.0034_phase50_variant2_commerce` is additive but changes the ProductVariant uniqueness contract. It is NOT authorized for Production until exact MySQL vendor/name, migration plan, successful DB backup and rollback target are verified.

### Regression gate
GitHub Actions `Phase50 Variant2 Gallery CI`, run `32872549545`, PASS on code snapshot `8e3c151159424437157d3ef6861881be08b1aea8`:
- compile PASS,
- Django check PASS,
- migration state dry-run PASS,
- migration plan PASS,
- SQLite migration apply PASS,
- focused Variant/Admin/endpoint/gallery contract tests PASS.

## 50.A.2 — Checkout & Delivery — next
- persist size/build/package snapshots from selected variant during checkout,
- use effective shipping weight consistently,
- normalize carrier quote inputs: origin/destination, postal code, weight, package dimensions, insured value, carrier/service,
- immutable quote result snapshot: base fee, taxes/charges, total, ETA, provider reference,
- Post/Tipax/Mahex adapters only after current official API/credentials are verified,
- timeout/error fallback to mature ShippingMethod weight rules,
- Admin provider/fallback controls.

## 50.A.3 — Secure Store ZarinPal
Reuse the mature service-payment engine for StorePayment:
- server-owned amount/currency,
- strict trusted redirect host allowlist,
- no card/PIN/CVV collection or storage,
- idempotent request/callback/verify,
- random callback identity + exact Authority match,
- server-to-server verification before paid state,
- reconciliation/audit/abuse monitoring,
- real Production merchant activation only after secure checkout E2E.

## 50.A.4 — Torob
Implement the current official Torob Product API v3 contract with product/variant grouping, size/color/material mapping, price/availability, image-quality rules, pagination and stable unique identifiers. Order-attribution/webhook work follows only after official contract verification.

## Must not touch
- healthy Catalog/Bridge/Product/Hero public media ownership,
- historical order/payment/ledger rows,
- public customer address history,
- Production source directly,
- card data capture/storage,
- unverified carrier endpoints.

## Remaining Phase50 path
### 50.B Accounting core
Chart of accounts کل/معین/تفصیلی, fiscal periods, balanced journal vouchers, immutable posting/reversal and party/subledger references.

### 50.C Treasury
Bank/cash accounts, receipt/payment vouchers, allocations, refunds and reconciliation.

### 50.D Purchasing
Supplier master, purchase orders/invoices/receiving/payables/returns.

### 50.E Sales accounting
Normalized Store/service receivables, payment allocation, tax/discount/shipping and credit notes.

### 50.F Reports & close
GL/subledger, trial balance, AR/AP aging, cashflow, profitability, VAT/tax and fiscal close.

## Acceptance target
Phase50 is accepted only when commerce operations, delivery/payment calculation and financial posting can be traced without duplicate payment/posting or balance mismatch.
