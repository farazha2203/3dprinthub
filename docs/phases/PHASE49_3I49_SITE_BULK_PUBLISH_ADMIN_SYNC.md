# Phase49.3I.49 — Guarded Multi-Product Site Publish + Full Slider/Admin Sync

Date: 2026-09-02

## Goal

Make Windows Catalog Center and the Django site operate one coherent Product/Slider publishing contract:
- select several Products;
- explicitly mark only complete Products ready;
- publish only selected-ready Products;
- accept Published only after Store/public verification;
- expose the same site-relevant Slider controls in Windows and Django Admin;
- preserve existing Product/Variant/pricing/secret authorities.

## Baseline and rollback

Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Pre-change head: `1f8910b6c8c7c601cfd50689d8c48af492f7c453`  
Rollback branch: `backup/pre-phase49-3i49-site-bulk-publish-admin-control-20260901`.

## Product publish contract

Ready is explicit operator intent over factual Stage readiness. It uses the existing `upload_ready`, `publish_as_product` and workflow fields; no parallel queue model is added.

Bulk publish reuses the mature pipeline:

`selected ready Products → Batch v8.5 → selected-image packaging/validation → FTP → Bridge import → Product/Store visibility → public HTTP/media verification → ACK receipt`.

Only strict success transitions to:
- `workflow_status = uploaded`;
- `upload_ready = 0`;
- `needs_update = 0`;
- persistent server identity/revision/ACK/published timestamp.

The pre-existing Published filter therefore becomes the UI destination automatically. A failed/skipped Product remains outside Published.

## Slider/Admin contract

No new Slider table or settings authority is introduced. Existing ProductCatalogProfile/HomepageHeroSlide persistence is completed across the Bridge.

Round-trip includes:
- Persian title, description, image Alt, button and focus keyword;
- selected Slider image;
- presentation mode;
- object fit and focal position;
- scale and X/Y position;
- background mode/color/blur;
- Desktop/Mobile max width/height;
- transition effect and duration;
- display duration;
- sort order and active state;
- optimistic sync revision/source/operator audit.

Admin fieldsets are ordered by user task and sync diagnostics are collapsed, following the registered professional-commerce design architecture.

## Tests

Windows exact-head run:
- `33596830380` — PASS on `f9f89643de883ff549a9c0089235e43f061c5d4d`.
- Includes dedicated `tests.test_phase49_3i49_site_bulk_publish`, mature Qt/Acquisition/Filament/Profile/Stage regressions, offscreen Qt launch and legacy launcher.

Single Active AI / Django no-migration:
- `33596830268` — PASS on `f9f896...`.

Admin/Bridge:
- `33596562467` — PASS on `16cf7cfaf6be3e8594435e3489cb0615624fcb00`.
- Compile, Django system check, `makemigrations --check --dry-run`, migration apply on CI SQLite and Admin regression passed.
- Compare `16cf7c... → f9f896...`: only `RUN_PHASE49_3I42C_LOCAL_GATE.ps1` changed.

## Safety

- Django migration: NO.
- Catalog destructive migration: NO.
- Production DB write: NO.
- Host deploy: NO.
- Production source edit: NO.
- secret migration: NO.
- FTP/Bridge credentials stay in the established Local secure store/environment boundary.

## Owner Local acceptance

Run the repository-owned checksum-backed Local gate on the canonical Windows checkout and verify:
- multi-select Product Ready action;
- incomplete Product rejection detail;
- Ready labels in Gallery/Table;
- Bulk Publish confirmation counts;
- Published lifecycle movement only after verified success;
- no failure is shown as Published.

Do not perform a real live Product publish until the owner intentionally chooses a disposable Product and the current Production receiver/deploy/migration state has first been verified through the normal read-only Host gate.
