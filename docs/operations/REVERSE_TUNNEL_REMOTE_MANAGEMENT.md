# Reverse SSH Remote Management Standard

Date: 2026-09-13
Status: repository profile local-tested; Windows side ready; Host E2E onboarding next.

## Purpose
This runbook standardizes a secure reverse-management transport between the verified Windows development PC and a project Host. It is transport only and never replaces repository governance, GitHub-first delivery, release gates, backup/rollback, database safety or Production acceptance.

## Mandatory workflow
`READ DOCS -> VERIFY STATE -> CHECK PREVIOUS ERRORS -> IMPLEMENT -> TEST LOCAL -> COMMIT/PUSH -> HOST FROM GITHUB -> VERIFY PRODUCTION -> UPDATE DOCS`

Permanent source edits directly on Production remain forbidden. Private keys, passwords, bearer tokens and provider secrets must never be committed.

## Architecture
Shared cPanel Host without a usable local sshd:
`Windows 127.0.0.1:<project-port> -> encrypted SSH -R -> Host 127.0.0.1:22224 -> authenticated loopback bridge -> Host shell`.

VPS/Host with a verified local sshd:
`Windows 127.0.0.1:<project-port> -> encrypted SSH -R -> Host 127.0.0.1:22`.

The repository bridge binds only to 127.0.0.1. Its cwd guard is not a filesystem sandbox; commands retain the permissions of the Host account running the bridge.

## Project profile
- Project: `3DPrintHub`.
- Repository: `farazha2203/3dprinthub`.
- Host: `nphost4.parsblog.com`.
- Host account: `sfkilvrs`.
- Verified/declared repository root: `/home/sfkilvrs/3dprinthub`.
- Host Python for bridge: `/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python`.
- Windows loopback port: `22024`.
- Host bridge port: `22224` for shared-host mode only.
- Mode: `shared-cpanel-bridge`.
- Activation status: **WINDOWS SIDE READY / REPOSITORY PROFILE LOCAL-TESTED / HOST E2E ONBOARDING NEXT**.
- Host source IP: `89.39.208.237`.
- Windows public endpoint: `37.255.236.184:443/tcp`.

Reserved loopback ports are coordination metadata only. A reserved port is not proof that a tunnel, firewall rule or Host listener is active.

## First-use onboarding gate
1. Re-read repository governance and current Host docs.
2. Verify Host identity, user, repository root, Python/sshd availability and current source IP read-only.
3. Verify Windows public endpoint and LAN target; never copy another project's source-IP rule blindly.
4. Verify Windows OpenSSH Server and the dedicated non-admin tunnel account/key.
5. Verify MikroTik DNAT and Windows Firewall are source-restricted to the exact Host IP.
6. On multi-WAN/PBR networks, verify the return path exits through the same WAN that received the inbound DNAT.
7. Prove TCP/443 -> Windows SSH and only then start the project tunnel.
8. Prove loopback health/identity before any Git, deploy, DB or filesystem action.

## 3DPrintHub first-use bootstrap
After the approved operations-only commit is ff-only merged on the verified Host checkout, use the repository bootstrap runner:

```bash
cd /home/sfkilvrs/3dprinthub
WAIT_SECONDS=300 scripts/host/phase50_reverse_tunnel_bootstrap.sh
```

Protected Host state is created below `$HOME/.config/reverse-host-bridge/3dprinthub/`: `operator.token`, `windows_tunnel_ed25519`, its `.pub`, dedicated `known_hosts`, PID files and bounded operational logs. The runner never prints the token or private key. It starts the bridge on `127.0.0.1:22224`, then retries the outbound Windows SSH connection while the generated public key is installed into the dedicated Windows authorized-key file. It performs no Git merge, database operation, collectstatic or Passenger restart.

## Shared-host session start
After the approved commit containing these scripts exists on the Host checkout, start the bridge as a child process from the verified repository root. Never enable `set -e` in the parent interactive cPanel shell.

```bash
cd <VERIFIED_REPOSITORY_ROOT>
export OPERATOR_BRIDGE_TOKEN_FILE="$HOME/.config/reverse-host-bridge/<project>.token"
scripts/operator/start_reverse_host_bridge.sh <VERIFIED_PYTHON> <VERIFIED_REPOSITORY_ROOT> 22224
```

The token file must be outside Git, owned by the Host account and mode 0600. Provision the same 64-hex token into the Windows operator credential/token file outside the repository.

In a second Host terminal, start the reverse forward. Use the project-specific Windows user/key and verified Windows public endpoint; placeholders are deliberate until onboarding proves them.

```bash
ssh -NT -p 443 -i <DEDICATED_TUNNEL_PRIVATE_KEY> \
  -o IdentitiesOnly=yes \
  -o PreferredAuthentications=publickey \
  -o PasswordAuthentication=no \
  -o ExitOnForwardFailure=yes \
  -o ServerAliveInterval=30 \
  -o ServerAliveCountMax=3 \
  -R 127.0.0.1:22024:127.0.0.1:22224 \
  <WINDOWS_TUNNEL_USER>@<VERIFIED_WINDOWS_PUBLIC_IP>
```

## Windows operator verification
Load the project bridge token into the current PowerShell process from its protected local file, then verify health before command execution.

```powershell
$env:OPERATOR_BRIDGE_TOKEN = (Get-Content '<PROTECTED_PROJECT_TOKEN_FILE>' -Raw).Trim()
& scripts/operator/invoke_reverse_host_bridge.ps1 -Port 22024 -Health
```

A read-only identity probe should be the first command:

```powershell
& scripts/operator/invoke_reverse_host_bridge.ps1 -Port 22024 -Command 'whoami; hostname; pwd; git status --short --branch' -Cwd '<VERIFIED_REPOSITORY_ROOT>'
```

Only after identity/branch/HEAD/status match the current repository docs may project-specific gates or deploy runners be executed. The tunnel never grants permission to skip backup, migration, release or rollback checks.

## Teardown
Stop the foreground `ssh -NT` process and the foreground bridge process. Confirm the Windows project loopback port is no longer LISTENING. Do not delete keys, firewall rules or route exceptions as part of ordinary session teardown.

## Failure rules
- Do not rerun an unchanged failed tunnel command.
- If Host TCP/443 cannot reach Windows, classify DNAT, source-IP, Windows firewall and multi-WAN return-path state before changing SSH.
- A SYN arriving on one WAN with the Windows reply policy-routed out another WAN is an asymmetric-route failure, not an OpenSSH failure.
- Never broaden the Windows SSH firewall to the Internet just to make a test pass.
- Never expose the bridge on 0.0.0.0 or a public Host interface.

## Asal-proven network pattern to reproduce for 3DPrintHub
The Asal reference path proved the same Windows public TCP/443 and LAN target `192.168.0.23:22`, but from Asal Host source IP `89.32.249.147`. 3DPrintHub must reproduce that path from its own Host source IP `89.39.208.237` and use Windows loopback `22024`.
The decisive blocker was asymmetric return routing: traffic entered the FTTH WAN, while source policy for `192.168.0.23/32` selected table `FTTH-2` whose default was `FTTH-Tejari`. A narrow Host `/32` route in that policy table returned replies through FTTH and made TCP/443 PASS.
Do not reuse the Asal `/32` route unchanged. If the same asymmetric return-routing condition appears, add/verify only the 3DPrintHub Host `/32` (`89.39.208.237/32`) in the currently active policy table after inspecting current MikroTik routing/mangle state.

## Repository-owned files
- `scripts/operator/reverse_host_bridge.py`
- `scripts/operator/start_reverse_host_bridge.sh`
- `scripts/operator/invoke_reverse_host_bridge.ps1`
- `scripts/host/phase50_reverse_tunnel_bootstrap.sh`
- `docs/operations/REVERSE_TUNNEL_REMOTE_MANAGEMENT.md`

No database migration, dependency change, application runtime change or Production deploy is part of publishing this operations standard.
