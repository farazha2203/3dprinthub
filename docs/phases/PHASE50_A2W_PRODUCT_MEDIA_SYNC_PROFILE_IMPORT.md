# Phase50.A.2W — Product Media Truth Sync + Source Profile Import

Status: **LOCAL_TESTED — W1/W2 REAL #625 TRUTH SYNC PASS / GITHUB NEXT**
Date: 2026-09-21
Parent baseline: Phase50.A.2V `PRODUCTION_VERIFIED`

## Owner request
The Windows Product Wizard can show more local media than the live Site Product, so the operator needs one explicit refresh that proves Local DB, Local files, Site Product media and source media separately. Re-publish must replace the live Product image set with the exact persisted `ارسال سایت` selection, including newly added screenshots/images and removal of stale Site images.

The same phase also records follow-up work for source videos, factual source Print Profile import, material-family mapping and manual self-produced Products. Only W1/W2 are active in this first deliverable.

## Baseline / safety
- Branch starts from clean A2V closure `346baa135c62ff58a6596a80433678ebd622206b`.
- Rollback ref: `backup/pre-phase50-a2w-product-media-sync-20260921`.
- Canonical Catalog DB: `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`.
- Existing `ارسال سایت` selection remains the only Site Product media membership authority.
- Visible local files are review candidates only; refresh must never silently select every visible image.
- No Production source edit, migration or destructive media operation is permitted by W1/W2.
## W1 — Product Media Truth Sync
The Stage-3 action `رفرش رسانه و وضعیت` must produce one structured truth snapshot for the current Product:
- canonical Local DB media count (`images_json`);
- persisted Site-selected count (`selected_images_json`);
- locally displayable file count;
- current live Site Product image count and main image through the authenticated Bridge;
- source-page image-link count already known locally;
- authority/missing-file/primary mismatches.

When a live Site Product exposes media not represented by the Local Product, refresh may download those public Site bytes into the Product trusted local image directory as recoverable candidates. It must be idempotent, checksum-aware and must not silently change Local `ارسال سایت` membership.

If Local has unpublished changes, Site revision/content must not overwrite Local editorial state. W1 is media truth/recovery, not a hidden Site pull.

## W2 — Authoritative Media Update
Before a Product is marked ready or published:
- pending Stage-3 Site-selection UI must be persisted;
- selected media must be a subset of canonical media;
- Primary must be selected;
- every selected image must have current finalized SEO WebP metadata/bytes;
- the exact selected order must be what enters the Batch.

Site import already rebuilds desktop-managed `ProductImage` rows from the current batch. A2W must add regression proof that adding, removing and reordering selected images produces exact replacement rather than additive stale media.
After successful publish, the current Site media count must agree with the Batch/ACK selected-media count; a mismatch is a verification failure, not a success.

## W3 — Source Print Profile Import (planned)
Add `دریافت پروفایل از محصول` to Stage 2. Parse only factual source-profile evidence such as profile name, plate count, print time, weight, nozzle/layer facts and material hints. Multiple source profiles must remain separate Local Profiles.

The owner-provided #625 example contains at least a Single Color and a Multicolor source profile; extraction must not collapse them into one default profile.

## W4 — Smart material-family mapping (planned)
A factual source material hint such as PLA maps to all compatible Local PLA offers for operator review. Brand/manufacturer/color are never invented when the source does not establish them.

## W5 — Manual Product creation (planned)
Add a first-class manual/self-produced Product flow with operator title/notes/media, optional video and normal Profile/Filament controls. AI may generate SEO/content from operator-provided description and images, but must not invent technical production facts.

## Future media extension (planned)
Source video discovery/download, Site Product video presentation and Instagram video/Reel handoff are tracked here but are not part of W1/W2 acceptance.

## W1/W2 acceptance gates
- [x] Focused Qt/Image/Site-sync regression 49/49 PASS.
- [x] Existing A2V Image/SEO/Packaging/Republish + bidirectional Site sync + A2W regression 83/83 PASS.
- [x] `git diff --check`, Python compile and `RUN_QT.ps1 -VerifyOnly` PASS.
- [x] Fresh pre-Truth-Sync SQLite backup integrity PASS with SHA256 recorded.
- [x] Product #625 real Truth Sync reports Local/Site truth without another publish: DB=2, Local=3, `ارسال سایت`=1, Site=1, mismatch=0, recovery=0.
- [x] Product #625 Site identity/revision/selection/Primary/dirty state unchanged by Truth Sync.
- [x] Production receiver inspected read-only and already enforces exact media count + filename/SHA parity; no Host source deploy is needed for W1/W2.
- [ ] Commit/push exact A2W SHA and verify remote SHA.
- [ ] Launch exact pushed SHA on Windows and smoke the Stage-3 `رفرش رسانه و وضعیت` button on #625.

## Real #625 evidence
Backup: `D:\projects\3dprinthub-backups\phase50-a2w-pre-truth-sync-20260921-093455\catalog-before-a2w-truth-sync.sqlite3`; integrity `ok`; SHA256 `0470eb8d64573b7e252756d2bb9f449ddd2b08b6f50e1eb39e39343b704320cb`.

Before and after Truth Sync, #625 remains Site Product #39 revision 11, `workflow_status=uploaded`, `needs_update=0`, `upload_ready=0`, selected/Primary=`local://04.webp`. Canonical DB media are `local://04.webp` plus the source-page screenshot; the gallery resolves three local files, but only one is Site-authoritative. Live Site media count is exactly one and maps to the existing finalized `04.webp` SEO derivative, so no recovery candidate was needed.

## Next exact task
Commit/push the tested W1/W2 delta, verify GitHub exact SHA, relaunch Qt only from that SHA, smoke the new Stage-3 button on #625 without publishing, then mark W1/W2 runtime accepted and begin W3 factual source Profile import.
