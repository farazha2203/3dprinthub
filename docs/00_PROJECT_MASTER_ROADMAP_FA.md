# 3DPrintHub — نقشه مادر پروژه، معماری، فازها و مسیر بعدی

> این فایل قبل از هر Phase/Hotfix/UI change/Migration/Sync/Deploy خوانده می‌شود. GitHub/Repository منبع اصلی حقیقت است.

**Repository:** `farazha2203/3dprinthub`  
**Branch توسعه:** `agent/phase49-3i18-operator-bulk-ai-rebuild`  
**Current Epic:** `Phase50 — Finance, Commerce & Admin Command Center`  
**Current Subphase:** `50.A.1E — Unified Product Admin Workspace`  
**Status:** `GITHUB CI TESTED / PRODUCTION DEPLOY NEXT`  
**Backend:** Django / Python

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
Catalog/Product/Hero/SEO/Bridge release is operational. Product-owned public media is the Production ownership contract; imported Catalog working-media remains private.

## 4) Phase50 current Production baseline
Owner deployment verified Phase50.A.1C at commit `5c5c5e1e141fd3ff8df3c079abc55e4593feb41f`.
`store.0034_phase50_variant2_commerce` is applied on Production MySQL; Home/Store/Admin/Product Admin/Imported Asset Admin/Hero Admin returned HTTP 200; rollback backup exists at `/home/sfkilvrs/3dprinthub-deploy-backups/20260825-205719`.
Repository state does not yet record `store.0035_phase50_sales_profiles` as Production-applied.

## 5) Phase50 path
### 50.A.1 — Admin Storefront / Hero parity — DEPLOYED
- `/admin/command-center/`, Product/imported Catalog add/remove Hero,
- 5-random / 10-random / deactivate-all Hero controls,
- Coupon, ShippingMethod, PricingSetting, StoreAddress and Iran location data surfaced.

### 50.A.1B — Product Gallery + Variant 2.0 — DEPLOYED
- contain-fit Product viewer + thumbnail switching + fullscreen lightbox,
- size/build/packaging weight/package dimensions,
- StoreOrderItem matching snapshots,
- migration `store.0034` applied,
- Variant Admin and metadata endpoint.

### 50.A.1C — Admin media / mobile / SEO / Windows dimensions — DEPLOYED
- imported-model Admin avoids private working-media previews,
- mobile Hero compacted,
- homepage SEO operator audit,
- Windows source shows image pixel dimensions.

### 50.A.1D — Sales Profiles + Hero Admin Public Media — GITHUB CI TESTED / PRODUCTION GATE REQUIRED
- Product selection mode: full list / size / weight / build / size→build / build→size,
- ProductVariant profile name/key/default/order,
- profile identity allows same material/color/size/build with distinct weight/time/price profiles,
- Admin copy-profile action duplicates the mature Variant as a starting point,
- Variant endpoint exposes profile selector, weight, time, price, packaging and shipping metadata,
- Hero Studio change page product/album JSON endpoints resolve public Product media or remote source media and never private `store/imported-models/...` paths,
- migration `store.0035_phase50_sales_profiles`,
- CI run `32879712980` PASS.

### 50.A.1E — Unified Product Admin Workspace — GITHUB CI TESTED / NEXT DEPLOY
- Product change page follows the exact operator sequence:
  `اطلاعات کالا → تصاویر → فروش و موجودی → پروفایل‌ها و سایز/وزن → قیمت‌گذاری → ارسال و بسته‌بندی → SEO → اسلایدر صفحه اول → منبع و لایسنس → همگام‌سازی ویندوز`,
- Product gallery and Variant/Profile inlines stay mature/authoritative,
- pricing/slider/license/sync are surfaced from ProductCatalogProfile rather than duplicated,
- actual Product SEO fields plus SERP preview are consolidated in the Product page,
- shipping/package completeness summarizes existing Variant 2.0 data,
- no new schema migration,
- `Phase50 Product Admin Workspace CI` run `32941662288` PASS on code snapshot `f34eaa3bbad965b2092279291ff8adf93f3d908e`.

### 50.A.2 — Checkout & Delivery — NEXT AFTER ADMIN/0035 PRODUCTION QA
- storefront profile-aware selector,
- persist selected profile/size/build/package snapshots,
- effective product + packaging shipping weight,
- carrier quote contract + immutable order snapshot,
- Post/Tipax/Mahex only after current official contract/credentials verification,
- fallback to mature ShippingMethod rules.

### 50.A.3 — Secure Store Payment
- reuse server-owned amount + request/callback/verify/idempotency,
- strict trusted gateway-host allowlist,
- never collect/store card/PIN/CVV,
- exact provider reference/Authority verification,
- reconciliation and audit.

### 50.A.4 — Torob
- current Torob Product API v3,
- stable product/profile grouping,
- size/color/material/weight mapping,
- price/availability/image-quality contract,
- attribution/webhooks only after verified official contract.

### 50.B — Accounting Core
کل / معین / تفصیلی, fiscal periods, balanced vouchers, immutable posting/reversal, party/subledger and numbering.

### 50.C — Treasury
Bank/cash accounts, receipts/payments, allocations, refunds and reconciliation.

### 50.D — Purchasing
Supplier master, purchase orders/invoices/receiving, payables and returns.

### 50.E — Sales Accounting
Store/service receivables, allocations, tax/discount/shipping, returns/refunds/credit notes.

### 50.F — Reports & Close
GL/subledger, trial balance, statements, AR/AP aging, cashflow, profitability, VAT/tax and close audit.

## 6) Current release gate
- 50.A.1D + 50.A.1E code/regression gates are green on GitHub.
- `store.0035` must be verified against actual Production before any schema mutation.
- before Production mutation verify exact Host branch/HEAD/worktree, MySQL vendor/name, actual `0034`/`0035` state, fresh backup and migration plan.
- next Windows EXE version follows source/manual smoke; immutable 8.8.1 remains the released Windows build until then.

## 7) Migration and integration safety
No Phase50 schema migration reaches Production without exact MySQL vendor/name, migration plan, successful fresh backup and rollback target. No live carrier/gateway endpoint is guessed. Historical payment/ledger/order/inventory rows remain preserved and integrations stay additive/idempotent.
