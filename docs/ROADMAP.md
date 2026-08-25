# PROJECT ROADMAP

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Epic: `Phase50 — Finance, Commerce & Admin Command Center`
Current Phase: `50.A.1D — Sales Profiles + Hero Admin Public Media`
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
- `size_label`, build profile, packaging weight and parcel dimensions,
- StoreOrderItem commerce snapshots,
- migration `store.0034_phase50_variant2_commerce` applied on Production,
- Variant Admin and public variant metadata endpoint.

### 50.A.1C Admin media / mobile / SEO / Windows dimensions — DEPLOYED
- ImportedPrintAsset Admin avoids private working-media previews,
- safe Product-owned public image resolution,
- mature imported-model editing preserved,
- mobile Hero compacted,
- homepage SEO Admin audit added,
- Windows source image dimensions added,
- Production verified at commit `5c5c5e1e141fd3ff8df3c079abc55e4593feb41f` with HTTP 200 smoke and Product Admin 500 regression cleared.

### 50.A.1D Sales Profiles + Hero Admin Public Media — CI TESTED / NEXT DEPLOY
- Product chooses how customers select profiles: list / size / weight / build / size→build / build→size,
- ProductVariant gains profile name/key/default/order,
- profile key becomes part of uniqueness so identical size/material/color/build combinations can still have different weight/time/price profiles,
- Admin supports copying a profile as a starting point and editing only changed commercial values,
- profile metadata endpoint exposes selector/value/weight/time/price/shipping data,
- Hero Studio product browser/gallery JSON now resolves public Product media and never emits private `store/imported-models/...` URLs,
- migration `store.0035_phase50_sales_profiles`,
- CI run `32879712980` PASS on snapshot `405d2c1daa85828d1a0dc68210d201c85b6db7ba`.

### 50.A.2 Checkout & Delivery — NEXT AFTER 50.A.1D PRODUCTION QA
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
No Production schema work without exact MySQL verification, migration plan, successful fresh backup and rollback target. Do not widen public media routing to imported Catalog working-media. No guessed carrier endpoint.
