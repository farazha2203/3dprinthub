# PROJECT_CONTEXT — 3DPrintHub

Updated: 2026-08-26
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Epic: `Phase50 — Finance, Commerce & Admin Command Center`
Current Subphase: `50.A.1G — Velzon Operator Surface V2`
Status: `GITHUB CI TESTED / PRODUCTION DEPLOY NEXT`

## Operating rule
GitHub/Repository is permanent source of truth.
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI/LOCAL GATE → MANUAL QA → OWNER APPROVAL → HOST READ-ONLY VERIFY → BACKUP/DEPLOY/VERIFY`.

No permanent Production source edit. Dirty Local/Host stops for inspection. New commerce/finance work is additive and preserves mature orders, payments, inventory and Catalog history. Purchased/private theme/font assets are not published into this public repository.

## Canonical paths
Windows project: `D:\projects\3DPrintHub`
Windows venv: `D:\projects\3DPrintHub\.venv`
Windows Django DB: `D:\projects\3DPrintHub\db.sqlite3`
Production project: `/home/sfkilvrs/3dprinthub`
Production venv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`
Production DB: MySQL `sfkilvrs_EmiAdmin_3dprinthub`

## Production verified baseline
Current Production application commit is `bc7b97f9c63432b8105f52f61cf5cdae1369689b`.
Verified:
- `store.0034_phase50_variant2_commerce` applied,
- `store.0035_phase50_sales_profiles` applied,
- Product Admin real-row changelist render 200,
- Product Admin 500 fixed,
- business-oriented Velzon navigation active,
- Home/Store/Admin login HTTP 200,
- public Home private imported-media refs = 0,
- no pending migration,
- clean Production worktree.

Fresh rollback backup for this Production baseline: `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-125848`.

## Existing business foundation
- StoreOrder/StoreOrderItem/StorePayment/StoreInvoice/Shipment/ReturnRequest,
- Coupon + VAT + packaging + shipping + order-weight calculation,
- ShippingMethod fixed/weight-rule pricing,
- StoreAddress + Iran Province/County/City,
- service Order/Quote/Payment + immutable PaymentLedgerEntry,
- mature payment request/callback/verify/idempotency architecture,
- filament purchasing/spools/movements,
- inventory reservation/movements,
- ProductionJob/MaterialUsage/CostEntry/BusinessFinanceDashboard,
- affiliate commission/payout/ledger,
- broad custom Django Admin.

## Phase50 deployed foundation
- `/admin/command-center/`,
- Product/imported Catalog Hero actions,
- Product contain-fit gallery/lightbox,
- Variant 2.0 size/build/package data and StoreOrderItem snapshots,
- Sales Profiles with `store.0035`,
- unified business-ordered Product edit workspace,
- safe imported-model/Hero public media resolution,
- mobile Hero, homepage SEO audit and Windows image dimensions,
- business-oriented Admin navigation,
- Product changelist 500 regression fix.

## Phase50.A.1G implementation
Owner visual QA of `bc7b97f` showed the remaining permanent Django `#changelist-filter` column made list pages cramped and visually legacy. Owner re-supplied `master.zip`; it was reviewed as Velzon Django Corporate 4.3.0 / Bootstrap 5.3.6.

Implemented final presentation layer:
- `static/admin/phase50-admin-console-v2.css`,
- `static/admin/phase50-admin-console-v2.js`,
- V2 assets loaded by `templates/admin/base.html`,
- default changelists are full-width,
- native Django filters move into an on-demand `فیلترها` drawer with backdrop/close/Escape/reset and active-filter count,
- Persian search/filter/action labels,
- card-based search, actions, result table and pagination,
- long change forms gain sticky horizontal section navigation and card fieldsets,
- existing ModelAdmin permissions/actions/query semantics stay authoritative,
- no schema migration.

Purchased Velzon vendor assets stay private/gitignored under `static/velzon_master/`; only project-owned adapters/integration code are committed to the public GitHub repository.

## Verification
GitHub Actions `Phase50 Product Admin Workspace CI` run `32955310832` PASS on code snapshot `3687d0922959fca53f2118be6dacd32639159346`:
- Python compile PASS,
- V2 JavaScript `node --check` PASS,
- Django check PASS,
- migration drift NONE,
- CI SQLite migrations PASS,
- Product and representative Admin HTTP/static regressions PASS.

## Immediate next work
1. Deploy the CI-tested Admin V2 snapshot from GitHub to Production using explicit verified `FETCH_HEAD`, fresh backup, no-migration gate, collectstatic and Passenger restart.
2. Owner Ctrl+F5 visual QA: Product list has no permanent Filter column; `فیلترها` opens only on demand; Product edit section navigator is present and usable.
3. Separate Product engagement phase: Favorite/Save + like/save/review/comment counters + verified-purchase buyer feedback rules with its own migration/tests/backup.
4. Continue Phase50.A.2 Shipping/Delivery → secure Store ZarinPal → Torob Product API v3 → accounting core.
