#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
DB="sfkilvrs_EmiAdmin_3dprinthub"
HOST_BRANCH="release/phase50-a2j-hero-20260915"
RELEASE_BRANCH="release/phase50-a2t-google-indexing-20261008"
BASE="c4cf19504081b8ccc9ed9cbeed392d44745a24ba"
TARGET="$1"
BACKUPS="/home/sfkilvrs/3dprinthub-deploy-backups"
BACKUP="$BACKUPS/$(date +%Y%m%d-%H%M%S)-phase50-a2u-seo"
DELTA="$(mktemp)"
PROBE="$BACKUPS/.a2u-quota-probe-$(date +%s)-$$"
trap 'rm -f -- "$DELTA" "$PROBE"' EXIT
fail(){ echo "PHASE50_A2U_DEPLOY_FAIL=$1" >&2; exit 1; }

cd "$ROOT"
test -x "$PY" || fail wrong_python
test "$(git rev-parse HEAD)" = "$BASE" || fail wrong_host_baseline
test "$(git branch --show-current)" = "$HOST_BRANCH" || fail wrong_host_branch
test -z "$(git status --porcelain --untracked-files=all)" || fail dirty_host
case "$(git remote get-url origin)" in
  *farazha2203/3dprinthub.git|*farazha2203/3dprinthub) ;;
  *) fail wrong_origin ;;
esac
test -d "$BACKUPS" || fail missing_backup_root

"$PY" - <<'PY'
import re, subprocess
out = subprocess.run(
    ["uapi", "StatsBar", "get_stats", "display=diskusage"],
    capture_output=True, text=True, check=True, timeout=30,
).stdout
used = re.search(r"(?m)^ *_count: *'?([0-9]+)", out)
limit = re.search(r"(?m)^ *_max: *'?([0-9]+)", out)
assert used and limit and int(limit.group(1)) == 2000, "CPANEL_QUOTA_UNVERIFIED"
print("CPANEL_REPORTED_MB=" + used.group(1) + "/2000")
PY

# StatsBar can serve a delayed usage counter, so prove real user quota by
# a fresh bounded, fsynced write in the exact account; always remove it.
reserve(){
  local count="$1"
  test ! -e "$PROBE" || fail probe_path_busy
  dd if=/dev/zero of="$PROBE" bs=1048576 count="$count" conv=fsync status=none ||
    fail real_quota_reservation_failed
  test "$(stat -c %s "$PROBE")" -eq "$((count * 1048576))" ||
    fail quota_reservation_incomplete
  rm -f -- "$PROBE"
  echo "REAL_ACCOUNT_RESERVE_MIB=$count PASS"
}
reserve 48

LIVE="$(git ls-remote origin "refs/heads/$RELEASE_BRANCH" | awk '{print $1}')"
test "$LIVE" = "$TARGET" || fail github_sha_changed
git fetch --no-tags origin "refs/heads/$RELEASE_BRANCH"
FETCHED="$(git rev-parse FETCH_HEAD)"
test "$FETCHED" = "$TARGET" || fail fetched_sha_changed
git merge-base --is-ancestor "$BASE" "$FETCHED" || fail not_fast_forward
git diff --name-only "$BASE" "$FETCHED" > "$DELTA"
cat "$DELTA"
while IFS= read -r changed; do
  case "$changed" in
    store/views.py|store/sitemaps.py|templates/store/product_list.html|store/test_phase50_a2u_category_seo.py|scripts/seo/phase50_live_seo_audit.py|scripts/host/phase50_a2u_seo_category_deploy.sh|scripts/host/test_phase50_a2u_deploy_runner.py|docs/CURRENT_STATE.md|docs/ROADMAP.md|docs/CHANGELOG.md|docs/ERRORS.md|docs/REQUESTS.md|docs/HOST_CONSTRAINTS.md|docs/phases/PHASE50_A2T_GOOGLE_POST_READINESS.md|docs/phases/PHASE50_A2U_SEO_CATEGORY_INDEXABILITY_AUDIT.md) ;;
    *) fail "unexpected_release_file:$changed" ;;
  esac
done < "$DELTA"
for file in store/views.py store/sitemaps.py templates/store/product_list.html store/test_phase50_a2u_category_seo.py; do
  grep -Fxq "$file" "$DELTA" || fail "required_file_missing:$file"
done
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
"$PY" - "$DB" <<'PY'
import os, django, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
assert connection.vendor == "mysql"
assert connection.settings_dict["NAME"] == sys.argv[1]
assert not MigrationExecutor(connection).migration_plan(MigrationExecutor(connection).loader.graph.leaf_nodes())
print("MYSQL_IDENTITY_EMPTY_MIGRATION_PLAN=PASS")
PY
reserve 32

mkdir "$BACKUP"
chmod 700 "$BACKUP"
printf '%s\n' "$BASE" > "$BACKUP/prior-sha.txt"
printf '%s\n' "$TARGET" > "$BACKUP/target-sha.txt"
cp -p store/views.py "$BACKUP/store-views.py"
cp -p store/sitemaps.py "$BACKUP/store-sitemaps.py"
cp -p templates/store/product_list.html "$BACKUP/product-list.html"
test -f .env || fail missing_protected_env
cp -p .env "$BACKUP/.env"
chmod 600 "$BACKUP/.env"
(cd "$BACKUP" && sha256sum store-views.py store-sitemaps.py product-list.html .env > source.sha256)
export PHASE49_PROJECT_ROOT="$ROOT"
export PHASE49_BACKUP_ROOT="$BACKUP"
"$PY" scripts/host/phase49_3i53_mysql_backup.py "$DB"
gzip -t "$BACKUP/database-before-3i53.sql.gz"
(cd "$BACKUP" && sha256sum database-before-3i53.sql.gz > database.sha256 &&
  sha256sum -c source.sha256 database.sha256)
echo "FRESH_SCOPED_SOURCE_ENV_FULL_MYSQL_ROLLBACK=PASS"
echo "A2U_BACKUP_ROOT=$BACKUP"

git merge --ff-only "$FETCHED"
test "$(git rev-parse HEAD)" = "$TARGET" || fail wrong_deployed_sha
test -z "$(git status --porcelain --untracked-files=all)" || fail postmerge_dirty
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
"$PY" manage.py collectstatic --noinput
mkdir -p tmp
touch tmp/restart.txt
echo "PHASE50_A2U_DEPLOY_CODE=PASS"
echo "A2U_PRODUCTION_SHA=$(git rev-parse HEAD)"
