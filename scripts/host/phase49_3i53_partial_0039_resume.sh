#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
BRANCH="agent/phase49-3i18-operator-bulk-ai-rebuild"
EXPECTED_DB="sfkilvrs_EmiAdmin_3dprinthub"
EXPECTED_CURRENT_HEAD="5f6c13ab879558cb66db3e316e0522c5e5783ae0"
FULL_ROLLBACK="/home/sfkilvrs/3dprinthub-deploy-backups/20260902-211013-phase49-3i53"
PRE_MIGRATION_BACKUP="/home/sfkilvrs/3dprinthub-deploy-backups/20260902-212529-phase49-3i53-resume"
TARGET_SHA="${1:-}"

BACKUP_BASE="/home/sfkilvrs/3dprinthub-deploy-backups"
STAMP="$(date +%Y%m%d-%H%M%S)"
PARTIAL_BACKUP="$BACKUP_BASE/${STAMP}-phase49-3i53g-partial"

fail() {
    printf 'PARTIAL_RECOVERY_FAIL=%s\n' "$1" >&2
    printf 'FULL_ROLLBACK=%s\n' "$FULL_ROLLBACK" >&2
    printf 'PRE_MIGRATION_BACKUP=%s\n' "$PRE_MIGRATION_BACKUP" >&2
    printf 'PARTIAL_BACKUP=%s\n' "$PARTIAL_BACKUP" >&2
    exit 1
}

printf '%s\n' "============================================================"
printf '%s\n' "3DPrintHub Phase49.3I.53G MySQL Partial Migration Recovery"
printf '%s\n' "audit partial 0039 -> fresh backup -> corrected migration -> verify"
printf '%s\n' "============================================================"

[ -n "$TARGET_SHA" ] || fail "target_sha_required"
[ -d "$ROOT/.git" ] || fail "project_root_or_git_missing"
[ -x "$PY" ] || fail "production_python_missing"

cd "$ROOT"

ORIGIN="$(git remote get-url origin)"
CURRENT_BRANCH="$(git branch --show-current)"
CURRENT_HEAD="$(git rev-parse HEAD)"
STATUS="$(git status --porcelain --untracked-files=all)"

printf 'ORIGIN=%s\n' "$ORIGIN"
printf 'CURRENT_BRANCH=%s\n' "$CURRENT_BRANCH"
printf 'CURRENT_HEAD=%s\n' "$CURRENT_HEAD"
printf 'EXPECTED_CURRENT_HEAD=%s\n' "$EXPECTED_CURRENT_HEAD"

case "$ORIGIN" in
  *farazha2203/3dprinthub.git|*farazha2203/3dprinthub) ;;
  *) fail "wrong_repository" ;;
esac

[ "$CURRENT_BRANCH" = "$BRANCH" ] || fail "wrong_branch"
[ "$CURRENT_HEAD" = "$EXPECTED_CURRENT_HEAD" ] || fail "unexpected_current_head"
[ -z "$STATUS" ] || {
    printf '%s\n' "$STATUS"
    fail "production_worktree_dirty"
}

printf '%s\n' "===== REVERIFY PRE-MIGRATION ROLLBACKS ====="
[ -d "$FULL_ROLLBACK" ] || fail "full_rollback_missing"
[ -d "$PRE_MIGRATION_BACKUP" ] || fail "fresh_pre_migration_backup_missing"

git bundle verify "$FULL_ROLLBACK/source-before.bundle"
gzip -t "$FULL_ROLLBACK/database-before-3i53.sql.gz"
sha256sum -c "$FULL_ROLLBACK/source-bundle.sha256"
sha256sum -c "$FULL_ROLLBACK/database.sha256"
gzip -t "$PRE_MIGRATION_BACKUP/database-before-3i53.sql.gz"
sha256sum -c "$PRE_MIGRATION_BACKUP/database.sha256"
printf '%s\n' "PRE_MIGRATION_ROLLBACKS_REVERIFIED=YES"

printf '%s\n' "===== READ-ONLY PARTIAL MIGRATION FORENSICS ====="
"$PY" - "$EXPECTED_DB" <<'PY'
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from django.db import connection
from django.db.migrations.recorder import MigrationRecorder
from store.models import ProductVariant, StoreOrderItem
from store.phase39_models import MaterialColorOption

expected_db = sys.argv[1]
if connection.vendor != "mysql":
    raise SystemExit("PARTIAL_RECOVERY_FAIL=database_vendor_not_mysql")
if str(connection.settings_dict.get("NAME") or "") != expected_db:
    raise SystemExit("PARTIAL_RECOVERY_FAIL=database_name_mismatch")

applied = set(
    MigrationRecorder.Migration.objects.filter(
        app__in={"store", "website"}
    ).values_list("app", "name")
)

required_applied = {
    ("website", "0024_phase49_3i51_material_catalog_description"),
    ("store", "0037_phase50_professional_commerce_policy"),
    ("store", "0038_phase50_profile_matrix"),
}
required_pending = {
    ("store", "0039_phase50_filament_offer_pricing"),
    ("store", "0040_phase50_filament_offer_operations"),
    ("store", "0041_phase50_filament_visual_identity"),
    ("store", "0042_phase49_3i51_filament_registry_descriptions"),
}

missing_applied = sorted(required_applied - applied)
unexpected_applied = sorted(required_pending & applied)
print("PARTIAL_REQUIRED_APPLIED_MISSING=" + repr(missing_applied))
print("PARTIAL_UNEXPECTED_APPLIED=" + repr(unexpected_applied))
if missing_applied:
    raise SystemExit("PARTIAL_RECOVERY_FAIL=expected_partial_migrations_missing")
if unexpected_applied:
    raise SystemExit("PARTIAL_RECOVERY_FAIL=partial_migration_recorder_changed")

def columns(model):
    with connection.cursor() as cursor:
        desc = connection.introspection.get_table_description(
            cursor,
            model._meta.db_table,
        )
    return {str(item.name) for item in desc}

material_columns = columns(MaterialColorOption)
variant_columns = columns(ProductVariant)
order_columns = columns(StoreOrderItem)

material_expected = {
    "brand_name",
    "manufacturer_name",
    "roll_weight_grams",
    "stock_roll_count_snapshot",
    "purchase_price_per_roll",
    "sale_price_per_roll",
    "usd_price_per_roll",
    "usd_fx_rate_toman",
}
order_0039_columns = {
    "support_weight_grams",
    "filament_brand_name",
    "filament_manufacturer_name",
}

material_missing = sorted(material_expected - material_columns)
order_already_present = sorted(order_0039_columns & order_columns)
variant_support_present = "support_weight_grams" in variant_columns

print("PARTIAL_0039_MATERIAL_PRESENT=" + repr(sorted(material_expected & material_columns)))
print("PARTIAL_0039_MATERIAL_MISSING=" + repr(material_missing))
print("PRODUCTVARIANT_SUPPORT_WEIGHT_PRESENT=" + repr(variant_support_present))
print("STOREORDERITEM_0039_ALREADY_PRESENT=" + repr(order_already_present))

if material_missing:
    raise SystemExit("PARTIAL_RECOVERY_FAIL=unexpected_material_partial_shape")
if not variant_support_present:
    raise SystemExit("PARTIAL_RECOVERY_FAIL=0033_support_weight_column_missing")
if order_already_present:
    raise SystemExit("PARTIAL_RECOVERY_FAIL=0039_progressed_past_observed_failure")

print("PARTIAL_0039_FORENSICS=PASS")
PY

printf '%s\n' "===== CREATE PARTIAL-STATE MYSQL BACKUP ====="
mkdir -p "$PARTIAL_BACKUP"
chmod 700 "$PARTIAL_BACKUP"

PHASE49_BACKUP_ROOT="$PARTIAL_BACKUP" \
PHASE49_PROJECT_ROOT="$ROOT" \
"$PY" scripts/host/phase49_3i53_mysql_backup.py "$EXPECTED_DB"

gzip -t "$PARTIAL_BACKUP/database-before-3i53.sql.gz"
sha256sum "$PARTIAL_BACKUP/database-before-3i53.sql.gz" > "$PARTIAL_BACKUP/database.sha256"
sha256sum -c "$PARTIAL_BACKUP/database.sha256"
printf '%s\n' "PARTIAL_STATE_DB_BACKUP_VERIFIED=YES"

printf '%s\n' "===== VERIFY LIVE FIX TARGET ====="
REMOTE_LINE="$(git ls-remote origin "refs/heads/$BRANCH")"
[ -n "$REMOTE_LINE" ] || fail "remote_branch_missing"
REMOTE_SHA="$(printf '%s\n' "$REMOTE_LINE" | awk '{print $1}')"
printf 'REMOTE_SHA=%s\n' "$REMOTE_SHA"
[ "$REMOTE_SHA" = "$TARGET_SHA" ] || fail "target_not_live_github_head"

git fetch --no-tags origin "refs/heads/$BRANCH"
FETCHED="$(git rev-parse FETCH_HEAD)"
printf 'FETCHED=%s\n' "$FETCHED"
[ "$FETCHED" = "$TARGET_SHA" ] || fail "fetched_target_mismatch"
git merge-base --is-ancestor "$CURRENT_HEAD" "$FETCHED" || fail "target_not_fast_forward"

printf '%s\n' "===== VERIFY 0039 RECOVERY CONTRACT ====="
git show "$FETCHED:store/migrations/0039_phase50_filament_offer_pricing.py" |
    grep -F "class AddFieldIfMissing(migrations.AddField):" >/dev/null
git show "$FETCHED:store/migrations/0039_phase50_filament_offer_pricing.py" |
    grep -F "migrations.AlterField(" >/dev/null
git show "$FETCHED:store/migrations/0039_phase50_filament_offer_pricing.py" |
    grep -F 'name="support_weight_grams"' >/dev/null
printf '%s\n' "MIGRATION_0039_RECOVERY_CONTRACT=PASS"

printf '%s\n' "===== FF-ONLY SOURCE FIX ====="
git merge --ff-only "$FETCHED"
[ "$(git rev-parse HEAD)" = "$TARGET_SHA" ] || fail "source_fix_head_mismatch"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "worktree_dirty_after_source_fix"

printf '%s\n' "===== DJANGO / MODEL STATE CHECK ====="
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run

printf '%s\n' "===== VERIFY RECOVERY MIGRATION PLAN ====="
"$PY" - <<'PY'
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from django.db import connection
from django.db.migrations.executor import MigrationExecutor

expected = {
    ("store", "0039_phase50_filament_offer_pricing"),
    ("store", "0040_phase50_filament_offer_operations"),
    ("store", "0041_phase50_filament_visual_identity"),
    ("store", "0042_phase49_3i51_filament_registry_descriptions"),
}

executor = MigrationExecutor(connection)
plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
actual = {(migration.app_label, migration.name) for migration, backwards in plan}
backwards = [(migration.app_label, migration.name) for migration, backwards in plan if backwards]

print("RECOVERY_MIGRATION_PLAN=" + repr(sorted(actual)))
print("RECOVERY_MIGRATION_BACKWARDS=" + repr(backwards))

if backwards:
    raise SystemExit("PARTIAL_RECOVERY_FAIL=backwards_migration_in_plan")
if actual != expected:
    raise SystemExit(
        "PARTIAL_RECOVERY_FAIL=unexpected_recovery_migration_plan:"
        + repr(sorted(actual))
    )
PY
"$PY" manage.py migrate --plan

printf '%s\n' "===== MIGRATE CORRECTED CHAIN ====="
"$PY" manage.py migrate --noinput

printf '%s\n' "===== VERIFY FINAL MIGRATION / READINESS ====="
"$PY" - <<'PY'
import json
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from django.db.migrations.recorder import MigrationRecorder
from catalog_bridge.publish_readiness import publish_readiness

required = {
    ("website", "0024_phase49_3i51_material_catalog_description"),
    ("store", "0037_phase50_professional_commerce_policy"),
    ("store", "0038_phase50_profile_matrix"),
    ("store", "0039_phase50_filament_offer_pricing"),
    ("store", "0040_phase50_filament_offer_operations"),
    ("store", "0041_phase50_filament_visual_identity"),
    ("store", "0042_phase49_3i51_filament_registry_descriptions"),
}
applied = set(
    MigrationRecorder.Migration.objects.filter(
        app__in={"store", "website"}
    ).values_list("app", "name")
)
missing = sorted(required - applied)
print("FINAL_REQUIRED_MIGRATIONS_MISSING=" + repr(missing))
if missing:
    raise SystemExit("PARTIAL_RECOVERY_FAIL=final_migration_recorder_incomplete")

payload = publish_readiness()
print("READINESS=" + json.dumps(payload, ensure_ascii=False, sort_keys=True))
if payload.get("ready") is not True:
    raise SystemExit("PARTIAL_RECOVERY_FAIL=receiver_not_ready")
PY

printf '%s\n' "===== COLLECTSTATIC ====="
"$PY" manage.py collectstatic --noinput

printf '%s\n' "===== PASSENGER RESTART ====="
mkdir -p tmp
touch tmp/restart.txt
sleep 4

printf '%s\n' "===== POST-RESTART CHECK ====="
"$PY" manage.py check

printf '%s\n' "===== PUBLIC / BRIDGE VERIFY ====="
"$PY" - <<'PY'
import json
import os
from urllib import request
from urllib.error import HTTPError, URLError

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from django.conf import settings

base = "https://3dprinthub.ir"
token = str(getattr(settings, "CATALOG_BRIDGE_TOKEN", "") or "").strip()
if len(token) < 24:
    raise SystemExit("PARTIAL_RECOVERY_FAIL=bridge_token_missing")

def fetch(path, *, auth=False):
    headers = {
        "User-Agent": "3DPrintHub-Phase49.3I.53G-Verify/1.0",
        "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
    }
    if auth:
        headers["Authorization"] = "Bearer " + token
    req = request.Request(base + path, headers=headers)
    try:
        with request.urlopen(req, timeout=20) as response:
            return response.status, response.read(2_000_000)
    except HTTPError as exc:
        body = exc.read(5000)
        raise SystemExit(
            f"PARTIAL_RECOVERY_FAIL=http_{path}_{exc.code}:"
            + body.decode("utf-8", errors="replace")[-1000:]
        )
    except URLError as exc:
        raise SystemExit(f"PARTIAL_RECOVERY_FAIL=http_{path}_urlerror:{exc}")

home_status, _ = fetch("/")
store_status, _ = fetch("/store/")
health_status, health_body = fetch("/api/catalog-bridge/v1/health/", auth=True)
ready_status, ready_body = fetch("/api/catalog-bridge/v1/publish-readiness/", auth=True)

health = json.loads(health_body.decode("utf-8"))
ready = json.loads(ready_body.decode("utf-8"))

print("HOME_HTTP=" + str(home_status))
print("STORE_HTTP=" + str(store_status))
print("BRIDGE_HEALTH_HTTP=" + str(health_status))
print("PUBLISH_READINESS_HTTP=" + str(ready_status))
print("BRIDGE_HEALTH_STATUS=" + str(health.get("status")))
print("PUBLISH_READY=" + str(ready.get("ready")))
print("PUBLISH_BLOCKERS=" + repr(ready.get("blockers") or []))

if home_status != 200:
    raise SystemExit("PARTIAL_RECOVERY_FAIL=home_http_not_200")
if store_status != 200:
    raise SystemExit("PARTIAL_RECOVERY_FAIL=store_http_not_200")
if health_status != 200 or health.get("status") != "ok":
    raise SystemExit("PARTIAL_RECOVERY_FAIL=bridge_health_not_ok")
if ready_status != 200 or ready.get("ready") is not True:
    raise SystemExit("PARTIAL_RECOVERY_FAIL=publish_readiness_not_ready")
PY

printf '%s\n' "===== FINAL STATE ====="
printf 'FINAL_HEAD=%s\n' "$(git rev-parse HEAD)"
printf 'FINAL_WORKTREE=%s\n' "$(test -z "$(git status --porcelain --untracked-files=all)" && printf CLEAN || printf DIRTY)"
printf 'FULL_ROLLBACK=%s\n' "$FULL_ROLLBACK"
printf 'PRE_MIGRATION_BACKUP=%s\n' "$PRE_MIGRATION_BACKUP"
printf 'PARTIAL_BACKUP=%s\n' "$PARTIAL_BACKUP"
printf '%s\n' "PHASE49_3I53G_PARTIAL_MIGRATION_RECOVERY=PASS"
