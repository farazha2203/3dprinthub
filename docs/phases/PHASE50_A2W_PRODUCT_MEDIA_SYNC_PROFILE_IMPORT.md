# Phase50.A.2W — Product Media Truth Sync + Source Profile Import

Status: **W1/W2 WINDOWS_RUNTIME_ACCEPTED — W3 LOCAL_TESTED / GITHUB NEXT**
Date: 2026-09-21
Parent baseline: Phase50.A.2V `PRODUCTION_VERIFIED`

## Owner request
The Windows Product Wizard can show more local media than the live Site Product, so the operator needs one explicit refresh that proves Local DB, Local files, Site Product media and source media separately. Re-publish must replace the live Product image set with the exact persisted `ارسال سایت` selection, including newly added screenshots/images and removal of stale Site images.

The same phase also records follow-up work for source videos, factual source Print Profile import, material-family mapping and manual self-produced Products. W1/W2 are runtime-accepted; W3 is the current Local-tested deliverable.

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

## W3 — Source Print Profile Import (LOCAL_TESTED)
Stage 2 now has `دریافت پروفایل از محصول`. MakerWorld `__NEXT_DATA__` is parsed deterministically into existing `source_print_profiles_json`; AI is not used. Multiple source Profiles remain separate, exact seconds/fractional minutes are retained in Source facts, and factual material/color/nozzle/layer evidence is preserved without inventing Brand or local price.

#625 evidence is exact: Single Color instance 3609481/profile 943581967 = 4814s / 13g / PLA #FECC66; Multicolor instance 3609488/profile 943610448 = 15748s / 50g / PLA 11g #804003 + 39g #FECC66. Both are A1/N2S, nozzle 0.4mm, layer 0.16mm, walls 2, infill 5%. Current integer Sales Ledger maps factual time to nearest minute 80/262.

Source refresh only updates source-fact authority. Explicit Ledger import uses deterministic `source-mw-<instance>` keys, preserves all non-source/manual Profiles and is idempotent. Commerce import is fail-closed while Stage 2 is locked; W4 remains responsible for mapping factual PLA/color hints to real Local Filament offers/pricing.

W3 verification: focused 5/5 PASS; corrected retained A2V/W1/W2/bidirectional 83/83 PASS; py_compile/diff-check/RUN_QT VerifyOnly PASS. Fresh pre-real-W3 rollback is `phase50-a2w-w3-pre-real-625-20260921-102142`, SHA256 `ba7d70b04cf5b084bd7922bd0f93f321a55cc4c7c241795f32c6840235764401`.

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
- [x] Commit/push exact A2W SHA `ab1e9d1051aba6ff12a8b3c8b1f9bf04fb22be17` and verify remote SHA exact match.
- [x] Launch exact pushed SHA on Windows and smoke the Stage-3 `رفرش رسانه و وضعیت` button on #625; real Qt button click PASS.

## Real #625 evidence
Backup: `D:\projects\3dprinthub-backups\phase50-a2w-pre-truth-sync-20260921-093455\catalog-before-a2w-truth-sync.sqlite3`; integrity `ok`; SHA256 `0470eb8d64573b7e252756d2bb9f449ddd2b08b6f50e1eb39e39343b704320cb`.

Before and after Truth Sync, #625 remains Site Product #39 revision 11, `workflow_status=uploaded`, `needs_update=0`, `upload_ready=0`, selected/Primary=`local://04.webp`. Canonical DB media are `local://04.webp` plus the source-page screenshot; the gallery resolves three local files, but only one is Site-authoritative. Live Site media count is exactly one and maps to the existing finalized `04.webp` SEO derivative, so no recovery candidate was needed.

## W3 acceptance gates
- [x] Exact #625 MakerWorld evidence proves two distinct factual Source Profiles.
- [x] Source parser/extractor persists multiple Profiles to `source_print_profiles_json` without AI/inference.
- [x] Manual Sales Ledger remains unchanged by Source refresh; explicit import is deterministic/idempotent and preserves manual Profiles.
- [x] W3 focused 5/5 PASS.
- [x] Correct retained W1/W2/A2V/bidirectional gate 83/83 PASS.
- [x] py_compile / diff-check / RUN_QT VerifyOnly PASS.
- [x] Fresh pre-real-W3 Catalog backup integrity PASS with SHA256 recorded.
- [ ] Commit/push W3 and verify remote exact SHA.
- [ ] Exact-SHA Qt real #625 Source Profile fetch smoke: exactly two facts, no FTP/Bridge publish, Site Product #39 revision 11 unchanged.
- [ ] Controlled Commerce unlock + import after Source smoke; preserve existing manual Profile and create exactly two source Profiles, no duplicates.

## Next exact task
Commit/push the tested W3 delta, verify GitHub exact SHA, relaunch Qt only from that SHA, execute real #625 `دریافت پروفایل از محصول` without publish, verify the two factual Source Profiles and unchanged Site identity, then perform controlled Commerce unlock/import only if that smoke passes.
