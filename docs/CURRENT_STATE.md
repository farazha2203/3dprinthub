# CURRENT PROJECT STATE

Updated: 2026-08-29  
Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Primary Web/Commerce Release: `Phase50.A.2E — Brand-aware Filament Offers + Immutable Filament Snapshot`  
Parallel Windows Track: `Phase49.3I.40 — Commerce Precision + Offer Ownership + Readiness Truth / Catalog Center 8.9.8`  
Status: `8.9.8 BASELINE PASS / ERR-49-066 CHECKER + STAGE OWNERSHIP HOTFIX GITHUB / OWNER LOCAL TEST NEXT / PRODUCTION NOT DEPLOYED`

## Exact code/runtime candidate

Current packaged/runtime candidate:

`55139b909f214f33994d76bc1e6fdfd028b5d6c7`

Catalog Center:
- version `8.9.8`,
- build `2026.08.29.2`,
- Phase49.3I.31–40 targeted run `33247729316` PASS,
- Single Active AI run `33247815007` PASS,
- Windows Portable run `33247815027` PASS,
- artifact `3DPrintHub-CatalogCenter-v8.9.8`,
- artifact ID `9713426658`,
- artifact digest `sha256:776eebb4daa1039119721697988508558991c6c4ccd6a2b1cca8b50b6f3b57a2`,
- EXE SHA256 `2be8be49e05575cb20ea12f061d006935df070ec9abb0f87e4f00e4151d5f02a`,
- browser/self-verify/source-URL/launcher/regression gates PASS,
- Production touched = NO.

### Phase49.3I.40 behavior verified in CI
- Stage 2 order is manufacturer → material/filament → color → Product Offer registration → pricing → production rows → Profile identity/dimensions,
- selected Offers from other manufacturers/filters are preserved when the current filter is registered,
- global filament stock/rates/preheat facts are separate from Product-specific fixed price per exact Offer,
- color preview uses image/explicit HEX/name fallback,
- Readiness separates real data defects from complete-but-not-finalized stages,
- AI terminal 100% is blocked unless final `ai_fixable_count == 0`,
- AI source authority remains Link / Saved-Crawled Data / Screenshot only,
- mature Crawl/Direct Link/parser/image/file acquisition remains the authority.

Canonical active phase doc:
`docs/phases/PHASE49_3I40_COMMERCE_PRECISION_READINESS_TRUTH.md`.


## Current owner blocker — ERR-49-066 checker/stage ownership mismatch

Owner Local retest of `c679c66d8c6554ff14e5705b7eb3aada24495990` proved the prior repaint fix was not the remaining root cause: 12/12 targeted tests passed and the correct 8.9.8 foreground runtime launched, but Product 63 still showed completed inputs as red/missing.

The foreground audit isolated the contract failure:
- an older visible 3I.31 full-AI action still ran and persisted Persian/SEO/image fields,
- the final readiness loop then saw 7 data defects / 5 AI-fixable,
- it scoped Stage 4 Content/SEO,
- a valid fallback Provider response was accepted,
- but no Product field update followed and the loop reported 0 defects fixed / 5 still AI-fixable.

The new GitHub hotfix aligns the whole chain:
- one field owner: `title_fa → quick`, image Alt → `images`, editorial/SEO → `content`,
- persisted title/description may preserve only exact Latin source-identity tokens; SEO/list fields remain Persian-only,
- AI repair uses the same semantic checker as readiness, including non-empty invalid keyword/tag/hashtag lists,
- guided Wizard uses `data_ready/missing_data` for red stars, stage icons and Next gating rather than operator-finalization `ready`,
- final 3I.39 class aliases route mature full-AI/link/current-stage actions through the same seven-stage repair engine.

Rollback:
`backup/pre-err49-066-readiness-checker-alignment-20260829` → `c679c66d8c6554ff14e5705b7eb3aada24495990`.

GitHub code/regressions are updated; no current-head Actions run is attached yet. Owner Local targeted tests + foreground Product 63 retest are the next gate. No DB/schema/media/secret/Host/Production change.

## Owner SEO/readiness reconciliation hotfix — ERR-49-065

After the ERR-49-064 geometry hotfix, the owner confirmed the professional 3I.39/3I.40 Product Workspace is now visible. The next foreground test exposed a narrower SEO/readiness problem: seven-stage AI filled the Persian/SEO fields, but red/missing readiness widgets remained stale.

Root cause: AI persisted the new fields, then the wrapped UI refresh chain allowed older guided-wizard cached state to repaint after the final 3I.40 readiness renderer.

Git hotfix:
- source `b9eb9d74b0c0be49ca8d04a4333750e68e93f4`,
- regression `375961a1621c43f168b7c3fd76523c6d3c9c9a26`,
- rollback `backup/pre-err49-065-seo-post-ai-refresh-20260829` → `3edda5ffe98d8c37dd66e3e7fc0d6eab3ec6c554`.

Behavior: whole-product and single-stage AI completion now rehydrate the Product from SQLite, reload, refresh lock/wizard/readiness surfaces, and run final readiness last again after a short settle delay. This changes only post-AI UI reconciliation; no AI Provider/source ownership, Offer/Profile, schema, Host or Production behavior changed.

Verification status: GitHub updated; owner Local targeted tests and foreground SEO retest are next. No Production work is allowed before that pass.

## Owner foreground 8.9.8 blocker — ERR-49-064

Owner foreground execution on the canonical checkout/branch/head proved the correct 8.9.8 source was running, but opening Product 63 raised a real Tk callback exception before 3I.39/3I.40 could finish ProductWorkspace construction:

`TclError: cannot use geometry manager pack inside ...!labelframe which already has slaves managed by grid`.

The traceback terminates in `phase49_3i35_operator_ledger.build_material_actions()`. The modern material/color checkbox picker had already converted that legacy commerce card to a grid-managed surface; the 3I.35 layer then attempted to mount obsolete Listbox actions with `pack`. This explains why the owner saw the older Stage-2/SEO UI despite 3I.39/3I.40 launcher markers: construction stopped part-way through the wrapper chain.

Hotfix:
- source commit `aa37dcf916dfab71409738f7087a171daffe4a0a`,
- regression commit `9a3ebd43b22a50ac1447b90cae159dcffb1ed451`,
- rollback `backup/pre-err49-064-stage2-geometry-20260829` → `c62df9dd1bbfee4cfa915beed6f9523efaa4937f`,
- modern picker now suppresses only the obsolete 3I.35 Listbox action row; 3I.35 data/business methods remain and 3I.39 stays the final visible Stage-2 authority,
- no DB/schema/media/secret/Production change.

Verification is not yet complete: owner must ff-only pull the current branch, run the targeted 3I.35/3I.40 tests and foreground-open the same Product Workspace. Production remains blocked.

### Phase50 / Store extension through 0040
Migration:
`store.0040_phase50_filament_offer_operations`.

Adds exact Offer operation facts:
- print hourly rate,
- supervision hourly rate,
- preheat hours/temperature/hourly cost,
- optional filament image URL.

Verification:
- first 0040 run `33246706102` exposed only Decimal string-format assertions; migration plan/apply and no-drift gates had passed,
- corrected tests at `b59c93cf37dcb66d3e97f61d2669df6e1d1644a4`,
- Phase50 Variant2/Profile Matrix run `33246843145` PASS,
- full CI SQLite migration through `0040` PASS,
- 21 Store/Profile/Checkout/Offer regressions PASS.

Production migration state is unchanged from the last terminal verification: only `0034` and `0035` are claimed applied. `0036..0040` require fresh Host read-only verification before any Production write.

## Owner Local automated acceptance — PASS

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

Only manual/visual operator acceptance remains before Host read-only audit. Automated Local acceptance is complete; this does not count as Production approval by itself.


### Detached launch note — visual QA not yet completed
The owner automated gate emitted `CATALOG_CENTER_LAUNCHED=YES`, but the owner did not see the new UI. The gate uses detached PowerShell `Start-Process`; therefore this marker is not evidence of visible/manual acceptance. Per `ERR-49-058`, the next action is a foreground `launch.py --debug` run from the canonical Local checkout and visual verification inside the Product workspace/order-pricing-options stage. Production remains blocked.

## Owner foreground startup incident — fixed in 8.9.2

Owner foreground launch of 8.9.1 exposed a real startup blocker after automated gates: 3I.35 mounted an AI settings panel with `grid` directly into the pack-managed UX87 `settings_tab`, causing Tk `TclError` before the window became usable. This is recorded as `ERR-49-059`.

The runtime fix changes only the outer panel geometry to `pack`, preserving internal panel layout and all previous AI/Profile behavior. Regression and Windows package CI now PASS on runtime `9bd9d0b4cd070a35c82c6ecefd6f6b3027b20284`. Owner must now pull the documentation-final head and run foreground `launch.py --debug`; visual acceptance is still open. Production remains untouched.

## Owner foreground Product Workspace incident — fixed in 8.9.3

8.9.2 confirmed the application startup geometry fix, but owner diagnostics exposed a second real Visual-QA blocker when Products 305/303 were opened: Profile Matrix selection called an unbound short helper `self._profile_by_key`. This is `ERR-49-060`.

8.9.3 changes the call to the actually installed namespaced method `self._phase49_3i34_profile_by_key`, adds an executable wrapper-binding regression, and passes targeted/Single-AI/Windows package gates on runtime `9637829a255a1d09800bc062c2f049cf5d92b585`.

That 8.9.3 checkpoint is historical and was superseded by 3I.37/3I.38. The current owner gate is Catalog Center 8.9.6 visual/functional QA. Production remains untouched.

## What is implemented now

### Phase49.3I.35 — Windows operator workflow
- 3I.35 is composed through the established `phase49_3i_pricing_modes.py` boundary; no parallel launcher-only patch.
- the old duplicate 3I.34 Profile panel is hidden.
- the upper Product controls are temporary working state.
- `ثبت پروفایل از فرم بالا` creates an independent registered Profile snapshot.
- `پروفایل جدید از آخرین` loads the latest snapshot into working state so the operator can rename/change size/price/options and register another Profile.
- registered Profile ledger is the synchronization/publish authority, not transient controls.
- multiple production rows per Profile support:
  - Product weight,
  - print time,
  - support weight.
- quick/basic Product page no longer owns fixed price/weight/Profile authority.
- material/color section has:
  - select all,
  - clear selection,
  - local register selection on current Product,
  - no full Products refresh for that local action.
- material offer carries:
  - material,
  - brand,
  - manufacturer/factory,
  - color,
  - roll weight,
  - roll stock,
  - purchase price,
  - sale price,
  - USD price,
  - explicit FX rate.
- effective customer filament rate uses the highest positive explicit sale basis and never guesses FX.
- source URL guard/history/recovery and existing extraction logic are preserved.

### Resilient Product AI
The mature 3I.33 AI pipeline remains the editorial execution authority and 3I.35 wraps it with observability/resilience:
- live provider/model preflight,
- progress 0–100,
- visible send/wait/reply/apply events,
- up to configured retry count per provider (default 3),
- explicit configured fallback providers only,
- optional `openrouter/free` only when configured,
- selected-Product bulk processing with isolated per-Product failures,
- no global Products-page refresh after every Product,
- cancel remains operator-controlled.

Supported Product AI modes:
- link-grounded Persian translation + SEO,
- saved Product data → Persian translation + SEO,
- Product-page screenshot/vision → extracted facts + Persian SEO,
- repair/fill missing editorial data.

Editorial AI does not own material/color.

### Manual readiness
- SEO stage can be manually approved when actual Persian title/description are complete but a detector is stale.
- source/license can fill from existing local facts.
- source fields can be repaired by AI.
- source review can be manually acknowledged.
- manual review cannot bypass invalid/non-commercial license policy.

### Phase50.A.2E — Store brand-aware filament bridge
Migration:
`store.0039_phase50_filament_offer_pricing`.

Adds:
- MaterialColorOption brand/manufacturer/roll/pricing/FX facts,
- `ProductVariant.support_weight_grams`,
- `StoreOrderItem.support_weight_grams`,
- `StoreOrderItem.filament_brand_name`,
- `StoreOrderItem.filament_manufacturer_name`.

Store behavior:
- Desktop Profile sync creates/updates brand-aware MaterialColorOption facts.
- same material/color from different brands remains distinct.
- formula pricing consumes `effective_sale_price_per_gram`.
- current color stock uses matching real spool remaining grams first; otherwise synchronized roll-count × roll-weight snapshot.
- Variant API returns brand/manufacturer/support.
- Product Profile selector/summary shows brand/manufacturer/support.
- successful checkout freezes support/brand/manufacturer into historical order items.

## Errors found and fixed in this development batch

### ERR-50-016
First Phase50 run `33059803005` stopped at migration drift and proposed an unapproved fake `0040_alter_productvariant_support_weight_grams`.

Root cause:
mature 3F runtime contributed the same field before 0039, but its `verbose_name` differed from migration 0039.

Fix:
align runtime field metadata to migration 0039. No 0040 created.

Verification:
Phase50 run `33059883188` PASS.

### ERR-49-056
First 8.9.1 Windows candidate run `33059799929` had two stale release-contract failures:
- old 3I.33 test still required retired quick-page `قیمت قطعی فروش`,
- `config.example.json.package_version` remained 8.9.0.

Fix:
- test now enforces the requested single pricing authority and absence of quick-page fixed-price control,
- example config aligned to 8.9.1.

Verification:
Windows run `33060047878` PASS.

No failed CI command was repeated unchanged.

## Production state — last terminal verified

Production application commit remains:
`c283864290f9c989a9fcdf24ee8eef519560e917`.

Verified Production:
- root `/home/sfkilvrs/3dprinthub`,
- venv `/home/sfkilvrs/virtualenv/3dprinthub/3.12`,
- Python 3.12.13 / Django 6.0.7,
- MySQL `sfkilvrs_EmiAdmin_3dprinthub`,
- `store.0034_phase50_variant2_commerce` applied,
- `store.0035_phase50_sales_profiles` applied,
- `store.0036_phase50_checkout_snapshot` not Production-applied at last verify,
- `store.0037_phase50_professional_commerce_policy` not claimed applied,
- `store.0038_phase50_profile_matrix` not claimed applied,
- `store.0039_phase50_filament_offer_pricing` not claimed applied,
- Home/Store/Admin/Product/Variant API healthy at last Production verify,
- public imported working-media exposure = 0.

No Production deploy, migration, collectstatic or restart was performed during 3I.35/50.A.2E development.

Last verified Production rollback backup:
`/home/sfkilvrs/3dprinthub-deploy-backups/20260826-143650`.

A **fresh** Production source + environment + MySQL backup is mandatory before the next deployment.

Expected pending schema chain, subject to fresh read-only MySQL verification:
1. `store.0036_phase50_checkout_snapshot`
2. `store.0037_phase50_professional_commerce_policy`
3. `store.0038_phase50_profile_matrix`
4. `store.0039_phase50_filament_offer_pricing`

CI proves that chain on SQLite; it does not prove the current Production MySQL migration table.

## Backup / rollback

Git safety anchors:
- `backup/pre-phase49-3i35-operator-ledger-20260827` → `ca9cc1160f407c0a78302ad75cb38396616aed52`
- `backup/pre-phase49-3i35-integration-20260827` → `1b02d413be00c09631661eafaf252d011ad45d40`

These are source rollback anchors only.

## Exact next work

### 1. Owner Local Windows 3I.38 gate
Canonical root:
`D:\projects\3DPrintHub`.

Required preflight:
- verify exact repository,
- branch `agent/phase49-3i18-operator-bulk-ai-rebuild`,
- clean worktree,
- live GitHub branch head,
- ff-only pull,
- run current `catalog_center\RUN_PHASE49_3I31_SMART_AI_GATE.ps1`.

Owner visual/functional QA on 8.9.6:
- crawl/received ledger opens and shows known URLs/statuses,
- a disposable Product can be rejected + local files/images purged while source URL/external ID remain as a rejected tombstone,
- deletion cannot escape the Catalog `collected\` root,
- rerunning the same Listing skips previously collected/rejected identities and continues to newer Products,
- ordinary new Product Crawl/Direct Link/image/file receive still works,
- Direct Link to a rejected Product skips before receive/download,
- selected-Product bulk Content/SEO uses the same mother AI source mode,
- single Product can clean/complete only Stage 4 without changing Profile/price/source/images/slider,
- locked stages remain unchanged until explicit `اصلاح`,
- image-only complete SEO does not spend an AI request,
- existing 3I.35 Profile/filament behavior remains healthy.

### 2. Local Django/Store regression
Local SQLite is already owner-verified through `store.0039` from the prior gate. Re-verify:
- effective DB path,
- fresh backup if any schema write becomes necessary,
- `django check`,
- `makemigrations --check --dry-run`,
- Store/Profile/Checkout regressions.
3I.38 itself adds only Catalog SQLite state and no Django migration.

### 3. Only after owner Local QA PASS
Perform read-only Host audit:
- project root,
- branch/current HEAD,
- clean worktree,
- live GitHub branch SHA,
- exact Python/Django,
- exact MySQL DB,
- actual `0034..0039` migration rows,
- exact migration plan,
- disk space,
- `mysqldump` availability.

Then create fresh tracked-source + environment + MySQL backups/checksums and record rollback HEAD.

### 4. Production deploy
Deploy only the owner-approved GitHub head:
- explicit branch fetch to `FETCH_HEAD` per `ERR-50-007`,
- verify exact SHA + ff-only ancestry,
- re-run Django checks/drift/DB/plan,
- apply only actually pending approved migrations,
- collectstatic,
- Passenger restart,
- Home/Store/Admin/Product/Profile API/Checkout/static/private-media/order verification,
- update docs with exact Production SHA/migrations/backup.

## Owner Local QA checkpoint — 2026-08-27 PowerShell DB-probe stop

Owner terminal evidence on canonical Windows root `D:\projects\3DPrintHub`:
- branch `agent/phase49-3i18-operator-bulk-ai-rebuild`,
- Local fast-forwarded successfully to `35ab63105f30fdca42518d5273a424a3200977e3`,
- worktree clean before the owner gate,
- live GitHub SHA matched that target,
- packaged runtime/tooling ancestry checks PASS,
- fresh Catalog SQLite backup created at `D:\projects\3dprinthub-backups\phase49-3i35-20260827-133859\catalog.sqlite3`,
- owner gate then stopped at the read-only Django DB detector because multiline PowerShell `python -c` quoting corrupted the Python source,
- this failed run stopped **before** Local Django migration execution; no new migration was applied by this failed run.

Earlier owner evidence on `ca9cc1160f407c0a78302ad75cb38396616aed52`:
- Local SQLite migration through `store.0038` PASS,
- 15 Store/Profile/Checkout tests PASS,
- post-migration drift check PASS,
- Catalog 49.3I.31–34 gate PASS.

Current correction:
- `ERR-49-057` records the wrapper defect,
- historical 3I.35 DB-probe correction completed; the current Catalog gate is 31–38 and Local Django SQLite was subsequently verified through `0039`.

## Related docs
- `docs/phases/PHASE49_3I38_CRAWL_LEDGER_STAGE_AI.md`
- `docs/phases/PHASE49_3I37_SEVEN_STAGE_AI_SCREENSHOT.md`
- `docs/phases/PHASE49_3I35_OPERATOR_LEDGER_RESILIENT_AI_FILAMENT.md`
- `docs/phases/PHASE50_FINANCE_ADMIN_COMMAND_CENTER.md`
- `docs/ERRORS.md`
- `docs/REQUESTS.md`
- `docs/ROADMAP.md`
- `PROJECT_CONTEXT.md`

Production remains blocked until owner Local QA passes.
