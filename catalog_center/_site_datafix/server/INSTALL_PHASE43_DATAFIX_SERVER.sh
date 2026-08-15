#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIXER="${HERE}/phase43_catalog_metrics_datafix.py"
MODE="${1:---dry-run}"

fail() {
    echo "STOP: $*" >&2
    exit 2
}

[[ -d "$ROOT" ]] || fail "Production project root missing: $ROOT"
[[ -x "$PY" ]] || fail "Production Python missing: $PY"
[[ -f "$ROOT/manage.py" ]] || fail "manage.py missing"
[[ -f "$ROOT/store/models.py" ]] || fail "store/models.py missing"
[[ -f "$ROOT/store/management/commands/phase37_import_catalog_center.py" ]] || \
    fail "Phase37 catalog-center importer missing"
[[ -f "$FIXER" ]] || fail "Datafix script missing"

cd "$ROOT"

echo "=== Phase 43.1 catalog metrics datafix preflight ==="
"$PY" manage.py check

echo "=== Dry-run ==="
"$PY" "$FIXER" --project-root "$ROOT"

case "$MODE" in
    --dry-run)
        echo "PHASE43_SERVER_DATAFIX=DRY_RUN_ONLY"
        ;;
    --apply)
        echo "=== Applying safe repairs ==="
        "$PY" "$FIXER" --project-root "$ROOT" --apply
        echo "=== Django post-check ==="
        "$PY" manage.py check
        echo "DATABASE_MIGRATION=NOT_RUN"
        echo "PHASE43_SERVER_DATAFIX=APPLIED_OK"
        ;;
    *)
        fail "Usage: $0 [--dry-run|--apply]"
        ;;
esac
