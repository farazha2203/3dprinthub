# Verified Persistent Reverse Tunnel Commands

Date: 2026-09-13
Status: `EXECUTED SUCCESSFULLY / AUTO_RECONNECT PASS`
Project: `3DPrintHub`

These are the commands that produced the accepted persistent-tunnel result. Secret values are deliberately absent. Before reuse, read `AGENTS.md`, the current project docs and `docs/operations/REVERSE_TUNNEL_REMOTE_MANAGEMENT.md`, then verify the real branch/HEAD/paths/network state.

## 1. cPanel Host — install one-minute watchdog and start/recover now
Run in cPanel Terminal. Strict mode stays inside the subshell so a fail-closed child command cannot kill the parent interactive shell.

```bash
(
set -Eeuo pipefail
umask 077

ROOT="/home/sfkilvrs/3dprinthub"
STATE="/home/sfkilvrs/.config/reverse-host-bridge/3dprinthub"
BRANCH="agent/phase49-3i18-operator-bulk-ai-rebuild"

cd "$ROOT"

echo "===== PRECHECK ====="
echo "ROOT=$(pwd)"
echo "BRANCH=$(git branch --show-current)"
echo "HEAD=$(git rev-parse HEAD)"

test "$(git branch --show-current)" = "$BRANCH"
test -z "$(git status --porcelain --untracked-files=all)"
test -x "$ROOT/scripts/host/phase50_reverse_tunnel_bootstrap.sh"

BASH_BIN="$(command -v bash)"
SSH_BIN="$(command -v ssh)"
FLOCK_BIN="$(command -v flock || true)"
CRONTAB_BIN="$(command -v crontab || true)"

echo "BASH_BIN=$BASH_BIN"
echo "SSH_BIN=$SSH_BIN"
echo "FLOCK_BIN=${FLOCK_BIN:-MISSING}"
echo "CRONTAB_BIN=${CRONTAB_BIN:-MISSING}"

mkdir -p "$STATE"
chmod 700 "$STATE"
touch "$STATE/watchdog.log"
chmod 600 "$STATE/watchdog.log"

[[ -n "$FLOCK_BIN" ]] || { echo "FLOCK_MISSING=YES"; exit 42; }
[[ -n "$CRONTAB_BIN" ]] || { echo "CRONTAB_MISSING=YES"; exit 43; }

TMP_CRON="$(mktemp)"
crontab -l 2>/dev/null \
  | grep -v '3DPrintHub reverse tunnel watchdog' \
  | grep -v 'phase50_reverse_tunnel_bootstrap.sh' \
  > "$TMP_CRON" || true

cat >> "$TMP_CRON" <<EOF
# 3DPrintHub reverse tunnel watchdog
* * * * * $FLOCK_BIN -n $STATE/watchdog.lock $BASH_BIN -lc 'cd $ROOT && WAIT_SECONDS=35 $BASH_BIN scripts/host/phase50_reverse_tunnel_bootstrap.sh >> $STATE/watchdog.log 2>&1'
EOF

crontab "$TMP_CRON"
rm -f "$TMP_CRON"

crontab -l | grep -A1 '3DPrintHub reverse tunnel watchdog'
echo "WATCHDOG_CRON=INSTALLED"

if WAIT_SECONDS=90 "$BASH_BIN" "$ROOT/scripts/host/phase50_reverse_tunnel_bootstrap.sh"; then
    echo "INITIAL_TUNNEL_START=PASS"
else
    BOOT_RC=$?
    echo "INITIAL_TUNNEL_START=WAITING_OR_FAILED"
    echo "BOOTSTRAP_RC=$BOOT_RC"
    echo "CRON_WILL_RETRY_AUTOMATICALLY=YES"
fi

for F in bridge.pid tunnel.pid; do
    if [[ -s "$STATE/$F" ]]; then
        PID="$(cat "$STATE/$F")"
        if kill -0 "$PID" 2>/dev/null; then
            echo "$F=RUNNING pid=$PID"
        else
            echo "$F=NOT_RUNNING old_pid=$PID"
        fi
    else
        echo "$F=NO_PID"
    fi
done

echo "WATCHDOG_READY=YES"
)
RC=$?
echo "CPANEL_PARENT_SHELL_STILL_ALIVE=YES"
echo "SETUP_RC=$RC"
```

Accepted result included `WATCHDOG_CRON=INSTALLED`, `INITIAL_TUNNEL_START=PASS`, running bridge/tunnel PIDs and `SETUP_RC=0`.

## 2. Windows — make OpenSSH persistent
Run from an elevated PowerShell window:

```powershell
$ErrorActionPreference = 'Stop'

Set-Service -Name sshd -StartupType Automatic

if ((Get-Service -Name sshd).Status -ne 'Running') {
    Start-Service -Name sshd
}

sc.exe failure sshd reset= 86400 actions= restart/5000/restart/15000/restart/60000
sc.exe failureflag sshd 1

powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0

Write-Host "===== SSHD ====="
Get-Service sshd | Format-List Name,Status,StartType

Write-Host "===== SSHD RECOVERY ====="
sc.exe qfailure sshd

Write-Host "===== PORT 22024 ====="
netstat -ano | Select-String '127.0.0.1:22024'
```

Accepted result: `sshd` Running/Automatic; service failure actions restart at 5 s, 15 s and 60 s; `127.0.0.1:22024` LISTENING while the tunnel is connected.

## 3. Controlled Host auto-reconnect acceptance test
This test intentionally terminates only the verified 3DPrintHub SSH tunnel process. Do not run it unless the watchdog is installed and the exact process identity guard passes.

```bash
(
set -u

STATE="/home/sfkilvrs/.config/reverse-host-bridge/3dprinthub"
OLD_PID="$(cat "$STATE/tunnel.pid" 2>/dev/null || true)"

[[ -n "$OLD_PID" ]] || { echo "TEST_FAIL=NO_TUNNEL_PID"; exit 41; }
OLD_CMD="$(ps -p "$OLD_PID" -o args= 2>/dev/null || true)"

echo "OLD_TUNNEL_PID=$OLD_PID"
echo "OLD_PROCESS_FOUND=$([[ -n "$OLD_CMD" ]] && echo YES || echo NO)"

case "$OLD_CMD" in
    *"ssh -NT"*"-R 127.0.0.1:22024:127.0.0.1:22224"*)
        echo "OLD_TUNNEL_IDENTITY=PASS"
        ;;
    *)
        echo "TEST_ABORT=PID_IS_NOT_3DPRINTHUB_TUNNEL"
        exit 42
        ;;
esac

BRIDGE_PID="$(cat "$STATE/bridge.pid" 2>/dev/null || true)"
if [[ -n "$BRIDGE_PID" ]] && kill -0 "$BRIDGE_PID" 2>/dev/null; then
    echo "BRIDGE_BEFORE_TEST=RUNNING pid=$BRIDGE_PID"
else
    echo "TEST_ABORT=BRIDGE_NOT_RUNNING"
    exit 43
fi

kill "$OLD_PID"
sleep 2
kill -0 "$OLD_PID" 2>/dev/null && { echo "TEST_FAIL=OLD_TUNNEL_STILL_RUNNING"; exit 44; }

echo "OLD_TUNNEL_KILLED=YES"
echo "WAITING_FOR_CRON_AUTO_RECOVERY=YES"

START="$(date +%s)"
NEW_PID=""
while (( $(date +%s) - START < 150 )); do
    CANDIDATE="$(cat "$STATE/tunnel.pid" 2>/dev/null || true)"
    if [[ -n "$CANDIDATE" && "$CANDIDATE" != "$OLD_PID" ]] && kill -0 "$CANDIDATE" 2>/dev/null; then
        NEW_CMD="$(ps -p "$CANDIDATE" -o args= 2>/dev/null || true)"
        case "$NEW_CMD" in
            *"ssh -NT"*"-R 127.0.0.1:22024:127.0.0.1:22224"*)
                NEW_PID="$CANDIDATE"
                break
                ;;
        esac
    fi
    printf '.'
    sleep 5
done

echo
if [[ -z "$NEW_PID" ]]; then
    echo "AUTO_RECONNECT=FAIL"
    tail -n 80 "$STATE/watchdog.log" 2>/dev/null || true
    exit 75
fi

echo "NEW_TUNNEL_PID=$NEW_PID"
echo "PID_CHANGED=$([[ "$NEW_PID" != "$OLD_PID" ]] && echo YES || echo NO)"
kill -0 "$BRIDGE_PID" 2>/dev/null || { echo "BRIDGE_AFTER_TEST=FAILED"; exit 76; }
echo "BRIDGE_AFTER_TEST=STILL_RUNNING"
echo "AUTO_RECONNECT=PASS"
)
RC=$?
echo "CPANEL_PARENT_SHELL_STILL_ALIVE=YES"
echo "RECONNECT_TEST_RC=$RC"
```

Accepted evidence on 2026-09-13:
- old tunnel PID `2179441`;
- new recovered tunnel PID `367104`;
- bridge PID remained `2086137`;
- `PID_CHANGED=YES`;
- `AUTO_RECONNECT=PASS`;
- `RECONNECT_TEST_RC=0`.

## 4. Windows authenticated post-recovery health
Do not print the token value.

```powershell
Write-Host "===== WINDOWS LOOPBACK ====="
netstat -ano | Select-String '127.0.0.1:22024'

Write-Host "===== AUTHENTICATED BRIDGE ====="
$TokenFile = "$env:LOCALAPPDATA\3DPrintHub\reverse-host-bridge\operator.token"
$env:OPERATOR_BRIDGE_TOKEN = (Get-Content $TokenFile -Raw).Trim()

& "D:\projects\3DPrintHub\scripts\operator\invoke_reverse_host_bridge.ps1" `
    -Port 22024 `
    -Health

Remove-Item Env:OPERATOR_BRIDGE_TOKEN -ErrorAction SilentlyContinue
```

Accepted result after recovery: loopback LISTENING and health `ok=True`, `version=1.0.0`, base `/home/sfkilvrs/3dprinthub`, bridge PID `2086137`.

## 5. Safe status checks
Host:

```bash
STATE="$HOME/.config/reverse-host-bridge/3dprinthub"
crontab -l | grep -A1 '3DPrintHub reverse tunnel watchdog'
for F in bridge.pid tunnel.pid; do
  printf '%s=' "$F"
  cat "$STATE/$F" 2>/dev/null || true
done
tail -n 80 "$STATE/watchdog.log" 2>/dev/null || true
```

Windows:

```powershell
Get-Service sshd | Format-List Name,Status,StartType
sc.exe qfailure sshd
netstat -ano | Select-String '127.0.0.1:22024'
```

## 6. Intentional maintenance shutdown rule
Do not merely kill the tunnel and expect it to stay down: the watchdog is designed to reconnect it. For planned maintenance, first remove/disable only the marked 3DPrintHub watchdog entry from the user's crontab, preserve a copy of the prior crontab, then stop the exact verified tunnel/bridge PIDs. Re-enable the reviewed watchdog afterward and run authenticated health. Never delete the private key/token or broaden the firewall as a routine shutdown step.

## Security rules
- Never commit or paste `operator.token` or the tunnel private key.
- Never expose the Host bridge on a public interface.
- Never broaden the Windows firewall to the Internet to make recovery easier.
- Do not copy another project's source-IP route blindly.
- A public-IP change of `37.255.236.184` requires a separately verified endpoint/DDNS update.
