#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
CURRENT_BRANCH="agent/phase49-3i18-operator-bulk-ai-rebuild"
RELEASE_BRANCH="release/phase50-a2j-hero-20260915"
EXPECTED_BASELINE="b1caeba0f20e711b29dfa9e0ff92a2f5186fb08d"
EXPECTED_DB="sfkilvrs_EmiAdmin_3dprinthub"
STATIC_ROOT="/home/sfkilvrs/public_html/static"
TARGET_SHA="${1:-}"
BACKUP_BASE="/home/sfkilvrs/3dprinthub-deploy-backups"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="$BACKUP_BASE/${STAMP}-phase50-a2j-hero"
DELTA_FILE="/tmp/3dprinthub-a2j-delta-$$.txt"
STATIC_LIST="/tmp/3dprinthub-a2j-static-$$.txt"
HERO_TEMPLATE_TMP="/tmp/3dprinthub-a2j-template-$$.html"
HERO_JS_TMP="/tmp/3dprinthub-a2j-js-$$.js"

cleanup() { rm -f "$DELTA_FILE" "$STATIC_LIST" "$HERO_TEMPLATE_TMP" "$HERO_JS_TMP" 2>/dev/null || true; }
trap cleanup EXIT
fail() { printf 'A2J_DEPLOY_FAIL=%s\nBACKUP_ROOT=%s\n' "$1" "$BACKUP_ROOT" >&2; exit 1; }
printf '%s\n' "============================================================"
printf '%s\n' "3DPrintHub Phase50.A.2J Standalone Hero Deploy"
printf '%s\n' "HERO-ONLY / NO MIGRATION / NO DATABASE WRITE / GITHUB-FIRST"
printf '%s\n' "============================================================"
[ -n "$TARGET_SHA" ] || fail "target_sha_required"
[ -d "$ROOT/.git" ] || fail "project_root_missing"
[ -x "$PY" ] || fail "production_python_missing"
cd "$ROOT"

ORIGIN="$(git remote get-url origin)"
BRANCH_NOW="$(git branch --show-current)"
HEAD_NOW="$(git rev-parse HEAD)"
STATUS="$(git status --porcelain --untracked-files=all)"
printf 'ROOT=%s\nORIGIN=%s\nCURRENT_BRANCH=%s\nCURRENT_HEAD=%s\nTARGET_SHA=%s\n' \
  "$ROOT" "$ORIGIN" "$BRANCH_NOW" "$HEAD_NOW" "$TARGET_SHA"
case "$ORIGIN" in *farazha2203/3dprinthub.git|*farazha2203/3dprinthub) ;; *) fail "wrong_repository" ;; esac
[ "$BRANCH_NOW" = "$CURRENT_BRANCH" ] || fail "unexpected_current_branch"
[ "$HEAD_NOW" = "$EXPECTED_BASELINE" ] || fail "production_head_changed"
[ -z "$STATUS" ] || fail "production_worktree_dirty"
printf '%s\n' "===== PREDEPLOY DATABASE / READINESS ====="
"$PY" - "$EXPECTED_DB" <<'PY'
import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django; django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from catalog_bridge.publish_readiness import publish_readiness
expected=sys.argv[1]
print("DB_VENDOR="+str(connection.vendor))
print("DB_NAME="+str(connection.settings_dict.get("NAME") or ""))
if connection.vendor != "mysql": raise SystemExit("A2J_DEPLOY_FAIL=database_vendor")
if str(connection.settings_dict.get("NAME") or "") != expected: raise SystemExit("A2J_DEPLOY_FAIL=database_name")
plan=MigrationExecutor(connection).migration_plan(MigrationExecutor(connection).loader.graph.leaf_nodes())
print("MIGRATION_PLAN="+repr([(m.app_label,m.name,b) for m,b in plan]))
if plan: raise SystemExit("A2J_DEPLOY_FAIL=migration_plan_not_empty")
r=publish_readiness()
print("PUBLISH_READY="+repr(r.get("ready")))
print("PUBLISH_BLOCKERS="+repr(r.get("blockers") or []))
if r.get("ready") is not True: raise SystemExit("A2J_DEPLOY_FAIL=receiver_not_ready")
PY
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
printf '%s\n' "===== LIVE RELEASE TARGET / EXPLICIT FETCH_HEAD ====="
REMOTE_LINE="$(git ls-remote origin "refs/heads/$RELEASE_BRANCH")"
[ -n "$REMOTE_LINE" ] || fail "release_branch_missing"
REMOTE_SHA="$(printf '%s\n' "$REMOTE_LINE" | awk '{print $1}')"
printf 'REMOTE_RELEASE_SHA=%s\n' "$REMOTE_SHA"
[ "$REMOTE_SHA" = "$TARGET_SHA" ] || fail "target_not_live_release_head"
git fetch --no-tags origin "refs/heads/$RELEASE_BRANCH"
FETCHED="$(git rev-parse FETCH_HEAD)"
printf 'FETCHED=%s\n' "$FETCHED"
[ "$FETCHED" = "$TARGET_SHA" ] || fail "fetched_target_mismatch"
git merge-base --is-ancestor "$EXPECTED_BASELINE" "$FETCHED" || fail "release_not_based_on_production"
git diff --name-only "$EXPECTED_BASELINE" "$FETCHED" > "$DELTA_FILE"
printf '%s\n' "===== RELEASE DELTA ====="
cat "$DELTA_FILE"
while IFS= read -r path; do
  [ -n "$path" ] || continue
  case "$path" in
    static/css/phase50-a2j-slicebox-hero.css|static/js/phase50-a2j-slicebox-hero.js) ;;
    templates/website/index.html|templates/website/partials/hero.html|website/views.py) ;;
    website/test_phase45_homepage_hero.py|website/test_phase46_home_experience.py) ;;
    website/test_phase49_2c_hero_studio.py|website/test_phase49_3b_hero_media.py) ;;
    website/test_phase49_persian_sales_hero.py|website/test_phase50_a2i_slicebox_hero.py) ;;
    website/test_phase50_mobile_hero_seo.py|scripts/host/phase50_a2j_standalone_hero_deploy.sh) ;;
    *) fail "unexpected_release_delta:$path" ;;
  esac
done < "$DELTA_FILE"
for required in \
  static/css/phase50-a2j-slicebox-hero.css \
  static/js/phase50-a2j-slicebox-hero.js \
  templates/website/partials/hero.html \
  website/views.py
do
  git diff --quiet "$EXPECTED_BASELINE" "$FETCHED" -- "$required" && fail "required_hero_delta_missing:$required"
done
if grep -Eq '(^|/)migrations/[0-9]{4}_[^/]+\.py$|^requirements[^/]*\.txt$|^config/settings' "$DELTA_FILE"; then
  fail "migration_dependency_or_settings_delta_detected"
fi
if git diff --name-only "$EXPECTED_BASELINE" "$FETCHED" | grep -Eq '(^|/)(payment|payments|gateway|zarinpal)'; then
  fail "payment_delta_detected"
fi
printf '%s\n' "HERO_ONLY_DELTA=PASS"

git show "$FETCHED:templates/website/partials/hero.html" > "$HERO_TEMPLATE_TMP"
git show "$FETCHED:static/js/phase50-a2j-slicebox-hero.js" > "$HERO_JS_TMP"
grep -Fq 'data-p50j-slicebox' "$HERO_TEMPLATE_TMP" || fail "a2j_template_marker_missing"
grep -Fq '50.4.0' "$HERO_TEMPLATE_TMP" || fail "a2j_version_missing"
grep -Fq 'p50j-slicebox' "$HERO_JS_TMP" || fail "a2j_js_marker_missing"
printf '%s\n' "===== VERIFIED ROLLBACK BACKUP ====="
mkdir -p "$BACKUP_ROOT/static-before"
chmod 700 "$BACKUP_ROOT"
git bundle create "$BACKUP_ROOT/source-before.bundle" HEAD
git bundle verify "$BACKUP_ROOT/source-before.bundle"
printf '%s\n' "$HEAD_NOW" > "$BACKUP_ROOT/source-head.txt"
printf '%s\n' "$BRANCH_NOW" > "$BACKUP_ROOT/source-branch.txt"
if [ -f .env ]; then
  cp -p .env "$BACKUP_ROOT/.env"
  chmod 600 "$BACKUP_ROOT/.env"
fi
cat > "$STATIC_LIST" <<'EOF'
css/phase50-a2i-slicebox-hero.css
js/phase50-a2i-slicebox-hero.js
css/phase50-a2j-slicebox-hero.css
js/phase50-a2j-slicebox-hero.js
EOF
while IFS= read -r rel; do
  [ -n "$rel" ] || continue
  if [ -f "$STATIC_ROOT/$rel" ]; then
    mkdir -p "$BACKUP_ROOT/static-before/$(dirname "$rel")"
    cp -p "$STATIC_ROOT/$rel" "$BACKUP_ROOT/static-before/$rel"
  else
    printf '%s\n' "$rel" >> "$BACKUP_ROOT/static-absent-before.txt"
  fi
done < "$STATIC_LIST"
sha256sum "$BACKUP_ROOT/source-before.bundle" > "$BACKUP_ROOT/source-bundle.sha256"
if [ -f "$BACKUP_ROOT/.env" ]; then
  sha256sum "$BACKUP_ROOT/.env" > "$BACKUP_ROOT/env.sha256"
fi
if find "$BACKUP_ROOT/static-before" -type f -print -quit | grep -q .; then
  (cd "$BACKUP_ROOT/static-before" && find . -type f -print0 | sort -z | xargs -0 sha256sum) > "$BACKUP_ROOT/static-before.sha256"
fi
(cd "$BACKUP_ROOT" && sha256sum -c source-bundle.sha256)
if [ -f "$BACKUP_ROOT/env.sha256" ]; then
  (cd "$BACKUP_ROOT" && sha256sum -c env.sha256)
fi
if [ -f "$BACKUP_ROOT/static-before.sha256" ]; then
  (cd "$BACKUP_ROOT/static-before" && sha256sum -c "$BACKUP_ROOT/static-before.sha256")
fi
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"
printf '%s\n' "PREDEPLOY_BACKUP_VERIFIED=YES"

printf '%s\n' "===== SWITCH TO GITHUB RELEASE ====="
if git show-ref --verify --quiet "refs/heads/$RELEASE_BRANCH"; then
  fail "local_release_branch_already_exists"
fi
git switch -c "$RELEASE_BRANCH" "$FETCHED"
[ "$(git rev-parse HEAD)" = "$TARGET_SHA" ] || fail "deployed_head_mismatch"
[ "$(git branch --show-current)" = "$RELEASE_BRANCH" ] || fail "release_branch_switch_failed"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "worktree_dirty_after_switch"
printf 'DEPLOYED_BRANCH=%s\nDEPLOYED_HEAD=%s\n' "$(git branch --show-current)" "$(git rev-parse HEAD)"
printf '%s\n' "===== POST-SWITCH SAFETY ====="
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
"$PY" - <<'PY'
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django; django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from catalog_bridge.publish_readiness import publish_readiness
ex=MigrationExecutor(connection)
plan=ex.migration_plan(ex.loader.graph.leaf_nodes())
print("POST_MIGRATION_PLAN="+repr([(m.app_label,m.name,b) for m,b in plan]))
if plan: raise SystemExit("A2J_DEPLOY_FAIL=post_migration_plan_not_empty")
r=publish_readiness()
print("POST_PUBLISH_READY="+repr(r.get("ready")))
print("POST_PUBLISH_BLOCKERS="+repr(r.get("blockers") or []))
if r.get("ready") is not True: raise SystemExit("A2J_DEPLOY_FAIL=post_receiver_not_ready")
PY

grep -Fq 'data-p50j-slicebox' templates/website/partials/hero.html || fail "live_template_marker_missing"
grep -Fq '50.4.0' templates/website/partials/hero.html || fail "live_version_marker_missing"
grep -Fq 'p50j-slicebox' static/js/phase50-a2j-slicebox-hero.js || fail "live_js_marker_missing"
printf '%s\n' "===== COLLECTSTATIC ====="
"$PY" manage.py collectstatic --noinput
for rel in css/phase50-a2j-slicebox-hero.css js/phase50-a2j-slicebox-hero.js; do
  [ -f "static/$rel" ] || fail "source_static_missing:$rel"
  [ -f "$STATIC_ROOT/$rel" ] || fail "collected_static_missing:$rel"
  SOURCE_SHA="$(sha256sum "static/$rel" | awk '{print $1}')"
  COLLECTED_SHA="$(sha256sum "$STATIC_ROOT/$rel" | awk '{print $1}')"
  printf 'STATIC_SHA %s source=%s collected=%s\n' "$rel" "$SOURCE_SHA" "$COLLECTED_SHA"
  [ "$SOURCE_SHA" = "$COLLECTED_SHA" ] || fail "collected_static_hash_mismatch:$rel"
done

printf '%s\n' "===== PASSENGER RESTART ====="
mkdir -p tmp
touch tmp/restart.txt
sleep 4

printf '%s\n' "===== PUBLIC HERO VERIFY ====="
"$PY" - <<'PY'
from urllib import request
base="https://3dprinthub.ir"
def fetch(path):
    req=request.Request(base+path,headers={"User-Agent":"3DPrintHub-A2J-Verify/1.0","Cache-Control":"no-cache"})
    with request.urlopen(req,timeout=20) as r:
        return int(r.status), r.read(2_000_000)
checks={
    "home": fetch("/"),
    "store": fetch("/store/"),
    "css": fetch("/static/css/phase50-a2j-slicebox-hero.css?v=50.4.0"),
    "js": fetch("/static/js/phase50-a2j-slicebox-hero.js?v=50.4.0"),
}
for key,(status,_) in checks.items(): print(key.upper()+"_HTTP="+str(status))
if any(status != 200 for status,_ in checks.values()): raise SystemExit("A2J_DEPLOY_FAIL=public_http")
home=checks["home"][1]
for marker in (
    b"data-p50j-slicebox",
    b"phase50-a2j-slicebox-hero.css",
    b"phase50-a2j-slicebox-hero.js",
    b"v=50.4.0",
):
    if marker not in home: raise SystemExit("A2J_DEPLOY_FAIL=home_marker_missing:"+marker.decode())
for old in (b"phase50-a2i-slicebox-hero.js", b"phase49_2c-home-hero.js"):
    if old in home: raise SystemExit("A2J_DEPLOY_FAIL=old_engine_still_loaded:"+old.decode())
if b"Phase50.A.2J" not in checks["css"][1]: raise SystemExit("A2J_DEPLOY_FAIL=css_marker")
if b"p50j-slicebox" not in checks["js"][1]: raise SystemExit("A2J_DEPLOY_FAIL=js_marker")
print("A2J_PUBLIC_VERIFY=PASS")
PY

printf '%s\n' "===== FINAL STATE ====="
printf 'FINAL_BRANCH=%s\n' "$(git branch --show-current)"
printf 'FINAL_HEAD=%s\n' "$(git rev-parse HEAD)"
printf 'FINAL_WORKTREE=%s\n' "$(test -z "$(git status --porcelain --untracked-files=all)" && printf CLEAN || printf DIRTY)"
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"
printf '%s\n' "PHASE50_A2J_STANDALONE_HERO_DEPLOY=PASS"
