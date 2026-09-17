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
- Local gates: Django/Store payment 11/11 PASS, A2L payment 4/4 PASS, scoped Catalog 55/55 PASS, Qt launcher verify PASS, `git diff --check` PASS. Historical all-test discovery remains unsuitable as a release gate and is recorded in ERRORS.

## Remaining gates
- Commit/push exact A2L candidate and relaunch Qt from that pushed SHA for owner visual QA.
- Production deploy/manual-payment apply remain blocked until ERR-49-154 reverse-tunnel recovery plus Host identity, MySQL backup, rollback and readiness gates.
- Later Podium/Farataz payment automation is intentionally deferred per owner request; do not guess/import it before a separate source/document audit.
