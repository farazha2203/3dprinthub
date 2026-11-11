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
