#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
EXPECTED_DB="sfkilvrs_EmiAdmin_3dprinthub"
EXPECTED_HOST_BRANCH="release/phase50-a2j-hero-20260915"
TARGET_BRANCH="release/phase50-a2l-owner-qa-20260918"
EXPECTED_BASELINE="12e319ace1eb55c114d7117e1b5a2fa170b410ab"
STATIC_ROOT="/home/sfkilvrs/public_html/static"
TARGET_SHA="${1:-}"
BACKUP_BASE="/home/sfkilvrs/3dprinthub-deploy-backups"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="$BACKUP_BASE/${STAMP}-phase50-a2l-site-priority"
TMP_DELTA="/tmp/3dprinthub-a2l-site-delta-$$.txt"
STATIC_LIST="/tmp/3dprinthub-a2l-site-static-$$.txt"

cleanup() { rm -f "$TMP_DELTA" "$STATIC_LIST" 2>/dev/null || true; }
trap cleanup EXIT
fail() {
  printf 'PHASE50_A2L_SITE_DEPLOY_FAIL=%s\n' "$1" >&2
  printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT" >&2
  exit 1
}

[ -n "$TARGET_SHA" ] || fail "target_sha_required"
[ -d "$ROOT/.git" ] || fail "project_root_or_git_missing"
[ -x "$PY" ] || fail "production_python_missing"
cd "$ROOT"
ORIGIN="$(git remote get-url origin)"
CURRENT_BRANCH="$(git branch --show-current)"
CURRENT_HEAD="$(git rev-parse HEAD)"
STATUS="$(git status --porcelain --untracked-files=all)"
printf 'ROOT=%s\nORIGIN=%s\nCURRENT_BRANCH=%s\nCURRENT_HEAD=%s\nTARGET_SHA=%s\n'   "$ROOT" "$ORIGIN" "$CURRENT_BRANCH" "$CURRENT_HEAD" "$TARGET_SHA"
case "$ORIGIN" in *farazha2203/3dprinthub.git|*farazha2203/3dprinthub) ;; *) fail "wrong_repository" ;; esac
[ "$CURRENT_BRANCH" = "$EXPECTED_HOST_BRANCH" ] || fail "wrong_host_branch"
[ "$CURRENT_HEAD" = "$EXPECTED_BASELINE" ] || fail "host_baseline_changed"
[ -z "$STATUS" ] || { printf '%s\n' "$STATUS"; fail "production_worktree_dirty"; }

"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
"$PY" - "$EXPECTED_DB" <<'PY'
import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django; django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from catalog_bridge.publish_readiness import publish_readiness
expected = sys.argv[1]
print("DB_VENDOR=" + str(connection.vendor))
print("DB_NAME=" + str(connection.settings_dict.get("NAME") or ""))
if connection.vendor != "mysql":
    raise SystemExit("PHASE50_A2L_SITE_DEPLOY_FAIL=database_vendor_not_mysql")
if str(connection.settings_dict.get("NAME") or "") != expected:
    raise SystemExit("PHASE50_A2L_SITE_DEPLOY_FAIL=database_name_mismatch")
plan = MigrationExecutor(connection).migration_plan(MigrationExecutor(connection).loader.graph.leaf_nodes())
print("CURRENT_MIGRATION_PLAN=" + repr([(m.app_label, m.name, b) for m, b in plan]))
if plan:
    raise SystemExit("PHASE50_A2L_SITE_DEPLOY_FAIL=current_migration_plan_not_empty")
ready = publish_readiness()
print("PUBLISH_READY=" + repr(ready.get("ready")))
print("PUBLISH_BLOCKERS=" + repr(ready.get("blockers") or []))
if ready.get("ready") is not True:
    raise SystemExit("PHASE50_A2L_SITE_DEPLOY_FAIL=receiver_not_ready_before_deploy")
PY
REMOTE_LINE="$(git ls-remote origin "refs/heads/$TARGET_BRANCH")"
[ -n "$REMOTE_LINE" ] || fail "remote_target_branch_missing"
REMOTE_SHA="$(printf '%s\n' "$REMOTE_LINE" | awk '{print $1}')"
printf 'REMOTE_SHA=%s\n' "$REMOTE_SHA"
[ "$REMOTE_SHA" = "$TARGET_SHA" ] || fail "target_not_live_github_head"

git fetch --no-tags origin "refs/heads/$TARGET_BRANCH"
FETCHED="$(git rev-parse FETCH_HEAD)"
printf 'FETCHED=%s\n' "$FETCHED"
[ "$FETCHED" = "$TARGET_SHA" ] || fail "fetched_target_mismatch"
git merge-base --is-ancestor "$EXPECTED_BASELINE" "$FETCHED" || fail "target_not_fast_forward"
git diff --name-only "$EXPECTED_BASELINE" "$FETCHED" > "$TMP_DELTA"
printf '%s\n' "===== TARGET DELTA ====="
cat "$TMP_DELTA"

if grep -Eq '(^|/)migrations/[0-9]{4}_[^/]+\.py$|^requirements[^/]*\.txt$|^config/settings' "$TMP_DELTA"; then
  fail "migration_dependency_or_settings_delta_detected"
fi
for required_path in   static/css/phase50-a2k-tympanus-slicebox.css   static/js/phase50-a2k-tympanus-slicebox.js   static/vendor/slicebox/js/jquery.slicebox.js   templates/website/partials/hero.html   store/phase50_product_admin_workspace.py
do
  git cat-file -e "$FETCHED:$required_path" 2>/dev/null || fail "required_target_file_missing:$required_path"
done
mkdir -p "$BACKUP_ROOT/static-before"
chmod 700 "$BACKUP_ROOT"
git bundle create "$BACKUP_ROOT/source-before.bundle" HEAD
git bundle verify "$BACKUP_ROOT/source-before.bundle"
printf '%s\n' "$CURRENT_HEAD" > "$BACKUP_ROOT/source-head.txt"
printf '%s\n' "$CURRENT_BRANCH" > "$BACKUP_ROOT/source-branch.txt"
if [ -f .env ]; then
  cp -p .env "$BACKUP_ROOT/.env"
  chmod 600 "$BACKUP_ROOT/.env"
fi
cat > "$STATIC_LIST" <<'EOF'
css/phase50-a2j-slicebox-hero.css
js/phase50-a2j-slicebox-hero.js
css/phase50-a2k-tympanus-slicebox.css
js/phase50-a2k-tympanus-slicebox.js
vendor/slicebox/css/slicebox.css
vendor/slicebox/js/jquery.slicebox.js
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
if [ -f "$BACKUP_ROOT/.env" ]; then sha256sum "$BACKUP_ROOT/.env" > "$BACKUP_ROOT/env.sha256"; fi
(cd "$BACKUP_ROOT" && sha256sum -c source-bundle.sha256 && if [ -f env.sha256 ]; then sha256sum -c env.sha256; fi)
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"
printf '%s\n' "PREDEPLOY_BACKUP_VERIFIED=YES"
git merge --ff-only "$FETCHED"
[ "$(git rev-parse HEAD)" = "$TARGET_SHA" ] || fail "deployed_head_mismatch"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "worktree_dirty_after_merge"

"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
"$PY" - <<'PY'
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django; django.setup()
from django.contrib import admin
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from catalog_bridge.publish_readiness import publish_readiness
from store.models import Product, ProductVariant
plan = MigrationExecutor(connection).migration_plan(MigrationExecutor(connection).loader.graph.leaf_nodes())
print("POST_MERGE_MIGRATION_PLAN=" + repr([(m.app_label, m.name, b) for m, b in plan]))
if plan:
    raise SystemExit("PHASE50_A2L_SITE_DEPLOY_FAIL=post_merge_migration_plan_not_empty")
ready = publish_readiness()
print("POST_MERGE_PUBLISH_READY=" + repr(ready.get("ready")))
if ready.get("ready") is not True:
    raise SystemExit("PHASE50_A2L_SITE_DEPLOY_FAIL=receiver_not_ready_after_merge")
product_admin = admin.site._registry.get(Product)
models = [getattr(inline, "model", None) for inline in getattr(product_admin, "inlines", ())]
print("PRODUCT_ADMIN_VARIANT_INLINE_PRESENT=" + repr(ProductVariant in models))
if ProductVariant in models:
    raise SystemExit("PHASE50_A2L_SITE_DEPLOY_FAIL=product_variant_inline_still_present")
PY
grep -Fq 'disperseFactor: 30' static/js/phase50-a2k-tympanus-slicebox.js || fail "example4_disperse_marker_missing"
grep -Fq 'orientation: "r"' static/js/phase50-a2k-tympanus-slicebox.js || fail "example4_orientation_marker_missing"
grep -Fq 'loading="eager"' templates/website/partials/hero.html || fail "hero_eager_load_fix_missing"

"$PY" manage.py collectstatic --noinput
for rel in   css/phase50-a2k-tympanus-slicebox.css   js/phase50-a2k-tympanus-slicebox.js   vendor/slicebox/css/slicebox.css   vendor/slicebox/js/jquery.slicebox.js
do
  [ -f "static/$rel" ] || fail "source_static_missing:$rel"
  [ -f "$STATIC_ROOT/$rel" ] || fail "collected_static_missing:$rel"
  A="$(sha256sum "static/$rel" | awk '{print $1}')"
  B="$(sha256sum "$STATIC_ROOT/$rel" | awk '{print $1}')"
  printf 'STATIC_SHA %s source=%s collected=%s\n' "$rel" "$A" "$B"
  [ "$A" = "$B" ] || fail "collected_static_hash_mismatch:$rel"
done

mkdir -p tmp
touch tmp/restart.txt
sleep 4
"$PY" - "$TARGET_SHA" <<'PY'
import json, os, sys
from urllib import request
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django; django.setup()
from django.conf import settings
target = sys.argv[1]
base = "https://3dprinthub.ir"
token = str(getattr(settings, "CATALOG_BRIDGE_TOKEN", "") or "").strip()
if len(token) < 24:
    raise SystemExit("PHASE50_A2L_SITE_DEPLOY_FAIL=bridge_token_missing")
def fetch(path, auth=False, limit=2_000_000):
    headers = {"User-Agent": "3DPrintHub-A2L-Site-Verify/1.0", "Cache-Control": "no-cache"}
    if auth:
        headers["Authorization"] = "Bearer " + token
    with request.urlopen(request.Request(base + path, headers=headers), timeout=20) as response:
        return int(response.status), response.read(limit)
checks = {
    "home": fetch("/"),
    "store": fetch("/store/"),
    "health": fetch("/api/catalog-bridge/v1/health/", True),
    "ready": fetch("/api/catalog-bridge/v1/publish-readiness/", True),
    "hero_css": fetch("/static/css/phase50-a2k-tympanus-slicebox.css?v=" + target),
    "hero_js": fetch("/static/js/phase50-a2k-tympanus-slicebox.js?v=" + target),
}
for key, (status, _) in checks.items():
    print(key.upper() + "_HTTP=" + str(status))
if any(status != 200 for status, _ in checks.values()):
    raise SystemExit("PHASE50_A2L_SITE_DEPLOY_FAIL=http_not_200")
health = json.loads(checks["health"][1].decode("utf-8"))
ready = json.loads(checks["ready"][1].decode("utf-8"))
if health.get("status") != "ok":
    raise SystemExit("PHASE50_A2L_SITE_DEPLOY_FAIL=bridge_health_not_ok")
if ready.get("ready") is not True:
    raise SystemExit("PHASE50_A2L_SITE_DEPLOY_FAIL=publish_readiness_not_ready")
home = checks["home"][1]
for marker in (b"data-p50k-slicebox", b"phase50-a2k-tympanus-slicebox.css", b"jquery.slicebox.js"):
    if marker not in home:
        raise SystemExit("PHASE50_A2L_SITE_DEPLOY_FAIL=home_hero_marker_missing")
js = checks["hero_js"][1]
for marker in (b'disperseFactor: 30', b'orientation: "r"'):
    if marker not in js:
        raise SystemExit("PHASE50_A2L_SITE_DEPLOY_FAIL=example4_runtime_marker_missing")
print("A2L_SITE_PUBLIC_VERIFY=PASS")
PY

printf 'FINAL_HEAD=%s\n' "$(git rev-parse HEAD)"
printf 'FINAL_WORKTREE=%s\n' "$(test -z "$(git status --porcelain --untracked-files=all)" && printf CLEAN || printf DIRTY)"
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"
printf '%s\n' "PHASE50_A2L_SITE_DEPLOY=PASS"
