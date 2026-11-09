#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
HOST_BRANCH="release/phase50-a2j-hero-20260915"
GITHUB_BRANCH="fix/website-order-finance-20261109"
EXPECTED_HEAD="0368448385d7e49ba8200c2695b349772c51f323"
DB_NAME="sfkilvrs_EmiAdmin_3dprinthub"
TARGET="${1:-}"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="/home/sfkilvrs/3dprinthub-deploy-backups/${STAMP}-finance-draft-html-hotfix"
DELTA="/tmp/3dprinthub-finance-hotfix-$$.txt"
trap 'rm -f "$DELTA" 2>/dev/null || true' EXIT
fail(){ printf 'ORDER_FINANCE_HOTFIX_FAIL=%s\nBACKUP=%s\n' "$1" "$BACKUP" >&2;exit 1; }
[ -n "$TARGET" ] || fail "target_missing"
[ -x "$PY" ] || fail "python_missing"
cd "$ROOT"
[ "$(git branch --show-current)" = "$HOST_BRANCH" ] || fail "wrong_branch"
[ "$(git rev-parse HEAD)" = "$EXPECTED_HEAD" ] || fail "unexpected_production_head"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "host_dirty"
case "$(git remote get-url origin)" in
  *farazha2203/3dprinthub.git|*farazha2203/3dprinthub) ;;
  *) fail "wrong_origin" ;;
esac

"$PY" - "$DB_NAME" <<'PYCODE'
import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from website.models import Order, Quote, Payment, PaymentLedgerEntry
if connection.vendor != "mysql" or connection.settings_dict.get("NAME") != sys.argv[1]:
    raise SystemExit("wrong_db")
executor = MigrationExecutor(connection)
if executor.migration_plan(executor.loader.graph.leaf_nodes()):
    raise SystemExit("pending_migrations")
if not executor.loader.applied_migrations.__contains__(("website", "0025_quote_pricing_snapshot")):
    raise SystemExit("snapshot_schema_migration_missing")
counts=(Order.objects.count(),Quote.objects.filter(status="draft").count(),
        Quote.objects.exclude(status="draft").count(),Payment.objects.count(),PaymentLedgerEntry.objects.count())
print("PREFLIGHT_ORDER_FINANCE_COUNTS="+str(counts))
if counts != (1,1,0,0,0):
    raise SystemExit("finance_state_changed")
PYCODE
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run

REMOTE_SHA="$(git ls-remote origin "refs/heads/$GITHUB_BRANCH" | awk '{print $1}')"
[ "$REMOTE_SHA" = "$TARGET" ] || fail "remote_branch_moved"
git fetch --no-tags origin "refs/heads/$GITHUB_BRANCH"
[ "$(git rev-parse FETCH_HEAD)" = "$TARGET" ] || fail "candidate_mismatch"
git merge-base --is-ancestor "$EXPECTED_HEAD" "$TARGET" || fail "not_fast_forward"
git diff --name-only "$EXPECTED_HEAD" "$TARGET" > "$DELTA"
printf 'HOTFIX_DELTA=\n';cat "$DELTA"
while IFS= read -r changed; do
  [ -n "$changed" ] || continue
  case "$changed" in
    docs/*|website/order_finance_admin.py|website/test_order_admin_finance.py|scripts/host/phase50_order_finance_draft_hotfix_deploy.sh) ;;
    *) fail "unauthorized_hotfix_file:$changed" ;;
  esac
done < "$DELTA"
grep -Fxq website/order_finance_admin.py "$DELTA" || fail "expected_runtime_fix_missing"
grep -Fxq scripts/host/phase50_order_finance_draft_hotfix_deploy.sh "$DELTA" || fail "hotfix_runner_not_versioned"
if grep -E '(^|/)migrations/|^config/|^requirements|^\.env' "$DELTA"; then
  fail "unapproved_schema_settings_delta"
fi
printf 'HOTFIX_ALLOWLIST=PASS\n'

mkdir -p "$BACKUP";chmod 700 "$BACKUP"
git archive --format=tar HEAD | gzip -1 > "$BACKUP/source-before.tar.gz"
tar -tzf "$BACKUP/source-before.tar.gz" >/dev/null
[ -f .env ] || fail "env_missing"
cp -p .env "$BACKUP/.env";chmod 600 "$BACKUP/.env"
printf '%s\n' "$EXPECTED_HEAD" > "$BACKUP/source-head.txt"
sha256sum "$BACKUP/source-before.tar.gz" > "$BACKUP/source-before.sha256"
sha256sum "$BACKUP/.env" > "$BACKUP/env.sha256"
(cd "$BACKUP" && sha256sum -c source-before.sha256 env.sha256) || fail "source_env_backup_bad"
export PHASE49_PROJECT_ROOT="$ROOT"
export PHASE49_BACKUP_ROOT="$BACKUP"
"$PY" scripts/host/phase49_3i53_mysql_backup.py "$DB_NAME" || fail "mysql_backup_failed"
[ -s "$BACKUP/database-before-3i53.sql.gz" ] || fail "mysql_backup_missing"
gzip -t "$BACKUP/database-before-3i53.sql.gz" || fail "mysql_backup_gzip_bad"
sha256sum "$BACKUP/database-before-3i53.sql.gz" > "$BACKUP/database-before.sha256"
(cd "$BACKUP" && sha256sum -c database-before.sha256) || fail "mysql_backup_sha_bad"
printf 'HOTFIX_FRESH_FULL_BACKUP=VERIFIED\n'

git merge --ff-only "$TARGET" || fail "ff_failed"
[ "$(git rev-parse HEAD)" = "$TARGET" ] || fail "target_mismatch"
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
"$PY" - "$DB_NAME" <<'PYCODE'
import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from django.contrib import admin
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from website.models import Order, Quote, Payment, PaymentLedgerEntry
assert connection.vendor == "mysql" and connection.settings_dict["NAME"] == sys.argv[1]
executor=MigrationExecutor(connection)
assert not executor.migration_plan(executor.loader.graph.leaf_nodes())
assert Quote.objects.filter(status="draft", pricing_snapshot_at__isnull=True).count() == 1
assert Payment.objects.count() == 0 and PaymentLedgerEntry.objects.count() == 0
panel=str(admin.site._registry[Order].finance_summary(Order.objects.get(pk=1)))
assert "قیمت هنوز تثبیت نشده است" in panel
assert "record-receipt/" not in panel
print("DRAFT_FINANCE_PANEL_RENDER=PASS")
print("FINANCE_LEDGER_UNCHANGED=PASS")
PYCODE
mkdir -p tmp;touch tmp/restart.txt;sleep 4
"$PY" - <<'PYCODE'
from urllib import request
for path in ("/", "/store/"):
    with request.urlopen(request.Request("https://3dprinthub.ir"+path,
        headers={"User-Agent":"3DPrintHub-Finance-Hotfix/1.0","Cache-Control":"no-cache"}),timeout=20) as response:
        if response.status!=200:raise SystemExit("public_smoke_failed:"+path)
        print("PUBLIC_HTTP=200 "+path)
PYCODE
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "dirty_after_hotfix"
[ "$(git rev-parse HEAD)" = "$TARGET" ] || fail "head_mismatch"
printf 'ORDER_FINANCE_DRAFT_HOTFIX=PASS\nTARGET=%s\nBACKUP=%s\n' "$TARGET" "$BACKUP"
