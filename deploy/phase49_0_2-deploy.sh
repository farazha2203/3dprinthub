#!/usr/bin/env bash
set -euo pipefail

PROJECT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
EXPECTED_COMMIT="${1:-}"

cd "$PROJECT"

echo "=== PHASE49.0.2 PRODUCTION DEPLOY ==="
echo "PROJECT=$PROJECT"
echo "HEAD=$(git rev-parse HEAD)"

if [[ -n "$EXPECTED_COMMIT" && "$(git rev-parse HEAD)" != "$EXPECTED_COMMIT" ]]; then
  echo "ERROR=HEAD_MISMATCH expected=$EXPECTED_COMMIT actual=$(git rev-parse HEAD)" >&2
  exit 2
fi

echo "=== DJANGO CHECK ==="
"$PY" manage.py check

echo "=== MIGRATION DRIFT CHECK ==="
"$PY" manage.py makemigrations --check --dry-run

echo "=== FOCUSED UNICODE ROUTE TESTS ==="
"$PY" manage.py test store.test_phase49_unicode_routes --verbosity 2

echo "=== PASSENGER RESTART ==="
mkdir -p tmp
touch tmp/restart.txt
sleep 4

echo "=== PHASE49 BASE RUNTIME VERIFY ==="
"$PY" deploy/phase49_verify_runtime.py

echo "=== PHASE49.0.2 UNICODE RUNTIME VERIFY ==="
"$PY" deploy/phase49_0_2_verify_unicode_routes.py

echo "PHASE49_0_2_PRODUCTION_DEPLOY=OK"
