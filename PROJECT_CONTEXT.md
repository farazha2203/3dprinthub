# PROJECT_CONTEXT - 3DPrintHub

## Permanent paths

- Windows project root: `D:\projects\3DPrintHub`
- Windows Catalog Center runtime: `D:\projects\3dprinthub_catalog_center`
- Windows Catalog Center data: `D:\projects\3dprinthub-catalog-manager`
- Windows Catalog Center rollback backups: `D:\projects\3dprinthub-backups`
- Production project root: `/home/sfkilvrs/3dprinthub`
- Production virtualenv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`
- Production MySQL database: `sfkilvrs_EmiAdmin_3dprinthub`
- Repository: `farazha2203/3dprinthub`
- Production runtime: Python 3.12, Django, MySQL, cPanel Passenger
- Local runtime: Python 3.12, Django, SQLite for tests/development

## Source-of-truth and delivery rule

GitHub is the code source of truth. Runtime state/data are not Git artifacts.
The required delivery flow is:

`GitHub phase branch -> exact Windows sync -> local checks/tests -> local visual acceptance -> reviewed main/tag -> production backup -> production deployment -> production smoke tests`

Never deploy to production before the exact branch/commit passes local validation and is explicitly approved.
Never reset the production database to solve a code/deployment problem.

Runtime data not replaced by Git includes:

- `.env` and secrets
- MySQL data
- local SQLite/runtime state
- `media` and `private_media`
- generated `staticfiles`
- licensed font/runtime assets intentionally kept outside Git
- Catalog Center API keys, local configuration, browser state and SQLite data

## Stable recovery baseline

Phase 31 recovery completed successfully and remains the historical recovery baseline:

- 2408 transferred fixture objects
- 51 fixture models
- 31 provinces
- 427 counties
- 1242 cities
- business model counts matched at restore time
- production MySQL/media backups were created
- site/admin smoke checks returned HTTP 200

Production data is live and can grow. Runtime verification uses invariants and lower bounds rather than destructive equality resets.

## Current active phase

**Phase 49.2A — Core consolidation + mobile stabilization**

Primary goals:

1. Keep the normal Store and Windows Catalog Center -> Catalog Bridge -> Product publishing path.
2. Keep material pricing and USD/FX pricing logic independent and active.
3. Retire the old direct public external ready-model catalog / Link Analyzer intake cycle.
4. Preserve historical database rows and useful parser/security/license/worker logic without exposing retired public routes.
5. Keep Catalog Center 8.7.1 slider/SEO/publish contracts.
6. Make the public website, Store and customer surfaces mobile-first and stable on real phone widths.

## Phase 49.2A retired public surface

The following old public flows are intentionally retired and must not be restored merely to satisfy legacy tests:

- `/store/ready-models/`
- old ready-model detail/public sitemap routes
- `/store/link-analyzer/`
- customer link-analysis public pages
- old external-ready-model homepage templates/schema
- public `ready_catalog` order intake choice

Historical records are preserved. External model automation is disabled by default through the Phase49.2A kill switch.

## Canonical active product flow

`Windows Catalog Center 8.7.1 -> Catalog Bridge -> Product/ProductCatalogProfile -> active Store product -> product detail URL`

Catalog Center canonical source lives in repository path `catalog_center/`.
The installed Windows runtime path is `D:\projects\3dprinthub_catalog_center`; it is not an expendable duplicate.
Catalog Center runtime data lives separately under `D:\projects\3dprinthub-catalog-manager`.

## Catalog Center version

- Application version: `8.7.1`
- Build ID: `2026.08.16.3`
- The former `release/catalog-center-8.7.1-slider-seo` work was merged into the Phase49.2A branch so slider/SEO/publish changes are not lost.

## Repository cleanup already performed

Superseded working-tree copies removed from the active branch include:

- Phase44 Catalog Center source backups
- Phase43 `_site_datafix` package and launcher
- old standalone Catalog Center changelog copies for superseded versions
- superseded transfer builders; `build_3dprinthub_transfer_v4.ps1` remains the retained generation
- retired external catalog/link-analyzer public templates

Git history remains the recovery source for removed tracked files.

## Validation state before mobile stabilization

Latest user-provided local results before this mobile subphase:

- Catalog Bridge contract tests: **2/2 OK**
- Full Catalog Bridge tests: **9/9 OK**
- Full Store suite: **220 tests OK, 1 environment-specific MySQL test skipped**
- Website suite: most tests OK, but six Phase27/44/46 assertions were stale and still required retired Phase27/external-catalog UI contracts.

The stale Website tests are aligned to the active Phase45/49.2A contract; retired public routes must not be resurrected.

Known warnings that are not the cause of these test failures:

- `ckeditor.W001`: CKEditor 4.22.1 is unsupported and has unresolved security issues; migrate in a separate controlled editor phase.
- `store.W026`: production realtime currently uses an in-memory channel layer; configure a production-capable shared channel layer (for example Redis when hosting supports it) before relying on cross-process realtime.

Warnings must not be hidden merely to make test output look clean.

## Phase 49.2A mobile stabilization contract

Mobile is treated as a first-class UI, not a desktop shrink-down.
Target validation widths include at minimum:

- 320 px
- 360 px
- 390 px
- 430 px
- tablet widths through 1023 px

The final responsive layer is:

`static/css/phase49_2a-mobile-first.css`

### Desktop-isolation hotfix

During the first mobile stabilization attempt, generic image/reset rules were placed outside responsive media queries and the Phase45 no-slide fallback logo was still allowed to grow to a very large size. This produced an unacceptable desktop visual regression where the fallback brand artwork dominated the viewport.

The hotfix contract is now explicit:

- `phase49_2a-mobile-first.css` must not apply layout/image reset rules above 1023px.
- All responsive layout rules in that file are scoped inside phone/tablet media queries.
- The generic unscoped `img { height:auto }` reset is prohibited by regression test.
- The Phase45 fallback logo has an explicit desktop cap of 320x320 and smaller tablet/phone caps.
- The normal Header logo keeps its explicit desktop dimensions and receives smaller dimensions only inside responsive breakpoints.
- Active Hero slide images retain their own Phase45 object-fit/object-position contract.

This hotfix adds no model, database migration, data conversion or production data change.

The responsive layer covers:

- accidental horizontal overflow protection only on responsive widths
- compact fixed header and consistent mobile/tablet navigation
- accessible menu state and scroll locking
- touch-safe controls
- 16px mobile form controls to avoid unwanted mobile browser zoom
- compact Phase45 managed hero and readable mobile CTA/caption
- one-column intro/cards/guides where appropriate
- contained horizontal scrolling for real tabular data and wizard steps instead of page overflow
- mobile order wizard layout
- Store filter/category/card/navigation layout
- customer portal/login/register mobile shell
- reduced decorative horizontal motion on small screens

## Canonical brand mark contract

The approved UI brand mark is the existing transparent PNG:

`static/img/brand/logo-icon-512.png`

Rules:

- Header, no-slide Hero fallback, Store/page icons and quote/payment branding use this canonical static asset.
- UI templates must not reference the superseded `img/brand/logo-header.png` or `img/brand/logo-full.png` artwork.
- A transparent brand mark must never receive an artificial `bg-white`, padding tile, border or card shadow directly behind the image.
- `static/css/brand-mark-contract.css` is the final logo-only cascade layer. It must stay isolated from general layout styling.
- If a future intentionally non-transparent logo asset is introduced, its containing surface must match the asset background color so there is no visible rectangular patch.
- Brand icon/favicons in public/store/quote HTML should use the same canonical PNG unless an explicitly approved derivative is created.
- Regression tests scan public templates for superseded brand artwork and verify transparent logo behavior.

This brand cleanup changes no database model or business data and requires no migration.

## Current production gate

**Production deployment is NOT approved yet.**

Before deployment, the exact current branch commit must pass on Windows:

1. `python manage.py check`
2. `python manage.py makemigrations --check --dry-run`
3. targeted Phase49.2A + mobile/brand regression tests
4. `python manage.py test website -v 2`
5. `python manage.py test store -v 2`
6. `python manage.py test catalog_bridge -v 2`
7. `python manage.py test -v 2`
8. local visual verification at desktop and phone/tablet widths
9. explicit user approval

Visual acceptance must include both:

- desktop regression check at >= 1280px, including no-slide Hero fallback and transparent Header logo
- mobile checks at 320/360/390/430px and tablet <= 1023px
- quote/payment page brand mark without a white rectangular backing

After approval only:

1. create production DB backup
2. deploy the exact approved commit/tag
3. preserve production `.env`, MySQL and media
4. run Django checks/migrations only as required
5. run `collectstatic --noinput`
6. restart Passenger (`tmp/restart.txt`)
7. verify Home, Store, product detail, customer entry points and Catalog Bridge health
8. verify retired public routes remain 404
9. verify mobile presentation on the deployed public site
10. record exact deployed commit and verification result here

## Next planned phase

After Phase49.2A is locally and production-verified, proceed to **Phase 49.2B Admin redesign** using the approved admin design source while preserving Django models, actions, permissions and backend behavior.
