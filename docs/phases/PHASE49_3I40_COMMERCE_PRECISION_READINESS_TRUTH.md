# Phase49.3I.40 — Commerce Precision, Offer Ownership and Readiness Truth

Updated: 2026-08-29  
Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Catalog Center: `8.9.8` / build `2026.08.29.2`  
Runtime/packaged candidate: `55139b909f214f33994d76bc1e6fdfd028b5d6c7`  
Status: `GITHUB CI + WINDOWS PORTABLE PASS / OWNER LOCAL 3I.40 VISUAL QA NEXT / PRODUCTION UNTOUCHED`

## Requested delta

Stage 2 must behave as one professional commerce workflow rather than duplicate pricing/profile forms:

1. manufacturer/company → filament/material → color → register Product Offer,
2. edit global Offer facts: stock, roll weight, purchase/sale/USD+explicit FX, hourly print/supervision, preheat hours/temperature/hourly cost and optional filament image/HEX,
3. pricing mode after Offer selection:
   - fixed price is Product-specific per exact Offer,
   - formula pricing consumes exact Offer facts and production time/weight,
   - range pricing remains available but is not the current operator focus,
4. production rows own product weight / print time / support weight,
5. Profile registration at the bottom owns only Profile identity + size label + actual part L/W/H; registering creates an immutable snapshot and later registrations must not mutate older Profiles,
6. same material/color across Bambu Lab/eSUN/other manufacturers remains distinct,
7. customer Storefront selects manufacturer → material → color and price/availability follows that exact selection,
8. color UI shows filament image when available, otherwise a swatch from explicit HEX or safe name fallback,
9. Link completion must report request/response/apply/readiness before/after and must never show 100% while AI-fixable defects remain,
10. stage data readiness and operator finalization are distinct states.

## Must-not-touch boundary

The mature acquisition path remains authoritative and was not replaced:
- browser/profile setup,
- listing/direct-link discovery,
- parser,
- image/file acquisition,
- `discovered_urls` identity ledger,
- rejection tombstones and continuation cursor from 3I.38,
- exact source URL preservation,
- one configured AI Provider/Model/key boundary,
- existing StoreOrder/Payment/Invoice/Coupon/VAT/inventory behavior.

3I.40 extends/wraps the final commerce/readiness boundary.

## Stage-2 Offer selection precision

`merge_offer_scope()` replaces only the currently visible manufacturer/material scope. Offers selected under other filters are preserved.

Example:
- register `Bambu Lab / PLA / White`,
- switch to `eSUN / PLA / Multicolor`,
- register the second scope,
- both Product Offers remain selected.

Deselecting the current filter removes only that visible scope and does not erase another manufacturer's Product Offer.

## Global Offer facts vs Product fixed price

Global filament facts belong to the exact manufacturer/material/color Offer:
- manufacturer / brand,
- material,
- color,
- HEX / optional filament image,
- roll weight,
- current stock,
- purchase price,
- sale price,
- USD price + explicit FX,
- print hourly rate,
- supervision hourly rate,
- preheat hours,
- preheat temperature,
- preheat hourly cost.

A fixed sale price for a Product using that Offer is a Product-owned value and is edited in a dedicated Product fixed-price editor. Changing it does not mutate the global roll/rate facts.

## Color preview

Operator and Storefront use:
1. filament image if configured where the surface supports it,
2. explicit valid HEX,
3. Persian/English color-name fallback,
4. neutral fallback if no color fact is known.

No hidden network fetch is required merely to open the Product workspace.

## Readiness truth

Stage rail separates:
- real missing data defects,
- complete data waiting for operator finalization,
- operator-finalized/locked stages.

The 3I.40 completion proxy suppresses internal cosmetic 100% events. Final 100% is emitted only when the final readiness snapshot proves `ai_fixable_count == 0`.

If AI-fixable defects remain after bounded passes/retry/fallback:
- progress stops below 100 (94% contract),
- remaining AI-fixable defects are emitted in diagnostics,
- remaining data defects are emitted separately,
- the operator is not told the Product is complete.

AI source choices remain exactly:
- Link,
- Saved/Crawled Data,
- Screenshot.

Repair is an operation on the same engine, not a fourth source.

## Screenshot contract

Product-page screenshot selected for the Product/Site is the top viewport reference, not a full-page capture. Mature acquisition/browser internals remain unchanged.

## Store / Phase50 extension

Migration:
`store.0040_phase50_filament_offer_operations`

Adds to `MaterialColorOption`:
- `print_hourly_rate`,
- `supervision_hourly_rate`,
- `preheat_hours`,
- `preheat_temperature_c`,
- `preheat_hourly_rate`,
- `filament_image_url`.

The Store selector and Variant metadata keep exact manufacturer/material/color identity, stock, preheat and visual facts.

## Verification

Catalog/Windows:
- Phase49.3I.31–40 targeted run `33247729316`: PASS,
- Single Active AI run `33247815007`: PASS on final packaged candidate,
- Windows Portable run `33247815027`: PASS,
- runtime/package SHA `55139b909f214f33994d76bc1e6fdfd028b5d6c7`,
- version `8.9.8`,
- build `2026.08.29.2`,
- artifact `3DPrintHub-CatalogCenter-v8.9.8`,
- artifact ID `9713426658`,
- artifact digest `sha256:776eebb4daa1039119721697988508558991c6c4ccd6a2b1cca8b50b6f3b57a2`,
- EXE SHA256 `2be8be49e05575cb20ea12f061d006935df070ec9abb0f87e4f00e4151d5f02a`,
- compile/regression/launcher/source-URL/self-verify/browser/SHA gates PASS.

Store/0040:
- first workflow `33246706102` failed only because two tests froze Decimal string presentation (`24.00` vs `24`, `3000` vs `3000.0000`); migration plan/apply and no-drift checks had already passed,
- corrected numeric comparison at `b59c93cf37dcb66d3e97f61d2669df6e1d1644a4`,
- Phase50 Variant2/Profile Matrix run `33246843145`: PASS,
- compile, Storefront JavaScript, selector behavior, Django check, no migration drift, migration plan, full CI SQLite migration and 21 Store/Profile/Checkout/Offer regressions PASS.

## Rollback

Source rollback branch:
`backup/pre-phase49-3i40-commerce-readiness-20260829` → `b59c93cf37dcb66d3e97f61d2669df6e1d1644a4`.

A fresh Local SQLite backup is mandatory before applying 0040 locally. A fresh Production source/environment/MySQL backup remains mandatory before any Host migration/deploy.

## Production

Production was not touched.

Last terminal-verified Production application:
`c283864290f9c989a9fcdf24ee8eef519560e917`.

Last verified Production migration state:
- applied `store.0034`,
- applied `store.0035`,
- `0036..0040` are not claimed applied without a new read-only Host verification.

## Exact next step

Owner Local acceptance:
1. verify canonical Local checkout, origin, branch and clean worktree,
2. ff-only pull the live GitHub head,
3. verify effective Django DB is the intended Local SQLite DB,
4. create checksum-verified pre-0040 SQLite backup,
5. verify 0039 applied / 0040 pending, inspect exact 0040 plan, apply 0040 locally,
6. run Store/Profile/Checkout/Offer regressions,
7. run the current 31–40 Catalog gate,
8. launch `catalog_center/launch.py --debug` in foreground,
9. visually test manufacturer → material → color registration, multi-brand preservation, per-Offer Product fixed price, formula/preheat, Profile identity/dimensions, swatch/image, truthful AI readiness and top-viewport screenshot,
10. verify ordinary Direct Link/Crawl/image/file acquisition remains healthy.

Only after owner Local QA PASS:
Host read-only audit → fresh backups → explicit `FETCH_HEAD` deployment → apply only actually pending migrations → collectstatic → Passenger restart → Production verification.
