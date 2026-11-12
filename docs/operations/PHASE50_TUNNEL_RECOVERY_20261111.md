# 2026-11-11 - Production reverse SSH tunnel outage / recovery gate

## Evidence (read-only; no credentials exported)
- On Windows `EMAD-NEWCOM`, `sshd` is Running / Automatic and listens on TCP 22. Other project reverse ports 22022, 22023, and 22026 reappeared, while the dedicated 3DPrintHub reverse port `127.0.0.1:22024` remains unavailable.
- The 3DPrintHub gateway `D:\projects\.chatgpt-gateway\project-host.ps1 -Project 3dprinthub -Health` fails with connection unavailable. Host project execution is **not operational**.
- Windows OpenSSH Operational events confirm other projects reconnecting from known source hosts, but no successful `PrintHubTunnel` authentication in the recent log. Previous recorded PrintHub tunnel login was 2026-11-09, so the common Windows SSH listener and forwarding infrastructure are not the sole issue.
- A read-only transfer via the saved WinSCP site `3DPrintHub-FTPS` could list `/.config/reverse-host-bridge/3dprinthub/`. Host `tunnel.log` (2026-11-11 08:42:50) says `Connection reset by peer` / `Broken pipe`; `watchdog.log` was last updated 2026-11-09 14:00:13, despite the documented per-minute cron. This suggests the project's cron watchdog may no longer be firing, but **its current crontab was not accessible for verification**.
- Read-only retrieval of `/3dprinthub/.git/HEAD` and the active branch ref confirmed Host SHA `0ae8d7851b803ddc8ab75be3adf35ac2a2d76a5a`; new dual-approval candidate `d13379b2891a85fec762bda79c08f85bb4d529a8` was **not deployed**. Database migration state could not be independently reread while project tunnel is unavailable. Last successful live DB check (preceding turn) had no migration pending and no dual-approval migration applied.
- Direct SSH from the Windows PC to the project's host using its project-specific key on TCP 23 timed out. This is a connectivity test only and did not change server state.
- No SSH keys, operator tokens, private configuration, original payments, customer data, product inventory or production files were altered as part of these diagnostics. Never copy another project's reverse tunnel to circumvent isolation.

## Authorized break-glass restoration (cPanel Terminal, on 3DPrintHub host only)
Use the documented, already deployed transport-only bootstrap to restart the project's authenticated reverse bridge/tunnel. This command does **not** deploy code or run migrations:

```bash
cd /home/sfkilvrs/3dprinthub && WAIT_SECONDS=35 /bin/bash scripts/host/phase50_reverse_tunnel_bootstrap.sh
```

Then review 3DPrintHub's cPanel **Cron Jobs** entry: the documented **per-minute** watchdog must exist and write to the project-specific watchdog log, and logs should continue to update. The known safe entry is in `docs/operations/REVERSE_TUNNEL_REMOTE_MANAGEMENT.md`; use the installed existing entry if it is still present, rather than creating a duplicate. Do not expose any Host bridge port publicly or broaden SSH firewall IP allowlists.

After successful recovery, verify from the authorized Windows PC:
```powershell
& 'D:\projects\.chatgpt-gateway\project-host.ps1' -Project 3dprinthub -Health
```
Then perform the exact Host Git SHA, project root/DB identity, no-unexpected-pending-migration, and financial/stock baseline checks. Only **then** consider the guarded, SHA-pinned dual-approval release. Full verified source/.env/MySQL backup, exact two-migration allowlist, before/after financial/3798-variant fingerprint, finance reconciliation and public/admin read-only smoke are mandatory.

## Release candidate still awaiting Host acceptance
GitHub branch `fix/service-store-refund-dual-approval-20261111`, SHA `d13379b2891a85fec762bda79c08f85bb4d529a8` (the new documentation update may advance the branch further without changing executable code). Local final finance/checkout/regression: 188/188 PASS. Previous Host publish stopped safely before any migration because an ORM fingerprint referenced a computed Quote property; fixed in the new script and confirmed by local schema checks. While the tunnel is down **do not** attempt a bypass deployment via FTP or any other unverified channel.

## 2026-11-11 15:51 local diagnosis - inherited flock descriptor likely blocks auto-reconnect

**Reproduction:** The documented cron uses `/bin/flock -n LOCK /bin/bash -lc '... bootstrap ...'`; the bootstrap launches both a long-lived bridge and SSH via `nohup ... &` without closing the inherited lock FD. With the same pattern under Linux util-linux `flock`, a detached `nohup sleep` kept the watchdog lock held after its parent shell exited (`LOCK_HELD_BY_DAEMON=yes`). Replacing cron invocation with `flock -n -o LOCK ...` made the lock immediately acquirable while the daemon was still alive (`WITH_FLOCK_CLOSE_REACQUIRED_WHILE_DAEMON_ALIVE=yes`). Closing fd 3 for each child was also independently verified to release the inherited lock.

**Evidence suggesting this is happening on 3DPrintHub (not yet confirmed on Host):** the project watchdog.log stopped advancing on 2026-11-09 at 14:00, exactly when the persistent PrintHubTunnel session began; the separate tunnel.log later records connection reset/broken pipe on 2026-11-11 08:42. Windows sshd remains healthy and other projects' reverse ports are listening, but PrintHub 22024 has not returned. The possible bridge process may still hold the original `flock` inode. No cPanel Terminal / live `flock` inspection was available in this session to conclusively verify the lock holder.

**Source fix staged locally (NOT deployed yet):**
- `scripts/host/phase50_reverse_tunnel_bootstrap.sh`: close inherited fd 3 on the detached bridge and SSH launches, preserving all original hostname, port, keys and permissions.
- `docs/operations/REVERSE_TUNNEL_REMOTE_MANAGEMENT.md`: change the cPanel cron example to `/bin/flock -n -o` (the documented `--close` option), preventing lock inheritance generically.
- `scripts/host/phase50_refund_dual_approval_deploy.sh`: allow only that exact additional transport script in the gated changed-file list. No new external transfer, no bank API or live database changes.
- `bash -n` passes for both modified scripts; `git diff --check` passes.

**Operational recovery sequence (through authenticated cPanel Terminal on this Host only):**
1. Read-only check: `/bin/flock -n /home/sfkilvrs/.config/reverse-host-bridge/3dprinthub/watchdog.lock /bin/true && echo WATCHDOG_LOCK_FREE || echo WATCHDOG_LOCK_BUSY`.
2. Verify whether current Cron Jobs contains the project's documented per-minute watchdog (not a duplicate or a similarly named different-project task).
3. Update **that 3DPrintHub entry only** to add `-o` after `flock -n`. This change is required in the actual cPanel Cron Jobs UI; committing the docs does not update live Cron.
4. Run the existing transport-only bootstrap outside the lock: `cd /home/sfkilvrs/3dprinthub && WAIT_SECONDS=35 /bin/bash scripts/host/phase50_reverse_tunnel_bootstrap.sh`.
5. If the lock remains busy after recovery, inspect the lock-holder PID carefully before any project-specific controlled restart. Do not kill any process based on a stale PID file alone, disable firewall or borrow another project's reverse tunnel.
6. Verify port 22024 and authenticated `project-host.ps1 -Health` from Windows; only then consider the separate financially gated release with fresh full backup, two migrations and exact money/stock hash.

**Important:** Neither this document nor the script fix has been applied to the current Host. Latest FTP read-only HEAD `0ae8d7851b803ddc8ab75be3adf35ac2a2d76a5a` and local pending release SHA `d13379b2891a85fec762bda79c08f85bb4d529a8`; after this source fix the deploy candidate SHA will change. Avoid claiming the feature is live.

## 2026-11-12 12:23 Europe/Istanbul / 12:23 office clock — follow-up diagnostics, no host execution

- Connected Emad-NewCom is online; Windows sshd is Running (Automatic), but reverse listener ports 22022-22027, including 3DPrintHub's isolated 22024, are absent. The authenticated project-host.ps1 health check reports remote-server connection unavailable.
- FTPS (read-only) succeeds. Exact Host release branch ref is still 0ae8d7851b803ddc8ab75be3adf35ac2a2d76a5a; new dual-approval source remains on its separate GitHub branch and was NOT published. FTP ref verification does not establish current DB migration state.
- Project watchdog.log is unchanged since 2026-11-09 14:00:13 and tunnel.log since 2026-11-11 08:42:50 (connection reset / broken pipe). The watchdog.lock file exists; whether an orphaned child actually holds its kernel flock cannot be observed through FTPS.
- Selective outbound networking is important: curl --noproxy '*' to api.ipify.org returns 5.188.190.59, but to ipv4.icanhazip.com returns 37.255.236.184; TCP port 22 of 37.255.236.184 was reachable from the office machine itself. Therefore it would be UNSAFE to replace the configured Windows reverse-tunnel destination based on ipify alone. The original endpoint may still be valid from an external host; it is not externally verified in this check.
- PrintHubTunnel local Windows account exists and is enabled; its authorized_keys path exists, but is access-restricted to the current operator, so no claim about current key content or fingerprint matching has been made. The last logged successful PrintHubTunnel public-key authentication remains 2026-11-09 14:00:10.
- No Host shell was available through the existing project gateway. Generic SSH TCP 22 to nphost4.parsblog.com is not available from this Windows computer; FTPS cannot run an authenticated shell and must NOT be used to deploy migration/code or create ad hoc exec endpoints.
- Financial release pending: source branch fix/service-store-refund-dual-approval-20261111, last known local QA 188/188 passed; must wait for proper Host Terminal / authenticated tunnel before full backup, exact two migrations Website.0029 and Store.0044, financial/stock fingerprints and read-only acceptance. No financial, stock, cron, firewall, SSH identity or Host source mutation occurred today.

Safe Host operator recovery, through the 3DPrintHub cPanel Terminal (not FTP):
1. Inspect the existing Cron Jobs entry and check whether the project-specific watchdog.lock is busy using nonblocking flock with /bin/true. Do not delete a live lock file or kill a process based only on a PID file.
2. Identify the actual project-owned orphan SSH/bridge processes and lock ownership; recover ONLY this project's watchdog if warranted.
3. Use the documented per-minute watchdog with `/bin/flock -n -o` so future detached children cannot inherit its lock; do not duplicate cron jobs.
4. Run the existing project transport-only bootstrap once, verify that reverse port 22024 and project-host.ps1 -Health work; then perform source/DB/migration and audited release controls.

## 2026-11-12 22:19 (+03:30) — follow-up: tunnel still absent, deployment still blocked

- Authorized Emad-NewCom command check confirms Windows `sshd` Running/Automatic; loopback reverse SSH listeners `22022` through `22027` are all absent, including dedicated 3DPrintHub `22024`. Project-specific `project-host.ps1 -Health` cannot connect.
- Project FTP read-only check confirms active Git ref remains `0ae8d7851b803ddc8ab75be3adf35ac2a2d76a5a`. The remote `watchdog.log` still ends at 2026-11-09 14:00:13 and `tunnel.log` at 2026-11-11 08:42:50. No evidence of a successful project watchdog restart or restored authenticated SSH.
- Public `/`, `/store/`, `/admin/login/` all returned HTTP 200, but public HTTP health does NOT prove pending finance migrations are applied. They have not been deliberately deployed from this branch.
- A September historical runbook `docs/operations/reverse-tunnel-ssh/VERIFIED_PERSISTENCE_COMMANDS.md` still contained an unsafe `flock -n` Cron recipe. This commit replaces it with `flock -n -o` and marks the old hard-coded September branch as historical, preventing accidental reinstallation of the known lock-inheritance pattern.
- Added isolated GitHub Actions CI for the Service + Store reviewer permissions, ledger/stock/quote regressions, migrations and shell scripts. It uses only ephemeral CI credentials; it cannot deploy to production or send money.
- Current production release remains **blocked pending authenticated cPanel Host Terminal / project tunnel recovery**. Do not use FTP to run migrations and do not alter unrelated project tunnels, accounts or firewalls.
