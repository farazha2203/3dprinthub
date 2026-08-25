# Phase50 — Finance, Commerce & Admin Command Center

Updated: 2026-08-25
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Subphase: `50.A — Admin Command Center completeness`
Status: `IMPLEMENTED ON GITHUB / LOCAL TEST REQUIRED`
Production: `PHASE49 WEB HEALTHY / PHASE50 UNDEPLOYED`

## Owner request
Continue development after the healthy Phase49 web release by completing business back-office finance/accounting, receipts/payments, purchasing/sales and a precise Django Admin command center.

## Verified existing foundation
- StoreOrder / StoreOrderItem / StorePayment / StoreInvoice / Shipment / ReturnRequest,
- service Order / Quote / Payment and immutable PaymentLedgerEntry,
- ZarinPal-capable server-owned request/callback/verify architecture,
- FilamentPurchase / FilamentPurchaseItem / FilamentSpool / FilamentMovement,
- ProductionJob / MaterialUsage / CostEntry / BusinessFinanceDashboard,
- inventory reservation/movements and store operations dashboard,
- affiliate commissions/payouts and immutable AffiliateLedgerEntry,
- broad mature ModelAdmin registrations.

## 50.A Requested Delta
Make the current back-office business-oriented before introducing any new financial schema.

### Touched surfaces
- `website/phase50a_admin_command_center.py`,
- `config/urls.py`,
- `website/apps.py`,
- `templates/admin/base_site.html`,
- `templates/admin/phase50_command_center.html`,
- `static/css/phase50a-admin-command-center.css`,
- `static/js/phase50a-admin-command-center.js`,
- `website/test_phase50a_admin_command_center.py`.

### Implemented
- authenticated `/admin/command-center/`,
- explicit Sales, Treasury, existing Accounting/Ledgers, Purchasing and Inventory/Production sections,
- permission-aware real links only; future accounting modules are shown as roadmap text, not broken admin URLs,
- live counters for pending payments/orders/purchases/payouts/cost entries,
- visible `مرکز مالی و بازرگانی` shortcut in the custom sidebar,
- date hierarchy + 50-row pagination applied to key mature finance/commerce ModelAdmins,
- focused regression coverage for auth, sections/links, admin registration metadata and sidebar script loading.

## Must not touch
- healthy Catalog/Bridge/Product/Hero/media behavior,
- StoreOrder/Quote/payment semantics,
- online-payment idempotency/security,
- historical PaymentLedgerEntry/AffiliateLedgerEntry,
- database schema in 50.A,
- Production before Local gate and owner approval.

## Regression / Local Gate
- `python manage.py check`,
- `python manage.py makemigrations --check --dry-run` => no changes,
- `python manage.py test website.test_phase50a_admin_command_center -v 2`,
- manual `/admin/` and `/admin/command-center/` desktop/mobile QA.

## Remaining business gaps after 50.A
### 50.B Accounting core
- chart of accounts (کل/معین/تفصیلی),
- fiscal periods,
- balanced journal vouchers,
- immutable posting/reversal,
- party/subledger references,
- general/subledger and trial balance.

### 50.C Treasury
- bank/cash accounts,
- generic receipt/payment vouchers,
- customer/supplier settlements,
- reconciliation,
- controlled refund workflow.

### 50.D Purchasing
- Supplier master,
- general purchase orders/invoices/lines,
- payables and supplier statement,
- purchase returns/adjustments,
- receiving integration.

### 50.E Sales accounting
- normalized sales accounting events for StoreOrder and custom Quote/Order,
- receivable statements and payment allocation,
- discount/tax/shipping mapping,
- credit notes/refunds.

### 50.F Reports & close
- GL/subledger, trial balance, AR/AP aging,
- cashflow, profitability, tax/VAT,
- financial integrity audit and fiscal close.

## Acceptance target
Phase50 is accepted only when a transaction can be traced from commercial document to payment/receipt, accounting posting, subledger, general ledger and reports without duplicate posting or balance mismatch.
