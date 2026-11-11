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
