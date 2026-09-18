#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
EXPECTED_DB="sfkilvrs_EmiAdmin_3dprinthub"
HOST_BRANCH="release/phase50-a2j-hero-20260915"
TARGET_BRANCH="release/phase50-a2l-owner-qa-20260918"
EXPECTED_BASELINE="16e24292d697e79bc6498d44826e191d6da57e23"
TARGET_SHA="${1:-}"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="/home/sfkilvrs/3dprinthub-deploy-backups/${STAMP}-phase50-a2l-product-hero"
TMP_DELTA="/tmp/3dprinthub-a2l-product-hero-$$.txt"

cleanup() { rm -f "$TMP_DELTA" 2>/dev/null || true; }
trap cleanup EXIT
fail() {
  printf 'A2L_PRODUCT_HERO_DEPLOY_FAIL=%s\n' "$1" >&2
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
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django; django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from catalog_bridge.publish_readiness import publish_readiness
expected = sys.argv[1]
print("DB_VENDOR=" + str(connection.vendor))
print("DB_NAME=" + str(connection.settings_dict.get("NAME") or ""))
if connection.vendor != "mysql" or str(connection.settings_dict.get("NAME") or "") != expected:
    raise SystemExit("A2L_PRODUCT_HERO_DEPLOY_FAIL=database_identity_mismatch")
plan = MigrationExecutor(connection).migration_plan(MigrationExecutor(connection).loader.graph.leaf_nodes())
print("MIGRATION_PLAN=" + repr([(m.app_label, m.name, b) for m, b in plan]))
if plan:
    raise SystemExit("A2L_PRODUCT_HERO_DEPLOY_FAIL=migration_plan_not_empty")
ready = publish_readiness()
print("PUBLISH_READY=" + repr(ready.get("ready")))
if ready.get("ready") is not True:
    raise SystemExit("A2L_PRODUCT_HERO_DEPLOY_FAIL=receiver_not_ready")
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
printf '%s\n' "===== PRODUCT HERO DELTA ====="
cat "$TMP_DELTA"
if grep -Eq '(^|/)migrations/[0-9]{4}_[^/]+\.py$|^requirements[^/]*\.txt$|^config/settings' "$TMP_DELTA"; then
  fail "migration_dependency_or_settings_delta_detected"
fi
grep -Fxq "website/views.py" "$TMP_DELTA" || fail "hero_view_delta_missing"
grep -Fxq "store/phase50_republish_contract.py" "$TMP_DELTA" || fail "republish_contract_delta_missing"
grep -Fxq "store/phase34b_publishing.py" "$TMP_DELTA" || fail "product_media_sync_delta_missing"
grep -Fxq "store/management/commands/phase37_import_catalog_center.py" "$TMP_DELTA" || fail "receiver_delta_missing"
mkdir -p "$BACKUP_ROOT/static-before"
chmod 700 "$BACKUP_ROOT"
git bundle create "$BACKUP_ROOT/source-before.bundle" HEAD
git bundle verify "$BACKUP_ROOT/source-before.bundle"
printf '%s\n' "$EXPECTED_BASELINE" > "$BACKUP_ROOT/source-head.txt"
printf '%s\n' "$HOST_BRANCH" > "$BACKUP_ROOT/source-branch.txt"
if [ -f .env ]; then
  cp -p .env "$BACKUP_ROOT/.env"
  chmod 600 "$BACKUP_ROOT/.env"
fi
for rel in   css/phase50-a2k-tympanus-slicebox.css   js/phase50-a2k-tympanus-slicebox.js; do
  if [ -f "/home/sfkilvrs/public_html/static/$rel" ]; then
    mkdir -p "$BACKUP_ROOT/static-before/$(dirname "$rel")"
    cp -p "/home/sfkilvrs/public_html/static/$rel" "$BACKUP_ROOT/static-before/$rel"
  fi
done
sha256sum "$BACKUP_ROOT/source-before.bundle" > "$BACKUP_ROOT/source-bundle.sha256"
if [ -f "$BACKUP_ROOT/.env" ]; then sha256sum "$BACKUP_ROOT/.env" > "$BACKUP_ROOT/env.sha256"; fi
(cd "$BACKUP_ROOT" && sha256sum -c source-bundle.sha256 && if [ -f env.sha256 ]; then sha256sum -c env.sha256; fi)
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"
printf '%s\n' "PREDEPLOY_BACKUP_VERIFIED=YES"

git merge --ff-only "$FETCHED"
[ "$(git rev-parse HEAD)" = "$TARGET_SHA" ] || fail "deployed_head_mismatch"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "worktree_dirty_after_merge"
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run

OLD_UMASK="$(umask)"
umask 022
"$PY" manage.py collectstatic --noinput
umask "$OLD_UMASK"
chmod 755 /home/sfkilvrs/public_html/static/vendor /home/sfkilvrs/public_html/static/vendor/slicebox
find /home/sfkilvrs/public_html/static/vendor/slicebox -type d -exec chmod 755 {} +
find /home/sfkilvrs/public_html/static/vendor/slicebox -type f -exec chmod 644 {} +

for rel in   css/phase50-a2k-tympanus-slicebox.css   js/phase50-a2k-tympanus-slicebox.js   vendor/slicebox/js/jquery.slicebox.js; do
  [ -f "static/$rel" ] || fail "source_static_missing:$rel"
  [ -f "/home/sfkilvrs/public_html/static/$rel" ] || fail "collected_static_missing:$rel"
  SOURCE_SHA="$(sha256sum "static/$rel" | awk '{print $1}')"
  PUBLIC_SHA="$(sha256sum "/home/sfkilvrs/public_html/static/$rel" | awk '{print $1}')"
  printf 'STATIC_SHA %s source=%s public=%s\n' "$rel" "$SOURCE_SHA" "$PUBLIC_SHA"
  [ "$SOURCE_SHA" = "$PUBLIC_SHA" ] || fail "static_hash_mismatch:$rel"
done

grep -Fq 'max-width: 1280px' static/css/phase50-a2k-tympanus-slicebox.css || fail "larger_hero_contract_missing"
grep -Fq 'p50k-slicebox__product-copy' templates/website/partials/hero.html || fail "hero_product_link_contract_missing"
grep -Fq 'REPUBLISH_PARITY_MISMATCH' store/management/commands/phase37_import_catalog_center.py || fail "republish_fail_closed_contract_missing"

"$PY" - <<'PY'
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django; django.setup()
from website.models import HomepageHeroSlide

base = (
    HomepageHeroSlide.objects.filter(is_active=True, asset__isnull=False)
    .exclude(asset__editorial_status__in=("rejected", "archived", "license_review"))
    .select_related("asset", "asset__product")
    .order_by("sort_order", "id")
)
products = list(base.filter(asset__product__is_active=True))
fallback = list(base.filter(
    asset__product__isnull=True,
    asset__commercial_license_status__in=("allowed", "owned", "public_domain"),
))
print("ACTIVE_PRODUCT_HERO_COUNT=" + str(len(products)))
print("ACTIVE_SOURCE_FALLBACK_COUNT=" + str(len(fallback)))
if products:
    urls = [str(s.effective_image_url or "") for s in products]
    print("PRODUCT_HERO_URLS=" + repr(urls))
    if not all(getattr(s.asset, "product_id", None) for s in products):
        raise SystemExit("A2L_PRODUCT_HERO_DEPLOY_FAIL=product_slide_identity_missing")
    if any("makerworld.bblmw.com" in u for u in urls):
        raise SystemExit("A2L_PRODUCT_HERO_DEPLOY_FAIL=product_hero_still_external")
else:
    print("PRODUCT_HERO_FALLBACK_MODE=YES")
PY

mkdir -p tmp
touch tmp/restart.txt
sleep 4
"$PY" - <<'PY'
from urllib import request
url = "https://3dprinthub.ir/"
with request.urlopen(request.Request(url, headers={"User-Agent":"3DPrintHub-A2L-Hero-Verify/1.0","Cache-Control":"no-cache"}), timeout=20) as r:
    body = r.read(3_000_000)
    print("HOME_HTTP=" + str(r.status))
    if r.status != 200:
        raise SystemExit("A2L_PRODUCT_HERO_DEPLOY_FAIL=home_not_200")
    for marker in (b"data-p50k-slicebox", b"phase50-a2k-tympanus-slicebox.js", b"jquery.slicebox.js"):
        if marker not in body:
            raise SystemExit("A2L_PRODUCT_HERO_DEPLOY_FAIL=hero_marker_missing")
print("A2L_PRODUCT_HERO_PUBLIC_HTTP=PASS")
PY

printf 'FINAL_HEAD=%s\n' "$(git rev-parse HEAD)"
printf 'FINAL_WORKTREE=%s\n' "$(test -z "$(git status --porcelain --untracked-files=all)" && printf CLEAN || printf DIRTY)"
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"
printf '%s\n' "PHASE50_A2L_PRODUCT_HERO_DEPLOY=PASS"
