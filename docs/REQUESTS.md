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

## REQ-49I-038 — Customer-readable Product intelligence
Status: `PRODUCTION VERIFIED`

## REQ-49I-039 — Homepage Hero uses Product-owned public media
Status: `OWNER REPORTS PRODUCTION OK`

## REQ-REL-001 — Catalog production release
Status: `WEB/CATALOG RELEASE OPERATIONAL`

## REQ-REL-002 — Final Windows Catalog Center executable
Status: `8.8.1 GITHUB RELEASE PUBLISHED / LIVE SOURCE EMPLOYEE SMOKE NEXT`

Delivered:
- `catalog-center-v8.8.1`,
- `3DPrintHub-CatalogCenter-v8.8.1.exe`,
- build `2026.08.25.2`,
- one-file/windowed executable requiring no Python installation on the employee PC,
- frozen runtime self-check and Playwright/browser launch smoke,
- persistent Catalog data outside the executable and secrets in Windows Credential Manager,
- SHA256-protected release artifact.

Acceptance remaining: open the released EXE on the employee Windows machine, verify preserved connection/AI profile, fetch one known MakerWorld source and perform one approved publish operation.

## REQ-50-001 — Complete business finance/accounting system
Status: `REQUESTED / PHASE50 ACTIVE`
Owner requests full GL/subledger/accounting, Treasury, Purchasing/Sales accounting, customer/supplier statements and management reports integrated with Store/service/inventory/production/payments.

## REQ-50-002 — Complete and reorganize Django Admin
Status: `50.A.1 GITHUB CI TESTED / MANUAL QA REQUIRED`

Implemented:
- authenticated `/admin/command-center/`,
- Sales / Storefront & Checkout / Treasury / Accounting / Purchasing / Inventory groups,
- Store Product actions to add/remove selected items from homepage slider,
- Imported Catalog Asset add/remove slider actions,
- Hero buttons for 5 random, 10 random and deactivate-all,
- Coupon, ShippingMethod, PricingSetting, customer addresses and Iran Province/County/City surfaced in Admin,
- non-destructive Hero deactivation and permission/POST/CSRF protected quick operations.

## REQ-50-003 — Preserve healthy commerce while adding accounting
Status: `ACTIVE CONSTRAINT`
Existing StoreOrder, Quote, Payment, StorePayment, invoices, inventory movements, Product/media/Catalog history and payment idempotency/security rules remain compatible and regression-tested.

## REQ-50-004 — Dynamic delivery price
Status: `REQUESTED / 50.A.2 NEXT`
Owner requires shipping calculation from product weight + packaging weight/dimensions and destination. Prefer Post/Tipax/Mahex live rates when current supported provider APIs/credentials are verified. Existing ShippingMethod fixed/weight rules remain the fallback. No guessed carrier endpoint is allowed.

## REQ-50-005 — Coupon + VAT checkout
Status: `BACKEND FOUNDATION ALREADY PRESENT / ADMIN SURFACED`
Verified current Store checkout already validates Coupon and applies discount, VAT, packaging fee, shipping fee and weight totals. Phase50 must preserve this and improve the customer/admin presentation rather than duplicate the logic.

## REQ-50-006 — Phishing-resistant comprehensive payment
Status: `REQUESTED / 50.A.3 PLANNED`
Preserve the mature service-payment contract: server-owned amount, transaction locking, random callback token, exact Authority match, server-to-server gateway verify and idempotent ledger. Extend StorePayment to the same model with trusted gateway-host allowlist, no card/PIN/CVV collection, secure redirect UX, immutable audit/reconciliation and abuse controls.

## REQ-50-007 — Professional Product gallery
Status: `IMPLEMENTED / GITHUB CI TESTED / MANUAL QA REQUIRED`
Owner requires thumbnails to replace the main product image inside one fixed viewer, full image visibility rather than forced cropping, and click-to-open full-screen viewing. Implemented with contain-fit viewer, keyboard/click thumbnail switching and accessible lightbox navigation.

## REQ-50-008 — Variant 2.0 size/build/packaging parity
Status: `IMPLEMENTED FOUNDATION / GITHUB CI TESTED / CHECKOUT SNAPSHOT NEXT`
Owner requires products to support multiple sizes and build/weight profiles (for example 20/24/26/28/30 cm and hollow/standard/solid), with material/color/quality, independent weight/price/inventory and package dimensions. Runtime/schema/Admin foundation and migration `store.0034` are implemented. Checkout snapshot/effective shipping use is next.

## REQ-50-009 — Torob marketplace integration
Status: `REQUESTED / 50.A.4 PLANNED`
Implement current official Torob Product API v3 with stable product/variant grouping, size/color/material, current price/availability, image-quality rules and later verified order attribution/webhooks.

## REQ-50-010 — ZarinPal Store checkout activation
Status: `REQUESTED / 50.A.3 PLANNED`
The mature secure ZarinPal engine already serves service Quote payments. StorePayment must be connected to the same server-owned amount, callback-token, Authority-match, server-to-server verification and idempotency contract before real Production merchant activation.

## Change rule
New work extends/wraps mature behavior and must pass CI/Local tests before Production deployment. No financial/shipping/schema migration is deployed without exact MySQL verification, migration plan, successful backup and rollback target.
