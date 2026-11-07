#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
ROOT=/home/sfkilvrs/3dprinthub
PY=/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python
HOST_BRANCH=release/phase50-a2j-hero-20260915
GITHUB_BRANCH=release/phase50-a2w-service-seo-20261010
EXPECTED_DB=sfkilvrs_EmiAdmin_3dprinthub
EXPECTED_BASELINE=d1f4ecc9d5f69997df8ef6ddfc053c35cc40e04f
[ "$#" -eq 1 ] || { echo target_sha_required >&2; exit 1; }
TARGET_SHA="$1"
BACKUP_BASE=/home/sfkilvrs/3dprinthub-deploy-backups
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="$BACKUP_BASE/$STAMP-phase50-order-admin-media-preview"
TMP_DELTA="/tmp/3dprinthub-order-media-preview-delta-$$.txt"
trap 'rm -f "$TMP_DELTA" 2>/dev/null || true' EXIT
fail() { printf 'PHASE50_ORDER_MEDIA_PREVIEW_DEPLOY_FAIL=%s\n' "$1" >&2; printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT" >&2; exit 1; }

printf '%s\n' 'Order #1 protected uploaded-image preview hotfix'
printf '%s\n' 'GITHUB -> VERIFIED SOURCE/ENV BACKUP -> FF-ONLY -> RESTART -> READ-ONLY VERIFY'
printf '%s\n' 'NO MIGRATION / NO DATABASE WRITE / NO FILE MOVE / NO COLLECTSTATIC'
[ -d "$ROOT/.git" ] && [ -x "$PY" ] || fail project_or_python_missing
cd "$ROOT"
ORIGIN="$(git remote get-url origin)"
CURRENT_BRANCH="$(git branch --show-current)"
CURRENT_HEAD="$(git rev-parse HEAD)"
STATUS="$(git status --porcelain --untracked-files=all)"
printf 'ORIGIN=%s\nHOST_BRANCH=%s\nHOST_HEAD=%s\nEXPECTED_BASELINE=%s\nTARGET_SHA=%s\n' "$ORIGIN" "$CURRENT_BRANCH" "$CURRENT_HEAD" "$EXPECTED_BASELINE" "$TARGET_SHA"
case "$ORIGIN" in *farazha2203/3dprinthub.git|*farazha2203/3dprinthub) ;; *) fail wrong_repository ;; esac
[ "$CURRENT_BRANCH" = "$HOST_BRANCH" ] || fail host_branch_changed
[ "$CURRENT_HEAD" = "$EXPECTED_BASELINE" ] || fail host_baseline_changed
[ -z "$STATUS" ] || { printf '%s\n' "$STATUS"; fail production_worktree_dirty; }

"$PY" - "$EXPECTED_DB" <<'PY'
import os,sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
import django; django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from website.models import Order,OrderReferencePhoto,OrderAttachment
if connection.vendor!="mysql" or str(connection.settings_dict.get("NAME") or "")!=sys.argv[1]: raise SystemExit("database_identity_mismatch")
ex=MigrationExecutor(connection); plan=ex.migration_plan(ex.loader.graph.leaf_nodes())
print("DB_IDENTITY=PASS"); print("MIGRATION_PLAN_COUNT="+str(len(plan)))
if plan: raise SystemExit("migration_plan_not_empty")
if not Order.objects.filter(pk=1).exists(): raise SystemExit("order_1_missing")
photos=list(OrderReferencePhoto.objects.filter(order_id=1).order_by("id")); files=list(OrderAttachment.objects.filter(order_id=1))
print("ORDER_1_REFERENCE_PHOTOS="+str(len(photos))); print("ORDER_1_ATTACHMENTS="+str(len(files)))
if len(photos)!=4 or len(files)!=1: raise SystemExit("order_1_media_inventory_changed")
if any(not x.image or not x.image.storage.exists(x.image.name) for x in photos): raise SystemExit("reference_photo_file_missing")
if any(not x.file or not x.file.storage.exists(x.file.name) for x in files): raise SystemExit("order_attachment_file_missing")
print("EXISTING_UPLOAD_FILES=ALL_PRESENT")
PY
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run

REMOTE_LINE="$(git ls-remote origin "refs/heads/$GITHUB_BRANCH")"
[ -n "$REMOTE_LINE" ] || fail github_release_branch_missing
REMOTE_SHA="$(printf '%s\n' "$REMOTE_LINE" | awk '{print $1}')"
[ "$REMOTE_SHA" = "$TARGET_SHA" ] || fail target_not_live_github_head
git fetch --no-tags origin "refs/heads/$GITHUB_BRANCH"
FETCHED="$(git rev-parse FETCH_HEAD)"
[ "$FETCHED" = "$TARGET_SHA" ] || fail fetched_target_mismatch
git merge-base --is-ancestor "$EXPECTED_BASELINE" "$FETCHED" || fail target_not_fast_forward
git diff --name-only "$EXPECTED_BASELINE" "$FETCHED" > "$TMP_DELTA"
while IFS= read -r path; do
  [ -n "$path" ] || continue
  case "$path" in website/admin.py|website/support_chat.py|website/urls.py|website/test_order_image_preview.py|docs/*|PROJECT_CONTEXT.md|scripts/host/phase50_order_admin_media_preview_deploy.sh) ;; *) fail "unexpected_target_delta:$path" ;; esac
done < "$TMP_DELTA"
for path in website/admin.py website/support_chat.py website/urls.py; do
  git diff --quiet "$EXPECTED_BASELINE" "$FETCHED" -- "$path" && fail "required_runtime_delta_missing:$path"
done
if grep -Eq '(^|/)migrations/[0-9]{4}_[^/]+\.py$|^requirements[^/]*\.txt$|^config/settings' "$TMP_DELTA"; then fail forbidden_schema_dependency_or_settings_delta; fi
printf '%s\n' 'NO_SCHEMA_DEPENDENCY_OR_SETTINGS_DELTA=PASS'

mkdir -p "$BACKUP_ROOT"; chmod 700 "$BACKUP_ROOT"
git bundle create "$BACKUP_ROOT/source-before.bundle" HEAD
git bundle verify "$BACKUP_ROOT/source-before.bundle"
printf '%s\n' "$CURRENT_HEAD" > "$BACKUP_ROOT/source-head.txt"
printf '%s\n' "$CURRENT_BRANCH" > "$BACKUP_ROOT/source-branch.txt"
[ -f .env ] || fail production_env_missing
cp -p .env "$BACKUP_ROOT/.env"; chmod 600 "$BACKUP_ROOT/.env"
sha256sum "$BACKUP_ROOT/source-before.bundle" > "$BACKUP_ROOT/source-bundle.sha256"
sha256sum "$BACKUP_ROOT/.env" > "$BACKUP_ROOT/env.sha256"
(cd "$BACKUP_ROOT" && sha256sum -c source-bundle.sha256 && sha256sum -c env.sha256)
printf 'BACKUP_ROOT=%s\nPREDEPLOY_BACKUP_VERIFIED=YES\n' "$BACKUP_ROOT"

git merge --ff-only "$FETCHED"
[ "$(git rev-parse HEAD)" = "$TARGET_SHA" ] || fail deployed_head_mismatch
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail worktree_dirty_after_merge
mkdir -p tmp; touch tmp/restart.txt; sleep 4

"$PY" - <<'PY'
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
import django; django.setup()
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory
from django.urls import reverse,resolve
from website.admin import OrderAdmin
from website.models import Order,OrderReferencePhoto
from website.support_chat import order_image_preview
order=Order.objects.get(pk=1); photos=list(OrderReferencePhoto.objects.filter(order=order).order_by("id"))
if len(photos)!=4: raise SystemExit("order_1_reference_photo_count_mismatch")
gallery=str(OrderAdmin(Order,AdminSite()).media_gallery(order))
if gallery.count("secure-order-images/reference/")!=4: raise SystemExit("protected_gallery_links_mismatch")
staff=get_user_model().objects.filter(is_superuser=True,is_staff=True).order_by("id").first()
if staff is None: raise SystemExit("staff_permission_probe_user_missing")
factory=RequestFactory()
for photo in photos:
    url=reverse("website:order_image_preview",args=["reference",photo.pk])
    if resolve(url).func is not order_image_preview: raise SystemExit("secure_route_resolution_failed")
    request=factory.get(url); request.user=staff
    response=order_image_preview(request,"reference",photo.pk)
    try:
        if response.status_code!=200 or not str(response.get("Content-Type","")).startswith("image/"):
            raise SystemExit("protected_preview_response_invalid")
        if not next(iter(response.streaming_content),b""): raise SystemExit("protected_preview_file_empty")
    finally: response.close()
print("ORDER_1_PROTECTED_REFERENCE_PREVIEWS=4/4")
print("ORDER_1_ADMIN_GALLERY=RENDERED")
PY
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
printf 'DEPLOYED_HEAD=%s\n' "$(git rev-parse HEAD)"
printf 'FINAL_WORKTREE=%s\n' "$(test -z "$(git status --porcelain --untracked-files=all)" && printf CLEAN || printf DIRTY)"
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"
printf '%s\n' 'PHASE50_ORDER_ADMIN_MEDIA_PREVIEW_DEPLOY=PASS'
