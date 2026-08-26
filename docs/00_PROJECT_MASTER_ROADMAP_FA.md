# 3DPrintHub — نقشه مادر پروژه، معماری، فازها و مسیر بعدی

> این فایل قبل از هر Phase/Hotfix/UI change/Migration/Sync/Deploy خوانده می‌شود. GitHub/Repository منبع اصلی حقیقت است.

**Repository:** `farazha2203/3dprinthub`  
**Branch توسعه:** `agent/phase49-3i18-operator-bulk-ai-rebuild`  
**Current Epic:** `Phase50 — Finance, Commerce & Admin Command Center`  
**Current Subphase:** `50.A.1G — Velzon Operator Surface V2`  
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
- Assetهای خریداری‌شده/private پوسته و فونت در Repository عمومی منتشر نمی‌شوند؛ فقط adapter/integration اختصاصی پروژه Commit می‌شود.

## 2) مسیرهای ثبت‌شده
Windows: `D:\projects\3DPrintHub`; venv: `D:\projects\3DPrintHub\.venv`; Local Django DB: `D:\projects\3DPrintHub\db.sqlite3`.

Production: `/home/sfkilvrs/3dprinthub`; venv `/home/sfkilvrs/virtualenv/3dprinthub/3.12`; MySQL `sfkilvrs_EmiAdmin_3dprinthub`; static `/home/sfkilvrs/public_html/static`; media `/home/sfkilvrs/public_html/media`; private media `/home/sfkilvrs/3dprinthub/private_media`.

## 3) Phase49 completed baseline
Catalog/Product/Hero/SEO/Bridge release is operational. Product-owned public media is the Production ownership contract; imported Catalog working-media remains private.

## 4) Current Production baseline
Production verified application commit: `bc7b97f9c63432b8105f52f61cf5cdae1369689b`.

Verified:
- MySQL `sfkilvrs_EmiAdmin_3dprinthub`,
- `store.0034_phase50_variant2_commerce` applied,
- `store.0035_phase50_sales_profiles` applied,
- Product Admin real-row changelist render HTTP 200,
- Product Admin 500 fixed,
- business-oriented Admin navigation active,
- Home/Store/Admin login HTTP 200,
- Home private imported-media refs = 0,
- no pending migration,
- Production worktree clean,
- fresh rollback backup `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-125848`.

## 5) Phase50 path
### 50.A.1 — Admin Storefront / Hero parity — DEPLOYED
Command center, Product/imported Catalog Hero controls, Coupon/Shipping/Pricing/address surfaces.

### 50.A.1B — Product Gallery + Variant 2.0 — DEPLOYED
Product viewer/lightbox, Variant size/build/package data, StoreOrderItem snapshots, `store.0034` applied.

### 50.A.1C — Admin media / mobile / SEO / Windows dimensions — DEPLOYED
Safe imported-model previews, mobile Hero, homepage SEO audit, Windows image dimensions.

### 50.A.1D — Sales Profiles + Hero Admin Public Media — DEPLOYED
Sales profile selection modes, profile key/default/order/copy action, safe Hero Admin media, `store.0035` applied.

### 50.A.1E — Unified Product Admin Workspace — DEPLOYED
Product change page follows:
`اطلاعات کالا → تصاویر → فروش و موجودی → پروفایل‌ها و سایز/وزن → قیمت‌گذاری → ارسال و بسته‌بندی → SEO → اسلایدر صفحه اول → منبع و لایسنس → همگام‌سازی ویندوز`.
Mature Product/ProductCatalogProfile/ProductVariant/SEO state remains authoritative.

### 50.A.1F — Business Admin Navigation + Product Admin 500 Fix — PRODUCTION VERIFIED
- fixed real Product changelist 500,
- added real-row render regression,
- business navigation groups Store, Orders, Finance/Coupons, Production/Inventory, Windows/Catalog, Homepage, Content, Engagement, Support, Affiliate and System,
- Production verification at `bc7b97f...` PASS,
- no migration.

### 50.A.1G — Velzon Operator Surface V2 — GITHUB CI TESTED / DEPLOY NEXT
Owner visual QA rejected the remaining permanent Django Filter column and cramped changelist layout. Owner re-supplied `master.zip`; verified theme reference is Velzon Django Corporate `4.3.0` / Bootstrap `5.3.6`.

Implementation:
- full-width changelists,
- native Django filters preserved but moved to on-demand `فیلترها` drawer/off-canvas,
- backdrop/close/Escape/reset + active-filter count,
- Persian search/filter/action presentation,
- card-based search, bulk actions, result table and pagination,
- sticky table headers + controlled table overflow,
- long Product/change forms gain sticky section navigator + card fieldsets,
- responsive/dark-mode integration,
- no schema migration.

CI:
- `Phase50 Product Admin Workspace CI` run `32955310832` PASS,
- runtime code snapshot `3687d0922959fca53f2118be6dacd32639159346`,
- Python compile PASS,
- V2 JavaScript `node --check` PASS,
- Django check PASS,
- migration drift NONE,
- CI SQLite migrations PASS,
- focused Admin HTTP/static regressions PASS.

### Product Engagement — NEXT AFTER ADMIN V2 QA
- preserve ProductLike/ProductComment/ProductReview,
- add real Favorite/Save contract if absent,
- Product like/save/review/comment counters in Product/Admin,
- buyer-feedback review/comment requires qualifying paid/purchased Product,
- separate migration/tests/Production backup/rollback.

### 50.A.2 — Checkout & Delivery
- storefront profile-aware selector,
- selected profile/size/build/package snapshots,
- effective shipping weight + parcel dimensions,
- normalized carrier quote + immutable order snapshot,
- Post/Tipax/Mahex only with verified official contracts/credentials,
- mature ShippingMethod fallback.

### 50.A.3 — Secure Store Payment
Server-owned amount, request/callback/verify/idempotency, strict trusted gateway host allowlist, exact Authority/provider reference, never card/PIN/CVV storage.

### 50.A.4 — Torob
Torob Product API v3, stable Product/Profile identity, size/color/material/weight, price/availability/image quality and verified attribution contract.

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
- 50.A.1G runtime is CI green.
- current Production must remain clean at `bc7b97f...` until deploy gate begins.
- because of `ERR-50-007`, Production must verify live branch SHA and explicitly fetch the branch to `FETCH_HEAD`; do not trust stale `origin/<branch>`.
- before mutation: verify exact root/branch/HEAD/MySQL, no migration-file delta, fresh backup and rollback target.
- after ff-only deploy: Django check, migration drift/plan, collectstatic, Passenger restart, HTTP/static/Product Admin/private-media verification, then owner Ctrl+F5 visual QA.
- immutable Windows release remains 8.8.1 until a separately tested/released EXE replaces it.

## 7) Migration and integration safety
No Phase50 schema migration reaches Production without exact MySQL vendor/name, migration plan, successful fresh backup and rollback target. No live carrier/gateway endpoint is guessed. Historical payment/ledger/order/inventory rows remain preserved and integrations stay additive/idempotent.
