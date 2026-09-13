#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
BRANCH="agent/phase49-3i18-operator-bulk-ai-rebuild"
EXPECTED_DB="sfkilvrs_EmiAdmin_3dprinthub"
EXPECTED_BASELINE="d7cf71dceca95e191a118336c7004683083278ee"
STATIC_ROOT="/home/sfkilvrs/public_html/static"
TARGET_SHA="${1:-}"
BACKUP_BASE="/home/sfkilvrs/3dprinthub-deploy-backups"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="$BACKUP_BASE/${STAMP}-phase50-a2h-storefront-showcase"
TMP_DELTA="/tmp/3dprinthub-a2h-delta-$$.txt"
STATIC_LIST="/tmp/3dprinthub-a2h-static-$$.txt"

cleanup() { rm -f "$TMP_DELTA" "$STATIC_LIST" 2>/dev/null || true; }
trap cleanup EXIT
fail() {
  printf 'PHASE50_A2H_DEPLOY_FAIL=%s\n' "$1" >&2
  printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT" >&2
  exit 1
}

printf '%s\n' "============================================================"
printf '%s\n' "3DPrintHub Phase50.A.2H Storefront Showcase Production Deploy"
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
if connection.vendor != "mysql": raise SystemExit("PHASE50_A2H_DEPLOY_FAIL=database_vendor_not_mysql")
if str(connection.settings_dict.get("NAME") or "") != expected: raise SystemExit("PHASE50_A2H_DEPLOY_FAIL=database_name_mismatch")
required={
("store","0036_phase50_checkout_snapshot"),("store","0037_phase50_professional_commerce_policy"),
("store","0038_phase50_profile_matrix"),("store","0039_phase50_filament_offer_pricing"),
("store","0040_phase50_filament_offer_operations"),("store","0041_phase50_filament_visual_identity"),
("store","0042_phase49_3i51_filament_registry_descriptions"),("website","0024_phase49_3i51_material_catalog_description")}
applied=set(MigrationRecorder.Migration.objects.filter(app__in={"store","website"}).values_list("app","name"))
missing=sorted(required-applied); print("REQUIRED_MIGRATIONS_MISSING="+repr(missing))
if missing: raise SystemExit("PHASE50_A2H_DEPLOY_FAIL=required_migrations_missing")
ex=MigrationExecutor(connection); plan=ex.migration_plan(ex.loader.graph.leaf_nodes())
print("CURRENT_MIGRATION_PLAN="+repr([(m.app_label,m.name,b) for m,b in plan]))
if plan: raise SystemExit("PHASE50_A2H_DEPLOY_FAIL=current_migration_plan_not_empty")
ready=publish_readiness(); print("PUBLISH_READY="+repr(ready.get("ready"))); print("PUBLISH_BLOCKERS="+repr(ready.get("blockers") or []))
if ready.get("ready") is not True: raise SystemExit("PHASE50_A2H_DEPLOY_FAIL=receiver_not_ready_before_deploy")
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
    PROJECT_CONTEXT.md|docs/*|scripts/host/phase50_a2h_storefront_showcase_deploy.sh) ;;
    static/css/brand-theme-preview.css|static/css/phase50-a2h-product-showcase.css|static/js/theme-preview.js) ;;
    static/store/css/phase50-profile-selector.css|static/store/js/phase50-profile-selector.js) ;;
    templates/website/partials/hero.html) ;;
    *) fail "unexpected_target_delta:$path" ;;
  esac
done < "$TMP_DELTA"

for required_path in \
  static/css/brand-theme-preview.css \
  static/css/phase50-a2h-product-showcase.css \
  static/js/theme-preview.js \
  static/store/css/phase50-profile-selector.css \
  static/store/js/phase50-profile-selector.js \
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
css/brand-theme-preview.css
css/phase50-a2h-product-showcase.css
js/theme-preview.js
store/css/phase50-profile-selector.css
store/js/phase50-profile-selector.js
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
ex=MigrationExecutor(connection); plan=ex.migration_plan(ex.loader.graph.leaf_nodes())
print("POST_MERGE_MIGRATION_PLAN="+repr([(m.app_label,m.name,b) for m,b in plan]))
if plan: raise SystemExit("PHASE50_A2H_DEPLOY_FAIL=post_merge_migration_plan_not_empty")
ready=publish_readiness(); print("POST_MERGE_PUBLISH_READY="+repr(ready.get("ready"))); print("POST_MERGE_PUBLISH_BLOCKERS="+repr(ready.get("blockers") or []))
if ready.get("ready") is not True: raise SystemExit("PHASE50_A2H_DEPLOY_FAIL=receiver_not_ready_after_merge")
PY

grep -Fq 'Phase50.A.2H' static/css/phase50-a2h-product-showcase.css || fail "hero_a2h_marker_missing"
grep -Fq 'Phase50.A.2H compact first-visit theme chooser' static/css/brand-theme-preview.css || fail "theme_a2h_marker_missing"
grep -Fq 'theme-preview-toggle' static/js/theme-preview.js || fail "theme_toggle_contract_missing"
grep -Fq 'Phase50.A.2H - price presentation only' static/store/css/phase50-profile-selector.css || fail "price_a2h_marker_missing"
grep -Fq 'store-profile-summary__price-value' static/store/js/phase50-profile-selector.js || fail "price_markup_contract_missing"

printf '%s\n' "===== COLLECTSTATIC ====="
"$PY" manage.py collectstatic --noinput
printf '%s\n' "===== COLLECTED STATIC HASHES ====="
while IFS= read -r rel; do
  [ -f "static/$rel" ] || fail "source_static_missing:$rel"
  [ -f "$STATIC_ROOT/$rel" ] || fail "collected_static_missing:$rel"
  A="$(sha256sum "static/$rel" | awk '{print $1}')"; B="$(sha256sum "$STATIC_ROOT/$rel" | awk '{print $1}')"
  printf 'STATIC_SHA %s source=%s collected=%s\n' "$rel" "$A" "$B"
  [ "$A" = "$B" ] || fail "collected_static_hash_mismatch:$rel"
done < "$STATIC_LIST"

printf '%s\n' "===== PASSENGER RESTART ====="
mkdir -p tmp; touch tmp/restart.txt; sleep 4
printf '%s\n' "===== PUBLIC / BRIDGE / A2H STATIC VERIFY ====="
"$PY" - "$TARGET_SHA" <<'PY'
import json, os, sys
from urllib import request
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django; django.setup()
from django.conf import settings
target=sys.argv[1]; base="https://3dprinthub.ir"; token=str(getattr(settings,"CATALOG_BRIDGE_TOKEN","") or "").strip()
if len(token)<24: raise SystemExit("PHASE50_A2H_DEPLOY_FAIL=bridge_token_missing_after_restart")
def fetch(path, auth=False, limit=2_000_000):
    h={"User-Agent":"3DPrintHub-Phase50.A.2H-Verify/1.0","Accept":"*/*","Cache-Control":"no-cache"}
    if auth: h["Authorization"]="Bearer "+token
    with request.urlopen(request.Request(base+path,headers=h),timeout=20) as r: return int(r.status), r.read(limit)
checks={}
checks['home']=fetch('/'); checks['store']=fetch('/store/')
checks['health']=fetch('/api/catalog-bridge/v1/health/',True); checks['ready']=fetch('/api/catalog-bridge/v1/publish-readiness/',True)
checks['hero']=fetch('/static/css/phase50-a2h-product-showcase.css?v='+target)
checks['theme_css']=fetch('/static/css/brand-theme-preview.css?v='+target); checks['theme_js']=fetch('/static/js/theme-preview.js?v='+target)
checks['selector_css']=fetch('/static/store/css/phase50-profile-selector.css?v='+target); checks['selector_js']=fetch('/static/store/js/phase50-profile-selector.js?v='+target)
for k,(s,_) in checks.items(): print(k.upper()+"_HTTP="+str(s))
if any(s!=200 for s,_ in checks.values()): raise SystemExit("PHASE50_A2H_DEPLOY_FAIL=http_not_200")
health=json.loads(checks['health'][1].decode('utf-8')); ready=json.loads(checks['ready'][1].decode('utf-8'))
print("BRIDGE_HEALTH_STATUS="+str(health.get('status'))); print("PUBLISH_READY="+repr(ready.get('ready'))); print("PUBLISH_BLOCKERS="+repr(ready.get('blockers') or []))
if health.get('status')!='ok': raise SystemExit("PHASE50_A2H_DEPLOY_FAIL=bridge_health_not_ok")
if ready.get('ready') is not True: raise SystemExit("PHASE50_A2H_DEPLOY_FAIL=publish_readiness_not_ready")
markers=[('hero',b'Phase50.A.2H'),('theme_css',b'Phase50.A.2H'),('theme_js',b'theme-preview-toggle'),('selector_css',b'Phase50.A.2H'),('selector_js',b'store-profile-summary__price-value')]
for key,marker in markers:
    if marker not in checks[key][1]: raise SystemExit("PHASE50_A2H_DEPLOY_FAIL=live_static_marker_missing:"+key)
print("A2H_PUBLIC_STATIC_MARKERS=PASS")
PY

printf '%s\n' "===== FINAL STATE ====="
printf 'FINAL_HEAD=%s\n' "$(git rev-parse HEAD)"
printf 'FINAL_WORKTREE=%s\n' "$(test -z "$(git status --porcelain --untracked-files=all)" && printf CLEAN || printf DIRTY)"
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"
printf '%s\n' "PHASE50_A2H_PRODUCTION_DEPLOY=PASS"
