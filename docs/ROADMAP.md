# PROJECT ROADMAP

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Release: `Phase49.3I — Unified Product / Slider / Catalog Sync`
Next Epic: `Phase50 — Finance, Commerce & Admin Command Center`
Status: `PHASE49 WEB OWNER-VERIFIED / PHASE50.A NEXT`

## Permanent delivery order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → WINDOWS PULL --FF-ONLY → LOCAL TEST → OWNER QA → HOST READ-ONLY VERIFY → BACKUP → DEPLOY FROM GITHUB → PRODUCTION VERIFY → DOCUMENT`

## Phase49 closeout
- structured Product presentation is deployed and verified,
- Product/Store/Home are healthy,
- first Catalog Site Publish validated Product-owned media,
- Hero production media ownership defect was fixed,
- owner now reports Production site/hero is OK.

Phase49 remains subject to the existing rollback/safety records; no new Catalog redesign is planned in Phase50.

## Existing business modules already present
- Store commerce: cart/checkout, StoreOrder, StoreOrderItem, StorePayment, invoice, shipping, returns, coupons, inventory reservation and order events.
- Service commerce: custom Order, Quote, deposit/full/balance Payment, manual receipt flow and online-payment architecture.
- Payment audit: immutable `PaymentLedgerEntry`; online payment uses server-owned amounts and idempotent callback/verify contract.
- Inventory/production: filament purchasing, spools, movements, material usage, production jobs and cost entries.
- Partner sales: affiliate partners, commissions, payouts and affiliate ledger.
- Admin: custom sidebar, store operations dashboard, finance/profit dashboard and extensive ModelAdmin coverage.

## What is NOT complete yet
Operational finance is not equivalent to full accounting. The following remain:
1. chart of accounts (کل / معین / تفصیلی),
2. balanced accounting vouchers and debit/credit journal,
3. immutable posting/reversal and fiscal periods,
4. customer/supplier ledgers and running balances,
5. generic receipt/payment vouchers, cash/bank accounts and reconciliation,
6. Supplier master and general purchasing beyond filament-only purchases,
7. receivable/payable aging,
8. consolidated sales/purchase/refund accounting,
9. general ledger, trial balance, account statements, cashflow and tax/VAT reports,
10. controlled real refund workflow with permissions/audit.

## Phase50 implementation order
### 50.A — Admin Command Center completeness — NO MIGRATION
- make navigation business-oriented rather than model-oriented,
- dedicated Sales / Treasury / Accounting / Purchasing / Inventory & Production sections,
- complete ModelAdmin search/filter/date/read-only/related-link/actions contracts,
- expose current Store/Service payments, invoices, ledger, filament purchases, costs and affiliate settlement clearly,
- admin registration/navigation/permission regression tests.

### 50.B — Accounting foundation
- chart of accounts,
- account/subledger parties,
- fiscal periods,
- journal vouchers and balanced entries,
- posting/reversal service layer,
- audit-safe numbering.

### 50.C — Treasury
- bank/cash accounts,
- receipt/payment vouchers,
- link to StorePayment / service Payment,
- refund/settlement workflow,
- reconciliation.

### 50.D — Purchasing & payables
- supplier registry,
- purchase invoice/order and lines,
- warehouse receiving integration,
- supplier payable/subledger,
- returns/adjustments.

### 50.E — Sales & receivables accounting
- normalize StoreOrder and custom Quote/Order accounting events,
- customer receivable statement,
- invoice/payment allocation,
- discount/tax/shipping mapping,
- sales return/refund/credit note.

### 50.F — Reports & close
- general ledger and subledger,
- trial balance,
- customer/supplier statements,
- AR/AP aging,
- cashflow,
- project profitability,
- tax/VAT summary,
- integrity audit and period close.

## Immediate next gate
`Phase50.A GitHub implementation → Windows ff-only pull → manage.py check → makemigrations --check --dry-run → admin regression tests → manual admin navigation QA`.

No Production schema work is authorized until Phase50.A is accepted and Phase50.B migration design has been reviewed with backup/rollback requirements.
