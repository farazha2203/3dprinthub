# PROJECT ROADMAP

Updated: 2026-08-29  
Repository: `farazha2203/3dprinthub`  
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Current Web Epic: `Phase50 — Finance, Commerce & Admin Command Center`  
Current Web Phase: `50.A.2E — Brand-aware Filament Offers + Immutable Filament Snapshot`  
Parallel Windows Phase: `49.3I.40 — Commerce Precision + Offer Ownership + Readiness Truth / Catalog Center 8.9.8`  
Status: `8.9.8 GITHUB + WINDOWS PORTABLE PASS / STORE 0040 CI PASS / OWNER LOCAL 3I.40 QA NEXT / PRODUCTION BLOCKED`

## Permanent delivery order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI/LOCAL TEST → OWNER QA → HOST READ-ONLY VERIFY → BACKUP → DEPLOY FROM GITHUB → VERIFY PRODUCTION → DOCUMENT`

## Phase49 Windows track — current target 49.3I.40

Current acceptance target:
- Catalog Center `8.9.8` / build `2026.08.29.2`,
- runtime/package candidate `55139b909f214f33994d76bc1e6fdfd028b5d6c7`,
- targeted 31–40 CI `33247729316` PASS,
- Single Active AI `33247815007` PASS,
- Windows Portable `33247815027` PASS,
- Store 0040/Variant/Profile run `33246843145` PASS,
- Production untouched.

3I.40 acceptance:
- manufacturer → filament/material → color → register Offer,
- registering another filter/manufacturer preserves previously selected Offers,
- global filament inventory/rates/preheat are not Product fixed-price authority,
- fixed price is Product-specific per exact Offer,
- formula pricing consumes exact Offer operation facts,
- production rows own weight/print time/support,
- Profile registration owns identity/size/actual dimensions and snapshots the upstream state,
- same material/color across manufacturers remains distinct,
- color image/HEX/name fallback is visible,
- readiness distinguishes data defects from operator finalization,
- AI never reports 100% while AI-fixable defects remain,
- AI inputs remain Link / Saved-Crawled Data / Screenshot,
- mature acquisition/crawl/file/image path remains unchanged.

Store extension:
- `store.0040_phase50_filament_offer_operations` adds Offer hourly print/supervision, preheat and filament-image facts,
- CI migration/no-drift/full-regression PASS,
- Local SQLite 0040 backup/apply/test is the next DB gate,
- Production `0036..0040` remain blocked until owner Local QA + fresh Host read-only audit + backup.

Exact next step:
`GitHub → owner Local ff-only pull → verify/backup SQLite → apply 0040 locally → Store regressions → 31–40 Local gate → foreground 8.9.8 visual QA`.

## Phase49 Windows track — preserved foundation through 49.3I.38
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

## 49.3I.37 — Seven-stage AI / Finalization / Screenshot-to-Site — GITHUB + WINDOWS CI TESTED
- one persisted mother AI source mode: Link / Saved Data / Screenshot,
- single and selected-Product bulk runs share the same source authority and seven-stage orchestrator,
- AI fills only missing/invalid fields in unlocked stages and re-checks readiness after each stage,
- `✅` means stage data is complete; `🔒` is created only by operator `ثبت`,
- stage locks persist in Catalog SQLite and block later AI/Save writes at the Database boundary,
- both `sales_profile_ledger_json` and legacy `sales_profiles_json` are protected by the Commerce lock,
- Profile/price/material/color/brand/stock/publication remain operator-owned,
- Product image AI is SEO-only; deterministic tooling owns rename/WebP/metadata,
- Product-page Screenshot becomes a selected site image and preserves `source_page_url`,
- semantic Persian SEO guard normalizes `Twistmas Tree` to `درخت کریسمس اسپیرال` and rejects mixed-language contamination.

Verification:
- runtime `8d5e58a839c89eedbe258d9236889834fc02d9a9`,
- targeted run `33074245603` PASS, 77 tests,
- Single Active AI run `33074245489` PASS,
- Windows Portable run `33074245604` PASS,
- Catalog Center `8.9.5` / build `2026.08.27.7`,
- artifact ID `9647216177`,
- EXE SHA256 `4a3e15a3c475460c2dac035cedcd8ccebb40107fec6360b7be6a313f69186079`.

Historical 3I.37 gate was superseded by 3I.38 and then by current 3I.40. Current owner Local visual/functional gate is Catalog Center 8.9.8 with Local Store 0040 verification. Production remains untouched.

## 49.3I.38 — Permanent Crawl Ledger / Reject-Purge / Stage-scoped AI — GITHUB + WINDOWS CI TESTED
- preserve the mature crawl/browser/parser/image/file receive path,
- permanent `discovered_urls` ledger remains the Product identity authority,
- new `crawl_listing_state` persists deeper Listing traversal without changing `discover_classic()`,
- known collected/rejected/blocked identities do not become new receive work,
- explicit reject/purge removes only the Product local directory under `collected/` and keeps a rejected URL/external-ID tombstone,
- Direct Link checks terminal identity before acquisition/download,
- explicit restore is required before a rejected identity becomes receivable again,
- the one 3I.37 AI engine now accepts optional Stage scope,
- Products bulk Content/SEO uses the same engine with Stage 4 scope,
- single Product can clean/complete one unlocked Stage without changing any other Stage,
- image-only complete SEO is a no-provider no-op.

Verification:
- runtime `c904193a7f0af9aad80365834ec3f0b856e77dc9`,
- targeted run `33077213590` PASS with 84 tests,
- Single Active AI `33077239617` PASS,
- Windows Portable `33077239660` PASS,
- Catalog Center `8.9.6` / build `2026.08.27.8`,
- artifact ID `9648474905`,
- EXE SHA256 `6490e4815f1e6e0d75f09c112bb6990041578616f170954f62fae037b98bd507`.

Next gate: owner Local visual/functional QA on the final docs head. Production remains untouched.

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
