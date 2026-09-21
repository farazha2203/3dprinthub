# Phase50.A.2X — Server parity + Hero public-media closure

Status: **PRODUCTION_VERIFIED / CLOSED**
Date: 2026-09-21
Accepted runtime-bearing Production source: `94e53831be67368ec199c1ea5b3ab728cbfff445`
Branch: `wip/phase50-a2x-server-parity-20260921`

## Completed server incident
Catalog Product #620 first reached Production in batch `desktop_catalog_v85_20260921_160339` / UUID `8be482aa-5469-439d-bad3-6dcab3f9f8de` and rolled back only because material-name casing differed (`pla/petg` vs canonical `PLA/PETG`).

Hotfix `143848eeeeac7be8ec64c33ab7aa4c95c9f42165` makes only material identity case-insensitive while keeping Brand, Manufacturer, Color, stock state, profile keys, media names/SHA and numeric commerce parity strict. A2X authoritative SEO assignment is also live. No migration/schema change.

Controlled retry used a new batch, not the failed batch:
- Batch `desktop_catalog_v85_20260921_163452`
- UUID `2cb55e9e-35fa-40b0-8901-2606e7a4118c`
- Site Product #41 revision 1
- Slider #17 revision 1
- republish parity OK, zero mismatches
- media count 1
- active profile/Variant rows 160, stale active rows 0
- public Product and canonical Product media HTTP 200

## Final Hero persistence defect
Hero #17 is active and Home already renders the canonical Product-owned image through the ERR-49-125 runtime ownership fallback. However, the stored `HomepageHeroSlide.image_url` still contains the private `/media/store/imported-models/gallery/...` URL, which correctly returns 404 because imported working media is intentionally not public.

The follow-up changes the unified Desktop -> Hero persistence boundary:
- persist matching ProductImage media first;
- otherwise persist Product.main_image;
- never persist private ImportedPrintAsset working-media as the public Hero URL;
- only use source HTTP(S) as fallback when no Product-owned public media exists;
- keep `selected_asset_image` for audit/edit identity;
- no Product #620 re-publish is required.

## Local verification
- Unified Sync + Hero media ownership + unified import E2E: 11/11 PASS.
- Home/Slicebox/Hero presentation regression: 16/16 PASS.
- Python compile: PASS.
- Django check: PASS with known warnings only.
- `makemigrations --check --dry-run`: no changes.
- `git diff --check`: PASS.

## Production closure
- [x] Commit/push exact Hero follow-up `94e53831be67368ec199c1ea5b3ab728cbfff445`; Local=GitHub exact.
- [x] Reverse-tunnel Host exact baseline/branch/worktree/MySQL/migration preflight.
- [x] Fresh scoped rollback `/home/sfkilvrs/3dprinthub-deploy-backups/20260921-165608-phase50-a2x-hero-media-minimal`; runtime-before/env/MySQL SHA256 + gzip PASS. ERR-49-213 records the quota-driven scoped-bundle choice.
- [x] Explicit fetch + ff-only deploy from GitHub; no migration.
- [x] Targeted one-time normalization of Hero #17 stored URL; exactly one row updated, Product #41 not republished.
- [x] Hero #17 stored/effective URLs are Product-owned canonical media; Hero and Product Profile revisions remain 1.
- [x] Home DOM and real Chrome/Playwright use canonical media, Product link is present, all 3 Hero images load, and public `store/imported-models` refs are zero.
- [x] Home/Store/Product/canonical Hero media HTTP 200; final Host worktree clean; migration plan empty.
- [x] Windows #620 remains on successful batch UUID `2cb55e9e-35fa-40b0-8901-2606e7a4118c` with no later publish receipts.

A2X is closed. Do not re-publish #620 for this phase.
