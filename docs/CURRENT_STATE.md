# CURRENT PROJECT STATE

Updated: 2026-09-01

## Current active checkpoint — Phase49.3I.47

Status: `IMPLEMENTED + WINDOWS CI PASS + ADMIN CI PASS + STOREFRONT CI PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT TOUCHED`

Repository: `farazha2203/3dprinthub`
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Code checkpoint: `9984e3bb9ab5ff293ad275ecbe86dba3a96db4b1`
Documentation checkpoint before this file update: `b9c64874dcb4b6290f743af1b0550f6f82add845`
Rollback: `backup/pre-phase49-3i47-owner-workspace-20260901` → `ecfd9260c168140757781bb672eb57c77bcc4ee3`
Canonical phase document: `docs/phases/PHASE49_3I47_QT_WORKSPACE_IMAGE_BULK_AI_SITE_IA.md`

## What is implemented

### Products
- Product Gallery remains bounded/lazy from Phase49.3I.46.
- Four lifecycle workspaces are exposed: active, sent/published, archived, rejected/deleted.
- Product cards expose title, description excerpt and image count.
- legacy/local Product image fallback resolves older Products that have local image files but no modern URL mapping.
- multi-select Products can run `AI تکمیل همه موارد` sequentially through the one shared AICore and shared single-Product postprocessing path.

### Product images / SEO
- all selected Product images are finalized under one semantic SEO identity;
- every image receives the same intended alt/title/caption/keywords metadata set;
- physical SEO WebP files use deterministic unique sequence suffixes such as `-01`, `-02`, `-03`;
- dedicated regression verifies all physical files exist and metadata is consistent across the image set.

### Add Product / Crawl
- Operations is split into three focused workspace tabs instead of one tall control wall;
- persistent inventory is immediately usable;
- inventory has Windows-like gallery/image and details/table views;
- cards/rows can show local thumbnail, title, description excerpt and image count;
- bounded 100-row Crawl paging from Phase49.3I.46 remains authoritative.

### Profile / Pricing
Three full-height tabs are now used:
1. `پروفایل و روش قیمت`
2. `وزن و زمان تولید`
3. `فیلامنت، رنگ و قیمت قطعی`

Production and Filament/price tables have enough minimum height to avoid the previous clipped nested-scroll presentation.

### Django Admin / Website management
- shared responsive accessible tabbed change-form architecture;
- Product Sales / Source / SEO workspaces;
- Store pricing settings grouped by task;
- material/color pricing split into focused tabs;
- site settings and quote workspaces organized into tabs.

### Storefront
- Product information is organized into progressive accessible tabs;
- existing Variant/Profile/pricing business authority is preserved.

## Verification

Qt/Desktop code checkpoint `9984e3bb9ab5ff293ad275ecbe86dba3a96db4b1`:
- `qt6-full-parity-windows` — run `33506242569` — PASS;
- `phase49-3i17` — run `33506242669` — PASS.

Admin checkpoint `ef215ba09044cd421302f9057bf3c1565b99ef1e`:
- `product-admin-workspace` — run `33505851712` — PASS;
- `phase49-3i17` — run `33505851749` — PASS.

Storefront checkpoint `f4beec484f060063d00de4a5753a135a020cfea1`:
- `phase50-variant2-gallery` — run `33506122579` — PASS;
- `phase49-3i17` — run `33506122534` — PASS.

Dedicated regression:
`catalog_center/tests/test_phase49_3i47_qt_workspace_image_bulk_ai.py`

It locks multi-image SEO numbering/metadata, local image fallback, Operations tabs and Windows-like views, Profile/Pricing tabs, sequential Bulk AI, and Product lifecycle tabs.

## Error corrected in this checkpoint

`ERR-49-087` conceptual root cause: Phase49.3I.46 correctly solved bounded database paging but retained monolithic presentation and incomplete multi-image/legacy-UI parity. The correction is Phase49.3I.47. Detailed implementation/verification is recorded in the canonical phase document above.

Prevention rule: large list/workflow surfaces must combine bounded database access with task-oriented tabbed information architecture, legacy-data fallbacks and many-item regressions; lazy SQL alone is not sufficient UX parity.

## webdesign1.zip

The owner supplied `webdesign1.zip` for typography/layout/effects/SEO study. The attachment name was received, but the declared mounted path was not readable in this Chat runtime and the file was not present in the active sandbox. No claim is made that the archive was read. The current 3I.47 work uses the project’s already-registered UI/UX engineering references plus owner QA. Re-ingest the ZIP when it becomes readable before attributing further design decisions to those books.

## Database / Host / Production safety

- Django migration changed = NO.
- Production MySQL changed = NO.
- Catalog destructive migration = NO.
- Host source changed = NO.
- Production deploy = NO.
- default launcher cutover = NO.
- secrets changed = NO.

Last verified Production application commit remains `c283864290f9c989a9fcdf24ee8eef519560e917`.
Last verified Production DB evidence still confirms only `store.0034` and `store.0035`; do not assume later migrations are applied without a fresh read-only Host audit.

## Exact next task

1. Owner closes Catalog Center.
2. On `D:\projects\3DPrintHub`, verify correct repository, active branch, clean worktree and live GitHub head.
3. Pull only by ff-only to the final documentation head.
4. Run repository-owned `RUN_PHASE49_3I42C_LOCAL_GATE.ps1 -ExpectedHead <final-head> -LaunchApp`; the runner is version `49.3I.47.1` and creates a checksum-verified Catalog SQLite backup before QA.
5. Foreground QA on real Catalog data:
   - four Product lifecycle tabs;
   - old/local Product thumbnails + title/description/image count;
   - sequential multi-select full AI on disposable Products;
   - one Product with at least three images → all SEO files numbered and metadata consistent;
   - Add Product/Crawl three workspaces + gallery/details views;
   - Profile/Pricing three full-height tabs and all rows visible.
6. If any contract fails, patch only that failed contract with a focused regression.
7. Production remains blocked until explicit owner Local acceptance.

Historical checkpoints remain available in Git history and their dedicated `docs/phases/` documents.
