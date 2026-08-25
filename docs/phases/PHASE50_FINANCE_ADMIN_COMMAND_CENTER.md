# Phase50 — Finance, Commerce & Admin Command Center

Updated: 2026-08-25
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Subphase: `50.A.1D — Sales Profiles + Hero Admin Public Media`
Status: `GITHUB CI TESTED / PRODUCTION DEPLOY REQUIRED`
Production baseline: `5c5c5e1e141fd3ff8df3c079abc55e4593feb41f`, MySQL `store.0034` applied.

## Owner request
Complete storefront/Admin commerce before accounting core. Current priorities: professional Product media, Admin parity, reusable sales profiles with size/weight/build selection, reliable Hero Studio media, mobile Hero, homepage SEO, shipping/VAT/coupon, secure ZarinPal and Torob.

## Preserved foundation
- Product/Catalog/Bridge/Hero public media ownership remains Product-owned.
- Imported Catalog working-media remains private.
- StoreOrder/StorePayment/StoreInvoice and mature coupon/VAT/packaging/shipping calculations remain authoritative.
- customer StoreAddress plus Iran Province/County/City remain intact.
- mature service-payment request/callback/verify/idempotency engine is reused later for Store payment.
- no direct Production source edits.

## 50.A.1 / 50.A.1B / 50.A.1C deployed baseline
- `/admin/command-center/`, Product/imported Asset Hero actions and 5/10 random/deactivate-all.
- Product contain-fit main viewer, thumbnail swap and fullscreen lightbox.
- Variant 2.0 size/build profile/packaging fields and StoreOrderItem snapshots.
- migration `store.0034_phase50_variant2_commerce` applied on Production.
- imported Admin safe preview, mobile Hero compaction, homepage SEO audit, Windows source image dimensions.
- owner deploy verified Home/Store/Admin/Product Admin/Imported Asset Admin/Hero Admin HTTP 200 and no public imported-working-media reference.

## 50.A.1D — Sales Profiles + Hero Admin Public Media
### Requested Delta
1. Allow one Product to have multiple commercial profiles that may share material/color/size/build but differ in weight, print time, price inputs and shipping data.
2. Let the operator choose the customer-facing selection criterion per Product: size, weight, build type, size→build, build→size or a full profile list.
3. Make creating a near-identical profile fast by copying an existing Variant/profile and editing only changed values.
4. Fix Hero Studio change pages where product/album images still used private `store/imported-models/...` URLs and failed to load on Production.

### Implemented
- Product `sales_profile_selection_mode` and optional selector label.
- ProductVariant profile name, stable key, default flag and display order.
- uniqueness now includes `sales_profile_key`, allowing otherwise-identical Variant attributes to coexist as distinct commercial profiles.
- Admin action `کپی پروفایل‌های فروش انتخاب‌شده` clones the selected Variant and generates a new code/profile key; source history is untouched.
- Product Admin and Variant inline expose profile selector/profile fields beside size/build/material/color/weight/print-time/price/stock data.
- Variant metadata endpoint exposes Product selection mode plus profile label/key/default/order, size/build, material/color, weight, print time, calculated unit price, packaging and shipping data.
- migration `store.0035_phase50_sales_profiles` owns the new schema.
- Hero Studio product-browser and asset-detail endpoints are replaced at the final Admin URL boundary; previews use Product-owned public gallery/main media or row-specific remote HTTP(S) source media, never private imported working-media.
- existing Hero selected image IDs, SEO suggestions, cinematic settings and public Hero rendering are preserved.

### Regression gate
GitHub Actions `Phase50 Sales Profiles Hero Admin CI` run `32879712980`, snapshot `405d2c1daa85828d1a0dc68210d201c85b6db7ba` PASS:
- compile PASS,
- Django check PASS,
- migration dry-run PASS,
- migration plan PASS,
- CI SQLite migration apply PASS,
- Sales Profile/Admin/Hero public-media regressions PASS.

### Production gate
Before `store.0035`:
1. verify exact Production HEAD/worktree and live remote HEAD,
2. verify MySQL vendor/name and `0034` applied,
3. fresh successful MySQL backup + rollback commit,
4. deploy committed GitHub snapshot only,
5. confirm `0035` is the expected pending migration and inspect its plan,
6. apply `0035`, collectstatic, Passenger restart,
7. verify Hero Studio images and profile Admin manually.

## 50.A.2 — Checkout & Delivery — next after 50.A.1D QA
- profile-aware selector on Product page,
- persist chosen profile/size/build/package snapshots,
- effective product + packaging shipping weight,
- normalized carrier quote + immutable order snapshot,
- Post/Tipax/Mahex only after verified current official API credentials/contracts,
- preserve ShippingMethod fallback.

## 50.A.3 — Secure Store ZarinPal
Reuse server-owned amount/currency, random callback identity, exact Authority, server-to-server verify and idempotency. Add trusted redirect host allowlist; never capture/store card/PIN/CVV.

## 50.A.4 — Torob
Implement official current Torob Product API v3 using stable Product/profile identifiers, size/color/material/weight, price/availability and image-quality contract.

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
