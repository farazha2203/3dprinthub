#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
BRANCH="agent/phase49-3i18-operator-bulk-ai-rebuild"
EXPECTED_DB="sfkilvrs_EmiAdmin_3dprinthub"
TARGET_SHA="${1:-}"
EXPECTED_PROD_HEAD="${2:-}"

fail() {
    printf 'AUDIT_FAIL=%s\n' "$1" >&2
    exit 1
}

printf '%s\n' "============================================================"
printf '%s\n' "3DPrintHub Phase49.3I.53 Production Read-Only Audit"
printf '%s\n' "NO FETCH / NO MERGE / NO MIGRATE / NO COLLECTSTATIC / NO RESTART"
printf '%s\n' "============================================================"

[ -n "$TARGET_SHA" ] || fail "target_sha_required"
[ -n "$EXPECTED_PROD_HEAD" ] || fail "expected_production_head_required"
[ -d "$ROOT/.git" ] || fail "project_root_or_git_missing"
[ -x "$PY" ] || fail "production_python_missing"

cd "$ROOT"

ORIGIN="$(git remote get-url origin)"
CURRENT_BRANCH="$(git branch --show-current)"
CURRENT_HEAD="$(git rev-parse HEAD)"
STATUS="$(git status --porcelain --untracked-files=all)"

printf 'ROOT=%s\n' "$ROOT"
printf 'ORIGIN=%s\n' "$ORIGIN"
printf 'CURRENT_BRANCH=%s\n' "$CURRENT_BRANCH"
printf 'CURRENT_HEAD=%s\n' "$CURRENT_HEAD"
printf 'EXPECTED_PROD_HEAD=%s\n' "$EXPECTED_PROD_HEAD"
printf 'TARGET_SHA=%s\n' "$TARGET_SHA"

case "$ORIGIN" in
  *farazha2203/3dprinthub.git|*farazha2203/3dprinthub) ;;
  *) fail "wrong_repository" ;;
esac

[ -z "$STATUS" ] || {
    printf '%s\n' "$STATUS"
    fail "production_worktree_dirty"
}

[ "$CURRENT_HEAD" = "$EXPECTED_PROD_HEAD" ] || fail "production_head_changed_from_verified_baseline"

REMOTE_LINE="$(git ls-remote origin "refs/heads/$BRANCH")"
[ -n "$REMOTE_LINE" ] || fail "remote_branch_not_found"
REMOTE_SHA="$(printf '%s\n' "$REMOTE_LINE" | awk '{print $1}')"

printf 'REMOTE_TARGET=%s\n' "$REMOTE_SHA"
[ "$REMOTE_SHA" = "$TARGET_SHA" ] || fail "target_sha_is_not_live_github_head"

printf '%s\n' "===== RUNTIME ====="
"$PY" --version
"$PY" - <<'PY'
import django
print("DJANGO_VERSION=" + django.get_version())
PY

printf '%s\n' "===== DJANGO READ-ONLY CHECKS ====="
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
"$PY" manage.py showmigrations store website
"$PY" manage.py migrate --plan

printf '%s\n' "===== EFFECTIVE DATABASE / STORAGE / RECEIVER STATE ====="
"$PY" - "$EXPECTED_DB" <<'PY'
import os
import sys
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from django.conf import settings
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder
from store.models import PrintQuality
from website.models import Material

expected_db = sys.argv[1]
db_name = str(connection.settings_dict.get("NAME") or "")
vendor = str(connection.vendor or "")

print("DB_VENDOR=" + vendor)
print("DB_NAME=" + db_name)
print("DB_NAME_EXPECTED=" + expected_db)
print("DB_VENDOR_OK=" + str(vendor == "mysql"))
print("DB_NAME_OK=" + str(db_name == expected_db))

if vendor != "mysql":
    raise SystemExit("AUDIT_FAIL=database_vendor_not_mysql")
if db_name != expected_db:
    raise SystemExit("AUDIT_FAIL=database_name_mismatch")

paths = {
    "STATIC_ROOT": Path(settings.STATIC_ROOT),
    "MEDIA_ROOT": Path(settings.MEDIA_ROOT),
    "PRIVATE_MEDIA_ROOT": Path(settings.PRIVATE_MEDIA_ROOT),
    "CATALOG_BRIDGE_PENDING_ROOT": Path(settings.CATALOG_BRIDGE_PENDING_ROOT),
}
for name, path in paths.items():
    print(f"{name}={path}")
    print(f"{name}_EXISTS={path.exists()}")
    print(f"{name}_READABLE={os.access(path, os.R_OK | os.X_OK) if path.exists() else False}")
    print(f"{name}_WRITABLE={os.access(path, os.W_OK | os.X_OK) if path.exists() else False}")
    print(f"{name}_PARENT_WRITABLE={path.parent.is_dir() and os.access(path.parent, os.W_OK | os.X_OK)}")

token = str(getattr(settings, "CATALOG_BRIDGE_TOKEN", "") or "")
print("BRIDGE_TOKEN_CONFIGURED=" + str(len(token) >= 24))
print("BRIDGE_TOKEN_LENGTH=" + str(len(token)))

required = (
    ("store", "0036_phase50_checkout_snapshot"),
    ("store", "0037_phase50_professional_commerce_policy"),
    ("store", "0038_phase50_profile_matrix"),
    ("store", "0039_phase50_filament_offer_pricing"),
    ("store", "0040_phase50_filament_offer_operations"),
    ("store", "0041_phase50_filament_visual_identity"),
    ("website", "0024_phase49_3i51_material_catalog_description"),
    ("store", "0042_phase49_3i51_filament_registry_descriptions"),
)
applied = set(
    MigrationRecorder.Migration.objects.filter(
        app__in={"store", "website"}
    ).values_list("app", "name")
)
for app, name in required:
    print(f"MIGRATION_{app}_{name}=" + ("APPLIED" if (app, name) in applied else "PENDING"))

print("ACTIVE_MATERIALS=" + str(Material.objects.filter(is_active=True).count()))
print("ACTIVE_PRINT_QUALITIES=" + str(PrintQuality.objects.filter(is_active=True).count()))

with connection.cursor() as cursor:
    tables = set(connection.introspection.table_names(cursor))
    checks = {
        "store_materialcoloroption": {
            "brand_name", "sale_price_per_roll", "print_hourly_rate",
            "color_finish", "description",
        },
        "store_productvariant": {
            "sales_profile_description", "part_length_cm", "support_weight_grams",
        },
        "website_material": {"catalog_description"},
        "store_filamentbrand": {"id", "name", "description", "is_active"},
    }
    for table, required_columns in checks.items():
        if table not in tables:
            print(f"SCHEMA_{table}=MISSING_TABLE")
            continue
        columns = {
            str(col.name)
            for col in connection.introspection.get_table_description(cursor, table)
        }
        missing = sorted(required_columns - columns)
        print(
            f"SCHEMA_{table}="
            + ("READY" if not missing else "MISSING_COLUMNS:" + ",".join(missing))
        )
PY

printf '%s\n' "===== DISK / INODES ====="
df -h "$ROOT" /home/sfkilvrs/public_html 2>/dev/null || df -h "$ROOT"
df -i "$ROOT" /home/sfkilvrs/public_html 2>/dev/null || df -i "$ROOT"

printf '%s\n' "===== BACKUP TOOL ====="
if command -v mysqldump >/dev/null 2>&1; then
    mysqldump --version
    printf '%s\n' "MYSQLDUMP_AVAILABLE=YES"
else
    printf '%s\n' "MYSQLDUMP_AVAILABLE=NO"
fi

printf '%s\n' "PHASE49_3I53_PRODUCTION_READONLY_AUDIT=PASS"
printf '%s\n' "NO_PRODUCTION_CHANGE_PERFORMED=YES"
