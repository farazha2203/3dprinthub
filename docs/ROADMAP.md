# PROJECT ROADMAP

Updated: 2026-08-26
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Epic: `Phase50 — Finance, Commerce & Admin Command Center`
Current Phase: `50.A.1G — Velzon Operator Surface V2`
Status: `GITHUB CI TESTED / PRODUCTION DEPLOY NEXT`

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
Business-ordered Product change workspace; mature gallery/Variant/Profile/SEO/Catalog state preserved. Product Admin 500 regression was subsequently fixed and Production verified.

### 50.A.1F Business Admin Navigation + Product Admin 500 hotfix — PRODUCTION VERIFIED
Production at `bc7b97f9c63432b8105f52f61cf5cdae1369689b`:
- Product changelist real-row render 200,
- business-oriented Admin navigation active,
- Windows/Catalog imports, Finance/Coupons, Orders, Store, Production and interaction models grouped by operator intent,
- Home/Store/Admin HTTP 200,
- no new migration.

### 50.A.1G Velzon Operator Surface V2 — GITHUB CI TESTED / DEPLOY NEXT
Owner QA showed that the legacy permanent Django `#changelist-filter` column still squeezed result tables and retained old UI behavior. Owner re-supplied Velzon Django Corporate 4.3.0 `master.zip` for reference.

Implementation:
- full-width modern changelists,
- native Django filter functionality moved to an on-demand off-canvas/drawer instead of always-visible sidebar,
- Persian filter/search/action labels,
- modern Velzon search toolbar, bulk action card, result card/table and pagination,
- sticky result headers and controlled table overflow,
- long change forms gain sticky horizontal section navigation and card fieldsets,
- existing permission, action, filtering and ModelAdmin contracts remain authoritative,
- purchased Velzon vendor assets remain private/gitignored; only project-owned adapter CSS/JS/templates are committed publicly,
- no schema migration.

Verification:
- GitHub Actions `Phase50 Product Admin Workspace CI` run `32955310832` PASS,
- CI-tested runtime snapshot `3687d0922959fca53f2118be6dacd32639159346`,
- JavaScript `node --check` PASS,
- Django check PASS,
- migration drift NONE,
- CI SQLite migrations PASS,
- focused Product/representative Admin HTTP regressions PASS.

Production gate:
1. host must still be clean on verified `bc7b97f...`,
2. explicit live branch fetch to `FETCH_HEAD` because `ERR-50-007`,
3. fresh rollback backup,
4. no migration-file delta and empty migration plan,
5. ff-only deploy,
6. collectstatic + Passenger restart,
7. Home/Store/Admin/Product Admin/static/private-media gates,
8. owner Ctrl+F5 visual QA of Product changelist/filter drawer/Product edit section navigator.

### Product engagement package — NEXT AFTER ADMIN V2 ACCEPTANCE
Separate schema/business-rule phase:
- real Favorite/Save model,
- Product like/save/review/comment counters and Admin visibility,
- verified-purchase-only Product review/comment policy where applicable,
- preserve existing ProductLike/ProductComment/ProductReview contracts,
- dedicated migration, regression tests, Production backup and rollback.

### 50.A.2 Checkout & Delivery — NEXT COMMERCE PHASE
- profile-aware Product selector,
- selected profile/size/build/package snapshots at checkout,
- effective product + packaging shipping weight,
- parcel dimensions / insured value,
- normalized carrier quote + immutable order snapshot,
- Post / Tipax / Mahex only with verified official contracts/credentials,
- preserve mature ShippingMethod fallback.

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

## Safety
No Production schema work without exact MySQL verification, migration plan, successful fresh backup and rollback target. Do not widen public media routing to imported Catalog working-media. No guessed carrier/gateway endpoint. Do not publish purchased/private `static/velzon_master/` or font assets to the public repository. On Production, do not trust stale `origin/<branch>` unless the branch fetch refspec is verified; explicit fetch to `FETCH_HEAD` is the known-good path.
