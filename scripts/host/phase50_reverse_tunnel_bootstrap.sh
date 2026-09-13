#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
PY="/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python"
STATE_DIR="$HOME/.config/reverse-host-bridge/3dprinthub"
TOKEN_FILE="$STATE_DIR/operator.token"
KEY_FILE="$STATE_DIR/windows_tunnel_ed25519"
KNOWN_HOSTS="$STATE_DIR/known_hosts"
BRIDGE_PID="$STATE_DIR/bridge.pid"
BRIDGE_LOG="$STATE_DIR/bridge.log"
TUNNEL_PID="$STATE_DIR/tunnel.pid"
TUNNEL_LOG="$STATE_DIR/tunnel.log"
BRIDGE_PORT=22224
WINDOWS_PORT=22024
WINDOWS_USER="PrintHubTunnel"
WINDOWS_HOST="37.255.236.184"
WINDOWS_SSH_PORT=443
WAIT_SECONDS="${WAIT_SECONDS:-300}"

fail() {
  echo "REVERSE_TUNNEL_BOOTSTRAP_FAIL=$1" >&2
  exit 1
}

cd "$ROOT" || fail "project_root_missing"
[[ -x "$PY" ]] || fail "production_python_missing"
command -v ssh >/dev/null 2>&1 || fail "ssh_client_missing"
command -v ssh-keygen >/dev/null 2>&1 || fail "ssh_keygen_missing"
[[ -x "$ROOT/scripts/operator/start_reverse_host_bridge.sh" ]] || fail "bridge_launcher_missing"
[[ -f "$ROOT/scripts/operator/reverse_host_bridge.py" ]] || fail "bridge_source_missing"

mkdir -p "$STATE_DIR"
chmod 700 "$STATE_DIR"

if [[ ! -s "$TOKEN_FILE" ]]; then
  "$PY" - "$TOKEN_FILE" <<'PY'
from pathlib import Path
import secrets
import sys
path = Path(sys.argv[1])
path.write_text(secrets.token_hex(32), encoding="ascii")
PY
fi
chmod 600 "$TOKEN_FILE"
TOKEN_LEN="$(wc -c < "$TOKEN_FILE" | tr -d '[:space:]')"
[[ "$TOKEN_LEN" == "64" ]] || fail "invalid_token_length"
echo "BRIDGE_TOKEN_FILE=READY"

if [[ ! -s "$KEY_FILE" ]]; then
  ssh-keygen -q -t ed25519 -N '' -f "$KEY_FILE" -C '3dprinthub-host-to-windows-20260913'
elif [[ ! -s "$KEY_FILE.pub" ]]; then
  ssh-keygen -y -f "$KEY_FILE" > "$KEY_FILE.pub"
fi
chmod 600 "$KEY_FILE"
chmod 644 "$KEY_FILE.pub"
FINGERPRINT="$(ssh-keygen -lf "$KEY_FILE.pub" | awk '{print $2}')"
echo "TUNNEL_KEY_FINGERPRINT=$FINGERPRINT"
echo "TUNNEL_PUBLIC_KEY_FILE=$KEY_FILE.pub"
bridge_health() {
  "$PY" - "$TOKEN_FILE" "$BRIDGE_PORT" <<'PY' >/dev/null 2>&1
import json
from pathlib import Path
import sys
from urllib.request import Request, urlopen

token = Path(sys.argv[1]).read_text(encoding="ascii").strip()
port = int(sys.argv[2])
req = Request(
    f"http://127.0.0.1:{port}/health",
    headers={"Authorization": f"Bearer {token}"},
)
with urlopen(req, timeout=3) as response:
    payload = json.load(response)
if response.status != 200 or payload.get("ok") is not True:
    raise SystemExit(1)
PY
}

if bridge_health; then
  echo "HOST_BRIDGE=ALREADY_HEALTHY"
else
  if [[ -f "$BRIDGE_PID" ]]; then
    OLD_BRIDGE_PID="$(cat "$BRIDGE_PID" 2>/dev/null || true)"
    if [[ -n "$OLD_BRIDGE_PID" ]] && kill -0 "$OLD_BRIDGE_PID" 2>/dev/null; then
      fail "existing_bridge_pid_unhealthy"
    fi
  fi
  : > "$BRIDGE_LOG"
  nohup env OPERATOR_BRIDGE_TOKEN_FILE="$TOKEN_FILE" \
    "$ROOT/scripts/operator/start_reverse_host_bridge.sh" \
    "$PY" "$ROOT" "$BRIDGE_PORT" \
    > "$BRIDGE_LOG" 2>&1 < /dev/null &
  NEW_BRIDGE_PID=$!
  printf '%s\n' "$NEW_BRIDGE_PID" > "$BRIDGE_PID"
  sleep 2
  kill -0 "$NEW_BRIDGE_PID" 2>/dev/null || fail "bridge_process_exited"
  bridge_health || fail "bridge_health_failed"
  echo "HOST_BRIDGE=HEALTHY"
fi

start_tunnel_once() {
  : > "$TUNNEL_LOG"
  nohup ssh -NT \
    -p "$WINDOWS_SSH_PORT" \
    -i "$KEY_FILE" \
    -o IdentitiesOnly=yes \
    -o PreferredAuthentications=publickey \
    -o PasswordAuthentication=no \
    -o StrictHostKeyChecking=accept-new \
    -o UserKnownHostsFile="$KNOWN_HOSTS" \
    -o ConnectTimeout=8 \
    -o ExitOnForwardFailure=yes \
    -o ServerAliveInterval=30 \
    -o ServerAliveCountMax=3 \
    -R "127.0.0.1:${WINDOWS_PORT}:127.0.0.1:${BRIDGE_PORT}" \
    "${WINDOWS_USER}@${WINDOWS_HOST}" \
    > "$TUNNEL_LOG" 2>&1 < /dev/null &
  printf '%s\n' "$!" > "$TUNNEL_PID"
}
if [[ -f "$TUNNEL_PID" ]]; then
  OLD_TUNNEL_PID="$(cat "$TUNNEL_PID" 2>/dev/null || true)"
  if [[ -n "$OLD_TUNNEL_PID" ]] && kill -0 "$OLD_TUNNEL_PID" 2>/dev/null; then
    echo "REVERSE_TUNNEL=ALREADY_RUNNING"
    echo "REVERSE_TUNNEL_BOOTSTRAP=PASS"
    exit 0
  fi
fi

DEADLINE=$(( $(date +%s) + WAIT_SECONDS ))
echo "WAITING_FOR_WINDOWS_AUTHORIZED_KEY=YES"
while (( $(date +%s) < DEADLINE )); do
  start_tunnel_once
  NEW_TUNNEL_PID="$(cat "$TUNNEL_PID")"
  sleep 4
  if kill -0 "$NEW_TUNNEL_PID" 2>/dev/null; then
    echo "REVERSE_TUNNEL_PID=$NEW_TUNNEL_PID"
    echo "REVERSE_TUNNEL=RUNNING"
    echo "WINDOWS_LOOPBACK_PORT=$WINDOWS_PORT"
    echo "REVERSE_TUNNEL_BOOTSTRAP=PASS"
    exit 0
  fi
  sleep 6
done

echo "REVERSE_TUNNEL=NOT_CONNECTED_WITHIN_WAIT_WINDOW"
echo "TUNNEL_LOG=$TUNNEL_LOG"
exit 75
