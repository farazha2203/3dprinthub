# Phase50 — Service Order #1 admin attachment 500

Status: `LOCAL_TESTED / GITHUB_UPDATE_PENDING / PRODUCTION_UNCHANGED`.

## Request and verified cause

The owner reports that dashboard order `website.Order #1` is visible but its admin detail URL `/admin/website/order/1/change/` returns HTTP 500. Production read-only reproduction established that `OrderAdmin.media_gallery()` evaluates `OrderAttachment.is_image`; `OrderAttachment.extension` calls `Path(...)`, but `website/models.py` had no `pathlib.Path` import. That `NameError` is the page failure. Order #1 exists and its attachment records are present; do not rewrite, delete, or recreate them.

## Requested delta

- Import `pathlib.Path` so private order attachment classification works.
- Add focused regression tests for case-insensitive image/PDF/unknown extensions and fallback to the stored filename.
- Promote only through the dedicated 3DPrintHub reverse route, from the exact Host baseline and a GitHub release descendant.

## Touched surfaces

- `website/models.py`
- `website/test_order_attachment_extension.py`
- `scripts/host/phase50_order_admin_attachment_500_deploy.sh`
- This phase record and required project status/error/changelog/request/roadmap documents.

## Must not touch

- Order/customer/attachment database rows, private media, or schema/migrations.
- Instagram/video/story workflows, Catalog Center, unrelated storefront/SEO code, or other project routes.
- Dirty canonical Windows checkout and unrelated WIP.

## Regression and safety gates

- Focused Django tests: 2/2 pass.
- `manage.py check`: pass with existing OAuth, CKEditor, and in-memory realtime warnings.
- `makemigrations --check --dry-run`: no changes.
- Python compile, deploy-runner Bash syntax, and `git diff --check`: pass.
- Production promotion must prove exact Host branch/HEAD/clean state, expected MySQL identity, empty migration plan, order #1 plus attachment presence, GitHub target ancestry, verified source/environment backup, and read-only post-restart `OrderAdmin.media_gallery(order)` rendering.
- Deployment must perform no database write, migration, media operation, collectstatic, or unrelated release.

## Exact identities and remaining work

- Host baseline: `76f12e22c3ba62913ad0701abac986c9a7bbfb50`, branch label `release/phase50-a2j-hero-20260915`.
- This Host commit is an ancestor of GitHub `release/phase50-a2w-service-seo-20261010`; the similarly named A2J GitHub branch is divergent and must not be used for this promotion.
- Local fix worktree: `D:\projects\3DPrintHub-order-hotfix-prod-20261107`; branch `fix/phase50-order-admin-attachment-path-prod-20261107`.
- Remaining: commit and push the narrow release descendant, run the guarded Host promotion, verify the admin rendering and live URL, then close documentation with exact SHA/backup evidence.
