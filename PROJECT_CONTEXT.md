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
GitHub is the code source of truth. Required flow:
`GitHub phase branch -> Windows sync -> local migration plan/test -> local visual acceptance -> explicit approval -> production backup -> production deploy -> smoke tests`.
Never reset production DB for a code/deploy problem. Preserve `.env`, MySQL, `media`, `private_media`, Catalog Center state/API keys and other runtime data.

## Stable recovery baseline
Phase 31 remains the historical recovery baseline: 2408 fixture objects, 51 fixture models, 31 provinces, 427 counties, 1242 cities; production DB/media backups existed and site/admin smoke checks were HTTP 200. Production data may have grown since then.

## Phase 49.2A foundation retained
Phase 49.2A consolidated the active product path:
`Windows Catalog Center 8.7.1 -> Catalog Bridge -> Product/ProductCatalogProfile -> Store`.
Public external ready-model catalog/Link Analyzer intake routes are retired and must not be restored to satisfy legacy tests. Historical records remain. External model sync is disabled by default. Material and USD/FX pricing logic remain independent.
Catalog Center: version `8.7.1`, build `2026.08.16.3`.
Latest known local results before 49.2B: Catalog Bridge 9/9 OK; Store 220 tests OK with one local MySQL-specific skip. Mobile/Desktop public-site stabilization is part of the retained foundation.
Known warnings remain visible: `ckeditor.W001` (CKEditor 4 technical debt) and `store.W026` (in-memory realtime layer; shared Redis needed for cross-process production realtime if required).

## Phase 49.2B foundation retained — Master Admin + Customer Portal
- Approved design source: uploaded `master.zip` only (Velzon Django Corporate 4.3.0).
- `interactive` is rejected and must not be used.
- Existing Master RTL assets under `static/velzon_master/` are reused.
- Exact user logo: `static/img/brand/3dprinthublogo.png`.
- Approved SHA-256: `97ec202678e386387fa9ebe2c6055fa45967d1f341d40dbc5f2d9e980b873cec`.
- User-supplied IRANSans FaNum weights are mapped as 200/300/400/500/700/900 in `static/css/phase49_2b-design-system.css`.
- Admin uses Master RTL + `phase49_2b-design-system.css` + `phase49_2b-admin.css`.
- Customer Portal uses `phase49_2b-customer.css/js`, desktop sidebar and <=1100px accessible drawer.
- Admin desktop Login regression was fixed: full auth shell is no longer constrained to 460px; only the login card is capped around 520px.
- Managed Hero Phase49.2B hotfix aligned Hero SEO/image/title/description/target with Store Product and retired External Catalog URLs.
- Phase49.2B Hero backend compatibility remains active in 49.2C: Store target resolver, SEO/image suggestions, `pre_save` completion and new-slide `is_active=True` default.
- The old Phase49.2B Select2 Admin Hero UI is retired in 49.2C and must not be restored just to satisfy an obsolete test.

## Current active phase
**Phase 49.2C — Hero Studio & Cinematic Slider**

Branch:
`epic/phase49-2c-hero-studio`

Detailed document:
`docs/PHASE49_2C_HERO_STUDIO.md`

### Goal
Make homepage Hero management visual and fast: select a product from an image album instead of a slow autocomplete-only workflow, select the exact product image with a persistent database relation, edit existing slides without delete/recreate, and choose a cinematic transition/timing per slide.

### UI / icon contract
No new frontend/icon library is installed. Existing Master/Velzon Remix Icons are used:
- search: `ri-search-2-line`
- filter: `ri-filter-3-line`
- gallery/image: `ri-image-2-line`
- selected state: `ri-checkbox-circle-fill`
- refresh: `ri-refresh-line`
- edit: `ri-edit-2-line`
- cinematic settings: `ri-movie-2-line`
- preview: `ri-play-circle-line`
- pagination: Remix arrow icons

Admin Studio files:
- `templates/admin/website/homepageheroslide/change_form.html`
- `static/css/admin-phase49_2c-hero-studio.css`
- `static/js/admin-phase49_2c-hero-studio.js`

The old Django autocomplete remains collapsed as an emergency/advanced fallback only.

### Album Picker backend
Staff-only ModelAdmin endpoints:
- `/admin/website/homepageheroslide/product-browser/`
- `/admin/website/homepageheroslide/asset-detail/`

The Product browser uses actual active Store Products backed by `ImportedPrintAsset`, 24 per page. Search covers Persian/English title, SKU, source external id, imported title/id and source name. Category filter uses real Store `Category` rows.

Selecting a product immediately:
1. writes the actual `ImportedPrintAsset` FK to the existing form;
2. fetches Phase49.2B / Catalog Center 8.7.1 SEO suggestions;
3. fills title/group/description/alt/button for a deliberate new selection;
4. renders the product image album without a first Save;
5. leaves every field manually editable before final Save.

### Database / migration
**Phase49.2C intentionally has a real additive migration.**

Migration:
`website/migrations/0020_phase49_2c_hero_studio.py`

Previous chain:
`website.0019_phase45_managed_homepage_hero -> store.0027_phase39_variant_color_fk`.
`ImportedPrintAssetImage` exists since `store.0009_inventory_finance_catalog`, so the FK target is available before 0020.

Added `HomepageHeroSlide` fields:
- `selected_asset_image`: nullable FK to `store.ImportedPrintAssetImage`, `SET_NULL`, no reverse relation.
- `transition_effect`: choice field, default `cinematic_fade`.
- `transition_duration_ms`: default 1400, valid 300..4000 ms.
- `display_duration_ms`: default 7000, valid 2000..30000 ms.

No table/row/media deletion exists in migration 0020. Existing slides keep all old data, receive transition defaults, and start with `selected_asset_image=NULL` until an operator selects an album image.

Runtime alignment module:
`website/phase49_2c_hero_studio.py`.
It contributes the same four persistent fields declared by migration 0020 to the mature runtime model rather than rewriting the very large legacy `website/models.py`. ORM/Admin/makemigrations remain aligned with the migration state.

### Local 0020 validation — 2026-08-18
Local DB vendor: SQLite.
Backup created under:
`D:\projects\3dprinthub-backups\phase49_2c_20260818-123411`.

Before 0020:
- full `db.sqlite3` copied;
- `website_homepageheroslide` exported to JSON;
- Hero rows: **2**.

After 0020:
- migration applied successfully;
- Hero rows: **2**;
- verified columns: `selected_asset_image_id`, `transition_effect`, `transition_duration_ms`, `display_duration_ms`;
- missing columns: none;
- `PHASE49_2C_DB_VERIFY=OK`.

Checks/tests:
- `makemigrations --check --dry-run`: **No changes detected**.
- `website.test_phase49_2c_hero_studio`: **9/9 OK**.
- first combined Phase49.2B/45 regression: 15 tests OK + 1 stale test failure because it still required `P49_HERO_PREFILL_URL` in the form.
- stale test has now been upgraded: 49.2B server fallback is required, but 49.2C Album Picker must be the only Admin Hero UI and legacy `admin-phase45-hero.js`/`P49_HERO_PREFILL_URL` must not return.

### Image selection precedence
1. manually selected `selected_asset_image.image`;
2. that image row's `remote_url`;
3. explicit legacy `image_url`;
4. Catalog/Store preview fallback.

Manual Hero Studio image selection is intentionally authoritative so a later Catalog Center publish cannot silently overwrite a manually approved Hero image. Choosing the default/fallback card clears the relation and returns the slide to Catalog/Store fallback behavior.

### Existing slide editing
Homepage Hero changelist is patched to expose:
- preview and title as edit links;
- explicit edit action with `ri-edit-2-line`;
- inline transition-effect edit;
- inline sort-order edit;
- inline active-status edit;
- display/transition timing summary.

Deleting/recreating an existing slide is no longer required.

### Cinematic transition engine
Frontend assets:
- `static/css/phase49_2c-hero-effects.css`
- `static/js/phase49_2c-home-hero.js`
- `templates/website/partials/hero.html` exposes per-slide effect/timing data.

Effects:
1. `cinematic_fade`
2. `wedding_dissolve`
3. `cinematic_zoom`
4. `ken_burns`
5. `soft_blur`
6. `cinematic_reveal`

The engine uses per-slide `setTimeout` timing, not a fixed `setInterval`. Each slide independently owns transition and display durations. Existing keyboard, swipe, dots, arrows, focus/hover pause and visibility pause behavior are retained.

### Legacy engine / cache isolation
The new root has `data-p49c-engine`. New JS removes `data-p45-hero` before DOMContentLoaded; therefore even an old browser-cached Phase45 JS cannot initialize a second slider engine against the same Hero.

### Mobile / accessibility
- `prefers-reduced-motion` removes cinematic animation and transforms.
- <=600px soft-blur becomes simple fade; reveal avoids expensive mobile clip animation.
- one active slide keeps navigation controls hidden as before.

### Admin effect preview
Hero Studio has a local preview stage reading the current transition type/duration from the form, so the operator can preview the selected effect before Save.

## Pending Store migration gate discovered during Phase49.2C
The local migration plan also exposed two **older Epic49 Store migrations** still pending locally:
- `store.0028_epic49_catalog_product_schema` — creates `ProductCatalogProfile`.
- `store.0029_epic49_catalog_product_backfill` — profile backfill plus Product slug/SEO normalization.

0029 can change Product fields including:
- `slug`, `canonical_url`;
- `meta_title`, `meta_description`, `seo_focus_keyword`;
- `og_title`, `og_description`;
- `editorial_source_url`, `source_attribution`, `hashtags`;
- `robots_index`, `robots_follow`.

Therefore **do not run a general `python manage.py migrate` yet**. 0028/0029 require an explicit read-only audit first.

### Read-only audit command
Path:
`store/management/commands/epic49_catalog_migration_audit.py`

Purpose:
- mirror the relevant 0029 slug/SEO calculations;
- report whether 0028/0029 are applied;
- report profile-table existence;
- count imported Products/profiles affected;
- count Product slug changes and per-field SEO changes;
- show detailed changed Product/SKU rows;
- perform **zero database mutation**.

Run:
`python manage.py epic49_catalog_migration_audit --limit 100`

JSON option:
`python manage.py epic49_catalog_migration_audit --limit 0 --json`

Behavior test:
`python manage.py test store.test_epic49_catalog_migration_audit -v 2`

The test snapshots Product slug/SEO fields, runs the command, verifies the Product is byte-for-byte unchanged at field level, and verifies no `ProductCatalogProfile` was created.

## Phase49.2C validation gate
**Production deployment is NOT approved. Migration 0020 must not be applied on host yet. Store 0028/0029 must not be applied locally/host until audit approval.**

Required Windows sequence now:
1. sync latest `epic/phase49-2c-hero-studio`;
2. rerun `website.test_phase49_2b_hero_login_hotfix`, `website.test_phase49_2c_hero_studio`, `website.test_phase45_homepage_hero`;
3. run `store.test_epic49_catalog_migration_audit`;
4. run `epic49_catalog_migration_audit --limit 100` and review all summary counts and changed slugs;
5. only after explicit audit approval: new local DB backup and controlled application of Store 0028/0029;
6. then `website`, `store`, `catalog_bridge`, full suite;
7. visual QA: Hero Studio add/edit/list, Home Hero desktop + 320/360/390/430/tablet, all six effects and reduced-motion behavior;
8. explicit user approval;
9. only then production DB backup/deploy/migrations/collectstatic/restart/smoke tests.

Known warnings remain:
- `ckeditor.W001`: CKEditor4 maintenance/security debt; separate upgrade phase required.
- `store.W026`: in-memory realtime layer; Redis needed for cross-process production realtime if required.

## Rollback rule
Before production migration, rollback is branch/code-only. After 0020 is applied locally, do not drop columns/reset DB as a shortcut. The migration is additive and old data remains. Store 0028/0029 must be audited before application because 0029 changes Product slug/SEO data.

## Next planned work after Phase49.2C
After compatibility retest and Store migration audit are accepted, continue visual Hero Studio QA, apply only approved pending migrations, run full suite, then return to Master-based Admin/Customer workflow improvements. No host changes before local approval.
