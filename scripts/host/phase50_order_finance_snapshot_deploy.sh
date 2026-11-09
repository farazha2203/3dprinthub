#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

# Controlled, single-use financial migration. Never use on a different project.
ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
EXPECTED_DB="sfkilvrs_EmiAdmin_3dprinthub"
HOST_BRANCH="release/phase50-a2j-hero-20260915"
GITHUB_BRANCH="fix/website-order-finance-20261109"
EXPECTED_BASELINE="29495708ac58c13fe600d998c7c23c0fcc4d8b80"
TARGET_SHA="${1:-}"
BACKUP_BASE="/home/sfkilvrs/3dprinthub-deploy-backups"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="$BACKUP_BASE/${STAMP}-order-finance-pricing-snapshot"
TMP_DELTA="/tmp/3dprinthub-order-finance-delta-$$.txt"

cleanup() { rm -f "$TMP_DELTA" 2>/dev/null || true; }
trap cleanup EXIT
fail() {
  printf 'ORDER_FINANCE_DEPLOY_FAIL=%s\nBACKUP_ROOT=%s\n' "$1" "$BACKUP_ROOT" >&2
  exit 1
}

[ -n "$TARGET_SHA" ] || fail "target_sha_required"
[ -x "$PY" ] || fail "production_python_missing"
[ -d "$ROOT/.git" ] || fail "project_root_missing"
cd "$ROOT"

[ "$(git branch --show-current)" = "$HOST_BRANCH" ] || fail "host_branch_changed"
[ "$(git rev-parse HEAD)" = "$EXPECTED_BASELINE" ] || fail "host_baseline_changed"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "worktree_dirty"
case "$(git remote get-url origin)" in
  *farazha2203/3dprinthub.git|*farazha2203/3dprinthub) ;;
  *) fail "wrong_git_origin" ;;
esac

printf 'PHASE50_ORDER_FINANCE_PREFLIGHT=START\n'
"$PY" - "$EXPECTED_DB" <<'PYCODE'
import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from website.models import Order, Quote, Payment, PaymentLedgerEntry
assert connection.vendor == "mysql", "unexpected_db_vendor"
assert connection.settings_dict.get("NAME") == sys.argv[1], "unexpected_database"
executor = MigrationExecutor(connection)
plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
if plan:
    raise SystemExit("preexisting_migration_plan_not_empty")
counts = {
    "orders": Order.objects.count(),
    "draft_quotes": Quote.objects.filter(status="draft").count(),
    "final_quotes": Quote.objects.exclude(status="draft").count(),
    "payments": Payment.objects.count(),
    "ledger": PaymentLedgerEntry.objects.count(),
}
print("FINANCE_COUNTS=" + ",".join(f"{k}:{v}" for k, v in counts.items()))
if not Order.objects.filter(pk=1).exists():
    raise SystemExit("requested_order_missing")
# Fail closed if financial data changes after the owner's authorized read-only audit.
if counts != {"orders": 1, "draft_quotes": 1, "final_quotes": 0, "payments": 0, "ledger": 0}:
    raise SystemExit("financial_state_changed_since_preflight")
print("FINANCE_PREDEPLOY_DB_IDENTITY=PASS")
PYCODE
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run

REMOTE_SHA="$(git ls-remote origin "refs/heads/$GITHUB_BRANCH" | awk '{print $1}')"
[ "$REMOTE_SHA" = "$TARGET_SHA" ] || fail "github_branch_sha_changed"
git fetch --no-tags origin "refs/heads/$GITHUB_BRANCH"
FETCHED="$(git rev-parse FETCH_HEAD)"
[ "$FETCHED" = "$TARGET_SHA" ] || fail "fetched_target_mismatch"
git merge-base --is-ancestor "$EXPECTED_BASELINE" "$FETCHED" || fail "candidate_not_fast_forward_from_host"
git diff --name-only "$EXPECTED_BASELINE" "$FETCHED" > "$TMP_DELTA"
printf 'FINANCE_DELTA=\n'; cat "$TMP_DELTA"
while IFS= read -r changed; do
  [ -n "$changed" ] || continue
  case "$changed" in
    docs/*|website/admin.py|website/models.py|website/payment_services.py|website/order_finance_admin.py|website/quote_pricing_policy.py|website/test_order_admin_finance.py|website/test_quote_price_snapshot.py|website/migrations/0025_quote_pricing_snapshot.py|templates/admin/website/order/change_form.html|templates/admin/website/order/record_receipt.html|scripts/host/phase50_order_finance_snapshot_deploy.sh)
      ;;
    *) fail "unexpected_target_delta:$changed" ;;
  esac
done < "$TMP_DELTA"
for required in website/admin.py website/models.py website/payment_services.py website/quote_pricing_policy.py website/order_finance_admin.py website/migrations/0025_quote_pricing_snapshot.py scripts/host/phase50_order_finance_snapshot_deploy.sh; do
  grep -Fxq "$required" "$TMP_DELTA" || fail "required_delta_missing:$required"
done
printf 'TARGET_DELTA_ALLOWLIST=PASS\n'

# Never promote changed source before a verified source+env+full-DB rollback.
mkdir -p "$BACKUP_ROOT"
chmod 700 "$BACKUP_ROOT"
git archive --format=tar HEAD | gzip -1 > "$BACKUP_ROOT/source-before.tar.gz"
tar -tzf "$BACKUP_ROOT/source-before.tar.gz" >/dev/null
printf '%s\n' "$EXPECTED_BASELINE" > "$BACKUP_ROOT/source-head.txt"
printf '%s\n' "$HOST_BRANCH" > "$BACKUP_ROOT/source-branch.txt"
[ -f .env ] || fail "env_missing"
cp -p .env "$BACKUP_ROOT/.env"
chmod 600 "$BACKUP_ROOT/.env"
sha256sum "$BACKUP_ROOT/source-before.tar.gz" > "$BACKUP_ROOT/source-before.sha256"
sha256sum "$BACKUP_ROOT/.env" > "$BACKUP_ROOT/env.sha256"
(cd "$BACKUP_ROOT" && sha256sum -c source-before.sha256 env.sha256) || fail "source_or_env_backup_checksum_invalid"

export PHASE49_PROJECT_ROOT="$ROOT"
export PHASE49_BACKUP_ROOT="$BACKUP_ROOT"
"$PY" scripts/host/phase49_3i53_mysql_backup.py "$EXPECTED_DB" || fail "mysql_dump_failed"
[ -s "$BACKUP_ROOT/database-before-3i53.sql.gz" ] || fail "mysql_dump_missing"
gzip -t "$BACKUP_ROOT/database-before-3i53.sql.gz" || fail "mysql_gzip_corrupt"
sha256sum "$BACKUP_ROOT/database-before-3i53.sql.gz" > "$BACKUP_ROOT/database-before.sha256"
(cd "$BACKUP_ROOT" && sha256sum -c database-before.sha256) || fail "mysql_backup_sha_invalid"
printf 'FINANCE_FULL_BACKUP=VERIFIED\nBACKUP_ROOT=%s\n' "$BACKUP_ROOT"

git merge --ff-only "$FETCHED" || fail "git_fast_forward_failed"
[ "$(git rev-parse HEAD)" = "$TARGET_SHA" ] || fail "promoted_head_mismatch"
"$PY" - "$EXPECTED_DB" <<'PYCODE'
import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
assert connection.vendor == "mysql" and connection.settings_dict["NAME"] == sys.argv[1]
executor = MigrationExecutor(connection)
pending = executor.migration_plan(executor.loader.graph.leaf_nodes())
names = [(node.app_label, node.name, backward) for node, backward in pending]
print("EXPECTED_POSTPROMOTION_MIGRATIONS=" + str(names))
if names != [("website", "0025_quote_pricing_snapshot", False)]:
    raise SystemExit("unapproved_migration_plan")
PYCODE

"$PY" manage.py migrate website 0025_quote_pricing_snapshot --noinput || fail "migration_failed"
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
"$PY" - "$EXPECTED_DB" <<'PYCODE'
import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from django.contrib import admin
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from website.models import Order, Quote, Payment, PaymentLedgerEntry
assert connection.vendor == "mysql" and connection.settings_dict["NAME"] == sys.argv[1]
executor = MigrationExecutor(connection)
if executor.migration_plan(executor.loader.graph.leaf_nodes()):
    raise SystemExit("postdeploy_migration_plan_not_empty")
assert Order.objects.count() == 1
assert Quote.objects.filter(status="draft", pricing_snapshot_at__isnull=True).count() == 1
assert Payment.objects.count() == 0
assert PaymentLedgerEntry.objects.count() == 0
order = Order.objects.get(pk=1)
panel = str(admin.site._registry[Order].finance_summary(order))
assert "قیمت هنوز تثبیت نشده است" in panel, "draft_quote_ui_wrong"
assert "record-receipt/" not in panel, "unfinalized_receipt_action_exposed"
print("FINANCE_PRICING_DRAFT_AND_ADMIN_PANEL=PASS")
print("FINANCE_NO_PRODUCTION_PAYMENT_MUTATIONS=PASS")
PYCODE

mkdir -p tmp; touch tmp/restart.txt
sleep 4
"$PY" - <<'PYCODE'
from urllib import request
for path in ("/", "/store/"):
    with request.urlopen(request.Request(
        "https://3dprinthub.ir" + path,
        headers={"User-Agent": "3DPrintHub-Finance-Deploy/1.0", "Cache-Control": "no-cache"},
    ), timeout=20) as response:
        if response.status != 200:
            raise SystemExit("public_http_failed:" + path)
        print("PUBLIC_HTTP=200 " + path)
PYCODE
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "worktree_dirty_after_deploy"
[ "$(git rev-parse HEAD)" = "$TARGET_SHA" ] || fail "final_head_changed"
printf 'ORDER_FINANCE_DEPLOY=PASS\nTARGET_SHA=%s\nBACKUP_ROOT=%s\n' "$TARGET_SHA" "$BACKUP_ROOT"
