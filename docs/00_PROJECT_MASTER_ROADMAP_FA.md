# 3DPrintHub — نقشه مادر پروژه، معماری، فازها و مسیر بعدی

> این فایل قبل از هر Phase/Hotfix/UI change/Migration/Sync/Deploy خوانده می‌شود. GitHub/Repository منبع اصلی حقیقت است.

**Repository:** `farazha2203/3dprinthub`  
**Branch توسعه:** `agent/phase49-3i18-operator-bulk-ai-rebuild`  
**Current Epic:** `Phase50 — Finance, Commerce & Admin Command Center`  
**Current Subphase:** `50.A.1 — Admin Storefront / Hero parity`  
**Status:** `GITHUB CI TESTED / MANUAL ADMIN QA REQUIRED`  
**Backend:** Django / Python  
**Production:** Phase49 healthy by owner visual QA; Phase50 undeployed.

## 1) قانون مادر
`READ DOCS → VERIFY REAL STATE → CHECK PREVIOUS ERRORS → IMPLEMENT ON GITHUB → CI/LOCAL GATE → MANUAL QA → EXPLICIT OWNER APPROVAL → HOST READ-ONLY VERIFY → BACKUP → DEPLOY FROM GITHUB → PRODUCTION VERIFICATION → UPDATE DOCS`

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
Catalog/Product/Hero/SEO/Bridge release is operational. Product-owned public media is the Production ownership contract; imported Catalog working-media remains private. Phase50 must not rewrite healthy Catalog architecture without a verified defect.

## 4) Existing commerce/finance foundation
Repository already includes StoreOrder/StorePayment/StoreInvoice, Coupon, VAT/packaging/shipping calculations, ShippingMethod weight rules, StoreAddress and Iran Province/County/City data, custom Order/Quote/Payment, immutable PaymentLedgerEntry, filament purchasing/inventory, ProductionJob/CostEntry, affiliate commissions/payouts/ledger and broad Django Admin coverage.

The service-payment path already has server-owned amounts, transaction locking, random callback identity, exact Authority matching, server-to-server verification and idempotent ledger behavior. These are preserved and reused rather than rebuilt.

## 5) Phase50 path
### 50.A.1 — Admin Storefront / Hero parity — CI TESTED
- `/admin/command-center/` includes Storefront & Checkout alongside Sales/Treasury/Accounting/Purchasing/Inventory,
- Product and imported Catalog assets can be added to or removed from the homepage Hero through bulk Admin actions,
- Hero Admin provides 5-random, 10-random and non-destructive deactivate-all controls,
- random selection uses active Product-backed assets with public-renderable media,
- existing manually edited Hero copy is preserved,
- Coupon, ShippingMethod, PricingSetting, StoreAddress and Iran location data are directly surfaced,
- no migration.

### 50.A.2 — Checkout & Delivery — NEXT
- preserve existing coupon/VAT/packaging/shipping totals,
- add explicit package weight and dimensions to shipping quote inputs,
- normalized carrier quote interface and immutable order quote snapshot,
- Post / Tipax / Mahex adapters only after current official API contract/credentials are verified,
- timeout/error fallback to mature ShippingMethod fixed/weight rules.

### 50.A.3 — Secure Store Payment
- reuse server-owned amount + request/callback/verify/idempotency model,
- strict trusted gateway-host allowlist,
- never collect/store card number, PIN or CVV,
- exact provider reference/Authority verification,
- reconciliation, audit and abuse controls,
- Production HTTPS/HSTS/Secure-cookie/header verification.

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

## 6) Current release gate
- GitHub CI for 50.A.1 has passed compile, Django check, no-migration dry-run and focused Admin regressions on code snapshot `7c8714b5715cd00900a76b99097823266251d4a2`.
- manual desktop/mobile Admin visual/operation QA remains required.
- Production remains untouched for Phase50.

## 7) Migration and integration safety
No Phase50 schema migration may reach Production until exact MySQL vendor/name, migration plan, successful backup and rollback target are verified. No live carrier endpoint is introduced from guessed or unofficial contracts. Historical payment/ledger/order/inventory rows remain preserved and accounting/payment integrations must be additive and idempotent.
