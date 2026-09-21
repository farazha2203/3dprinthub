# Phase50.A.2X — Slider SEO Readiness + Authoritative Re-publish

Status: **LOCAL_TESTED / GITHUB PROMOTION NEXT**
Date: 2026-09-21
Parent baseline: Phase50.A.2W W4.1 exact GitHub SHA `7f2280eafe7a3293008a6dc7a4559b0ef92f114c`
Branch: `wip/phase50-a2x-slider-authoritative-republish-20260921`
Rollback ref: `backup/pre-phase50-a2x-slider-authoritative-republish-20260921`

## Owner contract
Slider SEO/media data must be complete for every Product even when homepage membership is disabled. The operator checkbox alone decides whether the Product is active in the homepage slider. Single-Product AI completion and multi-select SEO completion must both fill Slider data without enabling membership.

Every Windows → Site re-publish must update the same Site Product identity and apply the current Windows-owned snapshot again, including current media selection, SEO, Profile/Variant state and Slider membership/data. Site values must not silently survive merely because an incoming value changed or the Slider checkbox is off.

## Implemented Local delta
- Base readiness has a real seventh Slider data stage; disabled membership no longer makes empty Slider fields appear complete.
- Slider title, description, ALT, button text, focus keyword and image are required data for all Products.
- AI task-center, refresh and operator rebuild persist Slider data independently of `homepage_slider_enabled`.
- Bulk selected-Product SEO repair now targets `content + slider`; it never toggles Slider membership.
- Missing Slider image falls back to current Primary/selected Product media.
- Editing Slider state on an already linked Product marks the same Site identity for re-publish even when only `server_product_id` is populated.
- Server SEO synchronization no longer preserves stale Site SEO through old-value fallbacks.

## Real evidence
Catalog Product #620 currently has homepage membership disabled and empty persisted Slider fields, but its existing `content_pack_json.homepage_slider_seo` already contains complete generated copy. Therefore #620 and similar Products can be backfilled from existing AI output without another AI request.

W4.1 real-data state was reverified before A2X: #628 has Source Profiles at 12×12×12 and 18×18×18 with 16 active PLA offers each; #625 preserves 5×5×5 on Profile 1, has owner-estimated 4×4×4 on Profile 2, and both Profiles carry 16 active PLA offers. Post-W4.1 snapshot: `D:\projects\3dprinthub-backups\phase50-a2w-w41-post-accept-20260921-152825\catalog-after-w41.sqlite3`, SHA256 `7743e63fba5d83b2991502ce320d21f7037a444dba0ef9bc2b240ad88c3ca8da`.

## Verification
- Focused readiness/AI/Qt media gate: 33/33 PASS.
- Server same-identity Slider/SEO/import gate: 9/9 PASS.
- Broad Catalog regression: 115/116 effective PASS; sole failure is the already-proven baseline Manufacturer-vs-Brand assertion tracked by ERR-49-203.
- `git diff --check`, touched Python compile, Django check, migration drift check and `RUN_QT.ps1 -VerifyOnly`: PASS.
- No migration is introduced by A2X.
- No Production source, Production DB or live Site Product has been mutated by A2X yet.

## Remaining acceptance
- [ ] Commit/push A2X and verify exact GitHub SHA.
- [ ] Launch Qt from the exact pushed A2X SHA.
- [ ] Take a fresh integrity-checked Catalog SQLite backup.
- [ ] Backfill existing Slider SEO/media from saved content packs without AI; preserve every membership checkbox.
- [ ] Verify #620 and sampled bulk Products in the real Qt UI.
- [ ] Deploy the Server delta only from exact GitHub SHA through the dedicated reverse tunnel.
- [ ] Perform one controlled same-identity re-publish and prove exact current Windows field/media/Slider replacement on Production.
- [ ] Production HTTP/data verification, docs closure and rollback record.
