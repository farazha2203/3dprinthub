#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
EXPECTED_DB="sfkilvrs_EmiAdmin_3dprinthub"
HOST_BRANCH="release/phase50-a2j-hero-20260915"
TARGET_BRANCH="release/phase50-a2l-owner-qa-20260918"
EXPECTED_BASELINE="8ec35d269ddab05bed5fab7d9c3fcc3fb6691fc7"
STATIC_ROOT="/home/sfkilvrs/public_html/static"
TARGET_SHA="${1:-}"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="/home/sfkilvrs/3dprinthub-deploy-backups/${STAMP}-phase50-a2l-pricing-engine"
TMP_DELTA="/tmp/3dprinthub-a2l-pricing-$$.txt"
STATIC_LIST="/tmp/3dprinthub-a2l-pricing-static-$$.txt"

cleanup(){ rm -f "$TMP_DELTA" "$STATIC_LIST" 2>/dev/null || true; }
trap cleanup EXIT
fail(){
  printf 'A2L_PRICING_DEPLOY_FAIL=%s\n' "$1" >&2
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
    raise SystemExit("A2L_PRICING_DEPLOY_FAIL=database_identity_mismatch")
plan=MigrationExecutor(connection).migration_plan(MigrationExecutor(connection).loader.graph.leaf_nodes())
print("MIGRATION_PLAN="+repr([(m.app_label,m.name,b) for m,b in plan]))
if plan:
    raise SystemExit("A2L_PRICING_DEPLOY_FAIL=migration_plan_not_empty")
ready=publish_readiness()
print("PUBLISH_READY="+repr(ready.get("ready")))
print("PUBLISH_BLOCKERS="+repr(ready.get("blockers") or []))
if ready.get("ready") is not True:
    raise SystemExit("A2L_PRICING_DEPLOY_FAIL=receiver_not_ready")
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
printf '%s\n' "===== PRICING DELTA ====="
cat "$TMP_DELTA"
if grep -Eq '(^|/)migrations/[0-9]{4}_[^/]+\.py$|^requirements[^/]*\.txt$|^config/settings' "$TMP_DELTA"; then
  fail "migration_dependency_or_settings_delta_detected"
fi
for required in store/phase49_3f_pricing_finalize.py store/phase50_profile_matrix.py store/test_phase50_filament_offer_operations.py; do
  grep -Fxq "$required" "$TMP_DELTA" || fail "required_delta_missing:$required"
done
git cat-file -e "$FETCHED:static/css/phase50-a2k-tympanus-slicebox.css" || fail "hero_css_missing_from_target"
git cat-file -e "$FETCHED:templates/website/partials/hero.html" || fail "hero_template_missing_from_target"
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
cat > "$STATIC_LIST" <<'EOF'
css/phase50-a2k-tympanus-slicebox.css
EOF
while IFS= read -r rel; do
  [ -n "$rel" ] || continue
  if [ -f "$STATIC_ROOT/$rel" ]; then
    mkdir -p "$BACKUP_ROOT/static-before/$(dirname "$rel")"
    cp -p "$STATIC_ROOT/$rel" "$BACKUP_ROOT/static-before/$rel"
  else
    printf '%s\n' "$rel" >> "$BACKUP_ROOT/static-absent-before.txt"
  fi
done < "$STATIC_LIST"
if [ -f "$BACKUP_ROOT/static-before/css/phase50-a2k-tympanus-slicebox.css" ]; then
  (cd "$BACKUP_ROOT" && sha256sum static-before/css/phase50-a2k-tympanus-slicebox.css > static-before.sha256 && sha256sum -c static-before.sha256)
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
grep -Fq 'desktop_sales_profile_formula_v1' store/phase49_3f_pricing.py || fail "desktop_pricing_authority_marker_missing"
grep -Fq 'managed_prefix = f"CC-P{product.pk}-"' store/phase49_3f_pricing_finalize.py || fail "managed_range_authority_marker_missing"

"$PY" - <<'PY'
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
import django; django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from catalog_bridge.publish_readiness import publish_readiness
from store.models import ProductVariant
plan=MigrationExecutor(connection).migration_plan(MigrationExecutor(connection).loader.graph.leaf_nodes())
if plan:
    raise SystemExit("A2L_PRICING_DEPLOY_FAIL=post_merge_migration_plan_not_empty")
ready=publish_readiness()
if ready.get("ready") is not True:
    raise SystemExit("A2L_PRICING_DEPLOY_FAIL=post_merge_receiver_not_ready")
variant=ProductVariant.objects.filter(code__startswith="CC-P39-",is_active=True).select_related("product","color","material").first()
if variant is None:
    raise SystemExit("A2L_PRICING_DEPLOY_FAIL=product39_managed_variant_missing")
breakdown=variant.price_breakdown()
print("PRODUCT39_VARIANT="+str(variant.pk))
print("PRICING_AUTHORITY="+str(breakdown.get("pricing_authority") or ""))
print("CURRENT_UNIT_PRICE="+str(breakdown.get("unit_price") or ""))
if breakdown.get("pricing_authority")!="desktop_sales_profile_formula_v1":
    raise SystemExit("A2L_PRICING_DEPLOY_FAIL=pricing_authority_not_installed")
print("POST_MERGE_PRICING_RUNTIME=PASS")
PY

grep -Fq 'v=50.8.0' templates/website/partials/hero.html || fail "hero_css_cache_version_missing"
grep -Fq 'aspect-ratio: 4 / 3' static/css/phase50-a2k-tympanus-slicebox.css || fail "mobile_image_priority_marker_missing"
grep -Fq 'border: 0 !important' static/css/phase50-a2k-tympanus-slicebox.css || fail "hero_border_reset_missing"

OLD_UMASK="$(umask)"
umask 022
"$PY" manage.py collectstatic --noinput
umask "$OLD_UMASK"
[ -f "$STATIC_ROOT/css/phase50-a2k-tympanus-slicebox.css" ] || fail "collected_hero_css_missing"
SRC_CSS_SHA="$(sha256sum static/css/phase50-a2k-tympanus-slicebox.css | awk '{print $1}')"
DST_CSS_SHA="$(sha256sum "$STATIC_ROOT/css/phase50-a2k-tympanus-slicebox.css" | awk '{print $1}')"
printf 'HERO_CSS_SHA source=%s collected=%s\n' "$SRC_CSS_SHA" "$DST_CSS_SHA"
[ "$SRC_CSS_SHA" = "$DST_CSS_SHA" ] || fail "collected_hero_css_hash_mismatch"

mkdir -p tmp
touch tmp/restart.txt
sleep 4

"$PY" - <<'PY'
from urllib import request
for url in (
    "https://3dprinthub.ir/store/product/mini-articulated-skeletal-spinosaurus/",
    "https://3dprinthub.ir/store/",
):
    with request.urlopen(request.Request(url,headers={"User-Agent":"3DPrintHub-A2L-Pricing/1.0","Cache-Control":"no-cache"}),timeout=20) as r:
        print(url+" HTTP="+str(r.status))
        if r.status!=200:
            raise SystemExit("A2L_PRICING_DEPLOY_FAIL=public_http_not_200")
with request.urlopen(request.Request("https://3dprinthub.ir/",headers={"User-Agent":"3DPrintHub-A2L-Pricing/1.0","Cache-Control":"no-cache"}),timeout=20) as r:
    home=r.read(2_000_000)
    print("HOME HTTP="+str(r.status))
    if r.status!=200 or b"phase50-a2k-tympanus-slicebox.css" not in home or b"v=50.8.0" not in home:
        raise SystemExit("A2L_PRICING_DEPLOY_FAIL=home_hero_version_missing")
with request.urlopen(request.Request("https://3dprinthub.ir/static/css/phase50-a2k-tympanus-slicebox.css?v=50.8.0",headers={"User-Agent":"3DPrintHub-A2L-Pricing/1.0","Cache-Control":"no-cache"}),timeout=20) as r:
    css=r.read(1_000_000)
    print("HERO_CSS HTTP="+str(r.status))
    for marker in (b"aspect-ratio: 4 / 3", b"border: 0 !important", b".p50k-slicebox__keyword"):
        if marker not in css:
            raise SystemExit("A2L_PRICING_DEPLOY_FAIL=hero_css_marker_missing")
print("PUBLIC_SMOKE=PASS")
PY

printf 'FINAL_HEAD=%s\n' "$(git rev-parse HEAD)"
printf 'FINAL_WORKTREE=%s\n' "$(test -z "$(git status --porcelain --untracked-files=all)" && printf CLEAN || printf DIRTY)"
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"
printf 'PHASE50_A2L_PRICING_ENGINE_DEPLOY=PASS\n'
