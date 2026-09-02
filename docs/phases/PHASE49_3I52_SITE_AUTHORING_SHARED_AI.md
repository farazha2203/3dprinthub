## 3I.53B — Host baseline correction before Production receiver audit

Date: 2026-09-02  
Status: `GITHUB_UPDATED / AUDIT RUNNER CI PASS / HOST READ-ONLY FORENSICS PARTIAL / PRODUCTION NOT CHANGED`.

Read-only owner evidence corrected two stale assumptions:
- Host HEAD is actually `198fa8e41ea4f4d87eb287ba69c91076acc78d62`, 23 commits ahead of the previous documented `c283864...` baseline and on the same GitHub ancestry chain;
- system `python3` is unavailable; the documented Production venv Python is authoritative.

The audit runner now accepts the verified current Host baseline explicitly instead of hardcoding an old SHA. It remains fail-closed on dirty worktree and live-target mismatch and performs no merge/migrate/collectstatic/restart.

Current untracked blocker: `ls-output.txt`, old ASCII output/evidence file, SHA256 `8e01c07fcdf242fdc9be7de5a3a9b86cd7f0244e37ace629bc22d10ac1bee738`. It must be inspected without printing contents, then preserved outside the repo if safe.

Verification: `d0984e1f9e01d959c028d2714c4814b6556acd84`; Product Admin/audit CI `33656829478` PASS; Single Active AI `33656829551` PASS.

Next: venv-Python secret-marker scan → reversible evidence move with hash verification → updated read-only audit → review actual MySQL/migration/storage state before any backup/deploy/migration.

## 3I.53 — Site Product receiver readiness + Production read-only audit

Date: 2026-09-02  
Status: `GITHUB_UPDATED / SITE CI PASS / WINDOWS QT PASS / PORTABLE PASS / HOST READ-ONLY AUDIT NEXT / PRODUCTION NOT TOUCHED`.

The owner moved the immediate priority from Windows Crawl repair to getting the Site/Host ready for real Catalog Center Product publishing.

### Receiver contract
New authenticated endpoint:
`/api/catalog-bridge/v1/publish-readiness/`.

It reports:
- Bridge token configured state without exposing the token;
- exact required migration rows for Store 0036..0042 and Website 0024;
- required receiver table/column evidence;
- pending-import and public-media storage accessibility;
- active Material and PrintQuality prerequisites required by the mature importer;
- explicit blockers and `ready=true/false`.

Desktop `publish_many()` asks this endpoint before FTP. If the receiver is blocked or unavailable, no batch upload starts.

### Mature path preserved
After readiness PASS the existing path remains:
Ready Product → Batch 8.5 packaging → FTP → authenticated Bridge import → canonical Product/Profile/Variant reconciliation → Store visibility → public Product/image HTTP verification → strict ACK → Local Published state.

No duplicate Product database, alternate importer or hidden publishing bypass was added.

### Production audit
Repository runner:
`scripts/host/phase49_3i53_production_readonly_audit.sh`.

The audit is intentionally read-only with respect to Source/DB/runtime. It verifies real Host repository/HEAD/worktree, live GitHub target, Python/Django, effective MySQL vendor/name, Django check/migration drift/plan, migration recorder, storage paths, token configured state, Product-import prerequisites, relevant schema, disk/inodes and mysqldump availability. It performs no merge/migrate/collectstatic/restart.

### Database
3I.53 itself adds no migration. Production still requires audit of the previously existing chain:
`store.0036 → 0037 → 0038 → 0039 → 0040 → 0041`, `website.0024`, then `store.0042`.

0037, 0041 and 0042 contain bounded data migrations in addition to additive schema work; fresh verified MySQL backup is mandatory before applying them.

### Verification
- Site/Product Admin `33652584032` PASS;
- Variant/Profile `33652583964` PASS;
- Host-audit contract `33652996666` PASS;
- final Qt `33653229142` PASS;
- final Single Active AI `33653229219` PASS;
- final Portable `33653229400` PASS, 235 regressions;
- artifact `9855771656`;
- EXE SHA256 `a6bebd3c10a56aac1c65a58d5ffb1029382e98c7b0782a4b034a315e60c2f1ed`;
- final code checkpoint `62ce5c3393a888cc1a027e4ca6bbb88f189bc845`.

ERR-49-104 records the one intermediate Windows compatibility/test failure and its correction. Production remains untouched.

### Next
Run the exact read-only Host audit from the GitHub target without changing working source. Review actual migration/schema/storage/backup evidence. Only then prepare a fresh rollback set and controlled Production deployment.

## 3I.52G — Adaptive Product acquisition failover + observable Crawl recovery

Date: 2026-09-02  
Status: `GITHUB_UPDATED / QT CI PASS / SINGLE ACTIVE AI PASS / WINDOWS PORTABLE PASS / OWNER LOCAL REAL-SOURCE QA NEXT / PRODUCTION NOT TOUCHED`.

Owner foreground symptom: MakerWorld Crawl discovery succeeded but full Product recovery could fail across the visible batch with no images.

Implemented:
- redacted acquisition JSONL under persistent Catalog data;
- Qt History/Report recent method diagnostics + log-folder action;
- explicit separation of discovery/Preview success from Product fetch success;
- meaningful-title, usable-data and real-local-image quality gates;
- ordered failover across rich, network capture, classic exact, public HTTP and attached Chrome;
- mature resilient image fallback reused when appropriate;
- successful method promoted for following Products;
- all-method exhaustion or invalid Product identity trips a circuit breaker and leaves later selected rows untouched;
- permanent Crawl bulk recovery opts into adaptive recovery while mature operator-field protections remain.

Rollback: `backup/pre-phase49-3i52g-adaptive-acquisition-observability-20260902` → `aa5ae5c9ff859b6fcd7630ef11b29254b7e2bcf3`.

Verification: runtime `bf1fafdb38233a23e13a5715ffac72f772412005`; Qt `33644903042` PASS; dedicated suite 27 PASS; Single Active AI `33644902970` PASS; Portable `33644902962` PASS; 235 portable regressions; artifact `9852476786`; EXE SHA256 `f3e0bce9e5d3b40317b5fd37cff8a5fc6ff1d5a2cef6f5b1bf84dc6f6699c310`.

No Django/Catalog migration, destructive media operation, Host change, Production deploy or Production MySQL write.

Owner Local next: clean ff-only sync, checksum-backed Local gate, launch Qt, verify `Phase49.3I.52G`, recover only 2–5 previously failed MakerWorld rows, then inspect `logs\acquisition` if any live failure remains.

# Phase49.3I.52 — Site Authoring Parity + Shared Host AI

Date: 2026-09-02

Status: `GITHUB_UPDATED / WINDOWS QT CI PASS / SITE ADMIN-BRIDGE CI PASS / PORTABLE PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT TOUCHED`

Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Pre-phase rollback: `backup/pre-phase49-3i52-site-authoring-ai-parity-20260902` → `75d0960cabe1673f586103bae2e3216f71947012`.

## Requested delta
- Site must remain fully usable if the Windows application is unavailable.
- Admin must be able to add/edit Product, Product Profile, price strategy and Variants on the canonical Site database.
- Windows publish continues to map into the same Product/Profile/Variant tables; no duplicate commerce database.
- Site Product pages must continue consuming the same canonical pricing/profile/Filament facts.
- Host must get the same Structured + semantic-validated Persian Product AI method used by Catalog Center.
- Auto AI policy prefers a verified exact free Persian Structured model, then a verified low-cost model under an explicit budget.
- AI knowledge/policy must live in a root `ai/` folder so the method can be reused project-by-project.

## Must not touch
- no direct Production source edit;
- no Production migration/deploy before Local acceptance and Host read-only audit;
- no Secret in database/Git/logs;
- no hidden Provider switch after runtime selection;
- no variable OpenRouter router as final Product model;
- no AI changes to price, stock, material/color, license, factual dimensions/weight or publish state;
- no second Product/Profile/Variant database.

## Data ownership
Product content/SEO:
- Site Admin or Windows may edit through revision-aware canonical Product/Profile records.

Commerce facts:
- Product fixed price, ProductCatalogProfile pricing strategy/range, ProductVariant price engine, Material/Filament rates and inventory remain operator/business-engine owned.

AI:
- preview-first;
- apply only after explicit operator confirmation;
- content/SEO only.

## Test contract
- manual Site Product receives a canonical ProductCatalogProfile after save;
- fixed Product price mirrors into its canonical profile;
- Product Admin exposes profile edit surface and AI preview;
- AI proposal cannot mutate price/stock/license/publish state;
- Auto model policy rejects variable routers and non-Structured free models;
- Auto model policy selects an exact free model only after Persian Structured probe;
- no live AI key/network is required by CI.


## Implemented Site-authoring boundary
- Product Admin can create/edit Products when Windows Catalog Center is unavailable.
- The same canonical Product, ProductCatalogProfile, ProductVariant, Material/Filament and pricing engines remain authoritative.
- Manual Site Product save ensures one canonical ProductCatalogProfile; no second commerce database exists.
- Site Product page continues to read those same canonical Product/Profile/Variant facts.

## Shared Host AI
Root `ai/` contains the reusable policy/playbook and the 3DPrintHub Product adapter.
- Host secrets are environment-only.
- Windows may use the mature OS Credential Store.
- exact model override is honored only for a deterministic model id;
- variable OpenRouter routers are rejected for Product work;
- Auto selection evaluates text/Structured candidates, runs a Persian Structured probe, prefers verified free, then a bounded low-cost candidate;
- AI is Preview → explicit Apply;
- AI may update content/SEO only and cannot mutate operator-owned pricing, stock, material/color, license, production facts or publish state;
- existing operator technical facts win over an AI key collision.

## 3I.52B — Bidirectional Product sync
Rollback: `backup/pre-phase49-3i52b-bidirectional-site-sync-20260902` → `48290db404739f07e322a700b6baa71d6b801871`.

Bridge:
- Product serialization includes source name/code/url, category slug, pricing strategy, pricing inputs and technical summary;
- Product listing supports bounded `limit + offset` pagination;
- Product update accepts the matching Pricing/Profile fields under the existing optimistic revision contract.

Windows:
- Products exposes `↻ دریافت تغییرات سایت`;
- Site Products match Local by Desktop id, then server id, then source identity;
- a clean Local mirror accepts a newer Site revision;
- dirty/unpublished Local state plus a newer Site revision produces an explicit conflict and no overwrite;
- a Site-only Product becomes a Local `reference_only=1` mirror and cannot enter the mature publish queue until it has a real acquisition/source identity;
- accepted Site facts update Local content, SEO, pricing/Profile, availability/stock/lead time, technical summary/features/keywords and Slider mirror fields without rewriting raw acquisition identity/media ownership.

Publish:
- existing Products with `server_product_id` must pass a live Site revision check before Batch packaging;
- revision mismatch or failure to verify revision fails closed;
- first publish without a server Product id still follows the mature path;
- after the guard, Batch 8.5 → FTP → Bridge → Store/public HTTP verification is unchanged.

## 3I.52B verification
Exact tested source checkpoint: `6d19bed7659b9ca4cd54ff1ffd1323ec423bea6a`.

- `33619876564` — Qt6 full parity — PASS;
- `33619876411` — Windows Portable — PASS;
- `33619876317` — Single Active AI — PASS;
- `33619558467` — Product Admin/Bridge/migration — PASS on runtime-equivalent `d6450ca2...`;
- `33619558562` — Variant/Profile Matrix — PASS.

The only delta from `d6450ca2...` to `6d19bed...` is the isolated Windows test fixture.

## Known implementation error and correction
ERR-49-096:
- first new Qt test exposed a missing `utc_now` import;
- after that runtime correction, the remaining tests failed because the isolated orchestration fixture crossed the real Bridge settings/token validation boundary;
- the fixture now provides an isolated Bridge settings object while network Product results remain mocked;
- the production Bridge credential guard was not weakened;
- final full Qt parity passed.

## Database / Production safety
- new Django migration in 3I.52/3I.52B: NO;
- destructive Catalog migration: NO;
- Production MySQL write: NO;
- Host/Production source change: NO;
- Secret persistence change: NO;
- last verified Production app commit remains `c283864290f9c989a9fcdf24ee8eef519560e917`;
- last verified Production Store migration evidence remains only through `store.0035`;
- 3I.51 additive migration candidates remain pending and must be audited on Host before any deployment.

## Owner Local acceptance next
Canonical runner: `RUN_PHASE49_3I42C_LOCAL_GATE.ps1` version `49.3I.52.1`.

Acceptance must cover:
- existing 3I.51 Product/Crawl/Profile/Filament behavior;
- Site pull of a newer clean Product revision;
- protection of a dirty Local Product from a newer Site revision;
- Site-only non-publishable Local mirror;
- no unintended Product publish;
- checksum-verified backup of the real Catalog SQLite.

Production remains blocked until owner Local acceptance, read-only Host/MySQL/migration audit and fresh verified backups.


## 3I.52C — Crawl visual review, multi-select and safe Product source recovery

Date: 2026-09-02  
Status: `GITHUB_UPDATED / QT CI PASS / SINGLE ACTIVE AI PASS / WINDOWS PORTABLE PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT TOUCHED`.

Owner foreground evidence showed that the Qt Crawl/Add Product workspace had become harder to operate than the mature Windows flow: candidates were text-heavy, image acquisition progress was not visible enough, current Search results were not an obvious fresh visual workspace, bulk selection/transfer was unclear, and Product editing needed an explicit safe source-data/image recovery action.

Implemented:
- current Search is a visual icon/card gallery scoped to the active Listing URL;
- every new Search clears prior live cards before its worker starts;
- Preview-first discovery exposes Product title/thumbnail before full collection;
- stable preview-thumbnail cache is shared with the legacy discovery evidence;
- cards report image state as `Preview: 1 عکس`, `N عکس دارد`, or an explicit no-preview state;
- rich collection emits per-image progress such as `عکس 3/5` and `عکس 5/5`;
- current-search and persistent Crawl gallery/table use explicit Qt MultiSelection with select-all/clear and selected-count feedback;
- selected candidates can be added/rejected in bulk; successful transfer returns Product ids and navigates to Products;
- already-collected identities route to their existing Product;
- persistent Crawl inventory is enriched with candidate title/thumbnail/status evidence;
- selected collected Product exposes a dedicated live image review strip with the actual local images, total image count and local-displayable file count;
- compact operator labels such as `شروع دریافت`, `موجودی Crawl`, `لینک پیش‌فرض`, `دریافت Product`, `افزودن انتخابی` and `حذف انتخابی` keep the full explanation in tooltips;
- Product image/source stage exposes `دریافت داده و عکس بیشتر از لینک محصول`;
- safe recovery refreshes source-owned data/images while preserving operator Persian title/description, final price, sale approval and publish decision.

Rollback:
`backup/pre-phase49-3i52c-crawl-review-recovery-20260902` → `dfc883cc6ac68c49c589c0d5a6007d50a9a4719c`.

Verification:
- `33625257602` Qt6 Crawl + AI Runtime CI PASS on final runtime `bb0dcd7cc521cacc540943ed8091a323038c28f9`;
- `33625257485` Single Active AI PASS;
- initial Portable run `33624135587` failed only because the newly added Qt regression imported PySide6 while that release job installed only the non-Qt requirements;
- the failed condition was changed: Portable CI now installs `requirements-qt6.txt`;
- `33625257693` Windows Portable PASS on final runtime `bb0dcd7cc521cacc540943ed8091a323038c28f9`;
- portable regression gate: 217 tests PASS;
- artifact id `9844598171`, EXE SHA256 `e4064509a8d3a53ab3787b785f97f849e929c0873ed4ea021a99d46bc363af2b`;
- browser smoke and EXE self-verification PASS.

Safety:
- no new Django migration;
- no destructive Catalog migration;
- Preview cache is additive under the persistent Catalog data root;
- no Host/Production source or MySQL write;
- Production remains at `c283864290f9c989a9fcdf24ee8eef519560e917`.

Owner Local acceptance:
- canonical runner is `RUN_PHASE49_3I42C_LOCAL_GATE.ps1`, version `49.3I.52.2`;
- it checksum-backs up `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3` before foreground QA;
- verify fresh Search clearing, visual Preview, per-Product 3/5→5/5 image progress, image-count labels, multi-select bulk transfer to Products, persistent visual inventory, and safe more-data/more-images Product recovery.


## 3I.52C final visual/runtime checkpoint — 2026-09-02

Final tested runtime: `f43c7aa464948832ba349543f94c94498490ab25`.

Owner-visible finalizations on top of the initial 3I.52C recovery:
- current-search cards keep Preview-first title/thumbnail and per-Product image progress;
- selecting one collected Product exposes a real local image strip with total-image and local-displayable-file counts;
- receive/bulk actions use compact labels plus full tooltips to prevent the crowded unreadable toolbar shown in owner QA;
- the Qt sidebar and About dialog now report `Phase49.3I.52C` instead of the stale `Phase49.3I.48` identity.

Final verification:
- `33625988684` Qt full parity PASS, including the dedicated 3I.52C visual/recovery suite and all mature regressions;
- `33625988674` Single Active AI PASS;
- `33625988663` Windows Portable PASS;
- Portable regression gate: 218 tests PASS;
- artifact id `9844889166`;
- EXE SHA256 `cd54431bd29bad76990c17eb818671e3f32c4d53a244cdc07132f5d93a532f4b`.

No Django migration, Host source change, Production deploy or Production MySQL write was performed.


## 3I.52D — Mature collected-image path parity + numeric control layout

Date: 2026-09-02  
Status: `GITHUB_UPDATED / QT CI PASS / SINGLE ACTIVE AI PASS / WINDOWS PORTABLE PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT TOUCHED`.

Owner foreground QA proved a remaining compatibility gap in Add Products / Crawl: real downloaded image files from the mature Catalog Center existed, but unlinked Crawl rows still rendered `Preview تصویر ندارد`. The receive-count QSpinBoxes also overlapped in RTL on Windows.

Verified mature path:
- persistent Catalog root: `D:\projects\3dprinthub-catalog-manager`;
- downloaded Product folder: `collected\<source_code>\<external_id>`;
- original images: `images`;
- finalized images: `seo_images`;
- retained old installed application root: `D:\projects\3dprinthub_catalog_center`, read-only compatibility only.

Root cause:
- Qt image lookup was Product-id-gated for Crawl rows;
- unlinked old ledger identities skipped mature local files and checked only the newer discovery Preview cache;
- source-code matching was case-sensitive;
- RTL QSpinBox arrow/text geometry was not normalized.

Implemented:
- read-only identity-based local image discovery rooted at the active Catalog SQLite parent;
- Product local_dir remains first authority;
- `seo_images` is preferred before original `images`;
- unlinked Crawl rows can show/count mature downloaded local images;
- live review can show those actual files before Product linkage;
- source-code Product resolution uses case-insensitive matching within the bounded page resolver;
- no Product record or image file is moved/rewritten to make the display work;
- requested Product count and image-limit QSpinBoxes are LTR, centered, width-bounded and padded from Windows arrow controls;
- receive form grid spacing and editable-column stretch are explicit.

Rollback:
`backup/pre-phase49-3i52d-legacy-image-path-layout-20260902` → `28b51d2f95b272d3bf6311fb02f55a7a4fa808e4`.

Verification:
- exact runtime `a18b6f3036d41271cf3e8c1d9a0dfd8c271a53ce`;
- Qt `33628825851` PASS;
- dedicated 3I.52C/52D suite: 13 tests PASS;
- Single Active AI `33628825772` PASS;
- Windows Portable `33628825715` PASS;
- Portable release regression: 221 tests PASS;
- artifact id `9846044486`;
- EXE SHA256 `c08aa1e9d12926203cb59c580aab6c606c2b0e259ad83df37aa3b3abec86c22a`.

No Django migration, Catalog migration, destructive file operation, Host source change, Production deploy or Production MySQL write was performed.


## 3I.52E — Permanent Crawl image parity for recent Preview + historical refetch folders

Date: 2026-09-02  
Status: `GITHUB_UPDATED / QT CI PASS / SINGLE ACTIVE AI PASS / WINDOWS PORTABLE PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT TOUCHED`.

Owner screenshots after 3I.52D clarified two remaining image-miss classes:
1. historical files written by mature refetch/source-refresh workflows into sibling folders rather than the exact external-id folder;
2. recent `new` identities whose listing-card image is lazy-loaded and therefore did not populate the Preview cache.

Verified mature historical folders:
- `<external_id>_refresh_latest`;
- `<external_id>_refetch_<timestamp>`;
- `<external_id>_bulk_refetch_<timestamp>`.

Implemented:
- read-only ImageCore resolution covers those folders plus exact/local_dir authority;
- queue selected Product identity matching is source-code case-insensitive;
- listing Preview extraction captures currentSrc, src, data-src, data-original, data-lazy-src, img srcset, picture/source srcset and CSS background-image;
- HTTP candidates are selected instead of data/blob placeholders;
- srcset prefers the largest/right-most candidate;
- rerunning the same Search updates candidate Preview evidence while Crawl uniqueness prevents duplicate identities;
- local `N عکس دارد` remains evidence-based and is never synthesized for merely discovered rows;
- Qt shell reports `Phase49.3I.52E`.

Rollback:
`backup/pre-phase49-3i52e-preview-legacy-variants-20260902` → `ef82abe775f88f6326c345b4e17c797471acbc27`.

Verification:
- exact tested runtime `016e84ab98d2e5577633833cbc87cb96824dbbf0`;
- Qt full parity `33632062812` PASS;
- dedicated visual/recovery suite 15 tests PASS;
- Single Active AI `33632062877` PASS;
- Windows Portable `33632062880` PASS;
- portable release regression 223 tests PASS;
- artifact `9847317893`;
- EXE SHA256 `f9bcfc0770a38b0c8eabc9f2deab7c05b2c4d8b577fd25eb540ea9b65f7dc970`.

ERR-49-099 records and closes the intermediate raw-JavaScript string delimiter mistake; final CI passed after correction.

No database migration, media rewrite, Host source change, Production deploy or Production MySQL write was performed.


## 3I.52F — Bulk recovery for incomplete permanent Crawl rows

Date: 2026-09-02  
Status: `GITHUB_UPDATED / QT CI PASS / SINGLE ACTIVE AI PASS / WINDOWS PORTABLE PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT TOUCHED`.

Requested operator workflow:
- select many permanent Crawl rows;
- select incomplete rows automatically;
- choose 5 or 10 images;
- reuse already-downloaded local evidence when complete;
- otherwise revisit each Product source URL and recover Product title/description/images;
- explicitly repair previously-collected-but-broken identities instead of being stopped forever by terminal-ledger deduplication.

Mature precedent:
the previous Tk application already provided `bulk_refetch_selected()` and used `merge_refetch()` to protect operator changes. Qt 3I.52F extends the same safety boundary to Crawl inventory.

Implemented:
- `انتخاب ناقص‌ها` on loaded permanent inventory rows;
- image target combo 5/10/20;
- `بازیابی دیتا + عکس` bulk action;
- complete Product + sufficient local files is reused without network;
- incomplete existing Product uses safe source refetch;
- explicit `force_recover` bypasses terminal identity skip only for this operator-triggered repair action;
- if an existing Product is found, force recovery routes through safe `refetch_product_from_source_async` rather than raw upsert;
- blocked Product cannot be silently revived;
- orphan ledger identity with no Product can be rebuilt;
- Product URL slug supplies readable fallback title before full receive;
- queue actions are split into two rows to avoid crowding;
- old queue status button is renamed `بازگردانی به صف`.

Rollback:
`backup/pre-phase49-3i52f-bulk-recover-incomplete-20260902` → `f35bd3e409c4293a756ddfe2fc9d4f7dcb968445`.

Verification:
- exact tested runtime `cf73f841418aac2eec1b78e0dbd682ceb2d3fef5`;
- Qt full parity `33637452385` PASS;
- dedicated 3I.52 suite 19 tests PASS;
- Single Active AI `33637452588` PASS;
- Windows Portable `33637452243` PASS;
- Portable release regression 227 tests PASS;
- artifact `9849484898`;
- EXE SHA256 `f0150359fd36c7ead84599ccd0b799797ed48e85e4c6eac1d191abc3f0315a64`.

ERR-49-100 and ERR-49-101 record the two test-fixture failures encountered and corrected before final PASS.

No Django/Catalog migration, destructive media operation, Host source change, Production deploy or Production MySQL write was performed.
