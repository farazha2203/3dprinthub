#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
BRANCH="agent/phase49-3i18-operator-bulk-ai-rebuild"
EXPECTED_DB="sfkilvrs_EmiAdmin_3dprinthub"
EXPECTED_CURRENT_HEAD="b372586ab60234ec3faf3ce0624e07766db6ecce"
PREDEPLOY_BASELINE="198fa8e41ea4f4d87eb287ba69c91076acc78d62"
VERIFIED_BACKUP="/home/sfkilvrs/3dprinthub-deploy-backups/20260902-211013-phase49-3i53"
TARGET_SHA="${1:-}"

BACKUP_BASE="/home/sfkilvrs/3dprinthub-deploy-backups"
STAMP="$(date +%Y%m%d-%H%M%S)"
RESUME_ROOT="$BACKUP_BASE/${STAMP}-phase49-3i53-resume"

fail() {
    printf 'RESUME_FAIL=%s\n' "$1" >&2
    printf 'VERIFIED_BACKUP=%s\n' "$VERIFIED_BACKUP" >&2
    printf 'RESUME_ROOT=%s\n' "$RESUME_ROOT" >&2
    exit 1
}

printf '%s\n' "============================================================"
printf '%s\n' "3DPrintHub Phase49.3I.53F Post-Merge Production Recovery"
printf '%s\n' "verify rollback -> source boot fix -> dependency -> fresh backup -> migrate -> verify"
printf '%s\n' "============================================================"

[ -n "$TARGET_SHA" ] || fail "target_sha_required"
[ -d "$ROOT/.git" ] || fail "project_root_or_git_missing"
[ -x "$PY" ] || fail "production_python_missing"
[ -d "$VERIFIED_BACKUP" ] || fail "verified_predeploy_backup_missing"

cd "$ROOT"

ORIGIN="$(git remote get-url origin)"
CURRENT_BRANCH="$(git branch --show-current)"
CURRENT_HEAD="$(git rev-parse HEAD)"
STATUS="$(git status --porcelain --untracked-files=all)"

printf 'ORIGIN=%s\n' "$ORIGIN"
printf 'CURRENT_BRANCH=%s\n' "$CURRENT_BRANCH"
printf 'CURRENT_HEAD=%s\n' "$CURRENT_HEAD"
printf 'EXPECTED_CURRENT_HEAD=%s\n' "$EXPECTED_CURRENT_HEAD"
printf 'TARGET_SHA=%s\n' "$TARGET_SHA"

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

printf '%s\n' "===== VERIFY EXISTING PRE-MIGRATION ROLLBACK ====="
[ "$(cat "$VERIFIED_BACKUP/source-head.txt")" = "$PREDEPLOY_BASELINE" ] || fail "backup_source_head_mismatch"
git bundle verify "$VERIFIED_BACKUP/source-before.bundle"
gzip -t "$VERIFIED_BACKUP/database-before-3i53.sql.gz"
sha256sum -c "$VERIFIED_BACKUP/source-bundle.sha256"
sha256sum -c "$VERIFIED_BACKUP/database.sha256"
if [ -f "$VERIFIED_BACKUP/env.sha256" ]; then
    sha256sum -c "$VERIFIED_BACKUP/env.sha256"
fi
if [ -f "$VERIFIED_BACKUP/pending.sha256" ]; then
    sha256sum -c "$VERIFIED_BACKUP/pending.sha256"
fi
printf '%s\n' "PRE_MIGRATION_ROLLBACK_REVERIFIED=YES"

printf '%s\n' "===== VERIFY LIVE GITHUB TARGET ====="
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
git merge-base --is-ancestor "$CURRENT_HEAD" "$FETCHED" || fail "target_not_fast_forward"

printf '%s\n' "===== VERIFY BOOT-SAFETY FIX IN TARGET ====="
git show "$FETCHED:ai/model_policy.py" | grep -F 'def _provider_client(' >/dev/null
if git show "$FETCHED:ai/model_policy.py" | grep -F '^from catalog_center.app.ai_providers import AIProviderClient$' >/dev/null; then
    fail "eager_model_policy_transport_import_present"
fi
if git show "$FETCHED:ai/product_content.py" | grep -F '^from catalog_center.app.openai_content import AIContentService$' >/dev/null; then
    fail "eager_product_content_transport_import_present"
fi
printf '%s\n' "BOOT_SAFETY_FIX_PRESENT=YES"

printf '%s\n' "===== FF-ONLY SOURCE HOTFIX ====="
git merge --ff-only "$FETCHED"
[ "$(git rev-parse HEAD)" = "$TARGET_SHA" ] || fail "source_hotfix_head_mismatch"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "worktree_dirty_after_hotfix"

printf '%s\n' "===== BOOT CHECK WITHOUT HTTPX REQUIREMENT ====="
"$PY" manage.py check
printf '%s\n' "DJANGO_BOOT_SAFE_BEFORE_HTTPX=YES"

printf '%s\n' "===== PREPARE RESUME EVIDENCE ====="
mkdir -p "$RESUME_ROOT"
chmod 700 "$RESUME_ROOT"
"$PY" -m pip freeze > "$RESUME_ROOT/pip-freeze-before-httpx.txt"
sha256sum "$RESUME_ROOT/pip-freeze-before-httpx.txt" > "$RESUME_ROOT/pip-freeze-before-httpx.sha256"

if [ -f ".env" ]; then
    cp -p ".env" "$RESUME_ROOT/.env"
    chmod 600 "$RESUME_ROOT/.env"
    sha256sum "$RESUME_ROOT/.env" > "$RESUME_ROOT/env.sha256"
fi
if [ -d "imports/desktop_catalog/pending" ]; then
    tar -czf "$RESUME_ROOT/pending-before-migrate.tgz" imports/desktop_catalog/pending
    gzip -t "$RESUME_ROOT/pending-before-migrate.tgz"
    sha256sum "$RESUME_ROOT/pending-before-migrate.tgz" > "$RESUME_ROOT/pending.sha256"
fi

printf '%s\n' "===== INSTALL EXACT TARGET DEPENDENCY ====="
HTTPX_REQ="$(grep -E '^httpx==[0-9]+(\.[0-9]+){2}$' requirements.txt || true)"
[ "$HTTPX_REQ" = "httpx==0.28.1" ] || fail "unexpected_httpx_requirement"
"$PY" -m pip --version
"$PY" -m pip install --disable-pip-version-check --no-input "$HTTPX_REQ"
"$PY" -m pip check
"$PY" - <<'PY'
import httpx
version = str(httpx.__version__)
print("HTTPX_VERSION=" + version)
if version != "0.28.1":
    raise SystemExit("RESUME_FAIL=httpx_version_mismatch")
PY
"$PY" manage.py check
printf '%s\n' "TARGET_DEPENDENCIES_READY=YES"

printf '%s\n' "===== VERIFY DB STILL PRE-MIGRATION ====="
"$PY" - "$EXPECTED_DB" <<'PY'
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from django.db import connection
from django.db.migrations.recorder import MigrationRecorder

expected_db = sys.argv[1]
if connection.vendor != "mysql":
    raise SystemExit("RESUME_FAIL=database_vendor_not_mysql")
if str(connection.settings_dict.get("NAME") or "") != expected_db:
    raise SystemExit("RESUME_FAIL=database_name_mismatch")

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
missing = sorted(must_be_applied - applied)
unexpected = sorted(must_be_pending & applied)
print("BASELINE_REQUIRED_MISSING=" + repr(missing))
print("BASELINE_UNEXPECTED_APPLIED=" + repr(unexpected))
if missing:
    raise SystemExit("RESUME_FAIL=required_baseline_migration_missing")
if unexpected:
    raise SystemExit("RESUME_FAIL=migration_state_changed_since_backup")
PY

printf '%s\n' "===== CREATE FRESH PRE-MIGRATION MYSQL BACKUP ====="
PHASE49_BACKUP_ROOT="$RESUME_ROOT" \
PHASE49_PROJECT_ROOT="$ROOT" \
"$PY" scripts/host/phase49_3i53_mysql_backup.py "$EXPECTED_DB"
gzip -t "$RESUME_ROOT/database-before-3i53.sql.gz"
sha256sum "$RESUME_ROOT/database-before-3i53.sql.gz" > "$RESUME_ROOT/database.sha256"
sha256sum -c "$RESUME_ROOT/database.sha256"
printf '%s\n' "FRESH_PRE_MIGRATION_DB_BACKUP_VERIFIED=YES"

printf '%s\n' "===== VERIFY EXACT MIGRATION PLAN ====="
"$PY" manage.py makemigrations --check --dry-run
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
    raise SystemExit("RESUME_FAIL=backwards_migration_in_plan")
if actual != expected:
    raise SystemExit("RESUME_FAIL=unexpected_migration_plan:" + repr(sorted(actual)))
PY
"$PY" manage.py migrate --plan

printf '%s\n' "===== MIGRATE APPROVED CHAIN ====="
"$PY" manage.py migrate --noinput

printf '%s\n' "===== VERIFY RECEIVER READINESS ====="
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
    raise SystemExit("RESUME_FAIL=receiver_not_ready_after_migrate")
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
    raise SystemExit("RESUME_FAIL=bridge_token_missing")

def fetch(path, *, auth=False):
    headers = {
        "User-Agent": "3DPrintHub-Phase49.3I.53F-Verify/1.0",
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
            f"RESUME_FAIL=http_{path}_{exc.code}:"
            + body.decode("utf-8", errors="replace")[-1000:]
        )
    except URLError as exc:
        raise SystemExit(f"RESUME_FAIL=http_{path}_urlerror:{exc}")

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
    raise SystemExit("RESUME_FAIL=home_http_not_200")
if store_status != 200:
    raise SystemExit("RESUME_FAIL=store_http_not_200")
if health_status != 200 or health.get("status") != "ok":
    raise SystemExit("RESUME_FAIL=bridge_health_not_ok")
if ready_status != 200 or ready.get("ready") is not True:
    raise SystemExit("RESUME_FAIL=publish_readiness_not_ready")
PY

printf '%s\n' "===== FINAL STATE ====="
printf 'FINAL_HEAD=%s\n' "$(git rev-parse HEAD)"
printf 'FINAL_WORKTREE=%s\n' "$(test -z "$(git status --porcelain --untracked-files=all)" && printf CLEAN || printf DIRTY)"
printf 'ROLLBACK_BACKUP=%s\n' "$VERIFIED_BACKUP"
printf 'FRESH_DB_BACKUP=%s\n' "$RESUME_ROOT"
printf '%s\n' "PHASE49_3I53F_POSTMERGE_RECOVERY=PASS"
