# Phase50 — Finance, Commerce & Admin Command Center

Updated: 2026-08-27  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Current Subphase: `50.A.2D — Product Profile Matrix + Dependent Storefront Selector`  
Status: `GITHUB CI TESTED / OWNER LOCAL QA NEXT / PRODUCTION MIGRATION CHAIN BLOCKED UNTIL QA + BACKUP`

Current verified Production application commit:
`c283864290f9c989a9fcdf24ee8eef519560e917`.

Last verified Production MySQL `sfkilvrs_EmiAdmin_3dprinthub` state:
- `store.0034_phase50_variant2_commerce` applied,
- `store.0035_phase50_sales_profiles` applied,
- `store.0036_phase50_checkout_snapshot` pending at last verify,
- `0037` and `0038` were created after that verify and are not claimed applied.

## Preserved foundation
- Product/Catalog/Bridge/Hero public media is Product-owned; imported Catalog working-media remains private.
- Product, ProductCatalogProfile and ProductVariant remain authoritative.
- mature Phase6 Checkout, Coupon/VAT, StoreOrder/StorePayment/StoreInvoice, inventory reservation, addresses and notifications remain authoritative.
- no permanent Production source edits.
- purchased/private Velzon/font assets remain private/gitignored.
- Admin shell footer/290px sidebar/internal menu scroll and initial Storefront Profile selector remain Production verified at `c283864...`.

## 50.A.2B — Immutable Checkout/Profile/Shipping Snapshot
Migration:
`store.0036_phase50_checkout_snapshot`.

Adds immutable order state for:
- profile name/key/label,
- selection mode/value,
- final/effective shipping weight,
- print time,
- insured value and normalized shipping quote.

Reuses `0034` item size/build/package fields.

Runtime:
- wraps mature checkout rather than replacing it,
- successful checkout finalizes inside an outer transaction,
- packaging weight participates in shipping weight unless explicit shipping override exists,
- Coupon/VAT/inventory/payment/notification logic remains authoritative,
- no combined carton geometry or external carrier quote is invented.

## 50.A.2C — Professional Commerce Policy
Migration:
`store.0037_phase50_professional_commerce_policy`.

Adds:
- Product pricing policy: formula/product fixed/profile fixed/profile+material/profile+material+color,
- Product sales notice,
- optional strict color-stock enforcement,
- ProductVariant fixed price override,
- shipping service type/scope/fee mode/address/postal/customer notice,
- StorePaymentSettings,
- safe shipping presets with Post/Tipax disabled by default until operator configuration.

Runtime bug fixed:
- saved-address checkout now validates shipping policy against the actual persisted address rather than empty new-address form fields (`ERR-50-013`).

## 50.A.2D — Product Profile Matrix
Migration:
`store.0038_phase50_profile_matrix`.

### Requested delta
A single Product may have many customer-selectable production Profiles, for example:
- size 20 cm → 100 g / 150 g / 200 g,
- size 30 cm → 150 g / 200 g / 300 g,
- optionally deeper build/material/color/quality combinations.

Every Profile is a real orderable Variant with its own price and production/shipping facts.

### Windows / Catalog contract
Phase49.3I.34 adds a Step-2 Profile editor:
- + new Profile,
- clone selected Profile,
- delete Profile,
- edit Profile,
- one default Profile,
- active/inactive and sort order.

Per Profile:
- name/description/key,
- size label,
- final/material weight,
- print time,
- fixed price,
- actual part L/W/H,
- build profile,
- material/color/quality,
- packaging/shipping weights,
- package L/W/H,
- stock mode/quantity.

The Product-owned Profile list persists as `sales_profiles_json` in Catalog SQLite and is included in the mature editorial batch payload.

### Django / Store contract
Desktop-managed Profiles are synchronized into canonical `ProductVariant` rows:
- stable `sales_profile_key` identifies a Profile,
- collision-safe Desktop-managed Variant codes,
- republish updates existing Profile rows,
- removed Desktop Profiles are deactivated only inside the Desktop-managed namespace,
- unrelated manual server Variants remain untouched,
- first/explicit default Profile is preserved,
- invalid stock/material/quality/color state fails closed instead of silently inventing a mapping.

Product is switched to Variant order mode and Profile pricing policy when Profile fixed prices exist.

### Storefront contract
Supported Profile modes:
- list,
- size,
- weight,
- build,
- size→build,
- build→size,
- size→weight,
- weight→size,
- size→weight→build,
- size→build→weight.

The selected Profile is the single displayed price/facts authority.

Professional Profile summary includes:
- Profile name/description,
- price,
- size,
- build,
- material/color/quality,
- final weight,
- actual part dimensions,
- effective shipping weight,
- print time,
- package dimensions.

Dependent selector semantics:
- each option group is filtered only by the choices before it,
- downstream selections never hide valid upstream options,
- changing size clears/re-resolves downstream state to a valid canonical Variant,
- weight/Profile price badges are calculated only from the active upstream prefix,
- native Variant select remains the fallback contract.

### Checkout snapshot extension
`0038` adds immutable part L/W/H fields to StoreOrderItem. A later ProductVariant edit cannot mutate the ordered Profile dimensions.

## Verification

### Web runtime
Snapshot:
`7d0a2a1125e8f38771ba325427d1efa8b8d07da6`.

GitHub Actions:
`Phase50 Variant2 + Profile Matrix CI` run `33051311828` PASS.

Gates:
- touched Python compile PASS,
- Storefront JS syntax PASS,
- `PHASE50_PROFILE_SELECTOR_HIERARCHY=PASS`,
- Django check PASS with known warning debt only,
- no model/migration drift,
- CI migration through `0038` PASS,
- 15 Variant/Profile/Checkout tests PASS.

### Windows runtime
Catalog Center:
- version `8.9.0`,
- build `2026.08.27.2`,
- packaged snapshot `b3280dd67cd7772f337f6792036ea92d3f252747`,
- workflow `33051114515` PASS,
- artifact ID `9637671099`,
- EXE SHA256 `32aed719e6d374447fc4b05f09a30fe12f0ce4dc05e570382f2e74036044900c`.

Public GitHub Release remains manual-only after owner Local QA.

## Resolved incidents in this subphase
- `ERR-50-012`: API executed bound pricing contract incorrectly → call canonical `price_breakdown()`.
- `ERR-50-013`: saved-address checkout rejected by wrapper → resolve persisted address facts.
- `ERR-50-014`: selector downstream state constrained upstream choices / cross-size price badge → prefix filtering and upstream-scoped price pool.
- `ERR-50-015`: packaged Windows workflow omitted mature Product studio trigger paths → watch both files.

## Must-not-touch
- historical paid orders,
- mature Coupon/VAT logic,
- inventory reservation,
- public/private media boundary,
- secrets,
- external Post/Tipax pricing without verified official contract/credentials,
- purchased/private Velzon/font assets,
- manual non-Desktop ProductVariants.

## Production deployment gate
1. Owner Local Windows and Django QA on the exact current GitHub head.
2. Read-only verify Host branch/HEAD/worktree/live remote SHA.
3. Verify exact effective MySQL DB and actual `0034..0038` migration rows.
4. Run exact migration plan and stop on any unapproved operation.
5. Verify disk and `mysqldump`.
6. Fresh tracked-source + `.env*` + MySQL backup, gzip/checksum, rollback HEAD.
7. Explicit branch fetch to `FETCH_HEAD` per `ERR-50-007`; verify exact target and ff-only ancestry.
8. Deploy source from GitHub.
9. Re-run Django check/drift/DB/plan.
10. Apply only verified pending chain `0036 → 0037 → 0038`.
11. `collectstatic --noinput`.
12. Passenger restart.
13. Verify Home/Store/Admin/Product/Profile API/Checkout/static/private-media.
14. Controlled new-order QA with one multi-size/multi-weight Product; do not rewrite old orders.
15. Owner visual QA.
16. Update Production docs with exact deployed SHA, backup path and migration rows.

## Following Phase50 work
After 50.A.2D Production verification:
- Product Engagement,
- Secure ZarinPal,
- Torob Product API,
- Accounting/Treasury/Purchasing/Sales/Reports.

## Canonical host constraints
- `ERR-50-007`: tag-only fetch refspec → live branch + explicit `FETCH_HEAD`.
- `ERR-50-010`: no reliable cPanel `/dev/fd` process substitution.
- `ERR-50-011`: JSON is data; verify with `python -` + `json.load`.
