# Phase49.3I.47 — Qt Workspace, Multi-Image SEO, Bulk AI, Admin + Storefront Information Architecture

## 2026-09-17 responsive Image + dual Social provider continuation
Status: `LOCAL_TESTED / GITHUB_SOURCE_PUSHED / WINDOWS RUNTIME GATE NEXT`.

The owner rejected the remaining small fixed image-frame UX and locked the final Windows commerce/social flow. The Product image workspace now has larger responsive cards, 1-4 columns, aspect-preserving portrait/square/landscape previews and a large preview dialog while retaining Select/Primary/Slider/reorder/SEO/delete authority. Social publication is Site-first and supports both Instagram Direct and Buffer -> Instagram, with ordered Single/Carousel media, per-image Alt, SEO/social caption + hashtags, deterministic UTM Product links, provider Post/Media ID receipts and same-public-revision duplicate prevention. Secrets stay in Windows Credential Store.

Exact runtime source: `81d9fafbcc29be41b14af3129afc1ccf681529b1` on `agent/phase49-windows-instagram-buffer-image-20260917`. Rollback: `backup/pre-phase49-windows-instagram-buffer-image-20260917 -> 6a3a51aacdccff69a4999c4a470cb10807ceb648`. Evidence: 58/58 focused PASS; 99/99 Batch/Image/Social PASS; 112/112 combined 3I36/37/42C3/47/49 + Social/Image PASS; compile/diff/secret guards PASS. Production was not changed. Next gate is backup -> Receiver/FTP/Bridge -> exact pushed verify-only -> foreground launch -> real credentialed Site-to-Instagram acceptance.


## 2026-09-16 image-order continuation
Status: `LOCAL_TESTED / GITHUB PROMOTION NEXT`.

The remaining owner image-workspace gap is now implemented without replacing the mature image authority. Trusted selected cards have explicit previous/next controls. Primary remains fixed as slot 1; selected secondary images can be reordered. The Core persists ordered `selected_images_json`, keeps Alt and metadata aligned by source URL, preserves Slider identity, marks an uploaded Product dirty for same-identity republish, and the Qt action immediately invokes the existing finalizer/renumber path so physical SEO WebPs follow the new `-01/-02/-03...` order. Legacy display-only cards cannot reorder. The image-card/scroll height contract was increased so the added action row remains reachable.

Regression evidence: Phase49.3I.47 12/12 PASS; combined Image+Publish 27/27 PASS; broader 3I.36/37/42C3/47/49 87/87 PASS; touched compile and diff-check PASS. Rollback branch `backup/pre-phase49-3i47-image-reorder-20260916` points to exact pre-change `551f70624536857ab36ba004404298abb503d180`. No Catalog schema, Django migration, Host source or Production data change is part of this continuation.

Acceptance remainder: push exact tested source/docs -> fresh canonical Catalog backup -> live receiver/FTP/Bridge verification -> exact pushed `qt_launch.py --verify-only` -> foreground Windows launch + post-launch Catalog integrity/process evidence.

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

## Owner Local acceptance incident — ERR-49-088

The first owner attempt on final 3I.47 documentation head `946b8594f0ee001bd9833973e23eb47803c98bac` stopped before functional tests.

Evidence:
- repo/branch/remote guards passed;
- ff-only pull succeeded;
- the prior 3I.46 gate on the same machine had already passed with a checksum-verified Catalog SQLite backup;
- Windows PowerShell 5.1 raised `ParserError / TerminatorExpectedAtEndOfString` at the single Persian manual-QA `Write-Host` line in the runner.

This was not treated as a Product/Crawl/AI/database failure.

Resolution:
- owner runner restored to ASCII-only;
- exact Windows PowerShell 5.1 raw-byte + parser guard added to CI;
- existing PowerShell Core parser/stdin guard retained;
- runner version advanced to `49.3I.47.2`;
- exact tested source checkpoint: `36a710953276aae99fa668f477ad5569f8dc23ba`;
- `33511403943` Qt6 Full Parity Windows PASS;
- `33511403901` Single Active AI PASS;
- rollback: `backup/pre-err49-088-ps51-runner-ascii-20260901`.

The next owner attempt must pull the final docs head and confirm `Runner = 49.3I.47.2` before foreground QA.

## Professional commerce design standard

Owner-supplied File Library references were reviewed directly and the durable implementation standard is:
`docs/PROFESSIONAL_COMMERCE_DESIGN_ARCHITECTURE.md`.

3I.47 task tabs are treated as the first structural application of that standard. Subsequent 42D work should refine typography, spacing, hierarchy, accessible state and responsive behavior without rewriting healthy acquisition/AI/pricing/persistence cores.

The current Qt offscreen missing bundled-font-directory warning is non-blocking for ERR-49-088, but it is explicitly queued for the Persian typography/runtime packaging audit. Licensed font binaries remain outside Git.



## 2026-09-14 compatibility hotfix - ERR-49-144

Owner foreground QA against the modern Catalog exposed two regressions in the original 3I.47 presentation contract. First, `Sent / Published` incorrectly became empty for Products that were already uploaded but had new Local changes. Second, legacy Products with many historical source URLs could render dozens of broken cards even though a smaller set of real local files existed.

The compatibility repair restores the original 3I.47 intent without changing publish authority: uploaded Products stay in the Published lifecycle while `needs_update` continues to drive republish work; Product display count/cards use factual local files; exact modern SEO mappings remain preferred; legacy numbered files are UI-display compatible; unmapped display-only files cannot perform mutating image actions; the gallery is four compact columns. The strict publish resolver remains fail-closed and unchanged.

Canonical Catalog read-only evidence after the fix: Published=19; #33 source=60/display=16; #34=60/display=25; #63/#628/#634 each source=2/display=2. Dedicated 3I.47 suite 9/9 PASS and combined neighboring Qt/Crawl/Publish suite 77/77 PASS. Rollback: `backup/pre-err49-144-published-gallery-regression-20260914` -> `b85f946094ffeb0aea406ebaf6603273a7ef49ed`. Production was not touched.

## 2026-09-14 ERR-49-145 CI contract follow-up

Initial ERR-49-144 GitHub checkpoint `1a5ba6a...` passed Single Active AI, Modern Acquisition and Windows Portable workflows. Qt6 Crawl + AI Runtime failed only because an older 3I.42B parity test still asserted the previous three-large-column gallery. The runtime intentionally implements the owner-approved four compact columns. The stale test contract was updated without runtime changes; the exact failed foundation/parity suite is 23/23 PASS locally. A fresh GitHub run is required before final acceptance.