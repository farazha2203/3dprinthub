

## 2026-10-08 — Windows runtime/worktree cleanup

Owner accepted the visible Catalog Center v8.9.11 / Build 2026.10.04.2 as the current runtime to preserve. Its source remains `D:\projects\3DPrintHub-a2z-a2r-converge`, Catalog data remains `D:\projects\3dprinthub-catalog-manager`, and the Desktop shortcut still targets this runtime. Historical local worktrees were removed only after compact dirty-delta rollback evidence was captured at `D:\projects\3dprinthub-backups\worktree-cleanup-20261008-193657`.

After cleanup, Qt VerifyOnly PASS and read-only Catalog quick_check=ok with 1076 Products. The running v8.9.11 process remained healthy. Current A2R/W5 source WIP in the preserved runtime was not reset, stashed, or overwritten; Host/Production were untouched.

2026-10-09 actual runtime A2R: Desktop shortcut points to D:\projects\3DPrintHub-a2z-a2r-converge\catalog_center\RUN_QT.ps1, pre-change W5 branch SHA 9a7c35b3. Active Buffer supports explicit operator repeated Story publication; do not apply old permanent Story lock. Feed duplicate guard, current revision provider reconciliation and Direct Instagram guard updated narrowly with stable Product ID/revision. 5 focused + 34 Buffer + 29 Instagram PASS, official Qt VerifyOnly PASS. No Social API mutations or Catalog data updates. Site runtime 02770187 and Windows W5 diverge at merge-base 2b48a593; broader Web deploy requires convergence. Next actual shortcut smoke/W5C gallery acceptance, then W6 Product Video/Reel.

A2R real-source GitHub and Desktop Qt closure 2026-10-09: W5 branch Local=Remote=b3c89f46be14f8c7ec45fc07108c040cd597778f; 5+34+29 social regression tests, Python compile, exact RUN_QT.ps1 -VerifyOnly PASS; RUN_QT.ps1 launched pythonw process from the verified real user shortcut source. Newer manual Story-repeat capability retained, Feed and provider receipt reconciliation identity guard robust against cosmetic ACK changes. No Product/DB/Host/Instagram side effects. Remaining W5C visual UI select/delete/reopen acceptance, Windows-vs-Production divergent ancestry convergence, Product #536 commercial approval and genuine latest provider status before new rev2 social publish. Next W5C acceptance; following W6 source video/Reel.
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

## 2026-10-09 — Owner continuation after A2U SEO closeout (READ_ONLY)
- Verified canonical Windows Catalog SQLite via read-only URI and correct Project current WIP/release. Product #536 / MakerWorld external 3190632 remains `commercial_status=review`, `workflow_status=uploaded`, `server_status=updated`, Site revision 2, server_product_id=48 and server_id=147. Last Site sync receipt `updated` 2026-09-23 14:39:05Z.
- Real `selected_video_links_json` contains one selected MakerWorld GIF CDN link; it has NOT been stored as a verified playable/downloaded local asset: `selected_video_url` empty, `local_video_path` empty, SHA empty and video_bytes=0. Earlier video discovery/manifest tests do not prove the full Site public video release.
- **DO NOT repost blindly:** same product has existing `instagram_published` receipt 2026-09-22 18:22:57Z and later `instagram_story_published` receipt 2026-09-23 07:47:14Z, alongside earlier Story failure. The provider-side current state and whether these receipts belong to exact newest Site revision still require reconciliation; no Buffer publishing performed.
- Current A2R status `IN_PROGRESS / VIDEO_ACQUISITION_AND_SITE_MEDIA_VERIFICATION_PENDING / SOCIAL_RECEIPT_RECONCILIATION_PENDING`. Owner requested phase continuation, but data-dependent write/publish gate is not satisfied. Next bounded work: protected Catalog backup, verify/download selected one GIF with source policies, Site-first same-identity Media+ACK exact-revision gate, public video response and variant parity, then explicit duplicate-safe per-destination social acceptance if genuinely new revision. Canonical WIP remains untouched in this read-only checkpoint.

## 2026-10-09 — A2R Product #536 media verified / revision-safe Social guard LOCAL_TESTED
- Local GIF exists in persisted local_video_files_json, SHA256=6f980225578d6afc94375ffc53848ca95440119f060f97f84dd3b2702fb056c6, size 12,778,636. Site ACK public_videos for Product48 revision2 shows HTTP200 image/gif; live URL independent response confirms 200 and same content length; Product /little-ballerina/ renders it. Previous missing-media claim corrected.
- Existing Buffer Feed and Story sent receipts refer to Product48 revision1, not current revision2. Do not repost rev1 or automatically post rev2 without provider confirmation and product social-content readiness.
- Implemented pure positive Site Product ID/revision dedup matcher for Buffer Feed+Story and Direct Instagram, preserving legacy identical raw ACK. New 5/5, related Buffer 12/12, Instagram 20/20, Story 2/2, Python compile PASS. No database migration, Catalog write or external provider call.
- Next: integrate release-tested change safely into canonical Windows WIP after backup, execute Qt verify; then provider read-only sync and deliberate rev2 publishing decision. Production Host still on A2U 02770187, no Windows social runtime release claimed.

Regression count note: A2R revision helper 5/5; Buffer suite 12/12 (includes Story companion 2/2); Instagram 20/20 = **37 distinct passing tests**. Live Buffer provider state for rev2 and Windows packaged app cutover are still unverified, so this checkpoint must not be labeled deployed/accepted.

A2R latest approved GitHub (2026-10-09): `1e0e00b34dd368e4aba275a443f42843dac0c74f`, 37 distinct regressions PASS, no new Instagram posts, no source/DB/Host mutation apart from tested GitHub Windows social receipt guard. Separate docs-only closeout may advance GitHub after this runtime code SHA. Status `GITHUB_UPDATED / ACTIVE_WINDOWS_CUTOVER_AND_REV2_SOCIAL_VERIFICATION_PENDING`.

2026-10-09 Buffer read-only provider check: configured Instagram channel authenticated successfully; recent 30 posts query completed, original two September receipt IDs were outside that result (not proof of deletion). Product #536 rev2 dry-run generated correct Site product path, four UTM tags, one owned Product image/ALT and eight hashtags. No Feed/Story mutation. GitHub guard 1e0e00b34dd368e4aba275a443f42843dac0c74f is not yet installed in the canonical Windows runtime; Catalog commercial_status=review also prevents treating rev2 as automatically approved social content.
