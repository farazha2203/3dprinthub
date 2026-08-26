# Phase50 — Finance, Commerce & Admin Command Center

Updated: 2026-08-26
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Subphase: `50.A.1E — Unified Product Admin Workspace`
Status: `GITHUB CI TESTED / PRODUCTION DEPLOY REQUIRED`
Production baseline: `5c5c5e1e141fd3ff8df3c079abc55e4593feb41f`, MySQL `store.0034` applied. Repository state does not yet record `store.0035` as Production-applied.

## Owner request
Complete storefront/Admin commerce before accounting core. The Product Admin must be one professional operator workspace ordered exactly as:
`اطلاعات کالا | تصاویر | فروش و موجودی | پروفایل‌ها و سایز/وزن | قیمت‌گذاری | ارسال و بسته‌بندی | SEO | اسلایدر صفحه اول | منبع و لایسنس | همگام‌سازی ویندوز`.

Current surrounding priorities remain reusable sales profiles, Hero Studio media integrity, shipping/VAT/coupon, secure ZarinPal and Torob.

## Preserved foundation
- Product/Catalog/Bridge/Hero public media ownership remains Product-owned.
- Imported Catalog working-media remains private.
- Product, ProductCatalogProfile and ProductVariant remain authoritative; the Admin workspace does not create duplicate commercial/SEO/sync state.
- StoreOrder/StorePayment/StoreInvoice and mature coupon/VAT/packaging/shipping calculations remain authoritative.
- customer StoreAddress plus Iran Province/County/City remain intact.
- mature service-payment request/callback/verify/idempotency engine is reused later for Store payment.
- no direct Production source edits.

## Deployed baseline through 50.A.1C
- `/admin/command-center/`, Product/imported Asset Hero actions and 5/10 random/deactivate-all.
- Product contain-fit main viewer, thumbnail swap and fullscreen lightbox.
- Variant 2.0 size/build/packaging fields and StoreOrderItem snapshots.
- migration `store.0034_phase50_variant2_commerce` applied on Production.
- imported Admin safe preview, mobile Hero compaction, homepage SEO audit, Windows source image dimensions.

## 50.A.1D — Sales Profiles + Hero Admin Public Media
Implemented/GitHub CI tested:
- Product `sales_profile_selection_mode` and optional selector label,
- ProductVariant profile name/key/default/order,
- profile identity supports same material/color/size/build with different weight/time/price profiles,
- copy-profile Admin action,
- Hero Studio Product/album JSON endpoints resolve Product-owned public media or safe remote HTTP(S) source media,
- migration `store.0035_phase50_sales_profiles`.

GitHub Actions `Phase50 Sales Profiles Hero Admin CI` run `32879712980` PASS on snapshot `405d2c1daa85828d1a0dc68210d201c85b6db7ba`.

## 50.A.1E — Unified Product Admin Workspace
### Requested Delta
Present one Product change page with the operator's exact business sequence while retaining the mature underlying models, actions, inlines and SEO behavior.

### Implemented
- `store/phase50_product_admin_workspace.py` is installed as the final additive Product Admin composition boundary.
- Exact main sections:
  1. اطلاعات کالا
  2. تصاویر
  3. فروش و موجودی
  4. پروفایل‌ها و سایز/وزن
  5. قیمت‌گذاری
  6. ارسال و بسته‌بندی
  7. SEO
  8. اسلایدر صفحه اول
  9. منبع و لایسنس
  10. همگام‌سازی ویندوز
- Collapsed `آمار و وضعیت` remains an auxiliary section for view/created/updated metadata.
- Product gallery and ProductVariant inlines are preserved and relabeled for operator clarity.
- Sales Profile section exposes selection mode and links/summarizes profile management; copy-profile remains on ProductVariant Admin.
- Pricing section keeps Product fixed-price fields and links to existing ProductCatalogProfile pricing strategy/min/max rather than duplicating pricing data.
- Shipping section summarizes existing profile-level product/package/shipping weight and parcel dimensions; no live carrier behavior added here.
- SEO section exposes the real Product focus keyword, meta title/description, canonical, robots, schema and OpenGraph fields plus existing SERP preview.
- Hero section links the existing ProductCatalogProfile slider controls and Hero Studio.
- Source/license section combines Product source fields with ProductCatalogProfile commercial-license status.
- Windows sync section shows Desktop ID, sync revision, last modified source and last sync timestamp from ProductCatalogProfile.
- no new migration in 50.A.1E.

### Regression gate
First CI run `32941533091` reached compile, Django check, migration drift and SQLite migration apply, then failed only because the test incorrectly expected a stale `seo_status` list column.
The mature Admin was preserved; the bad test assumption was corrected.

Corrected GitHub Actions `Phase50 Product Admin Workspace CI` run `32941662288` PASS on snapshot `f34eaa3bbad965b2092279291ff8adf93f3d908e`:
- compile PASS,
- Django check PASS with known warnings only,
- migration drift NONE,
- SQLite migrations through `store.0035` PASS,
- unified Product Admin regressions PASS.

### Production gate
1. verify exact Production HEAD/worktree and current remote HEAD,
2. verify MySQL vendor/name and actual `0034`/`0035` state,
3. if `0035` is pending: fresh successful MySQL backup + exact migration plan + rollback commit,
4. deploy committed GitHub snapshot only,
5. apply only approved pending migration(s), collectstatic and Passenger restart,
6. manual QA Product unified sections, Variant/Profile inline, pricing/SEO/Hero/source/sync links and Hero Studio images.

## 50.A.2 — Checkout & Delivery — next after Admin/0035 Production QA
- profile-aware selector on Product page,
- persist chosen profile/size/build/package snapshots,
- effective product + packaging shipping weight,
- normalized carrier quote + immutable order snapshot,
- Post/Tipax/Mahex only after verified current official API credentials/contracts,
- preserve ShippingMethod fallback.

## 50.A.3 — Secure Store ZarinPal
Reuse server-owned amount/currency, random callback identity, exact Authority, server-to-server verify and idempotency. Add trusted redirect host allowlist; never capture/store card/PIN/CVV.

## 50.A.4 — Torob
Implement official current Torob Product API v3 using stable Product/profile identifiers, size/color/material/weight, price/availability and image-quality contract.

## Remaining Phase50
- 50.B Accounting core: کل/معین/تفصیلی, fiscal periods, balanced vouchers, immutable posting/reversal.
- 50.C Treasury: bank/cash, receipts/payments, allocations/refunds/reconciliation.
- 50.D Purchasing: suppliers, purchase orders/invoices/receiving/payables/returns.
- 50.E Sales accounting: receivables, payment allocation, tax/discount/shipping, credit notes.
- 50.F Reports/close: GL/subledger, trial balance, aging, cashflow, profitability, VAT/tax, fiscal close.

## Must not touch
- no direct Production source edit,
- no public exposure of imported working-media,
- no destructive historical order/payment/ledger reset,
- no guessed carrier/gateway endpoint,
- no Production migration without exact DB/plan/backup/rollback verification.
