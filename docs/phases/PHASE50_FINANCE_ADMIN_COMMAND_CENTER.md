# Phase50 — Finance, Commerce & Admin Command Center

Updated: 2026-08-25
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Status: `PLANNED / REPOSITORY AUDIT COMPLETE`
Production: `PHASE49 WEB HEALTHY BY OWNER VISUAL QA`

## Owner request
After successful Production web/hero verification, continue development by completing the business back-office: finance, receipts/payments, purchases/sales, accounting detail, and a complete/clear Django Admin information architecture.

## Verified existing foundation
The repository already contains substantial operational commerce/finance capabilities:
- StoreOrder / StoreOrderItem / StorePayment / StoreInvoice / Shipment / ReturnRequest,
- service Order / Quote / Payment and immutable PaymentLedgerEntry,
- payment gateway architecture with ZarinPal request/callback/verify and idempotency contract,
- FilamentPurchase / FilamentPurchaseItem / FilamentSpool / FilamentMovement,
- ProductionJob / MaterialUsage / CostEntry / BusinessFinanceDashboard,
- InventoryMovement and stock reservation/operations dashboard,
- affiliate commissions, payouts and immutable AffiliateLedgerEntry,
- admin sections for orders, payments, invoices, production, inventory, costs, affiliate and catalog operations.

These are operational modules, but they are not yet a complete general accounting system.

## Remaining business gaps
### A. Accounting core
- chart of accounts (کل/معین/تفصیلی),
- journal voucher / balanced debit-credit entries,
- immutable posting and reversal instead of destructive edits,
- fiscal periods, opening/closing balances and document numbering,
- account/subledger statements and running balances,
- trial balance and general ledger reports.

### B. Treasury / receipts and payments
- cash and bank accounts,
- generic Receipt and Payment vouchers independent of only Quote/StoreOrder,
- customer/supplier settlements,
- cheque lifecycle if required,
- bank reconciliation,
- refund workflow with authorization/reason/audit trail.

### C. Purchasing / supplier operations
- Supplier master,
- general PurchaseInvoice/PurchaseOrder beyond filament-only purchases,
- purchase invoice lines for material/service/expense assets,
- payable balance and supplier statement,
- purchase return / debit adjustments,
- linkage to filament warehouse receiving when applicable.

### D. Sales accounting
- normalized sales invoice accounting source for both StoreOrder and custom Quote/Order,
- receivables/customer statement,
- discount/tax/shipping accounting mapping,
- sales returns/refunds/credit notes,
- invoice/payment reconciliation.

### E. Finance reporting
- cash/bank position,
- accounts receivable/payable aging,
- customer and supplier statements,
- daily cashflow,
- revenue/cost/gross margin/net operating result,
- tax/VAT summary,
- project profitability with production/material usage integration.

## Admin Command Center delta
The current custom sidebar is already broad, but finance is fragmented across service orders, store orders, production and affiliate sections. Phase50 will make the operator-facing structure explicit:
1. Dashboard & alerts
2. Customers / CRM / support
3. Sales — service orders, quotes, store orders, invoices, returns
4. Treasury — receipts, payments, online gateway, bank/cash accounts, refunds
5. Accounting — chart of accounts, vouchers, journal, general/subledger, trial balance
6. Purchasing — suppliers, purchase invoices/orders, filament receiving
7. Inventory & production — stock, spools, movements, jobs, material usage, costs
8. Marketing / affiliate — commissions, payouts, affiliate ledger
9. Catalog / products / pricing / SEO
10. Settings / users / permissions / integrations / audit

Every ModelAdmin must have useful list_display, search, filters, date hierarchy where useful, readonly audit fields, safe actions, links to related objects, and permission-aware destructive controls.

## Safety / implementation order
This phase will be additive. Existing StoreOrder, Quote, Payment, PaymentLedgerEntry, inventory and production history must not be rewritten or deleted.

Implementation order:
1. Admin information-architecture cleanup and current-model completeness with NO migration.
2. Accounting schema design + migration review.
3. Local SQLite migration/test gate.
4. Finance service layer and posting rules.
5. Reports/admin workflows.
6. Local E2E using store sale + custom order + filament purchase + receipt/payment.
7. Explicit owner approval.
8. MySQL backup, Production migration/deploy and financial integrity audit.

## Must not touch
- already healthy Catalog/Bridge/Product/Hero behavior,
- existing Product media ownership,
- payment idempotency/security rules,
- historical PaymentLedgerEntry/AffiliateLedgerEntry rows,
- Production data without a verified backup/rollback plan.

## Acceptance target
Phase50 is accepted only when the same transaction can be traced end-to-end from commercial document to payment/receipt, accounting posting, subledger, general ledger and reports without duplicate posting or balance mismatch.
