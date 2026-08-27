# PROJECT ROADMAP

Updated: 2026-08-27  
Repository: `farazha2203/3dprinthub`  
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Current Web Epic: `Phase50 — Finance, Commerce & Admin Command Center`  
Current Web Phase: `50.A.2E — Brand-aware Filament Offers + Immutable Filament Snapshot`  
Parallel Windows Phase: `49.3I.35 — Operator Ledger + Resilient AI / Catalog Center 8.9.3`  
Status: `8.9.3 PROFILE WORKSPACE HOTFIX PACKAGED CI PASS / OWNER FOREGROUND PRODUCT WORKSPACE QA NEXT / PRODUCTION BLOCKED`

## Permanent delivery order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI/LOCAL TEST → OWNER QA → HOST READ-ONLY VERIFY → BACKUP → DEPLOY FROM GITHUB → VERIFY PRODUCTION → DOCUMENT`

## Phase49 Windows track — current target 49.3I.35
Preserved foundations:
- 48-card paged Product Explorer,
- no global Product refresh on each Product Save/AI action,
- exact saved mother AI Provider/Model/key ownership,
- exact-link grounded Product AI,
- source-link preserve/recover guard,
- local Product identity/history preservation,
- mature 3I.34 Profile transport and Store ProductVariant sync.

49.3I.35 adds:
- accounting-style registered Profile ledger; upper Product controls are working state, not publish authority,
- legacy 3I.34 duplicate Profile panel hidden,
- Profile production rows: weight / print time / support weight,
- select-all + local-register material/color actions without global Products refresh,
- material + brand + manufacturer + color + roll stock/purchase/sale/USD/FX offer facts,
- highest explicit positive sale-rate basis with no guessed FX,
- visible AI preflight/progress/retry/failover using only configured candidates,
- bulk AI per-Product error isolation,
- manual SEO readiness approval and manual source review without license bypass.

8.9.2 foreground-startup hotfix:
- 8.9.1 owner foreground launch exposed `ERR-49-059`: 3I.35 used `grid` in the pack-managed Settings parent,
- fixed outer resilience panel to use `pack`, with dedicated regression,
- targeted run `33066472847` PASS,
- Windows one-file run `33066468014` PASS on runtime `9bd9d0b4cd070a35c82c6ecefd6f6b3027b20284`,
- artifact ID `9643957471`, EXE SHA256 `fac29fc610215cfc4115fcdb4c005fc69f99c3e6569b44c501d63ec82d6ba257`.

8.9.3 Profile Workspace hotfix:
- 8.9.2 starts successfully but owner diagnostics exposed `ERR-49-060` when opening Products 305/303,
- Profile Matrix selected-row callback used unbound `self._profile_by_key` instead of installed `self._phase49_3i34_profile_by_key`,
- exact callback binding fixed with executable regression,
- targeted run `33067612565` PASS,
- Single Active AI run `33067618639` PASS,
- Windows one-file run `33067618679` PASS on runtime `9637829a255a1d09800bc062c2f049cf5d92b585`,
- artifact ID `9644438652`, EXE SHA256 `fd525fad977f592dc62e68fc3a4310bba98c7ed9689c5101cbdc35589fef7bed`.

Windows verification:
- runtime snapshot `2622818d898e19b745c61ff653b80c03d22288f1`,
- Smart/Profile 31–35 run `33060613937` PASS,
- Single-AI run `33060613914` PASS,
- Windows portable run `33060047878` PASS,
- version `8.9.1`, build `2026.08.27.3`,
- artifact ID `9641338334`,
- EXE SHA256 `3099b26713a460fbd55c1204ef750b37dbef542269b5520fd393526cd8c9476c`,
- public Release remains manual after owner Local QA.

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

## 50.A.2E — Brand-aware Filament Offers + Immutable Filament Snapshot — GITHUB CI TESTED
`store.0039_phase50_filament_offer_pricing`
- MaterialColorOption carries brand/manufacturer, roll weight/stock snapshot, purchase/sale/USD/explicit FX,
- current stock prefers matching real FilamentSpool grams and falls back to roll-count snapshot,
- dynamic pricing consumes the effective brand/color sale rate,
- ProductVariant carries support weight,
- StoreOrderItem freezes support weight + filament brand/manufacturer,
- Storefront distinguishes same material/color across different brands,
- Profile summary/API expose brand/manufacturer/support,
- no guessed FX and no duplicate Product-level price authority.

Verification:
- Phase50 run `33059883188` PASS,
- no migration drift,
- clean CI SQLite migration through `0039`,
- 16 Store/Profile/Checkout tests PASS,
- brand-aware rate/API regression PASS,
- immutable support/brand/manufacturer checkout snapshot PASS.

## Owner Local QA checkpoint
Automated Local acceptance now PASS:
- owner Local root `D:\\projects\\3DPrintHub` verified exact repository/branch and clean worktree,
- Local fast-forwarded to `2cdb356fca6d6c4c4bcd0edf203acf8e24bab2b9`,
- effective Local Django DB verified as SQLite `D:\\projects\\3DPrintHub\\db.sqlite3`,
- fresh pre-0039 DB backup `D:\\projects\\3dprinthub-backups\\phase49-3i35-resume-20260827-142404\\django-local-before-0039.sqlite3` with matching SHA256,
- `store.0038` verified applied and `store.0039` verified pending before write,
- exact `0039_phase50_filament_offer_pricing` plan inspected, then `0039` applied successfully,
- 16 Store/Profile/Checkout regressions PASS,
- post-migration `makemigrations --check --dry-run` = no changes detected,
- Catalog Center 31–35 Local gate PASS with 107 tests, source URL invariant PASS, launcher verify PASS,
- Catalog Center `8.9.1` / build `2026.08.27.3` launched successfully,
- Production touched = NO.

Remaining Local gate: owner visual/functional QA of the actual Catalog Center workflow. Production remains blocked until that visual acceptance is confirmed.

## Production gate for 50.A.2B–2E
1. Owner Local Windows/Django QA on exact current GitHub head.
2. Read-only Host verify: root, branch, HEAD, clean worktree, live branch SHA, Python/Django, exact MySQL DB and actual `0034..0039` migration state.
3. Inspect exact migration plan; do not assume `0036/0037/0038` are still pending.
4. Verify disk + `mysqldump`.
5. Fresh tracked-source + environment + MySQL backups with checksums and rollback HEAD.
6. Explicit branch fetch to `FETCH_HEAD` per `ERR-50-007`; verify exact SHA and ff-only ancestry.
7. Deploy approved GitHub snapshot.
8. Re-run Django check/drift/plan; apply only verified pending `0036 → 0037 → 0038 → 0039`.
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
