#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
BRANCH="agent/phase49-3i18-operator-bulk-ai-rebuild"
EXPECTED_DB="sfkilvrs_EmiAdmin_3dprinthub"
EXPECTED_BASELINE="443d1b70ecdf59e26b106d8887d56cb0e61ece8d"
TARGET_SHA="${1:-}"
BACKUP_BASE="/home/sfkilvrs/3dprinthub-deploy-backups"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="$BACKUP_BASE/${STAMP}-phase50-a2g-bridge-media-hotfix"
TMP_DELTA="/tmp/3dprinthub-a2g-bridge-delta-$$.txt"

cleanup() { rm -f "$TMP_DELTA" 2>/dev/null || true; }
trap cleanup EXIT
fail() {
  printf 'PHASE50_A2G_BRIDGE_DEPLOY_FAIL=%s\n' "$1" >&2
  printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT" >&2
  exit 1
}

printf '%s\n' "============================================================"
printf '%s\n' "3DPrintHub Phase50.A.2G Bridge Public Media Hotfix Deploy"
printf '%s\n' "READINESS -> VERIFIED SOURCE BACKUP -> FF-ONLY -> RESTART -> VERIFY"
printf '%s\n' "NO DATABASE MIGRATION / NO DATABASE WRITE / NO COLLECTSTATIC"
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
from catalog_bridge.publish_readiness import publish_readiness
expected=sys.argv[1]
print("DB_VENDOR="+str(connection.vendor))
print("DB_NAME="+str(connection.settings_dict.get("NAME") or ""))
if connection.vendor != "mysql": raise SystemExit("database_vendor_not_mysql")
if str(connection.settings_dict.get("NAME") or "") != expected: raise SystemExit("database_name_mismatch")
ex=MigrationExecutor(connection)
plan=ex.migration_plan(ex.loader.graph.leaf_nodes())
print("CURRENT_MIGRATION_PLAN="+repr([(m.app_label,m.name,b) for m,b in plan]))
if plan: raise SystemExit("current_migration_plan_not_empty")
ready=publish_readiness()
print("PUBLISH_READY="+repr(ready.get("ready")))
print("PUBLISH_BLOCKERS="+repr(ready.get("blockers") or []))
if ready.get("ready") is not True: raise SystemExit("receiver_not_ready_before_deploy")
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
printf '%s\n' "===== TARGET DELTA ====="
cat "$TMP_DELTA"
while IFS= read -r path; do
  [ -n "$path" ] || continue
  case "$path" in
    PROJECT_CONTEXT.md|docs/*) ;;
    catalog_bridge/unified_views.py|catalog_bridge/test_phase49_unified_bridge.py) ;;
    scripts/host/phase50_a2g_bridge_media_hotfix_deploy.sh) ;;
    *) fail "unexpected_target_delta:$path" ;;
  esac
done < "$TMP_DELTA"

if git diff --quiet "$EXPECTED_BASELINE" "$FETCHED" -- catalog_bridge/unified_views.py; then
  fail "required_runtime_delta_missing:catalog_bridge/unified_views.py"
fi
if grep -Eq '(^|/)migrations/[0-9]{4}_[^/]+\.py$|^requirements[^/]*\.txt$|^config/settings' "$TMP_DELTA"; then
  fail "migration_dependency_or_settings_delta_detected"
fi
printf '%s\n' "NO_MIGRATION_OR_DEPENDENCY_DELTA=PASS"

printf '%s\n' "===== VERIFIED SOURCE / ENV BACKUP ====="
mkdir -p "$BACKUP_ROOT"
chmod 700 "$BACKUP_ROOT"
git bundle create "$BACKUP_ROOT/source-before.bundle" HEAD
git bundle verify "$BACKUP_ROOT/source-before.bundle"
printf '%s\n' "$CURRENT_HEAD" > "$BACKUP_ROOT/source-head.txt"
printf '%s\n' "$CURRENT_BRANCH" > "$BACKUP_ROOT/source-branch.txt"
if [ -f .env ]; then cp -p .env "$BACKUP_ROOT/.env"; chmod 600 "$BACKUP_ROOT/.env"; fi
sha256sum "$BACKUP_ROOT/source-before.bundle" > "$BACKUP_ROOT/source-bundle.sha256"
if [ -f "$BACKUP_ROOT/.env" ]; then sha256sum "$BACKUP_ROOT/.env" > "$BACKUP_ROOT/env.sha256"; fi
(
  cd "$BACKUP_ROOT"
  sha256sum -c source-bundle.sha256
  if [ -f env.sha256 ]; then sha256sum -c env.sha256; fi
)
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
if plan: raise SystemExit("post_merge_migration_plan_not_empty")
ready=publish_readiness()
print("POST_MERGE_PUBLISH_READY="+repr(ready.get("ready")))
print("POST_MERGE_PUBLISH_BLOCKERS="+repr(ready.get("blockers") or []))
if ready.get("ready") is not True: raise SystemExit("receiver_not_ready_after_merge")
PY

grep -Fq '_public_product_image_url' catalog_bridge/unified_views.py || fail "bridge_public_media_resolver_missing"
grep -Fq '/media/store/imported-models/' catalog_bridge/test_phase49_unified_bridge.py || fail "bridge_media_regression_missing"

printf '%s\n' "===== PASSENGER RESTART ====="
mkdir -p tmp
touch tmp/restart.txt
sleep 4

printf '%s\n' "===== PUBLIC BRIDGE PRODUCT / HERO MEDIA VERIFY ====="
"$PY" - "$TARGET_SHA" <<'PY'
import json, os, sys
from urllib import request
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django; django.setup()
from django.conf import settings
base="https://3dprinthub.ir"
token=str(getattr(settings,"CATALOG_BRIDGE_TOKEN","") or "").strip()
if len(token)<24: raise SystemExit("bridge_token_missing_after_restart")
def fetch(path, auth=False, limit=2_000_000):
    headers={"User-Agent":"3DPrintHub-A2G-Bridge-Hotfix-Verify/1.0","Accept":"*/*","Cache-Control":"no-cache"}
    if auth: headers["Authorization"]="Bearer "+token
    with request.urlopen(request.Request(base+path,headers=headers),timeout=20) as r:
        return int(r.status), str(r.headers.get("Content-Type") or ""), r.read(limit)
health_s,_,health_b=fetch('/api/catalog-bridge/v1/health/',True)
ready_s,_,ready_b=fetch('/api/catalog-bridge/v1/publish-readiness/',True)
product_s,_,product_b=fetch('/api/catalog-bridge/v1/products/15/',True)
hero_s,_,hero_b=fetch('/api/catalog-bridge/v1/hero-slides/',True)
print("HEALTH_HTTP="+str(health_s)); print("READY_HTTP="+str(ready_s)); print("PRODUCT_HTTP="+str(product_s)); print("HERO_HTTP="+str(hero_s))
if any(s!=200 for s in (health_s,ready_s,product_s,hero_s)): raise SystemExit("bridge_http_not_200")
health=json.loads(health_b.decode('utf-8')); ready=json.loads(ready_b.decode('utf-8'))
product_payload=json.loads(product_b.decode('utf-8')); hero=json.loads(hero_b.decode('utf-8'))
if health.get('status')!='ok': raise SystemExit("bridge_health_not_ok")
if ready.get('ready') is not True: raise SystemExit("publish_readiness_not_ready")
product=product_payload.get('product') or {}
if int(product.get('id') or 0)!=15: raise SystemExit("site_product_15_missing")
images=product.get('images') or []
print("PRODUCT15_IMAGE_COUNT="+str(len(images)))
if len(images)<2: raise SystemExit("site_product_15_expected_gallery_missing")
for idx,row in enumerate(images,1):
    url=str(row.get('url') or '').strip()
    print("PRODUCT15_IMAGE_%d_URL=%s"%(idx,url))
    if '/media/store/imported-models/' in url: raise SystemExit("private_imported_media_exposed")
    if not url.startswith('/media/store/products/'): raise SystemExit("product_media_not_product_owned")
    s,ct,_=fetch(url)
    print("PRODUCT15_IMAGE_%d_HTTP=%s CONTENT_TYPE=%s"%(idx,s,ct))
    if s!=200 or 'image/webp' not in ct.lower(): raise SystemExit("product_media_http_or_type_invalid")
slides=hero.get('items') or []
print("HERO_SLIDE_COUNT="+str(len(slides)))
for row in slides:
    selected_url=str(row.get('selected_image_url') or '').strip()
    if '/media/store/imported-models/' in selected_url: raise SystemExit("hero_private_imported_media_exposed")
slide=next((x for x in slides if int(x.get('product_id') or 0)==15),None)
if slide:
    hero_url=str(slide.get('selected_image_url') or '').strip()
    print("PRODUCT15_HERO_URL="+hero_url)
    if hero_url:
        s,ct,_=fetch(hero_url)
        print("PRODUCT15_HERO_HTTP=%s CONTENT_TYPE=%s"%(s,ct))
        if s!=200 or 'image/webp' not in ct.lower(): raise SystemExit("hero_media_http_or_type_invalid")
else:
    print("PRODUCT15_HERO=NOT_CONFIGURED")
print("A2G_BRIDGE_PUBLIC_MEDIA_VERIFY=PASS")
PY

printf '%s\n' "===== FINAL STATE ====="
printf 'FINAL_HEAD=%s\n' "$(git rev-parse HEAD)"
printf 'FINAL_WORKTREE=%s\n' "$(test -z "$(git status --porcelain --untracked-files=all)" && printf CLEAN || printf DIRTY)"
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"
printf '%s\n' "PHASE50_A2G_BRIDGE_MEDIA_HOTFIX_DEPLOY=PASS"