# PHASE50.A.2M — Authoritative Full Re-publish

Status: LOCAL_TESTED / GITHUB+PRODUCTION NEXT
Date: 2026-09-19

## Goal
When an already-published Windows Product is sent again, the current Windows payload replaces the Product-owned public state in place. The same Site Product identity is retained; stale public commerce/media state must not remain active beside the new revision.

## Acceptance contract
- Same Desktop identity updates the same ImportedPrintAsset and Site Product; no duplicate Product.
- Current `sales_profiles_json` is the sole active commerce matrix when supplied.
- Historical Variant rows may remain for rollback/order references, but every row not represented by the current CC-P matrix becomes inactive.
- Current weight, material, brand, color, print/supervision/preheat rates, dimensions, stock facts and calculated price replace stale active values.
- Current selected/finalized Product media is the sole Product gallery authority; stale gallery rows must not survive.
- Republish parity must compare all active Product Variants, not only CC-P rows, and fail closed on any extra active legacy row.
- Product price range is finalized after the current matrix mutation.
- Windows owner-added images must become selected/finalized Product media and mark an already-published Product dirty for the next same-identity update.

## Real incident
Catalog #625 -> Site Product #39 reached revision 7 with `republish_parity.ok=true`, but Production still exposed five active variants: three current CC-P rows plus two stale EP49-3F rows with 1g / 104500 Toman legacy values. The current Catalog payload owns three profiles at 60g final / 110g material weight and 1,095,000–1,215,000 Toman.

## Gates
1. Focused Server tests PASS.
2. Django check + no migration drift + diff-check PASS.
3. Commit/push exact release SHA and rollback ref.
4. Guarded GitHub-first Production deploy with fresh source/env/MySQL backup.
5. Re-publish #625 through the official Windows Batch/FTP/Bridge path.
6. Production must have exactly three active Variants, all current CC-P rows, and current price/weight/material facts.
7. Browser/API QA must show no stale 1g/104500 option.
8. Windows image-add/screenshot path must persist + select + finalize + dirty the Product.
