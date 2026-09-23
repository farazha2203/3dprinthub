#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
EXPECTED_DB="sfkilvrs_EmiAdmin_3dprinthub"
HOST_BRANCH="release/phase50-a2j-hero-20260915"
TARGET_BRANCH="release/phase50-a2r-video-social-20260923"
EXPECTED_BASELINE="e03bdd2b718fae3ce030df789c8b9db958d8d8ed"
TARGET_SHA="${1:-}"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="/home/sfkilvrs/3dprinthub-deploy-backups/${STAMP}-phase50-a2r-video-media"
TMP_DELTA="/tmp/3dprinthub-a2r-video-delta-$$.txt"

cleanup(){ rm -f "$TMP_DELTA" 2>/dev/null || true; }
trap cleanup EXIT
fail(){
  printf 'A2R_VIDEO_DEPLOY_FAIL=%s\n' "$1" >&2
  printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT" >&2
  exit 1
}

[ -n "$TARGET_SHA" ] || fail "target_sha_required"
cd "$ROOT"
[ -d .git ] || fail "project_git_missing"
[ "$(git branch --show-current)" = "$HOST_BRANCH" ] || fail "wrong_host_branch"
[ "$(git rev-parse HEAD)" = "$EXPECTED_BASELINE" ] || fail "host_baseline_changed"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "production_worktree_dirty"
case "$(git remote get-url origin)" in
  *farazha2203/3dprinthub.git|*farazha2203/3dprinthub) ;;
  *) fail "wrong_repository" ;;
esac

"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
"$PY" - "$EXPECTED_DB" <<'PY'
import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from catalog_bridge.publish_readiness import publish_readiness

expected = sys.argv[1]
print("DB_VENDOR=" + str(connection.vendor))
print("DB_NAME=" + str(connection.settings_dict.get("NAME") or ""))
if connection.vendor != "mysql" or str(connection.settings_dict.get("NAME") or "") != expected:
    raise SystemExit("A2R_VIDEO_DEPLOY_FAIL=database_identity_mismatch")
executor = MigrationExecutor(connection)
plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
print("MIGRATION_PLAN_COUNT=" + str(len(plan)))
if plan:
    raise SystemExit("A2R_VIDEO_DEPLOY_FAIL=migration_plan_not_empty")
ready = publish_readiness()
print("PUBLISH_READY=" + str(bool(ready.get("ready"))))
if ready.get("ready") is not True:
    raise SystemExit("A2R_VIDEO_DEPLOY_FAIL=receiver_not_ready")
PY

REMOTE_SHA="$(git ls-remote origin "refs/heads/$TARGET_BRANCH" | cut -f1)"
printf 'REMOTE_SHA=%s\n' "$REMOTE_SHA"
[ "$REMOTE_SHA" = "$TARGET_SHA" ] || fail "target_not_live_github_head"
git fetch --no-tags origin "refs/heads/$TARGET_BRANCH"
FETCHED="$(git rev-parse FETCH_HEAD)"
[ "$FETCHED" = "$TARGET_SHA" ] || fail "fetched_target_mismatch"
git merge-base --is-ancestor "$EXPECTED_BASELINE" "$FETCHED" || fail "target_not_fast_forward"
git diff --name-only "$EXPECTED_BASELINE" "$FETCHED" > "$TMP_DELTA"
printf '%s\n' "===== A2R VIDEO DELTA ====="
cat "$TMP_DELTA"

if grep -Eq '(^|/)migrations/[0-9]{4}_[^/]+\.py$|^requirements[^/]*\.txt$|^config/settings|(^|/)\.env$' "$TMP_DELTA"; then
  fail "migration_dependency_settings_or_env_delta_detected"
fi

while IFS= read -r changed; do
  case "$changed" in
    docs/CHANGELOG.md|docs/CURRENT_STATE.md|docs/ERRORS.md|docs/REQUESTS.md|docs/ROADMAP.md|docs/phases/PHASE50_A2R_CATALOG_VIDEO_INSTAGRAM.md|scripts/host/phase50_a2r_video_media_deploy.sh|store/management/commands/phase37_import_catalog_center.py|store/test_phase50_a2r_video.py|templates/store/product_detail.html)
      ;;
    *)
      fail "unexpected_target_delta:$changed"
      ;;
  esac
done < "$TMP_DELTA"

for required in   store/management/commands/phase37_import_catalog_center.py   templates/store/product_detail.html   store/test_phase50_a2r_video.py   scripts/host/phase50_a2r_video_media_deploy.sh
do
  grep -Fxq "$required" "$TMP_DELTA" || fail "required_delta_missing:$required"
done

mkdir -p   "$BACKUP_ROOT/files/store/management/commands"   "$BACKUP_ROOT/files/templates/store"
chmod 700 "$BACKUP_ROOT"
printf '%s\n' "$EXPECTED_BASELINE" > "$BACKUP_ROOT/source-head.txt"
printf '%s\n' "$HOST_BRANCH" > "$BACKUP_ROOT/source-branch.txt"
cp -p store/management/commands/phase37_import_catalog_center.py   "$BACKUP_ROOT/files/store/management/commands/phase37_import_catalog_center.py"
cp -p templates/store/product_detail.html   "$BACKUP_ROOT/files/templates/store/product_detail.html"
if [ -f .env ]; then
  cp -p .env "$BACKUP_ROOT/.env"
  chmod 600 "$BACKUP_ROOT/.env"
fi
(
  cd "$BACKUP_ROOT"
  sha256sum files/store/management/commands/phase37_import_catalog_center.py > runtime-files.sha256
  sha256sum files/templates/store/product_detail.html >> runtime-files.sha256
  sha256sum -c runtime-files.sha256
  if [ -f .env ]; then
    sha256sum .env > env.sha256
    sha256sum -c env.sha256
  fi
)

export PHASE49_PROJECT_ROOT="$ROOT"
export PHASE49_BACKUP_ROOT="$BACKUP_ROOT"
"$PY" scripts/host/phase49_3i53_mysql_backup.py "$EXPECTED_DB"
gzip -t "$BACKUP_ROOT/database-before-3i53.sql.gz"
sha256sum "$BACKUP_ROOT/database-before-3i53.sql.gz" > "$BACKUP_ROOT/database-before.sha256"
(cd "$BACKUP_ROOT" && sha256sum -c database-before.sha256)
printf 'PREDEPLOY_BACKUP_VERIFIED=YES\n'
printf 'ROLLBACK_HEAD=%s\n' "$EXPECTED_BASELINE"
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"

git merge --ff-only "$FETCHED"
[ "$(git rev-parse HEAD)" = "$TARGET_SHA" ] || fail "deployed_head_mismatch"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "worktree_dirty_after_merge"

"$PY" -m py_compile store/management/commands/phase37_import_catalog_center.py
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
"$PY" - "$EXPECTED_DB" <<'PY'
import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from catalog_bridge.publish_readiness import publish_readiness

expected = sys.argv[1]
if connection.vendor != "mysql" or str(connection.settings_dict.get("NAME") or "") != expected:
    raise SystemExit("A2R_VIDEO_DEPLOY_FAIL=post_database_identity_mismatch")
executor = MigrationExecutor(connection)
plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
print("POST_MIGRATION_PLAN_COUNT=" + str(len(plan)))
if plan:
    raise SystemExit("A2R_VIDEO_DEPLOY_FAIL=post_migration_plan_not_empty")
ready = publish_readiness()
print("POST_PUBLISH_READY=" + str(bool(ready.get("ready"))))
if ready.get("ready") is not True:
    raise SystemExit("A2R_VIDEO_DEPLOY_FAIL=post_receiver_not_ready")
PY

mkdir -p tmp
touch tmp/restart.txt
sleep 4

"$PY" - <<'PY'
from urllib import request
base = "https://3dprinthub.ir"
headers = {"User-Agent": "3DPrintHub-A2R-Video/1.0", "Cache-Control": "no-cache"}
for path in ("/", "/store/"):
    with request.urlopen(request.Request(base + path, headers=headers), timeout=20) as response:
        print("PUBLIC_HTTP=" + str(response.status) + " " + path)
        if response.status != 200:
            raise SystemExit("A2R_VIDEO_DEPLOY_FAIL=public_http_failed")
print("A2R_VIDEO_PUBLIC_SMOKE=PASS")
PY

printf 'FINAL_HEAD=%s\n' "$(git rev-parse HEAD)"
printf 'FINAL_WORKTREE=%s\n' "$(test -z "$(git status --porcelain --untracked-files=all)" && printf CLEAN || printf DIRTY)"
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"
printf 'PHASE50_A2R_VIDEO_MEDIA_DEPLOY=PASS\n'
