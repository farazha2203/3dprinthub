# Phase49.3I.35 — Operator Ledger, Resilient AI and Brand-aware Filament Offers

Updated: 2026-08-27  
Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Catalog Center: `8.9.2` / build `2026.08.27.4`  
Windows runtime snapshot: `9bd9d0b4cd070a35c82c6ecefd6f6b3027b20284`  
Status: `8.9.2 STARTUP HOTFIX PACKAGED CI PASS / OWNER FOREGROUND VISUAL QA NEXT / PRODUCTION NOT DEPLOYED`

## Goal

Replace the duplicated Step-2 Profile editor with the operator workflow requested for real daily catalog work:

- the upper Product form is a temporary working form,
- operator registers a Profile as an independent immutable-style snapshot of that working form,
- a new Profile can load the latest Profile into the working form and diverge safely,
- published/synchronized authority is the registered Profile ledger, not transient controls,
- price/weight/Profile authority is removed from the Product quick/basic page,
- material/color/brand selection is local and must not refresh the full Products gallery,
- AI work is observable, retryable and explicitly failover-capable,
- SEO/source readiness can be manually approved when the actual required data is present,
- Product source identity and all mature extraction/link safeguards remain preserved.

## Windows operator-ledger contract

`phase49_3i35_operator_ledger.py` owns the final Step-2 operator surface on top of the mature 3I.34 transport.

### Working form vs registered Profiles

The 3I.34 duplicate panel is hidden. The current upper form remains editable working state.

A registered Profile stores:
- profile key/name,
- size,
- one or more production rows,
- selected material/brand/manufacturer/color offers,
- pricing strategy / fixed price when explicitly fixed,
- support-cost multiplier,
- assembly fee,
- product/availability state,
- stock quantity,
- lead time,
- default/active/sort state.

Each production row stores:
- Product weight in grams,
- print time in minutes,
- support weight in grams.

The operator can:
- register the working form as a Profile,
- update an existing registered Profile,
- load a Profile back into the working form,
- create a new Profile from the latest snapshot,
- remove a registered Profile.

The ledger is persisted in local SQLite as `sales_profile_ledger_json`. It is flattened into the mature `sales_profiles_json` transport only for the existing Catalog → Django sync contract.

## Material / brand / manufacturer / color contract

Desktop material offers now preserve:
- material,
- filament brand,
- manufacturer/factory,
- color + color metadata,
- roll weight,
- roll-count stock snapshot,
- purchase price per roll,
- sale price per roll,
- USD price per roll,
- explicitly recorded USD/IRR-Toman exchange rate.

The UI includes:
- `✓ همه متریال/رنگ‌ها`,
- clear selection,
- `ثبت انتخاب‌ها روی همین محصول`.

That local selection commit updates only the current Product SQLite facts. It does **not** perform global Save/Products refresh.

### Effective filament sale rate

For a material/color/brand offer, the runtime takes the maximum positive explicit sale basis available from:
1. per-gram sale override,
2. sale price per roll ÷ roll weight,
3. USD price per roll × explicitly recorded FX rate ÷ roll weight,
4. mature Material sale rate fallback.

The FX rate is never guessed.

Purchase price is inventory/accounting information and is not silently promoted to customer sale price.

## Inventory contract

`MaterialColorOption.current_stock_grams` uses:
1. matching real FilamentSpool remaining grams for the same material/color and, when set, brand;
2. otherwise the synchronized `stock_roll_count_snapshot × roll_weight_grams`.

Therefore a Windows offer such as:
`PLA / Bambu Lab / سفید مات / 1 roll × 1000 g`
becomes a real Store color/brand stock source instead of an unrelated Product-level stock number.

## Resilient AI contract

`phase49_3i35_resilient_ai.py` wraps the existing 3I.33 AI ownership boundary; it does not introduce another editorial AI pipeline.

Visible dialog behavior:
- Product and mode shown,
- provider/model preflight before execution,
- progress 0–100,
- send/wait/reply/apply stages,
- up to configured 3 attempts per provider,
- explicit fallback to configured alternative providers only after the current provider is exhausted,
- optional OpenRouter `openrouter/free` candidate only when explicitly enabled/configured,
- per-Product error isolation in bulk mode,
- next Product begins without rebuilding the global Products page,
- operator can cancel the batch.

The Product modes remain:
- link-grounded Persian translation + SEO,
- saved Product data → Persian translation + SEO,
- Product-page screenshot/vision extraction + Persian SEO,
- AI repair / fill missing editorial data.

Material and color remain operator-owned and are not accepted from editorial AI.

## Readiness/manual-review contract

`phase49_3i35_readiness_review.py` adds:
- manual SEO approval when the actual Persian title/description contract is present but a detector remains stale,
- fill source/license from already stored facts,
- AI source-field repair,
- manual source review.

Manual source review does not bypass an invalid/non-commercial license policy.

## Store / Phase50.A.2E bridge

Migration `store.0039_phase50_filament_offer_pricing` adds brand-aware filament offer fields plus:
- `ProductVariant.support_weight_grams`,
- `StoreOrderItem.support_weight_grams`,
- `StoreOrderItem.filament_brand_name`,
- `StoreOrderItem.filament_manufacturer_name`.

Desktop Profile sync upserts a brand-aware `MaterialColorOption`, and formula pricing uses `effective_sale_price_per_gram`.

Storefront Profile selection now distinguishes otherwise identical material/color offers by filament brand and shows brand/manufacturer/support facts in the selected Profile summary.

Checkout freezes support weight + filament brand/manufacturer into the immutable order snapshot so later inventory/brand edits cannot rewrite historical orders.

## Verification

### Store / Django
GitHub Actions run `33059883188` PASS on runtime ancestor `d519a360e65b79db4b62af206b95f63c3539bc12`:
- Python compile PASS,
- Storefront JavaScript syntax PASS,
- Profile dependency behavior PASS,
- Django check PASS with known warning debt only,
- `makemigrations --check --dry-run` PASS,
- migration plan PASS,
- clean CI SQLite migration through `store.0039` PASS,
- 16 Variant/Profile/Checkout regressions PASS,
- brand-aware offer/rate/API regression PASS,
- support/brand/manufacturer immutable checkout snapshot regression PASS.

### Catalog targeted gates
Application runtime snapshot `2622818d898e19b745c61ff653b80c03d22288f1` is the packaged code. Later test-tooling head `b9c4d8d5f94c61c536736a1a828eff809f8e109d` changes only the local gate/workflow and docs; application runtime is unchanged.
- Phase49.3I.31–35 Smart Link + Operator Ledger run `33060613937` PASS,
- Single Active AI run `33060613914` PASS.

### Windows one-file release gate
Run `33060047878` PASS:
- current Phase49 regression PASS,
- launcher composition PASS,
- source URL preservation PASS,
- one-file EXE build PASS,
- packaged browser smoke PASS,
- portable self-verify PASS,
- manifest/SHA gate PASS,
- artifact upload PASS.

Artifact:
- name `3DPrintHub-CatalogCenter-v8.9.1`,
- artifact ID `9641338334`,
- EXE SHA256 `3099b26713a460fbd55c1204ef750b37dbef542269b5520fd393526cd8c9476c`,
- EXE size `65,456,439` bytes.

Public GitHub Release publication remains skipped/manual until owner Local QA.

## Rollback

Git anchors:
- `backup/pre-phase49-3i35-operator-ledger-20260827` → `ca9cc1160f407c0a78302ad75cb38396616aed52`,
- `backup/pre-phase49-3i35-integration-20260827` → `1b02d413be00c09631661eafaf252d011ad45d40`.

These do not replace a fresh Production source/environment/MySQL backup.

## Owner Local automated gate — PASS

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

This validates automated Local acceptance. Manual operator/visual verification of ledger behavior, material-brand UX, AI progress/retry/fallback and no-global-refresh remains required before Host audit.

## 8.9.2 owner-visible startup hotfix

Foreground owner launch of 8.9.1 exposed `ERR-49-059`: the new AI resilience settings LabelFrame was mounted with `grid` directly into UX87 `settings_tab`, while that parent is pack-managed. Tk aborted startup before the new UI could be seen.

Fix:
- outer resilience panel now uses `pack(fill="x", padx=8, pady=8)`,
- child controls remain grid-managed inside their own panel,
- regression prevents reintroducing the direct parent `grid`,
- targeted run `33066472847` PASS,
- Windows one-file run `33066468014` PASS on `9bd9d0b4cd070a35c82c6ecefd6f6b3027b20284`,
- artifact `9643957471`,
- EXE SHA256 `fac29fc610215cfc4115fcdb4c005fc69f99c3e6569b44c501d63ec82d6ba257`.

Manual foreground visual acceptance remains required.

## Production state and migration gate

No Production deployment or migration was performed in this phase.

Last verified Production remains application commit `c283864290f9c989a9fcdf24ee8eef519560e917` with `store.0034` and `store.0035` applied.

Pending schema chain must be re-verified read-only on MySQL before any write:
`0036 → 0037 → 0038 → 0039`.

No Production schema operation is allowed before owner Local QA, exact Host/Git/MySQL verification, migration plan, disk/mysqldump verification and fresh rollback backups.

## Exact next step

Owner Local QA on canonical Windows root `D:\projects\3DPrintHub`:
1. exact branch/head/clean-worktree verification,
2. run the Phase49.3I.31–35 local gate,
3. launch Catalog Center 8.9.1,
4. create multiple ledger Profiles from the working form,
5. verify multi-row weight/time/support,
6. verify all material/color selection + local commit without global refresh,
7. verify Bambu/eSUN-style same-material different-brand offers remain distinct,
8. verify fixed and formula-priced Profiles,
9. verify AI dialog preflight/progress/retries/fallback with configured providers,
10. verify manual SEO/source review,
11. close/reopen Product and verify source URL/images/Profiles remain intact.

Only after that PASS do we proceed to Host read-only audit and Production backup/deploy.
