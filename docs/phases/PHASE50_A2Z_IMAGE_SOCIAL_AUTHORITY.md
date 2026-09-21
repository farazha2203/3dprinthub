# Phase50.A.2Z — Image + Social Authority Hotfix

Status: A2Z-S FEED PRODUCTION_VERIFIED / STORY BLOCKED ON BUFFER MOBILE REMINDER DEVICE / ERR-49-220 LOCAL_TESTED
Date: 2026-09-21
Branch: `wip/phase50-a2z-image-social-authority-20260921`
Baseline: `f5f401167d14e560e53fc9cdc292024c67174459`

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

## Exact next
Wait for changed external condition: owner links/signs in to Buffer mobile and enables reminder notifications -> read-only provider gate + fresh Catalog backup -> Story-only recovery through normal Product Social action, proving Feed createPost is skipped -> require non-error notification state -> operator completes Link Sticker handoff in Instagram -> record truthful Story/Highlight result -> A2Z-S closure.

## Phase after this hotfix
Continue A2Z Catalog Slider completeness/backfill and final Windows operator acceptance; then A2Z-S changed-revision Social rollout.
