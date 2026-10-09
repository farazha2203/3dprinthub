#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
EXPECTED_DB="sfkilvrs_EmiAdmin_3dprinthub"
HOST_BRANCH="release/phase50-a2j-hero-20260915"
TARGET_BRANCH="release/phase50-a2t-google-indexing-20261008"
EXPECTED_BASELINE="2b48a593ace2e9a3703fa0f52b4c3c13b2751cf9"
TARGET_SHA="${1:-}"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="/home/sfkilvrs/3dprinthub-deploy-backups/${STAMP}-phase50-a2t-google-indexing"
TMP_DELTA="/tmp/3dprinthub-a2t-google-delta-$$.txt"

cleanup(){ rm -f "$TMP_DELTA" 2>/dev/null || true; }
trap cleanup EXIT
fail(){
  printf 'A2T_GOOGLE_DEPLOY_FAIL=%s\n' "$1" >&2
  printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT" >&2
  exit 1
}

[ -n "$TARGET_SHA" ] || fail "target_sha_required"
cd "$ROOT"
[ -d .git ] || fail "project_git_missing"
[ "$(git branch --show-current)" = "$HOST_BRANCH" ] || fail "wrong_host_branch"
[ "$(git rev-parse HEAD)" = "$EXPECTED_BASELINE" ] || fail "host_baseline_changed"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "production_worktree_dirty"
case "$(git remote get-url origin)" in
  *farazha2203/3dprinthub.git|*farazha2203/3dprinthub) ;;
  *) fail "wrong_repository" ;;
esac

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
from store.models import Product
from website.models import SEOSettings

expected = sys.argv[1]
name = str(connection.settings_dict.get("NAME") or "")
print("DB_VENDOR=" + str(connection.vendor))
print("DB_NAME=" + name)
if connection.vendor != "mysql" or name != expected:
    raise SystemExit("A2T_GOOGLE_DEPLOY_FAIL=database_identity_mismatch")
executor = MigrationExecutor(connection)
plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
print("MIGRATION_PLAN_COUNT=" + str(len(plan)))
if plan:
    raise SystemExit("A2T_GOOGLE_DEPLOY_FAIL=migration_plan_not_empty")
seo = SEOSettings.objects.order_by("pk").first()
print("SEO_SETTINGS_EXISTS=" + str(seo is not None))
print("SEARCH_INDEXING_ENABLED=" + str(bool(seo and seo.allow_search_indexing)))
print("GOOGLE_VERIFICATION_CONFIGURED=" + str(bool(seo and str(seo.google_site_verification or "").strip())))
print("SEO_SITE_URL=" + str((seo.site_url if seo else "") or ""))
print("ACTIVE_PRODUCT_COUNT=" + str(Product.objects.filter(is_active=True).count()))
print("INDEXABLE_PRODUCT_COUNT=" + str(Product.objects.filter(is_active=True, robots_index=True).count()))
PY

REMOTE_SHA="$(git ls-remote origin "refs/heads/$TARGET_BRANCH" | awk '{print $1}')"
printf 'REMOTE_SHA=%s\n' "$REMOTE_SHA"
[ "$REMOTE_SHA" = "$TARGET_SHA" ] || fail "target_not_live_github_head"
git fetch --no-tags origin "refs/heads/$TARGET_BRANCH"
FETCHED="$(git rev-parse FETCH_HEAD)"
[ "$FETCHED" = "$TARGET_SHA" ] || fail "fetched_target_mismatch"
git merge-base --is-ancestor "$EXPECTED_BASELINE" "$FETCHED" || fail "target_not_fast_forward"
git diff --name-only "$EXPECTED_BASELINE" "$FETCHED" > "$TMP_DELTA"
printf '%s\n' "===== A2T GOOGLE DELTA ====="
cat "$TMP_DELTA"

if grep -Eq '(^|/)migrations/[0-9]{4}_[^/]+\.py$|^requirements[^/]*\.txt$|^config/settings|(^|/)\.env$' "$TMP_DELTA"; then
  fail "migration_dependency_settings_or_env_delta_detected"
fi

while IFS= read -r changed; do
  case "$changed" in
    scripts/host/phase50_a2t_google_indexing_deploy.sh|    store/sitemaps.py|    store/templatetags/store_seo.py|    store/test_phase5.py|    store/views.py|    templates/store/base.html|    templates/store/product_detail.html|    templates/store/product_list.html|    templates/website/index.html|    website/test_phase50_search_console_readiness.py|    website/urls.py|    website/views_phase4.py)
      ;;
    *)
      fail "unexpected_target_delta:$changed"
      ;;
  esac
done < "$TMP_DELTA"

for required in   scripts/host/phase50_a2t_google_indexing_deploy.sh   store/sitemaps.py   store/templatetags/store_seo.py   store/views.py   templates/store/base.html   templates/store/product_detail.html   templates/store/product_list.html   templates/website/index.html   website/urls.py   website/views_phase4.py
do
  grep -Fxq "$required" "$TMP_DELTA" || fail "required_delta_missing:$required"
done

mkdir -p "$BACKUP_ROOT"
chmod 700 "$BACKUP_ROOT"
git bundle create "$BACKUP_ROOT/source-before.bundle" HEAD
git bundle verify "$BACKUP_ROOT/source-before.bundle"
printf '%s\n' "$EXPECTED_BASELINE" > "$BACKUP_ROOT/source-head.txt"
printf '%s\n' "$HOST_BRANCH" > "$BACKUP_ROOT/source-branch.txt"
printf '%s\n' "$TARGET_SHA" > "$BACKUP_ROOT/target-sha.txt"
if [ -f .env ]; then
  cp -p .env "$BACKUP_ROOT/.env"
  chmod 600 "$BACKUP_ROOT/.env"
fi
sha256sum "$BACKUP_ROOT/source-before.bundle" > "$BACKUP_ROOT/source-bundle.sha256"
if [ -f "$BACKUP_ROOT/.env" ]; then
  sha256sum "$BACKUP_ROOT/.env" > "$BACKUP_ROOT/env.sha256"
fi
(
  cd "$BACKUP_ROOT"
  sha256sum -c source-bundle.sha256
  if [ -f env.sha256 ]; then sha256sum -c env.sha256; fi
)

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

"$PY" -m py_compile   store/sitemaps.py   store/templatetags/store_seo.py   store/views.py   website/urls.py   website/views_phase4.py
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
from website.models import SEOSettings

expected = sys.argv[1]
name = str(connection.settings_dict.get("NAME") or "")
if connection.vendor != "mysql" or name != expected:
    raise SystemExit("A2T_GOOGLE_DEPLOY_FAIL=post_merge_database_identity_mismatch")
plan = MigrationExecutor(connection).migration_plan(
    MigrationExecutor(connection).loader.graph.leaf_nodes()
)
print("POST_MIGRATION_PLAN_COUNT=" + str(len(plan)))
if plan:
    raise SystemExit("A2T_GOOGLE_DEPLOY_FAIL=post_merge_migration_plan_not_empty")
seo = SEOSettings.objects.order_by("pk").first()
print("POST_SEARCH_INDEXING_ENABLED=" + str(bool(seo and seo.allow_search_indexing)))
PY

"$PY" manage.py collectstatic --noinput

mkdir -p tmp
touch tmp/restart.txt
sleep 4

"$PY" - <<'PY'
import json
import re
from urllib import request
from xml.etree import ElementTree

base = "https://3dprinthub.ir"
headers = {
    "User-Agent": "3DPrintHub-A2T-Google/1.0",
    "Cache-Control": "no-cache",
}

def fetch(path):
    req = request.Request(base + path, headers=headers)
    with request.urlopen(req, timeout=25) as response:
        body = response.read()
        print("PUBLIC_HTTP=" + str(response.status) + " " + path)
        if response.status != 200:
            raise SystemExit("A2T_GOOGLE_DEPLOY_FAIL=public_http_failed:" + path)
        return response, body

_, robots_raw = fetch("/robots.txt")
robots = robots_raw.decode("utf-8", "replace")
if "Disallow: /" not in robots:
    raise SystemExit("A2T_GOOGLE_DEPLOY_FAIL=indexing_changed_during_deploy")
print("ROBOTS_PRE_TOGGLE_BLOCKED=YES")

_, sitemap_raw = fetch("/sitemap.xml")
ElementTree.fromstring(sitemap_raw)
sitemap_text = sitemap_raw.decode("utf-8", "replace")
if base + "/" not in sitemap_text or base + "/store/" not in sitemap_text:
    raise SystemExit("A2T_GOOGLE_DEPLOY_FAIL=root_sitemap_missing_core_urls")
print("ROOT_SITEMAP_XML=PASS")

image_response, image_raw = fetch("/sitemap-images.xml")
ElementTree.fromstring(image_raw)
if image_response.headers.get("X-Robots-Tag", "").lower() != "noindex":
    raise SystemExit("A2T_GOOGLE_DEPLOY_FAIL=image_sitemap_xrobots_missing")
print("IMAGE_SITEMAP_XML=PASS")

_, home_raw = fetch("/")
home = home_raw.decode("utf-8", "replace")
if 'name="robots" content="noindex,nofollow"' not in home:
    raise SystemExit("A2T_GOOGLE_DEPLOY_FAIL=home_global_noindex_missing")
print("HOME_GLOBAL_NOINDEX=PASS")

_, store_raw = fetch("/store/")
store = store_raw.decode("utf-8", "replace")
if 'name="robots" content="noindex,nofollow"' not in store:
    raise SystemExit("A2T_GOOGLE_DEPLOY_FAIL=store_global_noindex_missing")
print("STORE_GLOBAL_NOINDEX=PASS")

locs = re.findall(rb"<loc>(https://3dprinthub\.ir/store/product/[^<]+)</loc>", sitemap_raw)
if locs:
    product_url = locs[0].decode("utf-8")
    req = request.Request(product_url, headers=headers)
    with request.urlopen(req, timeout=25) as response:
        product = response.read().decode("utf-8", "replace")
        print("PUBLIC_HTTP=" + str(response.status) + " PRODUCT_SAMPLE")
        if response.status != 200:
            raise SystemExit("A2T_GOOGLE_DEPLOY_FAIL=sample_product_http")
    if 'rel="canonical"' not in product:
        raise SystemExit("A2T_GOOGLE_DEPLOY_FAIL=sample_product_canonical_missing")
    blocks = re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        product,
        flags=re.I | re.S,
    )
    parsed = [json.loads(block) for block in blocks]
    if not any(
        isinstance(item, dict)
        and any(
            isinstance(node, dict) and node.get("@type") == "ProductGroup"
            for node in item.get("@graph", [])
        )
        for item in parsed
    ):
        raise SystemExit("A2T_GOOGLE_DEPLOY_FAIL=sample_product_group_missing")
    print("PRODUCT_SAMPLE_SCHEMA=PASS")
else:
    print("PRODUCT_SAMPLE_SCHEMA=SKIP_NO_PRODUCT_URL")

print("A2T_PUBLIC_PRE_TOGGLE_SMOKE=PASS")
PY

printf 'FINAL_HEAD=%s\n' "$(git rev-parse HEAD)"
printf 'FINAL_WORKTREE=%s\n' "$(test -z "$(git status --porcelain --untracked-files=all)" && printf CLEAN || printf DIRTY)"
printf 'BACKUP_ROOT=%s\n' "$BACKUP_ROOT"
printf 'PHASE50_A2T_GOOGLE_DEPLOY=PASS\n'
