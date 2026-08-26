# PROJECT ROADMAP

Updated: 2026-08-26
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Epic: `Phase50 — Finance, Commerce & Admin Command Center`
Current Phase: `50.A.2 Checkout & Delivery`
Status: `50.A.1H + 50.A.2A PRODUCTION_VERIFIED / OWNER VISUAL QA NEXT / 50.A.2B NEXT`

## Permanent delivery order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI/LOCAL TEST → OWNER QA → HOST READ-ONLY VERIFY → BACKUP → DEPLOY FROM GITHUB → PRODUCTION VERIFY → DOCUMENT`

## Phase49 closeout baseline
Structured Product/Catalog/Hero/SEO/Bridge is operational. Product-owned public media remains the Production contract; imported Catalog working-media is not a public namespace.

## Phase50.A — Admin and commerce operational completeness
### 50.A.1 Admin Storefront / Hero parity — DEPLOYED
Command center, Product/imported-asset Hero actions, Coupon/Shipping/Pricing/address surfaces.

### 50.A.1B Product Gallery + Variant 2.0 — DEPLOYED
Product viewer/lightbox, Variant 2.0 size/build/package data, `store.0034` applied.

### 50.A.1C Admin media / mobile / SEO / Windows dimensions — DEPLOYED
Safe imported-media Admin, mobile Hero, homepage SEO audit, Windows image dimensions.

### 50.A.1D Sales Profiles + Hero Admin Public Media — DEPLOYED
Profile selection modes, profile identity/copy controls, public Hero media resolver, `store.0035` applied.

### 50.A.1E Unified Product Admin Workspace — PRODUCTION VERIFIED
Business-ordered Product change workspace; mature gallery/Variant/Profile/SEO/Catalog state preserved.

### 50.A.1F Business Admin Navigation + Product Admin 500 hotfix — PRODUCTION VERIFIED
Product changelist real-row render fixed; business navigation groups Store, Orders, Finance, Production, Windows/Catalog, Homepage, Content, Engagement, Support, Affiliate and System surfaces.

### 50.A.1G Velzon Operator Surface V2 — PRODUCTION FOUNDATION
Full-width changelists, on-demand filter drawer, Persian controls, modern Velzon search/actions/results/pagination and long-form section navigation.
Initial V2 CI: `Phase50 Product Admin Workspace CI` run `32955310832` PASS on `3687d0922959fca53f2118be6dacd32639159346`.

### 50.A.1H Admin Shell Stability — PRODUCTION VERIFIED / OWNER VISUAL QA NEXT
Owner QA found footer flash/mid-page placement during refresh, whole-page jump around active menu navigation and insufficient sidebar width.

Deployed at Production application commit `c283864290f9c989a9fcdf24ee8eef519560e917`:
- footer normal/static flow instead of Velzon absolute positioning,
- stable flex/min-height shell,
- right sidebar 290px with improved Persian readability,
- broad shell geometry transitions disabled,
- active-menu centering limited to internal SimpleBar/sidebar scroll; document `scrollIntoView` removed,
- Velzon V2 filter drawer/full-width table preserved,
- no migration.

Verification:
- Admin CI run `32958276378` PASS on `27335832e90c35dd95bb8a686dd89d1efd46dc8f`,
- Production Django/migration/static/HTTP gates PASS,
- owner browser refresh/menu visual QA remains before ACCEPTED.

### 50.A.2 Checkout & Delivery — ACTIVE
#### 50.A.2A Storefront Sales Profile Selector — PRODUCTION VERIFIED / OWNER VISUAL QA NEXT
Deployed at `c283864290f9c989a9fcdf24ee8eef519560e917` using the existing Product/ProductVariant schema and `/store/api/variant-commerce-options/`:
- list / size / weight / build / size→build / build→size modes,
- modern size/build/weight/material/color/quality/profile controls,
- selected profile price, weights, print time and package facts,
- mature native Variant select retained as fallback,
- canonical ProductVariant ID synchronized into existing price/cart/AddToCartForm path,
- no new migration.

Verification:
- Storefront CI run `32958296546` PASS on `e3c57311c0c3980befeaf6012f3bb8fc502333bc`,
- Production Product detail HTTP 200,
- selector CSS/JS HTTP 200 and present in HTML,
- native `variant-select` present,
- Variant commerce API parsed and verified,
- public private-media refs 0.

#### 50.A.2B Checkout immutable profile/shipping snapshot — NEXT
- persist/verify selected profile identity and customer-visible choice in finalized immutable order state where required,
- preserve existing Variant2 StoreOrderItem snapshots while making profile identity explicit,
- exact effective product + packaging shipping weight,
- parcel dimensions / insured value,
- normalized carrier quote + immutable order snapshot,
- Post / Tipax / Mahex only with verified official contracts/credentials,
- preserve mature ShippingMethod fallback.

### Product engagement package — OWNER REQUESTED / AFTER 50.A.2B OR OWNER PRIORITY
- real Favorite/Save model if absent,
- Product like/save/review/comment counters and Admin visibility,
- verified-purchase-only buyer review/comment policy where applicable,
- preserve existing ProductLike/ProductComment/ProductReview,
- dedicated migration/tests/backup.

### 50.A.3 Secure Store ZarinPal
Reuse server-owned amount, callback identity, Authority matching, server-to-server verify, idempotency and audit. Trusted redirect-host allowlist; never collect/store card/PIN/CVV.

### 50.A.4 Torob
Torob Product API v3, stable product/profile grouping, size/color/material/weight, current price/availability and image-quality contract.

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

## Current Production baseline
Application commit: `c283864290f9c989a9fcdf24ee8eef519560e917`.
Fresh rollback backup: `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-143650`.
MySQL `sfkilvrs_EmiAdmin_3dprinthub`; `store.0034` + `store.0035` applied; migration plan empty; no migration executed in the 50.A.1H/50.A.2A deployment; Home/Store/Admin/Product/new static HTTP 200; Variant API PASS; private imported-media refs 0.

## Safety
No Production schema work without exact MySQL verification, migration plan, successful fresh backup and rollback target. Do not widen public media routing to imported Catalog working-media. No guessed carrier/gateway endpoint. Purchased/private `static/velzon_master/` and fonts remain out of the public repository. Do not trust stale `origin/<branch>` on Production; explicit verified fetch to `FETCH_HEAD` remains the known-good path because the host refspec still tracks only tag `v0.33.0`.
