# 3DPrintHub — نقشه مادر پروژه، معماری، فازها و مسیر بعدی

> این فایل قبل از هر Phase/Hotfix/UI change/Migration/Sync/Deploy خوانده می‌شود. GitHub/Repository منبع اصلی حقیقت است.

**Repository:** `farazha2203/3dprinthub`  
**Branch توسعه:** `agent/phase49-3i18-operator-bulk-ai-rebuild`  
**Current Epic:** `Phase50 — Finance, Commerce & Admin Command Center`  
**Current Subphase:** `50.A — Admin Command Center completeness`  
**Status:** `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA REQUIRED`  
**Backend:** Django / Python  
**Production:** Phase49 healthy by owner visual QA; Phase50 undeployed.

## 1) قانون مادر
`READ DOCS → VERIFY REAL STATE → CHECK PREVIOUS ERRORS → IMPLEMENT ON GITHUB → WINDOWS PULL --FF-ONLY → LOCAL AUTOMATED GATE → MANUAL QA → EXPLICIT OWNER APPROVAL → HOST READ-ONLY VERIFY → BACKUP → DEPLOY FROM GITHUB → PRODUCTION VERIFICATION → UPDATE DOCS`

قواعد ثابت:
- Mature behavior با Extend/Patch/Wrap اصلاح می‌شود.
- تغییر جدید حق خراب‌کردن مسیر سالم قبلی را ندارد.
- Bugfix بدون Regression Test کامل نیست.
- Source دائمی روی Production ویرایش نمی‌شود.
- Dirty Local/Host = STOP/INSPECT؛ reset/stash/delete ممنوع.
- Secret در Git/log/chat ذخیره نمی‌شود.
- SHA ثابت Chat مرجع Branch متحرک نیست؛ Remote بعد از fetch مرجع است.

## 2) مسیرهای ثبت‌شده
Windows: `D:\projects\3DPrintHub`; venv: `D:\projects\3DPrintHub\.venv`; Local Django DB: `D:\projects\3DPrintHub\db.sqlite3`.

Production: `/home/sfkilvrs/3dprinthub`; venv `/home/sfkilvrs/virtualenv/3dprinthub/3.12`; MySQL `sfkilvrs_EmiAdmin_3dprinthub`; static `/home/sfkilvrs/public_html/static`; media `/home/sfkilvrs/public_html/media`; private media `/home/sfkilvrs/3dprinthub/private_media`.

## 3) Phase49 completed baseline
Catalog/Product/Hero/SEO/Bridge release is operational. Product-owned public media is the production ownership contract; imported Catalog working-media remains private. Phase50 must not reopen or rewrite healthy Catalog architecture without a new verified defect.

## 4) Existing commerce/finance foundation
Repository already includes StoreOrder/StorePayment/StoreInvoice, custom Order/Quote/Payment, immutable PaymentLedgerEntry, filament purchasing/inventory, ProductionJob/CostEntry, affiliate commissions/payouts/ledger and broad Django Admin coverage.

These are operational modules, not yet a complete double-entry accounting system.

## 5) Phase50 path
### 50.A — Admin Command Center
Business-oriented `/admin/command-center/`, explicit Sales/Treasury/Accounting/Purchasing/Inventory groups, permission-aware links, operational counters, sidebar shortcut and safe ModelAdmin browsing ergonomics. NO migration.

### 50.B — Accounting Core
- کدینگ کل / معین / تفصیلی,
- دوره مالی,
- سند حسابداری دوطرفه,
- posting/reversal immutable,
- subledger party references,
- numbering/integrity rules.

### 50.C — Treasury
Bank/cash accounts, generic receipts/payments, allocation, refunds and reconciliation.

### 50.D — Purchasing
Supplier master, general purchase orders/invoices/lines, payables and returns.

### 50.E — Sales Accounting
Normalize Store and service sales into receivables/accounting events, payment allocation, tax/discount/shipping and credit notes.

### 50.F — Reports & Close
General/subledger, trial balance, statements, AR/AP aging, cashflow, profitability, tax/VAT and close audit.

## 6) Current Release Gate
1. Windows clean worktree.
2. live fetch/prune + ff-only pull; Local HEAD == Remote HEAD.
3. `manage.py check`.
4. `makemigrations --check --dry-run` with NO changes for 50.A.
5. `manage.py test website.test_phase50a_admin_command_center -v 2`.
6. manual `/admin/` + `/admin/command-center/` QA.
7. owner approval before any Host deploy.

## 7) Financial migration safety
No Phase50.B+ migration may reach Production until exact MySQL vendor/name, pending migration plan, `mysqldump` backup and rollback target are verified. Historical payment/ledger/order/inventory rows are preserved; accounting integration is additive and idempotent.
