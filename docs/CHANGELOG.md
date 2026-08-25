# PROJECT CHANGELOG

Record meaningful changes only. Older detailed entries remain available in Git history.

## 2026-08-25 — Phase50.A.1 Admin Storefront / Hero Parity

### Implemented
- added Product Admin bulk actions to add/remove selected products from the homepage Hero,
- added Imported Catalog Asset bulk actions for the same Hero add/remove operations,
- added Hero Admin quick controls for `۵ محصول رندوم`, `۱۰ محصول رندوم` and non-destructive deactivate-all,
- random Hero selection is limited to active Product-backed assets with a public-renderable image,
- reactivating an existing slide preserves operator-edited Hero text/SEO instead of overwriting it,
- quick Hero mutations are POST-only, permission-protected and CSRF-protected through Django Admin,
- expanded `/admin/command-center/` with a Storefront/Checkout section linking Products, Catalog Assets, Hero, Coupons, Shipping Methods, Pricing Settings, customer addresses and Iran Province/County/City reference data,
- verified the mature checkout already owns coupon discount, VAT, packaging, shipping and order-weight calculations; no duplicate pricing logic was added,
- recorded the next delivery work as a carrier-adapter layer for Post/Tipax/Mahex only after a current official API contract is verified,
- recorded StorePayment hardening/unification with the mature server-to-server payment verification contract.

### Verification
- GitHub Actions `Phase50 Admin Storefront Parity CI` passed on code snapshot `7c8714b5715cd00900a76b99097823266251d4a2`,
- Python compile PASS,
- `manage.py check` PASS with known warnings only,
- `makemigrations --check --dry-run` => `No changes detected`,
- Phase50 Admin regression tests PASS.

### Safety
- no schema/model migration,
- no direct Production edit or deploy,
- no StoreOrder/Quote/payment semantics changed,
- no public Product/Hero media-ownership contract changed,
- Hero removal deactivates rather than deletes history.

## 2026-08-25 — Phase50.A Admin Command Center

### Implemented
- added authenticated `/admin/command-center/` as a business-oriented back-office entry point,
- organized existing operations into Sales, Treasury, Accounting/Ledgers, Purchasing and Inventory/Production,
- added permission-aware links only to real registered ModelAdmins,
- added live counters for pending service/store payments, active store orders, draft filament purchases, open affiliate payouts and cost entries,
- added `مرکز مالی و بازرگانی` shortcut to the custom Admin sidebar,
- added date hierarchy and 50-row pagination to key Payment/Order/Purchase/Cost/Production/Payout admins,
- added focused regression test `website/test_phase50a_admin_command_center.py`,
- future Accounting/Treasury/Purchasing modules are displayed as Phase50.B-F roadmap items rather than fake links.

### Safety
- no schema/model migration,
- no commerce/payment/Catalog/Hero behavior change,
- Production untouched pending owner QA.

## 2026-08-25 — Phase49.3I.30 Production Hero Product-Media Ownership

### Owner Evidence
- first real Catalog Site Publish produced a healthy Product page on Production,
- homepage Hero slide text rendered but selected images were blank,
- browser console showed HTTP 404 for `/media/store/imported-models/gallery/...`,
- Local `127.0.0.1:8000` rendered the same Hero correctly.

### Verified Root Cause
- Production non-DEBUG media routing intentionally exposes public Product/category/SEO media, not the imported Catalog working-gallery namespace,
- Phase49 Hero Studio preferred `ImportedPrintAssetImage.image.url`, so public Hero HTML referenced an internal media path,
- Local DEBUG served all media and masked the production-only ownership mismatch.

### Implemented
- added `website/phase49_3i30_hero_media_ownership.py` as the final Hero media resolver,
- public Hero now maps the selected imported-image basename to the Product-owned gallery copy under `/media/store/products/gallery/`,
- if the exact Product gallery image is unavailable, Product main image is used,
- remote source image is only a final fallback,
- imported working-media paths are never returned as the public Hero image,
- public media routing was not widened,
- focused regression test added at `website/test_phase49_3i30_hero_media_ownership.py`.

No migration.

## 2026-08-25 — Phase49.3I.29 Production Deployment Verified
- owner-approved Phase49 application deployed to Production,
- MySQL verified and rollback backup created,
- pending Phase49 migrations applied,
- collectstatic/Passenger restart completed,
- Home/Store/Product HTTP checks returned 200,
- Product presentation sanitization passed,
- final Production worktree verified clean.

## 2026-08-25 — Phase49.3I.29 Structured Web Product Presentation
- replaced raw `technical_notes` JSON output with customer-readable product sections,
- internal AI/audit fields hidden from public Product pages,
- no web-time AI request added.

## 2026-08-25 — Phase49.3I.28 Exact-Link Canonical Title Call Contract
- fixed duplicate `current_title` binding while preserving mature source identity.

## 2026-08-25 — Phase49.3I.27 Exact-Link Category Provider Crash Fix
- bridged mature `App.get_all_categories()` provider into exact-link completion.

## 2026-08-25 — Phase49.3I.26 Unified Exact-Link Completion
- restored canonical Product stages, observable AI, vertical gallery and bulk archive/delete workflow.
