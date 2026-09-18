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
- Commit/push the Screenshot visibility repair and relaunch Qt from that exact SHA for owner use.
- Production deploy/manual-payment apply remain blocked until ERR-49-154 reverse-tunnel recovery plus Host identity, MySQL backup, rollback and readiness gates.
- Later Podium/Farataz payment automation is intentionally deferred per owner request; do not guess/import it before a separate source/document audit.
