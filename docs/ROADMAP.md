# PROJECT ROADMAP

Updated: 2026-08-26
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Epic: `Phase50 — Finance, Commerce & Admin Command Center`
Current Phase: `50.A.1E — Unified Product Admin Workspace`
Status: `GITHUB CI TESTED / PRODUCTION DEPLOY NEXT`

## Permanent delivery order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI/LOCAL TEST → OWNER QA → HOST READ-ONLY VERIFY → BACKUP → DEPLOY FROM GITHUB → PRODUCTION VERIFY → DOCUMENT`

## Phase49 closeout baseline
Structured Product/Catalog/Hero/SEO/Bridge is operational. Product-owned public media remains the Production contract; imported Catalog working-media is not a public namespace.

## Phase50.A — Admin and commerce operational completeness
### 50.A.1 Admin Storefront / Hero parity — DEPLOYED
- `/admin/command-center/`,
- Product/imported-asset add/remove Hero,
- Hero 5-random / 10-random / deactivate-all,
- Coupon, ShippingMethod, PricingSetting, StoreAddress and Iran location Admin links.

### 50.A.1B Product Gallery + Variant 2.0 — DEPLOYED
- contain-fit Product viewer + thumbnail swap + fullscreen lightbox,
- size/build/packaging weight and parcel dimensions,
- StoreOrderItem commerce snapshots,
- migration `store.0034_phase50_variant2_commerce` applied on Production,
- Variant Admin and public variant metadata endpoint.

### 50.A.1C Admin media / mobile / SEO / Windows dimensions — DEPLOYED
- ImportedPrintAsset Admin avoids private working-media previews,
- safe Product-owned public image resolution,
- mature imported-model editing preserved,
- mobile Hero compacted,
- homepage SEO Admin audit added,
- Windows source image dimensions added.

### 50.A.1D Sales Profiles + Hero Admin Public Media — GITHUB CI TESTED / PRODUCTION GATE REQUIRED
- Product profile selection: list / size / weight / build / size→build / build→size,
- ProductVariant profile name/key/default/order,
- copy-profile Admin action,
- Hero Studio JSON uses Product-owned public media or safe remote source fallback,
- migration `store.0035_phase50_sales_profiles`.

### 50.A.1E Unified Product Admin Workspace — GITHUB CI TESTED / NEXT DEPLOY
- Product change page follows the exact business sequence:
  `اطلاعات کالا → تصاویر → فروش و موجودی → پروفایل‌ها و سایز/وزن → قیمت‌گذاری → ارسال و بسته‌بندی → SEO → اسلایدر صفحه اول → منبع و لایسنس → همگام‌سازی ویندوز`,
- mature Product fields and SEO fields remain authoritative,
- gallery and Variant/Profile inlines are preserved rather than replaced,
- operator summaries/links expose Product Catalog Profile pricing, Hero, commercial license and Windows sync without duplicating state,
- no schema migration added,
- `Phase50 Product Admin Workspace CI` run `32941662288` PASS on snapshot `f34eaa3bbad965b2092279291ff8adf93f3d908e`.

### 50.A.2 Checkout & Delivery — NEXT AFTER ADMIN/0035 PRODUCTION QA
- render profile-aware selector UI on Product page,
- persist chosen profile/size/build/package snapshots at checkout,
- use effective product + packaging shipping weight,
- parcel dimensions / insured value,
- normalized carrier quote + immutable order snapshot,
- Post / Tipax / Mahex only with verified official contracts/credentials,
- fallback to mature ShippingMethod rules.

### 50.A.3 Secure Store ZarinPal
Reuse mature server-owned amount, callback identity, Authority matching, server-to-server verify, idempotency and audit. Add trusted redirect-host allowlist and never collect/store card/PIN/CVV.

### 50.A.4 Torob
Torob Product API v3, stable product/profile grouping, size/color/material/weight mapping, price/availability, image-quality guards and official order attribution contract.

## Phase50.B — Accounting foundation
Chart of accounts کل/معین/تفصیلی, fiscal periods, balanced vouchers, immutable posting/reversal, party/subledger and numbering.

## Phase50.C — Treasury
Bank/cash, receipts/payments, allocations, refunds and reconciliation.

## Phase50.D — Purchasing & payables
Supplier master, purchase orders/invoices/receiving, payables and returns.

## Phase50.E — Sales & receivables accounting
Store/service receivables, allocations, tax/discount/shipping, returns/refunds/credit notes.

## Phase50.F — Reports & close
GL/subledger, trial balance, statements, AR/AP aging, cashflow, profitability, VAT/tax and period close.

## Safety
No Production schema work without exact MySQL verification, migration plan, successful fresh backup and rollback target. Do not widen public media routing to imported Catalog working-media. No guessed carrier/gateway endpoint.
