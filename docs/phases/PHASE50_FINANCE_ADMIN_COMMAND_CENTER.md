# Phase50 — Finance, Commerce & Admin Command Center

Updated: 2026-08-25
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Subphase: `50.A.1 — Admin Storefront / Hero parity`
Status: `GITHUB CI TESTED / MANUAL QA REQUIRED`
Production: `PHASE49 WEB HEALTHY / PHASE50 UNDEPLOYED`

## Owner request
Complete the business back-office so Django Admin exposes the same mature storefront controls used by Windows/front-end operations, then finish delivery pricing, discounts/VAT and secure online payment before continuing the accounting core.

Explicit current requests:
- add/remove Product from homepage slider from Admin,
- 5-random and 10-random Product Hero controls,
- professional Admin access to front-end commerce/settings surfaces,
- preserve the mature customer portal and Iran province/county/city address flow,
- calculate delivery from product + packaging weight/dimensions with Post/Tipax/Mahex when a current supported API exists,
- coupon and VAT visible/operational in checkout,
- phishing-resistant comprehensive payment flow.

## Verified existing foundation
- StoreOrder / StoreOrderItem / StorePayment / StoreInvoice / Shipment / ReturnRequest,
- Coupon validation/discount application already exists,
- PricingSetting VAT and packaging fee already exist,
- ShippingMethod supports fixed and weight-rule pricing already,
- StoreAddress plus IranProvince/IranCounty/IranCity already exist,
- service Order / Quote / Payment and immutable PaymentLedgerEntry,
- online payment already owns amount server-side, locks attempts, uses random callback tokens, validates Authority and requires server-to-server provider verification before paid state,
- Production Django security already enables HTTPS redirect/HSTS/Secure cookies/SameSite/HttpOnly/nosniff/DENY framing when DEBUG is off,
- Filament purchasing, inventory, production cost and affiliate ledgers remain mature sources for Phase50 accounting.

## 50.A.1 Requested Delta
Make Storefront/Hero/Checkout operations professional and directly reachable from Django Admin without changing schema or healthy public rendering.

### Touched surfaces
- `website/phase50a_admin_command_center.py`,
- `website/phase50a_storefront_admin_parity.py`,
- `config/urls.py`,
- `website/apps.py`,
- `templates/admin/website/homepageheroslide/change_list.html`,
- `website/test_phase50a_admin_command_center.py`,
- `website/test_phase50a_storefront_admin_parity.py`,
- `.github/workflows/phase50-admin-storefront-ci.yml`.

### Implemented
- authenticated `/admin/command-center/`,
- Sales / Storefront & Checkout / Treasury / Accounting / Purchasing / Inventory sections,
- permission-aware real links,
- Product bulk actions: add selected to Hero / remove selected from Hero,
- Imported Catalog Asset bulk actions: add/remove from Hero,
- Hero quick buttons: 5 random, 10 random, deactivate all,
- random selection only from active Product-backed and public-image-capable Catalog assets,
- existing manually edited Hero copy preserved when reactivating an existing slide,
- Hero removal is non-destructive deactivation,
- quick mutation routes are POST-only and wrapped by `admin.site.admin_view`,
- Admin exposes Coupon, ShippingMethod, PricingSetting, StoreAddress and Iran location reference areas.

## Regression gate
GitHub Actions `Phase50 Admin Storefront Parity CI` PASS at code snapshot `7c8714b5715cd00900a76b99097823266251d4a2`:
- compile PASS,
- Django check PASS with known warnings only,
- migration dry-run: no changes,
- Phase50 admin tests PASS.

Manual desktop/mobile Admin QA is still required before Production deploy.

## 50.A.2 Checkout & Delivery — next
Design additive shipping quote architecture around the existing ShippingMethod fallback. Required normalized inputs:
- origin/destination province/county/city and postal code,
- sellable item weight,
- packaging weight,
- parcel dimensions,
- insured/order value,
- carrier/service code.

Provider result must snapshot base fee, provider taxes/charges, total, ETA and provider reference onto the finalized order. Direct Post/Tipax/Mahex adapters are only implemented after the current official API contract/credentials are verified. No guessed endpoint will enter Production.

## 50.A.3 Payment hardening/unification
Keep the mature service-payment contract and extend Store checkout to it:
- server-owned amount/currency,
- strict trusted gateway-host allowlist,
- no card number/PIN/CVV collection or storage,
- idempotent request/callback/verify,
- random callback identity + exact provider Authority match,
- server-to-server verification before paid state,
- audit/reconciliation and abuse monitoring,
- Production security-header verification.

## Must not touch
- healthy Catalog/Bridge/Product/Hero public media ownership,
- historical order/payment/ledger data,
- public customer portal address history,
- accounting schema until its own reviewed migration phase,
- Production source directly.

## Remaining Phase50 path
### 50.B Accounting core
Chart of accounts کل/معین/تفصیلی, fiscal periods, balanced journal vouchers, immutable posting/reversal and party/subledger references.

### 50.C Treasury
Bank/cash accounts, receipt/payment vouchers, allocations, refunds and reconciliation.

### 50.D Purchasing
Supplier master, purchase orders/invoices/receiving/payables/returns.

### 50.E Sales accounting
Normalized Store/service receivables, payment allocation, tax/discount/shipping and credit notes.

### 50.F Reports & close
GL/subledger, trial balance, AR/AP aging, cashflow, profitability, VAT/tax and fiscal close.

## Acceptance target
Phase50 is accepted only when commerce operations, delivery/payment calculation and financial posting can be traced without duplicate payment/posting or balance mismatch.
