#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
# Guarded, additive website.0028 credit/refund service finance deployment.
ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
DB="sfkilvrs_EmiAdmin_3dprinthub"
HOST_BRANCH="release/phase50-a2j-hero-20260915"
GIT_BRANCH="fix/website-service-credit-refund-20261110"
BASE="b5687b8120ee8ec3cfe7ad68aa04a8c531cf1c95"
TARGET="${1:-}"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="/home/sfkilvrs/3dprinthub-deploy-backups/${STAMP}-service-credit-refund"
DELTA="/tmp/3dprinthub-credit-refund-$$.txt"
trap 'rm -f "$DELTA" 2>/dev/null || true' EXIT
fail(){ printf 'SERVICE_FINANCE_RELEASE=FAIL\nREASON=%s\nBACKUP=%s\n' "$1" "$BACKUP" >&2;exit 1; }
[ -n "$TARGET" ] || fail "target_sha_required"
[ -d "$ROOT/.git" ] && [ -x "$PY" ] || fail "python_or_project_missing"
cd "$ROOT"
[ "$(git branch --show-current)" = "$HOST_BRANCH" ] || fail "unexpected_host_branch"
[ "$(git rev-parse HEAD)" = "$BASE" ] || fail "host_sha_not_expected"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "dirty_production_source"
case "$(git remote get-url origin)" in *farazha2203/3dprinthub.git|*farazha2203/3dprinthub) ;; *) fail "unexpected_remote";; esac

# The production service is expected to have zero real money/shipments at this release.
"$PY" - "$DB" <<'PYCODE'
import os,sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
import django;django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from website.models import Order,Quote,Payment,PaymentLedgerEntry,ServiceOrderDelivery
assert connection.vendor=="mysql" and connection.settings_dict.get("NAME")==sys.argv[1]
executor=MigrationExecutor(connection)
assert not executor.migration_plan(executor.loader.graph.leaf_nodes())
assert ("website","0027_service_order_payment_delivery_catalog_offer") in executor.loader.applied_migrations
counts=(Order.objects.count(),Quote.objects.count(),Payment.objects.count(),PaymentLedgerEntry.objects.count(),ServiceOrderDelivery.objects.count())
print("PREDEPLOY_RECORD_COUNTS="+str(counts))
assert counts==(1,1,0,0,0), "customer_finance_or_delivery_changed"
order=Order.objects.get(pk=1);quote=order.quote
print("PREDEPLOY_QUOTE="+str((quote.status,quote.print_time_scope,quote.total_price,quote.paid_amount,quote.pending_amount,quote.discount,order.quantity)))
assert (quote.status,quote.print_time_scope,quote.total_price,quote.paid_amount,quote.pending_amount,quote.discount,order.quantity)==("draft","per_piece",805000,0,0,0,4)
assert quote.filament_offer_id is None
print("PREDEPLOY_FINANCIAL_INVARIANTS=PASS")
PYCODE
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
remote_sha="$(git ls-remote origin "refs/heads/$GIT_BRANCH" | awk '{print $1}')"
[ "$remote_sha" = "$TARGET" ] || fail "remote_branch_head_mismatch"
git fetch --no-tags origin "refs/heads/$GIT_BRANCH"
[ "$(git rev-parse FETCH_HEAD)" = "$TARGET" ] || fail "fetched_sha_mismatch"
git merge-base --is-ancestor "$BASE" "$TARGET" || fail "candidate_not_descendant"
git diff --name-only "$BASE" "$TARGET" > "$DELTA"
printf 'SOURCE_CHANGE_ALLOWLIST=\n';cat "$DELTA"
while IFS= read -r changed; do
  [ -n "$changed" ] || continue
  case "$changed" in
    docs/*|website/models.py|website/payment_services.py|website/admin.py|website/order_finance_admin.py|website/service_adjustments.py|website/service_adjustment_admin.py|website/service_delivery_admin.py|website/test_service_financial_adjustments.py|website/migrations/0028_service_credit_refund_ledger.py|store/finance_reconciliation.py|templates/admin/website/order/change_form.html|templates/admin/website/order/service_finance_action.html|templates/website/quote_detail.html|scripts/host/phase50_service_credit_refund_deploy.sh)
      ;;
    *) fail "unexpected_source_delta:$changed" ;;
  esac
done < "$DELTA"
for required in website/models.py website/payment_services.py website/admin.py website/service_adjustments.py website/service_adjustment_admin.py website/migrations/0028_service_credit_refund_ledger.py website/test_service_financial_adjustments.py store/finance_reconciliation.py scripts/host/phase50_service_credit_refund_deploy.sh; do
  grep -Fxq "$required" "$DELTA" || fail "missing_expected_delta:$required"
done
if grep '^website/migrations/' "$DELTA" | grep -v -Fx 'website/migrations/0028_service_credit_refund_ledger.py'; then
  fail "extra_django_migrations"
fi
printf 'SOURCE_ALLOWLIST=PASS\n'

# Take fresh, verified source/.env/full-MySQL backups before advancing runtime.
mkdir -p "$BACKUP";chmod 700 "$BACKUP"
git archive --format=tar HEAD | gzip -1 > "$BACKUP/source-before.tar.gz"
tar -tzf "$BACKUP/source-before.tar.gz" >/dev/null || fail "source_backup_corrupt"
[ -f .env ] || fail "env_missing"
cp -p .env "$BACKUP/.env";chmod 600 "$BACKUP/.env"
printf '%s\n' "$BASE" > "$BACKUP/previous-sha.txt"
printf '%s\n' "$HOST_BRANCH" > "$BACKUP/previous-branch.txt"
sha256sum "$BACKUP/source-before.tar.gz" > "$BACKUP/source-before.sha256"
sha256sum "$BACKUP/.env" > "$BACKUP/env.sha256"
(cd "$BACKUP" && sha256sum -c source-before.sha256 env.sha256) || fail "source_env_checksum_failure"
export PHASE49_PROJECT_ROOT="$ROOT" PHASE49_BACKUP_ROOT="$BACKUP"
"$PY" scripts/host/phase49_3i53_mysql_backup.py "$DB" || fail "mysql_backup_command_failure"
[ -s "$BACKUP/database-before-3i53.sql.gz" ] || fail "mysql_backup_empty"
gzip -t "$BACKUP/database-before-3i53.sql.gz" || fail "mysql_gzip_corrupt"
sha256sum "$BACKUP/database-before-3i53.sql.gz" > "$BACKUP/database-before.sha256"
(cd "$BACKUP" && sha256sum -c database-before.sha256) || fail "mysql_sha256_bad"
printf 'VERIFIED_FULL_BACKUP=%s\n' "$BACKUP"

git merge --ff-only "$TARGET" || fail "ff_merge_failed"
[ "$(git rev-parse HEAD)" = "$TARGET" ] || fail "wrong_deployed_sha"
"$PY" - "$DB" <<'PYCODE'
import os,sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
import django;django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
assert connection.vendor=="mysql" and connection.settings_dict.get("NAME")==sys.argv[1]
executor=MigrationExecutor(connection)
plan=[(node.app_label,node.name,backward) for node,backward in executor.migration_plan(executor.loader.graph.leaf_nodes())]
print("EXPECTED_MIGRATION_PLAN="+str(plan))
assert plan==[("website","0028_service_credit_refund_ledger",False)]
PYCODE
"$PY" manage.py migrate website 0028_service_credit_refund_ledger --noinput || fail "migration_0028_failure"
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run

# Independent read-only checks: never create a fake payment/credit note/refund.
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
from django.urls import reverse
from website.models import (
    Order,Quote,Payment,PaymentLedgerEntry,ServiceOrderDelivery,
    ServiceCreditNote,ServiceRefund,
)
from website.views import quote_detail_view
from store.finance_reconciliation import collect_finance_reconciliation
assert connection.vendor=="mysql" and connection.settings_dict.get("NAME")==sys.argv[1]
ex=MigrationExecutor(connection)
assert not ex.migration_plan(ex.loader.graph.leaf_nodes())
assert ("website","0028_service_credit_refund_ledger") in ex.loader.applied_migrations
assert (Payment.objects.count(),PaymentLedgerEntry.objects.count(),ServiceOrderDelivery.objects.count(),
        ServiceCreditNote.objects.count(),ServiceRefund.objects.count())==(0,0,0,0,0)
o=Order.objects.get(pk=1);q=o.quote
assert (q.status,q.total_price,q.effective_total_price,q.credit_note_total,q.refunded_amount,
        q.paid_amount,q.pending_amount,q.remaining_amount,o.quantity,q.print_time_scope)==(
        "draft",805000,805000,0,0,0,0,805000,4,"per_piece")
user=User(pk=9999999,username="read-only-refund-auditor",is_staff=True,is_active=True,is_superuser=True)
def rget(path):
    r=RequestFactory().get(path,HTTP_HOST="3dprinthub.ir")
    r.user=user;r.session={};r._messages=FallbackStorage(r);r.current_app=admin.site.name
    return r
admin_url=reverse("admin:website_order_change",args=[o.pk])
admin_response=admin.site._registry[Order].change_view(rget(admin_url),str(o.pk));admin_response.render()
assert admin_response.status_code==200
credit_url=reverse("admin:website_order_issue_credit_note",args=[o.pk])
request_url=reverse("admin:website_order_request_refund",args=[o.pk])
assert "record-delivery/" in admin_response.content.decode("utf-8")
assert "record-receipt/" not in admin_response.content.decode("utf-8")
from website.service_adjustment_admin import issue_service_credit_note_view,request_service_refund_view
for fn,url in ((issue_service_credit_note_view,credit_url),(request_service_refund_view,request_url)):
    response=fn(admin.site._registry[Order],rget(url),o.pk)
    # django.shortcuts.render() already returns HttpResponse, not TemplateResponse.
    if hasattr(response, "render") and not getattr(response, "is_rendered", True):
        response.render()
    assert response.status_code==200
customer=quote_detail_view(rget("/quote/readonly/"),o.public_token)
assert customer.status_code==200 and "w-full min-w-[650px] text-sm" not in customer.content.decode("utf-8")
diagnostic=collect_finance_reconciliation(check_storage=False)
print("FINANCE_RECONCILIATION_OK="+str(diagnostic["ok"]))
print("FINANCE_RECONCILIATION_FAILURES="+str(diagnostic["failures"]))
print("READONLY_ADMIN_ORDER1_GET="+str(admin_response.status_code))
print("READONLY_CREDIT_AND_REFUND_FORMS=200")
print("FINANCE_RECORDS_UNCHANGED=PASS")
print("SCHEMA_AND_QUOTE_INVARIANTS=PASS")
PYCODE
mkdir -p tmp;touch tmp/restart.txt;sleep 4
"$PY" - <<'PYCODE'
from urllib import request
for path in ("/","/store/","/admin/login/"):
    with request.urlopen(request.Request("https://3dprinthub.ir"+path,
        headers={"User-Agent":"3DPrintHub-CreditRefundRelease/1.0","Cache-Control":"no-cache"}),timeout=20) as response:
        assert response.status==200
        print("PUBLIC_HTTP=200 "+path)
PYCODE
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "postrelease_worktree_dirty"
[ "$(git rev-parse HEAD)" = "$TARGET" ] || fail "postrelease_sha_drift"
printf 'SERVICE_FINANCE_RELEASE=PASS\nTARGET_SHA=%s\nBACKUP=%s\n' "$TARGET" "$BACKUP"
