#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
EXPECTED_DB="sfkilvrs_EmiAdmin_3dprinthub"
HOST_BRANCH="release/phase50-a2j-hero-20260915"
TARGET_BRANCH="release/phase50-a2z-unicode-media-hotfix-20260923"
EXPECTED_BASELINE="103f559c8a11c35495b4ac2a290d578c31c2a023"
TARGET_SHA="${1:-}"
BACKUP_ROOT="${2:-}"
TMP_DELTA="/tmp/3dprinthub-a2z-unicode-delta-$$.txt"
TMP_EXPECTED="/tmp/3dprinthub-a2z-unicode-expected-$$.txt"

cleanup() {
  rm -f "$TMP_DELTA" "$TMP_EXPECTED" 2>/dev/null || true
}
trap cleanup EXIT

fail() {
  printf 'A2Z_UNICODE_DEPLOY_FAIL=%s\n' "$1" >&2
  exit 1
}

[ -n "$TARGET_SHA" ] || fail "target_sha_required"
[ -n "$BACKUP_ROOT" ] || fail "backup_root_required"
cd "$ROOT"
[ -d .git ] || fail "project_git_missing"
[ "$(git branch --show-current)" = "$HOST_BRANCH" ] || fail "wrong_host_branch"
[ "$(git rev-parse HEAD)" = "$EXPECTED_BASELINE" ] || fail "host_baseline_changed"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "production_worktree_dirty"
case "$(git remote get-url origin)" in
  *farazha2203/3dprinthub.git|*farazha2203/3dprinthub) ;;
  *) fail "wrong_repository" ;;
esac

[ -d "$BACKUP_ROOT" ] || fail "backup_root_missing"
[ "$(cat "$BACKUP_ROOT/source-head.txt")" = "$EXPECTED_BASELINE" ] || fail "backup_source_head_mismatch"
[ -f "$BACKUP_ROOT/source-before.bundle.sha256" ] || fail "backup_source_sha_missing"
[ -f "$BACKUP_ROOT/database-before-3i53.sql.gz.sha256" ] || fail "backup_db_sha_missing"
[ -f "$BACKUP_ROOT/media-before.tar.gz.sha256" ] || fail "backup_media_sha_missing"
(
  cd "$BACKUP_ROOT"
  sha256sum -c source-before.bundle.sha256
  sha256sum -c database-before-3i53.sql.gz.sha256
  sha256sum -c media-before.tar.gz.sha256
  if [ -f env.sha256 ]; then sha256sum -c env.sha256; fi
)
git bundle verify "$BACKUP_ROOT/source-before.bundle" >/dev/null
gzip -t "$BACKUP_ROOT/database-before-3i53.sql.gz"
tar -tzf "$BACKUP_ROOT/media-before.tar.gz" >/dev/null
printf 'ROLLBACK_VERIFIED=YES\n'

"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
"$PY" - "$EXPECTED_DB" <<'PY'
import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from catalog_bridge.publish_readiness import publish_readiness
expected = sys.argv[1]
if connection.vendor != "mysql" or str(connection.settings_dict.get("NAME") or "") != expected:
    raise SystemExit("A2Z_UNICODE_DEPLOY_FAIL=database_identity_mismatch")
plan = MigrationExecutor(connection).migration_plan(
    MigrationExecutor(connection).loader.graph.leaf_nodes()
)
print("PRE_MIGRATION_PLAN_COUNT=" + str(len(plan)))
if plan:
    raise SystemExit("A2Z_UNICODE_DEPLOY_FAIL=pre_migration_plan_not_empty")
ready = publish_readiness()
print("PRE_PUBLISH_READY=" + repr(ready.get("ready")))
if ready.get("ready") is not True:
    raise SystemExit("A2Z_UNICODE_DEPLOY_FAIL=receiver_not_ready")
PY

REMOTE_SHA="$(git ls-remote origin "refs/heads/$TARGET_BRANCH" | awk '{print $1}')"
printf 'REMOTE_SHA=%s\n' "$REMOTE_SHA"
[ "$REMOTE_SHA" = "$TARGET_SHA" ] || fail "target_not_live_github_head"
git fetch --no-tags origin "refs/heads/$TARGET_BRANCH"
FETCHED="$(git rev-parse FETCH_HEAD)"
[ "$FETCHED" = "$TARGET_SHA" ] || fail "fetched_target_mismatch"
git merge-base --is-ancestor "$EXPECTED_BASELINE" "$FETCHED" || fail "target_not_fast_forward"

git diff --name-only "$EXPECTED_BASELINE" "$FETCHED" | sort > "$TMP_DELTA"
cat > "$TMP_EXPECTED" <<'EOF'
store/management/commands/phase37_import_catalog_center.py
store/phase34b_publishing.py
store/phase50_public_media_name.py
store/phase50_republish_contract.py
store/test_phase49_unified_import_e2e.py
EOF
sort -o "$TMP_EXPECTED" "$TMP_EXPECTED"
diff -u "$TMP_EXPECTED" "$TMP_DELTA" || fail "unexpected_target_delta"
if grep -Eq '(^|/)migrations/[0-9]{4}_[^/]+\.py$|^requirements[^/]*\.txt$|^config/settings' "$TMP_DELTA"; then
  fail "migration_dependency_or_settings_delta_detected"
fi
printf 'TARGET_DELTA_ALLOWLIST=PASS\n'

git merge --ff-only "$FETCHED"
[ "$(git rev-parse HEAD)" = "$TARGET_SHA" ] || fail "deployed_head_mismatch"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "worktree_dirty_after_merge"

"$PY" -m py_compile   store/phase50_public_media_name.py   store/phase34b_publishing.py   store/phase50_republish_contract.py   store/management/commands/phase37_import_catalog_center.py
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
"$PY" - "$EXPECTED_DB" <<'PY'
import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from catalog_bridge.publish_readiness import publish_readiness
from store.phase50_public_media_name import canonical_server_media_filename
expected = sys.argv[1]
if connection.vendor != "mysql" or str(connection.settings_dict.get("NAME") or "") != expected:
    raise SystemExit("A2Z_UNICODE_DEPLOY_FAIL=post_database_identity_mismatch")
plan = MigrationExecutor(connection).migration_plan(
    MigrationExecutor(connection).loader.graph.leaf_nodes()
)
print("POST_MIGRATION_PLAN_COUNT=" + str(len(plan)))
if plan:
    raise SystemExit("A2Z_UNICODE_DEPLOY_FAIL=post_migration_plan_not_empty")
ready = publish_readiness()
print("POST_PUBLISH_READY=" + repr(ready.get("ready")))
if ready.get("ready") is not True:
    raise SystemExit("A2Z_UNICODE_DEPLOY_FAIL=post_receiver_not_ready")
probe = canonical_server_media_filename(
    {"source_title": "Majestic Hydra | Voronoi Art Sculpture", "external_id": "3179519"},
    0,
    "\u0645\u062c\u0633\u0645\u0647-\u0647\u0646\u0631\u06cc.webp",
)
print("UNICODE_NAME_PROBE=" + probe)
if probe != "majestic-hydra-voronoi-art-sculpture-3d-print-01.webp":
    raise SystemExit("A2Z_UNICODE_DEPLOY_FAIL=unicode_name_probe_mismatch")
PY

mkdir -p tmp
touch tmp/restart.txt
sleep 4

"$PY" - <<'PY'
from urllib import request
urls = [
    "https://3dprinthub.ir/",
    "https://3dprinthub.ir/store/",
]
for url in urls:
    req = request.Request(
        url,
        headers={
            "User-Agent": "3DPrintHub-A2Z-Unicode/1.0",
            "Cache-Control": "no-cache",
        },
    )
    with request.urlopen(req, timeout=20) as response:
        print("HTTP", response.status, url)
        if response.status != 200:
            raise SystemExit("A2Z_UNICODE_DEPLOY_FAIL=public_http_smoke")
print("PUBLIC_SMOKE=PASS")
PY

printf 'FINAL_HEAD=%s\n' "$(git rev-parse HEAD)"
printf 'FINAL_WORKTREE=%s\n' "$(test -z "$(git status --porcelain --untracked-files=all)" && printf CLEAN || printf DIRTY)"
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"
printf 'PHASE50_A2Z_UNICODE_MEDIA_DEPLOY=PASS\n'
