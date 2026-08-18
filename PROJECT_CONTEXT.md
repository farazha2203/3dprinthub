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
`GitHub phase branch -> Windows sync -> local tests -> local visual acceptance -> explicit approval -> production backup -> production deploy -> smoke tests`.
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

## Current active phase
**Phase 49.2B — Master Admin + Customer Portal**

### Design source
- Approved source: uploaded `master.zip` only (Velzon Django Corporate 4.3.0).
- `interactive` is rejected and must not be used.
- Existing Master RTL assets under `static/velzon_master/` are reused rather than copying the full demo package.
- Django models, permissions, actions, forms, URLs, Store/Catalog Bridge behavior and database schema must remain intact.

### Exact brand logo
The one approved logo is the exact user-supplied file installed as:
`static/img/brand/3dprinthublogo.png`
Expected SHA-256:
`97ec202678e386387fa9ebe2c6055fa45967d1f341d40dbc5f2d9e980b873cec`
This SHA-256 supersedes the earlier provisional logo hash. The approved source file is the user's local `D:\projects\3dprinthublogo.png` with this exact hash.
It must never be redrawn, recolored, substituted or regenerated. Transparent logo surfaces must have no forced white tile, padding, border or shadow. `static/css/brand-mark-contract.css` points UI brand marks to this asset.

### Typography
Source: user-supplied `fonts.rar`. Required IRANSans FaNum WOFF weights are mapped in `static/css/phase49_2b-design-system.css`:
200 UltraLight, 300 Light, 400 Regular, 500 Medium, 700 Bold, 900 Black.
`scripts/install_phase49_2b_brand_assets.ps1` installs the exact logo and the six required font files from the user's own archives.

### Visual system
Shared tokens: deep navy/graphite (`#050b12`, `#081522`, `#102235`), metallic gold (`#d99a18`, `#f3b52d`), light surfaces and slate text/borders. This mirrors the supplied navy/gold logo and the site while keeping Master/Velzon structure.

### Admin implementation
Master RTL/Bootstrap remains loaded by `templates/admin/base.html`.
Final 49.2B layers are loaded through `templates/admin/base_site.html`:
- `static/css/phase49_2b-design-system.css`
- `static/css/phase49_2b-admin.css`
Admin login now extends `admin/base_site.html` so the same typography/branding applies. Sidebar/topbar/cards/tables/forms/filters/object tools and responsive states are styled without changing Django admin behavior.

### Customer Portal implementation
`templates/website/customer/account_base.html` remains the parent shell and preserves dashboard, support, profile, addresses, appearance, affiliate, notifications, store orders and build-order links.
New assets:
- `static/css/phase49_2b-customer.css`
- `static/js/phase49_2b-customer.js`
Desktop keeps a branded sidebar; <=1100px becomes an accessible off-canvas drawer with overlay/Escape/resize handling.

### Detailed phase document
See `docs/PHASE49_2B_MASTER_ADMIN_CUSTOMER.md`.

## Database / migrations
No model, schema or data migration is intended in Phase 49.2B.

## Production gate
**Production deployment is NOT approved yet.**
Before host deploy the exact branch must pass on Windows:
1. install exact user logo/fonts using the phase installer and commit/push those user-owned assets;
2. `python manage.py check`;
3. `python manage.py makemigrations --check --dry-run`;
4. `python manage.py test website.test_phase49_2b_master_ui -v 2`;
5. `python manage.py test website -v 2`;
6. `python manage.py test store -v 2`;
7. `python manage.py test catalog_bridge -v 2`;
8. `python manage.py test -v 2`;
9. visual QA of Admin and Customer Portal on desktop and 320/360/390/430px/mobile/tablet;
10. explicit user approval.

After approval only: backup production DB, deploy exact approved commit, preserve runtime data, run required checks/migrations, `collectstatic --noinput`, restart Passenger, smoke-test site/Admin/Customer/Store/Bridge and record deployed commit here.

## Next planned work after 49.2B
Continue functional/admin workflow improvements only after the Master-based Admin and Customer Portal are locally and production verified.
