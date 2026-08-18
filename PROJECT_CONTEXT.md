# PROJECT_CONTEXT - 3DPrintHub

## Permanent paths
- Windows project root: `D:\projects\3DPrintHub`
- Windows Catalog Center runtime: `D:\projects\3dprinthub_catalog_center`
- Windows Catalog Center data: `D:\projects\3dprinthub-catalog-manager`
- Windows rollback backups: `D:\projects\3dprinthub-backups`
- Production root: `/home/sfkilvrs/3dprinthub`
- Production virtualenv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`
- Production MySQL DB: `sfkilvrs_EmiAdmin_3dprinthub`
- Repository: `farazha2203/3dprinthub`

## Delivery rule
GitHub is the code source of truth.

Required flow:

`GitHub Epic branch -> Windows sync -> local backup/migration plan -> local tests -> local visual/E2E acceptance -> explicit approval -> production backup -> production deploy -> production smoke tests`.

Never reset/drop/truncate production DB for a code/deploy problem. Preserve `.env`, MySQL, `media`, `private_media`, Catalog Center data, API keys and other runtime state.

## Stable historical recovery baseline
Phase 31 remains the historical recovery baseline: 2408 fixture objects, 51 fixture models, 31 provinces, 427 counties, 1242 cities; production DB/media backups existed and site/admin smoke checks were HTTP 200. Production data may have grown since then.

---

# Phase49 foundations retained

## Phase49.2A — Core consolidation

Active product route:

`Windows Catalog Center 8.7.1 -> Catalog Bridge -> ImportedPrintAsset -> Product/ProductCatalogProfile -> Store`.

Retained decisions:
- public external ready-model catalog/Link Analyzer intake is retired;
- historical records are preserved;
- external background model sync is disabled by default;
- material pricing and USD/FX logic remain independent;
- External Catalog route must not be restored merely to satisfy stale tests.

Catalog Center baseline:
- version: `8.7.1`
- build: `2026.08.16.3`

Known warnings:
- `ckeditor.W001`: CKEditor 4 technical debt/security warning;
- `store.W026`: in-memory realtime channel layer; Redis required for cross-process realtime if enabled in production.

## Phase49.2B — Master Admin + Customer Portal

Approved UI source:
- uploaded `master.zip` / Velzon Django Corporate 4.3.0;
- `interactive` is rejected and must not be used.

Brand:
- canonical UI logo: `static/img/brand/3dprinthublogo.png`;
- approved SHA-256: `97ec202678e386387fa9ebe2c6055fa45967d1f341d40dbc5f2d9e980b873cec`;
- exact user-supplied logo only; do not regenerate/recolor/substitute;
- six IRANSans FaNum weights mapped 200/300/400/500/700/900.

Retained improvements:
- Master RTL Admin;
- Customer Portal desktop sidebar + responsive drawer;
- Admin login desktop width regression fixed;
- Hero Store target/SEO/image fallback aligned with Store Product;
- External Catalog Hero URLs retired.

## Phase49.2C — Hero Studio & Cinematic Slider

Migration already applied on **local SQLite only**:
`website.0020_phase49_2c_hero_studio`.

Fields:
- `selected_asset_image` -> nullable FK to `store.ImportedPrintAssetImage`;
- `transition_effect`;
- `transition_duration_ms`;
- `display_duration_ms`.

Local validation from 2026-08-18:
- Hero rows before 0020: 2;
- Hero rows after 0020: 2;
- all four columns verified;
- `PHASE49_2C_DB_VERIFY=OK`;
- dedicated 49.2C test: 9/9 OK;
- later combined Phase49 regression: 21/21 OK.

Hero Studio retained:
- visual Product Album Picker;
- visual image selection without first Save;
- persistent image relation;
- edit existing sliders without delete/recreate;
- cinematic effect/timing per slide;
- reduced-motion/mobile-safe behavior.

Six effects:
1. `cinematic_fade`
2. `wedding_dissolve`
3. `cinematic_zoom`
4. `ken_burns`
5. `soft_blur`
6. `cinematic_reveal`

---

# Local Store migration status before Unified Epic

On Windows local SQLite, these are already applied:
- `[X] store.0027_phase39_variant_color_fk`
- `[X] store.0028_epic49_catalog_product_schema`
- `[X] store.0029_epic49_catalog_product_backfill`
- `[X] website.0019_phase45_managed_homepage_hero`
- `[X] website.0020_phase49_2c_hero_studio`

Before 0028/0029 the read-only audit reported:
- `IMPORTED_ASSETS_WITH_PRODUCT=0`
- `PROFILES_TO_CREATE_OR_REFRESH=0`
- `PRODUCTS_WITH_ANY_CHANGE=0`
- `PRODUCTS_WITH_SLUG_CHANGE=0`
- `AUDIT_DB_MUTATIONS=0`

Therefore local application of 0028/0029 changed no existing Product slug/SEO because local Product count was zero.

After applying them:
- `STORE_0028_APPLIED=True`
- `STORE_0029_APPLIED=True`
- `PROFILE_TABLE_EXISTS=True`
- Product/slug/SEO change counts remained zero.

Do **not** re-run old warnings that 0028/0029 are pending; that state is obsolete.

---

# Local catalog dataset observation

Read-only local audit:
- `PRODUCTS = 0`
- `ACTIVE_PRODUCTS = 0`
- `IMPORTED_ASSETS = 45`
- `ASSETS_WITH_PRODUCT = 0`
- `ASSETS_WITHOUT_PRODUCT = 45`
- `HERO_SLIDES = 2`

Historical local Hero links:
- slide 10 -> asset 1, `Vesper – Sculptural Bedside Lamp`;
- slide 11 -> asset 8, `Articulated flexi lizard`.

Those 45 local Assets are **not to be bulk-converted automatically**. Windows employee publishing is the operational Source of Truth and must run the normal approval/license/image/category gates. Historical/reference assets stay preserved.

---

# CURRENT ACTIVE EPIC

## Epic 49 — Unified Product / SEO / Slider / Desktop / Bridge

Branch:

`epic/phase49-unified-product-slider-sync`

Detailed document:

`docs/EPIC49_UNIFIED_PRODUCT_SLIDER_SYNC.md`

### Current state
- Epic implementation: **complete on GitHub**;
- self-test CI: **green**;
- Windows local pull/migrations/visual QA: **not yet performed for the Unified Epic**;
- production: **untouched / not deployed**.

Code validation baseline before documentation-only commits:

`8ad84577498072cf8c3d007d8bd259d6e3428cba`

Final CI probe commit:

`03b9df7c8f5a7ce8e8ad44b916cd626cc419818d`

Final GitHub Actions:
- run: `32129944811`
- job: `95688635543`
- result: **SUCCESS**

All gates passed:
- dependency install;
- isolated runtime directories;
- Python compile;
- `manage.py check`;
- `makemigrations --check --dry-run`;
- `migrate --plan`;
- targeted Phase49 behavioral/regression tests;
- Windows Catalog Center Epic49 tests;
- **full Django test suite**.

---

## Unified operational model

**Windows Catalog Center is the primary employee editor.**

Employees should be able to perform from Windows:
- internet product intake;
- source/reference review;
- Persian content edit;
- Product SEO edit/AI generation;
- image selection;
- price/material/color configuration;
- publish approval/license controls;
- independent Hero Slider SEO;
- Hero image selection;
- Hero effect/timing;
- publish to site;
- read current site Product revision;
- read/edit all current site Hero sliders;
- refresh newer server edits.

**Django Admin remains an equal secondary/manager editor**, not a separate data model.

Server changes and Windows changes use the same persistent Product/Profile/Hero records.

---

## Product SEO vs Hero SEO

Product SEO remains independent from Hero SEO.

Hero-specific persistent contract:
- `homepage_slider_enabled`
- `homepage_slider_image_url`
- `homepage_slider_sort_order`
- `homepage_slider_title_fa`
- `homepage_slider_description_fa`
- `homepage_slider_alt_text`
- `homepage_slider_button_text`
- `homepage_slider_focus_keyword`
- `homepage_slider_transition_effect`
- `homepage_slider_transition_duration_ms`
- `homepage_slider_display_duration_ms`

Catalog Center AI Pack `homepage_slider_seo` is preserved. Dedicated Slider SEO takes priority; Product SEO is fallback only when Slider fields are empty.

---

## Unified Django database migrations — NOT YET APPLIED LOCALLY

### Store 0030

`store/migrations/0030_phase49_unified_sync_contract.py`

Adds to ProductCatalogProfile:
- dedicated Hero SEO fields;
- Hero effect/timing fields;
- `sync_revision`;
- `last_modified_source`;
- `last_modified_by`.

### Website 0021

`website/migrations/0021_phase49_unified_hero_sync.py`

Adds to HomepageHeroSlide:
- `sync_revision`;
- `last_modified_source`;
- `last_modified_by`.

Both migrations are additive. No DROP/DELETE/TRUNCATE operations.

The next Windows gate must review `migrate --plan` before applying 0030/0021.

---

## Windows SQLite unified schema

`catalog_center/app/epic49_desktop_schema.py`

New additive columns:
- `homepage_slider_transition_effect`
- `homepage_slider_transition_duration_ms`
- `homepage_slider_display_duration_ms`
- `server_product_id`
- `server_product_revision`
- `server_slider_id`
- `server_slider_revision`
- `server_updated_at`
- `last_sync_conflict`

Existing Hero SEO columns remain.

Installer only adds missing columns; old Windows data is not deleted/rebuilt.

---

## Windows UI / icons

No new UI/icon package installed.

Employee mental model/icons:
- 📦 product
- 🖼 gallery/images
- 🔎 Product SEO
- 🎬 Hero Slider
- ✨ AI content/Slider SEO
- 🌐 server sync / server sliders
- ✅ publish
- ⚠ revision conflict
- ↻ refresh from server

Final workspace:

`catalog_center/app/product_workspace_epic49.py`

Inheritance:

`ProductWorkspaceEpic49 -> ProductWorkspace871 -> ProductWorkspace87`

Existing V87/V871 workflow is preserved; Epic extends it rather than replacing it.

Adds:
- effect selector;
- transition/display timing;
- server revisions;
- local cinematic Preview from real cached Product images;
- refresh current Product from Server;
- manage all server sliders.

Server Slider Manager:

`catalog_center/app/epic49_server_slider_manager.py`

Edits:
- title;
- description;
- alt;
- focus keyword;
- button;
- exact image from same Asset;
- effect;
- transition/display timing;
- order;
- active state;
- revision/source/operator.

---

## Catalog Bridge unified contract

Bridge runtime:
- version `1.3.0`;
- contract `epic49-unified-v1`;
- same existing Bearer token / HMAC authorization.

Old endpoints retained:
- `/api/catalog-bridge/v1/health/`
- `/api/catalog-bridge/v1/import/`
- `/api/catalog-bridge/v1/diagnostics/<batch_name>/`

New endpoints:
- `GET /api/catalog-bridge/v1/products/`
- `GET /api/catalog-bridge/v1/products/<id>/`
- `POST /api/catalog-bridge/v1/products/<id>/sync/`
- `GET /api/catalog-bridge/v1/hero-slides/`
- `GET /api/catalog-bridge/v1/hero-slides/<id>/`
- `POST /api/catalog-bridge/v1/hero-slides/<id>/sync/`

Writes use explicit Allow-lists.

Hero image ownership is enforced: an image belonging to another Asset cannot be assigned to a Hero slide.

---

## Revision / conflict protection

Product Profile and Hero each have independent `sync_revision`.

If Windows revision equals Server revision:
- update accepted;
- revision incremented.

If Server revision is newer:
- HTTP `409 Conflict`;
- current server payload returned;
- Windows shows conflict and requires review/refresh.

Admin Product edits bump Profile revision.
Admin Hero edits bump Hero revision.
Profile Admin and Hero Admin mirror common Slider fields so they do not become competing sources.

Audit fields:
- `last_modified_source`: `desktop` / `admin`;
- `last_modified_by`: employee/operator/admin username.

---

## Same-batch idempotency

Key:

`batch_uuid + source_hash`

Purpose:
- multiple Asset saves/signals inside one official import must not conflict with themselves;
- repeated import of identical batch must not inflate revisions;
- duplicate Product/Hero must not be created.

Hero revision increments only when actual Hero state changes.

---

## ACK enrichment

Import ACK additionally returns:
- `server_product_id`
- `product_revision`
- `slider_id`
- `slider_revision`
- `sync_contract=epic49-unified-v1`

Windows stores revisions for subsequent optimistic updates.

---

## Brand contract after Full Suite cleanup

Canonical public brand asset:

`static/img/brand/3dprinthublogo.png`

Home and Store both use the canonical approved logo for browser icon/apple-touch references.

Legacy files under `static/favicon/` remain preserved for compatibility/history but are not the brand Source of Truth because they were generated before the final approved canonical-logo contract and their provenance could not be proven from Repository history.

---

# Epic49 tests

Key behavioral tests:
- `store.test_phase49_unified_sync`
- `store.test_phase49_unified_import_e2e`
- `store.test_epic49_operator_publish`
- `store.test_phase49_1_frontend_contract`
- `catalog_bridge.test_phase49_unified_bridge`
- `catalog_bridge.tests.test_epic49_contract`
- `website.test_phase49_2c_hero_studio`
- `website.test_phase49_2b_hero_login_hotfix`
- `website.test_phase45_homepage_hero`
- `catalog_center/tests/test_phase49_unified_desktop.py`
- all `catalog_center/tests/test_*epic49*.py`.

E2E test builds a real v8.5 batch, imports through the official `phase37_import_catalog_center` command, then verifies Product/Profile/Hero/image/SEO/effect/timing/revision/idempotency.

---

# CI issues found and fixed before handoff

1. **Legacy Windows tests tied to old workspace filename**
   - fixed by validating real inheritance `Epic49 -> V871 -> V87`.

2. **CI tried to write media under `/home/sfkilvrs`**
   - production settings were not changed;
   - CI uses isolated `/tmp/3dprinthub-ci/...` env paths.

3. **Legacy Bridge contract expected 1.2.0 / epic49-final**
   - upgraded to real 1.3.0 / epic49-unified-v1;
   - legacy import/health/diagnostic routes are explicitly tested as retained.

4. **Legacy Hero template test required direct Product URL expression**
   - upgraded to `slide.target_url` safe runtime contract;
   - active Product -> canonical product URL;
   - unpublished Product -> Store list;
   - retired External Catalog URL prohibited.

5. **Legacy favicon test required old favicon pack**
   - public layouts canonicalized to final approved `3dprinthublogo.png`;
   - legacy favicon files preserved, not used as brand source of truth.

After these corrections, final CI Run `32129944811` / Job `95688635543` completed successfully through the full Django suite.

---

# Temporary CI probe rule

Draft PRs/branches with `ci/phase49-unified-*` and `PHASE49_EPIC_SELFTEST_PROBE*` were created only to force GitHub Actions runs against the Epic branch.

They must **never be merged** into the Epic or Main branch.

The implementation branch itself contains no probe marker files.

---

# Current validation gate

## Completed
- Epic code implemented on GitHub.
- Django migrations tracked.
- Windows schema tracked.
- Bridge read/write revision contract tracked.
- targeted tests green in GitHub Actions.
- Windows tests green in GitHub Actions.
- full Django suite green in GitHub Actions.
- detailed Epic document written.

## Pending before production
1. Windows `git pull/switch` to Unified Epic;
2. local DB + Catalog Center data backup;
3. `check` + `makemigrations --check`;
4. inspect `migrate --plan`;
5. apply `store.0030` and `website.0021` locally;
6. verify DB columns/revisions;
7. run targeted tests locally;
8. run Website/Store/Catalog Bridge/full suite locally;
9. run Catalog Center Windows test/verify;
10. visual QA Product Workspace / Hero Studio / Server Slider Manager;
11. one real local employee flow:
    `internet -> Windows -> Product SEO -> Hero SEO/image/effect -> publish -> Django -> edit Admin -> refresh Windows`;
12. explicit user approval;
13. production backup/deploy/migrations/collectstatic/restart/smoke.

**Production deployment is NOT approved yet.**

No host changes should be made until Windows local acceptance is complete.
