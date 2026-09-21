#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
EXPECTED_DB="sfkilvrs_EmiAdmin_3dprinthub"
HOST_BRANCH="release/phase50-a2j-hero-20260915"
TARGET_BRANCH="release/phase50-a2r-payment-finance-admin-20260920"
EXPECTED_BASELINE="65d42e40979830b306e92457093aefe068086f66"
TARGET_SHA="${1:-}"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="/home/sfkilvrs/3dprinthub-deploy-backups/${STAMP}-phase50-a2r-payment-finance-admin"
TMP_DELTA="/tmp/3dprinthub-a2r-delta-$$.txt"

cleanup(){ rm -f "$TMP_DELTA" 2>/dev/null || true; }
trap cleanup EXIT
fail(){
  printf 'A2R_DEPLOY_FAIL=%s\n' "$1" >&2
  printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT" >&2
  exit 1
}

[ -n "$TARGET_SHA" ] || fail "target_sha_required"
cd "$ROOT"
[ -d .git ] || fail "project_git_missing"
[ "$(git branch --show-current)" = "$HOST_BRANCH" ] || fail "wrong_host_branch"
[ "$(git rev-parse HEAD)" = "$EXPECTED_BASELINE" ] || fail "host_baseline_changed"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "production_worktree_dirty"
ORIGIN="$(git remote get-url origin)"
case "$ORIGIN" in *farazha2203/3dprinthub.git|*farazha2203/3dprinthub) ;; *) fail "wrong_repository" ;; esac

"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
"$PY" - "$EXPECTED_DB" <<'PY'
import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
import django; django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from catalog_bridge.publish_readiness import publish_readiness
from store.phase50_commerce_policy import StorePaymentSettings
from website.models import SiteSetting
from website.payment_services import payment_gateway_status

expected=sys.argv[1]
print("DB_VENDOR="+str(connection.vendor))
print("DB_NAME="+str(connection.settings_dict.get("NAME") or ""))
if connection.vendor!="mysql" or str(connection.settings_dict.get("NAME") or "")!=expected:
    raise SystemExit("A2R_DEPLOY_FAIL=database_identity_mismatch")
executor=MigrationExecutor(connection)
plan=executor.migration_plan(executor.loader.graph.leaf_nodes())
print("MIGRATION_PLAN="+repr([(m.app_label,m.name,b) for m,b in plan]))
if plan:
    raise SystemExit("A2R_DEPLOY_FAIL=migration_plan_not_empty")
ready=publish_readiness()
print("PUBLISH_READY="+repr(ready.get("ready")))
print("PUBLISH_BLOCKERS="+repr(ready.get("blockers") or []))
if ready.get("ready") is not True:
    raise SystemExit("A2R_DEPLOY_FAIL=receiver_not_ready")
manual=StorePaymentSettings.objects.order_by("pk").first()
print("PAYMENT_SETTINGS_EXISTS="+str(manual is not None))
print("MANUAL_ACTIVE="+str(bool(manual and getattr(manual,"is_active",False))))
site=SiteSetting.objects.first()
gateway_ready,_=payment_gateway_status(site)
print("GATEWAY_READY="+str(bool(gateway_ready)))
PY

REMOTE_LINE="$(git ls-remote origin "refs/heads/$TARGET_BRANCH")"
REMOTE_SHA="$(printf '%s\n' "$REMOTE_LINE" | awk '{print $1}')"
printf 'REMOTE_SHA=%s\n' "$REMOTE_SHA"
[ "$REMOTE_SHA" = "$TARGET_SHA" ] || fail "target_not_live_github_head"
git fetch --no-tags origin "refs/heads/$TARGET_BRANCH"
FETCHED="$(git rev-parse FETCH_HEAD)"
[ "$FETCHED" = "$TARGET_SHA" ] || fail "fetched_target_mismatch"
git merge-base --is-ancestor "$EXPECTED_BASELINE" "$FETCHED" || fail "target_not_fast_forward"
git diff --name-only "$EXPECTED_BASELINE" "$FETCHED" > "$TMP_DELTA"
printf '%s\n' "===== A2R DELTA ====="
cat "$TMP_DELTA"

if grep -Eq '(^|/)migrations/[0-9]{4}_[^/]+\.py$|^requirements[^/]*\.txt$|^config/settings' "$TMP_DELTA"; then
  fail "migration_dependency_or_settings_delta_detected"
fi

while IFS= read -r changed; do
  case "$changed" in
    .github/workflows/phase50-a2r-payment-admin-ci.yml|\
    docs/CHANGELOG.md|docs/CURRENT_STATE.md|docs/ERRORS.md|docs/HOST_CONSTRAINTS.md|docs/REQUESTS.md|docs/ROADMAP.md|\
    docs/DEPLOYMENT.md|docs/phases/PHASE50_A2R_PAYMENT_FINANCE_ADMIN_CLOSURE.md|\
    store/management/commands/phase50_a2l_seed_manual_payment.py|store/test_phase50_a2l_manual_payment.py|\
    templates/admin/phase50_command_center.html|website/phase50a_admin_command_center.py|\
    website/templatetags/admin_console.py|website/test_phase50a_admin_command_center.py|\
    scripts/host/phase50_a2r_payment_finance_admin_deploy.sh)
      ;;
    *)
      fail "unexpected_target_delta:$changed"
      ;;
  esac
done < "$TMP_DELTA"

for required in \
  store/management/commands/phase50_a2l_seed_manual_payment.py \
  templates/admin/phase50_command_center.html \
  website/phase50a_admin_command_center.py \
  website/templatetags/admin_console.py \
  scripts/host/phase50_a2r_payment_finance_admin_deploy.sh
do
  grep -Fxq "$required" "$TMP_DELTA" || fail "required_delta_missing:$required"
done

mkdir -p "$BACKUP_ROOT"
chmod 700 "$BACKUP_ROOT"
git bundle create "$BACKUP_ROOT/source-before.bundle" HEAD
git bundle verify "$BACKUP_ROOT/source-before.bundle"
printf '%s\n' "$EXPECTED_BASELINE" > "$BACKUP_ROOT/source-head.txt"
printf '%s\n' "$HOST_BRANCH" > "$BACKUP_ROOT/source-branch.txt"
if [ -f .env ]; then
  cp -p .env "$BACKUP_ROOT/.env"
  chmod 600 "$BACKUP_ROOT/.env"
fi
sha256sum "$BACKUP_ROOT/source-before.bundle" > "$BACKUP_ROOT/source-bundle.sha256"
if [ -f "$BACKUP_ROOT/.env" ]; then sha256sum "$BACKUP_ROOT/.env" > "$BACKUP_ROOT/env.sha256"; fi
(cd "$BACKUP_ROOT" && sha256sum -c source-bundle.sha256 && if [ -f env.sha256 ]; then sha256sum -c env.sha256; fi)

export PHASE49_PROJECT_ROOT="$ROOT"
export PHASE49_BACKUP_ROOT="$BACKUP_ROOT"
"$PY" scripts/host/phase49_3i53_mysql_backup.py "$EXPECTED_DB"
gzip -t "$BACKUP_ROOT/database-before-3i53.sql.gz"
sha256sum "$BACKUP_ROOT/database-before-3i53.sql.gz" > "$BACKUP_ROOT/database-before.sha256"
(cd "$BACKUP_ROOT" && sha256sum -c database-before.sha256)
printf 'PREDEPLOY_BACKUP_VERIFIED=YES\n'
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"

git merge --ff-only "$FETCHED"
[ "$(git rev-parse HEAD)" = "$TARGET_SHA" ] || fail "deployed_head_mismatch"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "worktree_dirty_after_merge"

"$PY" -m py_compile \
  store/management/commands/phase50_a2l_seed_manual_payment.py \
  website/templatetags/admin_console.py \
  website/phase50a_admin_command_center.py
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
"$PY" - <<'PY'
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
import django; django.setup()
from django.contrib.auth import get_user_model
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import RequestFactory
from catalog_bridge.publish_readiness import publish_readiness
from store.phase50_commerce_policy import StorePaymentSettings
from website.models import SiteSetting
from website.payment_services import payment_gateway_status
from website.phase50a_admin_command_center import phase50_admin_command_center

executor=MigrationExecutor(connection)
plan=executor.migration_plan(executor.loader.graph.leaf_nodes())
if plan:
    raise SystemExit("A2R_DEPLOY_FAIL=post_merge_migration_plan_not_empty")
ready=publish_readiness()
if ready.get("ready") is not True:
    raise SystemExit("A2R_DEPLOY_FAIL=post_merge_receiver_not_ready")
manual=StorePaymentSettings.objects.order_by("pk").first()
manual_configured=bool(
    manual
    and str(getattr(manual,"account_holder","") or "").strip()
    and (
        str(getattr(manual,"card_number","") or "").strip()
        or str(getattr(manual,"sheba_number","") or "").strip()
        or str(getattr(manual,"account_number","") or "").strip()
    )
)
site=SiteSetting.objects.first()
gateway_ready,_=payment_gateway_status(site)
print("PAYMENT_READINESS_GATEWAY_READY="+str(bool(gateway_ready)))
print("PAYMENT_READINESS_MANUAL_EXISTS="+str(manual is not None))
print("PAYMENT_READINESS_MANUAL_CONFIGURED="+str(manual_configured))
print("PAYMENT_READINESS_MANUAL_ACTIVE="+str(bool(manual and manual.is_active and manual_configured)))

User=get_user_model()
operator=User.objects.filter(is_superuser=True,is_active=True).order_by("pk").first()
if operator is None:
    raise SystemExit("A2R_DEPLOY_FAIL=no_active_superuser_for_readonly_render_smoke")
request=RequestFactory().get("/admin/phase50-command-center/")
request.user=operator
response=phase50_admin_command_center(request)
response.render()
body=response.content.decode("utf-8","replace")
for marker in ('id="phase50-payment-readiness-title"', "Merchant credential", "Provider:"):
    if marker not in body:
        raise SystemExit("A2R_DEPLOY_FAIL=admin_readiness_marker_missing")
for forbidden in ("STORE_PAYMENT_CARD_NUMBER","STORE_PAYMENT_SHEBA_NUMBER","STORE_PAYMENT_ACCOUNT_NUMBER","ZARINPAL_MERCHANT_ID"):
    if forbidden in body:
        raise SystemExit("A2R_DEPLOY_FAIL=secret_identifier_rendered")
print("A2R_ADMIN_READONLY_RENDER_SMOKE=PASS")
PY

"$PY" manage.py phase50_a2l_seed_manual_payment | grep -Fq 'A2R_MANUAL_PAYMENT_DRY_RUN=PASS' || fail "manual_payment_dry_run_failed"

mkdir -p tmp
touch tmp/restart.txt
sleep 4

"$PY" - <<'PY'
from urllib import request
base="https://3dprinthub.ir"
headers={"User-Agent":"3DPrintHub-A2R/1.0","Cache-Control":"no-cache"}
for path in ("/","/store/"):
    with request.urlopen(request.Request(base+path,headers=headers),timeout=20) as r:
        print("PUBLIC_HTTP="+str(r.status)+" "+path)
        if r.status != 200:
            raise SystemExit("A2R_DEPLOY_FAIL=public_http_failed")
print("A2R_PUBLIC_SMOKE=PASS")
PY

printf 'FINAL_HEAD=%s\n' "$(git rev-parse HEAD)"
printf 'FINAL_WORKTREE=%s\n' "$(test -z "$(git status --porcelain --untracked-files=all)" && printf CLEAN || printf DIRTY)"
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"
printf 'PHASE50_A2R_PAYMENT_FINANCE_ADMIN_DEPLOY=PASS\n'
