# CURRENT PROJECT STATE

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Base Epic: `epic/phase49-unified-product-slider-sync`
Active Phase: `49.3I`
Active Hotfix: `49.3I.27 — Exact-Link Category Provider Bridge`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA REQUIRED`
Production: `UNTOUCHED / NOT APPROVED`

## Owner Evidence Driving 49.3I.27
Windows visual/runtime QA of 49.3I.26 showed the canonical exact-link button fails immediately with:

`AttributeError: 'Database' object has no attribute 'categories'`

The failure occurs before source fetch / progress / AI execution.

## Verified Root Cause
The mature Product Studio gets Catalog categories from `self.app.get_all_categories()` and uses App category maps for the visible category combobox. `catalog_center.app.db.Database` intentionally has no `categories()` repository API.

49.3I.26 introduced two calls to `workspace.db.categories()` in the unified exact-link path. A later composition guard attempted to normalize `Database.categories` only *if it existed*, therefore it did nothing on the real Database class and the operator button crashed immediately.

## 49.3I.27 Implemented on GitHub
- added `phase49_3i27_category_provider_bridge.py` as a narrow final runtime compatibility layer,
- exact-link category rows now come from the existing `App.get_all_categories()` contract,
- no duplicate category table/repository was added,
- no database schema change and no migration,
- the bridge is composed after 49.3I.26 so both category lookups inside the existing unified workflow see the canonical App category provider,
- invalid category rows are ignored rather than crashing the Product workflow,
- focused unit tests cover a real-shaped Workspace whose Database has no `categories` method,
- the Windows Phase49.3I gate now compiles/tests 49.3I.27 before launching the application.

## Preserved 49.3I.26 Contract
- stage order remains Basic Info → Commerce → Images → Content/SEO → Source/License → Slider → Review/Publish,
- stage navigation remains free; readiness blocks publish only,
- exact-link completion remains 0–100% observable with 120-second AI ceiling,
- AI receives Product/source text only and no image URL/file,
- one exact-link workflow still owns Product SEO + image text metadata,
- image file finalization only runs when selected source images are already local,
- five-column vertical Product image gallery remains final layout,
- Product Workspace full-screen toggle remains,
- Products gallery selection/archive/identity-preserving block remains,
- new acquisition default remains 5 source images + one extra local source-page screenshot,
- persistent diagnostics and startup no-hidden-AI rules remain.

## Database / Migration / Safety
- Django migration: `NONE`
- Catalog schema migration: `NONE`
- no reset/drop/truncate
- no Product/media/history physical deletion
- no API key/token committed
- Local Catalog SQLite is never copied to Production MySQL
- Production untouched

## Verification Status
GitHub code + focused tests + Windows runner are committed, but no Windows execution result has been reported for 49.3I.27 yet. Do not mark accepted or deployable until the Local gate and real button test pass.

## Exact Next Task — Windows 49.3I.27 Gate
1. close Catalog Center,
2. verify Local worktree is clean; dirty means STOP/INSPECT,
3. fetch/prune + ff-only pull the live feature branch,
4. verify Local HEAD == fetched Remote HEAD,
5. run `catalog_center\RUN_PHASE49_3I26_OPERATOR_COMPLETION_GATE.ps1` with the newly verified HEAD,
6. launch Product Workspace and press `تکمیل همه اطلاعات بر اساس لینک محصول`,
7. verify the old `Database.categories` exception is gone and progress enters source-fetch stage,
8. continue the full 49.3I.26 acceptance: real source facts → AI → preview → apply Product/SEO/image text metadata,
9. if any new error occurs, export fresh diagnostics and keep historical logs intact.

## Release Gate
Windows PASS → one Local Publish E2E → Local Store/Admin/Product/Media/SEO verification → explicit owner approval → read-only Production environment verification → approved GitHub snapshot only → Production verification.
