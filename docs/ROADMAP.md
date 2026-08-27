# PROJECT ROADMAP

Updated: 2026-08-27  
Repository: `farazha2203/3dprinthub`  
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Current Web Epic: `Phase50 — Finance, Commerce & Admin Command Center`  
Current Web Phase: `50.A.2D — Product Profile Matrix + Dependent Storefront Selector`  
Parallel Windows Phase: `49.3I.34 — Step-2 Product Profile Matrix / Catalog Center 8.9.0`  
Status: `GITHUB CI TESTED / WINDOWS PACKAGED CI PASS / OWNER LOCAL QA NEXT / PRODUCTION BLOCKED`

## Permanent delivery order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI/LOCAL TEST → OWNER QA → HOST READ-ONLY VERIFY → BACKUP → DEPLOY FROM GITHUB → VERIFY PRODUCTION → DOCUMENT`

## Phase49 Windows track — current target 49.3I.34
Preserved foundations:
- 48-card paged Product Explorer,
- no global Product refresh on each Product Save/AI action,
- exact saved mother AI Provider/Model/key with no hidden cross-provider fallback,
- exact-link grounded Product AI,
- source-link preserve/recover guard,
- local Product identity/history preservation,
- selected-Product bulk AI with isolated errors and one final refresh.

49.3I.34 adds:
- Product-owned Step-2 profile matrix,
- add/clone/delete/edit profiles,
- independent per-profile size, weight, fixed price, print time, part dimensions, build, material, color, quality, package and stock settings,
- customer-selection modes including size→weight and 3-level modes,
- batch transport of the exact profile JSON to Django,
- profile/range minimum as valid publish readiness price.

Windows package verification:
- runtime snapshot `b3280dd67cd7772f337f6792036ea92d3f252747`,
- workflow `33051114515` PASS,
- version `8.9.0`, build `2026.08.27.2`,
- artifact ID `9637671099`,
- EXE SHA256 `32aed719e6d374447fc4b05f09a30fe12f0ce4dc05e570382f2e74036044900c`,
- public Release publication remains explicit/manual after owner Local QA.

## Phase50.A — Admin and commerce operational completeness
Production verified foundation:
- 50.A.1 Admin Storefront/Hero parity,
- 50.A.1B Gallery + Variant2 / `0034`,
- 50.A.1D Sales Profiles / `0035`,
- unified Product Admin,
- Admin 500 hotfix/business navigation,
- Velzon V2 lists/filter drawer,
- stable footer/290px sidebar/internal menu scroll,
- initial canonical Storefront Profile selector.

Current Production application commit remains:
`c283864290f9c989a9fcdf24ee8eef519560e917`.

Last verified Production DB has only `store.0034` + `store.0035` from the new Phase50 chain.

## 50.A.2B — Immutable Checkout/Profile/Shipping Snapshot
`store.0036_phase50_checkout_snapshot`
- immutable selected profile/size/build/material/color/quality,
- final/package/effective shipping weight,
- print time/package facts,
- order insured value and normalized shipping quote,
- mature Coupon/VAT/inventory/payment flow preserved.

## 50.A.2C — Professional Commerce Policy
`store.0037_phase50_professional_commerce_policy`
- Product pricing-policy authority,
- per-Variant fixed price override,
- customer sales notice,
- optional strict color-stock rule,
- shipping service/scope/fee semantics,
- safe default Isfahan pickup/courier + disabled Post/Tipax presets,
- Store payment-display settings,
- saved-address shipping-policy validation fixed at the mature form boundary.

## 50.A.2D — Product Profile Matrix — GITHUB CI TESTED
`store.0038_phase50_profile_matrix`
- size/weight/build compound selection modes,
- per-Variant profile description,
- actual part dimensions,
- immutable ordered-item part dimensions,
- Desktop profile JSON → canonical ProductVariant upsert,
- per-profile fixed price and Profile as single Storefront price/facts authority,
- dependent selector hierarchy: downstream choices filter only from upstream choices,
- size-scoped weight/profile prices,
- professional navy/gold Profile UI aligned visually with Catalog Center,
- manual server variants remain preserved.

Web runtime verification:
- snapshot `7d0a2a1125e8f38771ba325427d1efa8b8d07da6`,
- `Phase50 Variant2 + Profile Matrix CI` run `33051311828` PASS,
- `PHASE50_PROFILE_SELECTOR_HIERARCHY=PASS`,
- no migration drift,
- migrations through `0038` apply on CI SQLite,
- 15 Store/Profile/Checkout tests PASS.

## Production gate for 50.A.2B–2D
1. Owner Local Windows/Django QA on exact current GitHub head.
2. Read-only Host verify: root, branch, HEAD, clean worktree, live branch SHA, Python/Django, exact MySQL DB and actual `0034..0038` migration state.
3. Inspect exact migration plan; do not assume `0036/0037/0038` are still pending.
4. Verify disk + `mysqldump`.
5. Fresh tracked-source + environment + MySQL backups with checksums and rollback HEAD.
6. Explicit branch fetch to `FETCH_HEAD` per `ERR-50-007`; verify exact SHA and ff-only ancestry.
7. Deploy approved GitHub snapshot.
8. Re-run Django check/drift/plan; apply only verified pending `0036 → 0037 → 0038`.
9. `collectstatic --noinput`, Passenger restart.
10. Verify Home/Store/Admin/Product/Profile API/Checkout/static/private-media and a controlled new order.
11. Owner browser QA of dependent size/weight prices and Profile presentation.
12. Update Production docs.

## Following business packages
After 50.A.2D Production verification:
- Product Engagement: Favorite/Save + counters + verified-purchased buyer feedback,
- 50.A.3 Secure ZarinPal,
- 50.A.4 Torob Product API v3,
- 50.B Accounting Core,
- 50.C Treasury,
- 50.D Purchasing/Payables,
- 50.E Sales/Receivables,
- 50.F Reports/Close.

## Safety
No Production schema work without exact MySQL verification, exact migration plan, fresh successful backup and rollback target. Imported Catalog working-media stays private. Purchased Velzon/font assets stay outside public GitHub. Host deploy always uses live branch → explicit `FETCH_HEAD` because the Production refspec remains tag-only.
