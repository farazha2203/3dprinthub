# Phase 49.2B — Master Admin + Customer Portal

## Design source
- UI reference: uploaded `master.zip` (Velzon Django Corporate 4.3.0) only.
- `interactive` is explicitly rejected and is not part of this phase.
- Existing Velzon Master RTL assets in `static/velzon_master/` are reused; the full demo package is not copied into the project.

## Brand
- Exact canonical user logo: `static/img/brand/3dprinthublogo.png`.
- Final approved SHA-256: `97ec202678e386387fa9ebe2c6055fa45967d1f341d40dbc5f2d9e980b873cec`.
- This hash supersedes the earlier provisional logo hash.
- Approved source file on Windows: `D:\projects\3dprinthublogo.png`.
- Logo is never regenerated/recolored and must render on a transparent surface without forced white tiles.
- Colors: deep navy/graphite surfaces with metallic gold accents derived from the supplied logo.

## Typography
IRANSans FaNum weights are mapped in `static/css/phase49_2b-design-system.css` as 200/300/400/500/700/900. The user-supplied `fonts.rar` is the original asset source. The six approved WOFF files are tracked in the project once installed.

## Admin architecture
Django Admin behavior remains intact. `templates/admin/base.html` continues to load Master RTL/Bootstrap assets. Phase 49.2B is an override layer loaded through `templates/admin/base_site.html`:
- `static/css/phase49_2b-design-system.css`
- `static/css/phase49_2b-admin.css`

The layer standardizes font, sidebar/topbar colors, cards, tables, forms, filters, object tools, responsive behavior and login branding without changing models, permissions, admin actions, URLs or database schema.

## Customer Portal architecture
`templates/website/customer/account_base.html` remains the common parent for customer pages and keeps current routes/features. New assets:
- `static/css/phase49_2b-customer.css`
- `static/js/phase49_2b-customer.js`

Desktop uses a branded sticky sidebar; tablet/mobile use an accessible off-canvas drawer. Dashboard, support, profile, addresses, appearance, affiliate, notifications and store-order links remain available.

## Asset installer
`scripts/install_phase49_2b_brand_assets.ps1` validates the exact final logo SHA-256 and copies it unchanged. It first verifies whether all six required IRANSans FaNum WOFF files already exist and are non-empty. When they are already present, they are reused and **7-Zip is not required**. Archive extraction and 7-Zip are only required if one or more required font files are actually missing.

## Managed homepage Hero hotfix
The Phase45 Hero was still coupled to the retired public External Catalog and its Admin form only copied an image URL after manually clicking the saved gallery. Selecting an asset did not prefill title, description, group or SEO alt text, and a newly-created slide was not initially approved. This made the homepage fall back to the brand logo when no active slide existed.

Phase 49.2B fixes this without a schema migration:
- `website/phase49_2b_hero_hotfix.py` installs runtime fallback properties and a `pre_save` safety net for `HomepageHeroSlide`.
- **Catalog Center 8.7.1 slider SEO is the first content source.** The hotfix reuses the existing server resolver in `store/epic49_publish_options.py` for `homepage_slider_title_fa`, `homepage_slider_description_fa`, `homepage_slider_alt_text`, `homepage_slider_button_text` and `homepage_slider_focus_keyword`, including its AI content-pack fallback.
- If dedicated slider copy is missing, title falls back through Persian imported title, Store Product title and source title.
- Description then falls back through Persian short description, Store Product short description and imported descriptions.
- Group fallback prefers the Store Product category and then catalog/source metadata.
- SEO image alt is generated from the resolved product title/group only when the dedicated 8.7.1 alt is absent.
- The image selected by Catalog Center (`homepage_slider_image_url`) is preferred; imported local media for that remote URL is used when available, then normal imported preview/catalog image and Store Product media are considered.
- Hero targets now resolve only to an active Store Product or the Store product list. `external_catalog_detail` is not a valid Hero target anymore.
- Staff-only endpoint `website:hero_slide_prefill` supplies immediate Admin suggestions after selecting an asset.
- `static/js/admin-phase45-hero.js` listens to the Django Select2 asset selector, fills title/description/group/Alt/button, shows the 8.7.1 focus keyword status, enables the new-slide approval checkbox and renders candidate image choices before a first save.
- `templates/admin/website/homepageheroslide/change_form.html` loads the hotfix JS with an explicit cache version.
- The public Hero renders `effective_description` and `target_url`; an active slide with no image does not masquerade as the site logo.
- `WebsiteConfig.ready()` loads the runtime contract for web requests, tests, shell and management commands.

The existing Catalog Center 8.7.1 publish path remains authoritative for automated publishing: when `homepage_slider_enabled` is enabled in the desktop payload, `store.epic49_publish_options.apply_homepage_slider()` creates or updates the asset slide, stores the selected image and SEO copy, and marks that generated slide active. Manual Admin editing remains available as an operator override/review layer.

Existing inactive slides remain intentionally inactive until an administrator approves them; no old data row is silently published by this hotfix.

## Admin login desktop hotfix
The first 49.2B CSS constrained the entire authentication content wrapper to `460px`, which made `/admin/login/` look like a mobile layout on desktop. The fix restores a full-width desktop authentication shell and constrains only the login card to approximately `520px`. The Admin CSS cache version is bumped to `49.2.1`. Internal Admin pages are not affected by this login-only layout fix.

## Database
No model or data migration is part of Phase 49.2B. The Hero hotfix uses runtime properties/signals and existing fields only.

## Validation gate
Before production: `manage.py check`, no pending migrations, Phase49.2B tests, website/store/catalog_bridge suites, full suite, desktop/mobile visual review of Admin and Customer Portal, explicit user approval. Production deployment remains blocked until those checks pass.

Focused regression tests now include:
- `website.test_phase49_2b_master_ui`
- `website.test_phase49_2b_hero_login_hotfix`
- `website.test_phase45_homepage_hero`
