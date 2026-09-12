# Reverse SSH Remote Management Standard

Date: 2026-09-12
Status: repository-published operator standard; Production runtime unchanged.

## Purpose
This runbook standardizes a secure reverse-management transport between the verified Windows development PC and a project Host. It is transport only and never replaces repository governance, GitHub-first delivery, release gates, backup/rollback, database safety or Production acceptance.

## Mandatory workflow
`READ DOCS -> VERIFY STATE -> CHECK PREVIOUS ERRORS -> IMPLEMENT -> TEST LOCAL -> COMMIT/PUSH -> HOST FROM GITHUB -> VERIFY PRODUCTION -> UPDATE DOCS`

Permanent source edits directly on Production remain forbidden. Private keys, passwords, bearer tokens and provider secrets must never be committed.

## Architecture
Shared cPanel Host without a usable local sshd:
`Windows 127.0.0.1:<project-port> -> encrypted SSH -R -> Host 127.0.0.1:22222 -> authenticated loopback bridge -> Host shell`.

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
- Windows loopback port: `22023`.
- Host bridge port: `22222` for shared-host mode only.
- Mode: `shared-cpanel-bridge`.
- Activation status: **PROFILE RESERVED; first-use source-IP/firewall/PBR/tunnel acceptance pending**.
- Host source IP: `VERIFY BEFORE USE`.
- Windows public endpoint: `VERIFY CURRENT WINDOWS PUBLIC ENDPOINT BEFORE USE`.

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

## Shared-host session start
After the approved commit containing these scripts exists on the Host checkout, start the bridge as a child process from the verified repository root. Never enable `set -e` in the parent interactive cPanel shell.

```bash
cd <VERIFIED_REPOSITORY_ROOT>
export OPERATOR_BRIDGE_TOKEN_FILE="$HOME/.config/reverse-host-bridge/<project>.token"
scripts/operator/start_reverse_host_bridge.sh <VERIFIED_PYTHON> <VERIFIED_REPOSITORY_ROOT> 22222
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
  -R 127.0.0.1:22023:127.0.0.1:22222 \
  <WINDOWS_TUNNEL_USER>@<VERIFIED_WINDOWS_PUBLIC_IP>
```

## Windows operator verification
Load the project bridge token into the current PowerShell process from its protected local file, then verify health before command execution.

```powershell
$env:OPERATOR_BRIDGE_TOKEN = (Get-Content '<PROTECTED_PROJECT_TOKEN_FILE>' -Raw).Trim()
& scripts/operator/invoke_reverse_host_bridge.ps1 -Port 22023 -Health
```

A read-only identity probe should be the first command:

```powershell
& scripts/operator/invoke_reverse_host_bridge.ps1 -Port 22023 -Command 'whoami; hostname; pwd; git status --short --branch' -Cwd '<VERIFIED_REPOSITORY_ROOT>'
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

## Repository-owned files
- `scripts/operator/reverse_host_bridge.py`
- `scripts/operator/start_reverse_host_bridge.sh`
- `scripts/operator/invoke_reverse_host_bridge.ps1`
- `docs/operations/REVERSE_TUNNEL_REMOTE_MANAGEMENT.md`

No database migration, dependency change, application runtime change or Production deploy is part of publishing this operations standard.
