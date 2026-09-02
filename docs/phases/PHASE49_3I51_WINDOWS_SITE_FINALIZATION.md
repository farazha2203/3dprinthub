# Phase49.3I.51 — Windows + Site Finalization

Date: 2026-09-02

Status: `IN_PROGRESS / SOURCE IMPLEMENTED / CI RECERTIFICATION RUNNING / OWNER LOCAL QA NEXT / PRODUCTION NOT TOUCHED`

Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Pre-phase rollback: `backup/pre-phase49-3i51-windows-site-finalization-20260902` → `191e8ef83f9a804805dda4cdd3df66b8224264d6`.

## Requested delta

Finalize the current Windows Catalog Center and complete the matching Site-side management contract without creating a second architecture.

Windows:
- make Product image review visibly larger and easier to operate;
- preserve multi-image selection and bulk actions;
- keep a fixed source-page open action in Product editing;
- detect Source from pasted Search/Product URLs so MakerWorld URLs cannot silently run under a stale GrabCAD selection;
- expose progressive Discovery/Receive results while the receive process is running;
- create a clearly named `پیش‌فرض` Product Profile when source facts cannot produce a usable Profile;
- owner fallback values are 100 g model, 50 g support and 60 minutes;
- fallback Filaments include all active PLA/PETG family inventory such as PLA-CF, PLA Silk and PETG-HF, but not unrelated materials;
- split Filament identity management into Filaments, Materials, Brands and Colors;
- assign Brand/Material/Color from managed registries rather than free-typing them inside Filament edit;
- allow optional descriptions on Filament, Brand and Material plus a Material reference price-per-kg.

Site:
- add a persistent Filament Brand registry rather than keeping Brand only as repeated text;
- persist optional Brand, Material and Filament descriptions;
- expose the same management concepts through Django Admin;
- extend the existing authenticated Filament Bridge rather than creating a second sync API;
- keep real Filament selling price authority as sale-price-per-roll divided by roll weight.

## Touched surfaces

Windows:
- `catalog_center/app/epic49_desktop_schema.py`;
- `catalog_center/qt6/parity_core.py`;
- `catalog_center/qt6/parity_dialogs.py`;
- `catalog_center/qt6/pages.py`;
- `catalog_center/qt6/product_wizard.py`;
- `catalog_center/qt6/image_gallery.py`;
- `catalog_center/qt6/kernel.py`;
- `catalog_center/qt6/acquisition_runtime.py`;
- focused Qt tests and the canonical Local gate.

Site:
- `store/phase39_models.py`;
- `store/phase50_filament_offer.py`;
- `store/phase39_admin.py`;
- `website/models.py`;
- `website/admin.py`;
- `catalog_bridge/unified_views.py`;
- additive migrations `website.0024` and `store.0042`;
- Bridge/Admin regressions.

## Must-not-touch

- no direct source edit on Production;
- no alternate crawler or alternate AI engine;
- no hidden price invention;
- no automatic Production publish;
- no mutation of paid historical orders;
- no secret movement into Git, Admin or SQLite;
- no migration apply before real Host/MySQL identity, migration plan, backup and rollback are verified;
- no replacement of the mature Batch/FTP/Bridge/Product publish path.

## Database and migration safety

Windows Catalog SQLite:
- only the existing additive `available_filament_offers.description` column is added through the normal parity-schema composer;
- registry metadata uses the existing Catalog settings table;
- Local acceptance must create a checksum-verified copy of the canonical SQLite before launch.

Django candidate migrations:
- `website.0024_phase49_3i51_material_catalog_description`;
- `store.0042_phase49_3i51_filament_registry_descriptions`.

These migrations are additive. They are currently GitHub/CI candidates only and are not authorized for Production until the normal read-only Host audit and fresh MySQL backup are complete.

## Regression contract

Dedicated Windows regression:
`catalog_center/tests/test_phase49_3i51_windows_site_finalization.py`

It locks:
- explicit default Profile fallback;
- PLA/PETG-family fallback inventory;
- managed Brand/Material/Color identity;
- four Filament workspace tabs;
- larger image stage and source-page action;
- multi-image selection observability;
- MakerWorld URL Source auto-detection;
- live discovery result surface.

Site regressions extend:
- `catalog_bridge/tests/test_phase49_3i41_filament_bridge.py`;
- `store/test_phase49_3i51_filament_registry_admin.py`.

## CI issues already found during implementation

Two earlier red runs represented changed contracts or test-fixture debt, not unexplained runtime failures:
- the previous Qt regression required four compact image columns while the owner requested larger cards; the regression was updated to the intentional three-column large-card contract;
- the previous source-profile regression forbade fallback print-time/profile creation; the owner now explicitly requires a named default Profile, so that regression was updated;
- the first rewritten fallback test then referenced a helper that does not exist in that test class. This is fixture-only and is corrected by creating the Product with the same `Database.upsert_product` path used elsewhere in that suite;
- Site regressions that asserted Filament Bridge contract v2 were updated to v3 because the payload now intentionally round-trips registry descriptions.

No failed command is repeated under the same known-bad condition.

## Acceptance sequence

1. GitHub CI all relevant gates green on one exact head.
2. Canonical Local gate version `49.3I.51.1` runs on clean Windows checkout after checksum-backed Catalog SQLite backup.
3. Owner foreground QA verifies Product images, Crawl Source detection/live results, default Profile and Filament registries.
4. Only after owner acceptance: read-only Host state/migration audit.
5. Verify Production MySQL identity, exact migration plan, disk and rollback.
6. Create fresh source/.env/MySQL backup and verify checksum/non-empty dump.
7. Deploy the exact approved GitHub commit from GitHub.
8. Apply only the verified migration chain.
9. Verify Admin/Bridge/store runtime and public Product behavior.
10. Update CURRENT_STATE/ROADMAP/CHANGELOG/ERRORS/DATABASE with exact Production evidence.
