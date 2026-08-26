# PROJECT ROADMAP

Updated: 2026-08-26
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Epic: `Phase50 — Finance, Commerce & Admin Command Center`
Current Phase: `50.A.2B — Immutable Checkout/Profile/Shipping Snapshot`
Status: `GITHUB CI TESTED / PRODUCTION MIGRATION AUDIT NEXT`

## Permanent delivery order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI/LOCAL TEST → OWNER QA → HOST READ-ONLY VERIFY → BACKUP → DEPLOY FROM GITHUB → PRODUCTION VERIFY → DOCUMENT`

## Phase50.A — Admin and commerce operational completeness
- 50.A.1 Admin Storefront/Hero parity — DEPLOYED.
- 50.A.1B Product Gallery + Variant2 — DEPLOYED; `store.0034` applied.
- 50.A.1C Admin media/mobile/SEO/Windows dimensions — DEPLOYED.
- 50.A.1D Sales Profiles + Hero public media — DEPLOYED; `store.0035` applied.
- 50.A.1E Unified Product Admin Workspace — PRODUCTION VERIFIED.
- 50.A.1F Business Admin Navigation + Product Admin 500 hotfix — PRODUCTION VERIFIED.
- 50.A.1G Velzon Operator Surface V2 — PRODUCTION FOUNDATION.
- 50.A.1H Admin Shell Stability — PRODUCTION VERIFIED.
- 50.A.2A Storefront Sales Profile Selector — PRODUCTION VERIFIED.

Current Production application commit remains `c283864290f9c989a9fcdf24ee8eef519560e917`; `0034` and `0035` are applied and 50.A.2B is not yet deployed.

## 50.A.2B — Immutable Checkout/Profile/Shipping Snapshot — GITHUB CI TESTED
Migration `store.0036_phase50_checkout_snapshot` adds explicit immutable order-state fields while preserving the mature Phase6 checkout contract.

### StoreOrderItem snapshot
- sales profile name/key/label,
- profile selection mode and customer-visible selection value,
- final part weight,
- effective shipping weight,
- print time,
- existing `0034` size/build/packaging weight/package dimensions are now populated during checkout finalization.

### StoreOrder snapshot
- `insured_value`,
- normalized `shipping_quote_snapshot` JSON.

### Runtime behavior
- Cart totals use `ProductVariant.effective_shipping_weight_grams`, including packaging weight when explicit shipping override is absent,
- final checkout remains driven by the mature Phase6 form, coupon validation, inventory reservation, address, notification and payment flow,
- successful checkout is finalized inside an outer atomic boundary before response commit,
- ShippingMethod/rate rules remain the current fallback quote authority,
- quote snapshot records destination, merchandise/insured value, total weight, fee and per-line package snapshots,
- combined parcel dimensions are deliberately not inferred from multiple products/quantities,
- pending payment amount is synchronized to the finalized total,
- no external Post/Tipax/Mahex request occurs in this phase.

Verification: GitHub Actions `Phase50 Variant2 Gallery CI` run `32966720475` PASS on `fba0631e60bce1f6e3f622317b70c2f7f35d978f`; compile, Django check, migration state/plan, SQLite migration through `0036`, Variant2/gallery/profile-selector tests and checkout snapshot integration tests all PASS.

### Production gate for 50.A.2B
1. Read-only verify actual Host HEAD/worktree/live GitHub SHA and MySQL `0034/0035/0036` state.
2. Verify exact migration plan and MySQL backup capability.
3. Fresh source + `.env*` + MySQL backup; preserve rollback HEAD.
4. Explicit branch fetch to `FETCH_HEAD` per ERR-50-007; verify ff-only target.
5. Apply only approved `store.0036_phase50_checkout_snapshot` after backup and exact DB verification.
6. Passenger restart and Production schema/runtime/HTTP/order-snapshot verification without altering historical paid orders.

## Product engagement package — NEXT AFTER 50.A.2B
- Favorite/Save model if absent,
- Product like/save/review/comment counters and Admin visibility,
- qualifying purchased/paid Product policy for buyer feedback,
- preserve ProductLike/ProductComment/ProductReview,
- dedicated migration/tests/backup.

## 50.A.3 Secure Store ZarinPal
Server-owned amount, exact callback/Authority verification, idempotency and trusted gateway-host allowlist; never store card/PIN/CVV.

## 50.A.4 Torob
Official Product API v3 with stable Product/Profile identity, price/availability and image-quality contract.

## Phase50.B–F
Accounting Core → Treasury → Purchasing/Payables → Sales/Receivables → Reports/Close.

## Safety
No Production schema work without exact MySQL verification, migration plan, successful fresh backup and rollback target. Imported Catalog working-media remains private. No guessed carrier/gateway endpoint. Purchased/private Velzon/font assets stay out of public GitHub. Production branch fetch uses explicit live branch → `FETCH_HEAD` because host `remote.origin.fetch` remains tag-only.
