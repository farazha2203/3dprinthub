# 3DPrintHub — نقشه مادر پروژه، معماری، فازها و مسیر بعدی

> این فایل قبل از هر Phase/Hotfix/UI change/Migration/Sync/Deploy خوانده می‌شود. GitHub/Repository منبع اصلی حقیقت است.

**Repository:** `farazha2203/3dprinthub`  
**Branch توسعه:** `agent/phase49-3i18-operator-bulk-ai-rebuild`  
**Current Epic:** `Phase50 — Finance, Commerce & Admin Command Center`  
**Current Subphase:** `50.A.1C — Admin media integrity + mobile Hero + homepage SEO + Windows image dimensions`  
**Status:** `GITHUB CI TESTED / HOST READ-ONLY AUDIT + MANUAL QA REQUIRED`  
**Backend:** Django / Python  
**Production:** وضعیت واقعی Host باید قبل از Deploy بعدی با Read-only Audit تطبیق داده شود.

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
Repository includes StoreOrder/StorePayment/StoreInvoice, Coupon, VAT/packaging/shipping calculations, ShippingMethod weight rules, StoreAddress and Iran Province/County/City data, custom Order/Quote/Payment, immutable PaymentLedgerEntry, filament purchasing/inventory, ProductionJob/CostEntry, affiliate commissions/payouts/ledger and broad Django Admin coverage.

The service-payment path already has server-owned amounts, transaction locking, random callback identity, exact Authority matching, server-to-server verification and idempotent ledger behavior. These are preserved and reused rather than rebuilt.

## 5) Phase50 path
### 50.A.1 — Admin Storefront / Hero parity — CI TESTED
- `/admin/command-center/`,
- Product and imported Catalog add/remove Hero actions,
- 5-random / 10-random / deactivate-all Hero controls,
- Coupon, ShippingMethod, PricingSetting, StoreAddress and Iran location data surfaced,
- no destructive Hero changes.

### 50.A.1B — Product Gallery + Variant 2.0 — CI TESTED
- contain-fit Product viewer and thumbnail-to-main behavior,
- full-screen accessible lightbox,
- ProductVariant size/build-profile/packaging-weight/package-dimensions,
- StoreOrderItem matching snapshot columns,
- Variant identity expanded to size/build,
- Admin parity for new sellable fields,
- public Variant metadata endpoint,
- migration `store.0034_phase50_variant2_commerce`.

### 50.A.1C — Admin media / mobile / SEO / Windows dimensions — CI TESTED
- ImportedPrintAsset Admin preview never emits private `store/imported-models/...` working-media as a public URL,
- safe preview order: Product gallery match → Product main image → remote HTTP(S) source,
- mature Phase35 editable pricing/editorial Admin contracts preserved,
- imported image source dimensions visible in Admin,
- mobile Hero title/caption/CTA compact; very narrow screens hide description so Product image remains visible,
- existing homepage `meta_title/meta_description` remain canonical and have Admin SEO health/SERP/Hero Alt-title audit,
- Windows Product image cards show original `W × H px`,
- no new migration in this subphase,
- corrected CI run `32875771848` PASS on code snapshot `d74683cd54b18cc0f02c3c117515e1a34bc8ec83`.

### Production reconciliation gate — NOW
Owner screenshots show Phase50-era Admin UI on Production while earlier docs reported Phase50 undeployed, and `/admin/store/product/` returns 500. Before any deploy or migration:
- verify exact Host branch/HEAD/worktree,
- verify Django/Python runtime,
- verify MySQL vendor/name,
- verify `store.0034` migration state and migrate plan,
- obtain real runtime evidence for the Product Admin 500,
- create a fresh successful MySQL backup before any pending migration.

### 50.A.2 — Checkout & Delivery — NEXT AFTER CURRENT QA
- persist size/build/package snapshots at checkout,
- use effective product + packaging shipping weight,
- normalized carrier quote interface and immutable order quote snapshot,
- Post / Tipax / Mahex adapters only after current official API contract/credentials are verified,
- timeout/error fallback to mature ShippingMethod fixed/weight rules,
- Admin provider/fallback controls.

### 50.A.3 — Secure Store Payment
- reuse server-owned amount + request/callback/verify/idempotency model,
- strict trusted gateway-host allowlist,
- never collect/store card number, PIN or CVV,
- exact provider reference/Authority verification,
- reconciliation, audit and abuse controls.

### 50.A.4 — Torob
- official current Torob Product API v3,
- stable product/variant grouping,
- size/color/material mapping,
- price/availability and image-quality contract,
- pagination and stable unique IDs,
- order attribution/webhooks only after official contract verification.

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
- Phase50.A.1, A.1B and A.1C have relevant GitHub CI PASS,
- current Host state must be reconciled before any Production mutation,
- `store.0034` must not be assumed pending/applied until `showmigrations` and `migrate --plan` are read on the real MySQL environment,
- Windows source includes image dimensions but the immutable 8.8.1 EXE does not; next EXE version follows source smoke and rebuild.

## 7) Migration and integration safety
No Phase50 schema migration may reach Production until exact MySQL vendor/name, migration plan, successful fresh backup and rollback target are verified. No live carrier endpoint is introduced from guessed or unofficial contracts. Historical payment/ledger/order/inventory rows remain preserved and accounting/payment integrations must be additive and idempotent.
