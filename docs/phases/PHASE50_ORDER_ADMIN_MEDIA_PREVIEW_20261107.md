# Phase50 — Protected order upload image previews

Status: `LOCAL_TESTED / GITHUB_UPDATE_PENDING / PRODUCTION_RUNTIME_AT_d1f4ecc9`.

## Request and verified cause

After the order #1 admin page was repaired, the owner showed broken previews for its uploaded reference photos and a Not Found tab. Production read-only checks proved all four `OrderReferencePhoto` files and the STEP attachment exist. The effective `MEDIA_ROOT` is `/home/sfkilvrs/3dprinthub/media`; Production intentionally serves only selected public Store media namespaces through `/media/`, so `/media/orders/reference/...` is not a valid public URL. This is a protected-media routing mismatch, not missing uploads.

## Requested delta

- Render order and reference images through one authenticated, ownership-checked image route.
- Reuse the route in the Order admin gallery, image inline, and reference-photo admin thumbnail.
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
- Local tests, Django check, no-migration check, compile, Bash syntax and diff hygiene must pass.
- Production promotion is GitHub-first and exact-baseline; it backs up source and `.env`, uses fast-forward only, and performs no DB writes, migration, media move, public-route change or collectstatic.
- Post-restart runner reads all four reference images through the protected endpoint and renders order #1 gallery read-only.

## Exact identities

- Current Host/runtime baseline: `d1f4ecc9d5f69997df8ef6ddfc053c35cc40e04f`, Host branch label `release/phase50-a2j-hero-20260915`.
- GitHub source lineage: `release/phase50-a2w-service-seo-20261010`, which contains the exact Host baseline.
- Worktree: `D:\projects\3DPrintHub-order-media-preview-20261107`, branch `fix/phase50-order-admin-media-preview-20261107`.
- Remaining: commit/push, guarded Host promotion, authenticated browser check of the four images, and exact backup/SHA documentation closure.
