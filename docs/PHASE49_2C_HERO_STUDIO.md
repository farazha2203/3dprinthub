# Phase 49.2C — Hero Studio & Cinematic Slider

## Goal
Replace the slow text/autocomplete-only homepage Hero workflow with a visual album picker, persistent image relation, explicit edit workflow and per-slide cinematic transitions while preserving Phase49.2A Store URLs/SEO and Phase49.2B Master Admin/Customer Portal.

## Branch
`epic/phase49-2c-hero-studio`

## UI / icons
No new icon or UI dependency is installed. Existing Master/Velzon Remix Icons are used:
- `ri-gallery-view-2` / gallery context
- `ri-search-2-line` / product search
- `ri-filter-3-line` / category filter
- `ri-image-2-line` / image album
- `ri-checkbox-circle-fill` / selected state
- `ri-refresh-line` / refresh
- `ri-edit-2-line` / explicit edit action
- `ri-movie-2-line` / transition settings
- `ri-play-circle-line` / transition preview
- `ri-arrow-*-s-line` / pagination

Admin Studio assets:
- `templates/admin/website/homepageheroslide/change_form.html`
- `static/css/admin-phase49_2c-hero-studio.css`
- `static/js/admin-phase49_2c-hero-studio.js`

The original Django autocomplete field remains in a collapsed emergency/advanced section. Normal workflow is the visual album.

## Product Album Browser
Staff-only ModelAdmin endpoints:
- `/admin/website/homepageheroslide/product-browser/`
- `/admin/website/homepageheroslide/asset-detail/`

The browser returns active Store Products backed by `ImportedPrintAsset`, 24 per page. Search covers Persian/English title, SKU, Store source external id, imported title/id and source name. Category filtering uses the real Store `Category` relation.

Selecting a product:
1. writes its `ImportedPrintAsset` id into the existing `asset` form field;
2. fetches Phase49.2B/8.7.1 SEO suggestions;
3. fills title/group/description/alt/button for a deliberate new selection;
4. renders the product image album without an initial save;
5. keeps all fields manually editable before save.

## Persistent database model
Migration: `website/migrations/0020_phase49_2c_hero_studio.py`.

Existing dependency chain:
`website.0019_phase45_managed_homepage_hero -> store.0027_phase39_variant_color_fk`.
`ImportedPrintAssetImage` already exists since `store.0009_inventory_finance_catalog`, so the new FK dependency is valid before 0020.

Added fields on `HomepageHeroSlide`:
- `selected_asset_image`: nullable FK to `store.ImportedPrintAssetImage`, `SET_NULL`, no reverse relation.
- `transition_effect`: persistent choice, default `cinematic_fade`.
- `transition_duration_ms`: 300..4000 ms, default 1400.
- `display_duration_ms`: 2000..30000 ms, default 7000.

No table, row, media file or historical slide is deleted. Existing slides receive safe defaults and keep `selected_asset_image=NULL` until explicitly chosen.

Runtime registration is in `website/phase49_2c_hero_studio.py`. This additive module contributes the same fields defined by migration 0020 to the mature `HomepageHeroSlide` runtime class, avoiding a risky rewrite of the very large legacy `website/models.py` while keeping ORM/admin/makemigrations aligned with the real database schema.

## Image precedence
Hero render image priority after Phase49.2C:
1. manually selected `selected_asset_image.image`;
2. manually selected image row `remote_url`;
3. explicit legacy `image_url`;
4. Phase49.2B Catalog/Store preview fallback.

A manual Hero Studio selection is intentionally authoritative so a later Catalog Center publish cannot silently replace it. Choosing the fallback/default image card clears the relation and returns the slide to Catalog/Store fallback behavior.

## Edit workflow
Homepage Hero changelist now exposes:
- preview and title as edit links;
- explicit `ri-edit-2-line` edit button;
- transition effect inline-editable;
- sort order inline-editable;
- active status inline-editable;
- timing summary.

Full edit retains image, SEO copy, object fit, focal position, transition, timing and publication controls. Deleting/recreating a slide is not required.

## Cinematic transition engine
Frontend assets:
- `static/css/phase49_2c-hero-effects.css`
- `static/js/phase49_2c-home-hero.js`
- existing `templates/website/partials/hero.html` exposes per-slide data attributes.

Effects:
1. `cinematic_fade` — cross fade + subtle incoming zoom.
2. `wedding_dissolve` — long soft dissolve inspired by wedding/photo montage editing.
3. `cinematic_zoom` — crossfade with outgoing/incoming scale motion.
4. `ken_burns` — slow pan/zoom during display with fade transition.
5. `soft_blur` — blur dissolve on capable displays.
6. `cinematic_reveal` — soft clip reveal + caption float.

Each slide independently owns effect, transition duration and display duration. The new engine uses `setTimeout`, not a hard-coded `setInterval`, so each slide timing is respected.

## Cache / legacy-engine isolation
`hero.html` retains the old Phase45 data structure for HTML/tests but adds `data-p49c-engine`. The new JS removes `data-p45-hero` before DOMContentLoaded. Therefore an old cached Phase45 JS file cannot initialize against the same root and two slider engines cannot run together.

The old Phase49.2B server compatibility layer remains intentionally active (`hero_suggestions`, Store target URL, `pre_save`, Admin `is_active=True` default). The old Admin Select2/`P49_HERO_PREFILL_URL` UI is retired from the change form. Regression tests now enforce this split: 49.2B backend compatibility remains, 49.2C is the only Admin Hero UI engine.

## Mobile / accessibility
- `prefers-reduced-motion` disables cinematic transforms/filter/clip effects.
- <=600px `soft_blur` falls back to a simple fade and reveal avoids expensive clip-path transitions.
- Existing swipe/keyboard/dots/arrows/pause-on-hover/focus behavior remains.
- One active slide still renders without unnecessary navigation controls.

## Admin transition preview
The change form includes a lightweight local preview stage. It reads the current `transition_effect` and `transition_duration_ms` form values and previews the effect without saving.

## Local database validation — 2026-08-18
Windows project: `D:\projects\3DPrintHub`.
Database vendor during this validation: SQLite.

Before migration 0020:
- backup directory created under `D:\projects\3dprinthub-backups\phase49_2c_20260818-123411`;
- full SQLite DB copied;
- `website_homepageheroslide` exported to JSON;
- exported Hero rows: **2**.

Checks:
- `python manage.py check`: no error; existing `ckeditor.W001` warning only at this step.
- `python manage.py makemigrations --check --dry-run`: **No changes detected**.
- `website.0019`: already applied.
- `website.0020_phase49_2c_hero_studio`: applied successfully.

Post-migration introspection:
- Hero rows after migration: **2**;
- columns present: `selected_asset_image_id`, `transition_effect`, `transition_duration_ms`, `display_duration_ms`;
- missing columns: none;
- `PHASE49_2C_DB_VERIFY=OK`.

Primary tests:
- `python manage.py test website.test_phase49_2c_hero_studio -v 2`: **9/9 OK**.
- combined Phase49.2B/45 regression run initially returned 15 OK + 1 legacy-contract failure because the old test still expected `P49_HERO_PREFILL_URL` in the Admin form.
- the failure was not a runtime/UI failure; it was a stale test contract after the Album Picker replaced the old Select2 UI.
- the compatibility test has now been updated to require the 49.2B server fallback but forbid the old Admin UI from returning.

Known warnings visible in test runs:
- `ckeditor.W001`: CKEditor4 maintenance/security technical debt.
- `store.W026`: in-memory Channels layer cannot deliver Worker events across multiple processes; Redis is required if cross-process realtime remains needed in production.

## Pending Store migrations discovered during local plan
`python manage.py migrate --plan` exposed two Store migrations that are still pending on the local DB:
- `store.0028_epic49_catalog_product_schema` — creates `ProductCatalogProfile`.
- `store.0029_epic49_catalog_product_backfill` — creates/refreshes catalog profiles and may change Product slug and SEO metadata.

0029 is not treated as a blind schema step because it may update:
- `Product.slug`;
- `canonical_url`;
- `meta_title`, `meta_description`;
- `seo_focus_keyword`;
- `og_title`, `og_description`;
- `editorial_source_url`, `source_attribution`;
- `hashtags`;
- `robots_index`, `robots_follow`.

Do **not** run a general `python manage.py migrate` until the audit below is reviewed.

## Read-only Store 0028/0029 audit
Management command:
`store/management/commands/epic49_catalog_migration_audit.py`

Run:
`python manage.py epic49_catalog_migration_audit --limit 100`

Optional full machine-readable output:
`python manage.py epic49_catalog_migration_audit --limit 0 --json`

The command mirrors migration 0029 slug/SEO calculations but performs no DB create/update/save/delete. It reports migration state, profile-table presence, affected Product count, slug-change count and per-field change counts. A dedicated behavior test verifies Product data and ProductCatalogProfile row count remain unchanged after the command.

Test:
`python manage.py test store.test_epic49_catalog_migration_audit -v 2`

## Tests / next validation gate
Primary regression suite:
`python manage.py test website.test_phase49_2c_hero_studio -v 2`

Current next steps on Windows:
1. sync latest `epic/phase49-2c-hero-studio`;
2. rerun Phase49.2B/49.2C/45 compatibility tests;
3. run `store.test_epic49_catalog_migration_audit`;
4. run `epic49_catalog_migration_audit --limit 100` and review output;
5. only after audit approval, back up local DB again and decide whether to apply Store 0028/0029;
6. then `website`, `store`, `catalog_bridge`, full suite;
7. desktop + 320/360/390/430/tablet visual QA of Hero Studio and all six effects;
8. explicit user approval.

## Rollback
Before production migration, rollback is Git branch-only. After migration 0020 is applied locally, the new columns are additive and existing rows remain intact. Do not drop columns or reset a database as a code rollback shortcut. Production migration 0020 and Store 0028/0029 remain blocked until local tests, audit and visual approval are complete.
