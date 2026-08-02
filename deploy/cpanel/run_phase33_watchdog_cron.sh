#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_ROOT="/home/sfkilvrs/3dprinthub"
PYTHON_BIN="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
LOG_DIR="$PROJECT_ROOT/logs"

mkdir -p "$LOG_DIR"
cd "$PROJECT_ROOT"
exec "$PYTHON_BIN" manage.py automation_watchdog
