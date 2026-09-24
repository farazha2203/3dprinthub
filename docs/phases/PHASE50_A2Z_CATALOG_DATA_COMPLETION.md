# Phase50.A.2Z — Catalog Data Completion + Site Truth

Status: PRODUCTION_FIX_DEPLOYED / PRODUCT_628_ROOT_CAUSE_TRACE_ACTIVE
Date: 2026-09-23
Baseline: `56c569145eead7cd0a35eb63c382f14dfe71c80e`
Branch: `wip/phase50-a2z-catalog-data-completion-20260923`

## Objective
Close Catalog/Site truth without duplicate Product identities or silent operator-data loss. Incomplete Crawl Products stay visible and can safely recover the same identity. Same-identity Site republish must replace current media/Profile/Variant/pricing state while preserving Product identity and explicit Slider membership.

## Verified current truth
- Catalog quick_check=ok; current inventory is 771 Products, not the older documented 635.
- Six-field Slider completeness: 61 complete / 710 incomplete; 13 memberships enabled and exactly one enabled Product (#40) lacks a Slider image.
- #152 = Site #50 / Hero #2 rev3; Local clean; Site truth matches accepted revision.
- #178 = Site #51 / Hero #4 rev6; Local clean; Site truth matches accepted revision.
- #620 = Site #41 / Hero #17 rev1; already public/clean; Slider fields currently complete and membership enabled.
- #625 = Site #39; Local rev11/needs_update=1 while Site profile rev12. Receipt #316 proves rev12 came from exact local Batch `26aa571c...` with status `publish_incomplete`.
- #628 = Site #38 rev1; Local needs_update=1 and factual publish preflight passes.

## Implemented source slice
- Crawl inventory label makes incomplete visibility explicit.
- Incomplete Product cards show actionable missing-data reasons.
- Selected collected Products are not skipped when incomplete; canonical same-identity recovery runs with force/adaptive fallback.
- Complete collected Products remain no-refetch/idempotent.
- Selected-row completeness falls back read-only to canonical Product facts when the bounded queue query only carries Product ID.
- Product revision guard can reconcile revision-only from an exact matching local `publish_incomplete` receipt; Product/media/Profile/Slider data are never pulled or overwritten by this reconciliation.
- Unknown or mismatching Site revision remains fail-closed and still requires Site Pull/review.
- Canonical motion authority remains `video_links_json / selected_video_links_json / local_video_files_json`; obsolete dirty precursor video authority was not ported.

## Verification
- Baseline Crawl/V84 40/40 and Video 8/8 PASS before changes.
- Changed Crawl/V84 41/41 and Video 8/8 PASS.
- Revision-only reconciliation targeted 4/4 PASS.
- Final related Catalog/Profile/Filament/Image/Slider/Site regression 153/153 PASS.
- Server related regression 12/12 PASS; Django check PASS; migration drift none.
- Python compile, git diff-check and Qt VerifyOnly PASS before final docs checkpoint.
- Fresh pre-mutation Catalog rollback: `D:\projects\3dprinthub-backups\phase50-a2z-data-completion-pre-mutation-20260923-202714\catalog-before-a2z-data-completion.sqlite3`; source+backup quick_check=ok, both 771 Products.

## Remaining ordered gates
1. Commit/push this Local-tested source/docs and verify Local=GitHub exact SHA.
2. Relaunch Qt from exact pushed SHA.
3. Reconcile #625 revision 11→12 through receipt proof only; verify operator-owned digest unchanged.
4. Real operator acceptance for #620/#625/#628; preserve #620 clean state and #625/#628 Profile/Filament/Image facts.
5. Mark #628 Ready only after exact-SHA gate; publish no broad queue.
6. Fresh rollback immediately before each Production-affecting republish.
7. Controlled same-identity republish, strict ACK replacement parity, public Product/media/Profile/Variant/Slider verification.
8. Real Desktop/Mobile browser acceptance.
9. Update CURRENT_STATE/ROADMAP/CHANGELOG/ERRORS and close only after all gates PASS.

## Exact-SHA local acceptance extension
- GitHub-exact source: fde86e23ba6b0a1d5f578279289328708184baf9; Qt launched from this SHA.
- #625 revision-only reconcile 11->12 PASS from receipt #316; operator-owned digest unchanged.
- #625 Ready refresh preserves 5x5x5 + 4x4x4 profiles, 16 PLA each, selected media and 458500-1655000 range.
- #628 Ready PASS: 12x12x12 / 18x18x18, 16 PLA each, two selected Local-backed images; current pricing refreshed to 3063500-6479000.
- Post-local rollback: phase50-a2z-post-local-gates-20260923-215515, quick_check=ok, SHA256 1c5b0439...848e8.
- Production write remains blocked because official Windows loopback 22024 is down. No Production DB/media rollback can be verified until the documented PrintHub tunnel is restored.

## 2026-09-24 final closure checkpoint
- Dedicated reverse tunnel recovered and authenticated; Production read-only gate passed on clean `103f559c8a11c35495b4ac2a290d578c31c2a023`.
- #625 was published alone after verified DB+full-media rollback. Site Product #39 is revision 13; strict parity/public media checks pass; one ProductImage and 32 active Variants remain current.
- #628 has verified prepublish rollback `20260923-230201-a2z-628-prepublish`. First bounded import failed rollback-safe on a Unicode media basename and Site revision remained 1.
- Shared Server/Public filename contract is implemented at `b5980306400f3f0951804cab1ad049c1aab4a6d7`: ASCII names remain unchanged; non-ASCII names become deterministic factual-source ASCII names only at Server/Public storage. Windows SEO metadata/ALT/caption/SHA are preserved; importer/Product/Portfolio/parity share the same contract.
- Verification PASS: Unicode 1/1, unified import 5/5, related visibility/profile/video 21/21, py_compile, Django check, migration drift none, diff-check.
- Selective release is GitHub-exact at `2b48a593ace2e9a3703fa0f52b4c3c13b2751cf9`, parent exactly `103f559c...`, with only the five verified Server/test files. Guarded ops runner `scripts/host/phase50_a2z_unicode_media_deploy.sh` is Local syntax/diff tested and remains outside the release runtime branch.
- Fresh predeploy rollback: `/home/sfkilvrs/3dprinthub-deploy-backups/20260924-104824-a2z-unicode-media-predeploy`; source bundle, .env, MySQL gzip and full media tar checksum verification PASS.
- Remaining gates: commit/push ops runner -> execute GitHub-first reverse-tunnel deploy -> receiver verify -> retry only #628 -> strict Site/Public parity -> collateral readback -> Desktop/Mobile acceptance -> CLOSED.
