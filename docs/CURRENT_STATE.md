# CURRENT PROJECT STATE

Updated: 2026-08-27  
Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Primary Web/Commerce Release: `Phase50.A.2D — Product Profile Matrix + Dependent Storefront Selector`  
Parallel Windows Track: `Phase49.3I.34 — Step-2 Product Profile Matrix / Catalog Center 8.9.0`  
Status: `GITHUB CI TESTED / WINDOWS PACKAGED CI PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT DEPLOYED`

## Production state — last terminal verified
Current Production application commit remains `c283864290f9c989a9fcdf24ee8eef519560e917`.

Verified Production environment:
- root `/home/sfkilvrs/3dprinthub`,
- venv `/home/sfkilvrs/virtualenv/3dprinthub/3.12`,
- Python 3.12.13 / Django 6.0.7,
- MySQL `sfkilvrs_EmiAdmin_3dprinthub`,
- `store.0034_phase50_variant2_commerce` applied,
- `store.0035_phase50_sales_profiles` applied,
- `store.0036_phase50_checkout_snapshot` not yet Production-applied at last verify,
- `store.0037_phase50_professional_commerce_policy` not yet Production-applied,
- `store.0038_phase50_profile_matrix` not yet Production-applied,
- Home/Store/Admin/Product/Variant API were healthy,
- public imported working-media exposure = 0.

Latest verified Production rollback backup remains:
`/home/sfkilvrs/3dprinthub-deploy-backups/20260826-143650`.

A **fresh** source + environment + MySQL backup is mandatory before any `0036 → 0037 → 0038` Production migration.

## Current GitHub runtime candidates

### Windows / Catalog Center — Phase49.3I.34
Catalog Center candidate:
- version `8.9.0`,
- build `2026.08.27.2`,
- packaged runtime snapshot `b3280dd67cd7772f337f6792036ea92d3f252747`,
- Windows portable workflow run `33051114515` PASS,
- artifact `3DPrintHub-CatalogCenter-v8.9.0`, artifact ID `9637671099`,
- EXE SHA256 `32aed719e6d374447fc4b05f09a30fe12f0ce4dc05e570382f2e74036044900c`.

Implemented:
- Step-2 Product Profile Matrix in the Product workspace,
- create new profile or clone the selected profile,
- independent per-profile size, final/material weight, fixed price, print time, part dimensions, build mode, material, color, quality, package weight/dimensions, stock and sort/default state,
- selection modes: list, size, weight, build, size→build, build→size, size→weight, weight→size, size→weight→build and size→build→weight,
- profile rows persist in Product-owned SQLite JSON,
- exact profile payload travels through the mature Catalog batch/import boundary,
- range/profile minimum price is accepted by mature Product publish readiness without reintroducing a second price authority,
- source-link guard, explicit refresh behavior, exact saved AI provider/model, Product paging and prior Phase49 safety contracts remain preserved.

### Web / Store — Phase50.A.2D
Runtime test snapshot:
`7d0a2a1125e8f38771ba325427d1efa8b8d07da6`.

GitHub Actions `Phase50 Variant2 + Profile Matrix CI` run `33051311828` PASS:
- Python compile PASS,
- Storefront JavaScript syntax PASS,
- dependent selector behavior test `PHASE50_PROFILE_SELECTOR_HIERARCHY=PASS`,
- Django check PASS with known warning debt only,
- `makemigrations --check --dry-run` → no changes,
- migration plan PASS,
- clean CI database migration through `store.0038` PASS,
- 15 Variant/Profile/Checkout regression tests PASS,
- Variant API/profile price regression PASS,
- saved-address checkout regression PASS,
- immutable checkout/profile/part-dimension snapshot regression PASS.

Implemented:
- each Desktop profile becomes a real canonical `ProductVariant`, not display-only text,
- Desktop-managed variants are idempotently upserted by profile key; unrelated manual server variants are preserved,
- per-profile fixed price uses the Phase50 pricing policy contract,
- Product page treats selected Profile as the single price/facts authority,
- customer can choose dependent size/weight/build/material/color/quality choices,
- size-first hierarchy now filters each downstream dimension only by **earlier** selections; a later weight/build can no longer hide valid options from the selected size,
- weight/profile option prices are scoped to the selected upstream size instead of taking a minimum across unrelated sizes,
- Product page summary updates profile name/description, price, size, part weight, part dimensions, build, material, color, quality, shipping weight, print time and package dimensions,
- native Variant select remains as fallback,
- duplicate legacy material selector is suppressed when canonical Variant/Profile selection is present,
- dynamic Profile text is HTML-escaped before rendering.

## Database chain
Pending Production schema chain is intentionally ordered:
1. `store.0036_phase50_checkout_snapshot`
2. `store.0037_phase50_professional_commerce_policy`
3. `store.0038_phase50_profile_matrix`

`0037` adds professional Product pricing policy, per-Variant fixed price override, customer sales notice, optional strict color-stock enforcement, shipping service/scope/fee policy and Store payment-display settings.  
`0038` adds size↔weight selection modes, profile description, actual part L/W/H on `ProductVariant`, and immutable part L/W/H snapshots on `StoreOrderItem`.

CI proves the full chain on SQLite only. Production MySQL is **not** assumed equivalent and has not been migrated in this batch.

## Errors found and corrected in this batch
- `ERR-50-012`: Variant API read the callable `price_breakdown` method as if it were a dict → execute the canonical price contract before serializing.
- `ERR-50-013`: Phase50 shipping policy validated empty raw form address fields even when a mature saved address was selected → resolve province/county/city/address/postal code from the saved address.
- `ERR-50-014`: downstream Profile state could over-filter upstream size/weight options and option price could be taken from another size → prefix-only dependency filtering + upstream-scoped option pricing.
- `ERR-50-015`: Windows release trigger did not include the mature Product studio files touched by profile-aware publish readiness → release workflow now watches both Product studio files.

## Backup / rollback
Git safety anchors created before this batch:
- `backup/pre-phase50-profile-matrix-20260827`
- `backup/pre-profile-matrix-ci-hotfix-20260827`

These are Git rollback anchors only. They do not replace the required fresh Production MySQL/source/environment backup.

## Exact next work
1. On canonical Windows path `D:\projects\3DPrintHub`, verify correct repository/branch/clean worktree and pull the exact current GitHub head.
2. Run `catalog_center\RUN_PHASE49_3I31_SMART_AI_GATE.ps1` with the exact current HEAD and `-LaunchApp`; no Production operation.
3. Owner QA in Product Step 2:
   - build a 20 cm Product with 100/150/200 g profiles,
   - clone a profile and change size/weight/price,
   - build a 30 cm Product with multiple weights,
   - save/reopen and verify profile persistence,
   - verify source URL, AI controls, images and existing Product data remain intact.
4. Run local Django/Store regression on Windows, including migrations to local SQLite only.
5. Only after Local QA PASS: perform a fresh **read-only** Host audit for actual HEAD/worktree/live GitHub SHA/MySQL migration state/plan/disk/mysqldump.
6. Create fresh Production source + `.env*` + MySQL backup and checksums.
7. Explicitly fetch the approved GitHub target to `FETCH_HEAD` per `ERR-50-007`; verify fast-forward ancestry.
8. Apply only the verified pending chain `0036 → 0037 → 0038`, then collectstatic, Passenger restart and Production HTTP/API/schema/profile QA.
9. Update docs with exact Production commit, migration rows and fresh backup path.

Production deployment remains blocked until Local owner QA and the fresh Host/MySQL backup gate pass.
