# 3DPrintHub Reverse Tunnel SSH — Persistent Operations

Date: 2026-09-13
Status: `E2E_VERIFIED / AUTO_RECONNECT_VERIFIED / ACCEPTED`
Acceptance baseline: `443d1b70ecdf59e26b106d8887d56cb0e61ece8d`

## Purpose
This folder is the canonical operations record for the persistent reverse SSH management path used by 3DPrintHub. It supplements `docs/operations/REVERSE_TUNNEL_REMOTE_MANAGEMENT.md`; it does not replace project governance, GitHub-first delivery, backup/rollback, migration safety or Production verification.

## Verified architecture
`Host 89.39.208.237 -> outbound SSH/443 -> Windows 37.255.236.184 -> OpenSSH PrintHubTunnel -> Windows 127.0.0.1:22024 -> reverse forward -> Host 127.0.0.1:22224 -> authenticated loopback command bridge`.

Canonical identities and ports:
- Host account: `sfkilvrs` on `nphost4.parsblog.com`.
- Production root: `/home/sfkilvrs/3dprinthub`.
- Host bridge: `127.0.0.1:22224`.
- Windows operator loopback: `127.0.0.1:22024`.
- Windows tunnel account: `PrintHubTunnel`.
- Windows public endpoint: `37.255.236.184:443/tcp`.
- Windows LAN SSH target: `192.168.0.23:22`.
- Windows firewall source restriction: `89.39.208.237/32`.

## Persistence layers
1. `scripts/host/phase50_reverse_tunnel_bootstrap.sh` is idempotent and health-checks/restarts the Host bridge and reverse SSH process.
2. cPanel cron runs the bootstrap every minute under `flock`; concurrent recovery attempts are rejected.
3. SSH keepalive is already enforced by the bootstrap: `ServerAliveInterval=30`, `ServerAliveCountMax=3`, and `ExitOnForwardFailure=yes`.
4. Windows OpenSSH `sshd` is `Running` and `Automatic`.
5. Windows service recovery restarts `sshd` after 5 s, 15 s and 60 s failures, with a 86400 s reset period.
6. Windows AC sleep and hibernate timeouts are disabled so a powered development PC does not suspend the endpoint.

## Verified persistence evidence
The acceptance deliberately terminated only the exact 3DPrintHub reverse SSH process after verifying its command contained `ssh -NT` and `-R 127.0.0.1:22024:127.0.0.1:22224`.

Evidence:
- bridge PID before test: `2086137`;
- original tunnel PID: `2179441`;
- original tunnel terminated successfully;
- cPanel watchdog recovered a new tunnel PID: `367104`;
- PID changed: `YES`;
- bridge remained alive at PID `2086137`;
- `AUTO_RECONNECT=PASS`;
- `RECONNECT_TEST_RC=0`;
- Windows `127.0.0.1:22024` returned to `LISTENING`;
- authenticated health after recovery returned `ok=True`, bridge version `1.0.0`, base `/home/sfkilvrs/3dprinthub`.

This proves real recovery after tunnel-process loss; it is not only a configuration claim.

## Private state
Host private state remains outside Git under:
`/home/sfkilvrs/.config/reverse-host-bridge/3dprinthub/`

Important non-secret operational paths:
- `bridge.pid`
- `tunnel.pid`
- `bridge.log`
- `tunnel.log`
- `watchdog.log`
- `watchdog.lock`

Windows protected token path:
`C:\Users\Emad-PC\AppData\Local\3DPrintHub\reverse-host-bridge\operator.token`

Never commit or paste the token, tunnel private key, passwords or bearer values. Public-key material itself is not needed in documentation either.

## Recovery expectations
A dead reverse SSH process is normally recovered on the next one-minute cron pass plus bootstrap connection time. A crashed Windows `sshd` is covered by Windows service recovery. Closing the cPanel browser/Terminal does not remove the detached Host processes or the cron watchdog.

If an operator intentionally wants the tunnel to remain down, the watchdog must be disabled first; otherwise it is expected to reconnect it.

## Not covered by this acceptance
The configured endpoint still uses public IP `37.255.236.184`. A future ISP public-IP change is not solved by the current watchdog. If that address is not static, add a separately verified DDNS design rather than guessing a hostname or weakening firewall rules.

## Canonical files
- `docs/operations/REVERSE_TUNNEL_REMOTE_MANAGEMENT.md`
- `docs/operations/reverse-tunnel-ssh/README.md`
- `docs/operations/reverse-tunnel-ssh/VERIFIED_PERSISTENCE_COMMANDS.md`
- `scripts/host/phase50_reverse_tunnel_bootstrap.sh`
- `scripts/operator/reverse_host_bridge.py`
- `scripts/operator/start_reverse_host_bridge.sh`
- `scripts/operator/invoke_reverse_host_bridge.ps1`

## Security / governance
The persistent tunnel is only a transport. Permanent source edits on Production remain forbidden. All application changes still follow:
`READ DOCS -> VERIFY STATE -> CHECK PREVIOUS ERRORS -> IMPLEMENT -> TEST LOCAL/CI -> DOCUMENT -> COMMIT/PUSH -> DEPLOY FROM GITHUB -> VERIFY PRODUCTION`.
