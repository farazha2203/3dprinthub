# CURRENT PROJECT STATE

Updated: 2026-08-27  
Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Primary Web/Commerce Release: `Phase50.A.2E — Brand-aware Filament Offers + Immutable Filament Snapshot`  
Parallel Windows Track: `Phase49.3I.38 — Permanent Crawl Ledger + Reject/Purge + Stage-scoped AI / Catalog Center 8.9.6`  
Status: `8.9.6 GITHUB + WINDOWS PORTABLE PASS / OWNER LOCAL VISUAL 3I.38 QA NEXT / PRODUCTION NOT DEPLOYED`

## Exact code/runtime candidate

The current runtime-changing commit verified by all current Windows Catalog gates is:

`c904193a7f0af9aad80365834ec3f0b856e77dc9`

Catalog Center:
- version `8.9.6`,
- build `2026.08.27.8`,
- Phase49.3I.31–38 targeted run `33077213590` PASS with 84 tests,
- Single Active AI run `33077239617` PASS,
- Windows portable workflow `33077239660` PASS,
- artifact `3DPrintHub-CatalogCenter-v8.9.6`,
- artifact ID `9648474905`,
- EXE size `65,520,499` bytes,
- EXE SHA256 `6490e4815f1e6e0d75f09c112bb6990041578616f170954f62fae037b98bd507`,
- artifact ZIP digest `sha256:13ae8582be09b71f90e607c2230075d875b7445f8a46b6462a9241edf9d52563`,
- browser smoke PASS,
- portable self verify PASS,
- source URL preservation gate PASS,
- Production touched = NO.

### Phase49.3I.38 behavior verified in CI
- mature Browser/Parser/image/file receive pipeline is preserved; 3I.38 wraps its boundaries rather than replacing it,
- permanent crawled/received ledger keeps known Product identities across scans,
- previously `collected`/terminal Product links are skipped instead of being requeued,
- same Listing uses a persisted deeper-scroll continuation cursor,
- 100 known Products + discovery of 1..200 produces exactly the next 100 pending Products,
- operator can `رد دائمی + حذف فایل‌ها و عکس‌های محلی`; Product source identity remains as `rejected` tombstone,
- physical deletion is allowed only below the canonical Catalog `collected/` root,
- Direct Link rejects terminal identities before browser/HTTP/image/file acquisition,
- explicit restore is required before a rejected Product may be received again,
- one mother AI engine remains authoritative with Link / Saved-Crawled Data / Screenshot inputs,
- selected-Product Bulk Content/SEO calls that same engine with `target_stages={"content"}`,
- Product workspace can clean/complete one selected unlocked Stage only,
- Stage 4 cleanup cannot write Quick/Profile/Source/Slider or any other out-of-scope stage,
- image-only scoped AI makes no provider request when image SEO is already complete.

Canonical active phase doc:
`docs/phases/PHASE49_3I38_CRAWL_LEDGER_STAGE_AI.md`.

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
