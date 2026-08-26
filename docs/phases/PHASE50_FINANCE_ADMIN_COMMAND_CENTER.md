# Phase50 — Finance, Commerce & Admin Command Center

Updated: 2026-08-26
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Subphase: `50.A.1G — Velzon Operator Surface V2`
Status: `GITHUB CI TESTED / PRODUCTION DEPLOY NEXT`
Current Production application commit: `bc7b97f9c63432b8105f52f61cf5cdae1369689b`.
Production MySQL has both `store.0034_phase50_variant2_commerce` and `store.0035_phase50_sales_profiles` applied.

## Owner request
Complete storefront/Admin commerce before accounting core. Admin must be a genuinely professional operator console, not merely Django Admin with a skin. Product management keeps the exact business sequence:
`اطلاعات کالا | تصاویر | فروش و موجودی | پروفایل‌ها و سایز/وزن | قیمت‌گذاری | ارسال و بسته‌بندی | SEO | اسلایدر صفحه اول | منبع و لایسنس | همگام‌سازی ویندوز`.

Current surrounding priorities remain reusable sales profiles, Hero Studio media integrity, professional Admin navigation/UI, Product engagement (likes/saves/reviews/comments), shipping/VAT/coupon, secure ZarinPal and Torob.

## Preserved foundation
- Product/Catalog/Bridge/Hero public media ownership remains Product-owned.
- Imported Catalog working-media remains private.
- Product, ProductCatalogProfile and ProductVariant remain authoritative; Admin presentation never duplicates commercial/SEO/sync state.
- StoreOrder/StorePayment/StoreInvoice and mature coupon/VAT/packaging/shipping calculations remain authoritative.
- StoreAddress plus Iran Province/County/City remain intact.
- mature payment request/callback/verify/idempotency architecture is reused later for Store payment.
- no direct Production source edits.
- purchased/private Velzon vendor assets remain private and gitignored; the public repository only stores project-owned adapters/integration code.

## Deployed baseline through 50.A.1E
- `/admin/command-center/`, Product/imported Asset Hero actions and bulk Hero controls.
- Product gallery/lightbox, Variant 2.0 package fields and StoreOrderItem snapshots.
- `store.0034_phase50_variant2_commerce` applied.
- Sales Profiles and Hero public-media resolver, `store.0035_phase50_sales_profiles` applied.
- unified Product change workspace in the required business order.
- imported Admin safe preview, mobile Hero, homepage SEO audit and Windows source image dimensions.

## 50.A.1F — Business Admin Navigation + Product Admin 500 Fix — PRODUCTION VERIFIED
Owner QA uncovered a real Product changelist 500 after the first unified workspace deploy. Root cause was `estimated_profit_admin` passing a numeric format specifier through `format_html`, which Django 6 applies to a SafeString. Corrected by formatting the numeric value first and passing the already-formatted string into safe HTML.

Also implemented business-oriented Admin navigation:
- Store/products,
- Orders/shipping,
- Finance/pricing/coupons,
- Production/inventory,
- Windows/Catalog imports,
- Homepage/site appearance,
- Content,
- Customer/product engagement,
- Support,
- Affiliate,
- System/base data.

Production verification at `bc7b97f9c63432b8105f52f61cf5cdae1369689b`:
- real Product changelist render 200,
- Velzon business navigation runtime gate PASS,
- Django check PASS with known warnings only,
- no migration drift,
- Home/Store/Admin login 200,
- private imported-media refs on public Home = 0,
- fresh rollback backup `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-125848`.

## 50.A.1G — Velzon Operator Surface V2
### Owner QA finding
After `bc7b97f`, Product Admin was functionally healthy but owner visual QA rejected the remaining changelist composition. The native Django `#changelist-filter` stayed permanently visible in a narrow sticky column, squeezed the Product result table and retained legacy labels/control styling. Owner requested a comprehensive modern Admin experience and re-supplied `master.zip`.

### Theme source review
The supplied package was reviewed as Velzon Django Corporate `4.3.0`, Bootstrap `5.3.6`. Reference patterns used include Velzon cards, table surfaces, off-canvas/drawer interaction, forms and responsive layout. The vendor package is purchased/private and remains gitignored under `static/velzon_master/`; it is not published into the public repository.

### Requested Delta
- eliminate the permanently visible filter column,
- keep native Django filter behavior/query semantics,
- open filters only when the operator requests them,
- modernize list/search/action/table/pagination surfaces,
- modernize long change forms and make large Product forms easy to navigate,
- retain existing Admin permissions/actions/model contracts,
- no schema/business change in this UI release.

### Implemented surfaces
- `static/admin/phase50-admin-console-v2.css`,
- `static/admin/phase50-admin-console-v2.js`,
- V2 assets loaded from `templates/admin/base.html`,
- focused contract extensions in `store/test_phase50_admin_http_regression.py`,
- CI JavaScript syntax gate added to `.github/workflows/phase50-product-admin-workspace-ci.yml`.

### Browser composition contract
- changelist is full-width by default,
- the existing Django `#changelist-filter` DOM node is moved into an on-demand Velzon-style drawer; no duplicate filter logic is created,
- `فیلترها` button opens the drawer; backdrop, close, Escape and filter reset supported,
- active query-filter count shown on trigger/drawer,
- common Filter/Search/Action labels normalized into Persian,
- search, bulk actions, results and pagination are independent card surfaces,
- result table has sticky headers, contained overflow and row hover,
- Product and other long change forms gain a sticky horizontal section navigator and card fieldsets,
- responsive/dark-mode behavior included.

### Regression gate
GitHub Actions `Phase50 Product Admin Workspace CI` run `32955310832` PASS on runtime snapshot `3687d0922959fca53f2118be6dacd32639159346`:
- Python compile PASS,
- `node --check static/admin/phase50-admin-console-v2.js` PASS,
- Django check PASS,
- migration drift NONE,
- CI SQLite migrations PASS,
- unified Product workspace regression PASS,
- real Product changelist and representative Admin HTTP/static contracts PASS.

### Database / migration
No new schema migration in 50.A.1G. Production `0034` and `0035` remain authoritative/applied.

### Production deployment gate
1. verify host root/branch/worktree and current `bc7b97f...` baseline read-only,
2. verify live GitHub branch SHA,
3. use explicit branch fetch to `FETCH_HEAD` per `ERR-50-007`,
4. verify approved target is a fast-forward and contains no migration-file delta,
5. create fresh `.env`/MySQL rollback backup,
6. `manage.py check`, `makemigrations --check --dry-run`, empty `migrate --plan`,
7. ff-only deploy approved GitHub snapshot,
8. collectstatic + Passenger restart,
9. Home/Store/Admin/Product Admin/static/private-media verification,
10. owner Ctrl+F5 visual QA: no permanent Filter column; drawer opens only on demand; Product edit section navigator visible and usable.

## Product Engagement — NEXT SEPARATE PHASE AFTER ADMIN V2 QA
Owner requested every Product to support likes, saves/favorites, comments/reviews and Admin counters. Existing `ProductLike`, `ProductComment`, `ProductReview` must be preserved. A real Favorite/Save contract is added only if absent. Buyer-feedback review/comment behavior must verify a qualifying paid/purchased Product. This is a separate schema/business-rule phase with its own migration, regression tests, Production backup and rollback; it is intentionally not mixed into the no-migration UI deploy.

## 50.A.2 — Checkout & Delivery
- profile-aware selector on Product page,
- persist chosen profile/size/build/package snapshots,
- effective product + packaging shipping weight,
- parcel dimensions and insured value,
- normalized carrier quote + immutable order snapshot,
- Post/Tipax/Mahex only after verified current official API credentials/contracts,
- preserve ShippingMethod fallback.

## 50.A.3 — Secure Store ZarinPal
Reuse server-owned amount/currency, random callback identity, exact Authority, server-to-server verify and idempotency. Trusted redirect-host allowlist; never capture/store card/PIN/CVV.

## 50.A.4 — Torob
Implement official current Torob Product API v3 using stable Product/profile identifiers, size/color/material/weight, price/availability and image-quality contract.

## Remaining Phase50
- 50.B Accounting core: کل / معین / تفصیلی, fiscal periods, balanced vouchers, immutable posting/reversal.
- 50.C Treasury: bank/cash, receipts/payments, allocations/refunds/reconciliation.
- 50.D Purchasing: suppliers, purchase orders/invoices/receiving/payables/returns.
- 50.E Sales accounting: receivables, payment allocation, tax/discount/shipping, credit notes.
- 50.F Reports/close: GL/subledger, trial balance, aging, cashflow, profitability, VAT/tax, fiscal close.

## Must not touch
- no direct Production source edit,
- no public exposure of imported working-media,
- no destructive historical order/payment/ledger reset,
- no guessed carrier/gateway endpoint,
- no Production migration without exact DB/plan/backup/rollback verification,
- no purchased/private Velzon/font assets committed to the public repository.
