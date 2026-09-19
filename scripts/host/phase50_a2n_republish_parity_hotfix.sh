#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
EXPECTED_DB="sfkilvrs_EmiAdmin_3dprinthub"
HOST_BRANCH="release/phase50-a2j-hero-20260915"
TARGET_BRANCH="release/phase50-a2l-owner-qa-20260918"
EXPECTED_BASELINE="6f55e0341f3e2ed747421be85cbff218e4fc973e"
TARGET_SHA="${1:-}"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="/home/sfkilvrs/3dprinthub-deploy-backups/${STAMP}-phase50-a2n-republish-parity-hotfix"
TMP_DELTA="/tmp/3dprinthub-a2n-parity-$$.txt"

cleanup(){ rm -f "$TMP_DELTA" 2>/dev/null || true; }
trap cleanup EXIT
fail(){ printf 'A2N_PARITY_HOTFIX_FAIL=%s\n' "$1" >&2; printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT" >&2; exit 1; }

[ -n "$TARGET_SHA" ] || fail "target_sha_required"
cd "$ROOT"
[ -d .git ] || fail "project_git_missing"
[ "$(git branch --show-current)" = "$HOST_BRANCH" ] || fail "wrong_host_branch"
[ "$(git rev-parse HEAD)" = "$EXPECTED_BASELINE" ] || fail "host_baseline_changed"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "production_worktree_dirty"
case "$(git remote get-url origin)" in *farazha2203/3dprinthub.git|*farazha2203/3dprinthub) ;; *) fail "wrong_repository" ;; esac

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
if connection.vendor!="mysql" or str(connection.settings_dict.get("NAME") or "")!=expected:
    raise SystemExit("A2N_PARITY_HOTFIX_FAIL=database_identity_mismatch")
plan=MigrationExecutor(connection).migration_plan(MigrationExecutor(connection).loader.graph.leaf_nodes())
print("MIGRATION_PLAN="+repr([(m.app_label,m.name,b) for m,b in plan]))
if plan: raise SystemExit("A2N_PARITY_HOTFIX_FAIL=migration_plan_not_empty")
ready=publish_readiness()
print("PUBLISH_READY="+repr(ready.get("ready")))
if ready.get("ready") is not True: raise SystemExit("A2N_PARITY_HOTFIX_FAIL=receiver_not_ready")
PY

REMOTE_SHA="$(git ls-remote origin "refs/heads/$TARGET_BRANCH" | awk '{print $1}')"
printf 'REMOTE_SHA=%s\n' "$REMOTE_SHA"
[ "$REMOTE_SHA" = "$TARGET_SHA" ] || fail "target_not_live_github_head"
git fetch --no-tags origin "refs/heads/$TARGET_BRANCH"
FETCHED="$(git rev-parse FETCH_HEAD)"
[ "$FETCHED" = "$TARGET_SHA" ] || fail "fetched_target_mismatch"
git merge-base --is-ancestor "$EXPECTED_BASELINE" "$FETCHED" || fail "target_not_fast_forward"
git diff --name-only "$EXPECTED_BASELINE" "$FETCHED" > "$TMP_DELTA"
cat "$TMP_DELTA"
if grep -Eq '(^|/)migrations/[0-9]{4}_[^/]+\.py$|^requirements[^/]*\.txt$|^config/settings' "$TMP_DELTA"; then
  fail "migration_dependency_or_settings_delta_detected"
fi
grep -Fxq "store/phase50_republish_contract.py" "$TMP_DELTA" || fail "parity_source_missing"
grep -Fxq "scripts/host/phase50_a2n_republish_parity_hotfix.sh" "$TMP_DELTA" || fail "runner_missing"

mkdir -p "$BACKUP_ROOT"
chmod 700 "$BACKUP_ROOT"
git bundle create "$BACKUP_ROOT/source-before.bundle" HEAD
git bundle verify "$BACKUP_ROOT/source-before.bundle"
printf '%s\n' "$EXPECTED_BASELINE" > "$BACKUP_ROOT/source-head.txt"
printf '%s\n' "$HOST_BRANCH" > "$BACKUP_ROOT/source-branch.txt"
if [ -f .env ]; then cp -p .env "$BACKUP_ROOT/.env"; chmod 600 "$BACKUP_ROOT/.env"; fi
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

git merge --ff-only "$FETCHED"
[ "$(git rev-parse HEAD)" = "$TARGET_SHA" ] || fail "deployed_head_mismatch"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "worktree_dirty_after_merge"
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
grep -Fq '0 if expected_profiles else expected_min' store/phase50_republish_contract.py || fail "profile_fixed_price_parity_marker_missing"
"$PY" manage.py test store.test_phase50_profile_matrix.Phase50ProfileMatrixTests.test_republish_contract_accepts_profile_range_with_zero_product_fixed_price --verbosity 1

mkdir -p tmp
touch tmp/restart.txt
sleep 4
"$PY" - <<'PY'
from urllib import request
for url in (
    "https://3dprinthub.ir/",
    "https://3dprinthub.ir/store/",
    "https://3dprinthub.ir/store/product/mini-articulated-skeletal-spinosaurus/",
):
    with request.urlopen(request.Request(url,headers={"User-Agent":"3DPrintHub-A2N-Parity/1.0","Cache-Control":"no-cache"}),timeout=20) as r:
        print("HTTP",r.status,url)
        if r.status != 200:
            raise SystemExit("A2N_PARITY_HOTFIX_FAIL=http_smoke_failed")
print("PUBLIC_SMOKE=PASS")
PY

printf 'FINAL_HEAD=%s\n' "$(git rev-parse HEAD)"
printf 'FINAL_WORKTREE=%s\n' "$(test -z "$(git status --porcelain --untracked-files=all)" && printf CLEAN || printf DIRTY)"
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"
printf 'PHASE50_A2N_REPUBLISH_PARITY_HOTFIX=PASS\n'
