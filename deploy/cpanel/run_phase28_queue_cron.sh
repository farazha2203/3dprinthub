#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$ROOT/.venv/bin/python}"
mkdir -p "$ROOT/tmp" "$ROOT/logs"
if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Python virtualenv not found: $PYTHON_BIN" >&2
  exit 1
fi
exec 9>"$ROOT/tmp/phase28-link-worker.lock"
if ! flock -n 9; then
  exit 0
fi
cd "$ROOT"
"$PYTHON_BIN" manage.py process_link_analysis_queue --limit 5 >> "$ROOT/logs/link-worker-cron.log" 2>&1
