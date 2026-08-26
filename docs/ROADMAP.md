# PROJECT ROADMAP

Updated: 2026-08-26
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Epic: `Phase50 — Finance, Commerce & Admin Command Center`
Current Phase: `50.A.1H Admin Shell Stability + 50.A.2A Storefront Sales Profile Selector`
Status: `GITHUB CI TESTED / HOST READ-ONLY VERIFY NEXT`

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

### 50.A.1G Velzon Operator Surface V2 — CI TESTED / OWNER QA FOUND FOLLOW-UP
- full-width changelists,
- filters moved to on-demand drawer,
- Persian search/filter/action controls,
- modern Velzon search/actions/results/pagination,
- change-form section navigation,
- no schema migration.

Initial V2 CI: `Phase50 Product Admin Workspace CI` run `32955310832` PASS on `3687d0922959fca53f2118be6dacd32639159346`.

### 50.A.1H Admin Shell Stability — GITHUB CI TESTED / DEPLOY WITH CURRENT BATCH
Owner QA found footer flash/mid-page placement during refresh, whole-page jump around active menu navigation and insufficient sidebar width.

Implementation:
- Velzon footer moved from vendor absolute positioning into normal Admin document flow,
- stable flex/min-height shell prevents footer painting across content while page initializes,
- operator sidebar widened to 290px and Persian menu spacing improved,
- broad shell geometry transitions disabled,
- active menu centering now adjusts only the internal sidebar/SimpleBar scroll position; no document-level `scrollIntoView`,
- preserves Velzon V2 filter drawer and all Django Admin behavior,
- no migration.

Verification:
- `Phase50 Product Admin Workspace CI` run `32958276378` PASS,
- Admin runtime snapshot `27335832e90c35dd95bb8a686dd89d1efd46dc8f`,
- JS syntax, Django check, migration drift, CI migrations and Admin regressions PASS.

### 50.A.2 Checkout & Delivery — ACTIVE
#### 50.A.2A Storefront Sales Profile Selector — GITHUB CI TESTED / DEPLOY WITH CURRENT BATCH
The existing Product/ProductVariant sales-profile metadata and `/store/api/variant-commerce-options/` contract are now surfaced on Product detail pages without a new schema:
- respects Product selection mode: list / size / weight / build / size→build / build→size,
- renders available size/build/weight/material/color/quality choices as modern controls,
- shows selected profile price, part/shipping weight, print time and parcel dimensions,
- keeps the mature native Variant select as progressive-enhancement fallback,
- synchronizes canonical Variant ID and dispatches the existing change event, preserving current `store.js`, price calculation and `AddToCartForm` cart contract,
- no new migration.

Verification:
- `Phase50 Variant2 Gallery CI` run `32958296546` PASS,
- Storefront runtime snapshot `e3c57311c0c3980befeaf6012f3bb8fc502333bc`,
- JS syntax, Django check, migration drift, migration apply and Variant2/gallery/profile-selector regressions PASS.

#### 50.A.2B Checkout immutable profile snapshot — NEXT
- persist/verify selected profile identity and customer-visible selection snapshot in the finalized order path,
- preserve existing Variant2 StoreOrderItem snapshots while making profile identity explicit where needed,
- exact effective product + packaging shipping weight,
- parcel dimensions / insured value,
- normalized carrier quote + immutable order snapshot,
- Post / Tipax / Mahex only with verified official contracts/credentials,
- preserve mature ShippingMethod fallback.

### Product engagement package — OWNER REQUESTED
- real Favorite/Save model if absent,
- Product like/save/review/comment counters and Admin visibility,
- verified-purchase-only buyer review/comment policy where applicable,
- preserve existing ProductLike/ProductComment/ProductReview,
- dedicated migration/tests/backup; do not mix schema work into the current no-migration UI deploy.

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

## Current Production gate
The repository's last terminal-verified Production HEAD is `bc7b97f9c63432b8105f52f61cf5cdae1369689b`, but owner screenshots subsequently show newer V2 visuals without an accompanying terminal HEAD transcript. Therefore current Host HEAD must be read-only verified before deployment; do not hard-code an assumed Production baseline.

After Host verification: explicit branch fetch to `FETCH_HEAD` per `ERR-50-007`, fresh rollback backup, no-migration gate, ff-only deploy, collectstatic/restart, then Admin refresh/sidebar and Product selector visual/data QA.

## Safety
No Production schema work without exact MySQL verification, migration plan, successful fresh backup and rollback target. Do not widen public media routing to imported Catalog working-media. No guessed carrier/gateway endpoint. Purchased/private `static/velzon_master/` and fonts remain out of the public repository. Do not trust stale `origin/<branch>` on Production; explicit verified fetch to `FETCH_HEAD` remains the known-good path.
