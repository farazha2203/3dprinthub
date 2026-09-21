#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
EXPECTED_DB="sfkilvrs_EmiAdmin_3dprinthub"
HOST_BRANCH="release/phase50-a2j-hero-20260915"
TARGET_BRANCH="wip/phase50-a2s-social-finance-20260920"
EXPECTED_BASELINE="888af6b4551b2e6b1e5681aab4c3d9610735474a"
TARGET_SHA="${1:-}"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="/home/sfkilvrs/3dprinthub-deploy-backups/${STAMP}-phase50-a2s-finance-receipt"
TMP_DELTA="/tmp/3dprinthub-a2s-finance-delta-$$.txt"

cleanup(){ rm -f "$TMP_DELTA" 2>/dev/null || true; }
trap cleanup EXIT
fail(){
  printf 'A2S_FINANCE_DEPLOY_FAIL=%s\n' "$1" >&2
  printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT" >&2
  exit 1
}

[ -n "$TARGET_SHA" ] || fail "target_sha_required"
cd "$ROOT"
[ -d .git ] || fail "project_git_missing"
[ "$(git branch --show-current)" = "$HOST_BRANCH" ] || fail "wrong_host_branch"
[ "$(git rev-parse HEAD)" = "$EXPECTED_BASELINE" ] || fail "host_baseline_changed"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "production_worktree_dirty"
case "$(git remote get-url origin)" in
  *farazha2203/3dprinthub.git|*farazha2203/3dprinthub) ;;
  *) fail "wrong_repository" ;;
esac

"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
"$PY" - "$EXPECTED_DB" <<'PY'
import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from catalog_bridge.publish_readiness import publish_readiness
from store.phase50_commerce_policy import StorePaymentSettings

expected = sys.argv[1]
print("DB_VENDOR=" + str(connection.vendor))
print("DB_NAME=" + str(connection.settings_dict.get("NAME") or ""))
if connection.vendor != "mysql" or str(connection.settings_dict.get("NAME") or "") != expected:
    raise SystemExit("A2S_FINANCE_DEPLOY_FAIL=database_identity_mismatch")
executor = MigrationExecutor(connection)
plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
print("MIGRATION_PLAN_COUNT=" + str(len(plan)))
if plan:
    raise SystemExit("A2S_FINANCE_DEPLOY_FAIL=migration_plan_not_empty")
ready = publish_readiness()
print("PUBLISH_READY=" + str(bool(ready.get("ready"))))
if ready.get("ready") is not True:
    raise SystemExit("A2S_FINANCE_DEPLOY_FAIL=receiver_not_ready")
manual = StorePaymentSettings.objects.order_by("pk").first()
configured = bool(
    manual
    and str(getattr(manual, "account_holder", "") or "").strip()
    and (
        str(getattr(manual, "card_number", "") or "").strip()
        or str(getattr(manual, "sheba_number", "") or "").strip()
        or str(getattr(manual, "account_number", "") or "").strip()
    )
)
print("MANUAL_PAYMENT_EXISTS=" + str(manual is not None))
print("MANUAL_PAYMENT_CONFIGURED=" + str(configured))
print("MANUAL_PAYMENT_ACTIVE=" + str(bool(manual and manual.is_active and configured)))
if not (manual and manual.is_active and configured):
    raise SystemExit("A2S_FINANCE_DEPLOY_FAIL=manual_payment_not_ready")
PY
"$PY" manage.py phase30_payment_audit

REMOTE_SHA="$(git ls-remote origin "refs/heads/$TARGET_BRANCH" | awk '{print $1}')"
printf 'REMOTE_SHA=%s\n' "$REMOTE_SHA"
[ "$REMOTE_SHA" = "$TARGET_SHA" ] || fail "target_not_live_github_head"
git fetch --no-tags origin "refs/heads/$TARGET_BRANCH"
FETCHED="$(git rev-parse FETCH_HEAD)"
[ "$FETCHED" = "$TARGET_SHA" ] || fail "fetched_target_mismatch"
git merge-base --is-ancestor "$EXPECTED_BASELINE" "$FETCHED" || fail "target_not_fast_forward"
git diff --name-only "$EXPECTED_BASELINE" "$FETCHED" > "$TMP_DELTA"
printf '%s\n' "===== A2S FINANCE DELTA ====="
cat "$TMP_DELTA"

if grep -Eq '(^|/)migrations/[0-9]{4}_[^/]+\.py$|^requirements[^/]*\.txt$|^config/settings|(^|/)\.env$' "$TMP_DELTA"; then
  fail "migration_dependency_settings_or_env_delta_detected"
fi

while IFS= read -r changed; do
  case "$changed" in
    catalog_center/app/buffer_media_host.py|    catalog_center/app/buffer_publish.py|    catalog_center/app/instagram_feed_asset.py|    catalog_center/app/instagram_publish.py|    catalog_center/app/instagram_story_asset.py|    catalog_center/app/secure_secrets.py|    catalog_center/app/social_content_policy.py|    catalog_center/config/instagram_brand_style.json|    catalog_center/qt6/kernel.py|    catalog_center/qt6/settings_page.py|    catalog_center/tests/test_phase50_buffer_media_host.py|    catalog_center/tests/test_phase50_buffer_publish.py|    catalog_center/tests/test_phase50_buffer_story_companion.py|    catalog_center/tests/test_phase50_instagram_feed_asset.py|    catalog_center/tests/test_phase50_instagram_publish.py|    catalog_center/tests/test_phase50_instagram_social_policy.py|    catalog_center/tests/test_phase50_instagram_story_asset.py|    docs/CHANGELOG.md|docs/CURRENT_STATE.md|docs/ERRORS.md|docs/REQUESTS.md|docs/ROADMAP.md|    docs/phases/PHASE50_A2R_PAYMENT_FINANCE_ADMIN_CLOSURE.md|    docs/phases/PHASE50_A2S_SOCIAL_FINANCE_RECONCILIATION.md|    scripts/social/render_instagram_story.py|    scripts/host/phase50_a2s_finance_receipt_deploy.sh|    store/admin.py|store/finance_reconciliation.py|    store/management/commands/phase50_finance_reconciliation.py|    store/models.py|store/test_phase50_a2s_finance_reconciliation.py|website/admin.py)
      ;;
    *)
      fail "unexpected_target_delta:$changed"
      ;;
  esac
done < "$TMP_DELTA"

for required in   store/admin.py   store/models.py   website/admin.py   store/finance_reconciliation.py   store/management/commands/phase50_finance_reconciliation.py   store/test_phase50_a2s_finance_reconciliation.py   scripts/host/phase50_a2s_finance_receipt_deploy.sh
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
if [ -f "$BACKUP_ROOT/.env" ]; then
  sha256sum "$BACKUP_ROOT/.env" > "$BACKUP_ROOT/env.sha256"
fi
(
  cd "$BACKUP_ROOT"
  sha256sum -c source-bundle.sha256
  if [ -f env.sha256 ]; then sha256sum -c env.sha256; fi
)

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

"$PY" -m py_compile   store/finance_reconciliation.py   store/management/commands/phase50_finance_reconciliation.py   store/models.py   store/admin.py   website/admin.py
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
"$PY" manage.py phase30_payment_audit
"$PY" manage.py phase50_finance_reconciliation

"$PY" - <<'PY'
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from store.models import ProductionJob, StoreOrder, StorePayment
from store.phase50_commerce_policy import StorePaymentSettings
from website.models import Payment, PaymentLedgerEntry

plan = MigrationExecutor(connection).migration_plan(
    MigrationExecutor(connection).loader.graph.leaf_nodes()
)
if plan:
    raise SystemExit("A2S_FINANCE_DEPLOY_FAIL=post_merge_migration_plan_not_empty")
manual = StorePaymentSettings.objects.order_by("pk").first()
configured = bool(
    manual
    and str(getattr(manual, "account_holder", "") or "").strip()
    and (
        str(getattr(manual, "card_number", "") or "").strip()
        or str(getattr(manual, "sheba_number", "") or "").strip()
        or str(getattr(manual, "account_number", "") or "").strip()
    )
)
print("POST_MANUAL_READY=" + str(bool(manual and manual.is_active and configured)))
print("STORE_PAYMENT_COUNT=" + str(StorePayment.objects.count()))
print("STORE_PAID_ORDER_COUNT=" + str(StoreOrder.objects.filter(payment_status="paid").count()))
print("WEBSITE_PAYMENT_COUNT=" + str(Payment.objects.count()))
print("WEBSITE_LEDGER_COUNT=" + str(PaymentLedgerEntry.objects.count()))
print("PRODUCTION_JOB_COUNT=" + str(ProductionJob.objects.count()))
PY

mkdir -p tmp
touch tmp/restart.txt
sleep 4

"$PY" - <<'PY'
from urllib import request
base = "https://3dprinthub.ir"
headers = {"User-Agent": "3DPrintHub-A2S-Finance/1.0", "Cache-Control": "no-cache"}
for path in ("/", "/store/"):
    with request.urlopen(request.Request(base + path, headers=headers), timeout=20) as response:
        print("PUBLIC_HTTP=" + str(response.status) + " " + path)
        if response.status != 200:
            raise SystemExit("A2S_FINANCE_DEPLOY_FAIL=public_http_failed")
print("A2S_PUBLIC_SMOKE=PASS")
PY

printf 'FINAL_HEAD=%s\n' "$(git rev-parse HEAD)"
printf 'FINAL_WORKTREE=%s\n' "$(test -z "$(git status --porcelain --untracked-files=all)" && printf CLEAN || printf DIRTY)"
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"
printf 'PHASE50_A2S_FINANCE_RECEIPT_DEPLOY=PASS\n'
