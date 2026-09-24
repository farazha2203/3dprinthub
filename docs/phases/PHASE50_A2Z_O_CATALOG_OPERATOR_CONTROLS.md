# Phase50.A.2Z-O - Catalog Operator Controls + Crawl Recovery

Status: O1_ACCEPTED / O1B_ACCEPTED / O2_NEXT
Date: 2026-09-24
Branch: `wip/phase50-a2z-o1b-recent-activity-20260924`
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

## Exact next
O2 Crawl Completeness Views -> freeze one factual complete/incomplete contract -> filters -> exact per-card missing reasons -> focused/related regression -> Catalog integrity -> commit/push -> exact-SHA runtime acceptance. O3 guarded deep reset/refetch/remap follows.
