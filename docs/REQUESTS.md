# OWNER REQUESTS

Last Updated: 2026-08-25

Older detailed request history remains available in Git history. This file keeps the active acceptance contracts.

## Preserved Phase49 contracts
- GitHub-first delivery; live branch/HEAD verification before Local/Host operations.
- Catalog Product Workspace remains canonical editor.
- exact Search/Listing URL remains authoritative.
- Product AI uses exactly one saved Provider/Model/key path and no hidden AI/model scan on open.
- fixed/range/formula pricing modes remain independent.
- Product/SEO/media/Bridge security and idempotency contracts remain intact.

## REQ-49I-038 — Customer-readable Product intelligence
Status: `PRODUCTION VERIFIED`

## REQ-49I-039 — Homepage Hero uses Product-owned public media
Status: `OWNER REPORTS PRODUCTION OK`

## REQ-REL-001 — Catalog production release
Status: `WEB/CATALOG RELEASE OPERATIONAL`

## REQ-50-001 — Complete business finance/accounting system
Status: `REQUESTED / PHASE50 ACTIVE`
Owner requests:
- دفتر کل / معین / تفصیلی,
- balanced debit/credit accounting documents,
- receipt/payment, bank/cash,
- customer/supplier accounts,
- purchase/sales accounting,
- debit/credit balances and statements,
- GL/subledger/trial balance,
- profit/loss, cashflow and management reports,
- integration of Store, service orders, purchasing, inventory, production and payments.

Existing PaymentLedgerEntry, CostEntry, BusinessFinanceDashboard and affiliate ledger must be preserved as operational/audit sources.

## REQ-50-002 — Complete and reorganize Django Admin
Status: `50.A IMPLEMENTED ON GITHUB / LOCAL QA REQUIRED`

Implemented first slice:
- authenticated `/admin/command-center/`,
- Sales / Treasury / Accounting & Ledgers / Purchasing / Inventory & Production groups,
- permission-aware links to real current ModelAdmins,
- live operational counters,
- sidebar shortcut `مرکز مالی و بازرگانی`,
- date hierarchy and consistent pagination on key financial/commerce admins,
- admin regression coverage.

Acceptance still requires Windows `manage.py check`, migration dry-run, focused tests and manual Admin navigation QA.

## REQ-50-003 — Preserve healthy commerce while adding accounting
Status: `ACTIVE CONSTRAINT`
Phase50 is additive. Existing StoreOrder, Quote, Payment, StorePayment, invoices, inventory movements, Product/media/Catalog history and payment idempotency/security rules remain compatible and regression-tested.

## Change rule
New work extends/wraps mature behavior and must pass Local tests before Production deployment. No financial schema migration is deployed without MySQL verification, backup and rollback plan.
