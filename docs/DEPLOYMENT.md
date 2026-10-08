## 2026-09-20 Phase50.A.2R payment/finance/admin guarded release

Verified Production baseline before this release is clean `release/phase50-a2j-hero-20260915 @ 65d42e40979830b306e92457093aefe068086f66`. The only authorized Host transport is the dedicated authenticated 3DPrintHub reverse tunnel on Windows `127.0.0.1:22024`.

Target release branch: `release/phase50-a2r-payment-finance-admin-20260920`.
Runner: `scripts/host/phase50_a2r_payment_finance_admin_deploy.sh`.
Fail-closed resume for exact partial-promotion baseline `0c9d328299a77c26fdef9450d985276178ecc120`: `scripts/host/phase50_a2r_payment_finance_admin_resume.sh`. The resume runner takes a new source/`.env`/MySQL verified backup before any further promotion.

The runner must be executed from the exact live GitHub target. It requires exact baseline/branch/clean worktree, correct repository and MySQL identity, empty migration plan, receiver readiness, target SHA equality and fast-forward ancestry, and an explicit allowlist of A2R files. It rejects migration, dependency, settings or unrelated source changes.

Before merge it creates and checksum-verifies a Git source bundle, protected `.env` copy when present, and a real MySQL gzip backup with `gzip -t` plus SHA256 verification. Promotion is `git merge --ff-only` from GitHub.

Post-merge gates include compile/check/no-drift/empty migration plan, masked Payment Readiness state, read-only Admin Command Center render smoke with secret identifiers forbidden, manual-payment dry-run marker, Passenger restart and Home/Store HTTP 200. The runner does not apply/activate manual payment, enable ZarinPal, run migrations or print financial destination/credential values.

Manual-transfer configuration/activation is a separate stateful operation after a fresh DB rollback boundary and must use only protected `STORE_PAYMENT_*` runtime environment values or the existing Admin singleton. ZarinPal stays disabled until legitimate merchant configuration is separately verified.

## 2026-09-19 collectstatic permission rule
Guarded runners may keep `umask 077` for private backup files, but public `collectstatic` creation must temporarily use `umask 022`. Any newly introduced nested static tree must be checked for web-traversable directories and verified through its real public URLs/MIME types before browser acceptance.

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

## 2026-10-08 — Phase50.A2T Google Search guarded deployment

Production was verified clean at `2b48a593ace2e9a3703fa0f52b4c3c13b2751cf9` before this release. Target branch: `release/phase50-a2t-google-indexing-20261008`; deployed target: `2b85a9c0d5d4a79219182bc9b986a5a81e70ed50`.

Runner: `scripts/host/phase50_a2t_google_indexing_deploy.sh`.

The runner requires exact baseline, clean Host worktree, correct repository, exact MySQL identity, empty migration plan, exact live GitHub target SHA, explicit branch fetch and fast-forward ancestry. Its allowlist is limited to the A2T Google files and rejects migrations, dependency/settings/environment changes.

Before promotion it creates and verifies a Git bundle, protected environment copy and real MySQL gzip backup. Promotion is `git merge --ff-only` from the exact fetched GitHub commit, followed by compile/check/no-drift, collectstatic, Passenger restart and public pre-indexing smoke. It deliberately does not enable indexing.

Verified deployment rollback:
`/home/sfkilvrs/3dprinthub-deploy-backups/20261008-112619-phase50-a2t-google-indexing`.

A second independent rollback boundary was then created and verified before the only stateful Google publication action:
`/home/sfkilvrs/3dprinthub-deploy-backups/20261008-112838-pre-google-indexing-toggle`.

After DB identity/head/worktree checks, `SEOSettings.allow_search_indexing` was transactionally changed from false to true and the public endpoints were reverified. Search Console submission remains separate from source deployment and requires verified Google property access.
