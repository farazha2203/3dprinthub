#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
EXPECTED_DB="sfkilvrs_EmiAdmin_3dprinthub"
HOST_BRANCH="release/phase50-a2j-hero-20260915"
TARGET_BRANCH="release/phase50-a2l-owner-qa-20260918"
EXPECTED_BASELINE="f13ba8134cf6569c5a95da080bb97077c0cd6745"
TARGET_SHA="${1:-}"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="/home/sfkilvrs/3dprinthub-deploy-backups/${STAMP}-phase50-a2l-public-media-payment"
TMP_DELTA="/tmp/3dprinthub-a2l-public-media-payment-$$.txt"

cleanup(){ rm -f "$TMP_DELTA" 2>/dev/null || true; }
trap cleanup EXIT
fail(){
  printf 'A2L_PUBLIC_MEDIA_PAYMENT_DEPLOY_FAIL=%s\n' "$1" >&2
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
expected=sys.argv[1]
print("DB_VENDOR="+str(connection.vendor))
print("DB_NAME="+str(connection.settings_dict.get("NAME") or ""))
if connection.vendor!="mysql" or str(connection.settings_dict.get("NAME") or "")!=expected:
    raise SystemExit("A2L_PUBLIC_MEDIA_PAYMENT_DEPLOY_FAIL=database_identity_mismatch")
plan=MigrationExecutor(connection).migration_plan(MigrationExecutor(connection).loader.graph.leaf_nodes())
print("MIGRATION_PLAN="+repr([(m.app_label,m.name,b) for m,b in plan]))
if plan:
    raise SystemExit("A2L_PUBLIC_MEDIA_PAYMENT_DEPLOY_FAIL=migration_plan_not_empty")
ready=publish_readiness()
print("PUBLISH_READY="+repr(ready.get("ready")))
print("PUBLISH_BLOCKERS="+repr(ready.get("blockers") or []))
if ready.get("ready") is not True:
    raise SystemExit("A2L_PUBLIC_MEDIA_PAYMENT_DEPLOY_FAIL=receiver_not_ready")
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
printf '%s\n' "===== PUBLIC MEDIA + PAYMENT DELTA ====="
cat "$TMP_DELTA"
if grep -Eq '(^|/)migrations/[0-9]{4}_[^/]+\.py$|^requirements[^/]*\.txt$|^config/settings' "$TMP_DELTA"; then
  fail "migration_dependency_or_settings_delta_detected"
fi
for required in config/urls.py store/public_media.py store/management/commands/phase50_a2l_seed_manual_payment.py store/operator_notifications.py store/views.py store/test_phase49_1_media.py store/test_phase50_a2l_manual_payment.py store/tests.py scripts/host/phase50_a2l_public_media_payment_deploy.sh; do
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
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
grep -Fq '"p/",' store/public_media.py || fail "canonical_public_media_prefix_missing"
grep -Fq '(?:store/(?:products|categories|seo)|p)' config/urls.py || fail "canonical_public_media_route_missing"
grep -Fq 'A2L_MANUAL_PAYMENT_DRY_RUN=PASS' store/management/commands/phase50_a2l_seed_manual_payment.py || fail "manual_payment_seed_missing"
grep -Fq 'notify_payment_receipt(payment)' store/views.py || fail "payment_receipt_notification_hook_missing"

"$PY" - <<'PY'
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
import django; django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from catalog_bridge.publish_readiness import publish_readiness
from store.phase50_commerce_policy import StorePaymentSettings
plan=MigrationExecutor(connection).migration_plan(MigrationExecutor(connection).loader.graph.leaf_nodes())
if plan:
    raise SystemExit("A2L_PUBLIC_MEDIA_PAYMENT_DEPLOY_FAIL=post_merge_migration_plan_not_empty")
ready=publish_readiness()
if ready.get("ready") is not True:
    raise SystemExit("A2L_PUBLIC_MEDIA_PAYMENT_DEPLOY_FAIL=post_merge_receiver_not_ready")
print("PAYMENT_SETTINGS_COUNT_PRE_APPLY="+str(StorePaymentSettings.objects.count()))
print("EFFECTIVE_MEDIA_ROOT="+str(__import__("django.conf").conf.settings.MEDIA_ROOT))
PY
"$PY" manage.py phase50_a2l_seed_manual_payment | grep -Fq 'A2L_MANUAL_PAYMENT_DRY_RUN=PASS' || fail "manual_payment_seed_dry_run_failed"

mkdir -p tmp
touch tmp/restart.txt
sleep 4

"$PY" - <<'PY'
import html, re
from urllib import request, error
base="https://3dprinthub.ir"
headers={"User-Agent":"3DPrintHub-A2L-Media/1.0","Cache-Control":"no-cache"}
product=base+"/store/product/mini-articulated-skeletal-spinosaurus/"
with request.urlopen(request.Request(product,headers=headers),timeout=20) as r:
    body=r.read(2_000_000).decode("utf-8","replace")
    print("PRODUCT_HTTP="+str(r.status))
    if r.status!=200:
        raise SystemExit("A2L_PUBLIC_MEDIA_PAYMENT_DEPLOY_FAIL=product_http_not_200")
paths=[]
for raw in re.findall(r'(?:src|href)=["\']([^"\']*/media/p/[^"\']+)["\']',body,re.I):
    path=html.unescape(raw.strip())
    if path not in paths:
        paths.append(path)
if not paths:
    raise SystemExit("A2L_PUBLIC_MEDIA_PAYMENT_DEPLOY_FAIL=canonical_media_not_in_product_html")
for path in paths[:6]:
    url=path if path.startswith("http") else base+path
    with request.urlopen(request.Request(url,headers=headers),timeout=20) as r:
        ctype=str(r.headers.get("Content-Type") or "").lower()
        print("CANONICAL_MEDIA_HTTP="+str(r.status)+" "+url)
        if r.status!=200 or not ctype.startswith("image/"):
            raise SystemExit("A2L_PUBLIC_MEDIA_PAYMENT_DEPLOY_FAIL=canonical_media_http_failed")
try:
    request.urlopen(request.Request(base+"/media/store/imported-models/private-probe.webp",headers=headers),timeout=10)
except error.HTTPError as exc:
    print("PRIVATE_MEDIA_PROBE_HTTP="+str(exc.code))
    if exc.code != 404:
        raise
else:
    raise SystemExit("A2L_PUBLIC_MEDIA_PAYMENT_DEPLOY_FAIL=private_imported_media_exposed")
print("PUBLIC_MEDIA_SMOKE=PASS")
PY

printf 'FINAL_HEAD=%s\n' "$(git rev-parse HEAD)"
printf 'FINAL_WORKTREE=%s\n' "$(test -z "$(git status --porcelain --untracked-files=all)" && printf CLEAN || printf DIRTY)"
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"
printf 'PHASE50_A2L_PUBLIC_MEDIA_PAYMENT_DEPLOY=PASS\n'
