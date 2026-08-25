# PROJECT ROADMAP

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Epic: `Phase50 — Finance, Commerce & Admin Command Center`
Current Phase: `50.A — Admin Command Center completeness`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL TEST NEXT`

## Permanent delivery order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → WINDOWS PULL --FF-ONLY → LOCAL TEST → OWNER QA → HOST READ-ONLY VERIFY → BACKUP → DEPLOY FROM GITHUB → PRODUCTION VERIFY → DOCUMENT`

## Phase49 closeout baseline
- structured Product presentation deployed and verified,
- Catalog Site Publish validated Product-owned media,
- Hero Product-media ownership fixed,
- owner reports Production site/hero healthy.

## Phase50.A — implemented first slice
- business-oriented Admin Command Center at `/admin/command-center/`,
- explicit Sales / Treasury / Accounting & Ledgers / Purchasing / Inventory & Production groups,
- permission-aware links only to real existing admin models,
- live operational counters,
- sidebar shortcut,
- date hierarchy and consistent pagination on key finance/commerce admins,
- focused admin regression tests,
- NO migration.

### 50.A Local gate
1. clean Windows worktree and live ff-only pull,
2. `manage.py check`,
3. `makemigrations --check --dry-run`,
4. `manage.py test website.test_phase50a_admin_command_center -v 2`,
5. manual Admin navigation QA on desktop/mobile.

## Phase50.B — Accounting foundation
After 50.A acceptance:
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
No Production schema work is authorized until Phase50.A is Local-tested/owner-approved and Phase50.B schema/migrations are explicitly reviewed with MySQL backup/rollback requirements.
