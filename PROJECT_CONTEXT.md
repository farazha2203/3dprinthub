# PROJECT_CONTEXT — 3DPrintHub

Updated: 2026-08-26
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Epic: `Phase50 — Finance, Commerce & Admin Command Center`
Current Subphase: `50.A.1E — Unified Product Admin Workspace`
Status: `GITHUB CI TESTED / PRODUCTION DEPLOY NEXT`

## Operating rule
GitHub/Repository is permanent source of truth.
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI/LOCAL GATE → MANUAL QA → OWNER APPROVAL → HOST READ-ONLY VERIFY → BACKUP/DEPLOY/VERIFY`.

No permanent Production source edit. Dirty Local/Host stops for inspection. New commerce/finance work is additive and preserves mature orders, payments, inventory and Catalog history.

## Canonical paths
Windows project: `D:\projects\3DPrintHub`
Windows venv: `D:\projects\3DPrintHub\.venv`
Windows Django DB: `D:\projects\3DPrintHub\db.sqlite3`
Production project: `/home/sfkilvrs/3dprinthub`
Production venv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`
Production DB: MySQL `sfkilvrs_EmiAdmin_3dprinthub`

## Production verified baseline
Owner deployed Phase50.A.1C at commit `5c5c5e1e141fd3ff8df3c079abc55e4593feb41f`.
`store.0034_phase50_variant2_commerce` is applied; Home/Store/Admin/Product Admin/Imported Asset Admin/Hero Admin returned HTTP 200; public Home emitted no private imported-media references. Rollback backup exists at `/home/sfkilvrs/3dprinthub-deploy-backups/20260825-205719`.
Repository state does not yet record `store.0035_phase50_sales_profiles` as Production-applied.

## Existing business foundation
- StoreOrder/StoreOrderItem/StorePayment/StoreInvoice/Shipment/ReturnRequest,
- Coupon discount + VAT + packaging + shipping + order-weight calculation,
- ShippingMethod fixed/weight-rule pricing,
- StoreAddress and Iran Province/County/City reference data,
- custom service Order/Quote/Payment and immutable PaymentLedgerEntry,
- mature online payment request/callback/verify/idempotency architecture,
- filament purchasing/spools/movements,
- inventory reservation/movements,
- ProductionJob/MaterialUsage/CostEntry/BusinessFinanceDashboard,
- affiliate commission/payout/ledger,
- broad custom Admin.

## Phase50 deployed foundation through 50.A.1C
- authenticated `/admin/command-center/`,
- Product/Imported Catalog Hero actions and 5/10 random/deactivate-all,
- Product contain-fit gallery + thumbnail switch + fullscreen lightbox,
- Variant 2.0 size/build/packaging fields,
- StoreOrderItem snapshot columns,
- migration `store.0034` applied,
- imported-model safe Admin preview,
- compact mobile Hero,
- homepage SEO Admin audit,
- Windows source image dimensions.

## Phase50.A.1D GitHub implementation
- Product selection mode: list / size / weight / build / size→build / build→size.
- ProductVariant profile name/key/default/order.
- profile key permits otherwise-identical material/color/size/build profiles to differ in weight, print time, pricing and shipping.
- Admin copy-profile action clones current mature Variant settings.
- Hero Studio Admin endpoints resolve Product-owned public media or safe remote source fallback.
- migration `store.0035_phase50_sales_profiles`.
- CI run `32879712980` PASS.

## Phase50.A.1E GitHub implementation
The Product change page is now one business-oriented workspace. Exact primary section order:
`اطلاعات کالا → تصاویر → فروش و موجودی → پروفایل‌ها و سایز/وزن → قیمت‌گذاری → ارسال و بسته‌بندی → SEO → اسلایدر صفحه اول → منبع و لایسنس → همگام‌سازی ویندوز`.

Implementation contract:
- no duplicate Product/SEO/Catalog/Profile state,
- mature ProductImage and ProductVariant inlines remain,
- sales profile copy/edit/default/order remain available through the mature Variant Admin,
- pricing summary links to ProductCatalogProfile pricing,
- shipping summary reads existing Variant 2.0 weight/package fields,
- Product SEO exposes real focus/meta/canonical/robots/OpenGraph/schema plus SERP preview,
- Hero section links slider controls/Hero Studio,
- source/license and Windows sync surface existing ProductCatalogProfile metadata,
- no new schema migration.

## Verification
`Phase50 Product Admin Workspace CI` run `32941662288` PASS on code snapshot `f34eaa3bbad965b2092279291ff8adf93f3d908e`: compile, Django check, migration drift, SQLite migration apply through `store.0035`, and focused Product Admin regressions all PASS.

An earlier run `32941533091` failed only a stale regression-test assumption about a `seo_status` list column. Mature Admin behavior was preserved; the test was corrected and the incident is recorded as ERR-50-006.

## Immediate next work
1. Production read-only verify current HEAD/worktree/MySQL and actual `0035` state.
2. Fresh backup; deploy current approved GitHub snapshot; apply only `store.0035` if pending after exact migration-plan inspection.
3. Manual QA unified Product Admin + Sales Profiles + Hero Studio media.
4. Build storefront profile selector and immutable checkout snapshots.
5. Continue Shipping/Delivery → secure Store ZarinPal → Torob Product API v3 → accounting core.
