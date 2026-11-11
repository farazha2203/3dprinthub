#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

# One-use, SHA-pinned dual-approval release: NO bank payout, fake payment or customer mutation.
ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
DB="sfkilvrs_EmiAdmin_3dprinthub"
HOST_BRANCH="release/phase50-a2j-hero-20260915"
BRANCH="fix/service-store-refund-dual-approval-20261111"
BASE="0ae8d7851b803ddc8ab75be3adf35ac2a2d76a5a"
TARGET="${1:-}"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="/home/sfkilvrs/3dprinthub-deploy-backups/${STAMP}-refund-dual-approval"
DELTA="/tmp/3dprinthub-refund-dual-approval-$$.txt"
trap 'rm -f "$DELTA" 2>/dev/null || true' EXIT
fail(){ printf 'REFUND_DUAL_APPROVAL_DEPLOY=FAIL\nCAUSE=%s\nBACKUP=%s\n' "$1" "$BACKUP" >&2; exit 1; }

[ -n "$TARGET" ] || fail "target_sha_missing"
[ -x "$PY" ] && [ -d "$ROOT/.git" ] || fail "host_runtime_missing"
cd "$ROOT"
[ "$(git branch --show-current)" = "$HOST_BRANCH" ] || fail "wrong_host_branch"
[ "$(git rev-parse HEAD)" = "$BASE" ] || fail "production_sha_drift"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "dirty_production_source"
case "$(git remote get-url origin)" in *farazha2203/3dprinthub.git|*farazha2203/3dprinthub) ;; *) fail "remote_not_expected";; esac

"$PY" - "$DB" <<'PYCODE'
import os,sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
import django;django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from store.models import (
    StoreOrder,StorePayment,ReturnRequest,InventoryMovement,ProductVariant,
    StoreReturnRefund,StoreReturnRefundLedger,StoreReturnInspection
)
from website.models import Order,Payment,PaymentLedgerEntry,ServiceRefund,ServiceCreditNote,ServiceOrderDelivery
assert connection.vendor=="mysql" and connection.settings_dict.get("NAME")==sys.argv[1]
ex=MigrationExecutor(connection)
assert not ex.migration_plan(ex.loader.graph.leaf_nodes()), "unexpected_pending_migrations"
assert ("store","0043_store_variant_rma_stock_refund_audit") in ex.loader.applied_migrations
assert ("website","0028_service_credit_refund_ledger") in ex.loader.applied_migrations
store_counts=(
    StoreOrder.objects.count(),StorePayment.objects.count(),ReturnRequest.objects.count(),
    InventoryMovement.objects.count(),ProductVariant.objects.count(),StoreReturnRefund.objects.count(),
    StoreReturnRefundLedger.objects.count(),StoreReturnInspection.objects.count(),
)
print("STORE_COUNTS_BEFORE="+str(store_counts))
assert store_counts==(1,1,0,0,3798,0,0,0), "live_store_records_changed"
service_counts=(
    Order.objects.count(),Payment.objects.count(),PaymentLedgerEntry.objects.count(),
    ServiceRefund.objects.count(),ServiceCreditNote.objects.count(),ServiceOrderDelivery.objects.count(),
)
print("SERVICE_COUNTS_BEFORE="+str(service_counts))
assert service_counts==(1,0,0,0,0,0), "live_service_finance_changed"
o=StoreOrder.objects.get()
assert (o.status,o.payment_status,int(o.total_amount))==(
    "payment_review","awaiting_review",945450
), "original_store_order_changed"
q=Order.objects.get(pk=1).quote
assert (q.status,q.total_price,q.paid_amount,q.discount)==("draft",805000,0,0)
print("PREFLIGHT_FINANCE_AND_ORDER=PASS")
PYCODE
"$PY" manage.py check || fail "preflight_django_check"
"$PY" manage.py makemigrations --check --dry-run || fail "preflight_unexpected_drift"

remote_sha="$(git ls-remote origin "refs/heads/$BRANCH" | awk '{print $1}')"
[ "$remote_sha" = "$TARGET" ] || fail "remote_branch_sha_mismatch"
git fetch --no-tags origin "refs/heads/$BRANCH"
[ "$(git rev-parse FETCH_HEAD)" = "$TARGET" ] || fail "fetched_sha_mismatch"
git merge-base --is-ancestor "$BASE" "$TARGET" || fail "target_not_descendant"
git diff --name-only "$BASE" "$TARGET" > "$DELTA"
printf 'SOURCE_DELTA=\n';cat "$DELTA"
while IFS= read -r name; do
    [ -n "$name" ] || continue
    case "$name" in
        docs/*|website/models.py|website/admin.py|website/service_adjustments.py|website/service_adjustment_admin.py|website/test_service_financial_adjustments.py|website/migrations/0029_refund_maker_checker_approval.py|store/models.py|store/admin.py|store/rma_services.py|store/rma_admin.py|store/finance_reconciliation.py|store/test_phase50_variant_rma.py|store/migrations/0044_refund_maker_checker_approval.py|templates/admin/website/order/service_finance_action.html|templates/admin/store/return_workflow_action.html|scripts/host/phase50_refund_dual_approval_deploy.sh)
        ;;
        *) fail "unapproved_source_change:$name";;
    esac
done < "$DELTA"
for expected in website/models.py website/service_adjustments.py website/migrations/0029_refund_maker_checker_approval.py store/models.py store/rma_services.py store/migrations/0044_refund_maker_checker_approval.py scripts/host/phase50_refund_dual_approval_deploy.sh; do
    grep -Fxq "$expected" "$DELTA" || fail "missing_source_change:$expected"
done
if grep -E '^(store|website)/migrations/' "$DELTA" | grep -Ev '^(store/migrations/0044_refund_maker_checker_approval.py|website/migrations/0029_refund_maker_checker_approval.py)$'; then
    fail "extra_migration"
fi
printf 'SOURCE_ALLOWLIST=PASS\n'

mkdir -p "$BACKUP";chmod 700 "$BACKUP"
git archive --format=tar HEAD | gzip -1 > "$BACKUP/source-before.tar.gz"
tar -tzf "$BACKUP/source-before.tar.gz" > /dev/null || fail "source_backup_bad"
[ -f .env ] || fail "missing_env"
cp -p .env "$BACKUP/.env";chmod 600 "$BACKUP/.env"
printf '%s\n' "$BASE" > "$BACKUP/previous-sha.txt"
printf '%s\n' "$HOST_BRANCH" > "$BACKUP/previous-branch.txt"
sha256sum "$BACKUP/source-before.tar.gz" > "$BACKUP/source-before.sha256"
sha256sum "$BACKUP/.env" > "$BACKUP/env.sha256"
(cd "$BACKUP" && sha256sum -c source-before.sha256 env.sha256) || fail "source_env_hash_mismatch"
export PHASE49_PROJECT_ROOT="$ROOT" PHASE49_BACKUP_ROOT="$BACKUP"
"$PY" scripts/host/phase49_3i53_mysql_backup.py "$DB" || fail "mysql_dump_failed"
[ -s "$BACKUP/database-before-3i53.sql.gz" ] || fail "db_backup_missing"
gzip -t "$BACKUP/database-before-3i53.sql.gz" || fail "db_gzip_invalid"
sha256sum "$BACKUP/database-before-3i53.sql.gz" > "$BACKUP/database-before.sha256"
(cd "$BACKUP" && sha256sum -c database-before.sha256) || fail "db_hash_mismatch"

"$PY" - "$BACKUP/baseline-sha256.txt" <<'PYCODE'
import os,sys,json,hashlib
os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
import django;django.setup()
from store.models import StoreOrder,StorePayment,ReturnRequest,InventoryMovement,ProductVariant,StoreReturnRefund,StoreReturnRefundLedger
from website.models import Order,Quote,Payment,PaymentLedgerEntry,ServiceRefund,ServiceCreditNote
def vals(qs,cols):return list(qs.order_by("pk").values_list(*cols))
snapshot={
    "store_orders":vals(StoreOrder.objects,("pk","status","payment_status","total_amount","inventory_reserved")),
    "store_payments":vals(StorePayment.objects,("pk","status","amount","method")),
    "website_orders":vals(Order.objects,("pk","status","quantity")),
    "website_quotes":vals(Quote.objects,("pk","status","total_price","discount")),
    "variant_stocks":vals(ProductVariant.objects,("pk","stock_quantity","reserved_quantity")),
    "return_requests":ReturnRequest.objects.count(),
    "stock_movements":InventoryMovement.objects.count(),
    "store_refunds":StoreReturnRefund.objects.count(),
    "store_refund_debits":StoreReturnRefundLedger.objects.count(),
    "service_payments":Payment.objects.count(),
    "service_ledger":PaymentLedgerEntry.objects.count(),
    "service_refunds":ServiceRefund.objects.count(),
    "service_credits":ServiceCreditNote.objects.count(),
}
digest=hashlib.sha256(json.dumps(snapshot,sort_keys=True,default=str).encode()).hexdigest()
with open(sys.argv[1],"w") as out:out.write(digest+"\n")
print("BEFORE_FINANCIAL_STOCK_HASH="+digest)
PYCODE
printf 'FULL_VERIFIED_BACKUP=%s\n' "$BACKUP"

git merge --ff-only "$TARGET" || fail "fast_forward_failed"
[ "$(git rev-parse HEAD)" = "$TARGET" ] || fail "unexpected_deployed_sha"
"$PY" - "$DB" <<'PYCODE'
import os,sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
import django;django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
assert connection.vendor=="mysql" and connection.settings_dict.get("NAME")==sys.argv[1]
ex=MigrationExecutor(connection)
plan=[(node.app_label,node.name,backward) for node,backward in ex.migration_plan(ex.loader.graph.leaf_nodes())]
print("MIGRATION_PLAN="+str(plan))
assert len(plan)==2 and set(plan)=={
    ("website","0029_refund_maker_checker_approval",False),
    ("store","0044_refund_maker_checker_approval",False),
},"unexpected_schema_migration_plan"
PYCODE
"$PY" manage.py migrate --noinput || fail "migration_failed"
"$PY" manage.py check || fail "postmigrate_check_failed"
"$PY" manage.py makemigrations --check --dry-run || fail "postmigrate_schema_drift"

"$PY" - "$DB" "$BACKUP/baseline-sha256.txt" <<'PYCODE'
import os,sys,json,hashlib
os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
import django;django.setup()
from django.contrib import admin
from django.contrib.auth.models import Permission,User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import RequestFactory
from django.urls import reverse
from store.models import StoreOrder,StorePayment,ReturnRequest,InventoryMovement,ProductVariant,StoreReturnRefund,StoreReturnRefundLedger
from website.models import Order,Quote,Payment,PaymentLedgerEntry,ServiceRefund,ServiceCreditNote
from store.finance_reconciliation import collect_finance_reconciliation
assert connection.vendor=="mysql" and connection.settings_dict.get("NAME")==sys.argv[1]
ex=MigrationExecutor(connection)
assert not ex.migration_plan(ex.loader.graph.leaf_nodes())
assert ("website","0029_refund_maker_checker_approval") in ex.loader.applied_migrations
assert ("store","0044_refund_maker_checker_approval") in ex.loader.applied_migrations
for app,codename in (("website","approve_servicerefund"),("store","approve_storereturnrefund")):
    assert Permission.objects.filter(content_type__app_label=app,codename=codename).count()==1
print("SEPARATE_FINANCE_APPROVAL_PERMISSIONS=PASS")
def vals(qs,cols):return list(qs.order_by("pk").values_list(*cols))
snapshot={
    "store_orders":vals(StoreOrder.objects,("pk","status","payment_status","total_amount","inventory_reserved")),
    "store_payments":vals(StorePayment.objects,("pk","status","amount","method")),
    "website_orders":vals(Order.objects,("pk","status","quantity")),
    "website_quotes":vals(Quote.objects,("pk","status","total_price","discount")),
    "variant_stocks":vals(ProductVariant.objects,("pk","stock_quantity","reserved_quantity")),
    "return_requests":ReturnRequest.objects.count(),
    "stock_movements":InventoryMovement.objects.count(),
    "store_refunds":StoreReturnRefund.objects.count(),
    "store_refund_debits":StoreReturnRefundLedger.objects.count(),
    "service_payments":Payment.objects.count(),
    "service_ledger":PaymentLedgerEntry.objects.count(),
    "service_refunds":ServiceRefund.objects.count(),
    "service_credits":ServiceCreditNote.objects.count(),
}
digest=hashlib.sha256(json.dumps(snapshot,sort_keys=True,default=str).encode()).hexdigest()
with open(sys.argv[2]) as fh:expected=fh.read().strip()
print("AFTER_FINANCIAL_STOCK_HASH="+digest)
assert digest==expected,"real_money_or_stock_changed"
staff=User(pk=9999999,username="readonly-dual-approval-qa",is_staff=True,is_active=True,is_superuser=True)
def admin_req(path):
    req=RequestFactory().get(path,HTTP_HOST="3dprinthub.ir")
    req.user=staff;req.session={};req._messages=FallbackStorage(req)
    return req
for model,route in (
    (ReturnRequest,"admin:store_returnrequest_changelist"),
    (StoreReturnRefund,"admin:store_storereturnrefund_changelist"),
    (ServiceRefund,"admin:website_servicerefund_changelist"),
):
    path=reverse(route);resp=admin.site._registry[model].changelist_view(admin_req(path))
    if hasattr(resp,"render") and not getattr(resp,"is_rendered",True):resp.render()
    print("READONLY_ADMIN_GET="+route+"="+str(resp.status_code))
    assert resp.status_code==200
report=collect_finance_reconciliation(check_storage=False)
print("FINANCE_RECON_OK="+str(report["ok"]))
print("FINANCE_RECON_FAILURES="+str(report["failures"]))
assert report["ok"] and not report["failures"]
print("CUSTOMER_FINANCIAL_AND_VARIANT_STOCK_UNCHANGED=PASS")
PYCODE
mkdir -p tmp;touch tmp/restart.txt;sleep 4
"$PY" - <<'PYCODE'
from urllib import request
for path in ("/","/store/","/admin/login/"):
    with request.urlopen(request.Request("https://3dprinthub.ir"+path,headers={
        "User-Agent":"3DPrintHub-RefundDualApproval/1.0","Cache-Control":"no-cache",
    }),timeout=20) as response:
        assert response.status==200
        print("PUBLIC_HTTP=200 "+path)
PYCODE
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "production_source_dirty_after"
[ "$(git rev-parse HEAD)" = "$TARGET" ] || fail "postrelease_sha_drift"
printf 'REFUND_DUAL_APPROVAL_DEPLOY=PASS\nTARGET_SHA=%s\nBACKUP=%s\n' "$TARGET" "$BACKUP"
