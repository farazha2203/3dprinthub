#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

# One-shot, sha-pinned Store ProductVariant RMA release; no live fake payments.
ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
DB="sfkilvrs_EmiAdmin_3dprinthub"
HOST_BRANCH="release/phase50-a2j-hero-20260915"
BRANCH="fix/store-variant-rma-20261110"
BASE="e9a088cfe7fc3ebcdcde49e70e31b8f59709478e"
TARGET="${1:-}"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="/home/sfkilvrs/3dprinthub-deploy-backups/${STAMP}-store-variant-rma"
DELTA="/tmp/3dprinthub-store-rma-$$.txt"
trap 'rm -f "$DELTA" 2>/dev/null || true' EXIT
fail(){ printf 'STORE_VARIANT_RMA_DEPLOY=FAIL\nCAUSE=%s\nBACKUP=%s\n' "$1" "$BACKUP" >&2; exit 1; }
[ -n "$TARGET" ] || fail "missing_target_sha"
[ -x "$PY" ] && [ -d "$ROOT/.git" ] || fail "python_or_project_missing"
cd "$ROOT"
[ "$(git branch --show-current)" = "$HOST_BRANCH" ] || fail "unexpected_host_branch"
[ "$(git rev-parse HEAD)" = "$BASE" ] || fail "unexpected_runtime_sha"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "dirty_production_worktree"
case "$(git remote get-url origin)" in *farazha2203/3dprinthub.git|*farazha2203/3dprinthub) ;; *) fail "wrong_git_remote";; esac

"$PY" - "$DB" <<'PYCODE'
import os,sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
import django;django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from store.models import StoreOrder,StorePayment,ReturnRequest,InventoryMovement,ProductVariant
from website.models import Order,Payment,PaymentLedgerEntry,ServiceRefund,ServiceCreditNote
assert connection.vendor=="mysql" and connection.settings_dict.get("NAME")==sys.argv[1], "wrong_production_db"
ex=MigrationExecutor(connection)
assert not ex.migration_plan(ex.loader.graph.leaf_nodes()), "preexisting_pending_migrations"
assert ("store","0042_phase49_3i51_filament_registry_descriptions") in ex.loader.applied_migrations
assert ("website","0028_service_credit_refund_ledger") in ex.loader.applied_migrations
counts=(StoreOrder.objects.count(),StorePayment.objects.count(),ReturnRequest.objects.count(),
        InventoryMovement.objects.count(),ProductVariant.objects.count())
print("PREFLIGHT_STORE_COUNTS="+str(counts))
assert counts==(1,1,0,0,3798), "store_baseline_changed"
assert (Payment.objects.count(),PaymentLedgerEntry.objects.count(),ServiceRefund.objects.count(),
        ServiceCreditNote.objects.count())==(0,0,0,0)
q=Order.objects.get(pk=1).quote
assert (q.status,q.total_price,q.paid_amount,q.discount)==("draft",805000,0,0)
print("PREFLIGHT_UNMODIFIED_CUSTOMER_ORDERS=PASS")
PYCODE
"$PY" manage.py check || fail "django_check_before"
"$PY" manage.py makemigrations --check --dry-run || fail "schema_drift_before"

remote_sha="$(git ls-remote origin "refs/heads/$BRANCH" | awk '{print $1}')"
[ "$remote_sha" = "$TARGET" ] || fail "remote_branch_changed"
git fetch --no-tags origin "refs/heads/$BRANCH"
[ "$(git rev-parse FETCH_HEAD)" = "$TARGET" ] || fail "fetched_sha_mismatch"
git merge-base --is-ancestor "$BASE" "$TARGET" || fail "not_descendant_of_production"
git diff --name-only "$BASE" "$TARGET" > "$DELTA"
printf 'SOURCE_DELTA=\n';cat "$DELTA"
while IFS= read -r name; do
  [ -n "$name" ] || continue
  case "$name" in
    docs/*|store/models.py|store/admin.py|store/forms.py|store/views.py|store/services.py|store/signals.py|store/rma_services.py|store/rma_admin.py|store/finance_reconciliation.py|store/test_phase50_variant_rma.py|store/migrations/0043_store_variant_rma_stock_refund_audit.py|templates/store/order_detail.html|templates/admin/store/return_workflow_action.html|scripts/host/phase50_store_variant_rma_deploy.sh)
      ;;
    *) fail "unexpected_changed_file:$name";;
  esac
done < "$DELTA"
for expected in store/models.py store/rma_services.py store/rma_admin.py store/admin.py store/migrations/0043_store_variant_rma_stock_refund_audit.py store/test_phase50_variant_rma.py scripts/host/phase50_store_variant_rma_deploy.sh; do
  grep -Fxq "$expected" "$DELTA" || fail "missing_source_change:$expected"
done
if grep '^store/migrations/' "$DELTA" | grep -v -Fx 'store/migrations/0043_store_variant_rma_stock_refund_audit.py'; then
  fail "extra_store_migration"
fi
printf 'SOURCE_ALLOWLIST=PASS\n'

mkdir -p "$BACKUP"; chmod 700 "$BACKUP"
git archive --format=tar HEAD | gzip -1 > "$BACKUP/source-before.tar.gz"
tar -tzf "$BACKUP/source-before.tar.gz" >/dev/null || fail "source_archive_corrupt"
[ -f .env ] || fail "env_missing"
cp -p .env "$BACKUP/.env"; chmod 600 "$BACKUP/.env"
printf '%s\n' "$BASE" > "$BACKUP/previous-sha.txt"
printf '%s\n' "$HOST_BRANCH" > "$BACKUP/previous-branch.txt"
sha256sum "$BACKUP/source-before.tar.gz" > "$BACKUP/source-before.sha256"
sha256sum "$BACKUP/.env" > "$BACKUP/env.sha256"
(cd "$BACKUP" && sha256sum -c source-before.sha256 env.sha256) || fail "source_env_sha_bad"
export PHASE49_PROJECT_ROOT="$ROOT" PHASE49_BACKUP_ROOT="$BACKUP"
"$PY" scripts/host/phase49_3i53_mysql_backup.py "$DB" || fail "mysql_backup_failed"
[ -s "$BACKUP/database-before-3i53.sql.gz" ] || fail "db_backup_missing"
gzip -t "$BACKUP/database-before-3i53.sql.gz" || fail "db_backup_corrupt"
sha256sum "$BACKUP/database-before-3i53.sql.gz" > "$BACKUP/database-before.sha256"
(cd "$BACKUP" && sha256sum -c database-before.sha256) || fail "db_backup_hash_failed"

# Private financial snapshot: hashes IDs/statuses/prices only, no names or addresses.
"$PY" - "$BACKUP/baseline-sha256.txt" <<'PYCODE'
import os,sys,hashlib,json
os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
import django;django.setup()
from store.models import StoreOrder,StorePayment,ReturnRequest,InventoryMovement,ProductVariant
def vals(qs,columns): return list(qs.order_by("pk").values_list(*columns))
snapshot={
 "orders":vals(StoreOrder.objects,("pk","status","payment_status","total_amount","inventory_reserved")),
 "payments":vals(StorePayment.objects,("pk","status","amount","method")),
 "return_count":ReturnRequest.objects.count(),
 "stock_movement_count":InventoryMovement.objects.count(),
 "variant_count":ProductVariant.objects.count(),
 "variant_stock_totals":list(ProductVariant.objects.order_by("pk").values_list("pk","stock_quantity","reserved_quantity")),
}
digest=hashlib.sha256(json.dumps(snapshot,sort_keys=True,default=str).encode()).hexdigest()
with open(sys.argv[1],"w") as file:file.write(digest+"\n")
print("BASELINE_HASH="+digest)
PYCODE
printf 'COMPLETE_SOURCE_ENV_MYSQL_BACKUP=VERIFIED\nBACKUP=%s\n' "$BACKUP"

git merge --ff-only "$TARGET" || fail "fast_forward_failed"
[ "$(git rev-parse HEAD)" = "$TARGET" ] || fail "deployed_sha_wrong"
"$PY" - "$DB" <<'PYCODE'
import os,sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
import django;django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
assert connection.vendor=="mysql" and connection.settings_dict.get("NAME")==sys.argv[1]
ex=MigrationExecutor(connection)
plan=[(node.app_label,node.name,backward) for node,backward in ex.migration_plan(ex.loader.graph.leaf_nodes())]
print("RMA_MIGRATION_PLAN="+str(plan))
assert plan==[("store","0043_store_variant_rma_stock_refund_audit",False)], "unexpected_migration_plan"
PYCODE
"$PY" manage.py migrate store 0043_store_variant_rma_stock_refund_audit --noinput || fail "migration_failed"
"$PY" manage.py check || fail "postmigrate_django_check_failed"
"$PY" manage.py makemigrations --check --dry-run || fail "postmigrate_schema_drift"

"$PY" - "$DB" "$BACKUP/baseline-sha256.txt" <<'PYCODE'
import os,sys,json,hashlib
os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
import django;django.setup()
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import RequestFactory
from django.urls import reverse
from store.models import (
    StoreOrder,StorePayment,ReturnRequest,InventoryMovement,ProductVariant,
    StoreReturnInspection,StoreReturnRefund,StoreReturnRefundLedger,
)
from website.models import Order,Payment,PaymentLedgerEntry,ServiceCreditNote,ServiceRefund
from store.finance_reconciliation import collect_finance_reconciliation
assert connection.vendor=="mysql" and connection.settings_dict.get("NAME")==sys.argv[1]
ex=MigrationExecutor(connection)
assert not ex.migration_plan(ex.loader.graph.leaf_nodes())
assert ("store","0043_store_variant_rma_stock_refund_audit") in ex.loader.applied_migrations
assert (StoreReturnInspection.objects.count(),StoreReturnRefund.objects.count(),StoreReturnRefundLedger.objects.count())==(0,0,0)
def vals(qs,cols):return list(qs.order_by("pk").values_list(*cols))
snap={
 "orders":vals(StoreOrder.objects,("pk","status","payment_status","total_amount","inventory_reserved")),
 "payments":vals(StorePayment.objects,("pk","status","amount","method")),
 "return_count":ReturnRequest.objects.count(),
 "stock_movement_count":InventoryMovement.objects.count(),
 "variant_count":ProductVariant.objects.count(),
 "variant_stock_totals":list(ProductVariant.objects.order_by("pk").values_list("pk","stock_quantity","reserved_quantity")),
}
digest=hashlib.sha256(json.dumps(snap,sort_keys=True,default=str).encode()).hexdigest()
with open(sys.argv[2]) as fh:expected=fh.read().strip()
print("STORE_POSTMIGRATE_FINGERPRINT="+digest)
assert digest==expected,"live_store_financial_or_stock_changed"
assert (Payment.objects.count(),PaymentLedgerEntry.objects.count(),
        ServiceCreditNote.objects.count(),ServiceRefund.objects.count())==(0,0,0,0)
q=Order.objects.get(pk=1).quote
assert (q.status,q.total_price,q.paid_amount,q.discount)==("draft",805000,0,0)
staff=User(pk=9999999,username="read-only-store-rma-auditor",is_staff=True,is_active=True,is_superuser=True)
request=RequestFactory().get(reverse("admin:store_returnrequest_changelist"),HTTP_HOST="3dprinthub.ir")
request.user=staff;request.session={};request._messages=FallbackStorage(request)
response=admin.site._registry[ReturnRequest].changelist_view(request)
if hasattr(response,"render") and not getattr(response,"is_rendered",True):response.render()
print("RETURN_ADMIN_GET="+str(response.status_code))
assert response.status_code==200
for name in ("admin:store_returnrequest_workflow_review","admin:store_returnrequest_workflow_inspect","admin:store_returnrequest_workflow_request_refund"):
  url=reverse(name,args=[42])
  assert url.startswith("/admin/store/returnrequest/")
print("RMA_ADMIN_URLS=PASS")
report=collect_finance_reconciliation(check_storage=False)
print("FINANCE_RECON_OK="+str(report["ok"]))
print("FINANCE_RECON_FAILURES="+str(report["failures"]))
assert report["ok"],"existing_finance_reconciliation_failed"
print("CUSTOMER_FINANCIAL_DATA_UNCHANGED=PASS")
PYCODE
mkdir -p tmp;touch tmp/restart.txt;sleep 4
"$PY" - <<'PYCODE'
from urllib import request
for path in ("/","/store/","/admin/login/"):
    with request.urlopen(request.Request("https://3dprinthub.ir"+path,headers={
        "User-Agent":"3DPrintHub-StoreVariantRMARelease/1.0",
        "Cache-Control":"no-cache",
    }),timeout=20) as response:
        assert response.status==200
        print("PUBLIC_HTTP=200 "+path)
PYCODE
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "postrelease_source_dirty"
[ "$(git rev-parse HEAD)" = "$TARGET" ] || fail "postrelease_sha_changed"
printf 'STORE_VARIANT_RMA_DEPLOY=PASS\nTARGET_SHA=%s\nBACKUP=%s\n' "$TARGET" "$BACKUP"
