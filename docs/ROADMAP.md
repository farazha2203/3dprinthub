# PROJECT ROADMAP

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Epic: `Phase50 — Finance, Commerce & Admin Command Center`
Current Phase: `50.A.1C — Admin media integrity + mobile Hero + homepage SEO + Windows image dimensions`
Status: `GITHUB CI TESTED / HOST AUDIT + MANUAL QA NEXT`

## Permanent delivery order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI/LOCAL TEST → OWNER QA → HOST READ-ONLY VERIFY → BACKUP → DEPLOY FROM GITHUB → PRODUCTION VERIFY → DOCUMENT`

## Phase49 closeout baseline
Structured Product/Catalog/Hero/SEO/Bridge is operational. Product-owned public media remains the Production contract; imported Catalog working-media is not a public namespace.

## Phase50.A — Admin and commerce operational completeness
### 50.A.1 Admin Storefront / Hero parity — CI TESTED
- `/admin/command-center/`,
- Product/imported-asset add/remove Hero,
- Hero 5-random / 10-random / deactivate-all,
- Coupon, ShippingMethod, PricingSetting, StoreAddress and Iran location Admin links.

### 50.A.1B Product Gallery + Variant 2.0 — CI TESTED
- contain-fit Product viewer + thumbnail swap + fullscreen lightbox,
- `size_label`, build profile, packaging weight and parcel dimensions,
- StoreOrderItem commerce snapshots,
- migration `store.0034_phase50_variant2_commerce`,
- Variant Admin and public variant metadata endpoint.

### 50.A.1C Admin media / mobile / SEO / Windows dimensions — CI TESTED
- ImportedPrintAsset Admin no longer renders private `store/imported-models/...` working files as public previews,
- safe preview order: matching Product gallery → Product main image → source HTTP(S) image,
- imported-model list/change views preserve mature Phase35 editable pricing/editorial controls and add public-media/data-completeness status,
- imported image inline shows source pixel dimensions,
- mobile Hero caption/title is substantially smaller; very narrow phones hide the description to preserve Product-image visibility,
- SiteSetting Admin keeps existing homepage `meta_title/meta_description` and adds SEO length audit, SERP preview and Hero Alt/title audit,
- Windows Product image cards now show original pixel dimensions,
- no new migration in 50.A.1C,
- CI run `32875771848` PASS on corrected code snapshot `d74683cd54b18cc0f02c3c117515e1a34bc8ec83`.

### Immediate host reconciliation — BEFORE DEPLOY
Owner screenshots show Phase50-era Admin UI on Production while repository docs previously said Phase50 was undeployed, and `/admin/store/product/` currently returns 500. Read-only verify exact Production branch/HEAD, worktree, MySQL DB and whether `store.0034` is applied/pending. Do not guess the 500 cause.

### 50.A.2 Checkout & Delivery — NEXT AFTER CURRENT QA
- snapshot size/build/package into finalized order items,
- effective product + packaging shipping weight,
- parcel dimensions / insured value,
- normalized carrier quote + immutable order snapshot,
- Post / Tipax / Mahex only with verified official contracts/credentials,
- fallback to mature ShippingMethod rules.

### 50.A.3 Secure Store ZarinPal
Reuse mature server-owned amount, callback identity, Authority matching, server-to-server verify, idempotency and audit. Add trusted redirect-host allowlist and never collect/store card/PIN/CVV.

### 50.A.4 Torob
Torob Product API v3, stable product/variant grouping, size/color/material, price/availability, image-quality guards and official order attribution contract.

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
No Production schema work without exact MySQL verification, migration plan, successful fresh backup and rollback target. Do not widen public media routing to imported Catalog working-media. No guessed carrier endpoint.
