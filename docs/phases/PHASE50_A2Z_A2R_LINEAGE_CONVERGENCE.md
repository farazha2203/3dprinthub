# Phase50.A.2Z-LC — A2Z / A2R Lineage Convergence

Status: LOCAL_TESTED / GITHUB PENDING
Date: 2026-09-23
Forward baseline: `3de2af09f25458a3d94904dac50818f97091a8cd`
Windows A2R heads: `d6799cc1...` + `03808add...`
Production selective A2R head: `103f559c8a11c35495b4ac2a290d578c31c2a023`
Worktree: `D:\projects\3DPrintHub-a2z-a2r-converge`
Branch: `wip/phase50-a2z-a2r-lineage-convergence-20260923`

## Reason

A2Y previously converged Windows and Server into one forward baseline, but the 2026-09-23
A2R motion-media work was later split again: Windows acquisition/social handoff advanced
on the old WIP branch while Production received a selective Server commit.

Per AGENTS.md, A2Z feature work cannot continue on divergent accepted lineages.
The dirty A2Z Data Completion worktree is therefore preserved unchanged while this
clean micro-convergence carries only evidence-backed A2R deltas into the newest A2Z head.

## Safety boundaries

- No reset/delete of the dirty A2Z worktree.
- Dirty rollback patch is stored under `pre-a2z-lineage-convergence-20260923-1821`.
- No Catalog mutation is part of source convergence.
- No Social provider mutation/repost is part of source convergence.
- No DB migration/dependency change is introduced.
- Production already runs the selective Server motion-media support at `103f559c...`.
## Converged authority

- Canonical Catalog motion fields are `video_links_json`,
  `selected_video_links_json`, and `local_video_files_json`.
- MakerWorld animated `GIF_*.gif` media is treated as motion media in addition to
  normal MP4/WebM/MOV/M4V sources.
- Explicit Product video download refreshes the canonical Source, stays bounded to
  the Product/provider CDN boundary, writes Product-owned Local media and does not
  publish automatically.
- Safe Source re-crawl can discover new video links but preserves operator-selected
  video/local media authority.
- Site Batch copies only Product-owned motion files with checksum/size/type gates.
- Server imports Product motion media to public storage and renders it on Product detail.
- Public verification treats Product images and motion media separately.
- Canonical Social payload records public Site video metadata, but current Buffer Feed
  remains image-based; this phase does not claim Reel/video publishing.

## Local verification

- Catalog A2R video: 8/8 PASS.
- Social v5/Story/Buffer regression: 41/41 PASS.
- Crawl + v8.4 changed-condition regression: 40/40 PASS.
- Publish/Bridge/Social regression: 55/55 PASS.
- Django Server motion/detail/variant regression: 12/12 PASS.
- Django check PASS; migration drift: none.
- Python compile PASS.
- `git diff --check` PASS.
- Host runner `bash -n` PASS.
- Qt `RUN_QT.ps1 -VerifyOnly` PASS.

## Changed-condition failure

The first Crawl regression had one stale UI assertion expecting the historical button
label «دریافت داده و عکس بیشتر از لینک محصول». Current accepted A2Z UI already uses
«دریافت جدید از منبع». Runtime was not rolled back; only the stale assertion was aligned,
then the same scope passed 40/40.
## Production truth at convergence start

Production Host is clean on `103f559c...`.
Verified: MySQL identity, empty migration plan, publish readiness=true, Home=200,
Store=200, valid scoped source/env + full MySQL rollback backup.

Product #536 already has Site Product #48 revision 2 with public GIF motion media HTTP 200.
No duplicate Site publish or Social send is required by this convergence phase.

## Exit gate

1. Commit/push the runtime-bearing convergence source and verify Local=GitHub.
2. Update CURRENT_STATE/ROADMAP/CHANGELOG/ERRORS/REQUESTS with the exact source SHA.
3. Audit unified-head vs current Production delta read-only.
4. Do not deploy unless that audit proves a required Server delta beyond the already-live
   `103f559c...` behavior.
5. Resume A2Z Catalog Data Completion only from the accepted unified forward head.

## Exact next phase after closure

Phase50.A.2Z — Catalog Data Completion:
incomplete-product truth -> safe URL re-crawl -> canonical video UI -> Slider completeness
with membership preserved -> #620/#625/#628 operator acceptance -> Profile/Filament/Image
gates -> one backup-backed same-identity republish -> public/browser parity.

Immediately following: A2Z-S changed-revision Social rollout, then W5 manual Product.
