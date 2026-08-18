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
Therefore the Store catalog/image models exist before Phase49.2C runs.

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

## Mobile / accessibility
- `prefers-reduced-motion` disables cinematic transforms/filter/clip effects.
- <=600px `soft_blur` falls back to a simple fade and reveal avoids expensive clip-path transitions.
- Existing swipe/keyboard/dots/arrows/pause-on-hover/focus behavior remains.
- One active slide still renders without unnecessary navigation controls.

## Admin transition preview
The change form includes a lightweight local preview stage. It reads the current `transition_effect` and `transition_duration_ms` form values and previews the effect without saving.

## Tests
Primary regression suite:
`python manage.py test website.test_phase49_2c_hero_studio -v 2`

Then required gates:
- `python manage.py check`
- `python manage.py makemigrations --check --dry-run`
- `python manage.py migrate --plan`
- `python manage.py migrate`
- Phase49.2C test
- Phase49.2B/45 regression tests
- `website`, `store`, `catalog_bridge`, full suite
- desktop + 320/360/390/430/tablet visual QA

## Rollback
Before production migration, rollback is Git branch-only. After migration 0020 is applied, code rollback must first be assessed because old code does not know the new columns but the columns are additive and nullable/defaulted. Do not drop columns or reset the database as a code rollback shortcut. Production deploy remains blocked until local migration/tests/visual approval are complete.
