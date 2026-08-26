# CURRENT PROJECT STATE

Updated: 2026-08-26
Repository: `farazha2203/3dprinthub`
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Release: `Phase50.A.2B — Immutable Checkout/Profile/Shipping Snapshot`
Status: `GITHUB CI TESTED / PRODUCTION MIGRATION AUDIT NEXT`

## Production state — terminal verified
Current Production application commit: `c283864290f9c989a9fcdf24ee8eef519560e917`.

Verified Production environment:
- root `/home/sfkilvrs/3dprinthub`,
- venv `/home/sfkilvrs/virtualenv/3dprinthub/3.12`, Python 3.12.13, Django 6.0.7,
- MySQL `sfkilvrs_EmiAdmin_3dprinthub`,
- `store.0034_phase50_variant2_commerce` applied,
- `store.0035_phase50_sales_profiles` applied,
- `store.0036_phase50_checkout_snapshot` NOT YET DEPLOYED/APPLIED,
- clean Production worktree,
- Home/Store/Admin/Product/Variant API verified HTTP/runtime healthy,
- public Home private imported-media refs = 0.

Latest verified Production rollback backup: `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-143650`.
A fresh backup is mandatory again before applying `0036`.

## Phase50.A.1H — Admin Shell Stability — PRODUCTION VERIFIED
- footer normal/static flow instead of vendor absolute positioning,
- stable Admin flex/min-height shell,
- right sidebar 290px,
- active-menu scrolling constrained to the internal sidebar,
- Velzon V2 on-demand filter/full-width tables preserved.

## Phase50.A.2A — Storefront Sales Profile Selector — PRODUCTION VERIFIED
- customer Product page exposes configured profile/size/build/weight/material/color/quality choices,
- `/store/api/variant-commerce-options/` remains authoritative,
- selected choice resolves to canonical ProductVariant ID and existing Cart/AddToCartForm,
- Production sample `shoe-holder-organiser` / Variant 1 verified through public API.

## Phase50.A.2B — Immutable Checkout/Profile/Shipping Snapshot — GITHUB CI TESTED
Implemented additively without rewriting mature `store/models.py` or the Phase6 checkout implementation.

### Schema — migration `store.0036_phase50_checkout_snapshot`
Adds immutable StoreOrderItem snapshots:
- `sales_profile_name`, `sales_profile_key`, `sales_profile_label`,
- `sales_profile_selection_mode`, `sales_profile_selection_value`,
- `final_weight_grams`, `shipping_weight_grams`, `print_time_minutes`.

Adds StoreOrder snapshots:
- `insured_value`,
- `shipping_quote_snapshot` JSON.

Existing `0034` item snapshots remain authoritative for size/build/packaging weight/package dimensions.

### Runtime contract
`store/phase50_checkout_snapshot.py` follows the existing additive Phase50 runtime-field pattern and installs a final Checkout/Cart wrapper:
- Cart summary uses `ProductVariant.effective_shipping_weight_grams`, so packaging weight is included when no explicit shipping override exists,
- mature Phase6 checkout still owns validation, coupon, inventory reservation, address, notifications, payment creation and redirects,
- successful checkout is enclosed by an outer atomic boundary and then finalized before response commit,
- item snapshots freeze the customer-visible sales profile, selection mode/value, size/build, material/color/quality, final/package/shipping weights, print time and per-unit package dimensions,
- `StoreOrder.total_weight_grams` is recomputed from effective per-unit shipping weight,
- current `ShippingMethod`/rate rules remain the fallback shipping authority,
- `shipping_quote_snapshot` records normalized method/destination/value/weight/fee and per-line package snapshots,
- no combined carton geometry is invented; `combined_parcel_dimensions_inferred=false` and multi-item/multi-quantity orders require final packing,
- `insured_value` currently freezes merchandise value after order discount,
- pending StorePayment amount is kept synchronized if effective shipping weight changes the shipping fee,
- any unexpected finalizer exception rolls back the DB transaction and restores the session cart.

### External carrier boundary
No Post/Tipax/Mahex endpoint, tariff or credential is guessed or called in 50.A.2B. `shipping_quote_snapshot.source` is explicitly `shipping_method_fallback` and `external_carrier_quote=false`. Official carrier adapters remain future work after verified contracts/credentials.

### Verification
GitHub Actions `Phase50 Variant2 Gallery CI` run `32966720475` PASS on runtime/CI snapshot `fba0631e60bce1f6e3f622317b70c2f7f35d978f`:
- Python compile PASS,
- Storefront JavaScript syntax PASS,
- Django check PASS,
- migration state matches runtime models,
- migration plan PASS,
- migrations through `0036` apply in CI SQLite,
- Variant2/gallery/profile-selector regressions PASS,
- new checkout snapshot integration regressions PASS,
- immutable snapshot after later Variant mutation PASS,
- effective product + packaging shipping weight PASS,
- normalized ShippingMethod fallback quote/payment synchronization PASS.

## Known operational incidents
- `ERR-50-007`: Production remote fetch refspec is stale/tag-only; use live `ls-remote` + explicit branch fetch to `FETCH_HEAD` + ff-only.
- `ERR-50-010`: avoid cPanel `/dev/fd` process substitution for backup enumeration; use Python filesystem copy.
- `ERR-50-011`: JSON verifier must use `python - <args>` and `json.load`, never execute JSON as Python.

Known warnings remain CKEditor4 maintenance/security debt, `store.W026` in-memory realtime debt and MySQL conditional-constraint warnings.

## Exact next work
1. Production read-only audit: exact Host HEAD/worktree, live GitHub SHA, MySQL database, current `0034/0035/0036` state, migration plan and backup capability.
2. If clean: fresh source/.env/MySQL backup, explicit branch fetch to `FETCH_HEAD`, verify ff-only target and exact `0036` plan, apply only approved `store.0036_phase50_checkout_snapshot`, collectstatic if needed, Passenger restart.
3. Production integration verification using a controlled test order or read-only schema/runtime probes; do not modify historical paid orders.
4. Then Product engagement package: Favorite/Save + like/save/review/comment counters + verified-purchase buyer-feedback policy.
5. Continue secure Store ZarinPal → Torob Product API v3 → accounting core.
