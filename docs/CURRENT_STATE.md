# CURRENT PROJECT STATE

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Base Epic: `epic/phase49-unified-product-slider-sync`
Current Release: `Phase50.A — Admin Command Center completeness`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL TEST REQUIRED`

## Production baseline
Owner reports the Phase49 Production site and Hero are healthy. Previously verified Production state remains:
- project `/home/sfkilvrs/3dprinthub`,
- MySQL `sfkilvrs_EmiAdmin_3dprinthub`,
- Phase49 migrations through `store.0033` and `website.0023` applied,
- Product / Store / Home healthy,
- rollback DB backup retained at `/home/sfkilvrs/3dprinthub-deploy-backups/20260825-150401/mysql-before-deploy.sql.gz`.

No Phase50 code has been deployed to Production yet.

## Phase50.A implemented on GitHub
Requested delta: make the mature back-office easier to operate before introducing new accounting schema.

Implemented:
- new business-oriented `/admin/command-center/` protected by Django Admin authentication,
- unified sections for Sales, Treasury, existing accounting/ledgers, Purchasing, Inventory & Production,
- permission-aware links to the already-registered mature ModelAdmins,
- live operational counters for pending service/store payments, active Store orders, draft filament purchases, open affiliate payouts and cost records,
- explicit upcoming Phase50.B-F accounting capabilities shown as roadmap items rather than fake/broken links,
- Phase50 shortcut injected into the custom Admin sidebar,
- safe ModelAdmin browsing ergonomics for Payment, PaymentLedgerEntry, StorePayment, StoreOrder, FilamentPurchase, CostEntry, ProductionJob and AffiliatePayout: date hierarchy + 50-row pagination,
- focused regression test `website/test_phase50a_admin_command_center.py`.

## Safety / Must-not-touch
- NO migration/schema change in Phase50.A,
- no StoreOrder/Quote/Payment behavior change,
- no payment gateway/idempotency change,
- no Catalog/Bridge/Product/Hero/media change,
- no destructive rewrite of PaymentLedgerEntry/AffiliateLedgerEntry,
- Production untouched.

## Verification status
GitHub implementation exists, but no Windows Local execution result has been reported yet. Do not mark LOCAL_TESTED/DEPLOYED until the Local gate is run.

## Exact next task
1. Windows clean worktree + live `fetch --prune` + ff-only pull of the current feature HEAD.
2. Run `manage.py check`.
3. Run `manage.py makemigrations --check --dry-run` and confirm NO migration.
4. Run `manage.py test website.test_phase50a_admin_command_center -v 2`.
5. Open `/admin/` and `/admin/command-center/`; verify sidebar shortcut, permission-aware links, Sales/Treasury/Accounting/Purchasing/Inventory sections and mobile/desktop layout.
6. After owner approval, continue Phase50.A completeness or begin reviewed Phase50.B accounting schema design.
