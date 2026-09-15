## Permanent operator rule — 2026-09-15
This transport is the normal Production execution path for 3DPrintHub. ChatGPT operates the Local repository through the connected Windows Remote Desktop device and operates Production through this dedicated reverse tunnel. When `127.0.0.1:22024` is healthy, routine Host/deploy commands must be executed through the tunnel rather than handed to the owner. The one-minute cPanel cron watchdog is mandatory; owner-side cPanel bootstrap is break-glass recovery only.

# Reverse SSH Remote Management Standard

Date: 2026-09-13
Status: `E2E_VERIFIED / PERSISTENT_WATCHDOG_VERIFIED / AUTO_RECONNECT_ACCEPTED`

## Purpose
This runbook standardizes a secure reverse-management transport between the verified Windows development PC and the 3DPrintHub shared Host. It is transport only and never replaces repository governance, GitHub-first delivery, release gates, backup/rollback, database safety or Production acceptance.

## Mandatory workflow
`READ DOCS -> VERIFY STATE -> CHECK PREVIOUS ERRORS -> IMPLEMENT -> TEST LOCAL/CI -> DOCUMENT -> COMMIT/PUSH -> HOST FROM GITHUB -> VERIFY PRODUCTION`

Permanent source edits directly on Production remain forbidden. Private keys, passwords, bearer tokens and provider secrets must never be committed.

## Architecture
Verified shared-cPanel path:
`Host 89.39.208.237 -> outbound SSH/443 -> Windows 37.255.236.184 -> OpenSSH PrintHubTunnel -> Windows 127.0.0.1:22024 -> reverse forward -> Host 127.0.0.1:22224 -> authenticated loopback bridge`.

The repository bridge binds only to `127.0.0.1`. Its cwd guard is not a filesystem sandbox; commands retain the permissions of the Host account running the bridge.

## Project profile
- Project: `3DPrintHub`.
- Repository: `farazha2203/3dprinthub`.
- Canonical branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`.
- Persistence acceptance baseline: `443d1b70ecdf59e26b106d8887d56cb0e61ece8d`.
- Host: `nphost4.parsblog.com`.
- Host account: `sfkilvrs`.
- Repository root: `/home/sfkilvrs/3dprinthub`.
- Host Python: `/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python`.
- Windows loopback port: `22024`.
- Host bridge loopback port: `22224`.
- Mode: `shared-cpanel-bridge`.
- Activation status: **E2E VERIFIED / AUTO-RECONNECT VERIFIED / ACTIVE**.
- Host source IP: `89.39.208.237`.
- Windows public endpoint: `37.255.236.184:443/tcp`.
- Windows LAN SSH target: `192.168.0.23:22`.
- Windows tunnel identity: `PrintHubTunnel`.

## First-use onboarding gate
1. Re-read repository governance and current Host docs.
2. Verify Host identity, repository root, branch/HEAD/worktree, Python and current source IP read-only.
3. Verify Windows public endpoint and LAN target; never copy another project's source-IP rule blindly.
4. Verify Windows OpenSSH Server and the dedicated non-admin tunnel account/key.
5. Verify MikroTik DNAT and Windows Firewall remain source-restricted to the exact Host IP.
6. On multi-WAN/PBR networks, verify the return path exits through the same WAN that received the inbound DNAT.
7. Prove TCP/443 -> Windows SSH and only then start the project tunnel.
8. Prove authenticated loopback health/identity before any Git, deploy, DB or filesystem action.

## First-use bootstrap
After the approved operations commit exists on the verified Host checkout:

```bash
cd /home/sfkilvrs/3dprinthub
WAIT_SECONDS=300 /bin/bash scripts/host/phase50_reverse_tunnel_bootstrap.sh
```

Protected Host state lives below `$HOME/.config/reverse-host-bridge/3dprinthub/`. The runner never prints the token or private key. It health-checks/starts the bridge on `127.0.0.1:22224`, then health-checks/starts outbound SSH/443 with remote forward `127.0.0.1:22024:127.0.0.1:22224`. It performs no Git merge, migration, database write, collectstatic or Passenger restart.

## Persistent self-healing operation
The accepted Production operations profile adds a one-minute cPanel cron watchdog guarded by `flock`:

```cron
# 3DPrintHub reverse tunnel watchdog
* * * * * /bin/flock -n /home/sfkilvrs/.config/reverse-host-bridge/3dprinthub/watchdog.lock /bin/bash -lc 'cd /home/sfkilvrs/3dprinthub && WAIT_SECONDS=35 /bin/bash scripts/host/phase50_reverse_tunnel_bootstrap.sh >> /home/sfkilvrs/.config/reverse-host-bridge/3dprinthub/watchdog.log 2>&1'
```

The bootstrap is idempotent: when the bridge/tunnel are healthy it exits successfully without starting duplicates; when the tunnel process is gone the next watchdog pass creates a new SSH process. `flock -n` prevents overlapping recovery attempts.

SSH process health is also bounded by `ExitOnForwardFailure=yes`, `ServerAliveInterval=30`, and `ServerAliveCountMax=3`.

Windows persistence is independently configured:
- `sshd` service status `Running`;
- startup type `Automatic`;
- service failure recovery restarts after 5 s, 15 s, then 60 s;
- AC sleep and hibernate timeouts are disabled for this always-available endpoint.

Canonical successful commands and the acceptance test are stored in `docs/operations/reverse-tunnel-ssh/VERIFIED_PERSISTENCE_COMMANDS.md`.

## Auto-reconnect acceptance evidence
A deliberate test verified the exact running SSH process contained the 3DPrintHub forward `-R 127.0.0.1:22024:127.0.0.1:22224`, then terminated only that tunnel PID.

Observed result:
- original tunnel PID `2179441` terminated;
- Host bridge PID `2086137` remained alive;
- watchdog recovered tunnel PID `367104`;
- `PID_CHANGED=YES`;
- `AUTO_RECONNECT=PASS`;
- `RECONNECT_TEST_RC=0`;
- Windows `127.0.0.1:22024` returned to LISTENING;
- authenticated bridge health returned `ok=True`, version `1.0.0`, base `/home/sfkilvrs/3dprinthub`.

Therefore persistence is accepted from real process-loss recovery evidence, not merely configuration inspection.

## Windows operator verification
Load the project token only from its protected local file and remove the environment variable afterward:

```powershell
$TokenFile = "$env:LOCALAPPDATA\3DPrintHub\reverse-host-bridge\operator.token"
$env:OPERATOR_BRIDGE_TOKEN = (Get-Content $TokenFile -Raw).Trim()
& "D:\projects\3DPrintHub\scripts\operator\invoke_reverse_host_bridge.ps1" -Port 22024 -Health
Remove-Item Env:OPERATOR_BRIDGE_TOKEN -ErrorAction SilentlyContinue
```

A read-only identity probe remains mandatory before sensitive operations:

```powershell
$TokenFile = "$env:LOCALAPPDATA\3DPrintHub\reverse-host-bridge\operator.token"
$env:OPERATOR_BRIDGE_TOKEN = (Get-Content $TokenFile -Raw).Trim()
& "D:\projects\3DPrintHub\scripts\operator\invoke_reverse_host_bridge.ps1" -Port 22024 -Command 'whoami; hostname; pwd; git branch --show-current; git rev-parse HEAD; git status --short' -Cwd '/home/sfkilvrs/3dprinthub'
Remove-Item Env:OPERATOR_BRIDGE_TOKEN -ErrorAction SilentlyContinue
```

Only after identity/branch/HEAD/status match current repository docs may project-specific gates or deploy runners be executed.

## Private operational paths
Host private state:
`/home/sfkilvrs/.config/reverse-host-bridge/3dprinthub/`

Operational files include `operator.token`, `windows_tunnel_ed25519`, `known_hosts`, `bridge.pid`, `bridge.log`, `tunnel.pid`, `tunnel.log`, `watchdog.lock` and `watchdog.log`. Secret contents stay outside Git/chat.

Windows protected token:
`C:\Users\Emad-PC\AppData\Local\3DPrintHub\reverse-host-bridge\operator.token`.

## Intentional maintenance / teardown
Because the watchdog is now active, killing the tunnel alone is not a teardown: it is expected to reconnect. For planned downtime, first preserve the existing crontab and disable/remove only the marked `3DPrintHub reverse tunnel watchdog` entry, then verify and stop only the exact tunnel/bridge PIDs. Do not delete keys/tokens or widen/remove unrelated firewall/routing rules as routine maintenance.

When re-enabling, restore the reviewed watchdog entry and require authenticated health plus Host identity before operations.

## Failure rules
- Do not rerun an unchanged failed tunnel command.
- If Host TCP/443 cannot reach Windows, classify DNAT, source-IP firewall and multi-WAN return path before changing SSH.
- A SYN entering one WAN while Windows replies through another WAN is an asymmetric-route failure, not an OpenSSH failure.
- Never broaden Windows SSH firewall exposure to make a test pass.
- Never expose the bridge on `0.0.0.0` or a public Host interface.
- Running `sshd -t` unelevated on this Windows machine can return 255 because protected host private keys are unreadable to the caller; service/listener/Event Log or elevated validation determines actual health.
- If public Windows IP `37.255.236.184` changes, current watchdog retries the old verified address. DDNS/endpoint rotation is a separate future task and must be verified before use.

## Asal-proven network pattern
The original Asal reference proved the same Windows public TCP/443 and LAN target `192.168.0.23:22` from Asal Host IP `89.32.249.147`. 3DPrintHub independently proved its own source `89.39.208.237/32` and loopback `22024`. Do not copy Asal's `/32` route or firewall source blindly.

## Repository-owned files
- `scripts/operator/reverse_host_bridge.py`
- `scripts/operator/start_reverse_host_bridge.sh`
- `scripts/operator/invoke_reverse_host_bridge.ps1`
- `scripts/host/phase50_reverse_tunnel_bootstrap.sh`
- `docs/operations/REVERSE_TUNNEL_REMOTE_MANAGEMENT.md`
- `docs/operations/reverse-tunnel-ssh/README.md`
- `docs/operations/reverse-tunnel-ssh/VERIFIED_PERSISTENCE_COMMANDS.md`

No database migration, dependency change or application business-runtime mutation is part of the persistence setup itself.
