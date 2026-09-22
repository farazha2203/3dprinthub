# Phase50.A.2Z — Image + Social Authority Hotfix

Status: A2Z-S SOCIAL DELIVERY READINESS GITHUB_UPDATED / WINDOWS_RUNTIME_ACCEPTED / BUFFER MOBILE EXTERNAL-BLOCKED
Date: 2026-09-22
Branch: `wip/phase50-a2z-image-social-authority-20260921`
Baseline: `f5f401167d14e560e53fc9cdc292024c67174459`

## 2026-09-22 — Post + linked Story readiness hardening

- Live Catalog provider is `buffer`; Buffer GraphQL endpoint is `https://api.buffer.com`; channel `6aabb3a8ea19ca0bde6694d5 / 3dprinthub_ir`; provider-media host `github_raw`.
- Feed remains automatic Buffer `createPost` with current Site Product revision, exact selected media, Product caption/hashtags/per-image ALT/UTM and existing Social SEO v4 policy.
- Companion Story remains the approved 1080×1920 Gold/Navy + IRANSans asset. Clickable Product link requires Buffer `notification` scheduling + `stickerFields` and final native Instagram Link Sticker handoff.
- New `InstagramCore.delivery_readiness()` checks connected/unlocked Buffer channel + `hasActiveMemberDevice` before Site mutation, provider-media generation/rehost or createPost.
- `publish_site_then_instagram()` and `publish_many()` both fail closed; `buffer_publish.publish_product()` retains its lower-level guard.
- Products UI action is now **«Instagram (Post + Story لینک‌دار)»** and checks readiness before starting a Worker. When mobile is missing, nothing new is Site-published/rehosted/submitted.
- Same-Site-ACK Feed receipt remains duplicate authority; retry after a Story failure reuses Feed and attempts only Story once readiness is restored.
- Focused readiness/Core/UI/Buffer gate **22/22 PASS**; full Site+Social gate **69/69 PASS**; 4 Python compile + diff + Qt VerifyOnly PASS; Server/migration delta=0.
- Rollback ref: `backup/pre-a2z-social-readiness-ui-20260922 @ 5dec164d14511bfd37adbc4ac69f146dc71eca7e`.
- Runtime-bearing SHA `ec05b77fec0d3316d8ee9663fb50b333cf437658` is Local=GitHub exact and running in Qt; exact-SHA VerifyOnly/launch PASS.
- Live Core readiness on this SHA still reports `hasActiveMemberDevice=False` and `ready=false`; no real send was attempted. External owner action remains: Buffer mobile same account -> push enabled/reset -> Test Notification -> API true -> bounded real Social acceptance.

## Owner-reported failures
- Product #609 selected Local media `local://04.webp` and `local://05.webp` were outside canonical `images_json`, so Site publish failed closed.
- UI could show the same SEO filename for two query-variant source URLs because metadata lookup collapsed them to one canonical asset key.
- Instagram/Buffer failed before publish because branch `social-assets-buffer` was already registered at another Git worktree.

## Correct contract
- A real trusted Product-local card checked for Site becomes canonical Product media at the same Stage-3 save boundary.
- Exact source URL identity wins metadata/SEO-slot lookup; canonical-key fallback is compatibility-only.
- Final physical publish media lives under `seo_images`, uses unique numbered SEO WebP names, and Batch copies those exact files/bytes.
- Social provider media reuses an already-registered worktree for its branch instead of attempting a duplicate `git worktree add`.
- Applying Product image SEO now promotes the actual selected Product-local physical file to the unique SEO WebP basename under `images/`; the old bytes are preserved under `source_originals/`.
- Remote source URL remains provenance, while exact `source_local_file` points to the SEO-named Product-local file. Local `local://` identities are remapped to the SEO basename.
- Duplicate physical SEO basenames are forbidden; numbering remains deterministic `-01, -02, ...`.

## Local verification
- New focused image/social/publish gate: 9/9 PASS.
- Broad Image/Publish/Windows/Social gate: 113/113 PASS.
- Two historical UI assertions first failed broad gate and reproduced identically on clean baseline `f5f40116...`; assertions were aligned to the already-accepted Site-selection/source-refresh UI contract.
- `git diff --check`, touched Python compile (7 files), and Qt VerifyOnly PASS.

## Real #609 checkpoint
- Fresh rollback: `phase50-a2z-609-pre-repair-20260921-194148`; SQLite integrity OK + full media manifest.
- Application-level repair completed: selected=5, canonical=5, physical SEO names `-01..-05.webp`, original selected bytes archived.
- Site Product remains #42 revision 1; no Site publish yet.
- ERR-49-218 fixes false source drift introduced by the new physical SEO boundary.
- Source-drift/promotion/Batch 3/3 and Image+Site Publish 51/51 PASS.

## A2Z-S real Instagram checkpoint
- Production #42 / Desktop #609 is already revision 2 with exactly five ProductImages; public HTTP + SHA parity is 5/5, so no duplicate Site re-publish is permitted.
- Current Site ACK has zero Instagram receipts.
- Buffer connection is healthy for `3dprinthub_ir`; provider host is `github_raw`; social-assets worktree/remote were clean/exact before the new fix.
- Policy v4 preflight passes all written rules: 5 media/5 ALT, 8 bounded hashtags, UTM, nationwide shipping, no free claim, approved Story style, Highlight target `قطعات سفارشی`.
- Fresh Catalog rollback: `pre-instagram-a2z-609-20260921-201631` / integrity OK.
- ERR-49-219: real dry-run failed before createPost because the github_raw path still forced a Story FTP upload to Site and hit WinError 10054.
- Fix: github_raw creates derivatives locally and uses only the dedicated GitHub provider-media path; site mode keeps FTP.
- Social regression 35/35 PASS; real local-only #609 render is 5 Feed PNGs + valid 1080x1920 Story, receipts unchanged at 0.
- Transport fix is GitHub exact at `d6b0de52...`. Real #609 rehost committed as `3294d817...`; current `social-assets-buffer` is clean/remote-exact at `2cc87108...`, #609 commit is retained as ancestor, and all 6 provider assets are public HTTP 200 image/png with exact manifest SHA.
- Final Story-link compliance delta is Local-tested: clickable Story uses Buffer notification-mode + explicit Link Sticker UTM handoff, records `instagram_story_notification_ready`, and remains duplicate guarded; fully automatic Story remains available only when clickable-sticker handoff is disabled. Expanded Social regression 36/36 PASS; compile/diff/Qt VerifyOnly PASS.

## Real external acceptance
- Exact-SHA `bc96c52f...` ran with fresh pre-send Catalog backup `pre-instagram-send-609-20260921-210748`, quick_check OK, revision 2 and zero pre-send Instagram receipts.
- Feed Buffer id `6ab16b897465bdab83a3fe40` reached `sent`; live link https://www.instagram.com/p/DdjtyiMG8RC/; exact five provider assets retained. Reconciliation appended published evidence without repost.
- Story notification id `6ab16b959d554f7b28a44302` is `error`; Buffer Post error says no allowed reminder-recipient mobile devices are linked. No Story external link exists.
- ERR-49-220 hardening is Local-tested 37/37: provider error is failure, not notification-ready; historical false-ready/error receipt is retryable; existing Feed remains deduplicated.
- External prerequisite remains owner-side Buffer mobile linking/sign-in + notification enablement. Automatic/no-sticker downgrade is prohibited by this phase contract.

ERR-49-220 is GitHub-updated exact at `c064c36f2d389bb0114489f958c9026b8573316b`. Fresh post-send rollback: `post-instagram-feed-609-20260921-211603`, integrity OK; revision 2 unchanged; Feed final receipt is published/reconciled without repost while the historical Story receipt explicitly carries `buffer_status=error`.

## ERR-49-221 — Product #588 transient WAF readiness recovery
- Owner's real #588 publish attempt was rejected at `publish-readiness` by transient BitNinja anti-robot HTML before any Batch/FTP/import receipt existed.
- Changed-condition authenticated read-only probes now return Bridge health 200 and publish-readiness 200/`ready=true`.
- Windows Bridge JSON transport retries only an exact anti-robot 403 on idempotent GET requests, max three total attempts with short backoff.
- Import POST remains single-attempt; no blind repost/reimport is introduced.
- Persistent WAF challenge produces a concise operator error rather than raw HTML.
- Rollback ref: `backup/pre-err49-221-waf-readiness-retry-20260922` -> `0202bdcafc252b1d409310838831bb0ea35100ee`.
- Verification: focused 13/13 PASS; corrected Publish/SiteConnection 86/86 PASS; py_compile/diff-check/Qt VerifyOnly PASS.
- Dedicated Host-management reverse tunnel 22024 is currently down. Host source deployment is blocked, but this Windows-only hotfix does not require Host deployment.

## Exact next
Commit/push ERR-49-221 -> verify Local=GitHub exact SHA -> fresh integrity-checked Catalog backup -> exact-SHA Qt relaunch -> require live readiness 200/`ready=true` -> retry **only Product #588** once through the canonical Product publish action -> require exactly one new Batch/start/FTP/terminal ACK chain -> verify Site identity/revision + Profile/Variant/media parity + public Product/media HTTP. Do not include the other queued Products.

After #588 Site acceptance, return to the already-open A2Z-S external prerequisite: owner links/signs in to Buffer mobile and enables reminder notifications -> Story-only recovery for #609 with Feed duplicate protection -> Link Sticker handoff -> truthful Story/Highlight receipt.

## Phase after this hotfix
Continue A2Z Catalog Slider completeness/backfill + final Windows operator acceptance, then A2Z-S changed-revision Social rollout and the remaining master A2Z plan.
