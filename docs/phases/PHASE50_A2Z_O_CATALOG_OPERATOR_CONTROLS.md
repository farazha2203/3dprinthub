# Phase50.A.2Z-O - Catalog Operator Controls + Crawl Recovery

Status: O1_ACCEPTED / O1B_ACCEPTED / O2_ACCEPTED / O2D_ACCEPTED / O2E_ACCEPTED / O2G_ACCEPTED / O2H_NEXT
Date: 2026-09-25
Branch: `wip/phase50-a2z-o2g-search-target-20260924`
Converged baseline: `82862b4569b537406618523f7350cd3514c4c03f`

## Objective
Close the owner-facing Product/Crawl operational gaps without creating a parallel Product, Site, or Social authority. All status views must derive from canonical Catalog fields, stage locks, and sync receipts. Destructive recovery must be backup-backed and same-identity safe.

## Six bounded phases
1. **O1 - Product Status Filters + Split Instagram Actions**
   - Exact 7/7 ready-to-publish filter.
   - AI-completed exact 6/7 filter.
   - Site-sent, Instagram Post-sent, and Instagram Story-sent filters.
   - Separate Post and Story buttons and execution paths.
1B. **O1B - Recent Product Activity Filters**
   - "Recently edited": Products ordered by the latest real operator save event, newest first.
   - Accepted edit events include factual Product editor saves such as `studio_save` and `qt_operator_edit`; generic `updated_at` is not the authority because sync/refetch can also change it.
   - "Recently viewed": Products ordered by the latest real Product Editor open/view event, newest first.
   - Only opening the Product Editor counts as a view; gallery visibility, hover, selection, filter refresh, or card rendering must never create a view.
   - View tracking must be persisted locally/auditable and must not dirty the Product for Site republish.
2. **O2 - Crawl Completeness Views**
   - Complete / incomplete filters.
   - Completeness includes valid local image plus required content.
   - Missing reasons shown directly on each Crawl card.
2D. **O2D - Product Identity / Dedup / Consumed-Crawl Suppression**
   - Existing Product identity must never re-enter Add Products or automatic Product fetch.
   - Identity authority remains the existing `source_code + external_id` and normalized source URL; no parallel ID is introduced.
   - Existing discovery ledger rows remain as identity memory but are hidden from Add Products and excluded from pending/batch/preview work.
   - Product table exposes `source_code:external_id` so the link-derived identity is visible to the operator.
   - Any destructive dedup is allowed only for proven identical canonical identity after backup; same-title/different-link Products are never auto-deleted.
2E. **O2E - Product Media Truth / Refresh / Instagram Image Parity**
   - Product image refresh must reload the exact canonical Local DB/files image set for that Product.
   - Product UI preview/selection and Instagram media preparation must resolve from the same canonical image authority.
   - Repair stale/missing mapping without substituting unrelated Product media.
2G. **O2G - Search Crawl Pagination / Target Count**
   - Requested Product count must drive lazy/infinite-scroll depth instead of using a fixed preview depth.
   - MakerWorld search must continue toward the requested target (for example 200/300) until target reached or listing exhaustion is verified.
   - Duplicate/consumed Product identities remain excluded by O2D and must not count as new target progress.
2H. **O2H - Hard Delete Broken Crawl Identity**
   - Explicit Delete must be distinct from Reject.
   - Hard delete is allowed only for Crawl identities that do not map to a Product.
   - Remove the selected discovery row, candidate row, preview/cache and verified candidate-derived local data for that identity after fresh rollback.
   - Product-backed identity fails closed and must use the Product-specific update/delete flow.
2F. **O2F - Instagram Disclosure / Product Details / Story Link**
   - Verify the current Buffer/Meta provider API capabilities before implementation.
   - Apply the supported AI-generated-content disclosure/label contract to both Feed and Story where the provider exposes it.
   - Product details/caption metadata must include the original source Product URL and the 3DPrintHub order Product URL where the provider contract permits.
   - Implement clickable Story link only through a provider-supported API/native workflow; fail closed rather than fabricate unsupported stickers/links.

3. **O3 - Deep Crawl Repair / Full Re-fetch**
   - Verify backup and Source identity before repair.
   - Purge only the selected Product's corrupted/derived Local data.
   - Crawl/refetch from Source from scratch and remap to the same identity.
   - Preserve Site identity, receipts, and order authority unless an explicit contract permits change.
4. **O4 - Delete Semantics Repair**
   - Delete must produce a visible, testable result.
   - Product/Crawl queue/cache/tombstone semantics must agree.
   - Restore stays available only for safe retained identities.
5. **O5 - Social Receipt Reconciliation + Operator Acceptance**
   - Reconcile Post and Story independently from final provider receipts.
   - Independent duplicate guards for Post vs Story.
   - Product Social filters must match final receipt truth.
6. **O6 - Integrated Regression + Closure**
   - Product/Crawl/Social related regression.
   - Catalog integrity and launcher/runtime acceptance.
   - Any Server delta must follow GitHub-first backup/deploy/Production gates.
   - Final CURRENT_STATE/ROADMAP/CHANGELOG/ERRORS/REQUESTS closure.

## O1 implementation
- Windows `740bfe6e...` and selective Production `2b48a593...` histories were converged first with no tree delta at `82862b45...`.
- GitHub rollback branch `backup/pre-phase50-a2z-o1-catalog-controls-20260924` points exactly to the converged pre-feature baseline `82862b45...`.
- Product filters use `operator_stage_locks_json` and `sync_receipts` as the only status authority.
- `ready_7` requires seven locked stages and excludes clean already-uploaded products unless they have a new update/queue state.
- `ai_6` requires `ai_completed_once=1` and exactly six locked stages.
- `published` retains the established Site-sent identity contract.
- `instagram_posted` requires final `instagram_published` receipt.
- `instagram_story` requires final `instagram_story_published` receipt.
- UI now has independent Instagram Post and Instagram Story buttons.
- Feed-only never creates Story and is not blocked by Story mobile readiness.
- Story-only never creates Feed/Post; Direct provider fails closed and Buffer has an independent Story route.
- Buffer GitHub media host now accepts Story-only media without Feed derivatives.

## O1 verification
- Changed-condition filter test: 1/1 PASS.
- Focused Product/Social/Buffer: 24/24 PASS.
- Broader Product/Qt/Social regression: 136/136 PASS.
- py_compile, git diff --check, and Qt RUN_QT.ps1 -VerifyOnly: PASS.
- Canonical Catalog quick_check=ok.
- Real counts: ready_7=2; ai_6=19; published=14; instagram_posted=4; instagram_story=2.

## O1 safety
- No Product/Site data mutation.
- No real Instagram Post/Story was sent by tests.
- Production source `2b48a593...` was not changed.
- Destructive Crawl repair/delete are deferred to O3/O4.

## O1B implementation — LOCAL_TESTED
- Added Products display filters `آخرین ادیت‌شده‌ها` (`recently_edited`) and `اخیراً دیده‌شده‌ها` (`recently_viewed`).
- Recent edit authority is explicit Product history, not generic `products.updated_at`. Accepted operator-edit events are: `studio_save`, `epic49_studio_save`, `qt_operator_edit`, `qt_stage_edit`, `qt_profile_ledger_edit`, `qt_image_reordered`, and `content_edit`.
- AI/refetch/Site-sync/publish/auto-finalize/finalize/unlock-only events do not make a Product "recently edited".
- Added persisted `product_viewed` history only after `ProductWizardPage.load_product()` succeeds inside `MainWindow.open_product()`. Gallery render, selection, hover, search, scrolling and Source URL opening do not record a view.
- View tracking writes only `product_history`; Product row bytes including `updated_at`, `needs_update`, Site identity/revision and content remain unchanged.
- Both recent filters force newest-activity ordering and temporarily lock the Gallery sort control to "newest" so UI and query cannot disagree.
- No schema migration is required; the existing auditable `product_history` table is the persistence authority.
- Real Catalog read-only baseline: `quick_check=ok`; `recently_edited=523`; `recently_viewed=0` before first post-O1B real Editor open. No historical View rows are fabricated.
- Verification: focused O1B 7/7 PASS; broad Product/Qt/O1 regression 106/106 PASS before final sort-control UX; changed final O1B + Product/Page related 7/7 + 77/77 PASS; py_compile and diff-check PASS.

## O1 runtime acceptance
- Source commit `22bb0fb1ecca2f894e34bcbd7dda8b7d424b394e` is GitHub-exact.
- Pre-runtime Catalog backup quick_check=ok with 771 Products; SHA256 `6afd42e6d6fea4dc034f3b32361dc179b2ceedce3ec74703a6bf38c757ebb5a3`.
- Catalog Center was closed exactly once and relaunched from the pushed source SHA.
- Live main window title: `3DPrintHub Catalog Center v8.9.11 - Qt 6`.
- Post-restart Catalog quick_check=ok / Products=771.

## O1B runtime acceptance
- Source commit `a0d5ea4677410d3cac424aeb1779d7b1f827e1f7` is GitHub-exact.
- Final broad regression 106/106 PASS; Qt VerifyOnly, compile, Django check and no-migration-drift gates PASS.
- Fresh evidence root: `D:\projects\3dprinthub-backups\phase50-a2z-o1b-runtime-acceptance-20260924-125209`; backup/clone quick_check=ok with 771 Products, backup SHA256 `327f75d0368132036ca0cf80a221e6b714b6f454c635e394581a48c73c5a3c55`.
- Real cloned MainWindow/ProductWizard acceptance: #717 open -> one new `product_viewed`; Recently Viewed top=#717; Product row unchanged; Recent sort lock PASS.
- Canonical DB was not polluted by acceptance: recently_viewed remained 0 until the owner's first real Editor open.
- Visible runtime launched from exact source SHA; prior app process was already absent so no forced close was needed. Window title `3DPrintHub Catalog Center v8.9.11 - Qt 6`; Catalog quick_check=ok / 771 Products.

## O2 implementation — ACCEPTED
- One shared AcquisitionCore completeness contract now owns both filtering and card status.
- Complete means: mapped Product identity + title + description + at least one physically displayable local image.
- Exact incomplete reasons are: unmapped Product, missing title, missing description, and missing local/Preview image.
- Persistent Crawl inventory exposes Complete and Incomplete filters; complete cards show a positive marker and incomplete cards show exact reasons.
- Image truth remains filesystem-aware through shared ImageCore. A first-hit existence helper plus per-scan identity cache avoids full image enumeration during completeness scans.
- Real canonical Catalog: quick_check=ok; total Crawl=1099; complete=453; incomplete=646; partition invariant PASS.
- Performance: initial correct cold complete scan ~11.479s; optimized complete ~2.402s and incomplete ~3.464s with identical counts.
- Tests: baseline 36/36 PASS; focused O2/Crawl/Video 39/39 PASS; broader Crawl/Product/O1/O1B 128/128 PASS; compile, diff-check, Qt VerifyOnly, Django check and no-migration-drift PASS.
- No migration, Server delta, Product/Site mutation or Production deployment is required.

## O2 runtime acceptance
- Source commit `f04d5b05a9e0ad1310459da5a152da6be48d2c34` is GitHub-exact.
- Fresh rollback: `D:\projects\3dprinthub-backups\phase50-a2z-o2-runtime-acceptance-20260924-161214\catalog-before-o2-runtime.sqlite3`; quick_check and logical digest match passed; backup SHA256 `ca7b9ff29c70b741ac522146b8d79b23111b38bf569563283a05558c8a87356a`.
- The old runtime still had acquisition work in flight and created #779/#780/#781 before the O2 cutover. Their creation timestamps precede the 16:13:12 O2 restart; backup-vs-live diff found zero changes to pre-existing Product rows.
- The one intended restart was not repeated after an early five-second no-handle probe. The same process later exposed `3DPrintHub Catalog Center v8.9.11 - Qt 6` and remained healthy.
- Final runtime truth: quick_check=ok; Products=781; Crawl total=1099; complete=463; incomplete=636; partition invariant PASS.
- Real Complete and Incomplete UI smoke loaded 100 rows for each filter with the expected complete/missing-reason card text.
- Scoped Product/Crawl/History logical digest before and after the filter smoke stayed exactly `f9cd3201bbc97f3d85d1085b63efca0a500a8c44b3158c82137d82f07df911b8`; O2 filtering is read-only against canonical state.

## O2D implementation — ACCEPTED
- Products table already enforces unique `(source_code, external_id)` and `(source_code, normalized_url)`; real Catalog audit found zero duplicate groups for both keys and zero semantic Source-pattern ID duplicate groups. Therefore no Product row was deleted merely because titles look alike.
- `Database.add_discovered()` now rejects any already-existing Product identity, not only blocked identities.
- Add Products persistent queue/count/page and queue summary exclude identities that already exist in Products while retaining the discovery ledger row as anti-recrawl memory.
- Batch listing pending queries exclude existing Product identities; legacy `new/failed` ledger rows cannot re-enter Product fetch.
- Listing Preview discovery skips existing Product identities before candidate upsert/thumbnail caching, so existing Products are not re-previewed as new candidates.
- `terminal_identity_state()` returns `collected` for an active existing Product; explicit `force_recover` remains the only recovery/update path for an existing Product.
- Live Add candidate rows exclude Product identities by both external ID and normalized URL.
- Products table/detail expose the canonical Source Identity `source_code:external_id`; no new identity column/schema is created.
- O2 completeness is redefined correctly for unconsumed Add candidates: complete/ready-to-add means Candidate title + physically available local Preview. Existing Products are not part of this inventory.
- Final real Catalog read-only audit: Products=790, discovery ledger=1115, consumed hidden=650, unconsumed visible=465, complete/ready-to-add=47, incomplete=418, queue summary=465, visible mapped Products=0.
- Exact duplicate audit: external identity groups=0, normalized URL groups=0, semantic Source-pattern ID groups=0. No destructive dedup was warranted.
- Final scoped real Catalog digest before/after audit remained identical: `82a8a906cb4d0d0059dfdf2088cba5457b44116b9c2f6d36e5daa37de4b6c300`.
- Verification: O2D identity/batch/preview changed-condition contracts PASS; focused 51/51 PASS; final broad identity/Crawl/acquisition/Product regression 131/131 PASS; py_compile/compileall, Qt VerifyOnly, Django check, makemigrations --check --dry-run and diff-check PASS.
- Initial Django check without the isolated worktree `.env` failed with the already-known ERR-49-155 environment mismatch; rerun used the documented temporary canonical ignored `.env` copy and removed it immediately. No secret was logged or committed.
- Windows/Catalog-only delta; no Server migration or Production deploy is required.

## O2D runtime acceptance
- Core source commit `4589500029cc7670ac2f060c798221fe3754feac` and final identity-suppression hardening `4e667f4f49358076b288bb8c8f6982b8a2b20bca` are GitHub-exact.
- Before cutover, Automatic acquisition was allowed to quiesce safely: run #46 completed naturally and run #50 was stopped through the official application stop control; no process kill was used for acquisition.
- Fresh rollback: `D:\projects\3dprinthub-backups\phase50-a2z-o2d-runtime-acceptance-20260924-182115\catalog-before-o2d-runtime.sqlite3`; quick_check=ok and source/backup logical digest match at `870c0286f998eec21fcfea3728b5a3c924cf4e1c4791d353ebcb9a570f2339c3`; backup SHA256 `fb01aaab1253851e83e869d3ba012fbab9f9aee8718ffea30fd3a42dc293339e`.
- Exact-SHA Catalog Center runtime is visible as `3DPrintHub Catalog Center v8.9.11 - Qt 6`.
- Final runtime truth: Products=847; raw Crawl=1192; consumed hidden=707; Add Products visible=485; ready-to-add=50; incomplete=435; visible mapped Products=0; queue summary total=485.
- Canonical duplicate groups remain zero for `(source_code, external_id)` and normalized URL. Product table visibly exposes canonical identity such as `makerworld:1298362`.
- Runtime Add Products smoke loaded 100 rows with mapped=0. Before/after Product/Crawl/History digest remained exactly `870c0286f998eec21fcfea3728b5a3c924cf4e1c4791d353ebcb9a570f2339c3`; acceptance caused no canonical mutation.

## O2E implementation — ACCEPTED
- One selected-media authority now spans Product Editor and Social: `selected_images_json` plus exact files contained in the current Product `local_dir`.
- Normal Product Gallery excludes historical/refetch sibling folders. Trusted unregistered files physically inside the current Product folder remain visible for operator selection, but do not become Social authority until persisted.
- Selected Product cards use the same exact finalized Local file resolver used by Social.
- Product Wizard Refresh is local-truth/compare-only and no longer injects Site media into Product DB; explicit Source recovery remains separate.
- Social public media is aligned one-to-one to selected Local images by SEO/final basename or finalized SHA path and fails closed on stale/missing/ambiguous ACK media.
- Truth Sync reports selected-local count and SHA/mapping errors.
- Tests: initial direct baseline 10/10; initial O2E changed/direct 14/14; fixture/legacy-contract 20/20; first broad 99/99 PASS. After real #625 runtime exposed ERR-49-246 and #628 Refresh exposed ERR-49-247, final dedicated regressions + focused 16/16 + direct Instagram publish 13/13 + expanded Image/Product/Social 131/131 PASS; continuation related rerun 74/74 PASS; compileall, Qt VerifyOnly, Django check, no migration drift and diff-check PASS.
- Real read-only audit: 543 Products have selected images; 93 exact selected-local mappings PASS; 450 legacy Products lack exact Local files and were not bulk-mutated. #625 and #628 exact selected Local/Social parity PASS. Audit digest unchanged at `1129de23233309efd5412f7d47ab286885bfa737586267459d97e68374c85a24`.
- Windows/Catalog-only delta; no Server migration or Production deploy is required.
- Final corrective source is GitHub-exact at `544e046b62f933e5461d57e9491a5ecee46c5225`.
- Final rollback `D:\projects\3dprinthub-backups\phase50-a2z-o2e-final-runtime-acceptance-20260924-201040\catalog-before-o2e-final-runtime.sqlite3`: source/backup quick_check=ok, logical digest exact `cf21d5ec4605dac1d744f636f438b7a98e625ba8e88982e52466e147d045e890`, Products=852 / History=3482 / Crawl=1192, backup SHA256 `34fb39594839ef0bfe936f4c88da7ab48b7bd3571220a6991e929355e71da5d9`.
- Acquisition was quiescent before cutover. Old Qt closed via `CloseMainWindow()` without kill; exact-SHA VerifyOnly PASS; one visible runtime launched as PID 52840.
- Real #625: selected DB=1 / ProductWizard selected card=1 / Refresh selected-local=1 / Site=1 / mismatches=0 / Social exact SHA prefix `30f41e1d56f5`.
- Real #628: selected DB=2 / ProductWizard selected cards=2 / Refresh selected-local=2 / Site=2 / mismatches=0 / Social exact SHA prefixes `959abcdd95d6`, `6138e2b6907d`.
- Direct ProductWizard UI smoke matched `image_grid.selected_urls()` and primary image for both targets; target Product+History digest remained exact at `85d1e5686e1f2dbc8b8c5aea3b6b01188dda5824d726296cc96a2ec5a5bb7fb6`.

## O2G implementation — ACCEPTED
- Requested count is the authoritative search target at 1..500. Progressive Preview/Browser depth is derived from that target instead of a fixed eight-scroll window.
- The existing 3I.38 `crawl_listing_state` remains the persisted continuation/depth authority; O2G does not introduce a second cursor.
- O2D terminal/consumed Product identities never count toward new target progress.
- MakerWorld Hybrid first respects HTTP/robots/rate behavior, then prefers the existing dedicated Chrome 9222 session. HTTP 403/429 is not listing exhaustion.
- Attached discovery scans a bounded 3000-link window with locator-safe href reads and `include_preview=False`; no `evaluate_all` is introduced into the hardened boundary.
- Persistence is capped to `requested - current_pending` in both attached and classic paths so a 200 request cannot over-enqueue the whole visible link window.
- Verified exhaustion requires stable cumulative listing size at deeper probes; zero-new alone is insufficient because all exposed rows may simply be O2D-consumed Products.
- Section A of Add/Crawl has clearer spacing/minimum widths/column stretch and one receive-options row. Section B has one horizontal six-button toolbar instead of the prior 3+3 stack.
- Real Source proof used an isolated SQLite clone from the canonical Catalog. Before probe the real `https://makerworld.com/en/search/models?keyword=Lamp` listing had 15 ledger rows and zero unconsumed pending. HTTP returned 403; Chrome 9222 then reached scroll depth 48, observed 397 links and persisted exactly 200 new candidates. Final clone: 215 listing rows, pending=200, target_reached=true, exhausted=false, quick_check=ok.
- The first clone-only probe found the target but persisted 313 candidates because the target gate was after the whole candidate loop. This was corrected before acceptance by capping persistence to the remaining target and locked by focused tests.
- Related broad regression also exposed the pre-existing over-escaped Preview JS newline sequence; it was corrected from the wrong double-backslash runtime text to the tested single escaped newline source contract.
- Verification: focused 49/49 PASS; Preview 3/3 PASS; related Crawl/O2/O2D 98/98 PASS; py_compile/compileall, diff-check, Qt VerifyOnly, pip check, Django check, migration drift PASS.
- Fresh rollback before runtime: `D:\projects\3dprinthub-backups\phase50-a2z-o2g-runtime-acceptance-20260925-020653\catalog-before-o2g-runtime.sqlite3`; source/backup quick_check=ok, logical digest exact `8ae24e2f6c08c8340ad21f00baff3656bf28f046378b0e295b37e4b522c5a807`, Products=852 / History=3482 / Crawl=1192, backup SHA256 `c8f3f50907e636678be5e5bcc1fedaff0d59e16c55959775b49dd9c27d11c619`.
- Source/tests/docs checkpoint is GitHub-exact at `436bca68a2ee30ed80cc262456a143099c9d5586`; Local=Remote and worktree clean before runtime acceptance.
- Exact-SHA VerifyOnly PASS immediately before launch. No prior Catalog Qt process was running; one launch produced visible `3DPrintHub Catalog Center v8.9.11 - Qt 6` PID 54404.
- Exact-source Qt render smoke on an isolated rollback clone verified requested range 1..500, one horizontal receive-options row under section A, one six-button action row under section B, and no legacy second action row.
- Post-launch canonical Catalog quick_check=ok; Products=852 / History=3482 / Crawl=1192; full logical digest remains exactly `8ae24e2f6c08c8340ad21f00baff3656bf28f046378b0e295b37e4b522c5a807`. Runtime/UI acceptance caused zero Catalog mutation.
- Production changed = NO; migration changed = NO; canonical Product/Site/Social data mutated by real-source probe or runtime acceptance = NO.

## O2H implementation — LOCAL_TESTED
- Reject and Delete are now separate operator contracts in both persistent Crawl inventory and current-search results. Reject remains status-only and reversible through Restore.
- Explicit hard-delete removes only an unconsumed `discovered_urls` identity plus matching `phase49_3i_discovery_candidates`, canonical Preview cache and bounded current-data-root identity folders (`<external>`, refresh/refetch/bulk-refetch variants).
- Product authority is resolved before any deletion by both Source+external ID and Source+normalized URL. Any matching Product fails closed; Product rows/files are never passed to the Crawl deletion path.
- Destructive path is bounded to the current Catalog data root. The legacy compatibility read root is never traversed as a deletion target.
- Qt confirmation explains destructive/non-restorable semantics and reports Product-blocked/error counts instead of silently deleting.
- Changed-condition O2H tests: 5/5 PASS. Related O2/O2D/Crawl/Acquisition/Preview regression: 68/68 PASS. py_compile/compileall, pip check, Qt VerifyOnly, git diff-check, Django check and migration drift PASS; known CKEditor warning only.
- Fresh rollback: `D:\projects\3dprinthub-backups\phase50-a2z-o2h-runtime-acceptance-20260925-095729\catalog-before-o2h-runtime.sqlite3`; source/backup quick_check=ok; Products=852 / History=3482 / Crawl=1192 / Candidates=647; four-table digest `e2993bc95b5fcb89dd67f458156877d469ee4653956095ddcf755f94e641b952`; backup SHA256 `819441eb384a798aa07a897a3cc357c396e15381885972e9ce014be6308c1bbc`.
- Production changed = NO; Server/migration delta = NO.

## Exact next
Commit/push O2H source/tests/checkpoint docs -> Local=Remote -> exact-SHA isolated-clone acceptance using a real failed unconsumed MakerWorld identity and a real Product-backed identity -> verify exact bounded deletion/no-collateral + canonical no-mutation digest -> exact-SHA Qt render/launch smoke -> closure docs. Then O2F Instagram all-media/disclosure/source+order links/Story-link capability -> O3 guarded deep reset/refetch/remap. O4 Delete semantics follows after O3.
