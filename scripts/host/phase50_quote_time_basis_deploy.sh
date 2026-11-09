#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

# Additive release of per-piece vs per-batch print-time semantics.
# Every external/business fact is checked before source or MySQL is changed.
ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
EXPECTED_DB="sfkilvrs_EmiAdmin_3dprinthub"
HOST_BRANCH="release/phase50-a2j-hero-20260915"
GITHUB_BRANCH="fix/website-quote-time-basis-20261109"
EXPECTED_HEAD="3b6a74a7659a82f8dae440795afc90ee20c25d99"
TARGET_SHA="${1:-}"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="/home/sfkilvrs/3dprinthub-deploy-backups/${STAMP}-quote-time-basis"
DELTA="/tmp/3dprinthub-time-basis-$$.txt"

cleanup(){ rm -f "$DELTA" 2>/dev/null || true; }
trap cleanup EXIT
fail(){ printf 'QUOTE_TIME_BASIS_DEPLOY_FAIL=%s\nBACKUP_ROOT=%s\n' "$1" "$BACKUP_ROOT" >&2;exit 1; }

[ -n "$TARGET_SHA" ] || fail "target_sha_required"
[ -d "$ROOT/.git" ] && [ -x "$PY" ] || fail "host_root_or_python_missing"
cd "$ROOT"
[ "$(git branch --show-current)" = "$HOST_BRANCH" ] || fail "wrong_host_branch"
[ "$(git rev-parse HEAD)" = "$EXPECTED_HEAD" ] || fail "host_changed"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "dirty_host_worktree"
case "$(git remote get-url origin)" in
  *farazha2203/3dprinthub.git|*farazha2203/3dprinthub) ;;
  *) fail "unexpected_repository" ;;
esac
printf 'QUOTE_TIME_BASIS_PREFLIGHT=START\n'

"$PY" - "$EXPECTED_DB" <<'PYCODE'
import os,sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
import django; django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from website.models import Order,Quote,Payment,PaymentLedgerEntry
if connection.vendor!="mysql" or connection.settings_dict.get("NAME")!=sys.argv[1]:
    raise SystemExit("database_identity_mismatch")
ex=MigrationExecutor(connection)
if ex.migration_plan(ex.loader.graph.leaf_nodes()):
    raise SystemExit("migration_plan_not_empty")
if ("website","0025_quote_pricing_snapshot") not in ex.loader.applied_migrations:
    raise SystemExit("finance_snapshot_migration_missing")
counts = (Order.objects.count(),Quote.objects.filter(status="draft").count(),
          Quote.objects.exclude(status="draft").count(),Payment.objects.count(),PaymentLedgerEntry.objects.count())
print("FINANCE_COUNTS="+str(counts))
if counts != (1,1,0,0,0):
    raise SystemExit("quote_finance_state_changed")
o=Order.objects.get(pk=1)
q=o.quote
values=(o.quantity,int(q.print_time_minutes),int(q.billable_print_minutes),
        int(q.material_cost),int(q.machine_cost),int(q.labor_fee),int(q.total_price))
print("QUOTE_TIME_INPUTS="+str(values))
if q.status!="draft" or q.pricing_snapshot_at is not None or values != (4,200,240,120000,640000,45000,805000):
    raise SystemExit("actual_quote_changed_since_pricing_audit")
print("QUOTE_PRICE_UNCHANGED_BEFORE_RELEASE=PASS")
PYCODE
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run

REMOTE_SHA="$(git ls-remote origin "refs/heads/$GITHUB_BRANCH" | awk '{print $1}')"
[ "$REMOTE_SHA" = "$TARGET_SHA" ] || fail "github_branch_head_changed"
git fetch --no-tags origin "refs/heads/$GITHUB_BRANCH"
[ "$(git rev-parse FETCH_HEAD)" = "$TARGET_SHA" ] || fail "fetched_sha_mismatch"
git merge-base --is-ancestor "$EXPECTED_HEAD" "$TARGET_SHA" || fail "not_descendant_of_production"
git diff --name-only "$EXPECTED_HEAD" "$TARGET_SHA" > "$DELTA"
printf 'CHANGED_FILES=\n';cat "$DELTA"
while IFS= read -r changed; do
  [ -n "$changed" ] || continue
  case "$changed" in
    docs/*|website/models.py|website/admin.py|website/quote_pricing_policy.py|website/migrations/0026_quote_print_time_scope.py|website/test_quote_time_basis.py|templates/website/quote_detail.html|scripts/host/phase50_quote_time_basis_deploy.sh)
      ;;
    *) fail "unexpected_file:$changed" ;;
  esac
done < "$DELTA"
for required in website/models.py website/admin.py website/quote_pricing_policy.py website/migrations/0026_quote_print_time_scope.py website/test_quote_time_basis.py templates/website/quote_detail.html scripts/host/phase50_quote_time_basis_deploy.sh; do
  grep -Fxq "$required" "$DELTA" || fail "missing_required_change:$required"
done
printf 'SOURCE_DELTA_ALLOWLIST=PASS\n'

# Full verified rollback before fast-forward or the additive migration.
mkdir -p "$BACKUP_ROOT";chmod 700 "$BACKUP_ROOT"
git archive --format=tar HEAD | gzip -1 > "$BACKUP_ROOT/source-before.tar.gz"
tar -tzf "$BACKUP_ROOT/source-before.tar.gz" > /dev/null
[ -f .env ] || fail "env_missing"
cp -p .env "$BACKUP_ROOT/.env";chmod 600 "$BACKUP_ROOT/.env"
printf '%s\n' "$EXPECTED_HEAD" > "$BACKUP_ROOT/source-head.txt"
printf '%s\n' "$HOST_BRANCH" > "$BACKUP_ROOT/source-branch.txt"
sha256sum "$BACKUP_ROOT/source-before.tar.gz" > "$BACKUP_ROOT/source-before.sha256"
sha256sum "$BACKUP_ROOT/.env" > "$BACKUP_ROOT/env.sha256"
(cd "$BACKUP_ROOT" && sha256sum -c source-before.sha256 env.sha256) || fail "source_env_checksum_failed"
export PHASE49_PROJECT_ROOT="$ROOT"
export PHASE49_BACKUP_ROOT="$BACKUP_ROOT"
"$PY" scripts/host/phase49_3i53_mysql_backup.py "$EXPECTED_DB" || fail "mysql_full_backup_failed"
[ -s "$BACKUP_ROOT/database-before-3i53.sql.gz" ] || fail "database_dump_missing"
gzip -t "$BACKUP_ROOT/database-before-3i53.sql.gz" || fail "database_gzip_invalid"
sha256sum "$BACKUP_ROOT/database-before-3i53.sql.gz" > "$BACKUP_ROOT/database-before.sha256"
(cd "$BACKUP_ROOT" && sha256sum -c database-before.sha256) || fail "database_checksum_invalid"
printf 'QUOTE_TIME_BASIS_FULL_ROLLBACK=VERIFIED\nBACKUP_ROOT=%s\n' "$BACKUP_ROOT"

git merge --ff-only "$TARGET_SHA" || fail "fast_forward_failed"
[ "$(git rev-parse HEAD)" = "$TARGET_SHA" ] || fail "target_sha_mismatch_after_merge"
"$PY" - "$EXPECTED_DB" <<'PYCODE'
import os,sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
import django;django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
if connection.vendor!="mysql" or connection.settings_dict.get("NAME")!=sys.argv[1]:
    raise SystemExit("postmerge_wrong_database")
ex=MigrationExecutor(connection)
plan=[(node.app_label,node.name,backward) for node,backward in ex.migration_plan(ex.loader.graph.leaf_nodes())]
print("PENDING_MIGRATIONS="+str(plan))
if plan != [("website","0026_quote_print_time_scope",False)]:
    raise SystemExit("unexpected_migration_plan")
PYCODE
"$PY" manage.py migrate website 0026_quote_print_time_scope --noinput || fail "website_0026_migrate_failed"
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run

# Read-only Django Admin GET and in-memory what-if; never save a production Quote.
"$PY" - "$EXPECTED_DB" <<'PYCODE'
import os,sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
import django;django.setup()
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from website.models import Order,Quote,Payment,PaymentLedgerEntry
if connection.vendor!="mysql" or connection.settings_dict.get("NAME")!=sys.argv[1]:
    raise SystemExit("post_migrate_database_changed")
ex=MigrationExecutor(connection)
if ex.migration_plan(ex.loader.graph.leaf_nodes()):
    raise SystemExit("pending_migrations_remain")
order=Order.objects.get(pk=1)
quote=order.quote
assert quote.status=="draft" and quote.pricing_snapshot_at is None
assert quote.print_time_scope=="per_piece"
assert quote.total_billable_machine_minutes==960 and quote.machine_cost==640000
assert quote.total_price==805000
quote.print_time_scope="batch" # in-memory only; no save!
assert quote.total_billable_machine_minutes==240
assert quote.machine_cost==160000 and quote.total_price==325000
quote.refresh_from_db()
assert quote.print_time_scope=="per_piece" and quote.total_price==805000
assert Payment.objects.count()==0 and PaymentLedgerEntry.objects.count()==0
req=RequestFactory().get("/admin/website/order/1/change/",HTTP_HOST="3dprinthub.ir")
req.user=User(pk=9999999,username="audit-only",is_staff=True,is_active=True,is_superuser=True)
req.session={};req._messages=FallbackStorage(req)
req.current_app=admin.site.name
response=admin.site._registry[Order].change_view(req,"1")
response.render()
body=response.content.decode("utf-8")
assert response.status_code==200 and "order-finance-summary" in body
assert "record-receipt/" not in body
assert "print_time_scope" in body
print("ORDER_1_PER_PIECE_PRICE_PRESERVED=PASS")
print("BATCH_WHAT_IF_NO_SAVE=PASS")
print("ORDER_1_ADMIN_GET=200")
print("FINANCE_LEDGER_UNCHANGED=PASS")
PYCODE

mkdir -p tmp;touch tmp/restart.txt;sleep 4
"$PY" - <<'PYCODE'
from urllib import request
for path in ("/","/store/"):
    with request.urlopen(request.Request("https://3dprinthub.ir"+path,
        headers={"User-Agent":"3DPrintHub-TimeBasis/1.0","Cache-Control":"no-cache"}),timeout=20) as response:
        if response.status != 200:
            raise SystemExit("public_http_failed:"+path)
        print("PUBLIC_HTTP=200 "+path)
PYCODE
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "dirty_after_deploy"
[ "$(git rev-parse HEAD)" = "$TARGET_SHA" ] || fail "final_head_mismatch"
printf 'QUOTE_TIME_BASIS_DEPLOY=PASS\nTARGET_SHA=%s\nBACKUP_ROOT=%s\n' "$TARGET_SHA" "$BACKUP_ROOT"
