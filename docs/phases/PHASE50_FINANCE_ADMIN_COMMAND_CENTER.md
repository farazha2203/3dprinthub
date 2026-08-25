# Phase50 — Finance, Commerce & Admin Command Center

Updated: 2026-08-25
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Subphase: `50.A.1C — Admin media integrity + mobile Hero + homepage SEO + Windows image dimensions`
Status: `GITHUB CI TESTED / HOST READ-ONLY AUDIT + MANUAL QA REQUIRED`
Production: `REAL HOST STATE MUST BE RECONCILED BEFORE NEXT DEPLOY`

## Owner request
Complete storefront/Admin commerce before accounting core. Current explicit priorities include professional Product media, Admin parity, size/build variants, reliable imported-data visibility, mobile Hero usability, homepage SEO controls, shipping/VAT/coupon, secure ZarinPal and Torob.

## Preserved foundation
- Product/Catalog/Bridge/Hero public media ownership remains Product-owned,
- StoreOrder/StorePayment/StoreInvoice and mature coupon/VAT/packaging/shipping calculations remain authoritative,
- customer StoreAddress plus Iran Province/County/City remain intact,
- mature service-payment request/callback/verify/idempotency engine is reused later for Store payment,
- no direct Production source edits.

## 50.A.1 / 50.A.1B baseline
Already CI tested:
- `/admin/command-center/`, Product/imported Asset Hero actions and 5/10 random/deactivate-all,
- Product contain-fit main viewer, thumbnail swap and fullscreen lightbox,
- Variant 2.0 size/build profile/packaging fields and StoreOrderItem snapshots,
- migration `store.0034_phase50_variant2_commerce`,
- Variant Admin + selector metadata endpoint.

## 50.A.1C — Current implementation
### Owner evidence
- Imported Catalog/Admin thumbnails on Production returned 404 for `store/imported-models/...` working media,
- imported records did not expose enough translated/commercial completeness at a glance,
- `/admin/store/product/` returned 500,
- mobile Hero text card covered too much of Product imagery,
- homepage SEO operator controls needed a clearer audit surface,
- Windows Product image cards needed original pixel dimensions.

### Requested Delta
Fix presentation/integrity at the final Admin/mobile/Windows boundaries without widening private media routing, rewriting Catalog, or guessing the Product Admin 500 cause.

### Implemented
- safe Admin image resolver: matching Product gallery → Product main image → source HTTP(S),
- imported working FileFields remain editable/auditable but are never rendered as public preview URLs,
- ImportedPrintAsset mature Phase35 list editing/actions preserved; safe preview and 4/4 completeness added,
- imported image inline displays source `W × H px`, selection/primary state and safe preview,
- mobile Hero caption/title/description/CTA footprint reduced; very narrow phones hide description,
- SiteSetting Admin keeps existing `meta_title/meta_description` and adds SEO health, SERP preview and active-Hero Alt/title audit,
- Windows Product image thumbnail cards display original pixel dimensions at the existing installed workspace boundary,
- no new migration added in 50.A.1C.

### Regression gate
First CI run failed because an initial Admin list replacement conflicted with mature Phase35 `list_display_links/list_editable`. Conditions were changed rather than retrying unchanged: the corrected patch extends the final list/fieldsets instead of replacing them.

Corrected `Phase50 Admin Media Mobile CI` run `32875771848`, snapshot `d74683cd54b18cc0f02c3c117515e1a34bc8ec83`:
- compile PASS,
- Django check PASS,
- migration dry-run PASS,
- CI SQLite migration apply PASS,
- Admin media + homepage/mobile tests PASS,
- Windows image-dimension regression PASS.

## Host reconciliation gate
Owner screenshots show Phase50-era Admin UI on `3dprinthub.ir` while earlier docs said Phase50 was undeployed. Before any deploy:
1. verify Production branch/HEAD/worktree read-only,
2. verify Python/Django check,
3. verify MySQL vendor/name,
4. verify `store.0034` status and migrate plan,
5. identify Product Admin 500 from real host evidence,
6. fresh DB backup before any pending migration.

## 50.A.2 — Checkout & Delivery — next after current QA
Persist selected Variant size/build/package snapshots, use effective shipping weight, add normalized carrier quote + immutable order snapshot, Post/Tipax/Mahex only after verified current official API credentials/contracts, preserve ShippingMethod fallback.

## 50.A.3 — Secure Store ZarinPal
Reuse server-owned amount/currency, random callback identity, exact Authority, server-to-server verify and idempotency. Add trusted redirect host allowlist; never capture/store card/PIN/CVV.

## 50.A.4 — Torob
Implement current official Torob Product API v3, stable Product/Variant identifiers, size/color/material, price/availability and image-quality contract.

## Remaining Phase50
- 50.B Accounting core: کل/معین/تفصیلی, fiscal periods, balanced vouchers, immutable posting/reversal.
- 50.C Treasury: bank/cash, receipts/payments, allocations/refunds/reconciliation.
- 50.D Purchasing: suppliers, purchase orders/invoices/receiving/payables/returns.
- 50.E Sales accounting: receivables, payment allocation, tax/discount/shipping, credit notes.
- 50.F Reports/close: GL/subledger, trial balance, aging, cashflow, profitability, VAT/tax, fiscal close.

## Must not touch
- no direct Production source edit,
- no public exposure of imported working-media,
- no destructive historical order/payment/ledger reset,
- no guessed carrier/gateway endpoint,
- no Production migration without exact DB/plan/backup/rollback verification.
