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
Status: `OWNER REPORTS PRODUCTION OK`

## REQ-REL-001 — Catalog production release
Status: `WEB/CATALOG RELEASE OPERATIONAL`

## REQ-REL-002 — Final Windows Catalog Center executable
Status: `8.8.1 RELEASED / SOURCE HAS NEW IMAGE-DIMENSION DELTA`
Released EXE remains `3DPrintHub-CatalogCenter-v8.8.1.exe`; source now also shows original image pixel dimensions. A new immutable Windows version/rebuild is required only after this source delta passes owner smoke.

## REQ-50-001 — Complete business finance/accounting system
Status: `REQUESTED / PHASE50 ACTIVE`
Full GL/subledger, Treasury, Purchasing/Sales accounting, customer/supplier statements and management reports integrated with Store/service/inventory/production/payments.

## REQ-50-002 — Complete and reorganize Django Admin
Status: `50.A.1 + 50.A.1C GITHUB CI TESTED / HOST QA REQUIRED`
Includes command center, Product/imported asset Hero actions, 5/10 random Hero, Coupon/Shipping/Pricing/addresses and professional imported-model media/data visibility.

## REQ-50-003 — Preserve healthy commerce while adding accounting
Status: `ACTIVE CONSTRAINT`
Existing StoreOrder, Quote, Payment, StorePayment, invoices, inventory movements, Product/media/Catalog history and payment idempotency/security remain compatible.

## REQ-50-004 — Dynamic delivery price
Status: `REQUESTED / 50.A.2 NEXT`
Shipping from product + packaging weight/dimensions/destination; Post/Tipax/Mahex only with verified current official API credentials/contracts; mature ShippingMethod fallback preserved.

## REQ-50-005 — Coupon + VAT checkout
Status: `BACKEND FOUNDATION ALREADY PRESENT / ADMIN SURFACED`
Current Store checkout already validates Coupon and applies discount, VAT, packaging, shipping and weight totals; improve presentation/integration rather than duplicate logic.

## REQ-50-006 — Phishing-resistant comprehensive payment
Status: `REQUESTED / 50.A.3 PLANNED`
Reuse server-owned amount, DB locking, random callback identity, exact Authority matching, server-to-server gateway verify and idempotent ledger. Add trusted redirect-host allowlist and never collect/store card/PIN/CVV.

## REQ-50-007 — Professional Product gallery
Status: `IMPLEMENTED / GITHUB CI TESTED / HOST QA REQUIRED`
Thumbnail-to-main contain-fit viewer and accessible fullscreen lightbox.

## REQ-50-008 — Variant 2.0 size/build/packaging parity
Status: `IMPLEMENTED FOUNDATION / GITHUB CI TESTED / CHECKOUT SNAPSHOT NEXT`
Multiple sizes/build profiles with material/color/quality, independent weight/price/inventory and package dimensions. Migration `store.0034` requires verified Production migration gate.

## REQ-50-009 — Torob marketplace integration
Status: `REQUESTED / 50.A.4 PLANNED`
Current official Torob Product API v3, stable product/variant grouping, size/color/material, current price/availability, image-quality rules and verified attribution/webhooks.

## REQ-50-010 — ZarinPal Store checkout activation
Status: `REQUESTED / 50.A.3 PLANNED`
Connect StorePayment to the mature secure service-payment engine before real Production merchant activation.

## REQ-50-011 — Imported-model Admin image/data integrity
Status: `IMPLEMENTED / GITHUB CI TESTED / HOST QA REQUIRED`
Owner requires uploaded/imported images to be visible in Admin without 404 and imported records to show useful translated/commercial data. Admin preview now resolves only Product-owned public media or remote source fallback and shows completeness; working-media remains private.

## REQ-50-012 — Mobile Hero product visibility
Status: `IMPLEMENTED / GITHUB CI TESTED / MOBILE QA REQUIRED`
Hero Product title and description must not hide the Product image. Mobile title/caption/buttons are reduced; very narrow phones hide description while preserving CTA.

## REQ-50-013 — Homepage SEO operator controls
Status: `IMPLEMENTED ADMIN AUDIT / SOCIAL META EXECUTION STILL OPEN`
Existing SiteSetting `meta_title/meta_description` remain canonical. Admin now shows length health, search-result preview and Hero title/Alt audit. Dedicated Twitter fields and `og:image:alt` remain separate execution debt rather than duplicated DB fields.

## REQ-50-014 — Windows Product image pixel dimensions
Status: `SOURCE IMPLEMENTED / CI TESTED / NEXT EXE VERSION AFTER SMOKE`
Every Product image card must show original `width × height px` so operator can reject weak images before publish.

## REQ-50-015 — Reconcile Production Product Admin 500
Status: `OPEN / READ-ONLY HOST AUDIT REQUIRED`
Do not guess the cause. Verify exact Production HEAD/branch, MySQL, `store.0034` state and runtime evidence before any migration/deploy.

## Change rule
New work extends/wraps mature behavior and must pass CI/Local tests before Production deployment. No financial/shipping/schema migration is deployed without exact MySQL verification, migration plan, successful backup and rollback target.
