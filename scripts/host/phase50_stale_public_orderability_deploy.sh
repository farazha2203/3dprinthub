#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
BRANCH="agent/phase49-3i18-operator-bulk-ai-rebuild"
EXPECTED_DB="sfkilvrs_EmiAdmin_3dprinthub"
EXPECTED_BASELINE="70a74e6f21113ae6bc5ed1f679d1e57e4e5a8eb7"
TARGET_SHA="${1:-}"
BACKUP_BASE="/home/sfkilvrs/3dprinthub-deploy-backups"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="$BACKUP_BASE/${STAMP}-phase50-stale-public-orderability"
TMP_DELTA="/tmp/3dprinthub-stale-public-orderability-delta-$$.txt"

cleanup() { rm -f "$TMP_DELTA" 2>/dev/null || true; }
trap cleanup EXIT
fail() {
  printf 'PHASE50_STALE_PUBLIC_DEPLOY_FAIL=%s\n' "$1" >&2
  printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT" >&2
  exit 1
}

printf '%s\n' "============================================================"
printf '%s\n' "3DPrintHub Phase50 Stale Public Orderability Hotfix Deploy"
printf '%s\n' "READINESS -> BACKUP -> FF-ONLY -> RESTART -> VERIFY"
printf '%s\n' "NO MIGRATION / NO DATABASE WRITE / NO COLLECTSTATIC"
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

printf '%s\n' "===== CURRENT DATABASE / READINESS ====="
"$PY" - "$EXPECTED_DB" <<'PY'
import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django; django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from catalog_bridge.publish_readiness import publish_readiness
expected=sys.argv[1]
print("DB_VENDOR="+str(connection.vendor)); print("DB_NAME="+str(connection.settings_dict.get("NAME") or ""))
if connection.vendor != "mysql": raise SystemExit("database_vendor_not_mysql")
if str(connection.settings_dict.get("NAME") or "") != expected: raise SystemExit("database_name_mismatch")
ex=MigrationExecutor(connection); plan=ex.migration_plan(ex.loader.graph.leaf_nodes())
print("CURRENT_MIGRATION_PLAN="+repr([(m.app_label,m.name,b) for m,b in plan]))
if plan: raise SystemExit("current_migration_plan_not_empty")
ready=publish_readiness(); print("PUBLISH_READY="+repr(ready.get("ready"))); print("PUBLISH_BLOCKERS="+repr(ready.get("blockers") or []))
if ready.get("ready") is not True: raise SystemExit("receiver_not_ready_before_deploy")
PY
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run

printf '%s\n' "===== LIVE TARGET / FETCH_HEAD ====="
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
    store/management/commands/phase37_import_catalog_center.py) ;;
    store/phase49_catalog_visibility.py|store/test_phase49_catalog_visibility.py) ;;
    scripts/host/phase50_stale_public_orderability_deploy.sh) ;;
    *) fail "unexpected_target_delta:$path" ;;
  esac
done < "$TMP_DELTA"

for required_path in \
  store/management/commands/phase37_import_catalog_center.py \
  store/phase49_catalog_visibility.py
do
  if git diff --quiet "$EXPECTED_BASELINE" "$FETCHED" -- "$required_path"; then
    fail "required_runtime_delta_missing:$required_path"
  fi
done
if grep -Eq '(^|/)migrations/[0-9]{4}_[^/]+\.py$|^requirements[^/]*\.txt$|^config/settings' "$TMP_DELTA"; then
  fail "migration_dependency_or_settings_delta_detected"
fi
printf '%s\n' "NO_MIGRATION_OR_DEPENDENCY_DELTA=PASS"

printf '%s\n' "===== VERIFIED SOURCE / ENV BACKUP ====="
mkdir -p "$BACKUP_ROOT"; chmod 700 "$BACKUP_ROOT"
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

printf '%s\n' "===== POST-MERGE SAFETY / CONTRACT ====="
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
"$PY" - <<'PY'
import os
from types import SimpleNamespace
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django; django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from catalog_bridge.publish_readiness import publish_readiness
from store.models import Product
from store.phase50_orderability import variant_is_orderable
ex=MigrationExecutor(connection); plan=ex.migration_plan(ex.loader.graph.leaf_nodes())
print("POST_MERGE_MIGRATION_PLAN="+repr([(m.app_label,m.name,b) for m,b in plan]))
if plan: raise SystemExit("post_merge_migration_plan_not_empty")
ready=publish_readiness(); print("POST_MERGE_PUBLISH_READY="+repr(ready.get("ready"))); print("POST_MERGE_PUBLISH_BLOCKERS="+repr(ready.get("blockers") or []))
if ready.get("ready") is not True: raise SystemExit("receiver_not_ready_after_merge")
base=dict(stock_status="made_to_order",track_inventory=False,allow_backorder=False,stock_quantity=0,reserved_quantity=0,color_stock_sufficient=True)
if not variant_is_orderable(SimpleNamespace(**base)): raise SystemExit("orderability_positive_contract_failed")
if variant_is_orderable(SimpleNamespace(**{**base,"color_stock_sufficient":False})): raise SystemExit("orderability_negative_contract_failed")
for product_id in (16,17):
    product=Product.objects.get(pk=product_id)
    variants=list(product.variants.filter(is_active=True))
    ok=any(variant_is_orderable(v) for v in variants)
    print(f"PRODUCT_{product_id}_ORDERABLE={ok}")
    if not ok: raise SystemExit(f"known_good_product_not_orderable:{product_id}")
print("ORDERABILITY_CONTRACT=PASS")
PY

grep -Fq 'stale_public' store/phase49_catalog_visibility.py || fail "stale_public_deactivation_contract_missing"
grep -Fq 'visibility is not None and not visibility.visible' store/management/commands/phase37_import_catalog_center.py || fail "importer_publish_incomplete_contract_missing"

printf '%s\n' "===== PASSENGER RESTART ====="
mkdir -p tmp
touch tmp/restart.txt
sleep 4

printf '%s\n' "===== PUBLIC / BRIDGE VERIFY ====="
"$PY" - <<'PY'
import json, os
from urllib import request
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django; django.setup()
from django.conf import settings
base="https://3dprinthub.ir"
token=str(getattr(settings,"CATALOG_BRIDGE_TOKEN","") or "").strip()
if len(token)<24: raise SystemExit("bridge_token_missing_after_restart")
def fetch(path, auth=False, limit=1_000_000):
    headers={"User-Agent":"3DPrintHub-Stale-Public-Hotfix/1.0","Accept":"*/*","Cache-Control":"no-cache"}
    if auth: headers["Authorization"]="Bearer "+token
    with request.urlopen(request.Request(base+path,headers=headers),timeout=20) as response:
        return int(response.status), response.read(limit)
checks={
    "home": fetch("/"),
    "store": fetch("/store/"),
    "health": fetch("/api/catalog-bridge/v1/health/", True),
    "ready": fetch("/api/catalog-bridge/v1/publish-readiness/", True),
}
for key,(status,_) in checks.items(): print(key.upper()+"_HTTP="+str(status))
if any(status != 200 for status,_ in checks.values()): raise SystemExit("public_or_bridge_http_not_200")
health=json.loads(checks["health"][1].decode("utf-8")); ready=json.loads(checks["ready"][1].decode("utf-8"))
print("BRIDGE_HEALTH_STATUS="+str(health.get("status")))
print("PUBLIC_PUBLISH_READY="+repr(ready.get("ready")))
print("PUBLIC_PUBLISH_BLOCKERS="+repr(ready.get("blockers") or []))
if health.get("status") != "ok": raise SystemExit("bridge_health_not_ok")
if ready.get("ready") is not True: raise SystemExit("public_publish_readiness_not_ready")
print("STALE_PUBLIC_ORDERABILITY_PUBLIC_VERIFY=PASS")
PY

printf '%s\n' "===== FINAL STATE ====="
printf 'FINAL_HEAD=%s\n' "$(git rev-parse HEAD)"
printf 'FINAL_WORKTREE=%s\n' "$(test -z "$(git status --porcelain --untracked-files=all)" && printf CLEAN || printf DIRTY)"
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"
printf '%s\n' "PHASE50_STALE_PUBLIC_ORDERABILITY_DEPLOY=PASS"
