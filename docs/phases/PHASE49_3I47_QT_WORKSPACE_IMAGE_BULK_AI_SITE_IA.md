# Phase49.3I.47 — Qt Workspace, Multi-Image SEO, Bulk AI, Admin + Storefront Information Architecture

Date: 2026-09-01

Status: `IMPLEMENTED + WINDOWS CI PASS + ADMIN CI PASS + STOREFRONT CI PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT TOUCHED`

Repository: `farazha2203/3dprinthub`
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Code checkpoint: `9984e3bb9ab5ff293ad275ecbe86dba3a96db4b1`
Rollback: `backup/pre-phase49-3i47-owner-workspace-20260901` → `ecfd9260c168140757781bb672eb57c77bcc4ee3`

## Owner QA that triggered this phase

After Phase49.3I.46 solved bounded database paging, the owner’s real Local QA exposed a presentation/workflow parity gap rather than another Crawl-core problem:

- Acquisition controls consumed too much vertical space, hiding the persistent inventory.
- Crawl inventory lacked the requested Windows-like image/gallery versus details views.
- Received Product cards did not expose enough useful facts such as image count and description.
- Legacy/local Product images could exist on disk but not render when modern URL mapping was missing.
- Products needed explicit lifecycle workspaces for active, sent/published, archived and rejected/deleted records.
- Multi-select Products needed the same full-content AI action available for one Product, executed safely through the one shared AICore.
- Full Product AI/image finalization could leave only the primary image with final SEO naming/metadata instead of treating every selected image consistently.
- Profile/Pricing was too scroll-heavy and could clip production rows.
- Product/Admin pricing/site settings and Storefront Product information needed the same task-oriented tabbed information architecture.

## Qt Product workspace

The Product surface now exposes four lifecycle tabs:

1. `محصولات فعال`
2. `ارسال / منتشرشده`
3. `آرشیو شده`
4. `حذف / رد شده`

The existing reversible archive/reject/restore semantics remain authoritative; this is a presentation/workflow reorganization, not a hard-delete redesign.

Product cards now expose useful preview facts including Product title, description excerpt and image count.

Legacy/local image fallback was added so older Products with files below their local Product directory can still resolve a visible local preview even when modern URL→local-file mapping metadata is absent.

## Sequential multi-Product full AI

Products can be multi-selected and sent through `AI تکمیل همه موارد` using the same process-wide AICore used by single-Product work.

The bulk path is intentionally sequential rather than spawning competing Product AI jobs. It shares the single-Product full-content postprocessing/finalization path so bulk execution does not become a second AI implementation.

Provider/Model/source rules remain those of the existing Single Active AI contract. Commerce/Profile/Publish ownership rules are not bypassed.

## Multi-image SEO and physical files

Image finalization now treats the Product image set as one semantic SEO identity while still creating unique physical filenames.

Example for three images with base SEO name `organic-table-lamp.webp`:

- `organic-table-lamp-01.webp`
- `organic-table-lamp-02.webp`
- `organic-table-lamp-03.webp`

All selected images receive the same semantic metadata set where appropriate:

- alt text,
- title,
- caption,
- keywords,

while each physical WebP receives its own deterministic sequence suffix. The files are verified to exist in the Product `seo_images` directory.

This restores the mature expectation that every image of one Product is finalized consistently rather than only the primary image.

## Add Product / Crawl workspace

The formerly tall Operations surface is split into focused workspace tabs so the inventory is immediately usable instead of being pushed below a large control wall.

The Operations page has three workspace tabs covering the persistent inventory, acquisition/receive controls and history/status work.

The inventory provides two Windows-like presentation modes:

- image/card gallery view,
- details/table view.

Inventory rows/cards can expose Product preview facts already received into the Catalog, including local thumbnail where available, image count, Product title and description excerpt.

The bounded 100-row paging contract from Phase49.3I.46 remains intact; 3I.47 changes presentation and preview enrichment, not the core ledger authority.

## Profile / Pricing workspace

The Profile editor is split into three full-height task tabs:

1. `پروفایل و روش قیمت`
2. `وزن و زمان تولید`
3. `فیلامنت، رنگ و قیمت قطعی`

The production table and filament/price table receive sufficient minimum height so rows are not hidden behind nested scroll-heavy layouts.

Business authority remains unchanged: Profile identity/dimensions, production rows, Filament/color choices and pricing rules still use the existing mature data contracts.

## Django Admin information architecture

The same task-oriented architecture is applied to the existing Admin surfaces without introducing a second pricing or Product model:

- responsive accessible tabbed change-form behavior,
- Product Sales / Source / SEO workspaces,
- Store pricing settings grouped by task,
- material/color pricing split into focused tabs,
- site settings and quote-related workspaces organized into tabs.

Shared tab CSS/JS is used instead of isolated per-form ad-hoc styling.

## Storefront Product information architecture

Storefront Product information is reorganized into progressive accessible tabs with dedicated CSS/JS behavior rather than one long information wall.

This phase is an information-architecture/presentation change; existing Variant/Profile/price/business truth remains authoritative.

## Verification

Dedicated regression:
`catalog_center/tests/test_phase49_3i47_qt_workspace_image_bulk_ai.py`

It locks:

- three-image SEO filenames exactly `-01/-02/-03` plus equal semantic metadata and physical file existence;
- legacy local-image fallback;
- three Operations workspace tabs + two inventory view modes + image count/description visibility;
- three full-height Profile/Pricing tabs and complete production rows;
- sequential multi-Product AICore execution;
- four Product lifecycle tabs + Bulk `AI تکمیل همه موارد` action.

Windows / Qt evidence on code checkpoint `9984e3bb9ab5ff293ad275ecbe86dba3a96db4b1`:

- `qt6-full-parity-windows` — run `33506242569` — PASS;
- `phase49-3i17` — run `33506242669` — PASS.

Admin evidence on `ef215ba09044cd421302f9057bf3c1565b99ef1e`:

- `product-admin-workspace` — run `33505851712` — PASS;
- `phase49-3i17` — run `33505851749` — PASS.

Storefront evidence on `f4beec484f060063d00de4a5753a135a020cfea1`:

- `phase50-variant2-gallery` — run `33506122579` — PASS;
- `phase49-3i17` — run `33506122534` — PASS.

The repository-owned `RUN_PHASE49_3I42C_LOCAL_GATE.ps1` is extended through Phase49.3I.47 and remains the canonical owner Local acceptance runner.

## Safety

- Django migration changed = NO.
- Production MySQL changed = NO.
- Production/Host source changed = NO.
- Catalog destructive rewrite = NO.
- Default launcher cutover = NO.
- Secret handling changed = NO.
- Existing Product/Crawl/Profile/Pricing authorities are preserved and wrapped rather than replaced.

## webdesign1.zip source note

The owner supplied `webdesign1.zip` and explicitly requested use of those books for website typography, layout, effects and SEO. In this Chat runtime the attachment name was received, but the declared mounted file path was not readable and the file could not be located in the active sandbox. Therefore this phase does **not** falsely claim book-derived decisions from that unread archive.

The current Admin/Storefront information architecture is grounded in the project’s already-registered UI/UX engineering references and the owner’s concrete QA. The uploaded archive should be re-ingested when it becomes readable, then useful source-derived principles can be registered in project docs and applied in later visual/typography/SEO refinement.

## Owner Local acceptance

Before 3I.47 is marked LOCAL_TESTED/ACCEPTED on real data:

1. Pull the final GitHub documentation HEAD by ff-only on the canonical Windows repo.
2. Run the repository-owned Local gate with `-ExpectedHead` and `-LaunchApp`; allow it to create and checksum-verify the Catalog SQLite backup.
3. Products:
   - verify the four lifecycle tabs;
   - verify old Products with local image files now show thumbnails;
   - verify card title + description + image count;
   - multi-select two disposable Products and run full AI using Saved Data first; verify sequential completion and refresh.
4. Images:
   - choose one disposable Product with at least three selected images;
   - run final content/image finalization;
   - verify every image has the same intended semantic SEO metadata and distinct numbered SEO WebP filename.
5. Add Product / Crawl:
   - verify Inventory is usable without a tall control wall;
   - verify all three workspace tabs;
   - verify gallery and details/table views;
   - verify thumbnail, title, description and image count;
   - verify scrolling still loads later bounded pages.
6. Profile/Pricing:
   - verify all three tabs;
   - verify every production row is fully visible/selectable;
   - verify Filament/color/fixed-price rows are fully usable without the previous clipped nested-scroll behavior.
7. Do not deploy Production from this acceptance. Any Host work remains blocked until explicit Local approval and a fresh read-only Host/migration/backup audit.

## Exact next task after Local acceptance

If owner Local QA passes, record the exact Local head and foreground evidence, then continue the remaining Catalog stabilization/42D visual refinement. If any behavior fails, patch only the failed contract with a focused regression; do not rewrite the healthy acquisition, AI, pricing or persistence cores.
