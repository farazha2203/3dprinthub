# PROJECT_CONTEXT — 3DPrintHub

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Epic: `Phase50 — Finance, Commerce & Admin Command Center`
Current Subphase: `50.A.1 — Admin Storefront / Hero parity`
Status: `GITHUB CI TESTED / MANUAL ADMIN QA REQUIRED`
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

## Current 50.A.1 implementation
- authenticated `/admin/command-center/`,
- business groups now include Storefront & Checkout alongside Sales/Treasury/Accounting/Purchasing/Inventory,
- Product and Imported Catalog Asset bulk actions to add/remove homepage Hero membership,
- Hero quick operations: 5 random Products, 10 random Products and non-destructive deactivate-all,
- random selection limited to active Product-backed assets with public-renderable media,
- existing manually edited Hero content preserved on reactivation,
- Coupon, ShippingMethod, PricingSetting, StoreAddress and Iran location reference models surfaced from the Command Center,
- no schema migration.

## Verification
GitHub Actions `Phase50 Admin Storefront Parity CI` passed on code snapshot `7c8714b5715cd00900a76b99097823266251d4a2` with compile, Django check, no-migration dry-run and focused Admin regressions.
Manual visual/operational Admin QA and Production deploy remain pending.

## Immediate next work
### 50.A.2 Checkout & Delivery
Extend mature shipping with package weight/dimensions and a normalized live-carrier quote adapter. Post/Tipax/Mahex adapters require verified current official API contracts/credentials; mature ShippingMethod weight rules remain fallback.

### 50.A.3 Secure Store Payment
Unify StorePayment with the mature service-payment security model: server-owned amount, trusted gateway redirect hosts, random callback identity, exact provider Authority match, server-to-server verification, idempotency, audit/reconciliation and no collection/storage of card number/PIN/CVV.

## Accounting path after commerce gate
Phase50.B designs double-entry accounting: chart of accounts کل/معین/تفصیلی, fiscal periods, balanced journals, immutable posting/reversal and subledger references. No Production migration before MySQL verification, migration testing, backup and rollback review.
