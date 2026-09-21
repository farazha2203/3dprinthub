#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
HOST_BRANCH="release/phase50-a2j-hero-20260915"
TARGET_BRANCH="release/phase50-a2l-owner-qa-20260918"
EXPECTED_BASELINE="c04539acfc6dd456699079edf206de019bf346e2"
TARGET_SHA="${1:-}"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="/home/sfkilvrs/3dprinthub-deploy-backups/${STAMP}-phase50-a2l-media-path-hotfix"
TMP_DELTA="/tmp/3dprinthub-a2l-media-path-$$.txt"

cleanup() { rm -f "$TMP_DELTA" 2>/dev/null || true; }
trap cleanup EXIT
fail() {
  printf 'A2L_MEDIA_PATH_HOTFIX_FAIL=%s\n' "$1" >&2
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

REMOTE_LINE="$(git ls-remote origin "refs/heads/$TARGET_BRANCH")"
REMOTE_SHA="$(printf '%s\n' "$REMOTE_LINE" | awk '{print $1}')"
printf 'REMOTE_SHA=%s\n' "$REMOTE_SHA"
[ "$REMOTE_SHA" = "$TARGET_SHA" ] || fail "target_not_live_github_head"
git fetch --no-tags origin "refs/heads/$TARGET_BRANCH"
FETCHED="$(git rev-parse FETCH_HEAD)"
[ "$FETCHED" = "$TARGET_SHA" ] || fail "fetched_target_mismatch"
git merge-base --is-ancestor "$EXPECTED_BASELINE" "$FETCHED" || fail "target_not_fast_forward"
git diff --name-only "$EXPECTED_BASELINE" "$FETCHED" > "$TMP_DELTA"
printf '%s\n' "===== MEDIA PATH HOTFIX DELTA ====="
cat "$TMP_DELTA"
if grep -Eq '(^|/)migrations/[0-9]{4}_[^/]+\.py$|^requirements[^/]*\.txt$|^config/settings' "$TMP_DELTA"; then
  fail "migration_dependency_or_settings_delta_detected"
fi
grep -Fxq "store/phase34b_publishing.py" "$TMP_DELTA" || fail "media_path_code_missing"
grep -Fxq "store/test_phase49_unified_import_e2e.py" "$TMP_DELTA" || fail "media_path_regression_missing"
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
printf 'PREDEPLOY_BACKUP_VERIFIED=YES\n'
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"

git merge --ff-only "$FETCHED"
[ "$(git rev-parse HEAD)" = "$TARGET_SHA" ] || fail "deployed_head_mismatch"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "worktree_dirty_after_merge"

"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
"$PY" - <<'PY'
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django; django.setup()
from store.models import Product, ProductImage
main_max = int(Product._meta.get_field("main_image").max_length or 100)
gallery_max = int(ProductImage._meta.get_field("image").max_length or 100)
name = "mini-articulated-skeletal-spinosaurus-3d-print-01.webp"
sample = f"p/625/{'a'*12}/{name}"
print("PRODUCT_MAIN_IMAGE_MAX=" + str(main_max))
print("PRODUCT_GALLERY_IMAGE_MAX=" + str(gallery_max))
print("REPRESENTATIVE_MEDIA_PATH_LENGTH=" + str(len(sample)))
if len(sample) > min(main_max, gallery_max):
    raise SystemExit("A2L_MEDIA_PATH_HOTFIX_FAIL=representative_path_exceeds_db_contract")
PY

mkdir -p tmp
touch tmp/restart.txt
sleep 4

"$PY" - <<'PY'
from urllib import request
url="https://3dprinthub.ir/store/product/mini-articulated-skeletal-spinosaurus/"
with request.urlopen(request.Request(url,headers={"User-Agent":"3DPrintHub-A2L-Media-Hotfix/1.0","Cache-Control":"no-cache"}),timeout=20) as r:
    body=r.read(2_000_000)
    print("PRODUCT39_PUBLIC_HTTP="+str(r.status))
    if r.status != 200 or b"mini-articulated-skeletal-spinosaurus" not in body:
        raise SystemExit("A2L_MEDIA_PATH_HOTFIX_FAIL=product39_public_smoke_failed")
PY

printf 'FINAL_HEAD=%s\n' "$(git rev-parse HEAD)"
printf 'FINAL_WORKTREE=%s\n' "$(test -z "$(git status --porcelain --untracked-files=all)" && printf CLEAN || printf DIRTY)"
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"
printf 'PHASE50_A2L_MEDIA_PATH_HOTFIX=PASS\n'
