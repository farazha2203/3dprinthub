#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
BRANCH="agent/phase49-3i18-operator-bulk-ai-rebuild"
EXPECTED_DB="sfkilvrs_EmiAdmin_3dprinthub"
EXPECTED_BASELINE="198fa8e41ea4f4d87eb287ba69c91076acc78d62"
TARGET_SHA="${1:-}"

BACKUP_BASE="/home/sfkilvrs/3dprinthub-deploy-backups"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="$BACKUP_BASE/${STAMP}-phase49-3i53"
TMP_EXPECTED="/tmp/3dprinthub-3i53-expected-migrations-$$.txt"
TMP_ACTUAL="/tmp/3dprinthub-3i53-actual-migrations-$$.txt"

cleanup() {
    rm -f "$TMP_EXPECTED" "$TMP_ACTUAL" 2>/dev/null || true
}
trap cleanup EXIT

fail() {
    printf 'DEPLOY_FAIL=%s\n' "$1" >&2
    printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT" >&2
    exit 1
}

printf '%s\n' "============================================================"
printf '%s\n' "3DPrintHub Phase49.3I.53C Production Deploy"
printf '%s\n' "GitHub -> verified backup -> ff-only -> migrate -> static -> restart -> verify"
printf '%s\n' "============================================================"

[ -n "$TARGET_SHA" ] || fail "target_sha_required"
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
printf 'EXPECTED_BASELINE=%s\n' "$EXPECTED_BASELINE"
printf 'TARGET_SHA=%s\n' "$TARGET_SHA"

case "$ORIGIN" in
  *farazha2203/3dprinthub.git|*farazha2203/3dprinthub) ;;
  *) fail "wrong_repository" ;;
esac

[ "$CURRENT_BRANCH" = "$BRANCH" ] || fail "wrong_branch"
[ "$CURRENT_HEAD" = "$EXPECTED_BASELINE" ] || fail "host_baseline_changed"
[ -z "$STATUS" ] || {
    printf '%s\n' "$STATUS"
    fail "production_worktree_dirty"
}

printf '%s\n' "===== VERIFY LIVE TARGET ====="
REMOTE_LINE="$(git ls-remote origin "refs/heads/$BRANCH")"
[ -n "$REMOTE_LINE" ] || fail "remote_branch_missing"
REMOTE_SHA="$(printf '%s\n' "$REMOTE_LINE" | awk '{print $1}')"
printf 'REMOTE_SHA=%s\n' "$REMOTE_SHA"
[ "$REMOTE_SHA" = "$TARGET_SHA" ] || fail "target_not_live_github_head"

printf '%s\n' "===== FETCH EXACT TARGET ====="
git fetch --no-tags origin "refs/heads/$BRANCH"
FETCHED="$(git rev-parse FETCH_HEAD)"
printf 'FETCHED=%s\n' "$FETCHED"
[ "$FETCHED" = "$TARGET_SHA" ] || fail "fetched_target_mismatch"
git merge-base --is-ancestor "$EXPECTED_BASELINE" "$FETCHED" || fail "target_not_fast_forward"

printf '%s\n' "===== VERIFY MIGRATION FILE DELTA ====="
cat > "$TMP_EXPECTED" <<'EOF'
store/migrations/0037_phase50_professional_commerce_policy.py
store/migrations/0038_phase50_profile_matrix.py
store/migrations/0039_phase50_filament_offer_pricing.py
store/migrations/0040_phase50_filament_offer_operations.py
store/migrations/0041_phase50_filament_visual_identity.py
store/migrations/0042_phase49_3i51_filament_registry_descriptions.py
website/migrations/0024_phase49_3i51_material_catalog_description.py
EOF

git diff --name-only "$EXPECTED_BASELINE" "$FETCHED" --     '*/migrations/*.py' |
    grep -E '/migrations/[0-9]{4}_[^/]+\.py$' |
    sort > "$TMP_ACTUAL"

sort -o "$TMP_EXPECTED" "$TMP_EXPECTED"

printf '%s\n' "--- expected migration files ---"
cat "$TMP_EXPECTED"
printf '%s\n' "--- actual migration files ---"
cat "$TMP_ACTUAL"

diff -u "$TMP_EXPECTED" "$TMP_ACTUAL" || fail "migration_file_delta_unexpected"

printf '%s\n' "===== VERIFY BASELINE DATABASE STATE ====="
"$PY" - "$EXPECTED_DB" <<'PY'
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from django.db import connection
from django.db.migrations.recorder import MigrationRecorder

expected_db = sys.argv[1]
db_name = str(connection.settings_dict.get("NAME") or "")
vendor = str(connection.vendor or "")

print("DB_VENDOR=" + vendor)
print("DB_NAME=" + db_name)

if vendor != "mysql":
    raise SystemExit("DEPLOY_FAIL=database_vendor_not_mysql")
if db_name != expected_db:
    raise SystemExit("DEPLOY_FAIL=database_name_mismatch")

applied = set(
    MigrationRecorder.Migration.objects.filter(
        app__in={"store", "website"}
    ).values_list("app", "name")
)

must_be_applied = {
    ("store", "0036_phase50_checkout_snapshot"),
    ("website", "0023_phase49_3f_material_runtime_rates"),
}
must_be_pending = {
    ("store", "0037_phase50_professional_commerce_policy"),
    ("store", "0038_phase50_profile_matrix"),
    ("store", "0039_phase50_filament_offer_pricing"),
    ("store", "0040_phase50_filament_offer_operations"),
    ("store", "0041_phase50_filament_visual_identity"),
    ("store", "0042_phase49_3i51_filament_registry_descriptions"),
    ("website", "0024_phase49_3i51_material_catalog_description"),
}

missing_required = sorted(must_be_applied - applied)
unexpected_applied = sorted(must_be_pending & applied)

print("BASELINE_REQUIRED_MISSING=" + repr(missing_required))
print("BASELINE_UNEXPECTED_APPLIED=" + repr(unexpected_applied))

if missing_required:
    raise SystemExit("DEPLOY_FAIL=baseline_required_migration_missing")
if unexpected_applied:
    raise SystemExit("DEPLOY_FAIL=baseline_migration_state_changed")
PY

printf '%s\n' "===== PREDEPLOY DJANGO CHECK ====="
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run

printf '%s\n' "===== CREATE BACKUP ROOT ====="
mkdir -p "$BACKUP_ROOT"
chmod 700 "$BACKUP_ROOT"
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"

printf '%s\n' "===== SOURCE / ENVIRONMENT BACKUP ====="
git bundle create "$BACKUP_ROOT/source-before.bundle" HEAD
git bundle verify "$BACKUP_ROOT/source-before.bundle"

printf '%s\n' "$CURRENT_HEAD" > "$BACKUP_ROOT/source-head.txt"
printf '%s\n' "$CURRENT_BRANCH" > "$BACKUP_ROOT/source-branch.txt"

if [ -f ".env" ]; then
    cp -p ".env" "$BACKUP_ROOT/.env"
    chmod 600 "$BACKUP_ROOT/.env"
    sha256sum "$BACKUP_ROOT/.env" > "$BACKUP_ROOT/env.sha256"
else
    printf '%s\n' "ENV_FILE_PRESENT=NO" > "$BACKUP_ROOT/env-state.txt"
fi

if [ -d "imports/desktop_catalog/pending" ]; then
    tar -czf "$BACKUP_ROOT/pending-before-deploy.tgz"         imports/desktop_catalog/pending
    gzip -t "$BACKUP_ROOT/pending-before-deploy.tgz"
    sha256sum "$BACKUP_ROOT/pending-before-deploy.tgz" > "$BACKUP_ROOT/pending.sha256"
fi

printf '%s\n' "===== MYSQL BACKUP ====="
PHASE49_BACKUP_ROOT="$BACKUP_ROOT" "$PY" - "$EXPECTED_DB" <<'PY'
import gzip
import os
import shutil
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from django.db import connection

expected_db = sys.argv[1]
cfg = connection.settings_dict
if connection.vendor != "mysql":
    raise SystemExit("DEPLOY_FAIL=backup_database_vendor_not_mysql")
if str(cfg.get("NAME") or "") != expected_db:
    raise SystemExit("DEPLOY_FAIL=backup_database_name_mismatch")

binary = shutil.which("mysqldump")
if not binary:
    raise SystemExit("DEPLOY_FAIL=mysqldump_missing")

root = Path(os.environ["PHASE49_BACKUP_ROOT"])
outfile = root / "database-before-3i53.sql.gz"

cmd = [
    binary,
    "--single-transaction",
    "--quick",
    "--routines",
    "--triggers",
    "--no-tablespaces",
    "--default-character-set=utf8mb4",
    "-h", str(cfg.get("HOST") or "localhost"),
    "-P", str(cfg.get("PORT") or "3306"),
    "-u", str(cfg.get("USER") or ""),
    str(cfg.get("NAME") or ""),
]

env = os.environ.copy()
env["MYSQL_PWD"] = str(cfg.get("PASSWORD") or "")

with gzip.open(outfile, "wb", compresslevel=6) as target:
    proc = subprocess.run(
        cmd,
        stdout=target,
        stderr=subprocess.PIPE,
        env=env,
        check=False,
    )

if proc.returncode:
    try:
        outfile.unlink()
    except FileNotFoundError:
        pass
    raise SystemExit(
        "DEPLOY_FAIL=mysqldump_failed:"
        + proc.stderr.decode("utf-8", errors="replace")[-1200:]
    )

size = outfile.stat().st_size
print("DATABASE_BACKUP=" + str(outfile))
print("DATABASE_BACKUP_SIZE=" + str(size))
if size < 1024:
    raise SystemExit("DEPLOY_FAIL=database_backup_too_small")
PY

gzip -t "$BACKUP_ROOT/database-before-3i53.sql.gz"
sha256sum "$BACKUP_ROOT/database-before-3i53.sql.gz" > "$BACKUP_ROOT/database.sha256"
sha256sum "$BACKUP_ROOT/source-before.bundle" > "$BACKUP_ROOT/source-bundle.sha256"

printf '%s\n' "===== BACKUP MANIFEST ====="
(
    cd "$BACKUP_ROOT"
    sha256sum -c source-bundle.sha256
    sha256sum -c database.sha256
    if [ -f env.sha256 ]; then sha256sum -c env.sha256; fi
    if [ -f pending.sha256 ]; then sha256sum -c pending.sha256; fi
)

printf '%s\n' "PREDEPLOY_BACKUP_VERIFIED=YES"

printf '%s\n' "===== FF-ONLY DEPLOY FROM FETCH_HEAD ====="
git merge --ff-only "$FETCHED"
DEPLOYED_HEAD="$(git rev-parse HEAD)"
printf 'DEPLOYED_HEAD=%s\n' "$DEPLOYED_HEAD"
[ "$DEPLOYED_HEAD" = "$TARGET_SHA" ] || fail "deployed_head_mismatch"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "worktree_dirty_after_merge"

printf '%s\n' "===== POST-MERGE DJANGO CHECK ====="
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run

printf '%s\n' "===== VERIFY EXACT MIGRATION PLAN ====="
"$PY" - <<'PY'
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from django.db import connection
from django.db.migrations.executor import MigrationExecutor

expected = {
    ("store", "0037_phase50_professional_commerce_policy"),
    ("store", "0038_phase50_profile_matrix"),
    ("store", "0039_phase50_filament_offer_pricing"),
    ("store", "0040_phase50_filament_offer_operations"),
    ("store", "0041_phase50_filament_visual_identity"),
    ("store", "0042_phase49_3i51_filament_registry_descriptions"),
    ("website", "0024_phase49_3i51_material_catalog_description"),
}

executor = MigrationExecutor(connection)
plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
actual = {(migration.app_label, migration.name) for migration, backwards in plan}
backwards = [(migration.app_label, migration.name) for migration, backwards in plan if backwards]

print("MIGRATION_PLAN=" + repr(sorted(actual)))
print("MIGRATION_BACKWARDS=" + repr(backwards))

if backwards:
    raise SystemExit("DEPLOY_FAIL=backwards_migration_in_plan")
if actual != expected:
    raise SystemExit(
        "DEPLOY_FAIL=unexpected_migration_plan:"
        + repr(sorted(actual))
    )
PY

"$PY" manage.py migrate --plan

printf '%s\n' "===== MIGRATE APPROVED CHAIN ====="
"$PY" manage.py migrate --noinput

printf '%s\n' "===== VERIFY RECEIVER READINESS IN-PROCESS ====="
"$PY" - <<'PY'
import json
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from catalog_bridge.publish_readiness import publish_readiness

payload = publish_readiness()
print("READINESS=" + json.dumps(payload, ensure_ascii=False, sort_keys=True))
if payload.get("ready") is not True:
    raise SystemExit("DEPLOY_FAIL=receiver_not_ready_after_migrate")
PY

printf '%s\n' "===== COLLECTSTATIC ====="
"$PY" manage.py collectstatic --noinput

printf '%s\n' "===== PASSENGER RESTART ====="
mkdir -p tmp
touch tmp/restart.txt
sleep 4

printf '%s\n' "===== POST-RESTART DJANGO CHECK ====="
"$PY" manage.py check

printf '%s\n' "===== HTTP VERIFY ====="
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
    raise SystemExit("DEPLOY_FAIL=bridge_token_missing_after_restart")

def fetch(path, *, auth=False):
    headers = {
        "User-Agent": "3DPrintHub-Phase49.3I.53C-Verify/1.0",
        "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
    }
    if auth:
        headers["Authorization"] = "Bearer " + token
    req = request.Request(base + path, headers=headers)
    try:
        with request.urlopen(req, timeout=20) as response:
            body = response.read(2_000_000)
            return response.status, response.headers.get("Content-Type", ""), body
    except HTTPError as exc:
        body = exc.read(5000)
        raise SystemExit(
            f"DEPLOY_FAIL=http_{path}_{exc.code}:"
            + body.decode("utf-8", errors="replace")[-1000:]
        )
    except URLError as exc:
        raise SystemExit(f"DEPLOY_FAIL=http_{path}_urlerror:{exc}")

home_status, _home_type, _home_body = fetch("/")
store_status, _store_type, _store_body = fetch("/store/")
health_status, _health_type, health_body = fetch(
    "/api/catalog-bridge/v1/health/",
    auth=True,
)
ready_status, _ready_type, ready_body = fetch(
    "/api/catalog-bridge/v1/publish-readiness/",
    auth=True,
)

print("HOME_HTTP=" + str(home_status))
print("STORE_HTTP=" + str(store_status))
print("BRIDGE_HEALTH_HTTP=" + str(health_status))
print("PUBLISH_READINESS_HTTP=" + str(ready_status))

health = json.loads(health_body.decode("utf-8"))
ready = json.loads(ready_body.decode("utf-8"))

print("BRIDGE_HEALTH_STATUS=" + str(health.get("status")))
print("BRIDGE_VERSION=" + str(health.get("version")))
print("PUBLISH_READY=" + str(ready.get("ready")))
print("PUBLISH_BLOCKERS=" + repr(ready.get("blockers") or []))

if home_status != 200:
    raise SystemExit("DEPLOY_FAIL=home_http_not_200")
if store_status != 200:
    raise SystemExit("DEPLOY_FAIL=store_http_not_200")
if health_status != 200 or health.get("status") != "ok":
    raise SystemExit("DEPLOY_FAIL=bridge_health_not_ok")
if ready_status != 200 or ready.get("ready") is not True:
    raise SystemExit("DEPLOY_FAIL=publish_readiness_not_ready")
PY

printf '%s\n' "===== FINAL STATE ====="
printf 'FINAL_HEAD=%s\n' "$(git rev-parse HEAD)"
printf 'FINAL_WORKTREE=%s\n' "$(test -z "$(git status --porcelain --untracked-files=all)" && printf CLEAN || printf DIRTY)"
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"
printf '%s\n' "PHASE49_3I53C_PRODUCTION_DEPLOY=PASS"
