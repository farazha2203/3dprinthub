# PROJECT_CONTEXT — 3DPrintHub

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Epic: `Phase50 — Finance, Commerce & Admin Command Center`
Current Subphase: `50.A.1B — Product Gallery + Variant 2.0 foundation`
Status: `GITHUB CI TESTED / MANUAL QA REQUIRED`
Production: `PHASE49 HEALTHY BY OWNER QA / PHASE50 UNDEPLOYED`

## Operating rule
GitHub/Repository is permanent source of truth.
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI/LOCAL GATE → MANUAL QA → OWNER APPROVAL → HOST READ-ONLY VERIFY → BACKUP/DEPLOY/VERIFY`.

No direct Production edits. Dirty Local/Host stops for inspection. New finance/commerce capabilities are additive and preserve mature orders, payments, inventory and Catalog history.

## Canonical paths
Windows project: `D:\projects\3DPrintHub`
Windows venv: `D:\projects\3DPrintHub\.venv`
Windows Django DB: `D:\projects\3DPrintHub\db.sqlite3`
Production project: `/home/sfkilvrs/3dprinthub`
Production venv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`
Production DB: MySQL `sfkilvrs_EmiAdmin_3dprinthub`

## Phase49 preserved contract
Catalog/Product/Hero release is operational. Product-owned media remains the public Hero/Product media ownership path in Production; imported Catalog working-media stays private.

## Existing business foundation
- StoreOrder/StoreOrderItem/StorePayment/StoreInvoice/Shipment/ReturnRequest,
- Coupon discount + VAT + packaging + shipping + order-weight calculation,
- ShippingMethod fixed/weight-rule pricing,
- StoreAddress and Iran Province/County/City reference data,
- custom service Order/Quote/Payment and immutable PaymentLedgerEntry,
- mature online payment request/callback/verify/idempotency architecture,
- filament purchasing/spools/movements,
- inventory reservation and movements,
- ProductionJob/MaterialUsage/CostEntry/BusinessFinanceDashboard,
- affiliate commission/payout/ledger,
- broad custom Admin.

## Phase50.A.1 Admin parity
- authenticated `/admin/command-center/`,
- Product and Imported Catalog add/remove Hero actions,
- Hero 5-random / 10-random / deactivate-all,
- Coupon, ShippingMethod, PricingSetting, customer addresses and Iran location reference models surfaced,
- GitHub CI tested.

## Phase50.A.1B current implementation
- product main media is a contain-fit interactive viewer,
- thumbnails swap into the main viewer,
- full-screen lightbox supports keyboard and previous/next navigation,
- ProductVariant now has size/build profile, packaging weight and parcel dimensions through migration-owned additive runtime fields,
- StoreOrderItem has matching snapshot columns,
- Admin exposes the new commerce attributes,
- safe public Variant metadata endpoint enriches the mature product selector,
- migration `store.0034_phase50_variant2_commerce` exists and is not deployed to Production.

## Verification
GitHub Actions `Phase50 Variant2 Gallery CI` run `32872549545` passed on code snapshot `8e3c151159424437157d3ef6861881be08b1aea8` with compile, Django check, no-untracked-migration state, migration plan/apply on CI SQLite and focused regressions.

## Immediate next work
### 50.A.2 Checkout & Delivery
Persist selected size/build/package snapshots during checkout; use effective shipping weight; add normalized carrier quote snapshots and provider/fallback Admin controls. Post/Tipax/Mahex live adapters require verified current official contracts/credentials.

### 50.A.3 Secure Store Payment
Unify StorePayment with the mature service-payment security model: server-owned amount, trusted gateway redirect hosts, random callback identity, exact provider Authority match, server-to-server verification, idempotency, audit/reconciliation and no collection/storage of card number/PIN/CVV.

### 50.A.4 Torob
Implement current official Product API v3 with stable product/variant grouping, size/color/material, price/availability and image-quality rules.

## Accounting path after commerce gate
Phase50.B designs double-entry accounting: chart of accounts کل/معین/تفصیلی, fiscal periods, balanced journals, immutable posting/reversal and subledger references. No Production migration before MySQL verification, migration testing, backup and rollback review.
