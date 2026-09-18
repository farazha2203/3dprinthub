#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
TARGET_BRANCH="release/phase50-a2l-owner-qa-20260918"
HOST_BRANCH="release/phase50-a2j-hero-20260915"
EXPECTED_BASELINE="28cac45bf05b09a50fefcaccf3ae43541af022f2"
STATIC_ROOT="/home/sfkilvrs/public_html/static"
TARGET_SHA="${1:-}"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="/home/sfkilvrs/3dprinthub-deploy-backups/${STAMP}-phase50-a2l-vendor-static-permissions"

fail() {
  printf 'A2L_VENDOR_STATIC_HOTFIX_FAIL=%s\n' "$1" >&2
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

DELTA="$(git diff --name-only "$EXPECTED_BASELINE" "$FETCHED")"
printf '%s\n' "===== HOTFIX DELTA =====" "$DELTA"
if printf '%s\n' "$DELTA" | grep -Eq '(^|/)migrations/[0-9]{4}_[^/]+\.py$|^requirements[^/]*\.txt$|^config/settings'; then
  fail "migration_dependency_or_settings_delta_detected"
fi
mkdir -p "$BACKUP_ROOT"
chmod 700 "$BACKUP_ROOT"
git bundle create "$BACKUP_ROOT/source-before.bundle" HEAD
git bundle verify "$BACKUP_ROOT/source-before.bundle"
if [ -f .env ]; then
  cp -p .env "$BACKUP_ROOT/.env"
  chmod 600 "$BACKUP_ROOT/.env"
  sha256sum "$BACKUP_ROOT/.env" > "$BACKUP_ROOT/env.sha256"
fi
find "$STATIC_ROOT/vendor/slicebox" -maxdepth 3 -printf '%m %y %p\n' > "$BACKUP_ROOT/vendor-mode-before.txt"
find "$STATIC_ROOT/vendor/slicebox" -type f -print0 | sort -z | xargs -0 sha256sum > "$BACKUP_ROOT/vendor-content-before.sha256"
sha256sum "$BACKUP_ROOT/source-before.bundle" > "$BACKUP_ROOT/source-bundle.sha256"
(cd "$BACKUP_ROOT" && sha256sum -c source-bundle.sha256)
if [ -f "$BACKUP_ROOT/env.sha256" ]; then (cd "$BACKUP_ROOT" && sha256sum -c env.sha256); fi
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"
printf '%s\n' "PRE_HOTFIX_BACKUP_VERIFIED=YES"

git merge --ff-only "$FETCHED"
[ "$(git rev-parse HEAD)" = "$TARGET_SHA" ] || fail "deployed_head_mismatch"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "worktree_dirty_after_merge"
[ -d "$STATIC_ROOT/vendor/slicebox" ] || fail "vendor_slicebox_directory_missing"
chmod 755 "$STATIC_ROOT/vendor" "$STATIC_ROOT/vendor/slicebox"
find "$STATIC_ROOT/vendor/slicebox" -type d -exec chmod 755 {} +
find "$STATIC_ROOT/vendor/slicebox" -type f -exec chmod 644 {} +
find "$STATIC_ROOT/vendor/slicebox" -maxdepth 3 -printf '%m %y %p\n' > "$BACKUP_ROOT/vendor-mode-after.txt"

while read -r hash file; do
  current="$(sha256sum "$file" | awk '{print $1}')"
  [ "$current" = "$hash" ] || fail "vendor_content_hash_changed:$file"
done < "$BACKUP_ROOT/vendor-content-before.sha256"

"$PY" - <<'PY'
from urllib import request
checks = {
    "/static/vendor/slicebox/css/slicebox.css": ("text/css", b".sb-slider"),
    "/static/vendor/slicebox/js/jquery-3.7.1.min.js": ("javascript", b"jQuery"),
    "/static/vendor/slicebox/js/jquery.slicebox.js": ("javascript", b"slicebox"),
    "/static/vendor/slicebox/js/modernizr.custom.46884.js": ("javascript", b"Modernizr"),
}
for path, (ctype_marker, body_marker) in checks.items():
    with request.urlopen("https://3dprinthub.ir" + path, timeout=20) as r:
        ctype = str(r.headers.get("Content-Type") or "").lower()
        body = r.read(300000)
        print(path, r.status, ctype)
        if r.status != 200 or ctype_marker not in ctype or body_marker not in body:
            raise SystemExit("A2L_VENDOR_STATIC_HOTFIX_FAIL=public_vendor_asset_invalid:" + path)
print("VENDOR_STATIC_PUBLIC_VERIFY=PASS")
PY
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run

printf 'FINAL_HEAD=%s\n' "$(git rev-parse HEAD)"
printf 'FINAL_WORKTREE=%s\n' "$(test -z "$(git status --porcelain --untracked-files=all)" && printf CLEAN || printf DIRTY)"
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"
printf '%s\n' "PHASE50_A2L_VENDOR_STATIC_HOTFIX=PASS"
