# CURRENT PROJECT STATE

Updated: 2026-08-27  
Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Primary Web/Commerce Release: `Phase50.A.2E — Brand-aware Filament Offers + Immutable Filament Snapshot`  
Parallel Windows Track: `Phase49.3I.35 — Operator Ledger + Resilient AI / Catalog Center 8.9.3`  
Status: `8.9.3 PROFILE WORKSPACE HOTFIX PACKAGED CI PASS / OWNER FOREGROUND PRODUCT WORKSPACE QA NEXT / PRODUCTION NOT DEPLOYED`

## Exact code/runtime candidate

The current runtime-changing commit verified by all Windows Catalog gates is:

`9637829a255a1d09800bc062c2f049cf5d92b585`

The branch contains only CI/local-gate tooling plus documentation commits after that packaged runtime snapshot. No packaged application module was changed after the successful Windows run documented below. The latest tooling head before documentation finalization is `b9c4d8d5f94c61c536736a1a828eff809f8e109d`.

Catalog Center:
- version `8.9.3`,
- build `2026.08.27.5`,
- targeted Smart Link + Operator Ledger run `33067612565` PASS,
- Single Active AI run `33067618639` PASS,
- Windows portable workflow `33067618679` PASS,
- artifact `3DPrintHub-CatalogCenter-v8.9.3`,
- artifact ID `9644438652`,
- EXE SHA256 `fd525fad977f592dc62e68fc3a4310bba98c7ed9689c5101cbdc35589fef7bed`,
- artifact ZIP digest `sha256:216b62072fd95a0a4d292b28ce99605fd60f3e4d9622d06987d6fe5b434e6141`,
- packaged browser smoke PASS,
- portable self verify PASS,
- public GitHub Release publication skipped/manual until owner foreground Product Workspace QA.

Store/Phase50 runtime was verified at commit:
`d519a360e65b79db4b62af206b95f63c3539bc12`

Later runtime commit `2622818...` contains no conflicting Store schema change after that verified Store state.

Phase50 workflow:
- run `33059883188` PASS,
- Python compile PASS,
- Storefront JavaScript syntax PASS,
- dependent Profile behavior PASS,
- Django check PASS with known warning debt only,
- `makemigrations --check --dry-run` PASS,
- migration plan PASS,
- clean CI SQLite migration through `store.0039` PASS,
- 16 Variant/Profile/Checkout regressions PASS,
- brand-aware filament rate/API test PASS,
- immutable support-weight/filament-brand/manufacturer checkout snapshot PASS.

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

The next gate is owner foreground Product Workspace QA on 8.9.3. Production remains untouched.

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

### 1. Owner Local Windows gate
Canonical root:
`D:\projects\3DPrintHub`.

Verify:
- exact repository,
- branch,
- clean worktree,
- live GitHub branch head,
- ff-only pull.

Run:
`catalog_center\RUN_PHASE49_3I31_SMART_AI_GATE.ps1` with exact head and `-LaunchApp`.

Owner QA:
- existing Product opens and source URL remains intact,
- register Profile from working form,
- new Profile from latest,
- multiple weight/time/support rows,
- select-all materials/colors + local register,
- same PLA/color across Bambu/eSUN stays distinct,
- roll stock/rate preview,
- fixed vs formula pricing,
- AI preflight/progress/retry/configured fallback,
- manual SEO/source review,
- image/source/AI existing functions remain intact,
- local actions do not rebuild the full Products page,
- close/reopen preserves ledger.

### 2. Local Django/Store gate
Use local SQLite only:
- backup local DB,
- inspect migration plan,
- migrate local through 0039,
- run Store/Profile/Checkout regressions,
- verify no migration drift.

### 3. Only after Local QA PASS
Read-only Host audit:
- project root,
- branch/current HEAD,
- clean worktree,
- live GitHub branch SHA,
- exact Python/Django,
- exact MySQL DB,
- actual 0034..0039 rows,
- exact migration plan,
- disk,
- `mysqldump` availability.

Then fresh source + `.env*` + MySQL backups/checksums and rollback HEAD.

### 4. Production deploy
Only the owner-approved GitHub head is deployed:
- explicit branch fetch to `FETCH_HEAD` per `ERR-50-007`,
- verify exact SHA + fast-forward ancestry,
- deploy source,
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
- resume from effective Local Django DB verification using Python stdin, create a fresh Django SQLite backup, inspect pending plan (expected only `0039` if the same Local DB is active), then migrate/test and run the current 31–35 Catalog gate.

## Related docs
- `docs/phases/PHASE49_3I35_OPERATOR_LEDGER_RESILIENT_AI_FILAMENT.md`
- `docs/phases/PHASE50_FINANCE_ADMIN_COMMAND_CENTER.md`
- `docs/ERRORS.md`
- `docs/REQUESTS.md`
- `docs/ROADMAP.md`
- `PROJECT_CONTEXT.md`

Production remains blocked until owner Local QA passes.
