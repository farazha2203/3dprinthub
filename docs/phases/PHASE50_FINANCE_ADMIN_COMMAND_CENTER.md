# Phase50 — Finance, Commerce & Admin Command Center

Updated: 2026-08-26
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Subphase: `50.A.2B — Immutable Checkout/Profile/Shipping Snapshot`
Status: `GITHUB CI TESTED / PRODUCTION MIGRATION AUDIT NEXT`

Current Production application commit: `c283864290f9c989a9fcdf24ee8eef519560e917`.
Production MySQL `sfkilvrs_EmiAdmin_3dprinthub` has `store.0034_phase50_variant2_commerce` and `store.0035_phase50_sales_profiles` applied. `store.0036_phase50_checkout_snapshot` exists on GitHub but is NOT yet applied on Production.

## Preserved foundation
- Product/Catalog/Bridge/Hero public media is Product-owned; imported Catalog working-media remains private.
- Product, ProductCatalogProfile and ProductVariant remain authoritative.
- mature Phase6 Checkout, Coupon/VAT, StoreOrder/StorePayment/StoreInvoice, inventory reservation, addresses and notifications remain authoritative.
- no direct Production source edits.
- purchased/private Velzon/font assets stay private/gitignored.

## 50.A.1H — Admin Shell Stability — PRODUCTION VERIFIED
Footer normal flow, stable shell, 290px right sidebar and internal-only sidebar scrolling are deployed at `c283864...` with CI `32958276378` PASS.

## 50.A.2A — Storefront Sales Profile Selector — PRODUCTION VERIFIED
Customer profile/size/build/weight/material/color/quality selector is deployed at `c283864...`, uses `/store/api/variant-commerce-options/`, keeps canonical ProductVariant ID and native fallback. Storefront CI `32958296546` PASS.

## 50.A.2B — Immutable Checkout/Profile/Shipping Snapshot — GITHUB CI TESTED
### Requested delta
The customer selection must not disappear or mutate after checkout. Shipping must use the exact effective ProductVariant weight including packaging, while preserving current Coupon/VAT/inventory/payment behavior and not inventing external carrier contracts.

### Schema
Migration `store.0036_phase50_checkout_snapshot` adds:

StoreOrderItem:
- `sales_profile_name`,
- `sales_profile_key`,
- `sales_profile_label`,
- `sales_profile_selection_mode`,
- `sales_profile_selection_value`,
- `final_weight_grams`,
- `shipping_weight_grams`,
- `print_time_minutes`.

Existing `0034` snapshot fields are reused for:
- `size_label`,
- `build_profile`,
- `packaging_weight_grams`,
- package length/width/height.

StoreOrder:
- `insured_value`,
- `shipping_quote_snapshot` JSON.

### Runtime architecture
`store/phase50_checkout_snapshot.py` follows the additive Phase50 model pattern:
- model fields are contributed at app setup and owned by migration `0036`,
- Cart item weights are normalized through `ProductVariant.effective_shipping_weight_grams`,
- mature final Phase6 `checkout_view` is wrapped rather than copied/replaced,
- POST checkout executes inside an outer atomic transaction; mature inner checkout performs validation/coupon/inventory/order/payment/notification work,
- before the response transaction commits, the created order is locked and finalized with immutable profile/package/weight snapshots,
- unexpected finalizer errors rollback DB work and restore the session cart.

### Shipping snapshot semantics
- `StoreOrder.total_weight_grams` = sum of effective per-unit shipping weight × quantity,
- explicit ProductVariant shipping weight remains authoritative when non-zero,
- otherwise final/material weight + packaging weight is used,
- current ShippingMethod/rate rules remain the fallback fee authority,
- `insured_value` freezes merchandise value after order discount,
- `shipping_quote_snapshot.source = shipping_method_fallback`,
- `external_carrier_quote = false`,
- destination, merchandise/insured value, total weight, fee and each line/package snapshot are frozen,
- combined carton dimensions are NOT guessed; per-unit package dimensions are retained and multi-item/multi-quantity orders are marked as requiring final packing,
- pending payment amount is synchronized with the finalized total.

### Must-not-touch
- do not alter historical paid orders,
- do not replace Coupon/VAT logic,
- do not bypass inventory reservation,
- do not expose imported working-media,
- do not call or claim Post/Tipax/Mahex without verified official API credentials/contracts,
- do not apply `0036` on Production without exact MySQL/plan/backup/rollback verification.

### Verification
GitHub Actions `Phase50 Variant2 Gallery CI` run `32966720475` PASS on snapshot `fba0631e60bce1f6e3f622317b70c2f7f35d978f`:
- touched Python compile PASS,
- Storefront JS syntax PASS,
- Django check PASS,
- `makemigrations --check --dry-run` PASS,
- migration plan PASS,
- migrations through `0036` apply on CI SQLite,
- Variant2/gallery/profile-selector regressions PASS,
- checkout profile/package/shipping snapshot integration PASS,
- snapshot immutability after later Variant edits PASS.

## Production deployment gate for 50.A.2B
1. Read-only verify actual Host branch/HEAD/worktree and live GitHub SHA.
2. Verify MySQL vendor/name, applied `0034/0035`, actual `0036` state and exact plan.
3. Verify mysqldump and disk; create fresh source/.env/MySQL rollback backup.
4. Explicitly fetch active branch to `FETCH_HEAD` because of ERR-50-007 and verify ff-only ancestry.
5. Deploy approved GitHub snapshot.
6. Re-run Django/model drift/DB gate and inspect exact `store 0036` migration plan.
7. Apply only `store.0036_phase50_checkout_snapshot` if pending.
8. Passenger restart; verify Home/Store/Admin/Product/Checkout and new DB/runtime fields.
9. Controlled new-order QA may be used after schema deployment; never rewrite existing paid order snapshots.
10. Update Production documentation.

## Next after 50.A.2B
### Product Engagement
Favorite/Save + like/save/review/comment counters + verified-purchased/paid buyer-feedback policy, preserving existing ProductLike/ProductComment/ProductReview, with dedicated migration/tests/backup.

### 50.A.3 Secure ZarinPal
Server-owned amount/currency, random callback identity, exact Authority, server-to-server verify, idempotency and trusted redirect-host allowlist; never store card/PIN/CVV.

### 50.A.4 Torob
Official Product API v3 with stable Product/Profile identity, price/availability and image-quality contract.

### 50.B–50.F
Accounting Core → Treasury → Purchasing/Payables → Sales/Receivables → Reports/Close.

## Canonical host incidents
- ERR-50-007: stale tag-only fetch refspec → live `ls-remote` + explicit branch fetch to `FETCH_HEAD`.
- ERR-50-010: no reliable cPanel `/dev/fd` process substitution → Python filesystem backup enumeration.
- ERR-50-011: JSON is data, not a Python script → `python - <args>` + `json.load`.
