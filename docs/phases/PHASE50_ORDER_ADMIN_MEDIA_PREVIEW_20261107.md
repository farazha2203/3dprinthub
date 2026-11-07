# Phase50 — Protected order upload image previews

Status: `INLINE_WIDGET_FIX_LOCAL_TESTED / PRODUCTION_BASELINE_17d60f73 / DEPLOY_PENDING`.

## Request and verified cause

After the order #1 admin page was repaired, the owner showed broken previews for its uploaded reference photos and a Not Found tab. Production read-only checks proved all four `OrderReferencePhoto` files and the STEP attachment exist. The effective `MEDIA_ROOT` is `/home/sfkilvrs/3dprinthub/media`; Production intentionally serves only selected public Store media namespaces through `/media/`, so `/media/orders/reference/...` is not a valid public URL. This is a protected-media routing mismatch, not missing uploads.

## Requested delta

- Render order and reference images through one authenticated, ownership-checked image route.
- Reuse the route in the Order admin gallery, image inline, and reference-photo admin thumbnail.
- Use the same protected route in the inline preview and Django's current-file widget link; retain file replacement controls.
- Keep technical attachments on their existing protected preview/download routes.

## Touched surfaces

- `website/support_chat.py`
- `website/urls.py`
- `website/admin.py`
- `website/test_order_image_preview.py`
- `scripts/host/phase50_order_admin_media_preview_deploy.sh`
- Project status/error/changelog/request/roadmap docs and this phase record.

## Must not touch

- Order/customer/photo/attachment database rows, uploaded files, media paths, or schema/migrations.
- Public media allowlists, Store media, unrelated site/social/video code, or other project routes.
- Dirty canonical Windows checkout and unrelated WIP.

## Regression and safety gates

- Owner and staff can view both order images and reference photos; unrelated customers receive 404.
- Admin gallery emits protected image URLs and no `/media/orders/` links.
- Existing image and attachment bytes stay in place; all current order #1 uploads must exist before deploy.
- Local tests (currently 6/6), Django check, no-migration check, compile, Bash syntax and diff hygiene must pass.
- Production promotion is GitHub-first and exact-baseline; it backs up source and `.env`, uses fast-forward only, and performs no DB writes, migration, media move, public-route change or collectstatic.
- Post-restart runner reads all four reference images through the protected endpoint and renders order #1 gallery read-only.

## Exact identities

- Initial Host/runtime baseline: `d1f4ecc9d5f69997df8ef6ddfc053c35cc40e04f`; first promoted runtime SHA `505c3a46eaf03b31440152b15850620ee77541e6`, Host branch label `release/phase50-a2j-hero-20260915`.
- GitHub source lineage: `release/phase50-a2w-service-seo-20261010`, which contains the exact Host baseline.
- Worktree: `D:\projects\3DPrintHub-order-media-preview-20261107`, branch `fix/phase50-order-admin-media-preview-20261107`.
- First promotion fast-forwarded to `505c3a46eaf03b31440152b15850620ee77541e6`, created verified rollback bundle and `.env` checksums at `/home/sfkilvrs/3dprinthub-deploy-backups/20261107-154308-phase50-order-admin-media-preview`, and restarted Passenger. The runner's gallery assertion initially counted one URL per photo, but the HTML correctly contains the same protected URL twice (image `src` and clickable `href`). Follow-up Host read-only probe confirmed all four endpoints return `200 image/jpeg` with JPEG bytes and the gallery contains four cards/eight URL occurrences.
- Runner/gallery verification is complete at `17d60f732797751e3ea09fa3e132e8682b9786e0`; browser refresh showed a remaining admin inline/widget display issue and identified the final current diff. Deploy the inline/current-file widget fix from this baseline, then confirm all four images in the authenticated browser. Record final SHA/backup evidence afterward.
