#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
HOST_BRANCH="release/phase50-a2j-hero-20260915"
GITHUB_BRANCH="release/phase50-a2w-service-seo-20261010"
EXPECTED_DB="sfkilvrs_EmiAdmin_3dprinthub"
EXPECTED_BASELINE="76f12e22c3ba62913ad0701abac986c9a7bbfb50"
TARGET_SHA="${1:-}"
BACKUP_BASE="/home/sfkilvrs/3dprinthub-deploy-backups"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="$BACKUP_BASE/${STAMP}-phase50-order-admin-attachment-500"
TMP_DELTA="/tmp/3dprinthub-order-admin-delta-$$.txt"

cleanup() { rm -f "$TMP_DELTA" 2>/dev/null || true; }
trap cleanup EXIT
fail() {
  printf 'PHASE50_ORDER_ADMIN_500_DEPLOY_FAIL=%s\n' "$1" >&2
  printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT" >&2
  exit 1
}

printf '%s\n' "3DPrintHub Order #1 admin attachment 500 hotfix"
printf '%s\n' "GITHUB FETCH -> VERIFIED SOURCE/ENV BACKUP -> FF-ONLY -> RESTART -> READ-ONLY VERIFY"
printf '%s\n' "NO MIGRATION / NO DATABASE WRITE / NO MEDIA CHANGE / NO COLLECTSTATIC"
[ -n "$TARGET_SHA" ] || fail "target_sha_required"
[ -d "$ROOT/.git" ] || fail "project_root_or_git_missing"
[ -x "$PY" ] || fail "production_python_missing"
cd "$ROOT"

ORIGIN="$(git remote get-url origin)"
CURRENT_BRANCH="$(git branch --show-current)"
CURRENT_HEAD="$(git rev-parse HEAD)"
STATUS="$(git status --porcelain --untracked-files=all)"
printf 'ROOT=%s\nORIGIN=%s\nHOST_BRANCH=%s\nHOST_HEAD=%s\nEXPECTED_BASELINE=%s\nTARGET_SHA=%s\n' \
  "$ROOT" "$ORIGIN" "$CURRENT_BRANCH" "$CURRENT_HEAD" "$EXPECTED_BASELINE" "$TARGET_SHA"
case "$ORIGIN" in *farazha2203/3dprinthub.git|*farazha2203/3dprinthub) ;; *) fail "wrong_repository" ;; esac
[ "$CURRENT_BRANCH" = "$HOST_BRANCH" ] || fail "host_branch_changed"
[ "$CURRENT_HEAD" = "$EXPECTED_BASELINE" ] || fail "host_baseline_changed"
[ -z "$STATUS" ] || { printf '%s\n' "$STATUS"; fail "production_worktree_dirty"; }

printf '%s\n' "===== READ-ONLY DATABASE / ORDER PREFLIGHT ====="
"$PY" - "$EXPECTED_DB" <<'PY'
import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django; django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from website.models import Order, OrderAttachment
expected=sys.argv[1]
if connection.vendor != "mysql": raise SystemExit("database_vendor_not_mysql")
if str(connection.settings_dict.get("NAME") or "") != expected: raise SystemExit("database_name_mismatch")
executor=MigrationExecutor(connection)
plan=executor.migration_plan(executor.loader.graph.leaf_nodes())
print("DB_IDENTITY=PASS")
print("MIGRATION_PLAN_COUNT="+str(len(plan)))
if plan: raise SystemExit("migration_plan_not_empty")
if not Order.objects.filter(pk=1).exists(): raise SystemExit("order_1_missing")
attachment_count=OrderAttachment.objects.filter(order_id=1).count()
print("ORDER_1_EXISTS=YES")
print("ORDER_1_ATTACHMENT_COUNT="+str(attachment_count))
if attachment_count < 1: raise SystemExit("expected_order_attachment_missing")
PY
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run

printf '%s\n' "===== LIVE GITHUB TARGET / EXPLICIT FETCH ====="
REMOTE_LINE="$(git ls-remote origin "refs/heads/$GITHUB_BRANCH")"
[ -n "$REMOTE_LINE" ] || fail "github_release_branch_missing"
REMOTE_SHA="$(printf '%s\n' "$REMOTE_LINE" | awk '{print $1}')"
[ "$REMOTE_SHA" = "$TARGET_SHA" ] || fail "target_not_live_github_head"
git fetch --no-tags origin "refs/heads/$GITHUB_BRANCH"
FETCHED="$(git rev-parse FETCH_HEAD)"
[ "$FETCHED" = "$TARGET_SHA" ] || fail "fetched_target_mismatch"
git merge-base --is-ancestor "$EXPECTED_BASELINE" "$FETCHED" || fail "target_not_fast_forward_from_production"
git diff --name-only "$EXPECTED_BASELINE" "$FETCHED" > "$TMP_DELTA"
printf '%s\n' "===== TARGET DELTA ====="
cat "$TMP_DELTA"
while IFS= read -r path; do
  [ -n "$path" ] || continue
  case "$path" in
    website/models.py|website/test_order_attachment_extension.py|docs/*|PROJECT_CONTEXT.md|scripts/host/phase50_order_admin_attachment_500_deploy.sh) ;;
    *) fail "unexpected_target_delta:$path" ;;
  esac
done < "$TMP_DELTA"
if git diff --quiet "$EXPECTED_BASELINE" "$FETCHED" -- website/models.py; then fail "runtime_fix_missing"; fi
if grep -Eq '(^|/)migrations/[0-9]{4}_[^/]+\.py$|^requirements[^/]*\.txt$|^config/settings' "$TMP_DELTA"; then
  fail "migration_dependency_or_settings_delta_detected"
fi
printf '%s\n' "NO_SCHEMA_DEPENDENCY_OR_SETTINGS_DELTA=PASS"

printf '%s\n' "===== VERIFIED SOURCE / ENV BACKUP ====="
mkdir -p "$BACKUP_ROOT"; chmod 700 "$BACKUP_ROOT"
git bundle create "$BACKUP_ROOT/source-before.bundle" HEAD
git bundle verify "$BACKUP_ROOT/source-before.bundle"
printf '%s\n' "$CURRENT_HEAD" > "$BACKUP_ROOT/source-head.txt"
printf '%s\n' "$CURRENT_BRANCH" > "$BACKUP_ROOT/source-branch.txt"
[ -f .env ] || fail "production_env_missing"
cp -p .env "$BACKUP_ROOT/.env"; chmod 600 "$BACKUP_ROOT/.env"
sha256sum "$BACKUP_ROOT/source-before.bundle" > "$BACKUP_ROOT/source-bundle.sha256"
sha256sum "$BACKUP_ROOT/.env" > "$BACKUP_ROOT/env.sha256"
(cd "$BACKUP_ROOT" && sha256sum -c source-bundle.sha256 && sha256sum -c env.sha256)
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"
printf '%s\n' "PREDEPLOY_BACKUP_VERIFIED=YES"

printf '%s\n' "===== FF-ONLY SOURCE PROMOTION ====="
git merge --ff-only "$FETCHED"
[ "$(git rev-parse HEAD)" = "$TARGET_SHA" ] || fail "deployed_head_mismatch"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "worktree_dirty_after_merge"

printf '%s\n' "===== PASSENGER RESTART ====="
mkdir -p tmp; touch tmp/restart.txt; sleep 4

printf '%s\n' "===== READ-ONLY ORDER ADMIN REGRESSION ====="
"$PY" - <<'PY'
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django; django.setup()
from django.contrib import admin
from website.models import Order
order=Order.objects.get(pk=1)
gallery=str(admin.site._registry[Order].media_gallery(order))
if "هیچ تصویر یا مدرکی ثبت نشده است" in gallery: raise SystemExit("order_media_gallery_empty")
if "admin-media-card" not in gallery: raise SystemExit("order_media_gallery_markup_missing")
print("ORDER_1_MEDIA_GALLERY=RENDERED")
print("ORDER_1_ADMIN_ATTACHMENT_PATH=PASS")
PY
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
printf 'DEPLOYED_HEAD=%s\n' "$(git rev-parse HEAD)"
printf 'FINAL_WORKTREE=%s\n' "$(test -z "$(git status --porcelain --untracked-files=all)" && printf CLEAN || printf DIRTY)"
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"
printf '%s\n' "PHASE50_ORDER_ADMIN_ATTACHMENT_500_DEPLOY=PASS"
