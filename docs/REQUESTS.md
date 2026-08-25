# OWNER REQUESTS

Last Updated: 2026-08-25

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
Status: `PHASE50.A.1C DEPLOYED / 50.A.1D CI TESTED`
Includes command center, Product/imported asset Hero actions, 5/10 random Hero, Coupon/Shipping/Pricing/addresses, professional imported-model media/data visibility and sales profile controls.

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
Status: `DEPLOYED FOUNDATION / HERO STUDIO FINAL BOUNDARY IN 50.A.1D`
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
Production deploy after exact MySQL/migration/backup verification returned HTTP 200 for `/admin/store/product/` and all primary Admin smoke endpoints.

## REQ-50-016 — Reusable sales profiles per Product
Status: `IMPLEMENTED / GITHUB CI TESTED / PRODUCTION DEPLOY NEXT`
Each Product can choose customer selection by full profile list, size, weight, build, size→build or build→size. Profiles can share material/color/size/build while differing in weight, print time, pricing inputs, packaging and shipping by using a distinct profile key. Admin provides copy-profile to duplicate all mature settings and then edit only changed values.

## REQ-50-017 — Hero Studio images must load on slide edit pages
Status: `IMPLEMENTED / GITHUB CI TESTED / PRODUCTION DEPLOY NEXT`
`/admin/website/homepageheroslide/<id>/change/` product and album thumbnails must never emit private `store/imported-models/...` URLs. Final Admin JSON endpoints resolve Product-owned public gallery/main media or row-specific remote HTTP(S) source media.

## Change rule
New work extends/wraps mature behavior and must pass CI/Local tests before Production deployment. No financial/shipping/schema migration is deployed without exact MySQL verification, migration plan, successful backup and rollback target.
