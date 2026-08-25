# PROJECT_CONTEXT — 3DPrintHub

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Epic: `Phase50 — Finance, Commerce & Admin Command Center`
Current Subphase: `50.A — Admin Command Center completeness`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA REQUIRED`
Production: `PHASE49 HEALTHY BY OWNER QA / PHASE50 UNDEPLOYED`

## Operating rule
GitHub/Repository is permanent source of truth.
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → WINDOWS PULL --FF-ONLY → LOCAL GATE → MANUAL QA → OWNER APPROVAL → HOST READ-ONLY VERIFY → BACKUP/DEPLOY/VERIFY`.

No direct Production edits. Dirty Local/Host stops for inspection. New finance capabilities are additive and must preserve mature commerce/payment/inventory history.

## Canonical paths
Windows project: `D:\projects\3DPrintHub`
Windows venv: `D:\projects\3DPrintHub\.venv`
Windows Django DB: `D:\projects\3DPrintHub\db.sqlite3`
Production project: `/home/sfkilvrs/3dprinthub`
Production venv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`
Production DB: MySQL `sfkilvrs_EmiAdmin_3dprinthub`

## Phase49 preserved contract
Catalog/Product/Hero release is operational. Product-owned media remains the only public Hero/Product media ownership path in Production; imported Catalog working-media stays private. Phase50 must not alter Catalog/Bridge/Product/Hero behavior.

## Existing business foundation
- StoreOrder/StoreOrderItem/StorePayment/StoreInvoice/Shipment/ReturnRequest,
- custom service Order/Quote/Payment and immutable PaymentLedgerEntry,
- online payment request/callback/verify/idempotency architecture,
- filament purchasing/spools/movements,
- inventory reservation and movements,
- ProductionJob/MaterialUsage/CostEntry/BusinessFinanceDashboard,
- affiliate commission/payout/ledger,
- broad custom Admin.

## Current 50.A implementation
- authenticated `/admin/command-center/`,
- business groups: Sales, Treasury, Accounting & existing ledgers, Purchasing, Inventory & Production,
- permission-aware real admin links,
- operational counters,
- sidebar shortcut,
- date hierarchy + consistent pagination on key financial/commerce ModelAdmins,
- focused regression test,
- NO migration.

## Current gate
Windows: clean worktree → live ff-only pull → `manage.py check` → `makemigrations --check --dry-run` → `manage.py test website.test_phase50a_admin_command_center -v 2` → manual Admin QA.

## Next phase after 50.A acceptance
Phase50.B designs the actual double-entry accounting schema: chart of accounts (کل/معین/تفصیلی), fiscal periods, balanced journal vouchers/entries, posting/reversal and subledger references. No Production migration before Local migration tests plus MySQL backup/rollback review.
