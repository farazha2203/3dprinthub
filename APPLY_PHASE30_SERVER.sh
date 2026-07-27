#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="${1:-$(pwd)}"
cd "$PROJECT_DIR"
PYTHON_BIN="${PYTHON_BIN:-python}"

$PYTHON_BIN scripts/verify_phase30.py
$PYTHON_BIN -m pip install -r requirements.txt
if [[ -f scripts/ensure_phase29_migration_merge.py ]]; then
  $PYTHON_BIN scripts/ensure_phase29_migration_merge.py
fi
$PYTHON_BIN manage.py migrate
$PYTHON_BIN manage.py makemigrations --check --dry-run
$PYTHON_BIN manage.py collectstatic --noinput
$PYTHON_BIN manage.py check
$PYTHON_BIN manage.py test website.test_phase30_online_payment website.test_phase30_zarinpal_provider website.test_phase28_payment store.test_phase29 --keepdb
$PYTHON_BIN manage.py phase30_payment_audit
$PYTHON_BIN scripts/verify_phase30.py

echo "Phase 30 server deployment completed. Keep the gateway disabled until sandbox callback verification succeeds."
