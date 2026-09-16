#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
BRANCH="release/phase50-a2j-hero-20260915"
BASELINE="f5aa5af1e3cea39f6a04099eec6ad5696e30a3ad"
EXPECTED_DB="sfkilvrs_EmiAdmin_3dprinthub"
TARGET="${1:-}"
BACKUP_BASE="/home/sfkilvrs/3dprinthub-deploy-backups"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="$BACKUP_BASE/${STAMP}-phase50-a2j-description-seed"
DELTA_FILE="/tmp/3dprinthub-a2j-desc-delta-$$.txt"

cleanup() { rm -f "$DELTA_FILE" 2>/dev/null || true; }
trap cleanup EXIT
fail() { printf 'A2J_DESC_DEPLOY_FAIL=%s\nBACKUP_ROOT=%s\n' "$1" "$BACKUP_ROOT" >&2; exit 1; }

[ -n "$TARGET" ] || fail "target_required"
[ -d "$ROOT/.git" ] || fail "project_root_missing"
[ -x "$PY" ] || fail "python_missing"
cd "$ROOT"
ORIGIN="$(git remote get-url origin)"
HEAD_NOW="$(git rev-parse HEAD)"
BRANCH_NOW="$(git branch --show-current)"
STATUS="$(git status --porcelain --untracked-files=all)"
printf 'ORIGIN=%s\nBRANCH=%s\nHEAD=%s\nTARGET=%s\n' "$ORIGIN" "$BRANCH_NOW" "$HEAD_NOW" "$TARGET"
case "$ORIGIN" in *farazha2203/3dprinthub.git|*farazha2203/3dprinthub) ;; *) fail "wrong_repository" ;; esac
[ "$BRANCH_NOW" = "$BRANCH" ] || fail "wrong_branch"
[ "$HEAD_NOW" = "$BASELINE" ] || fail "baseline_changed"
[ -z "$STATUS" ] || fail "worktree_dirty"

printf '%s\n' '===== PREDEPLOY DB STATE ====='
"$PY" - "$EXPECTED_DB" <<'PY'
import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django; django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from store.models import Product, ProductImage, ProductVariant
from website.models import HomepageHeroSlide
expected=sys.argv[1]
plan=MigrationExecutor(connection).migration_plan(MigrationExecutor(connection).loader.graph.leaf_nodes())
print("DB_VENDOR="+connection.vendor)
print("DB_NAME="+str(connection.settings_dict.get("NAME") or ""))
print("MIGRATION_PLAN_COUNT="+str(len(plan)))
print("STORE_COUNTS="+repr((Product.objects.count(), ProductVariant.objects.count(), ProductImage.objects.count())))
print("HERO_ACTIVE="+str(HomepageHeroSlide.objects.filter(is_active=True).count()))
if connection.vendor != "mysql" or str(connection.settings_dict.get("NAME") or "") != expected: raise SystemExit(21)
if plan: raise SystemExit(22)
if (Product.objects.count(), ProductVariant.objects.count(), ProductImage.objects.count()) != (0,0,0): raise SystemExit(23)
if HomepageHeroSlide.objects.filter(is_active=True).exists(): raise SystemExit(24)
PY
printf '%s\n' '===== LIVE TARGET / FETCH_HEAD ====='
REMOTE_LINE="$(git ls-remote origin "refs/heads/$BRANCH")"
[ -n "$REMOTE_LINE" ] || fail "release_branch_missing"
REMOTE_SHA="$(printf '%s\n' "$REMOTE_LINE" | awk '{print $1}')"
printf 'REMOTE_SHA=%s\n' "$REMOTE_SHA"
[ "$REMOTE_SHA" = "$TARGET" ] || fail "target_not_remote_head"
git fetch --no-tags origin "refs/heads/$BRANCH"
FETCHED="$(git rev-parse FETCH_HEAD)"
printf 'FETCHED=%s\n' "$FETCHED"
[ "$FETCHED" = "$TARGET" ] || fail "fetch_mismatch"
git merge-base --is-ancestor "$BASELINE" "$FETCHED" || fail "not_fast_forward"
git diff --name-only "$BASELINE" "$FETCHED" > "$DELTA_FILE"
cat "$DELTA_FILE"
while IFS= read -r path; do
  [ -n "$path" ] || continue
  case "$path" in
    website/management/commands/phase50_a2j_seed_hero.py) ;;
    website/phase49_persian_sales_hero.py) ;;
    website/test_phase49_persian_sales_hero.py) ;;
    website/test_phase50_a2j_hero_seed.py) ;;
    scripts/host/phase50_a2j_description_seed_deploy.sh) ;;
    *) fail "unexpected_delta:$path" ;;
  esac
done < "$DELTA_FILE"
if grep -Eq '(^|/)migrations/[0-9]{4}_[^/]+\.py$|^requirements[^/]*\.txt$|^config/settings' "$DELTA_FILE"; then
  fail "schema_dependency_settings_delta"
fi
if grep -Eiq 'payment|payments|gateway|zarinpal' "$DELTA_FILE"; then
  fail "payment_delta"
fi
printf '%s\n' 'DELTA_GATE=PASS'
printf '%s\n' '===== VERIFIED BACKUP ====='
mkdir -p "$BACKUP_ROOT"
chmod 700 "$BACKUP_ROOT"
git bundle create "$BACKUP_ROOT/source-before.bundle" HEAD
git bundle verify "$BACKUP_ROOT/source-before.bundle"
printf '%s\n' "$HEAD_NOW" > "$BACKUP_ROOT/source-head.txt"
printf '%s\n' "$BRANCH_NOW" > "$BACKUP_ROOT/source-branch.txt"
if [ -f .env ]; then cp -p .env "$BACKUP_ROOT/.env"; chmod 600 "$BACKUP_ROOT/.env"; fi

PHASE49_PROJECT_ROOT="$ROOT" PHASE49_BACKUP_ROOT="$BACKUP_ROOT" \
  "$PY" scripts/host/phase49_3i53_mysql_backup.py "$EXPECTED_DB"
gzip -t "$BACKUP_ROOT/database-before-3i53.sql.gz"

"$PY" - "$BACKUP_ROOT/hero-before.json" <<'PY'
import json, os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django; django.setup()
from website.models import HomepageHeroSlide
rows=list(HomepageHeroSlide.objects.order_by("id").values(
    "id","asset_id","title_override","group_title","description","sort_order","is_active"
))
with open(sys.argv[1],"w",encoding="utf-8") as f: json.dump(rows,f,ensure_ascii=False,indent=2)
print("HERO_BACKUP_ROWS="+str(len(rows)))
PY
sha256sum "$BACKUP_ROOT/source-before.bundle" "$BACKUP_ROOT/database-before-3i53.sql.gz" \
  "$BACKUP_ROOT/hero-before.json" > "$BACKUP_ROOT/manifest.sha256"
(cd "$BACKUP_ROOT" && sha256sum -c manifest.sha256)
printf 'BACKUP_ROOT=%s\nPREDEPLOY_BACKUP_VERIFIED=YES\n' "$BACKUP_ROOT"
printf '%s\n' '===== FF-ONLY SOURCE PROMOTION ====='
git merge --ff-only "$FETCHED"
[ "$(git rev-parse HEAD)" = "$TARGET" ] || fail "head_mismatch_after_merge"
[ "$(git branch --show-current)" = "$BRANCH" ] || fail "branch_changed_after_merge"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "worktree_dirty_after_merge"

"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
"$PY" - <<'PY'
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django; django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
plan=MigrationExecutor(connection).migration_plan(MigrationExecutor(connection).loader.graph.leaf_nodes())
print("POST_MIGRATION_PLAN_COUNT="+str(len(plan)))
if plan: raise SystemExit(31)
PY

printf '%s\n' '===== HERO SEED DRY RUN ====='
"$PY" manage.py phase50_a2j_seed_hero
printf '%s\n' '===== HERO SEED APPLY ====='
"$PY" manage.py phase50_a2j_seed_hero --apply
printf '%s\n' '===== POST-SEED DB VERIFY ====='
"$PY" - <<'PY'
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django; django.setup()
from store.models import Product, ProductImage, ProductVariant
from website.models import HomepageHeroSlide
rows=list(HomepageHeroSlide.objects.filter(is_active=True).order_by("sort_order","id"))
print("POST_STORE_COUNTS="+repr((Product.objects.count(), ProductVariant.objects.count(), ProductImage.objects.count())))
print("POST_HERO_ASSETS="+repr([r.asset_id for r in rows]))
print("POST_HERO_SORT="+repr([r.sort_order for r in rows]))
print("POST_HERO_DESCRIPTION_LENGTHS="+repr([len(r.description or "") for r in rows]))
print("POST_HERO_TARGETS="+repr([r.target_url for r in rows]))
if (Product.objects.count(), ProductVariant.objects.count(), ProductImage.objects.count()) != (0,0,0): raise SystemExit(41)
if [r.asset_id for r in rows] != [119,120,135,136]: raise SystemExit(42)
if [r.sort_order for r in rows] != [10,20,30,40]: raise SystemExit(43)
if not all(0 < len(r.description or "") <= 480 for r in rows): raise SystemExit(44)
if not all(r.target_url == "/#order" for r in rows): raise SystemExit(45)
if not all(bool(r.effective_image_url) for r in rows): raise SystemExit(46)
print("POST_SEED_DB_VERIFY=PASS")
PY

printf '%s\n' '===== STATIC HASH VERIFY ====='
STATIC_ROOT="/home/sfkilvrs/public_html/static"
for rel in css/phase50-a2j-slicebox-hero.css js/phase50-a2j-slicebox-hero.js; do
  [ -f "static/$rel" ] || fail "source_static_missing:$rel"
  [ -f "$STATIC_ROOT/$rel" ] || fail "collected_static_missing:$rel"
  SOURCE_SHA="$(sha256sum "static/$rel" | awk '{print $1}')"
  COLLECTED_SHA="$(sha256sum "$STATIC_ROOT/$rel" | awk '{print $1}')"
  printf 'STATIC_SHA %s source=%s collected=%s\n' "$rel" "$SOURCE_SHA" "$COLLECTED_SHA"
  [ "$SOURCE_SHA" = "$COLLECTED_SHA" ] || fail "static_hash_mismatch:$rel"
done
printf '%s\n' '===== PASSENGER RESTART ====='
mkdir -p tmp
touch tmp/restart.txt
sleep 4

printf '%s\n' '===== PUBLIC HTTP VERIFY ====='
"$PY" - <<'PY'
from urllib import request
base="https://3dprinthub.ir"
def fetch(path):
    req=request.Request(base+path,headers={"User-Agent":"3DPrintHub-A2J-Description-Seed/1.0","Cache-Control":"no-cache"})
    with request.urlopen(req,timeout=25) as r:
        return int(r.status), r.read(2_000_000)
home_status, home=fetch("/")
store_status, store=fetch("/store/")
css_status, css=fetch("/static/css/phase50-a2j-slicebox-hero.css?v=50.4.0")
js_status, js=fetch("/static/js/phase50-a2j-slicebox-hero.js?v=50.4.0")
print("HOME_HTTP="+str(home_status))
print("STORE_HTTP="+str(store_status))
print("CSS_HTTP="+str(css_status))
print("JS_HTTP="+str(js_status))
if (home_status,store_status,css_status,js_status)!=(200,200,200,200): raise SystemExit(51)
if b"data-p50j-slicebox" not in home: raise SystemExit(52)
if home.count(b"data-p50j-slide") != 4: raise SystemExit(53)
if b"phase50-a2i-slicebox-hero.js" in home or b"phase49_2c-home-hero.js" in home: raise SystemExit(54)
if b"p50j-slicebox" not in js or b"Phase50.A.2J" not in css: raise SystemExit(55)
if b"/store/product/" in home: raise SystemExit(56)
print("PUBLIC_HERO_SLIDES=4")
print("PUBLIC_HTTP_VERIFY=PASS")
PY

printf '%s\n' '===== FINAL STATE ====='
printf 'FINAL_BRANCH=%s\n' "$(git branch --show-current)"
printf 'FINAL_HEAD=%s\n' "$(git rev-parse HEAD)"
printf 'FINAL_WORKTREE=%s\n' "$(test -z "$(git status --porcelain --untracked-files=all)" && printf CLEAN || printf DIRTY)"
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"
[ "$(git rev-parse HEAD)" = "$TARGET" ] || fail "final_head_mismatch"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "final_worktree_dirty"
printf '%s\n' 'PHASE50_A2J_DESCRIPTION_SEED_DEPLOY=PASS'
