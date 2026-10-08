#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
EXPECTED_DB="sfkilvrs_EmiAdmin_3dprinthub"
HOST_BRANCH="release/phase50-a2j-hero-20260915"
TARGET_BRANCH="release/phase50-a2t-google-indexing-20261008"
EXPECTED_BASELINE="2b85a9c0d5d4a79219182bc9b986a5a81e70ed50"
TARGET_SHA="${1:-}"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="/home/sfkilvrs/3dprinthub-deploy-backups/${STAMP}-product-snippet"
TMP_DELTA="$(mktemp)"
trap 'rm -f "$TMP_DELTA"' EXIT

fail() { printf 'PRODUCT_SNIPPET_DEPLOY_FAIL=%s\n' "$1" >&2; exit 1; }
[ -n "$TARGET_SHA" ] || fail "target_sha_required"
cd "$ROOT"
[ -d .git ] || fail "project_git_missing"
[ "$(git branch --show-current)" = "$HOST_BRANCH" ] || fail "host_branch_mismatch"
[ "$(git rev-parse HEAD)" = "$EXPECTED_BASELINE" ] || fail "host_baseline_changed"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "host_worktree_dirty"
case "$(git remote get-url origin)" in
  *farazha2203/3dprinthub.git|*farazha2203/3dprinthub) ;;
  *) fail "wrong_repository" ;;
esac
REMOTE_SHA="$(git ls-remote origin "refs/heads/$TARGET_BRANCH" | awk '{print $1}')"
[ "$REMOTE_SHA" = "$TARGET_SHA" ] || fail "github_sha_mismatch"
git fetch --no-tags origin "refs/heads/$TARGET_BRANCH"
FETCHED="$(git rev-parse FETCH_HEAD)"
[ "$FETCHED" = "$TARGET_SHA" ] || fail "fetched_sha_mismatch"
git merge-base --is-ancestor "$EXPECTED_BASELINE" "$FETCHED" || fail "non_fast_forward"
git diff --name-only "$EXPECTED_BASELINE" "$FETCHED" > "$TMP_DELTA"
printf '===== PRODUCT SNIPPET RELEASE DELTA =====\n'
cat "$TMP_DELTA"
while IFS= read -r changed; do
  case "$changed" in
    store/templatetags/store_seo.py|store/test_phase5.py|scripts/host/phase50_product_snippet_deploy.sh|docs/CURRENT_STATE.md|docs/ROADMAP.md|docs/CHANGELOG.md|docs/ERRORS.md|docs/REQUESTS.md|docs/phases/PHASE50_A2T_GOOGLE_POST_READINESS.md|docs/DEPLOYMENT.md|docs/PATHS.md|docs/HOST_CONSTRAINTS.md) ;;
    *) fail "unexpected_delta:$changed" ;;
  esac
done < "$TMP_DELTA"
grep -Fxq "store/templatetags/store_seo.py" "$TMP_DELTA" || fail "schema_delta_missing"
grep -Fxq "store/test_phase5.py" "$TMP_DELTA" || fail "regression_delta_missing"

"$PY" manage.py check
"$PY" manage.py makemigrations --check --dry-run
"$PY" - "$EXPECTED_DB" <<'PY'
import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
expected = sys.argv[1]
assert connection.vendor == "mysql", "Wrong Production DB vendor"
assert str(connection.settings_dict["NAME"]) == expected, "Wrong Production DB name"
executor = MigrationExecutor(connection)
assert not executor.migration_plan(executor.loader.graph.leaf_nodes()), "Pending migrations"
print("DB_IDENTITY_AND_MIGRATIONS=PASS")
PY

mkdir -p "$BACKUP_ROOT"
chmod 700 "$BACKUP_ROOT"
git bundle create "$BACKUP_ROOT/source-before.bundle" HEAD
git bundle verify "$BACKUP_ROOT/source-before.bundle"
printf '%s\n' "$EXPECTED_BASELINE" > "$BACKUP_ROOT/source-head.txt"
printf '%s\n' "$TARGET_SHA" > "$BACKUP_ROOT/target-sha.txt"
if [ -f .env ]; then cp -p .env "$BACKUP_ROOT/.env"; chmod 600 "$BACKUP_ROOT/.env"; fi
sha256sum "$BACKUP_ROOT/source-before.bundle" > "$BACKUP_ROOT/source-before.sha256"
(cd "$BACKUP_ROOT" && sha256sum -c source-before.sha256)
export PHASE49_PROJECT_ROOT="$ROOT"
export PHASE49_BACKUP_ROOT="$BACKUP_ROOT"
"$PY" scripts/host/phase49_3i53_mysql_backup.py "$EXPECTED_DB"
gzip -t "$BACKUP_ROOT/database-before-3i53.sql.gz"
sha256sum "$BACKUP_ROOT/database-before-3i53.sql.gz" > "$BACKUP_ROOT/database-before.sha256"
(cd "$BACKUP_ROOT" && sha256sum -c database-before.sha256)
printf 'PREDEPLOY_BACKUP_VERIFIED=YES\nBACKUP_ROOT=%s\n' "$BACKUP_ROOT"

git merge --ff-only "$FETCHED"
[ "$(git rev-parse HEAD)" = "$TARGET_SHA" ] || fail "post_merge_head_mismatch"
[ -z "$(git status --porcelain --untracked-files=all)" ] || fail "post_merge_dirty"
"$PY" -m py_compile store/templatetags/store_seo.py
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
    with urlopen(Request(base + path, headers={"User-Agent": "3DPrintHub-ProductSchemaVerifier/1.0", "Cache-Control": "no-cache"}), timeout=25) as response:
        assert response.status == 200, (path, response.status)
        return response.read().decode("utf-8", "replace")
assert "Allow: /" in fetch("/robots.txt")
assert "<urlset" in fetch("/sitemap.xml")
assert "<html" in fetch("/")
assert "<html" in fetch("/store/")
for slug in slugs:
    path = "/store/product/" + slug + "/"
    html = fetch(path)
    assert 'rel="canonical"' in html, (slug, "canonical")
    scripts = re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', html, re.I | re.S)
    graphs = [json.loads(script) for script in scripts]
    nodes = [node for graph in graphs for node in graph.get("@graph", []) if isinstance(node, dict)]
    families = [node for node in nodes if node.get("@type") == "ProductGroup"]
    assert len(families) == 1, (slug, "missing_or_duplicate_product_group", len(families))
    family = families[0]
    assert "offers" not in family, (slug, "aggregate_offer_misused_for_variants")
    variants = family.get("hasVariant", [])
    assert variants, (slug, "missing_variants")
    assert all(
        item.get("@type") == "Product"
        and item.get("offers", {}).get("@type") == "Offer"
        and item["offers"].get("priceCurrency") == "IRR"
        and int(item["offers"]["price"]) > 0
        for item in variants
    ), (slug, "invalid_variant_offer")
    print("PRODUCT_SNIPPET_PASS=" + slug + " variants=" + str(len(variants)))
print("PUBLIC_PRODUCT_SNIPPET_SMOKE=PASS")
PY
printf 'FINAL_HEAD=%s\n' "$(git rev-parse HEAD)"
printf 'FINAL_WORKTREE=%s\n' "$(test -z "$(git status --porcelain --untracked-files=all)" && printf CLEAN || printf DIRTY)"
printf 'PRODUCT_SNIPPET_DEPLOY=PASS\n'
