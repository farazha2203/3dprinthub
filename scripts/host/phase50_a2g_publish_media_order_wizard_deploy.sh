#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
BRANCH="agent/phase49-3i18-operator-bulk-ai-rebuild"
EXPECTED_DB="sfkilvrs_EmiAdmin_3dprinthub"
EXPECTED_BASELINE="7d0b3df03c3657106ebaf86d5f9123ba262495a5"
STATIC_ROOT="/home/sfkilvrs/public_html/static"
TARGET_SHA="${1:-}"

BACKUP_BASE="/home/sfkilvrs/3dprinthub-deploy-backups"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="$BACKUP_BASE/${STAMP}-phase50-a2g-publish-ready"
TMP_DELTA="/tmp/3dprinthub-a2g-delta-$$.txt"

cleanup() {
    rm -f "$TMP_DELTA" 2>/dev/null || true
}
trap cleanup EXIT

fail() {
    printf 'PHASE50_A2G_DEPLOY_FAIL=%s\n' "$1" >&2
    printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT" >&2
    exit 1
}
printf '%s\n' "============================================================"
printf '%s\n' "3DPrintHub Phase50.A.2G Publish Media + Order Wizard Production Deploy"
printf '%s\n' "verified ready DB -> source backup -> ff-only -> static -> restart -> verify"
printf '%s\n' "NO DATABASE MIGRATION / NO DATABASE WRITE"
printf '%s\n' "============================================================"

[ -n "$TARGET_SHA" ] || fail "target_sha_required"
[ -d "$ROOT/.git" ] || fail "project_root_or_git_missing"
[ -x "$PY" ] || fail "production_python_missing"

cd "$ROOT"
ORIGIN="$(git remote get-url origin)"
CURRENT_BRANCH="$(git branch --show-current)"
CURRENT_HEAD="$(git rev-parse HEAD)"
STATUS="$(git status --porcelain --untracked-files=all)"

printf 'ROOT=%s\n' "$ROOT"
printf 'ORIGIN=%s\n' "$ORIGIN"
printf 'CURRENT_BRANCH=%s\n' "$CURRENT_BRANCH"
printf 'CURRENT_HEAD=%s\n' "$CURRENT_HEAD"
printf 'EXPECTED_BASELINE=%s\n' "$EXPECTED_BASELINE"
printf 'TARGET_SHA=%s\n' "$TARGET_SHA"

case "$ORIGIN" in
  *farazha2203/3dprinthub.git|*farazha2203/3dprinthub) ;;
  *) fail "wrong_repository" ;;
esac
[ "$CURRENT_BRANCH" = "$BRANCH" ] || fail "wrong_branch"
[ "$CURRENT_HEAD" = "$EXPECTED_BASELINE" ] || fail "host_baseline_changed"
[ -z "$STATUS" ] || {
    printf '%s\n' "$STATUS"
    fail "production_worktree_dirty"
}

printf '%s\n' "===== VERIFY CURRENT PRODUCTION DB / READINESS ====="
"$PY" - "$EXPECTED_DB" <<'PY'
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.recorder import MigrationRecorder
from catalog_bridge.publish_readiness import publish_readiness

expected_db = sys.argv[1]
print("DB_VENDOR=" + str(connection.vendor))
print("DB_NAME=" + str(connection.settings_dict.get("NAME") or ""))
if connection.vendor != "mysql":
    raise SystemExit("PHASE50_A2G_DEPLOY_FAIL=database_vendor_not_mysql")
if str(connection.settings_dict.get("NAME") or "") != expected_db:
    raise SystemExit("PHASE50_A2G_DEPLOY_FAIL=database_name_mismatch")
applied = set(
    MigrationRecorder.Migration.objects.filter(app__in={"store", "website"})
    .values_list("app", "name")
)
required = {
    ("store", "0036_phase50_checkout_snapshot"),
    ("store", "0037_phase50_professional_commerce_policy"),
    ("store", "0038_phase50_profile_matrix"),
    ("store", "0039_phase50_filament_offer_pricing"),
    ("store", "0040_phase50_filament_offer_operations"),
    ("store", "0041_phase50_filament_visual_identity"),
    ("store", "0042_phase49_3i51_filament_registry_descriptions"),
    ("website", "0024_phase49_3i51_material_catalog_description"),
}
missing = sorted(required - applied)
print("REQUIRED_MIGRATIONS_MISSING=" + repr(missing))
if missing:
    raise SystemExit("PHASE50_A2G_DEPLOY_FAIL=required_migrations_missing")

executor = MigrationExecutor(connection)
plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
print("CURRENT_MIGRATION_PLAN=" + repr([(m.app_label, m.name, b) for m, b in plan]))
if plan:
    raise SystemExit("PHASE50_A2G_DEPLOY_FAIL=current_migration_plan_not_empty")

ready = publish_readiness()
print("PUBLISH_READY=" + repr(ready.get("ready")))
print("PUBLISH_BLOCKERS=" + repr(ready.get("blockers") or []))
if ready.get("ready") is not True:
    raise SystemExit("PHASE50_A2G_DEPLOY_FAIL=receiver_not_ready_before_deploy")
PY
printf '%s\n' "===== PREDEPLOY DJANGO CHECK ====="
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run

printf '%s\n' "===== VERIFY LIVE TARGET / FETCH EXACT BRANCH ====="
REMOTE_LINE="$(git ls-remote origin "refs/heads/$BRANCH")"
[ -n "$REMOTE_LINE" ] || fail "remote_branch_missing"
REMOTE_SHA="$(printf '%s\n' "$REMOTE_LINE" | awk '{print $1}')"
printf 'REMOTE_SHA=%s\n' "$REMOTE_SHA"
[ "$REMOTE_SHA" = "$TARGET_SHA" ] || fail "target_not_live_github_head"

git fetch --no-tags origin "refs/heads/$BRANCH"
FETCHED="$(git rev-parse FETCH_HEAD)"
printf 'FETCHED=%s\n' "$FETCHED"
[ "$FETCHED" = "$TARGET_SHA" ] || fail "fetched_target_mismatch"
git merge-base --is-ancestor "$EXPECTED_BASELINE" "$FETCHED" || fail "target_not_fast_forward"

git diff --name-only "$EXPECTED_BASELINE" "$FETCHED" > "$TMP_DELTA"
printf '%s\n' "===== TARGET DELTA ====="
cat "$TMP_DELTA"

while IFS= read -r path; do
    [ -n "$path" ] || continue
    case "$path" in
      PROJECT_CONTEXT.md|docs/*|scripts/ci/*|scripts/host/phase50_a2g_publish_media_order_wizard_deploy.sh) ;;
      catalog_center/app/phase49_3i49_site_publish.py|catalog_center/tests/test_phase49_3i49_site_bulk_publish.py) ;;
      static/store/css/phase50-profile-selector.css|static/store/js/phase50-profile-selector.js) ;;
      store/management/commands/phase37_import_catalog_center.py|store/test_phase49_unified_import_e2e.py) ;;
      *) fail "unexpected_target_delta:$path" ;;
    esac
done < "$TMP_DELTA"
for required_path in \
  static/store/css/phase50-profile-selector.css \
  static/store/js/phase50-profile-selector.js \
  store/management/commands/phase37_import_catalog_center.py
do
    if git diff --quiet "$EXPECTED_BASELINE" "$FETCHED" -- "$required_path"; then
        fail "required_runtime_delta_missing:$required_path"
    fi
done

if grep -Eq '(^|/)migrations/[0-9]{4}_[^/]+\.py$|^requirements[^/]*\.txt$|^config/settings' "$TMP_DELTA"; then
    fail "migration_dependency_or_settings_delta_detected"
fi
printf '%s\n' "NO_MIGRATION_OR_DEPENDENCY_DELTA=PASS"

printf '%s\n' "===== CREATE VERIFIED SOURCE / ENV / STATIC BACKUP ====="
mkdir -p "$BACKUP_ROOT"
chmod 700 "$BACKUP_ROOT"
git bundle create "$BACKUP_ROOT/source-before.bundle" HEAD
git bundle verify "$BACKUP_ROOT/source-before.bundle"
printf '%s\n' "$CURRENT_HEAD" > "$BACKUP_ROOT/source-head.txt"
printf '%s\n' "$CURRENT_BRANCH" > "$BACKUP_ROOT/source-branch.txt"

if [ -f ".env" ]; then
    cp -p ".env" "$BACKUP_ROOT/.env"
    chmod 600 "$BACKUP_ROOT/.env"
    sha256sum "$BACKUP_ROOT/.env" > "$BACKUP_ROOT/env.sha256"
fi
if [ -d "$STATIC_ROOT/store" ]; then
    tar -czf "$BACKUP_ROOT/static-store-before.tgz" -C "$STATIC_ROOT" store
    gzip -t "$BACKUP_ROOT/static-store-before.tgz"
    sha256sum "$BACKUP_ROOT/static-store-before.tgz" > "$BACKUP_ROOT/static-store.sha256"
fi
sha256sum "$BACKUP_ROOT/source-before.bundle" > "$BACKUP_ROOT/source-bundle.sha256"

(
    cd "$BACKUP_ROOT"
    sha256sum -c source-bundle.sha256
    if [ -f env.sha256 ]; then sha256sum -c env.sha256; fi
    if [ -f static-store.sha256 ]; then sha256sum -c static-store.sha256; fi
)
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"
printf '%s\n' "PREDEPLOY_BACKUP_VERIFIED=YES"

printf '%s\n' "===== FF-ONLY DEPLOY FROM FETCH_HEAD ====="
git merge --ff-only "$FETCHED"
DEPLOYED_HEAD="$(git rev-parse HEAD)"
printf 'DEPLOYED_HEAD=%s\n' "$DEPLOYED_HEAD"
[ "$DEPLOYED_HEAD" = "$TARGET_SHA" ] || fail "deployed_head_mismatch"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "worktree_dirty_after_merge"

printf '%s\n' "===== POST-MERGE DJANGO / MIGRATION SAFETY ====="
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
"$PY" - <<'PY'
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
executor = MigrationExecutor(connection)
plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
print("POST_MERGE_MIGRATION_PLAN=" + repr([(m.app_label, m.name, b) for m, b in plan]))
if plan:
    raise SystemExit("PHASE50_A2G_DEPLOY_FAIL=post_merge_migration_plan_not_empty")
PY
printf '%s\n' "===== VERIFY RECEIVER STILL READY ====="
"$PY" - <<'PY'
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from catalog_bridge.publish_readiness import publish_readiness
ready = publish_readiness()
print("POST_MERGE_PUBLISH_READY=" + repr(ready.get("ready")))
print("POST_MERGE_PUBLISH_BLOCKERS=" + repr(ready.get("blockers") or []))
if ready.get("ready") is not True:
    raise SystemExit("PHASE50_A2G_DEPLOY_FAIL=receiver_not_ready_after_merge")
PY

printf '%s\n' "===== VERIFY A2G SOURCE CONTRACT ====="
grep -Fq '_stored_file_matches_local' store/management/commands/phase37_import_catalog_center.py || fail "importer_media_idempotence_contract_missing"
grep -Fq 'store-profile-progress' static/store/js/phase50-profile-selector.js || fail "wizard_progress_js_contract_missing"
grep -Fq 'Phase50.A.2G publish-ready ordering wizard' static/store/css/phase50-profile-selector.css || fail "wizard_a2g_css_contract_missing"

printf '%s\n' "===== COLLECTSTATIC ====="
"$PY" manage.py collectstatic --noinput

printf '%s\n' "===== VERIFY COLLECTED STOREFRONT ASSETS ====="
for rel in \
  store/css/phase50-profile-selector.css \
  store/js/phase50-profile-selector.js \
  store/js/store.js
do
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
printf '%s\n' "===== HTTP / BRIDGE / STATIC VERIFY ====="
"$PY" - "$TARGET_SHA" <<'PY'
import json
import os
import sys
from urllib import request

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from django.conf import settings

target = sys.argv[1]
base = "https://3dprinthub.ir"
token = str(getattr(settings, "CATALOG_BRIDGE_TOKEN", "") or "").strip()
if len(token) < 24:
    raise SystemExit("PHASE50_A2G_DEPLOY_FAIL=bridge_token_missing_after_restart")

def fetch(path, *, auth=False, limit=2_000_000):
    headers = {"User-Agent": "3DPrintHub-Phase50.A.2G-Verify/1.0", "Accept": "*/*", "Cache-Control": "no-cache"}
    if auth:
        headers["Authorization"] = "Bearer " + token
    req = request.Request(base + path, headers=headers)
    with request.urlopen(req, timeout=20) as response:
        return int(response.status), response.read(limit)

home_status, _ = fetch("/")
store_status, _ = fetch("/store/")
health_status, health_body = fetch("/api/catalog-bridge/v1/health/", auth=True)
ready_status, ready_body = fetch("/api/catalog-bridge/v1/publish-readiness/", auth=True)
js_status, js_body = fetch("/static/store/js/phase50-profile-selector.js?v=" + target)
css_status, css_body = fetch("/static/store/css/phase50-profile-selector.css?v=" + target)
health = json.loads(health_body.decode("utf-8"))
ready = json.loads(ready_body.decode("utf-8"))
print("HOME_HTTP=" + str(home_status))
print("STORE_HTTP=" + str(store_status))
print("BRIDGE_HEALTH_HTTP=" + str(health_status))
print("PUBLISH_READINESS_HTTP=" + str(ready_status))
print("STATIC_JS_HTTP=" + str(js_status))
print("STATIC_CSS_HTTP=" + str(css_status))
print("BRIDGE_HEALTH_STATUS=" + str(health.get("status")))
print("PUBLISH_READY=" + repr(ready.get("ready")))
print("PUBLISH_BLOCKERS=" + repr(ready.get("blockers") or []))

if home_status != 200 or store_status != 200:
    raise SystemExit("PHASE50_A2G_DEPLOY_FAIL=public_http_not_200")
if health_status != 200 or health.get("status") != "ok":
    raise SystemExit("PHASE50_A2G_DEPLOY_FAIL=bridge_health_not_ok")
if ready_status != 200 or ready.get("ready") is not True:
    raise SystemExit("PHASE50_A2G_DEPLOY_FAIL=publish_readiness_not_ready")
if js_status != 200 or b"GUIDED_DIMENSIONS" not in js_body or b"store-profile-progress" not in js_body:
    raise SystemExit("PHASE50_A2G_DEPLOY_FAIL=guided_js_not_live")
if css_status != 200 or b"store-profile-progress" not in css_body or b"Phase50.A.2G" not in css_body:
    raise SystemExit("PHASE50_A2G_DEPLOY_FAIL=guided_css_not_live")
PY

printf '%s\n' "===== FINAL STATE ====="
printf 'FINAL_HEAD=%s\n' "$(git rev-parse HEAD)"
printf 'FINAL_WORKTREE=%s\n' "$(test -z "$(git status --porcelain --untracked-files=all)" && printf CLEAN || printf DIRTY)"
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"
printf '%s\n' "PHASE50_A2G_PRODUCTION_DEPLOY=PASS"
