#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
BRANCH="agent/phase49-3i18-operator-bulk-ai-rebuild"
EXPECTED_DB="sfkilvrs_EmiAdmin_3dprinthub"
EXPECTED_BASELINE="b1caeba0f20e711b29dfa9e0ff92a2f5186fb08d"
TARGET_SHA="${1:-}"
BACKUP_BASE="/home/sfkilvrs/3dprinthub-deploy-backups"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="$BACKUP_BASE/${STAMP}-phase50-zarinpal-current-api"
TMP_DELTA="/tmp/3dprinthub-zarinpal-current-api-delta-$$.txt"

cleanup() { rm -f "$TMP_DELTA" 2>/dev/null || true; }
trap cleanup EXIT
fail() {
  printf 'PHASE50_ZARINPAL_CURRENT_API_DEPLOY_FAIL=%s\n' "$1" >&2
  printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT" >&2
  exit 1
}

printf '%s\n' "============================================================"
printf '%s\n' "3DPrintHub Phase50 Secure ZarinPal Current API Compatibility"
printf '%s\n' "READINESS -> TLS -> BACKUP -> FF-ONLY -> RESTART -> VERIFY"
printf '%s\n' "NO MIGRATION / NO DATABASE WRITE / NO COLLECTSTATIC / NO GATEWAY ENABLE"
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
from django.conf import settings
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
print("PAYMENT_GATEWAY_ENABLED="+repr(bool(getattr(settings,"PAYMENT_GATEWAY_ENABLED",False))))
print("MERCHANT_ID_PRESENT="+repr(bool(str(getattr(settings,"ZARINPAL_MERCHANT_ID","") or "").strip())))
print("SITE_GATEWAY_ACTIVATION_NOT_CHANGED=PASS")
PY
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run

printf '%s\n' "===== OFFICIAL ZARINPAL OUTBOUND TLS ====="
"$PY" - <<'PY'
import socket, ssl
for host in ("payment.zarinpal.com", "sandbox.zarinpal.com"):
    ctx=ssl.create_default_context()
    with socket.create_connection((host,443), timeout=10) as raw:
        with ctx.wrap_socket(raw, server_hostname=host) as tls:
            if not tls.getpeercert(): raise SystemExit("missing_peer_certificate:"+host)
            print(host+":TLS="+str(tls.version()))
print("ZARINPAL_OUTBOUND_TLS=PASS")
PY

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
    config/settings.py) ;;
    website/payment_gateways/zarinpal.py) ;;
    website/test_phase30_zarinpal_provider.py) ;;
    scripts/host/phase50_zarinpal_current_api_deploy.sh) ;;
    *) fail "unexpected_target_delta:$path" ;;
  esac
done < "$TMP_DELTA"
for required_path in config/settings.py website/payment_gateways/zarinpal.py website/test_phase30_zarinpal_provider.py; do
  if git diff --quiet "$EXPECTED_BASELINE" "$FETCHED" -- "$required_path"; then fail "required_runtime_or_regression_delta_missing:$required_path"; fi
done
if grep -Eq '(^|/)migrations/[0-9]{4}_[^/]+\.py$|^requirements[^/]*\.txt$|^static/' "$TMP_DELTA"; then
  fail "migration_dependency_or_static_delta_detected"
fi
printf '%s\n' "NO_MIGRATION_DEPENDENCY_STATIC_DELTA=PASS"

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

printf '%s\n' "===== POST-MERGE PAYMENT CONTRACT ====="
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
"$PY" manage.py phase30_payment_audit
"$PY" - <<'PY'
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django; django.setup()
from django.conf import settings
from django.test.utils import override_settings
from website.payment_gateways.zarinpal import ZarinPalGateway
expected={
  "request":"https://payment.zarinpal.com/pg/v4/payment/request.json",
  "verify":"https://payment.zarinpal.com/pg/v4/payment/verify.json",
  "start":"https://payment.zarinpal.com/pg/StartPay/",
}
print("PAYMENT_GATEWAY_ENABLED="+repr(bool(settings.PAYMENT_GATEWAY_ENABLED)))
print("MERCHANT_ID_PRESENT="+repr(bool(str(settings.ZARINPAL_MERCHANT_ID or "").strip())))
with override_settings(ZARINPAL_MERCHANT_ID="00000000-0000-0000-0000-000000000000", ZARINPAL_SANDBOX=False):
    g=ZarinPalGateway()
    actual={"request":g.request_url,"verify":g.verify_url,"start":g.start_url}
print("LIVE_ENDPOINTS="+repr(actual))
if actual != expected: raise SystemExit("live_endpoint_contract_mismatch")
with override_settings(ZARINPAL_MERCHANT_ID="00000000-0000-0000-0000-000000000000", ZARINPAL_SANDBOX=True):
    g=ZarinPalGateway()
    sandbox=(g.request_url,g.verify_url,g.start_url)
print("SANDBOX_ENDPOINTS="+repr(sandbox))
if sandbox != (
    "https://sandbox.zarinpal.com/pg/v4/payment/request.json",
    "https://sandbox.zarinpal.com/pg/v4/payment/verify.json",
    "https://sandbox.zarinpal.com/pg/StartPay/",
): raise SystemExit("sandbox_endpoint_contract_mismatch")
print("ZARINPAL_CURRENT_API_CONTRACT=PASS")
PY

"$PY" - <<'PY'
import ast
from pathlib import Path
path = Path("website/payment_gateways/zarinpal.py")
tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
verify = None
for node in tree.body:
    if isinstance(node, ast.ClassDef) and node.name == "ZarinPalGateway":
        verify = next((child for child in node.body if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name == "verify"), None)
        break
if verify is None:
    raise SystemExit("verify_function_missing")
payload_keys = None
for node in ast.walk(verify):
    if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "payload" for target in node.targets):
        if not isinstance(node.value, ast.Dict):
            raise SystemExit("verify_payload_not_dict")
        payload_keys = [key.value for key in node.value.keys if isinstance(key, ast.Constant) and isinstance(key.value, str)]
        break
expected = ["merchant_id", "amount", "authority"]
print("VERIFY_PAYLOAD_KEYS=" + repr(payload_keys))
if payload_keys != expected:
    raise SystemExit("verify_payload_contract_mismatch")
print("VERIFY_PAYLOAD_CONTRACT=PASS")
PY

printf '%s\n' "===== PASSENGER RESTART ====="
mkdir -p tmp
touch tmp/restart.txt
sleep 4

printf '%s\n' "===== PUBLIC VERIFY ====="
"$PY" - <<'PY'
from urllib import request
for path in ("/", "/store/"):
    req=request.Request("https://3dprinthub.ir"+path,headers={"User-Agent":"3DPrintHub-ZarinPal-Compatibility/1.0","Cache-Control":"no-cache"})
    with request.urlopen(req,timeout=20) as response:
        print(path+" HTTP="+str(response.status))
        if int(response.status) != 200: raise SystemExit("public_http_not_200:"+path)
print("PUBLIC_RUNTIME_VERIFY=PASS")
PY

printf '%s\n' "===== FINAL STATE ====="
printf 'FINAL_HEAD=%s\n' "$(git rev-parse HEAD)"
printf 'FINAL_WORKTREE=%s\n' "$(test -z "$(git status --porcelain --untracked-files=all)" && printf CLEAN || printf DIRTY)"
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"
printf '%s\n' "PHASE50_ZARINPAL_CURRENT_API_DEPLOY=PASS"
