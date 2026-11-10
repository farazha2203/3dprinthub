#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

# Single-use, fail-closed production release of Website service-order lifecycle.
ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
DB="sfkilvrs_EmiAdmin_3dprinthub"
BRANCH="release/phase50-a2j-hero-20260915"
GITHUB_BRANCH="fix/website-service-order-cycle-20261110"
BASE="df1be38355da6f3fa16ce5f480e5da81b5ae239a"
TARGET="${1:-}"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="/home/sfkilvrs/3dprinthub-deploy-backups/${STAMP}-service-order-cycle"
DELTA="/tmp/3dprinthub-service-order-cycle-$$.txt"

trap 'rm -f "$DELTA" 2>/dev/null || true' EXIT
fail(){ printf 'SERVICE_ORDER_CYCLE_DEPLOY_FAIL=%s\nBACKUP=%s\n' "$1" "$BACKUP" >&2;exit 1; }
[ -n "$TARGET" ] || fail "target_sha_required"
[ -d "$ROOT/.git" ] && [ -x "$PY" ] || fail "project_or_python_missing"
cd "$ROOT"
[ "$(git branch --show-current)" = "$BRANCH" ] || fail "unexpected_host_branch"
[ "$(git rev-parse HEAD)" = "$BASE" ] || fail "host_runtime_changed"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "production_worktree_dirty"
case "$(git remote get-url origin)" in *farazha2203/3dprinthub.git|*farazha2203/3dprinthub) ;; *) fail "repository_origin_mismatch";; esac
printf 'SERVICE_ORDER_PREFLIGHT=START\n'

"$PY" - "$DB" <<'PYCODE'
import os,sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
import django;django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from website.models import Order,Quote,Payment,PaymentLedgerEntry
if connection.vendor!="mysql" or connection.settings_dict.get("NAME")!=sys.argv[1]:
    raise SystemExit("unexpected_database")
ex=MigrationExecutor(connection)
if ex.migration_plan(ex.loader.graph.leaf_nodes()):
    raise SystemExit("existing_pending_migrations")
if ("website","0026_quote_print_time_scope") not in ex.loader.applied_migrations:
    raise SystemExit("time_basis_migration_missing")
counts=(Order.objects.count(),Quote.objects.count(),Payment.objects.count(),PaymentLedgerEntry.objects.count())
if counts != (1,1,0,0):raise SystemExit("real_finance_counts_changed:"+str(counts))
o=Order.objects.get(pk=1);q=o.quote
print("REAL_FINANCE_COUNTS="+str(counts))
print("ORDER1_FINANCE="+str((q.status,q.print_time_scope,q.total_price,o.quantity,q.paid_amount,q.discount)))
if (q.status,q.print_time_scope,q.total_price,o.quantity,q.paid_amount,q.discount)!=( "draft","per_piece",805000,4,0,0):
    raise SystemExit("order_1_financial_basis_changed")
print("PREDEPLOY_MYSQL_AND_ORDER=PASS")
PYCODE
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run

REMOTE_SHA="$(git ls-remote origin "refs/heads/$GITHUB_BRANCH" | awk '{print $1}')"
[ "$REMOTE_SHA" = "$TARGET" ] || fail "remote_git_head_moved"
git fetch --no-tags origin "refs/heads/$GITHUB_BRANCH"
[ "$(git rev-parse FETCH_HEAD)" = "$TARGET" ] || fail "candidate_sha_mismatch"
git merge-base --is-ancestor "$BASE" "$TARGET" || fail "candidate_not_descendant"
git diff --name-only "$BASE" "$TARGET" > "$DELTA"
printf 'SOURCE_DELTA=\n';cat "$DELTA"
while IFS= read -r changed; do
  [ -n "$changed" ] || continue
  case "$changed" in
    docs/*|templates/admin/website/order/change_form.html|templates/admin/website/order/record_delivery.html|templates/website/quote_detail.html|website/admin.py|website/forms.py|website/models.py|website/order_finance_admin.py|website/quote_catalog_offer.py|website/quote_pricing_policy.py|website/service_delivery_admin.py|website/views.py|website/test_order_admin_finance.py|website/test_service_order_cycle.py|website/migrations/0027_service_order_payment_delivery_catalog_offer.py|scripts/host/phase50_service_order_cycle_deploy.sh)
      ;;
    *) fail "unexpected_changed_file:$changed" ;;
  esac
done < "$DELTA"
for required in website/models.py website/admin.py website/order_finance_admin.py website/quote_catalog_offer.py website/service_delivery_admin.py website/migrations/0027_service_order_payment_delivery_catalog_offer.py website/test_service_order_cycle.py scripts/host/phase50_service_order_cycle_deploy.sh; do
  grep -Fxq "$required" "$DELTA" || fail "missing_required_delta:$required"
done
if grep -E '^website/migrations/' "$DELTA" | grep -v -Fx 'website/migrations/0027_service_order_payment_delivery_catalog_offer.py'; then
  fail "extra_schema_migration_delta"
fi
printf 'DELTA_ALLOWLIST=PASS\n'

mkdir -p "$BACKUP";chmod 700 "$BACKUP"
git archive --format=tar HEAD | gzip -1 > "$BACKUP/source-before.tar.gz"
tar -tzf "$BACKUP/source-before.tar.gz" >/dev/null || fail "source_archive_invalid"
[ -f .env ] || fail "production_env_missing"
cp -p .env "$BACKUP/.env";chmod 600 "$BACKUP/.env"
printf '%s\n' "$BASE" > "$BACKUP/source-head.txt"
printf '%s\n' "$BRANCH" > "$BACKUP/source-branch.txt"
sha256sum "$BACKUP/source-before.tar.gz" > "$BACKUP/source-before.sha256"
sha256sum "$BACKUP/.env" > "$BACKUP/env.sha256"
(cd "$BACKUP" && sha256sum -c source-before.sha256 env.sha256) || fail "source_env_checksum_failed"
export PHASE49_PROJECT_ROOT="$ROOT" PHASE49_BACKUP_ROOT="$BACKUP"
"$PY" scripts/host/phase49_3i53_mysql_backup.py "$DB" || fail "mysql_backup_failed"
[ -s "$BACKUP/database-before-3i53.sql.gz" ] || fail "mysql_backup_missing"
gzip -t "$BACKUP/database-before-3i53.sql.gz" || fail "mysql_backup_gzip_corrupt"
sha256sum "$BACKUP/database-before-3i53.sql.gz" > "$BACKUP/database-before.sha256"
(cd "$BACKUP" && sha256sum -c database-before.sha256) || fail "mysql_backup_sha_mismatch"
printf 'FULL_SOURCE_ENV_MYSQL_BACKUP=VERIFIED\nBACKUP=%s\n' "$BACKUP"

git merge --ff-only "$TARGET" || fail "fast_forward_failed"
[ "$(git rev-parse HEAD)" = "$TARGET" ] || fail "deployed_sha_mismatch"
"$PY" - "$DB" <<'PYCODE'
import os,sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
import django;django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
if connection.vendor!="mysql" or connection.settings_dict.get("NAME")!=sys.argv[1]:
    raise SystemExit("postmerge_database_identity")
ex=MigrationExecutor(connection)
plan=[(node.app_label,node.name,backward) for node,backward in ex.migration_plan(ex.loader.graph.leaf_nodes())]
print("POSTMERGE_MIGRATION_PLAN="+str(plan))
if plan != [("website","0027_service_order_payment_delivery_catalog_offer",False)]:
    raise SystemExit("unexpected_migration_plan")
PYCODE
"$PY" manage.py migrate website 0027_service_order_payment_delivery_catalog_offer --noinput || fail "website_0027_migration_failed"
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run

# Read-only live acceptance: do not create fake cash, discounts, shipments, or receipts.
"$PY" - "$DB" <<'PYCODE'
import os,sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
import django;django.setup()
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import RequestFactory
from store.models import ShippingMethod
from website.models import Order,Quote,Payment,PaymentLedgerEntry,ServiceOrderDelivery
from website.quote_catalog_offer import available_filament_offers
if connection.vendor!="mysql" or connection.settings_dict.get("NAME")!=sys.argv[1]:raise SystemExit("wrong_database")
ex=MigrationExecutor(connection)
if ex.migration_plan(ex.loader.graph.leaf_nodes()):raise SystemExit("postmigrate_plan_not_empty")
o=Order.objects.get(pk=1);q=o.quote
assert q.status=="draft" and q.filament_offer_id is None
assert q.print_time_scope=="per_piece" and q.total_price==805000
assert q.discount==0 and q.paid_amount==0 and q.pending_amount==0
assert Payment.objects.count()==0 and PaymentLedgerEntry.objects.count()==0
assert ServiceOrderDelivery.objects.count()==0
assert all(name in dict(Payment.METHOD_CHOICES) for name in ("cash","pos","bank_transfer","gateway"))
offers=available_filament_offers().count()
shipping=ShippingMethod.objects.filter(is_active=True).count()
print("AVAILABLE_CATALOG_OFFERS="+str(offers))
print("ACTIVE_SHIPPING_METHODS="+str(shipping))
assert offers>=1 and shipping>=3
req=RequestFactory().get("/admin/website/order/1/change/",HTTP_HOST="3dprinthub.ir")
req.user=User(pk=9999999,username="readonly-service-audit",is_staff=True,is_active=True,is_superuser=True)
req.session={};req._messages=FallbackStorage(req);req.current_app=admin.site.name
response=admin.site._registry[Order].change_view(req,"1")
response.render()
body=response.content.decode("utf-8")
print("ADMIN_ORDER1_GET="+str(response.status_code))
assert response.status_code==200 and "order-finance-summary" in body
assert "record-delivery/" in body and "filament_offer" in body
assert "record-receipt/" not in body
print("FINANCIAL_BALANCE_UNCHANGED=PASS")
print("SERVICE_ORDER_ADMIN_AND_CATALOG=PASS")
PYCODE

mkdir -p tmp;touch tmp/restart.txt;sleep 4
"$PY" - <<'PYCODE'
from urllib import request
for path in ("/","/store/","/admin/login/"):
    with request.urlopen(request.Request("https://3dprinthub.ir"+path,
        headers={"User-Agent":"3DPrintHub-ServiceOrderRelease/1.0","Cache-Control":"no-cache"}),timeout=20) as response:
        if response.status!=200:raise SystemExit("public_http_failed:"+path)
        print("PUBLIC_HTTP=200 "+path)
PYCODE
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "final_production_worktree_dirty"
[ "$(git rev-parse HEAD)" = "$TARGET" ] || fail "final_sha_mismatch"
printf 'SERVICE_ORDER_CYCLE_DEPLOY=PASS\nTARGET_SHA=%s\nBACKUP=%s\n' "$TARGET" "$BACKUP"
