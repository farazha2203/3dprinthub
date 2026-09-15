## 2026-09-15 Client handoff ? deployed and verified
Current verified Production application/source HEAD is `b1caeba0f20e711b29dfa9e0ff92a2f5186fb08d`, exact with Local/live GitHub and clean on the canonical branch. Authenticated reverse management is healthy through Windows loopback `127.0.0.1:22024`. The successful handoff deploy rollback directory is `/home/sfkilvrs/3dprinthub-deploy-backups/20260915-094656-phase50-client-handoff`; its source bundle verifies and records pre-deploy HEAD `70a74e6f21113ae6bc5ed1f679d1e57e4e5a8eb7`.

The separate Store reset has also completed with rollback evidence `/home/sfkilvrs/3dprinthub-deploy-backups/20260915-094827-store-product-reset`. Current Store preflight is intentionally blocked only by `store_already_empty`. Do not rerun `phase50_client_handoff_deploy.sh` from its old baseline or rerun Store deletion; future deploys require a new runner/baseline and fresh state verification.

## Permanent execution topology
Local implementation and testing are executed on the verified Windows machine via Remote Desktop. Production deployment is executed from GitHub through the dedicated 3DPrintHub reverse tunnel (`Windows 127.0.0.1:22024 -> Host 127.0.0.1:22224`). The one-minute Host cron watchdog must keep that reverse tunnel self-healing. Owner-side cPanel command entry is break-glass recovery only, not the normal deployment workflow.

## 2026-09-15 transport recovery prerequisite
Before any client-handoff deployment, require the dedicated 3DPrintHub reverse tunnel on Windows loopback 22024 and authenticated Host identity. If the cPanel watchdog is stale, restore/run only the documented 3DPrintHub bootstrap through an authorized cPanel execution channel. FTPS is not a deployment channel, another project tunnel is not a substitute, and cPanel authentication must not be bypassed.

# Deployment

## 2026-09-15 Client handoff path
Production source must move only from the canonical GitHub branch `agent/phase49-3i18-operator-bulk-ai-rebuild`.

Current verified Production baseline before handoff is `70a74e6f21113ae6bc5ed1f679d1e57e4e5a8eb7`.
The dedicated runner is `scripts/host/phase50_client_handoff_deploy.sh`.

The runner requires the exact clean Host repository, correct branch, live GitHub target equality, fast-forward ancestry, an empty migration plan, ready Catalog Bridge, and an allowlisted target delta. It creates verified source, `.env`, and changed-static rollback evidence before promotion.

Deployment is ff-only from fetched GitHub source, followed by Django checks, `collectstatic`, static hash verification, Passenger restart, and public/authenticated Production verification. It performs no Django migration.

Store Product deletion is intentionally separate from source deployment. After the new runtime is live, `scripts/host/phase50_store_reset_prepare.py` plus the authenticated Store Reset endpoint require a fresh real MySQL gzip dump, exact live-count manifest, and checksum-identical Product media backup before deletion is allowed.

Never upload permanent source directly over FTP/FTPS and never bypass GitHub-first promotion. Reverse management uses only the dedicated 3DPrintHub `PrintHubTunnel`; other project tunnels must not be modified.
