## 2026-09-02 — Phase49.3I.52G adaptive Product recovery

Status: `IMPLEMENTED + WINDOWS QT/PARITY PASS + PORTABLE PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT DEPLOYED`.

Completed:
- discovery success is separate from full Product data/image success;
- redacted per-method acquisition tracing + Qt log-folder access;
- factual Product quality gates for meaningful title/data and real local image evidence;
- ordered failover across distinct mature receive methods;
- successful method becomes preferred for following Products;
- all-method exhaustion or invalid Product identity stops the batch and leaves later rows untouched;
- partial-success batches with a later circuit break are reported failed;
- permanent Crawl bulk recovery opts into adaptive failover while preserving mature safe merge behavior.

Evidence: runtime `bf1fafdb38233a23e13a5715ffac72f772412005`; Qt `33644903042` PASS; dedicated suite 27 PASS; Single Active AI `33644902970` PASS; Portable `33644902962` PASS; 235 portable regressions; artifact `9852476786`; SHA256 `f3e0bce9e5d3b40317b5fd37cff8a5fc6ff1d5a2cef6f5b1bf84dc6f6699c310`.

Next: owner Local 2–5 Product real-source QA and log inspection if a live failure remains. Production stays blocked.

## 2026-09-02 — Phase49.3I.52F bulk incomplete Product recovery

Status: `IMPLEMENTED + WINDOWS QT/PARITY PASS + PORTABLE PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT DEPLOYED`.

Completed:
- restored the mature previous-version bulk refetch intent inside Qt permanent Crawl inventory;
- `انتخاب ناقص‌ها` selects loaded rows missing Product/data/image evidence;
- image target selector supports 5/10/20;
- `بازیابی دیتا + عکس` reuses complete local evidence first and force-refetches only incomplete Products;
- safe refetch preserves operator Persian content, pricing, approval and publish decisions;
- orphan collected-ledger identities can be explicitly rebuilt from their Product URL;
- URL slug gives a readable temporary Product identity before full receive;
- queue actions are split across two rows and `بازگردانی به صف` is distinct from data recovery.

Evidence: runtime `cf73f841418aac2eec1b78e0dbd682ceb2d3fef5`; Qt `33637452385` PASS; Single Active AI `33637452588` PASS; Portable `33637452243` PASS; 227 release regressions; artifact `9849484898`; SHA256 `f0150359fd36c7ead84599ccd0b799797ed48e85e4c6eac1d191abc3f0315a64`.

Next: owner Local sync/gate, then select incomplete permanent Crawl rows and recover 5/10 images in one batch. Production remains blocked.

## 2026-09-02 — Phase49.3I.52E Crawl preview + historical refetch image parity

Status: `IMPLEMENTED + WINDOWS QT/PARITY PASS + PORTABLE PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT DEPLOYED`.

Completed:
- include mature `<id>_refresh_latest`, `<id>_refetch_*`, and `<id>_bulk_refetch_*` image folders in read-only Crawl image resolution;
- preserve exact Product/local_dir authority and do not move media;
- recover MakerWorld lazy listing thumbnails from srcset, picture source, data-src/data-original/data-lazy-src and CSS background-image;
- allow same Search rerun to backfill candidate Preview without duplicating Crawl identity;
- keep local image counts factual: only real local files produce `N عکس دارد`;
- expose `Phase49.3I.52E` in Qt shell.

Evidence: runtime `016e84ab98d2e5577633833cbc87cb96824dbbf0`; Qt `33632062812` PASS; Single Active AI `33632062877` PASS; Portable `33632062880` PASS; 223 portable regressions; artifact `9847317893`; SHA256 `f9bcfc0770a38b0c8eabc9f2deab7c05b2c4d8b577fd25eb540ea9b65f7dc970`.

Next: owner Local sync/gate, then permanent inventory + same-search Preview backfill foreground QA. Production remains blocked.

## 2026-09-02 — Phase49.3I.52D legacy image-path parity + numeric control repair

Status: `IMPLEMENTED + WINDOWS QT/PARITY PASS + PORTABLE PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT DEPLOYED`.

Completed:
- verified the mature Catalog download layout from the retained Tk runtime instead of inventing a new path;
- canonical downloaded images remain under `D:\projects\3dprinthub-catalog-manager\collected\<source>\<external_id>\images`;
- Qt Crawl inventory now reads that mature folder directly even when an old Crawl row is not yet linked to a Product id;
- finalized `seo_images` are preferred before original `images`;
- legacy source-code casing differences no longer hide matching Product rows;
- actual local image count is shown as `N عکس دارد` for unlinked candidates too;
- live single-candidate review exposes real downloaded files from the mature collected tree;
- old retained `D:\projects\3dprinthub_catalog_center\collected` is a read-only secondary compatibility fallback only;
- Product/price/SEO/publish state is not mutated by this image lookup;
- Crawl `requested` and per-Product image-count spinboxes are LTR, centered, width-bounded and padded to prevent Windows RTL arrow/text overlap;
- control grid spacing is explicit.

Evidence:
- exact runtime `a18b6f3036d41271cf3e8c1d9a0dfd8c271a53ce`;
- Qt `33628825851` PASS;
- dedicated 3I.52C/52D 13-test suite PASS;
- Single Active AI `33628825772` PASS;
- Windows Portable `33628825715` PASS with 221 release regressions;
- artifact `9846044486`;
- EXE SHA256 `c08aa1e9d12926203cb59c580aab6c606c2b0e259ad83df37aa3b3abec86c22a`;
- rollback `backup/pre-phase49-3i52d-legacy-image-path-layout-20260902` → `28b51d2f95b272d3bf6311fb02f55a7a4fa808e4`.

Immediate next:
1. owner Local clean ff-only sync;
2. canonical Local gate + foreground Qt launch;
3. verify the exact owner screenshot area now displays mature downloaded images/counts;
4. verify the 100/5 spinboxes are visually separated from arrow controls;
5. if any one external id still misses, inspect that exact DB/local_dir/collected identity read-only before any further change;
6. Production stays blocked.

## 2026-09-02 — Phase49.3I.52C Crawl visual review + bulk transfer recovery

Status: `IMPLEMENTED + WINDOWS QT/PARITY PASS + PORTABLE PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT DEPLOYED`.

Completed:
- Preview-first Product cards in the current Crawl Search workspace;
- stable candidate thumbnail reuse and visible image-count state;
- per-Product image progress during full receive;
- selected collected Product local image review strip with real local files and explicit counts;
- compact receive/bulk action labels with full tooltips;
- Qt shell phase identity updated from stale 3I.48 to current 3I.52C;
- new Search clears prior live Search cards;
- explicit multi-select/select-all/clear/bulk add/reject in current Search and persistent Crawl inventory;
- successful bulk transfer navigates to Products and preserves existing collected identity;
- safe Product source-data/more-images recovery that preserves operator/business-owned fields;
- shorter task-oriented Crawl bulk actions and explicit selected-count feedback;
- dedicated 3I.52C regressions;
- Portable CI dependency correction after ERR-49-097.

Evidence:
- final runtime/CI checkpoint `f43c7aa464948832ba349543f94c94498490ab25`;
- Qt `33625988684` PASS;
- Single Active AI `33625988674` PASS;
- Windows Portable `33625988663` PASS, 218 release regressions;
- artifact id `9844889166`, EXE SHA256 `cd54431bd29bad76990c17eb818671e3f32c4d53a244cdc07132f5d93a532f4b`;
- pre-phase rollback `backup/pre-phase49-3i52c-crawl-review-recovery-20260902` → `dfc883cc6ac68c49c589c0d5a6007d50a9a4719c`.

Immediate next:
1. owner clean ff-only Local pull;
2. canonical `RUN_PHASE49_3I42C_LOCAL_GATE.ps1` / runner `49.3I.52.2` with exact final GitHub head and `-LaunchApp`;
3. foreground QA with one bounded MakerWorld Search: Preview image/title, 3/5→5/5 progress, image-count labels, multi-select transfer and Products navigation;
4. verify persistent Crawl inventory thumbnails/multi-select;
5. verify Product `دریافت داده و عکس بیشتر از لینک محصول` without operator price/content/publish clobber;
6. only after owner acceptance start the normal Host read-only audit/backups. Production remains blocked.

## 2026-09-02 — Phase49.3I.52 Site fallback authoring + Shared AI + bidirectional Product sync

Status: `IMPLEMENTED + WINDOWS QT CI PASS + SITE/ADMIN CI PASS + PORTABLE PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT DEPLOYED`.

Completed:
- canonical Site Product authoring when Windows Catalog Center is unavailable;
- same Product/Profile/Variant pricing authority on Site and Desktop;
- root `ai/` shared policy/playbook with environment-only Host secrets, exact-model Product safety, Persian Structured probe, verified-free-first and bounded low-cost fallback;
- Site AI Preview → explicit Apply, limited to Product content/SEO;
- Bridge source identity + category + pricing/Profile payload parity and bounded Product pagination;
- explicit Windows `دریافت تغییرات سایت` Product pull;
- Site-only non-publishable Local mirrors;
- dirty-Local/newer-Site conflict protection;
- pre-publish Site revision verification that fails closed on mismatch or Bridge verification failure;
- mature Batch/FTP/Bridge/public verification path retained after the guard;
- owner Local gate upgraded to `49.3I.52.1`.

Evidence:
- tested source `6d19bed7659b9ca4cd54ff1ffd1323ec423bea6a`;
- Qt full parity `33619876564` PASS;
- Windows Portable `33619876411` PASS;
- Single Active AI `33619876317` PASS;
- Product Admin/Bridge/migration `33619558467` PASS on runtime-equivalent `d6450ca2...`;
- Variant/Profile Matrix `33619558562` PASS;
- rollback `backup/pre-phase49-3i52b-bidirectional-site-sync-20260902` → `48290db4...`.

Immediate next:
1. owner Local 3I.52 checksum-backed gate + foreground QA;
2. if PASS, read-only Host audit of actual root/HEAD/worktree/Python/Django/MySQL/migrations/disk/backup tools;
3. fresh source + environment + MySQL backups with non-empty/checksum verification;
4. deploy only the owner-approved GitHub commit;
5. apply only the migration plan proven by the live Host audit;
6. Production verify Admin, Bridge, Product page, pricing/Profile and AI environment boundary.

Production remains blocked until Local acceptance and Host audit.

## 2026-09-02 — Phase49.3I.51 Windows + Site finalization

Status: `IMPLEMENTED + WINDOWS CI PASS + SITE CI PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT DEPLOYED`.

Completed:
- final Product image/source-link/Crawl Source-detection/live-result parity;
- explicit source-missing default Profile with owner fallback production facts;
- PLA/PETG-family fallback Filament matching;
- four-part Filament registry workspace with managed Material/Brand/Color identities;
- optional descriptions and Material reference price/kg;
- registry rename propagation/collision protection;
- selected and full Site Filament reconciliation over the mature authenticated Bridge, including inactive offers;
- persistent Site FilamentBrand + Material/Filament descriptions;
- task-focused Django Admin parity while preserving Material production rates;
- additive Django migration candidates `website.0024` and `store.0042`;
- canonical owner gate upgraded to `49.3I.51.1`.

Evidence:
- Windows Qt `33611776817` PASS;
- Windows Portable `33611776806` PASS;
- Single Active AI `33611776891` PASS;
- final Site/Admin/Bridge `33611936196` PASS on `8f01ea264dea2771cf1eb2f592be794d0dc95bbf`;
- final Single Active AI `33611936216` PASS;
- rollback branch verified identical to pre-phase `191e8ef83f9a804805dda4cdd3df66b8224264d6`.

Immediate next:
1. owner Local 3I.51 gate + foreground QA;
2. if PASS, read-only Host audit of root/HEAD/worktree/Python/Django/MySQL/migration state/disk/backup tools;
3. fresh source + environment + MySQL backup with checksum/non-empty verification;
4. deploy only the owner-approved GitHub commit;
5. apply only the verified migration chain;
6. Production runtime/Admin/Bridge/Product verification;
7. then continue visual/accessibility/typography polish and remaining stability work.

Production remains blocked until Local acceptance and Host audit.

## 2026-09-02 — Phase49.3I.49 site publish + Slider/Admin parity

Status: `IMPLEMENTED + WINDOWS CI PASS + ADMIN CI PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT DEPLOYED`.

Completed:
- explicit Product multi-select ready-for-publish gate;
- selected-ready-only bulk publish;
- mature Batch8.5/FTP/Bridge/public-HTTP verification retained;
- successful publish automatically enters the existing Published lifecycle workspace;
- failed/skipped Products remain outside Published with diagnostics;
- full existing Slider composition/SEO/motion/timing fields round-trip Desktop ↔ Site;
- HomepageHeroSlide and ProductCatalogProfile Admin organized by operator task, with sync diagnostics collapsed;
- Local gate expanded through 3I.49.

Evidence:
- exact final Windows Qt CI `33596830380` PASS on `f9f89643de883ff549a9c0089235e43f061c5d4d`;
- exact final Single Active AI/no-migration CI `33596830268` PASS;
- Admin/Bridge CI `33596562467` PASS on `16cf7cfaf6be3e8594435e3489cb0615624fcb00`;
- the only later delta from `16cf7c...` to `f9f896...` is the repository-owned Local gate.

Owner acceptance next:
1. clean ff-only pull on `D:\projects\3DPrintHub`;
2. checksum-backed Local gate + foreground launch;
3. verify multi-select Ready state, blocked-Gate explanation and Published workspace transition;
4. verify Slider controls are present in Qt and, after a later approved site deploy, in Django Admin;
5. no Production publish/deploy until explicit owner acceptance and the normal Host audit/backup sequence.

No new Django migration or secret-store contract is introduced by 3I.49.

# ROADMAP

## 2026-09-01 — Phase49.3I.47 owner rerun + professional commerce design-system track

Status: `PS5.1 GATE FIXED + EXACT WINDOWS CI PASS / OWNER LOCAL RERUN NEXT / PRODUCTION NOT DEPLOYED`.

Immediate accepted source checkpoint:
- `36a710953276aae99fa668f477ad5569f8dc23ba`;
- runner `49.3I.47.2`;
- `33511403943` Qt6 Full Parity Windows PASS;
- `33511403901` Single Active AI PASS;
- explicit Windows PowerShell 5.1 ASCII/parser guard PASS.

Owner acceptance still required:
- lifecycle Product tabs and local thumbnail fallback;
- sequential multi-select full-content AI;
- every image final SEO metadata + numbered WebP identity;
- Acquisition workspaces with gallery/details views;
- Profile/Pricing full-height tabs.

Professional commerce architecture is now registered in:
`docs/PROFESSIONAL_COMMERCE_DESIGN_ARCHITECTURE.md`.

Source-guided next design slices after owner acceptance:
1. Persian typography/font-runtime and packaging audit; solve the Qt/system-font experience without committing licensed font binaries;
2. shared visual tokens/components and accessibility states for Catalog Center;
3. Admin design-system consolidation;
4. Storefront IA for discovery → technical fit → price/quote → trust → variant/custom order → CTA;
5. Product-detail technical/trust hierarchy and responsive intermediate-width QA;
6. performance-safe optional 3D preview only where it materially improves product evaluation;
7. SEO/accessibility/performance regression gates;
8. remaining Catalog stability work: worker/read connection discipline, serialized/batched writes, bulk discovery persistence, slow-query/health auditing and resume/soak testing.

Guardrails:
- Django remains authoritative; book examples do not imply framework migration;
- no visual phase may change pricing/business authority implicitly;
- critical SEO/Product text remains server-rendered/crawlable;
- no Production deployment before owner Local approval and the normal Host read-only audit/backup/deploy chain.


Updated: 2026-09-01

## Current Windows/Desktop track — Phase49.3I.47

Status: `IMPLEMENTED + WINDOWS CI PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT DEPLOYED`.

Current code checkpoint: `9984e3bb9ab5ff293ad275ecbe86dba3a96db4b1`.
Canonical phase: `docs/phases/PHASE49_3I47_QT_WORKSPACE_IMAGE_BULK_AI_SITE_IA.md`.
Rollback: `backup/pre-phase49-3i47-owner-workspace-20260901` → `ecfd9260c168140757781bb672eb57c77bcc4ee3`.

### Completed in 49.3I.46
- Product Gallery bounded SQL paging: initial 50 + incremental fetch.
- Product Table/Detail bounded SQL paging: initial 20 + incremental fetch.
- Crawl inventory bounded paging: initial 100 + incremental fetch.
- lightweight Product list projection, SQL-backed search/sort/filter and planner indexes.
- mature pre-Qt acquisition methods restored through headless Core/runtime.

### Completed in 49.3I.47
- Products reorganized into active, sent/published, archived and rejected/deleted lifecycle workspaces.
- legacy/local Product thumbnail fallback for old records without modern URL mapping.
- Product cards expose description excerpt + image count.
- sequential multi-select `AI تکمیل همه موارد` through one shared AICore and shared single-Product finalization path.
- every selected Product image receives consistent SEO metadata and unique numbered WebP filenames (`-01`, `-02`, `-03`, ...).
- Add Product/Crawl split into focused inventory/receive/history workspaces.
- Crawl inventory gains Windows-like gallery/image and details/table views with Product preview facts.
- Profile/Pricing split into three full-height task tabs with production/filament rows no longer clipped by nested scrolling.
- Django Admin adopts shared accessible task tabs for Product sales/source/SEO, pricing, material/color rates, site settings and quotes.
- Storefront Product information adopts progressive accessible tabs while preserving existing Variant/Profile/pricing authority.

### Verification
Qt/Desktop on `9984e3bb9ab5ff293ad275ecbe86dba3a96db4b1`:
- `33506242569` — `qt6-full-parity-windows` — PASS.
- `33506242669` — `phase49-3i17` — PASS.

Admin on `ef215ba09044cd421302f9057bf3c1565b99ef1e`:
- `33505851712` — `product-admin-workspace` — PASS.
- `33505851749` — `phase49-3i17` — PASS.

Storefront on `f4beec484f060063d00de4a5753a135a020cfea1`:
- `33506122579` — `phase50-variant2-gallery` — PASS.
- `33506122534` — `phase49-3i17` — PASS.

## Immediate acceptance gate
1. Owner clean ff-only pull on `D:\projects\3DPrintHub` to the final docs HEAD.
2. Run repository-owned `RUN_PHASE49_3I42C_LOCAL_GATE.ps1 -ExpectedHead <final-head> -LaunchApp`; runner version is `49.3I.47.1` and backs up/checksums the real Catalog SQLite before QA.
3. Verify four Product lifecycle tabs, old thumbnails, card description/image count and sequential Bulk AI on disposable Products.
4. Verify one disposable Product with at least three images produces consistent SEO metadata and distinct numbered SEO files for every image.
5. Verify Add Product/Crawl three workspaces plus Gallery/Details inventory views and bounded scroll continuation.
6. Verify Profile/Pricing three full-height tabs and all production/filament rows.
7. Record owner Local foreground evidence.
8. Do not deploy Production from this gate.

## Next engineering slice after owner acceptance
- remaining Catalog stability work: worker/read connection discipline, serialized/batched writes, bulk discovery persistence, query auditor/slow-query health and resume/soak testing;
- Phase42D visual/accessibility polish based on real owner QA;
- owner File Library constituent design books have now been reviewed directly; apply grounded refinements through `docs/PROFESSIONAL_COMMERCE_DESIGN_ARCHITECTURE.md`;
- only later evaluate 42E default-launcher/package cutover.

## Web / Admin track
Current Admin/Storefront information architecture is implemented and CI-tested but not Production-deployed. Any later Host work must start with read-only verification of root/branch/HEAD/worktree/live SHA/Python/Django/MySQL/migration state, followed by exact migration plan, fresh backups/checksums and deploy only from the owner-approved GitHub commit.

Last verified Production application commit remains `c283864290f9c989a9fcdf24ee8eef519560e917`.
Last verified Production migration evidence remains only `store.0034` and `store.0035`; no later migration is assumed applied.

Historical roadmap checkpoints remain available in Git history and dedicated `docs/phases/` documents.
