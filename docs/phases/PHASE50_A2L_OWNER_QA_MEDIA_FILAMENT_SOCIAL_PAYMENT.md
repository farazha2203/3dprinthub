## Pricing authority + Instagram companion Story/Highlight — 2026-09-19
- Real Product #625 remains the acceptance identity. After ERR-49-173 media-path recovery, strict parity correctly stopped its resend on Windows/Site price-range divergence.
- Owner-approved post-default Catalog preview is integrity-ok and establishes PLA defaults: 3.5m/4.5m purchase/sale, 150k print/hour, 50k supervision/hour; offer-specific preheat remains independent.
- Windows Ready/Publish now refreshes selected Filament/Profile snapshots from current inventory and recalculates price range without reopening Product UI.
- Server Desktop-managed `CC-P...` pricing now mirrors Catalog material + print + supervision + preheat + assembly formula and uses managed Variants as public range authority.
- Social policy v3 is Site-first: primary verified Site Product media first, ALT per media, SEO caption, bounded hashtags, Product tracking URL and nationwide-Iran shipping.
- Companion Story is default; final evidence style is `3dprinthub_instagram_gold_navy_v2_iransans`, 1080x1920, IRANSans.
- Highlight classifier follows approved taxonomy; #625 `toys-games` -> `اسباب بازی`. Official Buffer API cannot add a Story to a Highlight, so receipt queues `highlight_status=operator_required`.
- Tests: Server targeted 5/5 PASS + no drift; Windows pricing/social/story 19/19 PASS; Manufacturer-vs-Brand regression PASS.
- Rollback refs: Windows `backup/pre-phase50-a2l-pricing-social-20260919 @ 585e203...`; Server `backup/pre-phase50-a2l-pricing-engine-20260919 @ ba05c7fc...`.
- Exact next: Commit/Push both candidates -> dedicated tunnel recovery -> Server deploy -> fresh backups -> owner-default PLA repair -> refresh/republish #625 -> Site #39 read-back/browser -> real Feed+Story -> receipt/Highlight queue closure.

## Screenshot SEO + changed-source real acceptance — 2026-09-18
- Exact runtime `89931e8958b3a738fbfb4b8d65c099124aa24de0` is pushed and running.
- Fresh Catalog backup `pre-republish-89931e8-20260918-191741` passed source/backup integrity with 635 Products.
- Real Product #625 preflight: FTP PASS, Bridge/readiness PASS, zero blockers, two selected finalized images.
- Same-identity Site update completed on Product #39 / asset 143; Product revision is now 5 and strict ACK reports `updated`.
- Public Product page and all ACK media return HTTP 200. Public media SHA256 exactly equals Local finalized WebP SHA256 for both selected images.
- Screenshot SEO + changed-source-media contract is now real-path verified. Remaining Production code promotion is separate and reverse-tunnel-only.

## Screenshot SEO + changed-source re-publish closure — 2026-09-18
- Product #625 owner QA exposed two remaining media boundaries: empty per-card SEO on manual Screenshot and stale finalized WebP reuse after local source bytes changed.
- Single-image SEO now receives Product semantic defaults only when stored metadata is absent; it does not toggle Site selection.
- Unselected Screenshot metadata persists for later review but stays `metadata_ready=False` until explicitly selected.
- `اصلاح اسم و سئو` with no operation subset processes every editable Product image.
- Ready/Send detects source-byte drift only for already-finalized selected images and rebuilds their final SEO WebP automatically. Missing/unfinalized media remains blocked.
- Same Site Product identity is preserved; no duplicate Product path was introduced.
- Local gates: 41/41 focused, 77/77 aligned current-contract, 145/145 broad regression, Qt VerifyOnly, compile/check/no-drift/diff-check PASS.
- Rollback: `backup/pre-card-seo-source-refresh-20260918` at pre-fix `ea1a4a7...`.
- Next: GitHub promotion -> Catalog backup -> exact-SHA Qt relaunch -> Product #625 controlled republish/public verification. Production source deploy remains tunnel-only.

## Image name+SEO + in-place re-publish hardening — 2026-09-18
- Owner requested one `اصلاح اسم و سئو` Stage-3 action. Automatic semantic SEO and deterministic numbered filename generation are now one operation; selected operation subset wins, otherwise all editable Site-selected images are processed.
- Mature manual SEO editor, Screenshot, image membership, Primary/Slider and filename authority remain unchanged.
- Windows direct image/operator mutation boundaries now mark a server-linked uploaded Product `needs_update=1` without changing its Site identity. Stage edits already had this behavior through StageCore.
- Existing Stage-7 Send already requeues the Product and performs revision guard before Batch/FTP/Bridge.
- Server E2E proves changed content/SEO/media re-import updates the same Product/Asset, not a duplicate.
- Gates: 22/22 image, 59/59 Windows/Site, 3/3 unified importer, 23/23 profile/identity/admin-sync PASS.
- Production unchanged; next Host action remains dedicated-tunnel recovery -> GitHub deploy -> Production verify -> #152 Site -> Instagram #152.

## Site-first Product/Admin hotfix — 2026-09-18
- Owner priority: deploy Site before additional Instagram publication.
- Public Product detail current source intentionally has no standalone Filament roll-price cards; the four-step guided selector remains customer ordering authority.
- Product change-page 504 root cause is the large ProductVariant inline. A 37-Variant Local page measured 781 queries / 892118 bytes with it versus 60 queries / 277103 bytes without it. Variant editing remains available in dedicated ProductVariant admin.
- Profile name/size identity is now ASCII-only; Product #625 real read-only acceptance is Standard / Standard with all 64 material options preserved.
- Real Site ACK media parser accepts numeric images count + public_http_checks.images and filters media to the current Product; #309/#301 real ACK acceptance PASS.
- Local gates: 17/17 Site/Admin, 82/82 Catalog/Instagram/Qt, 27/27 Hero, compile/check/drift/diff-check PASS.
- Production remains unchanged until the dedicated 3DPrintHub reverse tunnel is restored and Host gates pass.

## Image filename/four-row runtime — 2026-09-18
- Runtime `aaa5cb9f6d743becf3f1588501733ae835bd7451` is pushed and running from clean worktree `D:\projects\3dprinthub-runtime-aaa5cb9`.
- Fresh Catalog backup passed integrity with 635 Products.
- Product #301 post-launch: English planned/final filename match; Persian Alt/SEO title/caption/12 keywords preserved.
- Main worktree concurrent Instagram/Buffer changes were not touched.
- Remaining Windows gate is owner visual smoke. Production unchanged.

## Image filename authority + four-row scroll correction — 2026-09-18
- Product #301 read-only verification proved existing semantic image SEO is healthy: English finalized filename, Persian Alt/SEO title, caption, 12 keywords.
- Restored only `planned_seo_filename()` to source-English-title-first ASCII naming.
- Alt/Title/Caption/Keywords, AI refresh, operator overrides, Screenshot, selection and finalization behavior are unchanged.
- Large Stage-3 gallery always reserves at least four 206px rows; empty probe host 842px / viewport 652px / scroll max 190.
- Focused 4/4 + broader 97/97 PASS; compile/diff-check/Qt VerifyOnly PASS; no migration delta.
- Production unchanged; dedicated reverse tunnel remains the only allowed Host path.

## Stage-3 3×3 runtime — 2026-09-18
- Exact runtime `a52cd52a18a119f9aa2940ebc00f588828d1a558` is pushed and running in canonical Qt.
- Fresh Catalog backup `pre-stage3-3x3-a52cd52-20260918-123308` passed source/backup integrity with 635 Products.
- Qt child PID 53788 is visible/responsive.
- Current Product #628 persistence has 2 selected/source images; isolated 9-card acceptance proves the 3×3 capacity.
- Dedicated reverse tunnel `22024` is down. Production deploy is blocked and no alternate cPanel/browser path is allowed.

## Stage-3 3×3 compact review correction — 2026-09-18
- Owner correction is presentation-only: three columns, three complete visible rows, smaller image preview, always-visible SEO filename and one compact Previous/Next/SEO/Delete row.
- Review card: 300–520px width, fixed 206px height; preview 260x90 min / 94px max. Gallery min-height 670px.
- 9-card isolated acceptance: viewport 652px high; row-three card bottom 634 and filename bottom 576; no scrollbar required. 12 cards require scroll and wheel-over-preview remains functional.
- Image selection/Primary/Slider/SEO/Delete/Reorder/Screenshot behavior is unchanged.
- Focused 4/4 + maintained Qt/Gallery/Wizard/Screenshot 68/68 PASS.
- Host deploy remains separate and may use only the dedicated 3DPrintHub reverse tunnel.

## Design-only Stage-3 compaction — 2026-09-18
- No image operation/mode/callback changed.
- Eight Stage-3 actions are a single 7pt/26px row; Save/Finalize/Unlock/Previous/Next are a single compact bottom row.
- Freed vertical space raises the gallery minimum to 650px; real Product #628 acceptance gives a 634px visible image viewport while the whole page remains within the 1032px Windows working height.
- Geometry assertions prove one Y row for all eight top actions and zero vertical-center spread for all five bottom actions.
- Maintained Qt/Gallery/Wizard/Screenshot suite 67/67 PASS; Qt VerifyOnly/compile/diff-check PASS.
- Homepage Slicebox work is tracked in A2K; no Production/DB change yet.

## Stage-3 scroll runtime — 2026-09-18
- Hotfix `00f16237cf27eea2cdf7bef97fa7cc140014c947` is pushed and running in the canonical Qt app.
- Fresh Catalog backup `pre-stage3-scroll-00f1623-20260918-112042` passed source/backup integrity and retained 635 Products.
- Visible Qt child is responsive. Owner smoke remains: wheel directly on image must reach lower filename/select/edit/delete controls and the Stage must stay screen-bounded.
- Production is unchanged.

## Stage-3 visibility / wheel-scroll correction — 2026-09-18
- Owner screenshot showed the large cards but lower filename/select/edit/delete controls were still unreachable.
- Exact root cause: 720px gallery minimum pushed the Product Wizard beyond the real desktop working area; wheel events over `ClickableImageLabel` did not reach the gallery scrollbar.
- Fix keeps large cards/previews and all image business logic unchanged, sets the gallery container minimum to 560px, and forwards image-preview wheel deltas to the gallery vertical scrollbar.
- Real Product #628 copy: gallery viewport 544px, content host 2424px, scrollbar range 0..1880; preview wheel 0 -> 270.
- Regression 67/67 PASS; compile/diff-check/Qt VerifyOnly PASS. No DB/schema/Production change.
- Unrelated Instagram Story render/font work already present in the worktree is preserved and excluded from this hotfix.

## Stage-3 image runtime promotion — 2026-09-18
- Exact runtime `91d4c188aa57c125e46d45f39a70d913085dcf6c` is pushed and Local/GitHub match.
- Fresh pre-launch Catalog backup: `pre-image-workspace-91d4c18-20260918-105013`, source/backup integrity `ok`, 635 Products.
- Exact-SHA Qt verification passed and the canonical Qt application was relaunched; visible child window is `3DPrintHub Catalog Center v8.9.10 - Qt 6`.
- Post-launch Catalog remains integrity `ok`; Product #628 keeps 11 persistent Site-selected images.
- Remaining Stage-3 gate is owner visual smoke only. Production remains unchanged.

## Stage-3 image workspace continuation — 2026-09-18
- Owner requested a larger image review surface, compact surrounding controls, arbitrary multi-select Edit/Delete, deterministic SEO filename display, and Product-main-image-first Instagram feed behavior.
- Bulk-operation selection is now independent from persistent Site-image membership; clicking an image preview may toggle only the temporary operation selector.
- Trusted real legacy numbered files are editable under safe local identity; recoverable delete moves those files outside the active images directory.
- Operator metadata/renumber preserves the selected set and bypasses publish-time perceptual dedup only for that explicit operator action. Default publication finalization remains deduplicating.
- Product #628 isolated-copy acceptance: selected 11 -> 11, zero legacy local-display identities after renumber, 11 unique final SEO metadata names, Primary preserved, 15 visible/15 editable local files.
- Instagram/Buffer media ordering forces verified Product main image to first position without discarding remaining verified media.
- Tests: 9/9 targeted, 80/80 maintained, 107/107 expanded, compile/diff-check/Qt VerifyOnly PASS. No migration/schema/Production change.
- Next: commit/push exact candidate, verify remote SHA, fresh Catalog backup, exact-SHA Qt relaunch and owner visual smoke.

# Phase50.A.2L — Owner QA: Media, Filament Intelligence, Social & Manual Payment

Date: 2026-09-17
Status: `LOCAL_IMPLEMENTATION / TESTED_CORE / PRODUCTION_BLOCKED_BY_ERR-49-154`

## Owner acceptance scope
This phase is driven by the 2026-09-17 owner screenshots from Catalog Center v8.9.10.

1. Product Wizard Stage 3 must be large enough to review, multi-select, reorder, SEO-edit and delete several images without controls being clipped.
2. Source image recovery must map and display all distinct recovered product images, not only report a count.
3. `Sync همه با سایت` must continue syncing valid Filaments when a legacy row has incomplete identity, while reporting rejected rows for repair.
4. Filament operating rates must support single-row, selected-row and all-active bulk edits.
5. Product/Profile material selection must support deterministic smart recommendations based on actual product use and source facts.
6. For decorative/display products, PLA/PETG are the conservative default recommendation; engineering CF/Nylon families are not auto-selected without matching evidence.
7. Material descriptions, use cases and sample parts must remain visible in the material registry and Site order wizard.
8. AI may propose approximate dimensions/weight/print-time/spec facts from source page + saved crawl data + product images, but estimates must be explicitly labelled and require operator confirmation before becoming commerce facts.
9. Instagram path remains Site-first: verified public Product -> Buffer -> Instagram feed/Story; if five verified Product images exist, all five stay in the feed payload.
10. Instagram content must use canonical Product copy, relevant hashtags/alt text, tracked Product URL and approved gold/navy brand style; Highlight placement remains operator-required where Buffer has no supported Highlight mutation.
11. Until the online gateway is connected, manual card transfer is the active fallback with receipt upload -> admin review -> operator notification.

## Manual payment authority
- Bank: بانک پاسارگاد
- Account holder: فراز حراجی
- Card: `5022-2910-9403-4343`
- Receipt approval remains an admin action; receipt submission triggers the existing operator notification pipeline.
## Local implementation evidence
- Stage 3: 2 large image columns, 560 px minimum viewport, always-visible vertical scrollbar, 72 px single step and 420 px page step.
- Multi-image controls: Select All / Clear / bulk SEO / delete / primary / slider / reorder are retained.
- Mature source recovery uses `refetch_product_from_source_async(... preferred_method="rich", adaptive_fallback=True)` and preserves operator-owned commerce/SEO decisions.
- Full Filament Site sync catches identity failures per-row; valid rows continue and failures are summarized.
- Bulk Filament rate editor changes only explicitly enabled fields for selected rows or all active rows.
- Smart material recommendation honors explicit source material first, then product-use rules; decorative regression requires PLA/PETG and excludes engineering CF/Nylon defaults.
- Buffer feed retains up to 10 verified public media assets; 5-image regression requires exactly 5 assets.
- Buffer companion Story and Highlight target receipt are implemented; actual Highlight assignment is marked `operator_required`.
- Manual payment seed is dry-run by default and requires explicit `--apply`.

## Acceptance update — 2026-09-18
- AI production/spec Preview is implemented and regression-tested: source/link + saved Product images are passed to the configured AI Provider; no estimate writes until explicit operator confirmation, and existing operator facts are preserved.
- Profile editor exposes «انتخاب هوشمند متریال مناسب محصول»; decorative/display regression selects PLA/PETG and excludes PA12-CF/PLA-CF defaults unless source/product evidence justifies engineering materials.
- Stage 3 is two large columns with always-on vertical scrolling and row-height expansion; Product #628 resolves 10 real local Product images from the canonical Catalog runtime.
- Filament Site sync is fail-soft per row; valid rows continue while incomplete legacy identities are reported for repair.
- Bulk Filament editing supports selected rows or all active rows and independently applies print-hour, supervision, preheat time, preheat temperature and preheat-hour cost.
- Real Buffer gate PASS using Windows Credential Store + configured Instagram channel; provider reports Instagram connected/unlocked. Five verified Product images remain five Buffer feed assets; companion Story keeps the canonical tracked Product URL.
- Approved gold/navy Instagram profile/Highlight base asset is installed at `assets/instagram/final/profile_logo_gold_navy.png`; actual Highlight assignment remains operator-required because the current Buffer path has no supported Highlight mutation.
- Manual-payment flow uses the existing StorePayment receipt model: receipt -> `awaiting_review`/`payment_review` -> admin review. Operator alert fan-out attempts Telegram, WhatsApp and Email and cannot roll back a saved receipt.
- Pasargad seed is dry-run by default, logs only a safe card suffix, and requires explicit `--apply` after Production backup/readiness gates.
- Local gates: Django Store+manual-payment 11/11 PASS, scoped Catalog 57/57 PASS, Qt launcher verify PASS, changed-file compile and `git diff --check` PASS. Historical all-test discovery remains unsuitable as a release gate and is recorded in ERRORS.

## Real Catalog reconciliation — 2026-09-18
- Exact candidate `4375c007874faa87c874f3806705532128814176` was pushed and relaunched from GitHub after a fresh integrity-checked Catalog backup.
- Product #628 real-data probe: 10 local Product images, two large columns, 560 px gallery minimum, 2508 px content minimum and 1964 px vertical scroll range.
- Real Filament inventory has 71 rows. 63 legacy rows have blank Brand; only 8 currently have complete Material/Brand/Color Site identity. The program must not fabricate the missing Brand.
- Follow-up adds selected/filterable registered-Brand repair. It changes Brand/Manufacturer only, preserves Material/Color/pricing/stock/print settings, rejects unregistered Brand values and reuses the guarded Site sync after repair.
- Copy-of-real-Catalog repair of row #14 to an existing registered Bambulab identity passed Site-payload validation and SQLite integrity while leaving the canonical Catalog untouched.
- Follow-up focused gate 28/28 PASS; full maintained A2L Catalog scope 57/57 PASS.

## Owner correction — 2026-09-18
- The owner explicitly rejected the recent Stage-3 control/workflow changes and required a sizing-only repair.
- Corrective scope restores the mature button/action wiring, Screenshot route, recover-limit behavior, slider panel, AI visibility and normal saved window geometry.
- Only the Product image review presentation may change: larger cards/previews with reachable scroll content. Image filename display/generation and Screenshot capture/naming are explicitly frozen to the mature pre-change behavior; the rejected filename-display override was removed.
- No migration, Catalog schema or Production change. Corrective focused Qt/Gallery/Wizard/Screenshot regression: 60/60 PASS. Runtime correction is pushed at `20f483af983cad550b1e2473751798daf0e8d39b` and the canonical Qt window was relaunched after backup.

## Screenshot visibility repair — 2026-09-18
- Real Product #628 proved the Screenshot button was capturing and persisting files; the failure was in Qt display resolution after the A2L numbered-image path returned before explicit manual Screenshot mappings.
- The fix changes only `qt6/kernel.py`: persisted `local://source-page-screenshot...` images remain visible beside numbered Product files and can no longer be mistaken for numbered source slots.
- Screenshot capture/naming/crop, Product Wizard button wiring, SEO pipeline, selection persistence and enlarged card dimensions are unchanged.
- Dedicated regression failed before the fix and passes after it; maintained Qt/Gallery/Wizard/Screenshot gate 61/61 PASS, launcher verify/compile/diff-check PASS.
- Copy-of-real Catalog acceptance used integrity-checked backup `pre-screenshot-resolver-20260918-095910`; canonical Catalog, schema and Production were not mutated.

## Remaining gates
- Screenshot visibility repair is pushed at `bab82e89e9e27722b8b1000a959b1161ee84e038`; Local/GitHub SHA matched and the canonical Qt runtime was relaunched from that exact source. Remaining acceptance is the owner's same-Product Screenshot smoke.
- Production deploy/manual-payment apply remain blocked until ERR-49-154 reverse-tunnel recovery plus Host identity, MySQL backup, rollback and readiness gates.
- Later Podium/Farataz payment automation is intentionally deferred per owner request; do not guess/import it before a separate source/document audit.
