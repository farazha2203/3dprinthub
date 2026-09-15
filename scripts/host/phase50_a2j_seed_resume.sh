#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
BRANCH="release/phase50-a2j-hero-20260915"
EXPECTED_DB="sfkilvrs_EmiAdmin_3dprinthub"
TARGET="${1:-}"
BACKUP_ROOT="${2:-}"

fail() { printf 'A2J_SEED_RESUME_FAIL=%s\n' "$1" >&2; exit 1; }
[ -n "$TARGET" ] || fail "target_required"
[ -n "$BACKUP_ROOT" ] || fail "backup_root_required"
[ -d "$ROOT/.git" ] || fail "project_root_missing"
[ -x "$PY" ] || fail "python_missing"
cd "$ROOT"

[ "$(git branch --show-current)" = "$BRANCH" ] || fail "wrong_branch"
[ "$(git rev-parse HEAD)" = "$TARGET" ] || fail "wrong_head"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "worktree_dirty"
REMOTE="$(git ls-remote origin "refs/heads/$BRANCH" | awk '{print $1}')"
[ "$REMOTE" = "$TARGET" ] || fail "target_not_remote_head"
[ -s "$BACKUP_ROOT/source-before.bundle" ] || fail "baseline_bundle_missing"
printf '%s\n' '===== PRE-SEED STATE ====='
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
print("STORE_COUNTS="+repr((Product.objects.count(),ProductVariant.objects.count(),ProductImage.objects.count())))
print("HERO_ACTIVE="+str(HomepageHeroSlide.objects.filter(is_active=True).count()))
if connection.vendor != "mysql" or str(connection.settings_dict.get("NAME") or "") != expected: raise SystemExit(11)
if plan: raise SystemExit(12)
if (Product.objects.count(),ProductVariant.objects.count(),ProductImage.objects.count()) != (0,0,0): raise SystemExit(13)
if HomepageHeroSlide.objects.filter(is_active=True).exists(): raise SystemExit(14)
PY

printf '%s\n' '===== PRE-SEED BACKUP ====='
git bundle create "$BACKUP_ROOT/source-preseed.bundle" HEAD
git bundle verify "$BACKUP_ROOT/source-preseed.bundle"
PHASE49_PROJECT_ROOT="$ROOT" PHASE49_BACKUP_ROOT="$BACKUP_ROOT" \
  "$PY" scripts/host/phase49_3i53_mysql_backup.py "$EXPECTED_DB"
gzip -t "$BACKUP_ROOT/database-before-3i53.sql.gz"
"$PY" - "$BACKUP_ROOT/hero-before.json" <<'PY'
import json, os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django; django.setup()
from website.models import HomepageHeroSlide
rows=list(HomepageHeroSlide.objects.order_by("id").values(
    "id","asset_id","title_override","group_title","description","button_text",
    "image_url","image_alt_text","object_fit","focal_position","sort_order","is_active"
))
with open(sys.argv[1],"w",encoding="utf-8") as handle:
    json.dump(rows,handle,ensure_ascii=False,indent=2)
print("HERO_BACKUP_ROWS="+str(len(rows)))
PY
sha256sum "$BACKUP_ROOT/source-before.bundle" "$BACKUP_ROOT/source-preseed.bundle" \
  "$BACKUP_ROOT/database-before-3i53.sql.gz" "$BACKUP_ROOT/hero-before.json" \
  > "$BACKUP_ROOT/preseed-manifest.sha256"
(cd "$BACKUP_ROOT" && sha256sum -c preseed-manifest.sha256)
printf 'PRESEED_BACKUP_VERIFIED=YES\nBACKUP_ROOT=%s\n' "$BACKUP_ROOT"

printf '%s\n' '===== SEED ====='
"$PY" manage.py phase50_a2j_seed_hero
"$PY" manage.py phase50_a2j_seed_hero --apply
printf '%s\n' '===== POST-SEED VERIFY ====='
"$PY" - <<'PY'
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django; django.setup()
from store.models import Product, ProductImage, ProductVariant
from website.models import HomepageHeroSlide
rows=list(HomepageHeroSlide.objects.filter(is_active=True).order_by("sort_order","id"))
assets=[row.asset_id for row in rows]
sorts=[row.sort_order for row in rows]
lengths=[len(row.description or "") for row in rows]
targets=[row.target_url for row in rows]
print("STORE_COUNTS="+repr((Product.objects.count(),ProductVariant.objects.count(),ProductImage.objects.count())))
print("HERO_ASSETS="+repr(assets))
print("HERO_SORTS="+repr(sorts))
print("HERO_DESCRIPTION_LENGTHS="+repr(lengths))
print("HERO_TARGETS="+repr(targets))
if (Product.objects.count(),ProductVariant.objects.count(),ProductImage.objects.count()) != (0,0,0): raise SystemExit(21)
if assets != [119,120,135,136]: raise SystemExit(22)
if sorts != [10,20,30,40]: raise SystemExit(23)
if not all(0 < value <= 480 for value in lengths): raise SystemExit(24)
if not all(value == "/#order" for value in targets): raise SystemExit(25)
if not all(bool(row.effective_image_url) for row in rows): raise SystemExit(26)
print("POST_SEED_DB_VERIFY=PASS")
PY

mkdir -p tmp
touch tmp/restart.txt
sleep 4
printf '%s\n' '===== PUBLIC VERIFY ====='
"$PY" - <<'PY'
from urllib import request
base="https://3dprinthub.ir"
def fetch(path):
    req=request.Request(base+path,headers={"User-Agent":"3DPrintHub-A2J-Seed-Resume/1.0","Cache-Control":"no-cache"})
    with request.urlopen(req,timeout=25) as response:
        return int(response.status), response.read(2_000_000)
home_status, home=fetch("/")
store_status, store=fetch("/store/")
print("HOME_HTTP="+str(home_status))
print("STORE_HTTP="+str(store_status))
print("PUBLIC_SLIDE_MARKERS="+str(home.count(b"data-p50j-slide")))
if home_status != 200 or store_status != 200: raise SystemExit(31)
if b"data-p50j-slicebox" not in home: raise SystemExit(32)
if home.count(b"data-p50j-slide") != 4: raise SystemExit(33)
if b"phase50-a2i-slicebox-hero.js" in home or b"phase49_2c-home-hero.js" in home: raise SystemExit(34)
print("PUBLIC_VERIFY=PASS")
PY

printf 'FINAL_BRANCH=%s\n' "$(git branch --show-current)"
printf 'FINAL_HEAD=%s\n' "$(git rev-parse HEAD)"
printf 'FINAL_WORKTREE=%s\n' "$(test -z "$(git status --porcelain --untracked-files=all)" && printf CLEAN || printf DIRTY)"
[ "$(git rev-parse HEAD)" = "$TARGET" ] || fail "final_head_mismatch"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "final_worktree_dirty"
printf '%s\n' 'PHASE50_A2J_SEED_RESUME=PASS'
