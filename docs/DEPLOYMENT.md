## 2026-09-15 Phase50.A.3 ZarinPal compatibility deploy
Production application baseline is exact clean `b1caeba0f20e711b29dfa9e0ff92a2f5186fb08d`. The dedicated runner is `scripts/host/phase50_zarinpal_current_api_deploy.sh` and must be executed only through the authenticated 3DPrintHub reverse tunnel after the target commit is the exact live canonical GitHub head.

The runner verifies repository/branch/baseline/clean worktree, MySQL identity, empty migration plan, publish readiness, current payment disabled/credential-presence booleans, outbound TLS to live/sandbox ZarinPal, explicit `FETCH_HEAD`, ff-only ancestry and an allowlisted target delta. It creates and checksum-verifies source bundle + `.env` rollback evidence before merge. It performs no migration, no Production DB write, no collectstatic and no gateway enable. Post-merge it runs Django/no-drift/payment audit, validates live/sandbox endpoint defaults and the Verify payload AST, restarts Passenger, and requires Home/Store HTTP 200.

This deploy only makes the existing secure provider compatible with the current API defaults. Real Store checkout activation remains blocked on canonical StorePayment wiring and legitimate merchant credentials.

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

## 2026-10-08 — Product snippets guarded deploy (verified)
The no-migration SEO-only release is `8e9f395b93f6a31802b951a71fcabbc8171985af` on GitHub release branch `release/phase50-a2t-google-indexing-20261008`. Production HEAD is the same exact commit and clean despite historical Host branch label `release/phase50-a2j-hero-20260915`.
Deploy runner from target Git object: `scripts/host/phase50_product_snippet_deploy.sh`; it verifies exact clean source, actual GitHub target, ff-only ancestry, source/document path allowlist, DB vendor/name, zero pending migrations; creates validated git bundle and MySQL gzip backup, then ff-only merges exact fetched SHA, checks, collectstatic, Passenger restart and six public Product JSON-LD smoke tests.
Verified backup `/home/sfkilvrs/3dprinthub-deploy-backups/20261008-203110-product-snippet` (source bundle + protected env copy + compressed MySQL with checksums), prior HEAD `2b85a9c0d5d4a79219182bc9b986a5a81e70ed50`.
Terminal `PRODUCT_SNIPPET_DEPLOY=PASS`, independent 6/6 public PASS, no DB migration. Account disk quota only 2000MB and last reported 1961MB used; future Deploy requires quota headroom and rollback preparation. Google Search Console issue resolution requires authenticated validation/re-crawl separately.
