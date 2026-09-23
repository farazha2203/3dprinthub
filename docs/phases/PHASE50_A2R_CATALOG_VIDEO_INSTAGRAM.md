# Phase50.A2R — Catalog completion, Product video and Instagram set/Story

Status: `IN_PROGRESS / WINDOWS GITHUB_UPDATED / SERVER RELEASE LOCAL_TESTED`
Date: 2026-09-23

## Requested Delta

Continue the existing 3DPrintHub Catalog Center workflow with three connected operator needs:

1. Incomplete Crawl rows must remain visible and useful even when Product linkage or a modern image mapping is missing.
2. A row with a canonical Product URL must support safe, explicit re-fetch of source data and images.
3. A Product detail must support receiving a Product video and preparing the same Product for Site media, Instagram Feed/Carousel and companion Story publication.

## Existing contracts to preserve

- `discovered_urls` remains the canonical Crawl identity ledger.
- Existing adaptive acquisition, source refetch/merge, Product history and circuit-breaker behavior remain authoritative.
- Operator pricing, Persian editorial fields, Site selection, Slider/Primary state and publish receipts are never overwritten by a source refresh unless explicitly owned by the refresh contract.
- Site publication remains Site-first and public-HTTPS verified.
- Buffer publication continues to use provider-compatible GitHub-hosted derivatives when required, with canonical Site media retained separately in receipts.
- ProductVariant remains the canonical commerce/pricing/order authority.

## Touched Surfaces

- Catalog Crawl inventory and Product preview/local-media resolvers.
- Existing URL-owned acquisition/refetch and safe Product merge boundaries.
- Product detail media workspace and local media manifest/state.
- Existing Instagram Feed/Carousel, companion Story, Buffer media-host and receipt reconciliation paths.
- Focused regression suites and operator documentation.

## Must Not Touch

- No parallel crawler, Product identity table, pricing engine or social provider architecture.
- No direct Production source/database/media mutation.
- No deletion of incomplete media, valid backups, secrets or pending queue records as quota cleanup.
- No automatic Instagram Highlight mutation where the provider API does not support it.

## Delivery Gates

1. Local source/WIP and exact GitHub relationship inspected.
2. Focused unit/regression tests, Python compile, `git diff --check`, Qt VerifyOnly and bounded foreground QA pass.
3. Fresh Catalog backup and rollback reference.
4. Commit/push with exact remote SHA verification.
5. Host quota/write capability and authenticated reverse-tunnel identity verified through project `3dprinthub` Router.
6. One bounded refetch/video/Feed/Story acceptance; then docs closure.

## Current transport evidence

- Router Health: `ok=true`, base `/home/sfkilvrs/3dprinthub`.
- Host identity: `sfkilvrs@nphost4.parsblog.com`.
- Windows loopback `127.0.0.1:22024`: TCP reachable.
- Host filesystem is not full (`39%` blocks, `15%` inodes); the historical FTP `Disk quota exceeded` remains an account/FTP quota issue to isolate without deletion.


## 2026-09-23 split execution checkpoint

To keep long execution bounded, A2R is delivered in two independently testable slices.

### Slice 1 - Catalog video acquisition
- Real Catalog Product #536 / MakerWorld 3190632 persists the animated GIF link and local video manifest.
- Catalog SQLite source and fresh online backup both pass `PRAGMA quick_check`.
- Fresh rollback: `D:\\projects\\3dprinthub-backups\\pre-a2r-slice1-20260923-171036\\catalog.sqlite3`.
- Backup SHA256: `716FEE336369273381884CC078CD02D8E0538E44021DAFCD295FDBFCF30F2D26`.
- Logical source/backup Product count, page count and Product #536 video state match.
- A2R + acquisition regressions: 35/35 PASS.
- Changed Slice-1 Python compile: PASS.

### Slice 2 - Site/social acceptance
Pending after Slice 1 GitHub checkpoint: Site receiver/video rendering regressions, social manifest/Story regression, Qt VerifyOnly, commit/push, reverse-tunnel Host gate, bounded Site-first acceptance and final docs closure.

### Slice 2 - Site/social local acceptance
- Site receiver stores bounded Product motion media without a Django schema change and Product Detail renders GIF/video from the imported asset.
- Windows public verification separates image and motion-media HTTP checks and requires declared Product videos to be rendered publicly.
- Instagram payload preserves canonical images/ALT and adds bounded verified video entries in `media_manifest`; Story artwork does not print a raw non-clickable URL.
- Site/receiver focused tests: 6/6 PASS.
- Mature Product Detail/import related regression: 5/5 PASS.
- Buffer/Instagram/Story regression: 34/34 PASS; no external post was created.
- Django check PASS with only known CKEditor warning; migration drift: none.
- Slice-2 Python compile and `git diff --check`: PASS.
- Qt VerifyOnly: `QT6_FOUNDATION_VERIFY=OK`, `QT6_42B2_FULL_PARITY_VERIFY=OK`, `QT_OPERATOR_LAUNCHER_VERIFY=PASS`.

Next gate: commit/push Slice 2 with exact Local=Remote proof, then use only the dedicated `3dprinthub` project router for Host read-only audit and release-lineage verification before any Production mutation.

## 2026-09-23 selective Production release checkpoint

Production truth was re-audited through the dedicated 3DPrintHub router. Host is clean at exact `e03bdd2b718fae3ce030df789c8b9db958d8d8ed` on the historically named `release/phase50-a2j-hero-20260915` branch. That commit is live on GitHub as `origin/wip/phase50-a2x-server-parity-20260921` and is newer than the stale remote A2J release head, so the release candidate is based on exact Production SHA rather than the stale branch ref.

The new isolated release worktree/branch is `D:\projects\3DPrintHub-a2r-video-release-20260923` / `release/phase50-a2r-video-social-20260923`. Only the Production-required Server delta from Windows commit `03808add798da6629c73d4c9bdba71b322a52a14` was applied: Catalog batch receiver video persistence, Product Detail motion-media rendering and the dedicated Server regression. Windows Catalog/Instagram code remains on the tested Windows WIP lineage and is not wholesale-merged into Production.

Release Local verification with CI-only non-Production environment: 12/12 focused+related Store tests PASS; Django check PASS with known warnings; migration drift none; touched Python compile PASS; diff-check PASS. No migration/requirements/settings delta exists.

Guarded deploy runner: `scripts/host/phase50_a2r_video_media_deploy.sh`. It requires exact Host baseline and clean worktree, exact live GitHub target and ff-only ancestry, allowlisted no-migration delta, MySQL identity + empty migration plan + receiver readiness before/after, scoped runtime-file + protected env rollback evidence and a full verified MySQL gzip, Passenger restart and public Home/Store HTTP verification. It intentionally avoids another large Git bundle because `ERR-49-213` proved quota pressure; exact pre-change commit remains retained in Git/GitHub.

Next: commit/push this release candidate, verify Local=Remote, run the guarded runner through the dedicated project router, then perform same-identity Product #536 republish/public-video verification before any duplicate-safe Instagram Feed/Story acceptance.
