#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
EXPECTED_DB="sfkilvrs_EmiAdmin_3dprinthub"
HOST_BRANCH="release/phase50-a2j-hero-20260915"
TARGET_BRANCH="release/phase50-a2l-owner-qa-20260918"
EXPECTED_BASELINE="36a69e76f9cd553273862ee400f9391573f3dd01"
TARGET_SHA="${1:-}"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="/home/sfkilvrs/3dprinthub-deploy-backups/${STAMP}-phase50-a2q-hero-shadow-cache"
TMP_DELTA="/tmp/3dprinthub-a2q-hero-$$.txt"

cleanup(){ rm -f "$TMP_DELTA" 2>/dev/null || true; }
trap cleanup EXIT
fail(){ printf 'A2Q_HERO_DEPLOY_FAIL=%s\n' "$1" >&2; printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT" >&2; exit 1; }

[ -n "$TARGET_SHA" ] || fail "target_sha_required"
cd "$ROOT"
[ -d .git ] || fail "project_git_missing"
[ "$(git branch --show-current)" = "$HOST_BRANCH" ] || fail "wrong_host_branch"
[ "$(git rev-parse HEAD)" = "$EXPECTED_BASELINE" ] || fail "host_baseline_changed"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "production_worktree_dirty"
case "$(git remote get-url origin)" in *farazha2203/3dprinthub.git|*farazha2203/3dprinthub) ;; *) fail "wrong_repository" ;; esac

"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
"$PY" - "$EXPECTED_DB" <<'PY'
import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
import django; django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
expected=sys.argv[1]
if connection.vendor!="mysql" or str(connection.settings_dict.get("NAME") or "")!=expected:
    raise SystemExit("A2Q_HERO_DEPLOY_FAIL=database_identity_mismatch")
plan=MigrationExecutor(connection).migration_plan(MigrationExecutor(connection).loader.graph.leaf_nodes())
print("MIGRATION_PLAN="+repr([(m.app_label,m.name,b) for m,b in plan]))
if plan:
    raise SystemExit("A2Q_HERO_DEPLOY_FAIL=migration_plan_not_empty")
PY

REMOTE_SHA="$(git ls-remote origin "refs/heads/$TARGET_BRANCH" | awk '{print $1}')"
[ "$REMOTE_SHA" = "$TARGET_SHA" ] || fail "target_not_live_github_head"
git fetch --no-tags origin "refs/heads/$TARGET_BRANCH"
FETCHED="$(git rev-parse FETCH_HEAD)"
[ "$FETCHED" = "$TARGET_SHA" ] || fail "fetched_target_mismatch"
git merge-base --is-ancestor "$EXPECTED_BASELINE" "$FETCHED" || fail "target_not_fast_forward"
git diff --name-only "$EXPECTED_BASELINE" "$FETCHED" > "$TMP_DELTA"
cat "$TMP_DELTA"
if grep -Eq '(^|/)migrations/[0-9]{4}_[^/]+\.py$|^requirements[^/]*\.txt$|^config/settings' "$TMP_DELTA"; then
  fail "migration_dependency_or_settings_delta_detected"
fi
for required in \
  static/css/phase50-a2k-tympanus-slicebox.css \
  static/js/phase50-a2k-tympanus-slicebox.js \
  templates/website/partials/hero.html \
  website/test_phase50_a2k_tympanus_slicebox.py \
  scripts/host/phase50_a2q_hero_shadow_cache_deploy.sh
do
  grep -Fxq "$required" "$TMP_DELTA" || fail "required_delta_missing:$required"
done

mkdir -p "$BACKUP_ROOT/static-before"
chmod 700 "$BACKUP_ROOT" "$BACKUP_ROOT/static-before"
git bundle create "$BACKUP_ROOT/source-before.bundle" HEAD
git bundle verify "$BACKUP_ROOT/source-before.bundle"
printf '%s\n' "$EXPECTED_BASELINE" > "$BACKUP_ROOT/source-head.txt"
printf '%s\n' "$HOST_BRANCH" > "$BACKUP_ROOT/source-branch.txt"
if [ -f .env ]; then cp -p .env "$BACKUP_ROOT/.env"; chmod 600 "$BACKUP_ROOT/.env"; fi
for public_file in \
  /home/sfkilvrs/public_html/static/css/phase50-a2k-tympanus-slicebox.css \
  /home/sfkilvrs/public_html/static/js/phase50-a2k-tympanus-slicebox.js
do
  if [ -f "$public_file" ]; then cp -p "$public_file" "$BACKUP_ROOT/static-before/"; fi
done
sha256sum "$BACKUP_ROOT/source-before.bundle" > "$BACKUP_ROOT/source-before.sha256"
(cd "$BACKUP_ROOT" && sha256sum -c source-before.sha256)
printf 'PREDEPLOY_BACKUP_VERIFIED=YES\n'
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"

git merge --ff-only "$FETCHED"
[ "$(git rev-parse HEAD)" = "$TARGET_SHA" ] || fail "deployed_head_mismatch"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "worktree_dirty_after_merge"
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run

old_umask="$(umask)"
umask 022
"$PY" manage.py collectstatic --noinput
umask "$old_umask"
chmod 755 /home/sfkilvrs/public_html/static /home/sfkilvrs/public_html/static/css /home/sfkilvrs/public_html/static/js
chmod 644 /home/sfkilvrs/public_html/static/css/phase50-a2k-tympanus-slicebox.css
chmod 644 /home/sfkilvrs/public_html/static/js/phase50-a2k-tympanus-slicebox.js
mkdir -p tmp
touch tmp/restart.txt
sleep 4

HOME_HTML="$(curl -fsSL --max-time 25 -H 'Cache-Control: no-cache' 'https://3dprinthub.ir/?a2q=1')"
CSS="$(curl -fsSL --max-time 25 'https://3dprinthub.ir/static/css/phase50-a2k-tympanus-slicebox.css?v=50.10.0')"
JS="$(curl -fsSL --max-time 25 'https://3dprinthub.ir/static/js/phase50-a2k-tympanus-slicebox.js?v=50.10.0')"
printf '%s' "$HOME_HTML" | grep -Fq '50.10.0' || fail "home_cache_marker_missing"
if printf '%s' "$HOME_HTML" | grep -Fq 'id="shadow"'; then fail "legacy_shadow_dom_present"; fi
printf '%s' "$CSS" | grep -Fq '.p50k-slicebox #shadow' || fail "shadow_hard_kill_css_missing"
printf '%s' "$CSS" | grep -Fq 'display: none !important' || fail "shadow_display_kill_missing"
printf '%s' "$JS" | grep -Fq 'legacyShadow.remove()' || fail "shadow_runtime_removal_missing"
printf 'PUBLIC_HERO_50_10=PASS\n'
printf 'FINAL_HEAD=%s\n' "$(git rev-parse HEAD)"
printf 'FINAL_WORKTREE=%s\n' "$(test -z "$(git status --porcelain --untracked-files=all)" && printf CLEAN || printf DIRTY)"
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"
printf 'PHASE50_A2Q_HERO_SHADOW_CACHE_DEPLOY=PASS\n'
