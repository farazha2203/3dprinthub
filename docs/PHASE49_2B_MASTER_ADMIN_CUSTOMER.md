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
IRANSans FaNum weights are mapped in `static/css/phase49_2b-design-system.css` as 200/300/400/500/700/900. The user-supplied `fonts.rar` is the asset source. The installer script copies only the required FaNum WOFF files.

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
`scripts/install_phase49_2b_brand_assets.ps1` validates the exact final logo SHA-256, copies it unchanged, extracts six IRANSans FaNum WOFF weights from the user's archive, and refuses a different logo.

## Database
No model or data migration is part of Phase 49.2B.

## Validation gate
Before production: `manage.py check`, no pending migrations, Phase49.2B tests, website/store/catalog_bridge suites, full suite, desktop/mobile visual review of Admin and Customer Portal, explicit user approval. Production deployment remains blocked until those checks pass.
