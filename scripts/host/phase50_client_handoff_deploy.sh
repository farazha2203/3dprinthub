#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
BRANCH="agent/phase49-3i18-operator-bulk-ai-rebuild"
EXPECTED_DB="sfkilvrs_EmiAdmin_3dprinthub"
EXPECTED_BASELINE="70a74e6f21113ae6bc5ed1f679d1e57e4e5a8eb7"
STATIC_ROOT="/home/sfkilvrs/public_html/static"
TARGET_SHA="${1:-}"
BACKUP_BASE="/home/sfkilvrs/3dprinthub-deploy-backups"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="$BACKUP_BASE/${STAMP}-phase50-client-handoff"
TMP_DELTA="/tmp/3dprinthub-handoff-delta-$$.txt"
STATIC_LIST="/tmp/3dprinthub-handoff-static-$$.txt"

cleanup() { rm -f "$TMP_DELTA" "$STATIC_LIST" 2>/dev/null || true; }
trap cleanup EXIT
fail() {
  printf 'PHASE50_HANDOFF_DEPLOY_FAIL=%s\n' "$1" >&2
  printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT" >&2
  exit 1
}

printf '%s\n' "============================================================"
printf '%s\n' "3DPrintHub Client Handoff Production Deploy"
printf '%s\n' "READINESS -> VERIFIED BACKUP -> FF-ONLY -> STATIC -> RESTART -> VERIFY"
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
printf 'ROOT=%s\nORIGIN=%s\nCURRENT_BRANCH=%s\nCURRENT_HEAD=%s\nEXPECTED_BASELINE=%s\nTARGET_SHA=%s\n' \
  "$ROOT" "$ORIGIN" "$CURRENT_BRANCH" "$CURRENT_HEAD" "$EXPECTED_BASELINE" "$TARGET_SHA"
case "$ORIGIN" in *farazha2203/3dprinthub.git|*farazha2203/3dprinthub) ;; *) fail "wrong_repository" ;; esac
[ "$CURRENT_BRANCH" = "$BRANCH" ] || fail "wrong_branch"
[ "$CURRENT_HEAD" = "$EXPECTED_BASELINE" ] || fail "host_baseline_changed"
[ -z "$STATUS" ] || { printf '%s\n' "$STATUS"; fail "production_worktree_dirty"; }

printf '%s\n' "===== CURRENT DB / MIGRATION / READINESS ====="
"$PY" - "$EXPECTED_DB" <<'PY'
import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django; django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.recorder import MigrationRecorder
from catalog_bridge.publish_readiness import publish_readiness
expected=sys.argv[1]
print("DB_VENDOR="+str(connection.vendor))
print("DB_NAME="+str(connection.settings_dict.get("NAME") or ""))
if connection.vendor != "mysql": raise SystemExit("PHASE50_HANDOFF_DEPLOY_FAIL=database_vendor_not_mysql")
if str(connection.settings_dict.get("NAME") or "") != expected: raise SystemExit("PHASE50_HANDOFF_DEPLOY_FAIL=database_name_mismatch")
required={
("store","0036_phase50_checkout_snapshot"),("store","0037_phase50_professional_commerce_policy"),
("store","0038_phase50_profile_matrix"),("store","0039_phase50_filament_offer_pricing"),
("store","0040_phase50_filament_offer_operations"),("store","0041_phase50_filament_visual_identity"),
("store","0042_phase49_3i51_filament_registry_descriptions"),("website","0024_phase49_3i51_material_catalog_description")}
applied=set(MigrationRecorder.Migration.objects.filter(app__in={"store","website"}).values_list("app","name"))
missing=sorted(required-applied); print("REQUIRED_MIGRATIONS_MISSING="+repr(missing))
if missing: raise SystemExit("PHASE50_HANDOFF_DEPLOY_FAIL=required_migrations_missing")
ex=MigrationExecutor(connection); plan=ex.migration_plan(ex.loader.graph.leaf_nodes())
print("CURRENT_MIGRATION_PLAN="+repr([(m.app_label,m.name,b) for m,b in plan]))
if plan: raise SystemExit("PHASE50_HANDOFF_DEPLOY_FAIL=current_migration_plan_not_empty")
ready=publish_readiness(); print("PUBLISH_READY="+repr(ready.get("ready"))); print("PUBLISH_BLOCKERS="+repr(ready.get("blockers") or []))
if ready.get("ready") is not True: raise SystemExit("PHASE50_HANDOFF_DEPLOY_FAIL=receiver_not_ready_before_deploy")
PY
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run

printf '%s\n' "===== LIVE TARGET / EXPLICIT FETCH_HEAD ====="
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
printf '%s\n' "===== TARGET DELTA ====="; cat "$TMP_DELTA"
while IFS= read -r path; do
  [ -n "$path" ] || continue
  case "$path" in
    AGENTS.md|PROJECT_CONTEXT.md|docs/*) ;;
    catalog_bridge/store_reset.py|catalog_bridge/test_phase50_store_reset.py|catalog_bridge/urls.py) ;;
    catalog_center/app/db.py|catalog_center/app/instagram_publish.py|catalog_center/app/phase49_3i49_site_publish.py|catalog_center/app/secure_secrets.py|catalog_center/app/site_connection.py) ;;
    catalog_center/qt6/image_gallery.py|catalog_center/qt6/kernel.py|catalog_center/qt6/pages.py|catalog_center/qt6/product_explorer.py|catalog_center/qt6/product_wizard.py|catalog_center/qt6/settings_page.py) ;;
    catalog_center/tests/test_epic49_final.py|catalog_center/tests/test_phase49_3i42b_core_parity.py|catalog_center/tests/test_phase49_3i47_qt_workspace_image_bulk_ai.py|catalog_center/tests/test_phase49_3i49_site_bulk_publish.py|catalog_center/tests/test_phase49_3i51_windows_site_finalization.py|catalog_center/tests/test_phase50_instagram_publish.py) ;;
    scripts/host/phase50_stale_public_orderability_deploy.sh|scripts/host/phase50_store_reset_prepare.py|scripts/host/phase50_client_handoff_deploy.sh) ;;
    static/css/phase50-a2i-slicebox-hero.css|static/js/phase50-a2i-slicebox-hero.js|templates/website/partials/hero.html|website/test_phase50_a2i_slicebox_hero.py) ;;
    store/management/commands/phase37_import_catalog_center.py|store/phase49_catalog_visibility.py|store/test_phase49_catalog_visibility.py) ;;
    *) fail "unexpected_target_delta:$path" ;;
  esac
done < "$TMP_DELTA"

for required_path in \
  catalog_bridge/store_reset.py \
  catalog_bridge/urls.py \
  scripts/host/phase50_store_reset_prepare.py \
  store/phase49_catalog_visibility.py \
  static/css/phase50-a2i-slicebox-hero.css \
  static/js/phase50-a2i-slicebox-hero.js \
  templates/website/partials/hero.html
do
  if git diff --quiet "$EXPECTED_BASELINE" "$FETCHED" -- "$required_path"; then fail "required_runtime_delta_missing:$required_path"; fi
done
if grep -Eq '(^|/)migrations/[0-9]{4}_[^/]+\.py$|^requirements[^/]*\.txt$|^config/settings' "$TMP_DELTA"; then
  fail "migration_dependency_or_settings_delta_detected"
fi
printf '%s\n' "NO_MIGRATION_OR_DEPENDENCY_DELTA=PASS"
printf '%s\n' "===== VERIFIED SOURCE / ENV / STATIC BACKUP ====="
mkdir -p "$BACKUP_ROOT/static-before"; chmod 700 "$BACKUP_ROOT"
git bundle create "$BACKUP_ROOT/source-before.bundle" HEAD
git bundle verify "$BACKUP_ROOT/source-before.bundle"
printf '%s\n' "$CURRENT_HEAD" > "$BACKUP_ROOT/source-head.txt"
printf '%s\n' "$CURRENT_BRANCH" > "$BACKUP_ROOT/source-branch.txt"
if [ -f .env ]; then cp -p .env "$BACKUP_ROOT/.env"; chmod 600 "$BACKUP_ROOT/.env"; fi
cat > "$STATIC_LIST" <<'EOF'
css/phase50-a2i-slicebox-hero.css
js/phase50-a2i-slicebox-hero.js
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
if find "$BACKUP_ROOT/static-before" -type f -print -quit | grep -q .; then
  (cd "$BACKUP_ROOT/static-before" && find . -type f -print0 | sort -z | xargs -0 sha256sum) > "$BACKUP_ROOT/static-before.sha256"
fi
(cd "$BACKUP_ROOT" && sha256sum -c source-bundle.sha256 && if [ -f env.sha256 ]; then sha256sum -c env.sha256; fi)
if [ -f "$BACKUP_ROOT/static-before.sha256" ]; then
  (cd "$BACKUP_ROOT/static-before" && sha256sum -c "$BACKUP_ROOT/static-before.sha256")
fi
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"
printf '%s\n' "PREDEPLOY_BACKUP_VERIFIED=YES"

printf '%s\n' "===== FF-ONLY DEPLOY ====="
git merge --ff-only "$FETCHED"
[ "$(git rev-parse HEAD)" = "$TARGET_SHA" ] || fail "deployed_head_mismatch"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "worktree_dirty_after_merge"
printf 'DEPLOYED_HEAD=%s\n' "$(git rev-parse HEAD)"

printf '%s\n' "===== POST-MERGE SAFETY ====="
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
print("POST_MERGE_MIGRATION_PLAN="+repr([(m.app_label,m.name,b) for m,b in plan]))
if plan: raise SystemExit("PHASE50_HANDOFF_DEPLOY_FAIL=post_merge_migration_plan_not_empty")
ready=publish_readiness()
print("POST_MERGE_PUBLISH_READY="+repr(ready.get("ready")))
print("POST_MERGE_PUBLISH_BLOCKERS="+repr(ready.get("blockers") or []))
if ready.get("ready") is not True: raise SystemExit("PHASE50_HANDOFF_DEPLOY_FAIL=receiver_not_ready_after_merge")
PY

grep -Fq 'phase50-store-reset-v2' catalog_bridge/store_reset.py || fail "store_reset_contract_missing"
grep -Fq 'store-reset/' catalog_bridge/urls.py || fail "store_reset_route_missing"
grep -Fq 'data-p50i-slicebox' templates/website/partials/hero.html || fail "hero_slicebox_template_marker_missing"
grep -Fq 'window.P50SliceboxHero' static/js/phase50-a2i-slicebox-hero.js || fail "hero_slicebox_runtime_marker_missing"
grep -Fq 'Phase50.A.2I' static/css/phase50-a2i-slicebox-hero.css || fail "hero_slicebox_css_marker_missing"

printf '%s\n' "===== COLLECTSTATIC ====="
"$PY" manage.py collectstatic --noinput
printf '%s\n' "===== COLLECTED STATIC HASHES ====="
while IFS= read -r rel; do
  [ -f "static/$rel" ] || fail "source_static_missing:$rel"
  [ -f "$STATIC_ROOT/$rel" ] || fail "collected_static_missing:$rel"
  A="$(sha256sum "static/$rel" | awk '{print $1}')"
  B="$(sha256sum "$STATIC_ROOT/$rel" | awk '{print $1}')"
  printf 'STATIC_SHA %s source=%s collected=%s\n' "$rel" "$A" "$B"
  [ "$A" = "$B" ] || fail "collected_static_hash_mismatch:$rel"
done < "$STATIC_LIST"

printf '%s\n' "===== PASSENGER RESTART ====="
mkdir -p tmp
touch tmp/restart.txt
sleep 4

printf '%s\n' "===== PUBLIC / BRIDGE / HERO VERIFY ====="
"$PY" - "$TARGET_SHA" <<'PY'
import json, os, sys
from urllib import request
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django; django.setup()
from django.conf import settings
target=sys.argv[1]
base="https://3dprinthub.ir"
token=str(getattr(settings,"CATALOG_BRIDGE_TOKEN","") or "").strip()
if len(token)<24: raise SystemExit("PHASE50_HANDOFF_DEPLOY_FAIL=bridge_token_missing_after_restart")
def fetch(path, auth=False, limit=2_000_000):
    headers={"User-Agent":"3DPrintHub-Client-Handoff-Verify/1.0","Accept":"*/*","Cache-Control":"no-cache"}
    if auth: headers["Authorization"]="Bearer "+token
    with request.urlopen(request.Request(base+path,headers=headers),timeout=20) as r:
        return int(r.status), str(r.headers.get("Content-Type") or ""), r.read(limit)
checks={}
checks["home"]=fetch("/")
checks["store"]=fetch("/store/")
checks["health"]=fetch("/api/catalog-bridge/v1/health/",True)
checks["ready"]=fetch("/api/catalog-bridge/v1/publish-readiness/",True)
checks["reset"]=fetch("/api/catalog-bridge/v1/store-reset/",True)
checks["hero_api"]=fetch("/api/catalog-bridge/v1/hero-slides/",True)
checks["hero_css"]=fetch("/static/css/phase50-a2i-slicebox-hero.css?v="+target)
checks["hero_js"]=fetch("/static/js/phase50-a2i-slicebox-hero.js?v="+target)
for key,(status,ctype,_) in checks.items(): print(key.upper()+"_HTTP="+str(status)+" CONTENT_TYPE="+ctype)
if any(status!=200 for status,_,_ in checks.values()): raise SystemExit("PHASE50_HANDOFF_DEPLOY_FAIL=http_not_200")
health=json.loads(checks["health"][2].decode("utf-8"))
ready=json.loads(checks["ready"][2].decode("utf-8"))
reset=json.loads(checks["reset"][2].decode("utf-8"))
hero_payload=json.loads(checks["hero_api"][2].decode("utf-8"))
if health.get("status")!="ok": raise SystemExit("PHASE50_HANDOFF_DEPLOY_FAIL=bridge_health_not_ok")
if ready.get("ready") is not True: raise SystemExit("PHASE50_HANDOFF_DEPLOY_FAIL=publish_readiness_not_ready")
if reset.get("contract")!="phase50-store-reset-v2": raise SystemExit("PHASE50_HANDOFF_DEPLOY_FAIL=store_reset_contract_missing")
print("STORE_RESET_STATUS="+str(reset.get("status")))
print("STORE_RESET_COUNTS="+repr(reset.get("counts") or {}))
slides=hero_payload.get("items") or []
for row in slides:
    selected=str(row.get("selected_image_url") or "").strip()
    if "/media/store/imported-models/" in selected: raise SystemExit("PHASE50_HANDOFF_DEPLOY_FAIL=hero_private_imported_media_exposed")
for key,marker in (("hero_css",b"Phase50.A.2I"),("hero_js",b"P50SliceboxHero")):
    if marker not in checks[key][2]: raise SystemExit("PHASE50_HANDOFF_DEPLOY_FAIL=live_static_marker_missing:"+key)
home=checks["home"][2]
for marker in (b"data-p50i-slicebox",b"phase50-a2i-slicebox-hero.css",b"phase50-a2i-slicebox-hero.js",b"v=50.3.0"):
    if marker not in home: raise SystemExit("PHASE50_HANDOFF_DEPLOY_FAIL=home_hero_marker_missing")
print("CLIENT_HANDOFF_PUBLIC_VERIFY=PASS")
PY

printf '%s\n' "===== FINAL STATE ====="
printf 'FINAL_HEAD=%s\n' "$(git rev-parse HEAD)"
printf 'FINAL_WORKTREE=%s\n' "$(test -z "$(git status --porcelain --untracked-files=all)" && printf CLEAN || printf DIRTY)"
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"
printf '%s\n' "PHASE50_CLIENT_HANDOFF_DEPLOY=PASS"
