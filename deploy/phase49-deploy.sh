#!/usr/bin/env bash
set -euo pipefail

PROJECT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
EXPECTED_COMMIT="${1:-}"

cd "$PROJECT"

echo "=== PHASE49 PRODUCTION DEPLOY ==="
echo "PROJECT=$PROJECT"
echo "HEAD=$(git rev-parse HEAD)"
if [[ -n "$EXPECTED_COMMIT" && "$(git rev-parse HEAD)" != "$EXPECTED_COMMIT" ]]; then
  echo "ERROR=HEAD_MISMATCH expected=$EXPECTED_COMMIT actual=$(git rev-parse HEAD)" >&2
  exit 2
fi

# Reuse the proven Phase48 deploy path: DB backup, checks, migration plan,
# migrate, collectstatic, Passenger restart and base runtime verification.
bash deploy/phase48-deploy.sh

echo "=== PHASE49 VISIBILITY RECONCILIATION ==="
PENDING_COUNT="$(find imports/desktop_catalog/pending -mindepth 1 -maxdepth 1 -type d -name 'desktop_catalog_v85_*' 2>/dev/null | wc -l | tr -d ' ')"
echo "PENDING_BATCH_COUNT=$PENDING_COUNT"
if [[ "$PENDING_COUNT" -gt 0 ]]; then
  echo "--- DRY RUN ---"
  "$PY" manage.py phase49_reconcile_catalog_visibility --all-pending
  echo "--- APPLY ---"
  "$PY" manage.py phase49_reconcile_catalog_visibility --all-pending --apply
else
  echo "VISIBILITY_RECONCILE=SKIPPED_NO_PENDING_BATCHES"
fi

mkdir -p tmp
touch tmp/restart.txt
sleep 4

"$PY" deploy/phase49_verify_runtime.py

echo "PHASE49_PRODUCTION_DEPLOY=OK"
