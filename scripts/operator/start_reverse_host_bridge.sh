#!/usr/bin/env bash
set -Eeuo pipefail

if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "usage: $0 <python-bin> <allowed-base-dir> [port]" >&2
  exit 64
fi

PYTHON_BIN="$1"
BASE_DIR="$2"
PORT="${3:-22222}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "python executable not found: $PYTHON_BIN" >&2
  exit 66
fi
if [[ ! -d "$BASE_DIR" ]]; then
  echo "allowed base directory not found: $BASE_DIR" >&2
  exit 66
fi
if [[ -z "${OPERATOR_BRIDGE_TOKEN:-}" && -n "${OPERATOR_BRIDGE_TOKEN_FILE:-}" ]]; then
  if [[ ! -f "$OPERATOR_BRIDGE_TOKEN_FILE" ]]; then
    echo "token file not found" >&2
    exit 66
  fi
  OPERATOR_BRIDGE_TOKEN="$(tr -d '\r\n' < "$OPERATOR_BRIDGE_TOKEN_FILE")"
  export OPERATOR_BRIDGE_TOKEN
fi

if [[ ! "${OPERATOR_BRIDGE_TOKEN:-}" =~ ^[0-9A-Fa-f]{64}$ ]]; then
  echo "OPERATOR_BRIDGE_TOKEN must be 64 hexadecimal characters" >&2
  exit 65
fi

exec "$PYTHON_BIN" \
  "$SCRIPT_DIR/reverse_host_bridge.py" \
  --host 127.0.0.1 \
  --port "$PORT" \
  --base "$BASE_DIR"
