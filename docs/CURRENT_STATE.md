## 2026-09-02 — Phase49.3I.52C Crawl visual review + multi-select + safe Product recovery

Status: `GITHUB_UPDATED / WINDOWS QT CI PASS / SINGLE ACTIVE AI PASS / WINDOWS PORTABLE PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT TOUCHED`.

Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Runtime/CI checkpoint: `bb0dcd7cc521cacc540943ed8091a323038c28f9`  
Pre-phase rollback: `backup/pre-phase49-3i52c-crawl-review-recovery-20260902` → `dfc883cc6ac68c49c589c0d5a6007d50a9a4719c`.  
Catalog Center: `8.9.10` / build `2026.09.02.1`.

### What changed
- current Crawl Search results are now a visual icon/card gallery, scoped to the active Search/Listing URL;
- each new Search clears the previous live-result cards before starting;
- Preview-first discovery shows Product title/thumbnail before full receive;
- stable discovery Preview cache is reused by Qt and persistent Crawl inventory;
- cards visibly report `Preview: 1 عکس`, `N عکس دارد` or the explicit no-preview state;
- rich receive emits per-Product image progress such as `عکس 3/5` and `عکس 5/5`;
- selected collected Product has a dedicated live image strip showing actual local images, total image count and locally displayable file count;
- dense receive/bulk controls were shortened to task labels (`شروع دریافت`, `موجودی Crawl`, `لینک پیش‌فرض`, `دریافت Product`, `افزودن انتخابی`, `حذف انتخابی`) while full explanations remain in tooltips;
- current Search and persistent Crawl gallery/table use explicit Qt MultiSelection with select-all/clear and selected-count feedback;
- selected candidates can be bulk-added/rejected; successful selected transfer returns Product ids and navigates to Products;
- already-collected identities stay mapped to their existing Product;
- persistent Crawl inventory is enriched with candidate title/thumbnail/status evidence;
- Product image/source stage exposes `دریافت داده و عکس بیشتر از لینک محصول`;
- safe recovery refreshes source-owned/source-derived data and images while preserving operator Persian title/description, final price, final-price flag, sale approval and publish decision;
- Crawl bulk actions are task-grouped with shorter operator labels rather than a dense row of long actions.

### Verification
- `33625257602` — Phase49.3I.42C3 Qt6 Crawl + AI Runtime CI — PASS on final runtime `bb0dcd7...`;
- dedicated 3I.52C regression covers visual Preview, image count, Search clearing/scoping, Qt MultiSelection, per-image progress, Product routing and safe source recovery;
- `33625257485` — Single Active AI — PASS;
- initial Portable `33624135587` failed because the new Qt regression imported PySide6 while that job installed only non-Qt requirements; recorded as ERR-49-097 and not rerun unchanged;
- CI dependency boundary was fixed at `b43880a763d00bfda52dc29c4bf080cb428b1230`; final visual runtime is `bb0dcd7cc521cacc540943ed8091a323038c28f9`;
- `33625257693` — Windows Portable — PASS;
- Portable release regression gate: 217 tests PASS;
- artifact `3DPrintHub-CatalogCenter-v8.9.10`, artifact id `9844598171`;
- EXE SHA256 `e4064509a8d3a53ab3787b785f97f849e929c0873ed4ea021a99d46bc363af2b`;
- EXE self-verify and browser smoke PASS.

### Database / media / Production
- no new Django migration in 3I.52C;
- no destructive Catalog schema/data operation;
- Preview cache is additive below the persistent Catalog data root;
- canonical Local Catalog SQLite remains `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`;
- no Host source change;
- no Production MySQL write or migration;
- last verified Production application commit remains `c283864290f9c989a9fcdf24ee8eef519560e917`;
- existing 3I.51 Site migration candidates remain pending until a later verified Host audit; nothing in 3I.52C claims they are applied.

### Documentation updated
- active Phase49.3I.52 document;
- CURRENT_STATE;
- ROADMAP;
- CHANGELOG;
- REQUESTS as REQ-49-089;
- ERRORS as ERR-49-097;
- PATHS;
- master roadmap and PROJECT_CONTEXT.

### Exact next task
1. close Catalog Center;
2. on Windows verify `D:\projects\3DPrintHub`, origin, active branch and clean worktree;
3. ff-only pull the latest `agent/phase49-3i18-operator-bulk-ai-rebuild`;
4. run root `RUN_PHASE49_3I42C_LOCAL_GATE.ps1` version `49.3I.52.2` with the exact live GitHub head and `-LaunchApp`;
5. foreground QA one bounded MakerWorld Search: prior cards clear, Preview title/image appears, each Product shows 3/5→5/5 progress and final image count;
6. select multiple candidates, add them, verify automatic navigation to Products and visible Product identity;
7. verify persistent Crawl inventory remains visual/multi-selectable;
8. in Product image/source stage run `دریافت داده و عکس بیشتر از لینک محصول` and verify source images/data refresh while operator Persian content/final price/publish state remain unchanged;
9. only after owner Local acceptance may the normal Host read-only audit/backups begin; Production deploy remains blocked.

## 2026-09-02 — Phase49.3I.52 Site authoring + Shared Host AI + Bidirectional Product sync

Status: `GITHUB_UPDATED / WINDOWS QT CI PASS / SITE ADMIN-BRIDGE CI PASS / PORTABLE PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT TOUCHED`.

Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Exact tested source checkpoint: `6d19bed7659b9ca4cd54ff1ffd1323ec423bea6a`  
Site/Admin runtime checkpoint: `d6450ca2d9016bbdb75b37b7a31d20d8c2b6d111`  
3I.52B rollback: `backup/pre-phase49-3i52b-bidirectional-site-sync-20260902` → `48290db404739f07e322a700b6baa71d6b801871`.

Implemented:
- Django Admin is now a first-class fallback Product authoring surface when Catalog Center is unavailable, while reusing the canonical Product, ProductCatalogProfile and ProductVariant authority;
- manual Site Products receive the same canonical ProductCatalogProfile and existing pricing/Profile/Variant engine; no parallel commerce database was created;
- Host Product AI reuses the mature Structured/semantic-validated Catalog provider stack through root `ai/`, with Preview-before-Apply and an explicit content/SEO-only safety boundary;
- Host AI secrets are environment-only; Windows may keep using the mature OS Credential Store boundary;
- automatic Product-model policy rejects variable OpenRouter routers, probes exact Structured models for real Persian output, prefers verified free models and only then a bounded low-cost fallback;
- Bridge Product payload now includes source identity, category slug, pricing strategy, pricing inputs and technical summary, plus bounded offset pagination;
- Products page now has `↻ دریافت تغییرات سایت` and pulls newer Site revisions into Windows through the authenticated Bridge;
- clean Local Products accept a newer Site revision; Local Products with unpublished edits are never overwritten automatically and instead receive an explicit revision conflict;
- Site-only Products become non-publishable Local mirrors (`reference_only=1`) until linked to a real acquisition/source identity;
- republish now verifies the current Site Product revision before Batch packaging; mismatch or revision-check failure stops closed instead of overwriting newer Site Admin work;
- existing Batch 8.5 → FTP → Bridge → Store/public HTTP verification remains unchanged after the revision gate.

Verification:
- `33619876564` — final Phase49.3I.42C3 Qt6 full parity on `6d19bed...` — PASS, including dedicated 3I.52B Site→Windows pull, conflict protection and publish revision guard plus all mature acquisition/Filament/Profile/Stage/launcher regressions;
- `33619876411` — Windows Portable on `6d19bed...` — PASS;
- `33619876317` — Single Active AI on `6d19bed...` — PASS;
- `33619558467` — Product Admin/Bridge/migration CI on runtime-equivalent `d6450ca...` — PASS, including new 3I.52B Bridge serialization/pagination/pricing round-trip tests;
- `33619558562` — Phase50 Variant2/Profile Matrix on `d6450ca...` — PASS;
- delta `d6450ca... → 6d19bed...` is only the isolated Windows 3I.52B test fixture, so Site/Admin runtime source did not change after the passing Admin/Bridge gate.

Errors resolved:
- initial 3I.52B Qt test exposed missing `utc_now` import in the new Site→Local apply helper;
- the next run proved the runtime fix and isolated the remaining failure to tests invoking the real Bridge settings boundary without a CI token;
- the test fixture was corrected to provide an isolated Bridge settings object while the network Product list remained mocked;
- final Qt full parity then passed. Recorded as ERR-49-096.

Database / Production safety:
- 3I.52/3I.52B add no new Django migration and no destructive Catalog migration;
- existing 3I.51 additive migration candidates remain `website.0024` and `store.0042`;
- pricing fields used by this sync already belong to the existing Store migration chain, including `store.0033`;
- Production MySQL has NOT been changed;
- Host/Production source has NOT been changed;
- last verified Production application commit remains `c283864290f9c989a9fcdf24ee8eef519560e917`;
- last verified Production Store migration evidence remains only through `store.0035`; no later migration is assumed.

Local acceptance:
- canonical runner: `RUN_PHASE49_3I42C_LOCAL_GATE.ps1`;
- runner version: `49.3I.52.1`;
- Windows PowerShell 5.1 ASCII/parser guard remains mandatory;
- the gate checksum-backs up `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3` before foreground QA.

Exact next task:
1. close Catalog Center;
2. verify Local repo/origin/branch/clean worktree and live GitHub head;
3. ff-only pull the final documentation head;
4. run the canonical 3I.52 Local gate with the exact final GitHub head and `-LaunchApp`;
5. foreground-QA Site Product pull, newer-clean revision acceptance, dirty-Local conflict protection and Site-only non-publishable mirror behavior together with the existing 3I.51 Product/Crawl/Profile/Filament checks;
6. only after owner Local acceptance start the read-only Host/MySQL/migration/disk/backup audit;
7. create and verify fresh source/environment/MySQL backups before any deploy or migration;
8. Production deploy remains blocked until those gates pass.

## 2026-09-02 — Phase49.3I.51 Windows + Site finalization

Status: `GITHUB_UPDATED / WINDOWS CI PASS / SITE CI PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT TOUCHED`.

Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Approved source checkpoint: `8f01ea264dea2771cf1eb2f592be794d0dc95bbf`  
Exact Windows/Qt checkpoint: `25981269c2859ba107aad1feaa04b711b5761ae5`  
Rollback: `backup/pre-phase49-3i51-windows-site-finalization-20260902` → `191e8ef83f9a804805dda4cdd3df66b8224264d6`.

Implemented:
- Product image review is larger while multi-image selection/bulk operations remain intact;
- Product editor keeps the fixed source-page open action;
- pasted MakerWorld Search/Product URLs auto-select MakerWorld instead of inheriting a stale GrabCAD selection;
- Crawl exposes live Discovery/Receive progress and persistent review data;
- missing source production facts create one explicit `پیش‌فرض` Profile using owner defaults 100 g model + 50 g support + 60 min;
- fallback Profile includes all active PLA/PETG-family Filaments and excludes unrelated materials;
- Filament workspace is split into Filaments / Materials / Brands / Colors;
- Brand/Material/Color are managed registries; rename propagates to assigned Filaments and collision is rejected before mutation;
- optional Filament/Brand/Material descriptions and Material reference price/kg are preserved;
- Filament description survives Qt table normalization/edit;
- Qt exposes selected/full Filament Site Sync over the existing authenticated Bridge; FTP is not required for this Bridge-only operation;
- full Site reconciliation includes inactive Local Filaments so stale active Site offers can be deactivated;
- Site Django models/Admin persist FilamentBrand and optional descriptions; Material Admin keeps price/kg plus print/supervision rates visible;
- existing selling-price authority remains sale price per roll ÷ roll weight.

Verification:
- `33611776817` — Qt6 full parity on `25981269...` — PASS, including dedicated 3I.51 finalization regression and mature acquisition/Filament/Profile/Stage/launcher/source guards;
- `33611776806` — Windows Portable on `25981269...` — PASS; artifact `3DPrintHub-CatalogCenter-v8.9.10`, artifact id `9839347209`;
- `33611776891` — Single Active AI/no-migration safety on `25981269...` — PASS;
- `33611936196` — Product Admin/Bridge/migration CI on final source `8f01ea26...` — PASS, including `website.0024` and `store.0042` on isolated CI SQLite and the 3I.51 Admin/Bridge regressions;
- `33611936216` — Single Active AI/no-migration safety on final source `8f01ea26...` — PASS;
- compare `25981269... → 8f01ea26...` changes only `website/admin.py` and `store/test_phase49_3i51_filament_registry_admin.py`; Windows runtime source did not change after the passing Qt checkpoint.

Known implementation failures were resolved and are recorded as ERR-49-093..095. No failed command was repeated under the same known-bad condition.

Database/Production safety:
- Catalog SQLite change is additive only: `available_filament_offers.description`;
- registry metadata remains in existing Catalog settings;
- new Django migrations are additive candidates `website.0024_phase49_3i51_material_catalog_description` and `store.0042_phase49_3i51_filament_registry_descriptions`;
- Production MySQL has NOT been migrated;
- Host/Production source has NOT been changed;
- last verified Production application commit remains `c283864290f9c989a9fcdf24ee8eef519560e917`;
- last verified Production migration evidence remains only through `store.0035`; no later migration is assumed;
- secrets remain in the existing secure Local/environment boundary.

Local acceptance:
- canonical runner: `RUN_PHASE49_3I42C_LOCAL_GATE.ps1`;
- runner version: `49.3I.51.1`;
- runner remains ASCII-only for Windows PowerShell 5.1;
- it must checksum-back up `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3` before foreground QA.

Exact next task:
1. close Catalog Center;
2. verify Local repository/origin/branch/clean worktree and live GitHub head;
3. ff-only pull the final documentation head;
4. run the canonical 3I.51 Local gate with `-ExpectedHead <final-doc-head> -LaunchApp`;
5. foreground-QA Product images/source link, MakerWorld Search-Link Source detection/live results, default Profile, Filament registries, descriptions and selected/full Site Sync controls without intentionally publishing a Product;
6. only after owner Local acceptance start the read-only Host/MySQL/migration/disk/backup audit;
7. Production deploy/migrations remain blocked until that audit and fresh verified backups are complete.

## 2026-09-02 — Phase49.3I.49 guarded multi-product site publish + full Slider/Admin sync

Status: `GITHUB_UPDATED / WINDOWS CI PASS / ADMIN CI PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT TOUCHED`.

Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Exact Windows/Local-gate source checkpoint: `f9f89643de883ff549a9c0089235e43f061c5d4d`  
Admin/Bridge checkpoint: `16cf7cfaf6be3e8594435e3489cb0615624fcb00`  
Rollback: `backup/pre-phase49-3i49-site-bulk-publish-admin-control-20260901` → `1f8910b6c8c7c601cfd50689d8c48af492f7c453`.

Requested delta:
- Products supports explicit multi-select `آماده انتشار` and guarded multi-product site publish;
- only factually complete Products can enter the publish queue;
- publish reuses the mature `Batch 8.5 → FTP → Bridge Import → Store/public HTTP verification` path;
- only a strict successful ACK/public verification moves Local state to `workflow_status=uploaded`, clears `upload_ready`, and therefore moves the Product into `ارسال / منتشرشده`;
- failures remain visible as failures and are never presented as Published;
- the complete existing Slider presentation contract now round-trips Desktop ↔ Bridge ↔ ProductCatalogProfile ↔ HomepageHeroSlide;
- Django Admin exposes the same site-relevant Product/Profile/Slider controls in task order instead of creating a duplicate settings store.

Site-relevant Slider round-trip now covers:
`presentation_mode`, object fit, focal position, image scale, X/Y position, background mode/color/blur, Desktop/Mobile max width/height, Persian Slider title/description/Alt/button/focus keyword, transition effect/duration, display duration, sort order, active state and optimistic sync revision.

Admin information architecture follows the repository professional-commerce design rules derived from the owner design references: task-first grouping, progressive disclosure for diagnostics, one explicit publish action, and responsive/motion controls separated from content/SEO.

Verification:
- `33596830380` — exact-head `qt6-full-parity-windows` on `f9f896...` — PASS, including the dedicated `Qt6 3I.49 bulk site publish parity` regression, mature acquisition/Filament/Profile/Stage regressions, offscreen Qt launch, legacy launcher and final source guards;
- `33596830268` — exact-head Single Active AI / no-migration safety — PASS;
- `33596562467` — Product Admin Workspace CI on `16cf7c...` — PASS: compile, Django check, `makemigrations --check --dry-run`, CI migration apply and Admin regressions including 3I.49;
- compare `16cf7c... → f9f896...`: only `RUN_PHASE49_3I42C_LOCAL_GATE.ps1` changed, so no Admin/Bridge source changed after the successful Admin run.

Local gate:
- `RUN_PHASE49_3I42C_LOCAL_GATE.ps1` now includes 3I.46 paging, 3I.47 workspace/image/bulk-AI, 3I.48 owner/Filament/Slider and 3I.49 bulk-publish regressions;
- success marker: `PHASE49_3I49_LOCAL_GATE=PASS`;
- existing checksum-verified backup of `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3` remains mandatory before Local QA.

Safety:
- Django migration added = NO;
- Catalog destructive schema change = NO;
- Production MySQL changed = NO;
- Production source changed = NO;
- Host touched = NO;
- secret storage changed = NO;
- FTP password and Bridge token remain in the existing secure Local/environment boundary and are not copied into Django Admin;
- last verified Production application commit remains `c283864290f9c989a9fcdf24ee8eef519560e917`;
- last verified Production migration evidence remains only `store.0034` and `store.0035`.

Exact next task:
1. owner closes Catalog Center;
2. verify Local repo/origin/branch/clean worktree and live GitHub head;
3. ff-only pull the final documentation head;
4. run the canonical Local gate with `-LaunchApp`;
5. verify ready-state visibility and multi-select behavior on disposable Products;
6. do NOT click the real site-publish action until the owner intentionally chooses a disposable Product and the current Production receiver/deploy state has been verified;
7. after Local acceptance, start the normal read-only Host/migration/backup/deploy chain from the approved GitHub commit.

# CURRENT PROJECT STATE

## Continuation checkpoint — 2026-09-01 / ERR-49-088 PS5.1 Local gate repair + professional commerce design standard

Status: `SOURCE TESTED ON WINDOWS CI / OWNER LOCAL 3I.47 RERUN NEXT / PRODUCTION NOT TOUCHED`

Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Exact tested source checkpoint: `36a710953276aae99fa668f477ad5569f8dc23ba`  
Owner Local runner: `RUN_PHASE49_3I42C_LOCAL_GATE.ps1` version `49.3I.47.2`  
Rollback: `backup/pre-err49-088-ps51-runner-ascii-20260901`

Owner evidence:
- the earlier 3I.46 Local gate completed successfully and produced checksum-identical Catalog SQLite source/backup SHA256 `041CAE222B2784F8CC36B266341A33220B16194E16F29397440F001DBD89E988`;
- backup: `D:\projects\3dprinthub-backups\phase49-3i42c-20260901-145303\catalog-before-qt42c-qa.sqlite3`;
- the first 3I.47 attempt stopped before tests because Windows PowerShell 5.1 could not parse one newly introduced non-ASCII QA string;
- this was a runner encoding regression, not a Product/Crawl/AI/database failure.

ERR-49-088 resolution:
- runner is ASCII-only again;
- CI now raw-byte checks the runner and parses it under Windows PowerShell 5.1 before the existing `pwsh` parser/stdin gate;
- exact source checkpoint `36a710...`:
  - `33511403943` Qt6 Full Parity Windows — PASS;
  - `33511403901` Single Active AI — PASS;
  - 3I.47 Product lifecycle / local thumbnail / bulk AI / all-image SEO / Acquisition workspace / Profile-Pricing regressions PASS.

Professional commerce design sources:
- the uploaded `webdesign1.zip` binary itself was not exposed as a readable archive mount in this execution environment, so no ZIP-extraction claim is made;
- constituent owner File Library books were read directly, including Practical UI 2nd Edition, Lean UX, UI/UX Web Design Simply Explained, 100 Things Every Designer Needs to Know About People, Designing Brand Identity, 3D Web Development with Three.js and Next, and NextJS Cookbook;
- source-grounded rules are registered in `docs/PROFESSIONAL_COMMERCE_DESIGN_ARCHITECTURE.md`;
- this does NOT authorize a Next.js/React rewrite. Current Django architecture remains authoritative.

Design direction now canonical:
- information architecture and customer task flow before decoration;
- one reusable design system across Storefront/Admin/Catalog Center;
- disciplined Persian typography scale and readable dense-operator typography;
- progressive disclosure/tabs instead of control walls and nested scroll traps;
- restrained specialist/industrial trust presentation rather than decorative neon;
- Product pages prioritize identity, media, technical fit, price/quote state, production facts and one primary CTA;
- no color-only status communication;
- optional 3D is lazy/progressive and may never block LCP, core content or purchase controls;
- SEO metadata/structured data must match visible server-rendered content.

Non-blocking warnings observed in the older Local gate:
- Qt offscreen `QFontDatabase` reports no PySide6 bundled font directory; this is not the parser failure and is queued for the typography/packaging audit;
- `QSortFilterProxyModel.invalidateFilter()` deprecation is technical debt;
- Pillow `Image.getdata()` deprecation is known technical debt;
- pip upgrade notice is informational.

Database/Host/Production:
- Django migration changed = NO;
- Production MySQL changed = NO;
- Host/Production source changed = NO;
- Catalog destructive migration = NO;
- Production remains on last verified application commit `c283864290f9c989a9fcdf24ee8eef519560e917`;
- only `store.0034` and `store.0035` remain last verified applied Production migrations; later migration state is not assumed.

Exact next task:
1. owner closes Catalog Center;
2. verify correct Local repo/branch/clean worktree and live remote head;
3. ff-only pull the final documentation head;
4. run `RUN_PHASE49_3I42C_LOCAL_GATE.ps1 -ExpectedHead <final-doc-head> -LaunchApp`;
5. confirm output reports runner `49.3I.47.2`;
6. perform foreground 3I.47 QA on Product lifecycle tabs, old/local thumbnails, sequential multi-select AI, all-image SEO numbering/metadata, Acquisition gallery/details workspaces and Profile/Pricing tabs;
7. if QA passes, continue typography/font packaging + 42D visual/accessibility polish under `docs/PROFESSIONAL_COMMERCE_DESIGN_ARCHITECTURE.md`;
8. Production remains blocked until explicit owner Local acceptance.


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
4. Run repository-owned `RUN_PHASE49_3I42C_LOCAL_GATE.ps1 -ExpectedHead <final-head> -LaunchApp`; the runner is version `49.3I.47.2` and creates a checksum-verified Catalog SQLite backup before QA.
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
