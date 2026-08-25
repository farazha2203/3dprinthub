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
Raw Catalog/AI internals are not exposed publicly.

## REQ-49I-039 — Homepage Hero uses Product-owned public media
Status: `OWNER REPORTS PRODUCTION OK`
Imported working-media namespace must remain private; public Hero resolves to Product-owned media.

## REQ-REL-001 — Catalog production release
Status: `WEB/CATALOG RELEASE OPERATIONAL`
Do not reopen completed Catalog architecture unless a new verified defect appears.

## REQ-50-001 — Complete business finance/accounting system
Status: `REQUESTED / PHASE50 PLANNED`
Owner requests completion of the business back-office including:
- دفتر کل / معین / تفصیلی,
- اسناد حسابداری بدهکار/بستانکار,
- دریافت و پرداخت,
- صندوق و بانک,
- حساب مشتریان و تامین‌کنندگان,
- خرید و فروش,
- مانده بدهکار/بستانکار,
- گزارش گردش حساب، دفتر کل/معین و تراز آزمایشی,
- سود و زیان / جریان نقد / گزارش‌های مدیریتی,
- اتصال واقعی فروشگاه، سفارش خدمات، خرید فیلامنت، انبار، تولید و پرداخت‌ها به حسابداری.

Existing PaymentLedgerEntry, CostEntry, BusinessFinanceDashboard and affiliate ledger are preserved as operational/audit sources; they must not be destructively replaced.

## REQ-50-002 — Complete and reorganize Django Admin
Status: `REQUESTED / PHASE50.A NEXT`
Admin must become a precise business command center with explicit groups:
- Dashboard & alerts,
- Customers / CRM / support,
- Sales & service orders,
- Store sales / invoices / returns,
- Treasury / receipts / payments / gateway / refunds,
- Accounting / chart of accounts / vouchers / ledgers / reports,
- Purchasing / suppliers / purchase invoices,
- Inventory & production,
- Affiliate / commissions / payouts,
- Catalog / products / pricing / SEO,
- Settings / users / permissions / integrations / audit.

Each business ModelAdmin should have meaningful list columns, search, filters, date hierarchy where relevant, links to related documents, safe actions, immutable audit fields and permission-aware delete/change behavior.

## REQ-50-003 — Preserve healthy commerce while adding accounting
Status: `ACTIVE CONSTRAINT`
Phase50 is additive. Existing StoreOrder, Quote, Payment, StorePayment, invoices, inventory movements, Product/media/Catalog history and payment idempotency/security rules must remain compatible and regression-tested.

## Change rule
New work extends/wraps mature behavior and must pass Local tests before Production deployment. No financial schema migration is deployed without MySQL verification, backup and rollback plan.
