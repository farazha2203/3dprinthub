# Phase50.A.2M — Authoritative Windows Re-publish Replacement

Status: `LOCAL_TESTED / GITHUB+PRODUCTION NEXT`
Date: 2026-09-19

## Requested delta
When an already-published Product is edited in Windows and sent again, the existing Site Product identity must be preserved, but the current Windows snapshot must replace the old active Product configuration. Re-publish is replacement, not additive merge.

## Verified production defect
Product #625 -> Site Product #39 reached revision 7 with strict ACK `updated` and parity `ok=true`, yet Production still had five active Variants: three current `CC-P39-...` rows plus two stale `EP49-3F...` rows. The stale rows still carried 1 g / 60 min / 104,500 Toman and polluted the customer-facing choices/range despite the new Windows matrix carrying 60 g, 110 g material+support input, 180 min and 1,095,000–1,215,000 Toman.

## Replacement contract
- Preserve Product PK/slug/server identity and historical rows needed by past orders/rollback.
- Text, SEO, pricing profile, active material/color/profile/weight/time/price configuration comes from the latest Windows batch.
- If `sales_profiles_json` exists, only the exact current `CC-P<product>-...` matrix may remain active/orderable.
- Older manual/MW-FIX/EP49/EP49-3F/removed CC rows are deactivated, never deleted.
- ProductImage rows are rebuilt from the exact current selected-image set on every Desktop re-import.
- Windows local image addition must persist the file into the Product, select it, mark an uploaded Product dirty, and still pass the existing SEO-finalization gate before publish.
- A successful sync must fail closed if stale active non-CC Variants survive or active profile count differs from the Windows snapshot.

## Must not touch
No duplicate Product creation, no destructive historical Variant deletion, no order/history rewrite, no Production source edits outside GitHub-first deploy, no weakening of SEO/public-media/parity gates.

## Local verification
- Python compile PASS.
- Django check PASS with existing CKEditor warning.
- Migration drift: none.
- Server profile/import/admin-sync focused gate: 15/15 PASS.
- Windows image workspace focused gate: 25/25 PASS.
- New explicit local-file image persistence test PASS.
- Stale legacy/manual Variant deactivation tests PASS.

## Production acceptance
Commit/push exact candidate -> selective Production release promotion -> fresh rollback backup -> deploy from GitHub through reverse tunnel -> re-publish #625 once -> require exactly 3 active current CC Variants, 0 stale active non-CC rows, current price/weight/material/time on public API/page, exact current ProductImage set and HTTP 200 media -> Browser QA desktop/mobile -> docs closure.

Instagram remains separate: Buffer still rejects media ingestion before post creation; no successful #625 Feed/Story receipt exists yet.
