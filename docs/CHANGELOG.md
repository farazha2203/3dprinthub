# PROJECT CHANGELOG

Record meaningful changes only. Older detailed entries remain available in Git history.

## 2026-08-26 — Phase50.A.1G Velzon Operator Surface V2

### Owner QA / requested delta
- owner confirmed the `bc7b97f` Product Admin 500 fix and business navigation deployment,
- visual QA showed the legacy Django `#changelist-filter` remained permanently visible, squeezed the Product table and retained old English Filter/Action controls,
- owner re-supplied `master.zip` and requested a substantially more modern/professional Admin comparable to the best project Admin experience rather than another small CSS adjustment.

### Theme review
- reviewed owner-supplied Velzon Django Corporate `4.3.0` / Bootstrap `5.3.6` package,
- reused Velzon design/composition patterns for cards, off-canvas controls, tables/forms and responsive operator UI,
- purchased vendor assets remain private/gitignored under `static/velzon_master/` and are not published to the public GitHub repository,
- project-owned adapter CSS/JS/templates are committed normally.

### Implemented
- added `static/admin/phase50-admin-console-v2.css`,
- added `static/admin/phase50-admin-console-v2.js`,
- loaded V2 assets from `templates/admin/base.html`,
- default changelist is now full-width; the native Django filter node is moved into an on-demand `فیلترها` drawer rather than reserving a permanent column,
- added backdrop, close/Escape, reset filters and active-filter count,
- normalized legacy Filter/Search/Action labels to the Persian operator UI,
- modernized search toolbar, bulk actions, result table and pagination as Velzon card surfaces,
- added sticky result headers, controlled horizontal table scrolling and row hover,
- long change forms gain sticky horizontal section navigation and card fieldsets,
- preserved native Django ModelAdmin actions, permissions, filters, query semantics and business models,
- no migration/schema change.

### Verification
- added static/UI contract regressions to `store/test_phase50_admin_http_regression.py`,
- CI workflow now validates the V2 JavaScript with `node --check`,
- GitHub Actions `Phase50 Product Admin Workspace CI` run `32955310832` PASS on runtime snapshot `3687d0922959fca53f2118be6dacd32639159346`,
- Python compile PASS, JavaScript syntax PASS, Django check PASS, migration drift NONE, CI SQLite migrations PASS, focused Admin HTTP/static regressions PASS.

### Production status
- current Production remains verified at `bc7b97f9c63432b8105f52f61cf5cdae1369689b`,
- Admin V2 is not yet deployed,
- next gate is fresh Production backup + explicit `FETCH_HEAD` ff-only deploy + collectstatic + Passenger restart + owner visual QA.

## 2026-08-26 — Phase50.A.1F Business Admin Navigation / Product Admin 500 Fix — Production Verified
- fixed Product changelist 500 caused by formatting a SafeString with numeric format code in `estimated_profit_admin`,
- added real-row Product changelist regression,
- reorganized Admin navigation around Store, Orders, Finance, Production, Windows/Catalog, Homepage, Content, Engagement, Support, Affiliate and System groups,
- deployed and verified at `bc7b97f9c63432b8105f52f61cf5cdae1369689b`,
- fresh rollback backup at `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-125848`,
- Product Admin render 200, Velzon business navigation PASS, Home/Store/Admin login 200, private imported-media refs 0, no migration.

## 2026-08-26 — Phase50.A.1E Production Deployment Verified

### Deployment
- deployed active branch application snapshot `9cfbc54ed4196144864b5f4201976d8466a88134` to Production,
- Phase50.A.1E runtime remained the CI-tested code from snapshot `f34eaa3bbad965b2092279291ff8adf93f3d908e`; later commits through deployed HEAD were documentation/archive-only,
- fresh rollback backup created at `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-114327`,
- rollback source HEAD recorded as `8fbe3413cada1099745f4d17312b8eb519694379`,
- MySQL backup/source backup verification passed before source deployment.

### Production gates
- Production root/branch/worktree gate PASS,
- MySQL vendor/name gate PASS for `sfkilvrs_EmiAdmin_3dprinthub`,
- `store.0034_phase50_variant2_commerce` applied,
- `store.0035_phase50_sales_profiles` applied,
- post-deploy migration plan empty,
- no new migration executed,
- Django check PASS with known warnings only,
- migration drift NONE,
- unified Product Admin runtime section/inlines gate PASS,
- collectstatic PASS,
- Passenger restart completed,
- Home/Store/Admin login HTTP 200,
- public Homepage private imported-media references = 0,
- final Production worktree clean.

### Resolved deployment incident
- first deployment attempt stopped safely before source mutation because `git fetch --prune origin` did not advance the active branch remote-tracking ref,
- host `remote.origin.fetch` was configured only for tag `v0.33.0`; active branch had no upstream,
- corrected path explicitly fetched `refs/heads/agent/phase49-3i18-operator-bulk-ai-rebuild` to `FETCH_HEAD`, verified SHA/ancestry and used ff-only merge,
- incident recorded as `ERR-50-007`.

## 2026-08-26 — Phase50.A.1E Unified Product Admin Workspace
- added `store/phase50_product_admin_workspace.py` as final additive Product Admin composition boundary,
- organized Product edit in the exact requested business order while preserving mature Product/ProductCatalogProfile/ProductVariant/SEO data,
- no new migration,
- corrected CI run `32941662288` PASS on snapshot `f34eaa3bbad965b2092279291ff8adf93f3d908e`.

## 2026-08-25 — Phase50.A.1C Admin Media Integrity / Mobile Hero / Homepage SEO / Windows Image Dimensions
- safe ImportedPrintAsset Admin media resolver using Product-owned public media,
- compact mobile Hero, homepage SEO audit and Windows image dimensions,
- corrected CI run `32875771848` PASS.

## 2026-08-25 — Phase50.A.1B Product Gallery + Variant 2.0 Foundation
- Product gallery/lightbox, Variant 2.0 size/build/package fields, StoreOrderItem snapshots,
- migration `store.0034_phase50_variant2_commerce`, CI run `32872549545` PASS.

## 2026-08-25 — Catalog Center Windows v8.8.1 Final Portable Release
- released `3DPrintHub-CatalogCenter-v8.8.1.exe`, build `2026.08.25.2`, SHA256 `c32f37affcbd2c6ffacb803247daf804a490fecd7c8162bc37c2729a2197e990`.

## 2026-08-25 — Phase50.A.1 Admin Storefront / Hero Parity
- Product/imported-asset Hero controls and Storefront/Coupon/Shipping/Pricing/address Admin surfaces.

## 2026-08-25 — Phase50.A Admin Command Center
- authenticated `/admin/command-center/` organized around Sales, Treasury, Accounting/Ledgers, Purchasing and Inventory/Production.

## 2026-08-25 — Phase49.3I.30 Production Hero Product-Media Ownership
- fixed Production Hero media ownership to Product-owned public gallery/main media; imported working-media remained private.

## 2026-08-25 — Phase49.3I.29 Production Deployment Verified
- Phase49 application deployed with MySQL backup, migrations/collectstatic/Passenger restart and HTTP verification.

## 2026-08-25 — Phase49.3I.29 Structured Web Product Presentation
- customer-readable Product sections replaced raw technical output.

## 2026-08-25 — Phase49.3I.28 Exact-Link Canonical Title Call Contract
- fixed duplicate `current_title` binding.

## 2026-08-25 — Phase49.3I.27 Exact-Link Category Provider Crash Fix
- bridged mature `App.get_all_categories()` provider.

## 2026-08-25 — Phase49.3I.26 Unified Exact-Link Completion
- restored canonical Product stages, observable AI, vertical gallery and bulk archive/delete workflow.
