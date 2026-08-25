# PROJECT ROADMAP

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Epic: `Phase50 — Finance, Commerce & Admin Command Center`
Current Phase: `50.A.1 — Admin Storefront / Hero parity`
Status: `GITHUB CI TESTED / MANUAL ADMIN QA NEXT`

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
- Product-backed/public-media eligibility guard for random Hero selection,
- Coupon, ShippingMethod, PricingSetting, StoreAddress and Iran location links surfaced in Command Center,
- no destructive Hero deletion,
- no migration,
- GitHub CI compile/check/no-migration/admin regressions PASS.

### 50.A.2 Checkout & Delivery — NEXT
Preserve the existing coupon/VAT/packaging/shipping calculations and extend them with:
- package weight in addition to product/variant weight,
- package dimensions and shipment insured value where required,
- normalized live quote provider contract,
- adapters for Post / Tipax / Mahex only after current official API endpoints, credentials, units and commercial terms are verified,
- provider timeout/error handling with fallback to the mature ShippingMethod weight rules,
- immutable shipping quote snapshot on the finalized order so later carrier price changes cannot mutate history,
- Admin controls for carrier/provider enablement and fallback pricing.

### 50.A.3 Secure online payments — AFTER 50.A.2 DESIGN
Preserve the mature service-payment transaction locking, random callback token, Authority matching and server-to-server verification. Extend Store checkout with the same contract plus:
- strict allowlist of payment redirect hosts,
- no card/PIN/CVV capture or storage on 3DPrintHub,
- server-owned amount and currency,
- idempotent request/callback/verify,
- reconciliation and immutable audit trail,
- abuse/rate-limit monitoring,
- Production HTTPS/HSTS/Secure-cookie/CSP/frame protections verified at deploy time.

## Phase50.B — Accounting foundation
After commerce/admin acceptance:
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
No Production schema work is authorized without exact MySQL verification, migration plan, successful backup and rollback target. Live-carrier integration is not implemented from guessed/unofficial API contracts.
