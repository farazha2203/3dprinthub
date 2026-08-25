# CURRENT PROJECT STATE

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Base Epic: `epic/phase49-unified-product-slider-sync`
Current Release: `Phase49.3I`
Last Hotfix: `49.3I.30 — Production Hero Product-Media Ownership`
Next Phase: `Phase50 — Finance, Commerce & Admin Command Center`
Status: `PHASE49 WEB OWNER-VERIFIED / PHASE50 PLANNED`

## Production / owner verification
Owner reports the Production site is now healthy after the Hero media ownership fix. Previous machine-verified Production baseline remains:
- Production project `/home/sfkilvrs/3dprinthub`,
- MySQL `sfkilvrs_EmiAdmin_3dprinthub`,
- Phase49 migrations through `store.0033` and `website.0023` already applied,
- Product page and Product-owned media healthy,
- Product presentation sanitization PASS,
- prior Production worktree verified clean,
- rollback DB backup retained at `/home/sfkilvrs/3dprinthub-deploy-backups/20260825-150401/mysql-before-deploy.sql.gz`.

The latest owner message confirms the site/hero is visually OK. No new host command output was provided in that message, so this is recorded as owner visual acceptance rather than a fresh machine audit.

## Verified existing business foundation
Repository audit confirms substantial modules already exist:
- StoreOrder / StoreOrderItem / StorePayment / StoreInvoice / Shipment / ReturnRequest,
- custom service Order / Quote / Payment,
- immutable `PaymentLedgerEntry` for service payment events,
- ZarinPal-capable online payment gateway architecture with server-owned amount, callback/verify and idempotency contract,
- FilamentPurchase / FilamentPurchaseItem / FilamentSpool / FilamentMovement,
- ProductionJob / MaterialUsage / CostEntry / BusinessFinanceDashboard,
- InventoryMovement and stock reservation/operations,
- affiliate commission/payout/ledger modules,
- broad custom Django Admin sidebar and operational dashboards.

## Important gap
The project does NOT yet have a complete accounting system. Existing finance pieces are operational ledgers and profitability/inventory tools, not a balanced double-entry accounting core.

Missing major business capabilities are defined in `docs/phases/PHASE50_FINANCE_ADMIN_COMMAND_CENTER.md`, including:
- chart of accounts: کل / معین / تفصیلی,
- balanced accounting vouchers and posting/reversal,
- customer/supplier subledgers,
- generic receipt/payment vouchers and cash/bank accounts,
- supplier master and general purchase invoices/orders beyond filament-only purchases,
- receivable/payable aging and reconciliation,
- general ledger / trial balance / statements,
- controlled refund workflow,
- consolidated sales/purchase/treasury/accounting reporting.

## Admin status
The Admin already exposes most operational models, but finance is fragmented across service orders, store orders, production and affiliate menus. Phase50 begins by reorganizing and completing the Admin Command Center before adding new accounting schema.

## Exact next development task
`Phase50.A — Admin Command Center completeness, NO migration`:
1. audit every registered business ModelAdmin,
2. reorganize admin navigation into Sales / Treasury / Accounting / Purchasing / Inventory & Production / Marketing / Catalog / Settings,
3. add missing safe links, filters, searches, read-only audit fields and operational actions,
4. add regression tests for admin registration/navigation/permissions,
5. Windows Local Django check + migration dry-run + admin smoke.

Only after Phase50.A passes do we design Phase50.B accounting schema/migrations.
