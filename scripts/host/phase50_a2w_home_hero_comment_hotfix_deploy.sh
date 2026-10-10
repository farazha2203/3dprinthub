#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
DB="sfkilvrs_EmiAdmin_3dprinthub"
HOST_BRANCH="release/phase50-a2j-hero-20260915"
RELEASE_BRANCH="release/phase50-a2w-service-seo-20261010"
BASE="5a1a6ea08abf6400661fbeb80dec03446500e158"
TARGET="${1:-}"
BACKUPS="/home/sfkilvrs/3dprinthub-deploy-backups"
BACKUP="$BACKUPS/$(date +%Y%m%d-%H%M%S)-phase50-a2w-home-hero-comment"
DELTA="$(mktemp)"
PROBE="$BACKUPS/.a2w-hero-quota-probe-$(date +%s)-$$"
trap 'rm -f -- "$DELTA" "$PROBE"' EXIT
fail(){ echo "PHASE50_A2W_HERO_DEPLOY_FAIL=$1" >&2; exit 1; }

test -n "$TARGET" || fail target_sha_required
cd "$ROOT"
test -d .git || fail project_git_missing
test -x "$PY" || fail production_python_missing
test "$(git rev-parse HEAD)" = "$BASE" || fail wrong_host_baseline
test "$(git branch --show-current)" = "$HOST_BRANCH" || fail wrong_host_branch
test -z "$(git status --porcelain --untracked-files=all)" || fail dirty_host
case "$(git remote get-url origin)" in *farazha2203/3dprinthub.git|*farazha2203/3dprinthub) ;; *) fail wrong_origin ;; esac
test -d "$BACKUPS" || fail backup_root_missing

"$PY" - <<'PY'
import re, subprocess
out = subprocess.run(["uapi", "StatsBar", "get_stats", "display=diskusage"], capture_output=True, text=True, check=True, timeout=30).stdout
used = re.search(r"(?m)^ *_count: *'?([0-9]+)", out)
limit = re.search(r"(?m)^ *_max: *'?([0-9]+)", out)
if not used or not limit or int(limit.group(1)) != 2000:
    raise SystemExit("CPANEL_QUOTA_UNVERIFIED")
print("CPANEL_REPORTED_MB=" + used.group(1) + "/2000")
PY

reserve(){
  local count="$1"
  test ! -e "$PROBE" || fail quota_probe_path_busy
  dd if=/dev/zero of="$PROBE" bs=1048576 count="$count" conv=fsync status=none || fail "real_quota_reservation_failed_${count}MiB"
  test "$(stat -c %s "$PROBE")" -eq "$((count * 1048576))" || fail quota_reservation_incomplete
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
while IFS= read -r changed; do
  case "$changed" in
    templates/website/partials/hero.html|website/test_phase50_a2k_tympanus_slicebox.py|scripts/host/phase50_a2w_home_hero_comment_hotfix_deploy.sh|scripts/host/test_phase50_a2w_home_hero_comment_hotfix_deploy.py|docs/CURRENT_STATE.md|docs/ROADMAP.md|docs/CHANGELOG.md|docs/ERRORS.md|docs/REQUESTS.md|docs/PATHS.md|docs/HOST_CONSTRAINTS.md|docs/phases/PHASE50_A2V_ISFAHAN_SEO_RELEASE.md|docs/phases/PHASE50_A2W_SERVICE_SEO.md) ;;
    *) fail "unexpected_release_file:$changed" ;;
  esac
done < "$DELTA"
for required in templates/website/partials/hero.html website/test_phase50_a2k_tympanus_slicebox.py scripts/host/test_phase50_a2w_home_hero_comment_hotfix_deploy.py; do
  grep -Fxq "$required" "$DELTA" || fail "required_delta_missing:$required"
done
if grep -Eq '(^|/)migrations/[0-9]{4}_[^/]+\.py$|^requirements[^/]*\.txt$|^config/settings|(^|/)\.env$' "$DELTA"; then fail migration_dependency_settings_or_env_delta; fi

"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
"$PY" - "$DB" <<'PY'
import os, sys, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
if connection.vendor != "mysql" or connection.settings_dict.get("NAME") != sys.argv[1]:
    raise SystemExit("MYSQL_DATABASE_IDENTITY_MISMATCH")
executor = MigrationExecutor(connection)
if executor.migration_plan(executor.loader.graph.leaf_nodes()):
    raise SystemExit("MIGRATION_PLAN_NOT_EMPTY")
print("MYSQL_IDENTITY_AND_EMPTY_MIGRATION_PLAN=PASS")
PY
reserve 32

mkdir "$BACKUP"
chmod 700 "$BACKUP"
printf '%s\n' "$BASE" > "$BACKUP/prior-sha.txt"
printf '%s\n' "$TARGET" > "$BACKUP/target-sha.txt"
mkdir "$BACKUP/source-before"
while IFS= read -r changed; do
  [ -n "$changed" ] || continue
  if [ -f "$ROOT/$changed" ]; then
    mkdir -p "$BACKUP/source-before/$(dirname "$changed")"
    cp -p "$ROOT/$changed" "$BACKUP/source-before/$changed"
  else
    printf '%s\n' "$changed" >> "$BACKUP/source-absent-before.txt"
  fi
done < "$DELTA"
test -f .env || fail protected_env_missing
cp -p .env "$BACKUP/.env"
chmod 600 "$BACKUP/.env"
(cd "$BACKUP/source-before" && find . -type f -print0 | sort -z | xargs -0 sha256sum) > "$BACKUP/source-before.sha256"
(cd "$BACKUP/source-before" && sha256sum -c "$BACKUP/source-before.sha256")
(cd "$BACKUP" && sha256sum .env > env.sha256 && sha256sum -c env.sha256)
export PHASE49_PROJECT_ROOT="$ROOT" PHASE49_BACKUP_ROOT="$BACKUP"
"$PY" scripts/host/phase49_3i53_mysql_backup.py "$DB"
gzip -t "$BACKUP/database-before-3i53.sql.gz"
(cd "$BACKUP" && sha256sum database-before-3i53.sql.gz > database.sha256 && sha256sum -c database.sha256)
echo "PREDEPLOY_SOURCE_ENV_DATABASE_BACKUP=PASS"
echo "BACKUP_ROOT=$BACKUP"

cat > "$BACKUP/rollback-source.sh" <<EOF
#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
cd "$ROOT"
test "\$(git branch --show-current)" = "$HOST_BRANCH"
test "\$(git rev-parse HEAD)" = "$TARGET"
test -z "\$(git status --porcelain --untracked-files=all)"
git reset --hard "$BASE"
test "\$(git rev-parse HEAD)" = "$BASE"
touch tmp/restart.txt
echo "ROLLBACK_SOURCE_SHA=$BASE"
EOF
chmod 700 "$BACKUP/rollback-source.sh"
sha256sum "$BACKUP/rollback-source.sh" > "$BACKUP/rollback-source.sha256"
sha256sum -c "$BACKUP/rollback-source.sha256"

git merge --ff-only "$FETCHED"
test "$(git rev-parse HEAD)" = "$TARGET" || fail deployed_sha_mismatch
test -z "$(git status --porcelain --untracked-files=all)" || fail dirty_after_merge
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
"$PY" manage.py collectstatic --noinput
mkdir -p tmp
touch tmp/restart.txt

for attempt in $(seq 1 12); do
  if "$PY" - <<'PY'
from urllib.request import Request, urlopen
import re
url = "https://3dprinthub.ir/"
request = Request(url, headers={"User-Agent":"3DPrintHub-A2W-Hero-Hotfix/1.0", "Cache-Control":"no-cache"})
with urlopen(request, timeout=20) as response:
    body = response.read().decode("utf-8", "replace")
    if response.status != 200:
        raise SystemExit("HOME_HTTP_STATUS=" + str(response.status))
if "A home-page Hero is a visual navigation list" in body:
    raise SystemExit("HOME_HERO_COMMENT_STILL_VISIBLE")
match = re.search(r'<ul[^>]*id="sb-slider"[^>]*>(.*?)</ul>', body, re.S)
if not match:
    raise SystemExit("HOME_HERO_SLIDER_MISSING")
hero = match.group(1)
slides = re.findall(r"<li(?:\s|>)", hero)
images = re.findall(r"<img\b", hero)
if not slides or len(slides) != len(images):
    raise SystemExit(f"HOME_HERO_IMAGE_PARITY_FAIL slides={len(slides)} images={len(images)}")
print(f"PUBLIC_HOME_HERO_SMOKE=PASS slides={len(slides)} images={len(images)} raw_comment=0")
PY
  then break; fi
  [ "$attempt" -lt 12 ] || fail public_home_hotfix_not_served
  sleep 5
done
echo "PHASE50_A2W_HERO_COMMENT_DEPLOY=PASS"
echo "PRODUCTION_SHA=$(git rev-parse HEAD)"
