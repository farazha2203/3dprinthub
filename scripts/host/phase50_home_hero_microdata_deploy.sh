#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
EXPECTED_DB="sfkilvrs_EmiAdmin_3dprinthub"
HOST_BRANCH="release/phase50-a2j-hero-20260915"
TARGET_BRANCH="release/phase50-a2t-google-indexing-20261008"
EXPECTED_BASELINE="2b567c9485ec5b2950d2c2644eb8d19ab425fdea"
TARGET_SHA="$1"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="/home/sfkilvrs/3dprinthub-deploy-backups/$STAMP-home-hero-microdata"
DELTA="$(mktemp)"
trap 'rm -f "$DELTA"' EXIT

fail() { printf 'HERO_MICRODATA_DEPLOY_FAIL=%s\n' "$1" >&2; exit 1; }
[ -n "$TARGET_SHA" ] || fail "target_sha_required"
cd "$ROOT"
[ -d .git ] || fail "repo_missing"
[ "$(git branch --show-current)" = "$HOST_BRANCH" ] || fail "host_branch_mismatch"
[ "$(git rev-parse HEAD)" = "$EXPECTED_BASELINE" ] || fail "host_baseline_changed"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "host_dirty"
case "$(git remote get-url origin)" in
  *farazha2203/3dprinthub.git|*farazha2203/3dprinthub) ;;
  *) fail "origin_mismatch" ;;
esac

# This cPanel account has a hard 2000 MB user quota; df is not authoritative.
# Scoped source + protected env + FULL fresh MySQL backup are mandatory.
check_quota() {
  "$PY" - "$1" <<'PY'
import re
import subprocess
import sys
data = subprocess.run(
    ["uapi", "StatsBar", "get_stats", "display=diskusage"],
    check=True, text=True, capture_output=True, timeout=30,
).stdout
used = re.search(r"(?m)^ *_count: *'?([0-9]+)", data)
limit = re.search(r"(?m)^ *_max: *'?([0-9]+)", data)
if not used or not limit:
    raise SystemExit("HOST_ACCOUNT_QUOTA_UNVERIFIED")
free = int(limit.group(1)) - int(used.group(1))
print(f"HOST_ACCOUNT_QUOTA_FREE_MB={free} REQUIRED_MB={sys.argv[1]}")
if free < int(sys.argv[1]):
    raise SystemExit("HOST_QUOTA_BELOW_SCOPED_BACKUP_RESERVE")
PY
}
check_quota 6

REMOTE_SHA="$(git ls-remote origin "refs/heads/$TARGET_BRANCH" | awk '{print $1}')"
[ "$REMOTE_SHA" = "$TARGET_SHA" ] || fail "github_sha_mismatch"
git fetch --no-tags origin "refs/heads/$TARGET_BRANCH"
FETCHED="$(git rev-parse FETCH_HEAD)"
[ "$FETCHED" = "$TARGET_SHA" ] || fail "fetched_sha_mismatch"
git merge-base --is-ancestor "$EXPECTED_BASELINE" "$FETCHED" || fail "non_ff_target"
git diff --name-only "$EXPECTED_BASELINE" "$FETCHED" > "$DELTA"
cat "$DELTA"
while IFS= read -r changed; do
  case "$changed" in
    templates/website/partials/hero.html|website/test_phase50_a2k_tympanus_slicebox.py|scripts/host/phase50_home_hero_microdata_deploy.sh|scripts/host/test_phase50_home_hero_microdata_runner.py|docs/CURRENT_STATE.md|docs/ROADMAP.md|docs/CHANGELOG.md|docs/ERRORS.md|docs/REQUESTS.md|docs/phases/PHASE50_A2T_GOOGLE_POST_READINESS.md) ;;
    *) fail "unexpected_file:$changed" ;;
  esac
done < "$DELTA"
grep -Fxq "templates/website/partials/hero.html" "$DELTA" || fail "hero_template_missing"
grep -Fxq "website/test_phase50_a2k_tympanus_slicebox.py" "$DELTA" || fail "hero_regression_missing"

"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
"$PY" - "$EXPECTED_DB" <<'PY'
import os, sys, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
assert connection.vendor == "mysql"
assert connection.settings_dict["NAME"] == sys.argv[1]
assert not MigrationExecutor(connection).migration_plan(MigrationExecutor(connection).loader.graph.leaf_nodes())
print("HOST_DB_IDENTITY_NO_MIGRATIONS=PASS")
PY

# Previous full source bundle is verified and the pre-change source SHA stays in Git.
# Limit fresh rollback to the actual one HTML file, .env and a FULL MySQL dump.
check_quota 5
mkdir -p "$BACKUP_ROOT"
chmod 700 "$BACKUP_ROOT"
printf '%s\n' "$EXPECTED_BASELINE" > "$BACKUP_ROOT/prechange-sha.txt"
printf '%s\n' "$TARGET_SHA" > "$BACKUP_ROOT/target-sha.txt"
git cat-file -e "$EXPECTED_BASELINE^{commit}" || fail "no_prior_git_commit"
cp -p templates/website/partials/hero.html "$BACKUP_ROOT/hero-before.html"
if [ -f .env ]; then cp -p .env "$BACKUP_ROOT/.env"; chmod 600 "$BACKUP_ROOT/.env"; fi
sha256sum "$BACKUP_ROOT/hero-before.html" > "$BACKUP_ROOT/hero-before.sha256"
sha256sum "$BACKUP_ROOT/hero-before.html" | cut -d' ' -f1 > "$BACKUP_ROOT/prechange-source-digest.txt"
export PHASE49_PROJECT_ROOT="$ROOT"
export PHASE49_BACKUP_ROOT="$BACKUP_ROOT"
"$PY" scripts/host/phase49_3i53_mysql_backup.py "$EXPECTED_DB"
gzip -t "$BACKUP_ROOT/database-before-3i53.sql.gz"
sha256sum "$BACKUP_ROOT/database-before-3i53.sql.gz" > "$BACKUP_ROOT/database-before.sha256"
(cd "$BACKUP_ROOT" && sha256sum -c hero-before.sha256 database-before.sha256)
[ -f "$BACKUP_ROOT/.env" ] || fail "protected_env_missing"
printf 'FRESH_SCOPED_SOURCE_ENV_FULL_DB_ROLLBACK=PASS\nBACKUP_ROOT=%s\n' "$BACKUP_ROOT"

git merge --ff-only "$FETCHED"
[ "$(git rev-parse HEAD)" = "$TARGET_SHA" ] || fail "postmerge_sha_mismatch"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "postmerge_dirty"
"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
"$PY" manage.py collectstatic --noinput
mkdir -p tmp
touch tmp/restart.txt
sleep 4

"$PY" - <<'PY'
import json
import re
from urllib.request import Request, urlopen
base = "https://3dprinthub.ir"
slugs = (
    "ribbed-cake-stand-cookie-platter",
    "christmas-tree-minimalistic-japandi-decor",
    "fox-cute-animal-stylish-japandi-style",
    "handbag-purse-organizer-editable-text",
    "winter-reindeer",
    "floating-drip-tealight-holders",
)
def fetch(path):
    with urlopen(Request(
        base + path,
        headers={"User-Agent": "3DPrintHub-HeroSchemaVerifier/1.0", "Cache-Control": "no-cache"},
    ), timeout=25) as response:
        assert response.status == 200, (path, response.status)
        return response.read().decode("utf-8", "replace")

home = fetch("/")
assert 'id="sb-slider"' in home and 'id="nav-arrows"' in home and 'id="nav-dots"' in home
assert 'itemtype="https://schema.org/Product"' not in home, "homepage_incomplete_product_microdata"
assert 'itemprop="description"' not in home, "homepage_orphan_product_microdata"
assert 'itemprop="name"' not in home, "homepage_orphan_product_microdata"
assert 'itemprop="image"' not in home, "homepage_orphan_product_microdata"
assert 'itemprop="url"' not in home, "homepage_orphan_product_microdata"
for slug in slugs:
    assert ('href="/store/product/' + slug + '/"') in home, (slug, "hero_link_missing")
    detail = fetch("/store/product/" + slug + "/")
    scripts = re.findall(r'<script[^>]*application/ld[+]json[^>]*>(.*?)</script>', detail, re.I | re.S)
    nodes = [node for script in scripts for node in json.loads(script).get("@graph", [])]
    families = [node for node in nodes if node.get("@type") == "ProductGroup"]
    assert len(families) == 1, (slug, "store_schema_regressed")
    variants = families[0].get("hasVariant", [])
    assert variants and all(
        item.get("offers", {}).get("priceCurrency") == "IRR"
        and int(item["offers"]["price"]) > 0
        for item in variants
    ), (slug, "variant_offers_regressed")
    print("HERO_LINK_AND_STORE_OFFER_PASS=" + slug)
print("HOMEPAGE_6_INVALID_PRODUCTS_REMOVED=PASS")
print("SIX_STORE_PRODUCT_OFFERS_PRESERVED=PASS")
PY
printf 'FINAL_HEAD=%s\n' "$(git rev-parse HEAD)"
printf 'FINAL_WORKTREE=%s\n' "$(test -z "$(git status --porcelain --untracked-files=all)" && printf CLEAN || printf DIRTY)"
printf 'HERO_MICRODATA_DEPLOY=PASS\n'
