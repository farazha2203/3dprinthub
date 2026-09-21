# Phase50.A.2W — Product Media Truth Sync + Source Profile Import

Status: **W1/W2/W3/W4 WINDOWS_RUNTIME_ACCEPTED — W4.1 REAL_DATA_PATCHED / A2X ACTIVE**
Date: 2026-09-21
Parent baseline: Phase50.A.2V `PRODUCTION_VERIFIED`

## Owner request
The Windows Product Wizard can show more local media than the live Site Product, so the operator needs one explicit refresh that proves Local DB, Local files, Site Product media and source media separately. Re-publish must replace the live Product image set with the exact persisted `ارسال سایت` selection, including newly added screenshots/images and removal of stale Site images.

The same phase also records follow-up work for source videos, factual source Print Profile import, material-family mapping and manual self-produced Products. W1/W2/W3/W4 are runtime-accepted; W4.1 is real-data patched on #628/#625 at exact pushed source `7f2280eafe7a3293008a6dc7a4559b0ef92f114c`. A2X now owns Slider completeness and authoritative re-publish acceptance.

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

## W3 — Source Print Profile Import (WINDOWS_RUNTIME_ACCEPTED)
Stage 2 now has `دریافت پروفایل از محصول`. MakerWorld `__NEXT_DATA__` is parsed deterministically into existing `source_print_profiles_json`; AI is not used. Multiple source Profiles remain separate, exact seconds/fractional minutes are retained in Source facts, and factual material/color/nozzle/layer evidence is preserved without inventing Brand or local price.

#625 evidence is exact: Single Color instance 3609481/profile 943581967 = 4814s / 13g / PLA #FECC66; Multicolor instance 3609488/profile 943610448 = 15748s / 50g / PLA 11g #804003 + 39g #FECC66. Both are A1/N2S, nozzle 0.4mm, layer 0.16mm, walls 2, infill 5%. Current integer Sales Ledger maps factual time to nearest minute 80/262.

Source refresh only updates source-fact authority. Explicit Ledger import uses deterministic `source-mw-<instance>` keys, preserves all non-source/manual Profiles and is idempotent. Commerce import is fail-closed while Stage 2 is locked; W4 remains responsible for mapping factual PLA/color hints to real Local Filament offers/pricing.

W3 verification: focused 5/5 PASS; corrected retained A2V/W1/W2/bidirectional 83/83 PASS; py_compile/diff-check/RUN_QT VerifyOnly PASS. Fresh pre-real-W3 rollback is `phase50-a2w-w3-pre-real-625-20260921-102142`, SHA256 `ba7d70b04cf5b084bd7922bd0f93f321a55cc4c7c241795f32c6840235764401`.

## W4 — Smart material-family mapping (WINDOWS_RUNTIME_ACCEPTED)
W4 is intentionally read-only. Factual Source material slots map to compatible active Local Filament offers for operator review; no Source fact, Sales Ledger, Stage lock, Site identity or publish state is mutated by Preview.

Material-family matching is exact/case-insensitive. Color authority uses only explicit Local HEX/Palette values. Localized color names are never interpreted into a HEX value. Real Local inspection currently finds 16 active PLA offers, but neither #625 Source color `#FECC66` nor `#804003` has an exact Local HEX match; therefore exact HEX count must remain zero and no named color may be auto-selected.

The Multicolor Profile remains two simultaneous factual slots (11g `#804003` + 39g `#FECC66`) instead of being flattened into alternative `material_options`. W4 reports per-slot material cost and real Local pricing facts. For single-slot Profiles, full-price preview reuses the mature `formula_price_breakdown()` authority. No combined Multicolor Ledger price is fabricated before concrete Local offers are chosen.

Stage 2 exposes `W4 تطبیق Filament محلی` and a read-only review dialog. W4 focused regression 5/5 PASS; corrected mature Filament/Profile/Commerce + W3/W4 gate 49/49 PASS; retained media/site gate 83/83 PASS; py_compile/diff-check/RUN_QT VerifyOnly PASS. Rollback ref is `backup/pre-phase50-a2w-w4-material-mapping-20260921` at `eda42e84b0bf39052fb76aa3c74e35b7dd0a85e5`.

## W4.1 — Source Profile dimensions (LOCAL_TESTED)
W4.1 preserves factual dimensional evidence while applying the owner-approved operational Profile rule. MakerWorld Description text is parsed deterministically for labeled size/version dimensions and generic L×W×H values, normalized to cm, and attached to Source Profiles only when ordered size evidence and Profile counts match unambiguously. If exactly one factual dimension exists for a size, that numeric value is copied to all three operational Profile axes; the factual axis remains `source_description` and the derived axes are marked `owner_equal_dimension_rule`.

Real Hydra Product #628 / MakerWorld 3179519 exposes exactly:
- Profile 3595936 -> Small Version -> factual Height 120mm = 12cm -> operational size 12×12×12cm;
- Profile 3596024 -> Large Version -> factual Height 180mm = 18cm -> operational size 18×18×18cm.

The latest captured MakerWorld meta concatenates the second unit with the next numbered heading as `180 mm2. Support...`; the parser explicitly accepts this numbered-section boundary while retaining strict unit matching. Source provenance still records only Height as factual, while the owner rule supplies matching Length/Width operational values.

Owner-estimated fallback is separate provenance. For #625, existing Profile 1 5×5×5cm is preserved. Only still-missing axes on Profile 2 may receive the explicit owner-approved 4×4×4cm fallback, marked `owner_estimated`. Factual Source axes always win the same axis.

Material-family hydration is now part of operator-ready Source Profile creation/repair: if Source declares PLA, every active exact-family Local PLA offer is selected/added automatically. Real Catalog currently has 16 active PLA offers. Exact matching excludes PLA-CF/HT-PLA-GF/PETG; concrete operator Filament choices are preserved and brandless Source placeholders are removed once real Local offers exist. Reconciliation must preserve pricing, production weight/time, manual Profiles, Site Product identity/revision and publish state.

Local gates after owner correction: focused Source/Profile+dimension 15/15 PASS; W4 mapping 5/5 PASS; corrected Commerce/Profile + W3/W4/W4.1 59/59 PASS; retained media/site 83/83 PASS; py_compile/diff-check/RUN_QT VerifyOnly PASS. Real-Catalog read-only simulation proves #628 Small=12×12×12 + 16 PLA and Large=18×18×18 + 16 PLA; #625 Profile 1 remains 5×5×5 + 16 PLA and Profile 2 receives 16 PLA before its explicit 4×4×4 fallback. Owner-correction rollback ref: `backup/pre-phase50-a2w-w41-owner-dimension-filament-correction-20260921` -> `436d34f2e62532ea5890b44400d1d236ed3b53a1`.

### W4.1 acceptance gates
- [x] Exact/partial dimension parser with cm normalization and provenance.
- [x] Fail-closed ordered binding on count mismatch.
- [x] Owner equal-dimension rule: one factual Source dimension populates all three operational axes with explicit provenance; manual Profile full-dimension validation preserved.
- [x] Source=PLA automatically hydrates every active exact-family Local PLA offer; non-PLA families excluded and concrete operator choices preserved.
- [x] Profile repair preserves non-dimension commerce/production/Site fields.
- [x] Compact MakerWorld numbered-section regression.
- [x] Real Hydra latest-capture operational sizes 12×12×12 / 18×18×18 and real Local PLA count 16/16 proof.
- [x] Focused 15/15 + W4 mapping 5/5 + Commerce/Profile 59/59 + retained 83/83 + compile/diff/Qt VerifyOnly PASS.
- [x] Exact GitHub SHA push/readback: `7f2280eafe7a3293008a6dc7a4559b0ef92f114c`.
- [x] Integrity-checked post-repair Catalog snapshot: `phase50-a2w-w41-post-accept-20260921-152825\catalog-after-w41.sqlite3`, SHA256 `7743e63fba5d83b2991502ce320d21f7037a444dba0ef9bc2b240ad88c3ca8da`.
- [ ] Exact-SHA Qt runtime launch is superseded by the immediate A2X exact-SHA runtime gate and must be satisfied there before further real Product UI mutation.
- [x] Controlled real #628 patch: operational dimensions 12×12×12 / 18×18×18 + all 16 active Local PLA offers on both Source Profiles; read-only recheck confirms persisted state.
- [x] Controlled real #625 patch: Profile 1 remains 5×5×5, Profile 2 is owner-estimated 4×4×4, both with 16 active Local PLA offers; Site identity/revision remains preserved.

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
- [x] Commit/push W3 source `36dbf3cf283fc1e5697091549e930416c671cbe7` and verify remote exact SHA.
- [x] Exact-SHA Qt real #625 Source Profile fetch smoke: fresh MakerWorld capture, exactly two facts, no FTP/Bridge publish, Site Product #39 revision 11 and Sales Ledger unchanged.
- [x] Fresh pre-import backup integrity PASS: `phase50-a2w-w3-pre-ledger-import-20260921-103253`, SHA256 `bbf3614285b79da354505775a3750db57257a8ab790171a953168895443f055e`.
- [x] Controlled StageCore Commerce unlock + real import preserved manual `ledger-dcff93fba1e9` and created exactly `source-mw-3609481` + `source-mw-3609488`; no duplicates or invented Brand/local prices.
- [x] Site identity remains #39 revision 11; no publish event; Commerce intentionally remains unlocked/ready for W4.
- [x] Post-import integrity/snapshot PASS: `phase50-a2w-w3-post-ledger-import-20260921-103507`, SHA256 `fbeeca44c9ebb46be75c1dc6a70ab2eaa6a34aa719483808578c56fb3be05a9d`; Qt Stage-2 readback shows exactly three Profiles.

## W4 acceptance gates
- [x] Read-only mapping core + Stage-2 review action implemented.
- [x] Real Local inventory inspected: 16 active PLA offers; exact Source color HEX matches = 0.
- [x] Multicolor Source slots remain distinct; no fake combined Ledger mapping/price.
- [x] W4 focused 5/5 PASS.
- [x] Corrected mature Filament/Profile/Commerce + W3/W4 gate 49/49 PASS.
- [x] Retained A2V/W1/W2 media/site gate 83/83 PASS.
- [x] py_compile / diff-check / RUN_QT VerifyOnly PASS.
- [x] Commit/push W4 source `27bb00a1d8a8dd34e033af9cfaba27f37384a0a0` and verify GitHub exact SHA.
- [x] Fresh pre-preview Catalog backup integrity PASS: `phase50-a2w-w4-pre-preview-20260921-114901`, SHA256 `a38f78d346e2b367eaaeed540837ff5e076dea890c26808ddc0437106f239f7e`.
- [x] Exact-SHA Qt real #625 W4 Preview PASS: 2 Profiles / 3 slots / 48 PLA candidates / exact HEX=0.
- [x] Source facts + Ledger + Stage locks + Site #39 revision 11 + product-history count are unchanged before/after Preview.
- [x] #625 was not published by W4. A separate pre-W4 failed publish attempt remains preserved at batch `26aa571c-1a0c-4ad4-9431-65e74c27d94f` with Site revision still 11.

## Next exact task
Do not return to W1/W2/W3. W4.1 source is Local-tested. Exact next is GitHub exact-SHA promotion -> fresh integrity-checked Catalog backup -> exact-SHA Qt runtime -> controlled dimension-only real patch for #628 and #625 with invariant proof. Only after W4.1 real-data acceptance, investigate failed batch `26aa571c-...` as a separate publish-recovery task; never auto-retry it during dimension work.
