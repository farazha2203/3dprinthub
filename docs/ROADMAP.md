## 2026-09-19 - Phase50.A.2L site-priority release
- [x] Recover and authenticate dedicated reverse tunnel `22024`; verify Host identity, clean Production baseline and watchdog cron.
- [x] Build Production-based release containing only Example-4 Slicebox Hero + Product Admin 504 fix.
- [x] Local syntax/check/no-drift and focused Hero/Admin 25/25 regression PASS.
- [x] Add guarded no-migration deploy runner with source/.env/static rollback evidence and Production HTTP/runtime gates.
- [x] Commit/push exact release `28cac45...` and verify live GitHub SHA.
- [x] Deploy ff-only from GitHub through the dedicated reverse tunnel; backup/readiness/no-migration/static-wrapper gates PASS.
- [x] Detect ERR-49-170 in real Chromium: nested Slicebox vendor assets 404 because new public directories inherited `0700`.
- [x] Add repository-owned static permission prevention + dedicated guarded hotfix runner.
- [ ] Push/deploy permission hotfix from current clean Production `28cac45...`.
- [ ] Re-run nested asset HTTP/MIME + desktop/mobile real-browser Example-4 acceptance.
- [ ] Verify Product Admin runtime composition remains Variant-inline-free and close Production docs.

## 2026-09-16 - Phase50.A.2J standalone Hero acceptance
- [x] Recover and verify the dedicated 3DPrintHub reverse tunnel/watchdog path.
- [x] Keep the client-facing Store empty: Product/Variant/ProductImage = `0/0/0`.
- [x] Replace the public top Hero with standalone A2J CSS/JS; no legacy A2I/Phase49 Hero JS is loaded.
- [x] Fix ERR-49-147 by bounding Persian Hero description persistence to the real model max length and using explicit short Seeder copy.
- [x] Focused 29/29 and broad Hero 90/90 tests PASS; compile/check/no-model-drift/diff-check PASS.
- [x] Production source/GitHub release exact at `859b9e77...`; MySQL identity correct; migration plan empty; Host clean.
- [x] Verified rollback root `/home/sfkilvrs/3dprinthub-deploy-backups/20260916-030333-phase50-a2j-description-seed` including source bundles, MySQL gzip and Hero JSON checksums.
- [x] Seed exactly assets `119,120,135,136` in order `10,20,30,40` with safe `/#order` targets.
- [x] Browser desktop: four slides, real five-cuboid preserve-3d transition, slide change and overlay cleanup, no broken images/errors.
- [x] Browser mobile 390px: four slides, zero cuboids, fallback transition, no overflow/errors.
- [x] Store `/store/` HTTP 200 and empty after Hero release.
- [ ] Re-verify canonical Windows Catalog Center branch/head/SQLite backup/receiver readiness.
- [ ] Relaunch the exact tested Windows runtime so the owner can intentionally resend Products/images to the empty Store.
- [ ] Run one controlled resend/update from Windows after owner selects a Product; require strict ACK/public media/Store verification before widening.

## 2026-09-15 - Host transport recovery
- [x] Restore dedicated 3DPrintHub reverse tunnel and verify Windows `127.0.0.1:22024` listening.
- [x] Verify authenticated Host bridge identity/base.
- [x] Verify one-minute cPanel watchdog cron entry is present and uses `flock` + repository bootstrap.
- [ ] Deploy current GitHub handoff head through the reverse tunnel.
- [ ] Create fresh MySQL/media reset backup, execute eligible Store reset, and complete Production browser QA.

## 2026-09-15 - Client handoff transport blocker
- [x] Push application candidate and dedicated guarded deploy runner.
- [x] Prove Local Hero 50.3.0 in Chromium and Store Reset regression gates.
- [x] Diagnose reverse tunnel: Host bridge state exists; authorized-key fingerprint matches; Windows loopback 22024 closed.
- [x] Prove watchdog/cron stopped updating and FTPS has no command channel.
- [x] Prove stored FTP credential is not accepted by cPanel API and no `.cpanel.yml`/GitHub auto-deploy exists.
- [ ] Restore only 3DPrintHub cPanel watchdog/bootstrap execution.
- [ ] Run guarded GitHub deploy, verified reset backup, Store Reset and Production browser acceptance.

## 2026-09-15 - Client handoff deploy runner checkpoint
- [x] Push application candidate `dd1e770...` to canonical branch.
- [x] Browser-verify Local Hero 50.3.0: 1440x823 full-bleed, real temporary 3D cuboids, mobile fallback.
- [x] Add dedicated exact-baseline handoff deploy runner.
- [x] Runner bash syntax, diff-check and secret scan PASS.
- [ ] Commit/push runner and require GitHub checks green.
- [ ] Restore PrintHubTunnel only; verify Host branch/HEAD/worktree/MySQL/readiness.
- [ ] Run guarded GitHub deploy, create verified MySQL/media reset backup, reset Store if eligible, then Production browser acceptance.

## 2026-09-15 - Client handoff delivery gate
- [x] Re-read repository rules/state/errors/paths/active Phase from source of truth.
- [x] Preserve the existing dirty worktree and inspect Store Reset, Hero, publish/Instagram and timeout-reconciliation deltas instead of resetting them.
- [x] Complete fail-closed Store Reset API that preserves source assets/master data/Portfolio/Hero/history and refuses protected/manual/inventory-conflicted state.
- [x] Add repository-owned Store Reset backup-manifest/media helper with exact MySQL identity and checksum boundaries.
- [x] Upgrade Home Hero candidate to full-screen native 3D cuboids with random horizontal/vertical transitions and mobile/reduced-motion fallback.
- [x] Verify Site→Instagram order remains Site publish/public URL first, Instagram second; no social post without configured Professional credentials.
- [x] Local gates: 8/8 Store Reset+Hero, 57/57 broader Qt/Publish/Instagram/SiteConnection, compile, Node syntax, Django check, no drift, empty migration plan, diff-check PASS.
- [ ] Commit/push exact candidate and verify live GitHub SHA.
- [ ] Re-establish authorized reverse Host transport and verify Host root/branch/HEAD/worktree/MySQL/readiness read-only.
- [ ] Deploy only the GitHub candidate with fresh source/env/static rollback evidence.
- [ ] Generate fresh real MySQL gzip + Store Reset manifest/media backup and verify hashes/counts.
- [ ] Run Production reset only if preflight is eligible; verify Store Product/Variant/Image count reaches zero and protected/master/source/Hero data is unchanged.
- [ ] Browser-verify Production Hero desktop 3D transition, mobile fallback and public Home/Store HTTP after reset.
- [ ] Update final docs with deployed SHA, backup root, reset counts and browser acceptance before client handoff.

## 2026-09-14 - ERR-49-144 GitHub CI correction follow-up
- [x] Runtime/docs commit `1a5ba6a...` pushed and remote verified.
- [x] Fresh checksum-identical Catalog backup created and SQLite integrity/count parity verified.
- [x] Pushed Qt runtime launched successfully; startup structural contract PASS and DB post-launch quick check PASS.
- [x] Three GitHub workflows PASS on `1a5ba6a...`.
- [x] Diagnose Qt6 CI failure as stale three-column test expectation, not runtime regression.
- [x] Update parity test to the accepted four compact columns.
- [x] Run exact failed CI foundation/parity suite locally: 23/23 PASS.
- [ ] Push corrective test/docs checkpoint and require GitHub Qt6 CI PASS.
- [ ] After green CI, preserve the currently running owner foreground app for visual acceptance.

## 2026-09-14 - ERR-49-144 Published/gallery regression
- [x] Preserve `workflow_status=uploaded` Products in the Published lifecycle even when Local edits set `needs_update=1`.
- [x] Preserve republish discoverability through the existing Work Queue at the same time.
- [x] Count/render actual locally-displayable Product media instead of raw source URL count.
- [x] Reuse legacy numbered local WebPs read-only without weakening strict publish media mapping.
- [x] Disable mutating controls for legacy display-only files that lack trustworthy source URL identity.
- [x] Restore a compact four-column Product image gallery.
- [x] Verify real Catalog: Published=19; #33=16 real files; #34=25; #63/#628/#634=2 each.
- [x] Run focused + adjacent Qt/Crawl/Publish regression: 77/77 PASS.
- [ ] Commit/push exact isolated delta and verify live GitHub SHA.
- [ ] Create fresh Catalog rollback backup and relaunch the pushed Qt runtime for owner foreground acceptance.

## 2026-09-14 - Product #303 bounded sales candidate
- [x] Audit all approved non-uploaded candidates on a copied Catalog DB.
- [x] Identify #303 as the only candidate with no operator-only missing facts.
- [x] Preview keyword backfill from existing finalized image metadata on copied DB + copied Product folder.
- [x] Preview Content/Images finalization, media gate and publish gate PASS.
- [ ] Create fresh canonical Catalog + Product-media rollback backup.
- [ ] Apply the same StageCore repair to canonical #303 and verify no unrelated Product changed.
- [ ] Mark ready, receiver/FTP/Bridge gate, publish exactly #303, then strict public Variant/orderability/cart acceptance.

## 2026-09-14 - Sales expansion checkpoint: Product #62 accepted
- [x] Repair Catalog #62 with one canonical factual Profile using the mature CommerceCore ledger path.
- [x] Preserve existing Host/Site identity: asset 140 / Product 18.
- [x] Create fresh Catalog + Production MySQL rollback backups before writes.
- [x] Republish #62 through Batch 8.5 -> FTP -> Bridge; strict visibility/orderability/public-media checks PASS.
- [x] Real Chromium Cart acceptance: Variant 884, 500,000 Toman, quantity 1; POST intercepted before server.
- [x] Confirm current orderable Production set: Site Products 16, 17, 18.
- [ ] Deploy GitHub-approved `07772ca...` stale-public lifecycle fix through an authorized Host execution path.
- [ ] Republish #84; keep Product 19 inactive/noindex while selected black-matte stock remains zero.
- [ ] Audit the next factual ready subset; do not guess #43 Material/Color/image metadata.

## 2026-09-14 - ERR-49-138 stale-public gate
- [x] Prove #18/#19 active but 0 orderable Variants on Production.
- [x] Add committed deactivation/noindex path for already-public non-orderable Products.
- [x] Importer reports `publish_incomplete` and excludes non-visible Product from published count.
- [x] 19 focused E2E/visibility/Variant tests + no-drift PASS.
- [x] Commit/push ERR-49-138 source from exact `70a74e6...` baseline to GitHub (`07772ca...`).
- [x] Repair #62 with factual fixed-price/PLA-white/Profile data and republish; Chromium Cart acceptance PASS.
- [ ] Deploy `07772ca...` to Production through an authorized Host mutation path.
- [ ] Republish #84 fail-closed; keep off Store until selected black-matte inventory is real.

## 2026-09-14 - Active sales gate: ERR-49-135 real orderability
- [x] #628/#634 strict ACK + live customer Cart acceptance.
- [x] Detect #62/#84 false-positive visibility: public but no orderable Variant.
- [x] Local contract fix: canonical Profile required before FTP + shared Store orderability + visibility orderable gate.
- [x] Local compile/tests/check/no-drift/runner syntax gates PASS.
- [x] Commit/push exact orderability hotfix and verify GitHub head/CI.
- [x] Guarded no-migration Production deploy from exact `6569e5a...` to `70a74e6...`.
- [x] Backup Catalog and repair/re-publish #62 same identity; live Cart PASS.
- [ ] Repair/republish #84 only when lifecycle fix is live; current selected black-matte stock is zero.
- [ ] Keep #43 blocked until factual Material/Color and current image metadata are complete.

## 2026-09-14 - Sales launch gate passed
- [x] Deploy owner-license Host parity at `6569e5a...`.
- [x] Fresh Catalog backup before bounded retry.
- [x] Publish exactly #628/#634: strict ACK/public media/Product visibility PASS.
- [x] Real browser Variant/price/Cart wiring PASS with POST intercepted before server.
- [ ] Audit remaining ready #43/#62/#84 against current factual gates.
- [ ] Publish only passing subset, then verify strict ACK/public pages/media/cart before any larger batch.

## 2026-09-14 - Active sales-unblock gate: ERR-49-131 owner-license Host parity

The first bounded two-Product publish exposed a contract mismatch, not a legal-status rewrite requirement. Project owner policy already marks every reviewed Catalog source/license stage through explicit `source_license_owner_approved`; Windows readiness/export honors it, while the Host importer/conversion/visibility path ignored it and returned `review_required` for #628/#634. Local hotfix preserves raw license evidence and honors the separate owner approval at every Host gate. Automated Site/Catalog/no-drift/deploy-runner gates PASS. Next: GitHub-first no-migration Production promotion from `44a7be9...`, then retry only #628/#634 from a fresh checksum Catalog backup. Broader Product publishing remains bounded until both receive strict Store-visible ACK and live cart verification.

## 2026-09-14 - Controlled Product gate PASS; bounded publishing unlocked

Production is now exact clean `44a7be9...` with the ERR-49-125 Product-owned public-media fix and A2I seven-slice Hero deployed through verified backup/ff-only/collectstatic/restart gates. Desktop/mobile Hero browser QA, public Bridge/media, strict stored ACK for Windows Product #63 -> Site Product #15, canonical Variant 618 selector and intercepted no-write Cart POST all PASS. The one-Product prerequisite that blocked broader publishing is closed. Next: publish only a bounded small set of factually ready Products with the same strict ACK/public-media/cart verification, while continuing Phase50 finance/payment/admin work.
## 2026-09-14 - A2I + Bridge public-media combined Production gate

The A2I 3D Hero is already committed/pushed at `b1bbdee...`, while Production remains clean at A2H source `443d1b70...`. The pending ERR-49-125 Bridge public-media fix and A2I static assets must move together because the old Bridge-only runner forbids collectstatic. A new combined fail-closed runner is Local-tested: exact baseline/live target/ff-only guards, MySQL/readiness/empty-plan checks, verified source/env/static backup, collectstatic with hash equality, Passenger restart, authenticated Product #15/Hero public-media verification and live A2I static/Home markers. No migration or DB write is allowed. Next: commit/push -> GitHub-first deploy -> Production browser Hero + Product #63 selector/cart/strict ACK -> bounded bulk only after PASS.
## 2026-09-13 - A2G Bridge media hotfix deployment gate

A dedicated fail-closed Production runner is Local-tested for the ERR-49-125 public-media serializer fix. It requires exact clean Host baseline `443d1b70...`, live target equality and ff-only ancestry, forbids migration/dependency/settings drift, creates verified source/environment rollback evidence, performs no DB migration/write or collectstatic, restarts Passenger and verifies Product #15/Hero use only Product-owned public WebPs. Next: commit/push -> guarded Host deploy -> Product #63 selector/cart/strict ACK -> bounded multi-product publish.

## 2026-09-13 - A2G controlled Product acceptance: public Bridge media hotfix

Product #63 reached Production with valid Product-owned WebP gallery files, but the unified Bridge read contract still serialized ImportedPrintAsset working-media URLs. A narrow no-migration fix now maps imported image identity to Product-owned public gallery media and applies the same rule to Hero selected media. Local focused regression is green and the fix is on live GitHub at `d830a9af05d768f9b81568a0665a74f59e864a34`. Next: guarded no-migration Host promotion -> authenticated Bridge/public HTTP verification -> Product #63 guided cart + strict ACK. Bulk remains blocked until that acceptance passes.
## 2026-09-13 - Active gate: Phase50.A.2H Storefront Showcase Polish

A2G remains Production-verified at `d7cf71d...`; A2H is the Local-tested visual follow-up. It improves Hero product staging, selected-Variant price presentation and the first-visit theme chooser without changing commerce authority or introducing a migration. Local Django/no-drift, Node 8/8, Playwright responsive and real Home desktop/tablet/mobile gates PASS. Next: dedicated no-migration GitHub-first deploy and Production verification, then the already-required one-Product end-to-end publish acceptance before bulk.

## 2026-09-13 - Reverse management + A2G Production gate complete

Reverse Host management is E2E verified and active: authenticated Windows loopback `127.0.0.1:22024` reaches the Host-only bridge `127.0.0.1:22224`, with Host source restricted to `89.39.208.237/32`. Exact Production/Local/GitHub source at acceptance is `d7cf71dceca95e191a118336c7004683083278ee`. The repository read-only Production audit, MySQL identity, Store 0036-0042 + Website 0024 recorder state, empty migration plan, receiver readiness, public Bridge and A2G static HTTP gates all PASS.

Phase50.A.2G is now `PRODUCTION_VERIFIED`. Next is exactly one controlled Product Windows-to-Production acceptance with finalized SEO WebPs, strict ACK, canonical Product/Profile/Variant, public media/page and guided cart verification. Bulk Product publication remains blocked until that one Product passes. The tunnel changes transport only; development remains Local -> tests -> GitHub -> Host ff-only -> Production verify.

## 2026-09-13 - Operations gate: 3DPrintHub reverse Host management

Adopt the repository-published Asal reverse-management standard for this shared cPanel Host: loopback authenticated command bridge on Host `127.0.0.1:22224`, outbound Host SSH/443 to the verified Windows public endpoint, and Windows loopback operator port `22024`. Windows side is prepared and source-restricted for declared Host IP `89.39.208.237/32`; Repository operations implementation `180fe16c0e296156ef38ffc00a042c329318ff7c` is on live GitHub. Host onboarding/E2E identity proof is next. This is transport only; normal Local test -> GitHub -> Host ff-only deploy -> Production verify remains mandatory.
## 2026-09-12 - Active gate: Phase50.A.2G Publish-ready Media + Professional Order Wizard

A2F is Production verified at `7d0b3df...`. A2G closes the final pre-bulk Product-publication boundary: only current finalized SEO WebP files may enter a Product Batch, exact media bytes/names survive Windows-to-Host, identical re-import is idempotent, and changed media advances visual revision only once. The Storefront wizard is responsive across desktop/tablet/mobile with progress, guidance, keyboard/touch support and canonical Variant fallback.

Local gates pass: Catalog 10/10, Django 16/16, Node 8/8, Playwright responsive suite, compile/check/no-migration-drift/diff-check and A2G Host-runner syntax/no-migrate/exact-delta contract. Exact runtime `e76e555...` passed the canonical checksum-backed Windows gate and Catalog Center launched. Host source has since advanced to `a320a0d...`; public Home/Store/new JS/CSS are HTTP 200. Next: complete reverse-tunnel E2E + authenticated Host worktree/Bridge/readiness acceptance, then publish one controlled Product and verify Product/Profile/Variant/WebP/public page/strict ACK before bounded bulk.

## 2026-09-12 — Phase50.A.2F PRODUCTION VERIFIED

Status: `PRODUCTION_VERIFIED`.

Production deployment completed successfully from recovered baseline `e12fdaf281f7e08013e54c7cf936f8275127ab2b` to exact GitHub commit `7d0b3df03c3657106ebaf86d5f9123ba262495a5` using `scripts/host/phase50_a2f_storefront_production_deploy.sh`.

Verified Host evidence: MySQL `sfkilvrs_EmiAdmin_3dprinthub`; required Store 0036–0042 + Website 0024 migrations present; migration plan empty before and after promotion; publish-readiness ready=true with no blockers; verified source/.env/static backup at `/home/sfkilvrs/3dprinthub-deploy-backups/20260912-182234-phase50-a2f-storefront`; ff-only Git promotion; collectstatic; Passenger restart; Home/Store/Bridge health/readiness/new JS/new CSS all HTTP 200; final Host worktree clean.

Guided customer ordering is now live on Production: size → color → compatible material → print quality → canonical ProductVariant → server-authoritative price/stock/weight/time → cart. Native Variant select remains fallback.

Next exact acceptance: one controlled Product publish from Windows Catalog Center to the now-ready receiver, verify Product/Profile/Variant/images/public Store/strict ACK, then enable bounded multi-product publish. In parallel continue Phase50 finance/payment/admin work after this Product-publish acceptance.
- 2026-09-12 A2F deploy follow-up: fix/test ERR-49-115 root-document allowlist, push a new exact GitHub target, then retry the no-migration guarded Host deploy from unchanged `e12fdaf...` baseline.
## 2026-09-12 — Production recovery verified; 2F deployment is the active gate

Live Bridge/readiness evidence supersedes the older partial-0039 roadmap state: Production MySQL is ready, Store 0036–0042 and Website 0024 are applied, receiver schema/storage prerequisites pass with no blockers, and Production source is `e12fdaf...`. Do not rerun 53G.

Phase50.A.2F is Local-tested and GitHub-tested at `38458ce...`; next is the repository-owned no-migration deploy gate. The deployment must start from exact clean Host baseline `e12fdaf...`, fetch the live branch explicitly to `FETCH_HEAD`, make verified source/env/static backups, prove no migration/requirements/settings delta, ff-only promote, collectstatic/restart and verify public Store + Bridge + new guided JS/CSS. After Production verification, continue Phase50 commerce/finance work.

## 2026-09-12 — Active Local gate: Phase50.A.2F Guided Storefront Configurator

Phase50 customer ordering now advances from the internal Profile Matrix toward a four-step guided Storefront flow: size → color → compatible material → print quality. Canonical ProductVariant, server price, stock, weight/time and native fallback remain authoritative. Local Node/Django/Playwright gates pass and no migration is introduced.

Immediate sequence: commit/push exact Local delta; run canonical Windows Catalog Center Local gate on the clean GitHub HEAD; re-audit actual Host/partial MySQL state; complete 3I.53G recovery before any normal Production deployment. Finance/ZarinPal/Torob work remains after the current commerce/receiver safety gates.
## 2026-09-02 — Phase49.3I.53G recover partial MySQL migration 0039

Status: `IMPLEMENTED + REAL MYSQL PROBE PASS / HOST PARTIAL-STATE RECOVERY NEXT`.

Production source is `5f6c13ab...`. Website 0024 and Store 0037/0038 are applied. Store 0039 stopped on duplicate `ProductVariant.support_weight_grams`; 0040–0042 remain pending.

Root cause is confirmed in Repository history: 0033 already creates ProductVariant support weight; 0039 incorrectly attempted a second AddField. 0039 is corrected to AlterField for that existing ProductVariant column and idempotent AddFieldIfMissing for the truly new columns.

Recovery is encoded in `scripts/host/phase49_3i53_partial_0039_resume.sh`: exact recorder/schema forensics → reverify old rollback sets → fresh backup of current partial DB → ff-only source fix → exact 0039–0042 plan → migrate → readiness → static/restart/public verification.

Evidence: Variant/Profile `33664796042` PASS; Product Admin + real MySQL focused recovery probe `33666085743` PASS; Single Active AI `33666085841` PASS; tested recovery code `66e940e6e659f86e3783d78d091b3ff00acbf5aa`.

Next: run 53G recovery on Host. If physical partial state differs from the observed failure boundary, stop and inspect; no fake migration.

## 2026-09-02 — Phase49.3I.53F post-merge dependency/startup recovery

Status: `IMPLEMENTED + CI PASS / PRODUCTION RESUME NEXT`.

Production source is already at `b372586a...`, but DB remains unchanged because the deploy stopped at post-merge Django startup on missing `httpx==0.28.1`.

Recovery now:
- makes Site AI provider/content transport imports lazy;
- preserves mature AIProviderClient patchability;
- proves Django bootstrap does not require httpx;
- adds target dependency install/verify to normal deployment;
- adds a dedicated post-merge resume runner that reuses/re-verifies the valid rollback backup, then installs exact dependency, takes a fresh DB backup, verifies the exact migration plan and completes migration/static/restart/readiness.

Evidence: `ccd1b98997a8dd0c8389ccbe2b6c78b83dd7f176`; Product Admin `33663316332` PASS; Single Active AI `33663316324` PASS.

Next: execute post-merge resume from Host HEAD `b372586a...`; do not rerun the original baseline deploy runner.

## 2026-09-02 — Phase49.3I.53E backup helper import-boundary fix

Status: `IMPLEMENTED + CI PASS / PRODUCTION DEPLOY RETRY NEXT`.

Second deploy attempt stopped safely before source promotion because the extracted backup helper could not import `config` from outside the repository. The helper now receives and validates the exact Production project root and prepends it to Python import paths before Django setup.

Production remains on `198fa8e41ea4f4d87eb287ba69c91076acc78d62`.

Evidence: `2016b84ee1b053e792ceb44ede516b3d7a2dea7e`; Product Admin CI `33661199115` PASS; Single Active AI `33661199159` PASS.

Next: fresh timestamped backup and deploy retry against the current live GitHub target.

## 2026-09-02 — Phase49.3I.53D verified MySQL backup streaming fix

Status: `IMPLEMENTED + CI PASS / PRODUCTION DEPLOY RETRY NEXT`.

The first audited deploy stopped safely before source promotion because the MySQL file had a `.gz` suffix but raw mysqldump contents. The backup boundary has been corrected with a repository helper that pipes mysqldump output through the actual gzip encoder and verifies gzip magic/header before the existing `gzip -t` + SHA256 gate.

Production remains at `198fa8e41ea4f4d87eb287ba69c91076acc78d62`; no migration or restart occurred.

Final fix `3b6254bf7700bb26b4af63d21e31e56e7700877c`; Product Admin/backup CI `33659707983` PASS; Single Active AI `33659707957` PASS.

Next: fresh timestamped backup + controlled deploy retry. Do not reuse the invalid 20260902-203857 MySQL artifact.

## 2026-09-02 — Phase49.3I.53C audited Production receiver deployment

Status: `DEPLOY RUNNER READY + CI PASS / PRODUCTION EXECUTION NEXT`.

Host audit proved the exact Production baseline and pending receiver migration chain. A repository-owned deployment runner now enforces verified backups, exact migration-file/plan gates, ff-only promotion, migration, collectstatic, Passenger restart and authenticated receiver/public HTTP verification.

Current Host DB state: Store 0036 + Website 0023 applied; Store 0037–0042 + Website 0024 pending. Active Material/PrintQuality prerequisites and storage/token/disk/backup tooling are ready.

Evidence: read-only Host audit PASS from owner output; deploy runner `5c5f087ae26e78c106984cf3c92e9b322537f203`; Product Admin/audit CI `33658713537` PASS; Single Active AI `33658713594` PASS.

Next: execute deploy runner from GitHub. After receiver PASS, publish exactly one controlled Product from Catalog Center and verify site Product/image/ACK before bulk enablement.

## 2026-09-02 — Phase49.3I.53 Site publish receiver + Host deployment gate

Status: `IMPLEMENTED + SITE/WINDOWS CI PASS / HOST READ-ONLY AUDIT NEXT / PRODUCTION NOT DEPLOYED`.

Completed:
- added authenticated receiver-readiness endpoint for Desktop Product publish;
- checks required Store/Website migration state, schema, token presence, pending/media storage and Product-import prerequisites;
- Desktop publish fails closed before FTP when the live Site receiver is not ready;
- Bridge health and publish readiness are separate operator states;
- old Site without the new endpoint is shown as Bridge-connected but publish-blocked;
- added repository-owned Production read-only audit with no source/DB/runtime mutation;
- reviewed the pending Production migration chain 0036..0042 + website.0024; no new 3I.53 migration.

Evidence: Site `33652584032` PASS; Variant/Profile `33652583964` PASS; Host-audit contract `33652996666` PASS; final Qt `33653229142` PASS; final Single Active AI `33653229219` PASS; final Portable `33653229400` PASS with 235 regressions; artifact `9855771656`; EXE SHA256 `a6bebd3c10a56aac1c65a58d5ffb1029382e98c7b0782a4b034a315e60c2f1ed`.

Next: read-only Production audit, then fresh verified backups, then controlled ff-only deploy/migration/collectstatic/restart/receiver+Product verification. Production remains untouched until audit evidence is reviewed.

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

## 2026-09-14 - Phase50.A.2I Slicebox-inspired 3D Hero

Status: `LOCAL_TESTED / GITHUB PROMOTION NEXT`. The existing managed Django Hero now has an optional dependency-free seven-slice 3D transition inspired by Codrops Slicebox. Existing SSR content, Product links, timing, arrows, dots, keyboard/swipe and mobile/reduced-motion fallback remain authoritative. Focused Hero/Public-Media regression 30/30 PASS and real Playwright desktop/mobile QA PASS. No migration, dependency or commerce-authority change. Next: commit/push the reviewed A2I delta, then combine it with the already-tested A2G Bridge public-media fix for guarded Production deployment and Product #63 final cart/ACK acceptance.

## 2026-09-14 - Manual publication simplification checkpoint
- [x] Give every active Local Filament one 1000 g roll of stock.
- [x] Remove zero purchase/sale/service pricing from active Local Filaments using owner overrides + existing Material reference authority.
- [x] Ensure every Local Product has a canonical Sales Profile.
- [x] Preselect every unique active Filament identity in every Product Profile.
- [x] Preserve existing factual Profile rows; use fallback production facts only where Profile/production data was absent.
- [x] Mark previously uploaded Products for same-identity republish instead of duplicate publication.
- [x] Focused Filament/Profile tests 34/34 + Qt verification PASS; relaunch Windows Catalog Center.
- [ ] Owner manually adjusts Product dimensions/finalizes required stages and publishes selected Products from Windows.
- [ ] Continue the separate Store Reset feature before claiming the Production Store is empty; do not conflate that pending source work with this Local data policy.
