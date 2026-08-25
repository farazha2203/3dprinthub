# PROJECT ROADMAP

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Epic: `Phase50 — Finance, Commerce & Admin Command Center`
Current Phase: `50.A.1B — Product Gallery + Variant 2.0 foundation`
Status: `GITHUB CI TESTED / MANUAL QA NEXT`

## Permanent delivery order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI/LOCAL TEST → OWNER QA → HOST READ-ONLY VERIFY → BACKUP → DEPLOY FROM GITHUB → PRODUCTION VERIFY → DOCUMENT`

## Phase49 closeout baseline
- structured Product presentation deployed and verified,
- Catalog Site Publish validated Product-owned media,
- Hero Product-media ownership fixed,
- owner reports Production site/hero healthy.

## Phase50.A — Admin and commerce operational completeness
### 50.A.1 Admin Storefront / Hero parity — CI TESTED
- business-oriented `/admin/command-center/`,
- Sales / Storefront & Checkout / Treasury / Accounting / Purchasing / Inventory groups,
- Store Product and Imported Asset actions for add/remove homepage slider,
- Homepage Hero buttons for 5 random, 10 random and deactivate-all,
- Product-backed/public-media eligibility guard,
- Coupon, ShippingMethod, PricingSetting, StoreAddress and Iran location links surfaced.

### 50.A.1B Product Gallery + Variant 2.0 — CI TESTED
- contain-fit main product viewer,
- thumbnail click swaps main image,
- full-screen accessible lightbox with previous/next/Escape,
- sellable variant adds `size_label` and `build_profile` (standard/hollow/reinforced/solid/custom),
- packaging weight and parcel dimensions added to ProductVariant,
- size/build/package snapshots added to StoreOrderItem,
- ProductVariant identity now includes size/build profile,
- Admin exposes the new commerce fields,
- public variant metadata endpoint enriches the mature selector,
- migration `store.0034_phase50_variant2_commerce`,
- CI compile/check/migration-state/migrate/tests PASS on snapshot `8e3c151159424437157d3ef6861881be08b1aea8`.

### 50.A.2 Checkout & Delivery — NEXT
Preserve coupon/VAT/packaging/shipping calculations and extend them with:
- snapshot Variant size/build/package fields when StoreOrderItem is created,
- effective shipping weight from product + packaging when no explicit override exists,
- parcel dimensions and shipment insured value,
- normalized live quote provider contract,
- Post / Tipax / Mahex adapters only after official current endpoints, credentials, units and commercial terms are verified,
- provider timeout/error fallback to mature ShippingMethod weight rules,
- immutable quote snapshot on finalized orders,
- Admin controls for carrier/provider enablement and fallback pricing.

### 50.A.3 Secure Store ZarinPal payment
Preserve the mature service-payment transaction locking, random callback token, Authority matching and server-to-server verification. Extend Store checkout with the same contract plus:
- strict trusted gateway-host allowlist,
- no card/PIN/CVV capture or storage,
- server-owned amount and currency,
- idempotent request/callback/verify,
- reconciliation and immutable audit trail,
- abuse/rate-limit monitoring,
- Production HTTPS/HSTS/Secure-cookie/CSP/frame verification.

### 50.A.4 Torob integration
- current Torob Product API v3 contract,
- product/variant grouping with stable unique identifiers,
- size/color/material mapping,
- current price and availability,
- image-quality guards for marketplace export,
- pagination/filtering required by Torob,
- order-attribution/webhook only after official contract verification.

## Phase50.B — Accounting foundation
- chart of accounts: کل / معین / تفصیلی,
- fiscal periods,
- accounting vouchers,
- balanced debit/credit entries,
- immutable posting/reversal,
- party/subledger references,
- audit-safe numbering.

## Phase50.C — Treasury
- bank/cash accounts,
- receipt/payment vouchers,
- allocation to StorePayment/service Payment,
- refund workflow,
- reconciliation.

## Phase50.D — Purchasing & payables
- Supplier master,
- purchase orders/invoices and lines,
- general receiving beyond filament-only purchases,
- supplier payable/subledger,
- purchase returns/adjustments.

## Phase50.E — Sales & receivables accounting
- normalize StoreOrder and custom Quote/Order accounting events,
- customer receivable statements,
- payment allocation,
- discount/tax/shipping mapping,
- sales returns/refunds/credit notes.

## Phase50.F — Reports & close
- general/subledger,
- trial balance,
- customer/supplier statements,
- AR/AP aging,
- cashflow,
- project profitability,
- tax/VAT summary,
- integrity audit and period close.

## Safety
No Production schema work is authorized without exact MySQL verification, migration plan, successful backup and rollback target. Live carrier integrations are not implemented from guessed/unofficial API contracts.
