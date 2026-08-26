# OWNER REQUESTS

Last Updated: 2026-08-26

Older detailed request history remains available in Git history. This file keeps the active acceptance contracts.

## Preserved Phase49 contracts
- GitHub-first delivery; live branch/HEAD verification before Local/Host operations.
- Catalog Product Workspace remains canonical editor.
- exact Search/Listing URL remains authoritative.
- Product AI uses exactly one saved Provider/Model/key path and no hidden AI/model scan on open.
- fixed/range/formula pricing modes remain independent.
- Product/SEO/media/Bridge security and idempotency contracts remain intact.
- imported Catalog working-media is not a Production-public media namespace.

## REQ-49I-038 — Customer-readable Product intelligence
Status: `PRODUCTION VERIFIED`

## REQ-49I-039 — Homepage Hero uses Product-owned public media
Status: `PRODUCTION VERIFIED`

## REQ-REL-001 — Catalog production release
Status: `WEB/CATALOG RELEASE OPERATIONAL`

## REQ-REL-002 — Final Windows Catalog Center executable
Status: `8.8.1 RELEASED / SOURCE HAS NEW IMAGE-DIMENSION DELTA`
Released EXE remains `3DPrintHub-CatalogCenter-v8.8.1.exe`; source now also shows original image pixel dimensions. A new immutable Windows version/rebuild is required after the current source delta passes owner smoke.

## REQ-50-001 — Complete business finance/accounting system
Status: `REQUESTED / PHASE50 ACTIVE`
Full GL/subledger, Treasury, Purchasing/Sales accounting, customer/supplier statements and management reports integrated with Store/service/inventory/production/payments.

## REQ-50-002 — Complete and reorganize Django Admin
Status: `ACTIVE / 50.A.1G CI TESTED / PRODUCTION DEPLOY NEXT`
The Admin must be a professional operator console rather than a lightly styled legacy Django Admin. Business navigation, Product workspace and Product 500 fix are already Production-verified at `bc7b97f9c63432b8105f52f61cf5cdae1369689b`. Current delta modernizes final changelist/change-form composition using the owner-supplied Velzon Django Corporate 4.3.0 theme as reference while preserving mature Django Admin behavior.

## REQ-50-003 — Preserve healthy commerce while adding accounting
Status: `ACTIVE CONSTRAINT`
Existing StoreOrder, Quote, Payment, StorePayment, invoices, inventory movements, Product/media/Catalog history and payment idempotency/security remain compatible.

## REQ-50-004 — Dynamic delivery price
Status: `REQUESTED / 50.A.2 NEXT`
Shipping from chosen profile/product + packaging weight/dimensions/destination; Post/Tipax/Mahex only with verified current official API credentials/contracts; mature ShippingMethod fallback preserved.

## REQ-50-005 — Coupon + VAT checkout
Status: `BACKEND FOUNDATION ALREADY PRESENT / ADMIN SURFACED`
Current Store checkout already validates Coupon and applies discount, VAT, packaging, shipping and weight totals; improve presentation/integration rather than duplicate logic.

## REQ-50-006 — Phishing-resistant comprehensive payment
Status: `REQUESTED / 50.A.3 PLANNED`
Reuse server-owned amount, DB locking, random callback identity, exact Authority matching, server-to-server gateway verify and idempotent ledger. Add trusted redirect-host allowlist and never collect/store card/PIN/CVV.

## REQ-50-007 — Professional Product gallery
Status: `DEPLOYED FOUNDATION / OWNER QA CONTINUES`
Thumbnail-to-main contain-fit viewer and accessible fullscreen lightbox.

## REQ-50-008 — Variant 2.0 size/build/packaging parity
Status: `DEPLOYED / STORE.0034 APPLIED`
Multiple sizes/build profiles with material/color/quality, independent weight/price/inventory and package dimensions. Checkout profile snapshot/presentation continues in 50.A.2.

## REQ-50-009 — Torob marketplace integration
Status: `REQUESTED / 50.A.4 PLANNED`
Current official Torob Product API v3, stable product/profile grouping, size/color/material/weight, current price/availability, image-quality rules and verified attribution/webhooks.

## REQ-50-010 — ZarinPal Store checkout activation
Status: `REQUESTED / 50.A.3 PLANNED`
Connect StorePayment to the mature secure service-payment engine before real Production merchant activation.

## REQ-50-011 — Imported-model Admin image/data integrity
Status: `PRODUCTION VERIFIED / HERO STUDIO OWNER QA CONTINUES`
Imported-model list/change previews resolve Product-owned public media or remote source fallback; working-media remains private.

## REQ-50-012 — Mobile Hero product visibility
Status: `DEPLOYED / OWNER QA`
Hero Product title and description must not hide the Product image. Mobile title/caption/buttons are reduced; very narrow phones hide description while preserving CTA.

## REQ-50-013 — Homepage SEO operator controls
Status: `DEPLOYED ADMIN AUDIT / SOCIAL META EXECUTION STILL OPEN`
Existing SiteSetting `meta_title/meta_description` remain canonical. Admin shows length health, search-result preview and Hero title/Alt audit. Dedicated Twitter fields and `og:image:alt` remain separate execution debt.

## REQ-50-014 — Windows Product image pixel dimensions
Status: `SOURCE IMPLEMENTED / CI TESTED / NEXT EXE VERSION AFTER SMOKE`
Every Product image card must show original `width × height px` so operator can reject weak images before publish.

## REQ-50-015 — Reconcile Production Product Admin 500
Status: `RESOLVED / PRODUCTION VERIFIED`
Product changelist real-row render is HTTP 200 after the `estimated_profit_admin` fix; regression coverage now renders the actual changelist with a Product row.

## REQ-50-016 — Reusable sales profiles per Product
Status: `PRODUCTION DEPLOYED / OWNER QA CONTINUES`
Each Product can choose customer selection by full profile list, size, weight, build, size→build or build→size. `store.0035_phase50_sales_profiles` is applied on Production.

## REQ-50-017 — Hero Studio images must load on slide edit pages
Status: `PRODUCTION DEPLOYED / OWNER QA CONTINUES`
Hero Admin must never emit private `store/imported-models/...` URLs. Product-owned public gallery/main media or safe remote fallback remains the contract.

## REQ-50-018 — Unified Product Admin workspace
Status: `PRODUCTION VERIFIED / VISUAL REFINEMENT CONTINUES IN 50.A.1G`
The Product change page retains the exact business order `اطلاعات کالا | تصاویر | فروش و موجودی | پروفایل‌ها و سایز/وزن | قیمت‌گذاری | ارسال و بسته‌بندی | SEO | اسلایدر صفحه اول | منبع و لایسنس | همگام‌سازی ویندوز`. Existing Product, ProductCatalogProfile, ProductVariant and SEO data remain authoritative.

## REQ-50-019 — Modern Velzon Admin interaction surface
Status: `IMPLEMENTED / GITHUB CI TESTED / PRODUCTION DEPLOY NEXT`
Owner QA rejected the remaining legacy changelist presentation. Acceptance contract:
- no permanently visible Django Filter column,
- full-width operational tables,
- `فیلترها` opens only on demand as a professional drawer/off-canvas,
- Persian search/filter/action controls,
- modern Velzon cards for search, bulk actions, tables and pagination,
- long Product/change forms have fast section navigation,
- responsive/dark-mode friendly,
- existing Django permissions/actions/filter query semantics remain authoritative,
- purchased Velzon vendor package stays private/gitignored; only project-owned integration code belongs in the public repository.

GitHub Actions run `32955310832` PASS on code snapshot `3687d0922959fca53f2118be6dacd32639159346`.

## REQ-50-020 — Product likes, saved/favorites, comments and verified-buyer reviews
Status: `REQUESTED / NEXT SEPARATE SCHEMA-BUSINESS PHASE AFTER ADMIN V2 QA`
Preserve existing ProductLike/ProductComment/ProductReview. Add a real Favorite/Save contract if absent, Product-level engagement counters and Admin visibility. Review/comment rules representing buyer feedback must verify a qualifying purchased/paid Product order. This work requires its own migration/tests/backup and must not be mixed into the no-migration Admin skin deploy.

## Change rule
New work extends/wraps mature behavior and must pass CI/Local tests before Production deployment. No financial/shipping/schema migration is deployed without exact MySQL verification, migration plan, successful backup and rollback target. On the current Production host, verify the Git fetch refspec before relying on `origin/<branch>`; explicit live branch fetch to `FETCH_HEAD` is the verified path when remote-tracking refs are stale.
