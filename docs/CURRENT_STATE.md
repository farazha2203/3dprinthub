## 2026-09-24 - Phase50.A.2Z-O1 Product Filters + Split Instagram LOCAL_TESTED / GITHUB_PROMOTION NEXT

Active branch is `wip/phase50-a2z-o1-catalog-controls-20260924`. The blocking Windows/Production lineage divergence was closed first with no tree delta at `82862b4569b537406618523f7350cd3514c4c03f`; both Windows `740bfe6e...` and selective Production `2b48a593...` are ancestors.

O1 implements the owner-requested Product controls without Product/Site mutation: operational filters for 7/7 ready, AI-completed 6/7, Site sent, Instagram Post sent and Instagram Story sent; Feed/Post and Story are now separate buttons, readiness scopes and worker paths. Feed-only never creates Story and is not blocked by native-Story mobile readiness. Story-only never creates Feed/Post and uses independent Buffer media hosting; Direct provider fails closed for Story-only.

Real Catalog truth after implementation: quick_check=ok; ready_7=2, ai_6=19, published=14, instagram_posted=4, instagram_story=2. Focused changed-condition 1/1 PASS; focused Product/Social/Buffer 24/24 PASS; broader Product/Qt/Social 136/136 PASS; py_compile, diff-check and Qt VerifyOnly PASS. No Production deploy is required for this Windows-only O1 delta.

Phase plan is now six bounded slices in `docs/phases/PHASE50_A2Z_O_CATALOG_OPERATOR_CONTROLS.md`: O1 filters/split Social -> O2 Crawl complete/incomplete + missing reasons -> O3 deep reset/refetch/remap repair -> O4 delete semantics -> O5 Social receipt/operator acceptance -> O6 integrated closure.

Phase50.A.2Z is now factually CLOSED/ACCEPTED: Product #628 successfully published as Site #38 revision 2 with ACK parity ok=true, 2 media, 32 active variants, exact 12cm/18cm profiles, Slider disabled and public HTTP=true. Independent Production DB readback and real Playwright Desktop 1440x1000 + Mobile 390x844 acceptance passed with no stale Unicode media path, no overflow and no page/console errors. #625/#620/#152/#178 collateral readback remained stable.

Exact next: final docs/diff review -> commit/push O1 -> verify Local=Remote -> Qt VerifyOnly from pushed SHA -> close the running Catalog Center once -> relaunch from that exact branch/SHA -> runtime smoke -> mark O1 ACCEPTED -> start O2.

## 2026-09-24 - Phase50.A.2Z #628 ASCII BATCH SOURCE FIX GITHUB_EXACT / BOUNDED RETRY NEXT

Current branch `wip/phase50-a2z-catalog-data-completion-20260923` contains the final Windows Batch-source fix at GitHub-exact code commit `7b1b447ab772e15f3ecdc1345e69e2e8771573f8`. Earlier Server destination canonicalization remains deployed on Production `2b48a593ace2e9a3703fa0f52b4c3c13b2751cf9`.

Production truth before selective release: Host remains clean on `103f559c8a11c35495b4ac2a290d578c31c2a023`; official reverse tunnel/Bridge recovered and Host read-only gate passed. #625 was published alone from a verified fresh DB+media rollback: Site Product #39 advanced to revision 13, price range 458,500-1,655,000, exactly one active ProductImage, exactly 32 active Variants (= two Profiles x 16 PLA), old Variant rows inactive, and public page contains only the current /media/p/625 path with stale hashes absent.

Fresh #628 prepublish rollback is `/home/sfkilvrs/3dprinthub-deploy-backups/20260923-230201-a2z-628-prepublish`; DB gzip + full media tar + SHA manifests passed. First #628 Batch `desktop_catalog_v85_20260923_230223` failed with UnicodeEncodeError and rolled back; Local remains Site Product #38 revision 1 / needs_update=1, so no partial publish was accepted.

Unicode fix verification: dedicated regression 1/1 PASS; full unified import 5/5 PASS; related visibility/profile/video 21/21 PASS; Python compile, Django check and makemigrations --check --dry-run PASS; no source/migration/schema delta beyond the bounded media-name contract.

Selective release is already GitHub-exact at `2b48a593ace2e9a3703fa0f52b4c3c13b2751cf9`, parent exactly `103f559c...`, with the exact five-file Server/test delta. Repository-owned guarded deploy runner `scripts/host/phase50_a2z_unicode_media_deploy.sh` is Local syntax/diff tested and enforces the exact baseline/target/allowlist plus rollback verification.

Production selective release is now deployed and verified at exact clean `2b48a593ace2e9a3703fa0f52b4c3c13b2751cf9`: rollback recheck PASS, migration plan 0 before/after, receiver ready=true, Unicode basename probe PASS, Home/Store HTTP 200. Fresh post-deploy/pre-#628 rollback `/home/sfkilvrs/3dprinthub-deploy-backups/20260924-105351-a2z-628-postdeploy-prepublish` passed source/MySQL/full-media/.env checks.

Changed-condition retry of only #628 used Batch `desktop_catalog_v85_20260924_105415` / UUID `bc40a728-5b26-453d-ba27-e74608ed8a7a`. FTP completed 12/12, but Bridge still returned the same `UnicodeEncodeError: ascii`; import remained failed, Local/Site revision stayed 1 and no third unchanged retry is permitted. This proves the Server/Public basename hardening is valid but not the complete root cause.

GitHub-exact tracer `6d0dbbe3...` then ran the failed Batch rollback-only and every internal importer stage PASSed, including `republish_parity ok=true / media_count=2 / profile_count=32` and Portfolio. Site Product #38 remained revision 1 after forced rollback. The remaining difference was proven at the physical Batch source path: forcing the exact uploaded Batch to `FS=ascii` reproduced the Production UnicodeEncodeError exactly at positions 127-131 while opening its Persian `local_image_files_json[0]`.

Windows packaging is now locally hardened: Unicode SEO filename stays in metadata, but the physical Batch/FTP filename and `local_image_files_json` use the same deterministic ASCII-safe name as Server canonicalization. Focused 1/1, bulk/batch 33/33, broader 50/50, compile/diff/Qt VerifyOnly and exact Windows-vs-Server basename parity PASS. Real #628 dry-run on a cloned Catalog generated two ASCII files, preserved metadata/SHA, and canonical Catalog logical digest/state remained unchanged. Evidence: `D:\projects\3dprinthub-backups\phase50-a2z-628-package-dryrun-20260924-111133`.

Production remains clean at `2b48a593...`; this final root-cause fix is Windows packaging only, so no additional Server deploy is required before the bounded retry.

Exact next: commit/push this documentation checkpoint -> Local=Remote -> exact-SHA Qt VerifyOnly/launch from the same source bytes -> fresh integrity Catalog backup -> Host/readiness gate + fresh Production DB/media backup -> preflight and publish only #628 once under the changed ASCII Batch-source condition -> strict Product/Image/Profile/Variant/Slider/public parity -> collateral readback -> Desktop/Mobile acceptance -> Phase 1 CLOSED.

## 2026-09-23 - Phase50.A.2Z EXACT-SHA LOCAL ACCEPTED / PRODUCTION REPUBLISH BLOCKED BY TUNNEL

Source checkpoint fde86e23ba6b0a1d5f578279289328708184baf9 is committed, pushed and Local=GitHub exact on wip/phase50-a2z-catalog-data-completion-20260923. Qt is running from that exact SHA.

Real Catalog mutation gates are accepted. Product #625 Site revision authority reconciled 11 -> 12 only from exact publish_incomplete receipt #316 / Batch 26aa571c-1a0c-4ad4-9431-65e74c27d94f; operator-owned digest remained byte-identical (6ba4929d...f7ab6) and SQLite quick_check stayed ok. Re-running the official Ready core preserved #625 profiles (5x5x5 and 4x4x4), 16 PLA options per profile, selected media and current 458,500-1,655,000 price range.

Product #628 was marked Ready through the exact-SHA PublishCore. Its two canonical profiles remain 12x12x12 / 113g / 511min and 18x18x18 / 312g / 991min, with exactly 16 PLA offers each; two selected images and their Local files are unchanged. The official pricing refresh advanced current range from 2,211,833-4,827,333 to 3,063,500-6,479,000 based on current Filament inventory. SQLite quick_check remains ok.

Fresh post-local rollback: D:\projectsdprinthub-backups\phase50-a2z-post-local-gates-20260923-215515\catalog-after-local-gates.sqlite3, quick_check=ok, SHA256 1c5b0439ea938d6b19af65fa07bedb08dbe80ac962efd772e6bf1e4c904848e8.

Production republish is intentionally blocked, not failed. Dedicated Windows loopback 127.0.0.1:22024 is not listening while sshd is Running/Automatic. The last accepted PrintHubTunnel authentication was 2026-09-23 14:19:41 from Host source 89.39.208.237 with the expected ED25519 fingerprint; current Windows public IP probe is 5.188.190.59. Public Catalog Bridge health/readiness still returns healthy/ready, but it exposes no Production backup endpoint. Per project policy, no Product DB/media write is allowed until the official reverse tunnel is restored and a fresh Production DB/media rollback is verified.

Exact next: restore only the documented PrintHub reverse tunnel -> read-only Host identity/worktree/DB/migration/readiness gate -> fresh Production DB+media rollback -> publish #625 alone -> strict ACK/public parity -> fresh rollback -> publish #628 alone -> strict Product/media/Profile/Variant/Slider parity -> Desktop/Mobile browser acceptance -> final docs closure.

## 2026-09-23 - Phase50.A.2Z CATALOG DATA COMPLETION LOCAL_TESTED / GITHUB PROMOTION NEXT

Active branch is `wip/phase50-a2z-catalog-data-completion-20260923` from clean accepted baseline `56c569145eead7cd0a35eb63c382f14dfe71c80e`. The preserved dirty A2Z precursor remains untouched; only evidence-backed Crawl incompleteness/recovery was ported, and the accepted canonical A2R video authority was preserved.

Current real Catalog truth is newer than the prior 635-Product snapshot: SQLite quick_check=`ok`, Products=771. Six-field Slider inventory is 61 complete / 710 incomplete; membership enabled=13 and exactly one enabled Product (#40) lacks `homepage_slider_image_url`. #152/#178 Site truth is already reconciled and must not be retried: #152 -> Site #50 / Hero #2 rev3; #178 -> Site #51 / Hero #4 rev6. #620 is already public/clean at Site #41 / Hero #17 rev1 and its current six Slider fields are complete.

#625 is the bounded stale-revision case: Local Site Product #39 rev11, `needs_update=1`, current Local price range 458,500–1,655,000; Site profile rev12. Sync receipt #316 proves Site rev12 was created by exact Desktop Product #625 Batch `26aa571c-1a0c-4ad4-9431-65e74c27d94f` with terminal `publish_incomplete`, not by an unknown Site edit. Source hardening now permits revision-only reconciliation only from such exact receipt proof; Product/media/Profile/Slider content remains Local-owned and unchanged. Unknown/mismatching revision evidence remains fail-closed. #628 remains Site #38 rev1 with Local `needs_update=1`; factual publish preflight passes.

Crawl recovery hardening is Local-tested: incomplete collected Products no longer get silently skipped, cards expose missing-data reasons, selected-row completeness can resolve canonical Product facts, and complete Products remain idempotent/no-refetch. Canonical video remains `video_links_json / selected_video_links_json / local_video_files_json`.

Verification: changed Crawl/V84 41/41 + Video 8/8 PASS; revision reconcile targeted 4/4 PASS; final related Catalog/Profile/Filament/Image/Slider/Site regression 153/153 PASS; Server 12/12 PASS; Django check and no migration drift PASS; Python compile/diff-check/Qt VerifyOnly PASS. Fresh pre-mutation rollback: `D:\projects\3dprinthub-backups\phase50-a2z-data-completion-pre-mutation-20260923-202714\catalog-before-a2z-data-completion.sqlite3`, backup/source quick_check=`ok`, both 771 Products.

**Current Production:** selective Server head `103f559c...` remains unchanged.
**Current local development HEAD:** baseline `56c569...` plus tested uncommitted A2Z Data Completion delta; commit/push is next.
**Exact next:** docs/static final check -> commit/push -> Local=GitHub exact -> exact-SHA Qt -> receipt-backed #625 revision-only reconcile -> #620/#625/#628 operator gates -> fresh rollback -> bounded same-identity republish -> strict public/Desktop/Mobile parity.

## 2026-09-23 - Phase50.A.2Z-LC A2R LINEAGE CONVERGENCE GITHUB_VERIFIED / ACCEPTED

A post-A2Y lineage gate found that the newest A2Z Windows head `3de2af09...`, Windows A2R `03808add...` and Production A2R `103f559c...` had diverged again. Per `AGENTS.md`, new A2Z feature work was stopped before any further Catalog/Social mutation.

The dirty A2Z Data Completion worktree was preserved unchanged. Rollback evidence: `D:\projects\3dprinthub-backups\pre-a2z-lineage-convergence-20260923-1821`; dirty patch SHA256 `d7b4fce25373a4427cf8d06db917da0e85bc9c5a41f8ec7d4f5807943c49e673`.

Runtime-bearing source convergence: `be00cc73d7745406b7219d323890f05222f17494`.
Accepted forward merge head: `05f29ba3a4de53fcf8b0a6fd73427a3653bb0ed3` on `wip/phase50-a2z-a2r-lineage-convergence-20260923`, Local=GitHub exact. Merge parents are source convergence + Windows A2R `03808add...` + Production A2R `103f559c...`; both accepted A2R heads are now ancestors of the unified forward head and the merge tree is identical to the tested source commit.

Canonical motion-media authority is now one path: `video_links_json / selected_video_links_json / local_video_files_json`. MakerWorld animated GIF motion media is supported, safe Source re-crawl preserves operator video selection/local media, Site Batch/import/public verification carry motion media, and Product detail renders public motion media. Buffer remains image-based for Feed/Story; Social Reel/video is not falsely claimed complete.

Verification: Catalog video 8/8, Social 41/41, Crawl/V84 40/40, Publish/Bridge 55/55, Django Server 12/12 PASS; Python compile, Django check/no-drift, diff-check, Host runner syntax and Qt VerifyOnly PASS. One stale historical Stage-3 button assertion was corrected after changed-condition proof; runtime was not rolled back.

Production remains clean and healthy on selective Server head `103f559c8a11c35495b4ac2a290d578c31c2a023`: MySQL correct, migration plan empty, readiness=true, Home/Store 200. Product #536 is Site Product #48 revision 2 with public GIF motion media HTTP 200. Unified-vs-Production audit shows no migration/dependency delta but does include unrelated Server settings/ZarinPal deltas, so no full unified deploy is permitted in this convergence phase.

**Current Production:** `103f559c...` (unchanged, verified healthy).
**Current forward development baseline:** `05f29ba3...`.
**Remaining:** carry the preserved A2Z Data Completion work onto this unified head without parallel video authority, then run its own local gates before any Catalog mutation.
**Exact next:** Phase50.A.2Z Catalog Data Completion on the unified branch -> incomplete-product truth/recovery -> canonical video UI -> Slider completeness preserving membership -> #620/#625/#628 operator acceptance -> Profile/Filament/Image gates -> fresh Catalog backup -> one controlled same-identity republish -> public/browser parity.

## 2026-09-23 - Phase50.A.2Z-S2 AUTOMATIC STORY + SHOP GRID LINK PRODUCTION_VERIFIED / ACCEPTED

Owner correctly reported two regressions in the newer Social route: real Story publication had worked before, while the newer mandatory Link-Sticker notification path made Story depend on Buffer mobile; and raw Product URLs shown in Instagram captions/Story artwork were being treated as if they were clickable links.

Historical real evidence resolves the ambiguity: Product #625 successfully published both Buffer Feed `6aaed28f6e039ccbc8221fa8` and Buffer Story `6aaed29a7fcdd8931977c3f1`; the Story reached `sent` and live Instagram Story without the later notification/mobile contract. Therefore automatic Story publication itself is proven.

A2Z-S2 restores that proven path as the default while preserving the newer native Link Sticker path as an optional mode:
- Provider remains Buffer GraphQL / channel `3dprinthub_ir`; media host remains `github_raw`.
- Feed remains `schedulingType=automatic` and keeps `metadata.instagram.link=<tracked Product URL>`, which is the Buffer Shop Grid Product link authority.
- Feed Caption no longer prints the raw tracked URL. CTA is now **«خرید این محصول: لینک بیو...»** because Instagram caption URLs are not clickable.
- Default Story link mode is now `bio_shop_grid`; Story is again `schedulingType=automatic`, matching the proven #625 path and requiring no Buffer mobile device.
- Native Instagram Link Sticker remains available only when `instagram_story_link_mode=native_sticker_notification`; only that optional mode requires Buffer mobile notification handoff.
- Story artwork remains 1080×1920 Gold/Navy + IRANSans, but no longer displays a raw Product URL as if clickable. CTA is **«خرید از لینک بیو»** with `@3dprinthub_ir`.
- Social policy becomes `instagram-product-v5-20260923`; Story style becomes `3dprinthub_instagram_gold_navy_v3_iransans_bio`.
- Story cache identity now includes Story style ID, so an old cached v2 Story image cannot be reused after the CTA/link correction.
- Existing Feed/Story receipt dedupe remains unchanged; a failed Story retry for an already-live Feed creates no new Feed.

Rollback: `backup/pre-a2z-s2-auto-story-shop-grid-20260923 @ 02be495fbf0f2cb48c527c280cf8b62edfeb2f38`.

Verification: focused Social/Story/link gate **27/27 PASS**. First full Site+Social run was 69/70 with one intentionally stale assertion that still required the tracking URL inside Caption; changed-condition assertion was updated to require UTM in tracking metadata but not Caption. Full Site+Social rerun **70/70 PASS**. All 11 changed Python files compile; `git diff --check` + Qt VerifyOnly PASS; Server/migration/template/static delta=0.

Runtime-bearing A2Z-S2 source is GitHub-exact at `447e81306a19d816042530f3d00989305a84bd2c` and running in Qt. Live readiness on that exact SHA returns `provider=buffer`, `story_link_mode=bio_shop_grid`, `feed_link_mode=buffer_shop_grid`, `requires_mobile_handoff=false`, `ready=true` while `has_active_member_device=false`; therefore default Social no longer depends on Buffer mobile.

Fresh pre-send Catalog rollback: `D:\projects\3dprinthub-backups\pre-a2z-s2-story536-20260923-111601\catalog-before-story536.sqlite3`, quick_check=`ok`, SHA256 `486d5c50d78f8e17e8e15ce173aa9b3d35400d0014147a5c3a96bd5a038f5b34`. Pre-state proved exactly one successful Feed receipt for #536 and no successful Story receipt.

Real bounded retry of Product #536 from exact SHA completed `published=1 / failed=0`. Existing Feed provider id `6ab2c7781259e27877f070c7` was reused with `resume_status=already_sent`; **zero duplicate Feed createPost** occurred. New automatic Story provider id `6ab383f9497d7707d81648c8` reached Buffer `sent` and live Instagram URL `https://www.instagram.com/stories/3dprinthub_ir/3992386891974821993`. Story receipt is `instagram_story_published`, `story_publish_mode=automatic`, `story_link_strategy=bio_shop_grid`, policy `instagram-product-v5-20260923`, style `3dprinthub_instagram_gold_navy_v3_iransans_bio`, IRANSans, 1080×1920.

Provider-media authority is GitHub branch `social-assets-buffer` exact at `3fedd69e2b1d107c3b05c24d50fdf9444235f8a7`; public Story asset `.../social_media/instagram/536/bc790a3a9f7af09b/story.png` is HTTP 200 image/png with SHA256 `ae9cf18bab82a9d40b963be92f28238bc308f038a73e6c839dd08c718eb7c729`, matching Local bytes. Buffer Shop Grid public page is HTTP 200 and its #536 tile carries the exact tracked Product destination `https://3dprinthub.ir/store/product/little-ballerina/?utm_source=instagram&utm_medium=social&utm_campaign=product_catalog&utm_content=product-536`.

Post-accept Catalog rollback: `D:\projects\3dprinthub-backups\post-a2z-s2-story536-20260923-111942\catalog-after-story536.sqlite3`, quick_check=`ok`, SHA256 `de20ec0cf04f46533a4bd4bc1fb2638c6cd96d276f7286f23faab63849c95964`.

Existing #536 Feed intentionally remains the historical v4 caption because duplicate safety reused the already-live post. That caption still contains the old raw URL; Buffer cannot edit a published Instagram post after send, so cleaning that one historical caption requires a direct Instagram edit. All **future** v5 Feed sends omit raw caption URLs and carry Product click-through only in Buffer Shop Grid metadata; new v3 Story artwork likewise contains no fake/raw URL.

A2Z-S2 is ACCEPTED.

**Exact next phase:** A2Z Catalog Data Completion -> Slider completeness/backfill with membership preserved -> #620/#625/#628 operator acceptance -> final Profile/Filament/Image gates -> one controlled same-identity republish -> browser/public parity.

**Immediately following phase:** changed-revision Social rollout using the accepted v5 Feed + automatic Story contract, then W5 manual Product.

## 2026-09-22 - Phase50.A.2Z-S SOCIAL DELIVERY READINESS GITHUB_UPDATED / WINDOWS_RUNTIME_ACCEPTED / BUFFER MOBILE EXTERNAL

Owner reconfirmed the Instagram contract and requested that the Windows action reliably create **Post + companion Story** under the already-accepted Social policy, without repeating the 2026-09-22 partial outcome where Feed succeeded and Story notification later failed.

Verified live provider/config from the real Catalog: `instagram_publish_provider=buffer`; Buffer GraphQL endpoint is `https://api.buffer.com`; channel id `6aabb3a8ea19ca0bde6694d5` / `3dprinthub_ir`; provider media host is `github_raw`; companion Story is enabled; clickable Story is enabled by default. Feed uses Buffer `createPost` with `schedulingType=automatic`, `mode=shareNow`, Product-specific caption/hashtags/per-image ALT and current Site-first Product URL/UTM. Companion Story uses the accepted 1080×1920 Gold/Navy + IRANSans renderer and Buffer `createPost` with `type=story`. When the Product Link Sticker is required, Story uses `schedulingType=notification` plus `stickerFields`; final Link Sticker completion therefore occurs in Instagram mobile. Existing Feed/Story receipts remain revision-scoped duplicate authority; Highlight target is recorded and final Highlight placement remains operator-required.

New hardening on rollback baseline `backup/pre-a2z-social-readiness-ui-20260922 @ 5dec164d14511bfd37adbc4ac69f146dc71eca7e`: `InstagramCore.delivery_readiness()` now checks Buffer channel health and `hasActiveMemberDevice` before any Site mutation, provider-media render/rehost or Feed createPost. `publish_site_then_instagram()` and `publish_many()` both retain fail-closed readiness, while `buffer_publish.publish_product()` keeps its lower-level duplicate/mobile guard. Products UI now labels the action **«Instagram (Post + Story لینک‌دار)»**, runs readiness before Worker creation and clearly refuses to start when linked Story delivery is impossible. This prevents a new partial state where Post succeeds while required Story cannot be handed to mobile.

Verification: focused readiness/Core/UI/Buffer gate **22/22 PASS**; complete Site+Social regression **69/69 PASS**; 4 changed Python files compile; `git diff --check` + Qt VerifyOnly PASS; Server/migration/template/static delta=0. No real Product/Site/Instagram mutation occurred during this hardening.

Live Buffer still reports `hasActiveMemberDevice=False`. Therefore software is ready but **new Post+linked-Story delivery remains externally blocked** until the same Buffer account is connected in Buffer mobile with push notifications enabled/reset/tested. Product #536 Feed remains live and duplicate-protected; do not recreate it. Buffer API boundary was also verified: `hasActiveMemberDevice` is read-only and the documented public GraphQL mutations expose no mobile-device registration/Test-Notification action, so this prerequisite cannot be completed safely from the Windows/API layer.

Runtime-bearing Social-readiness SHA is `ec05b77fec0d3316d8ee9663fb50b333cf437658`, Local=GitHub exact and running in Qt from the authoritative A2Y worktree. Exact-SHA Qt VerifyOnly/launch PASS. Live `InstagramCore.delivery_readiness()` on this SHA returns `provider=buffer`, `companion_story_enabled=true`, `clickable_story_enabled=true`, `requires_mobile_handoff=true`, channel `3dprinthub_ir`, and `has_active_member_device=false`; therefore the new guard correctly returns `ready=false` before all Site/provider/media work.

**Exact next external gate:** owner links/signs in to Buffer mobile with the same account, enables Buffer push notifications, uses Account Settings -> Push Notifications -> Reset Push Notifications, then sends a Test Notification from the Instagram channel settings. Re-run live readiness; only when `hasActiveMemberDevice=True`: fresh integrity Catalog backup -> one bounded intended Product Social action -> if Feed already exists for the current Site ACK, require zero new Feed createPost and Story notification only -> owner taps Buffer notification, opens Instagram, applies the prepared Product Link Sticker and publishes -> reconcile truthful provider receipt -> record Highlight target/operator step.

**Following development phase after Story acceptance:** resume A2Z Catalog Data Completion, then changed-revision Social rollout and W5 manual Product creation.

## 2026-09-22 - Phase50.A.2Z-C3 ACCEPTED / HERO CONFLICTS PRODUCTION_VERIFIED / SOCIAL APP HARDENING GITHUB_UPDATED / STORY EXTERNAL_MOBILE_BLOCKED

Owner reported real Site publish failure with FTP `550 Can't create directory: Disk quota exceeded` and requested a one-click **«✅ ثبت کامل»** beside **«✏ ویرایش کامل»** so current edits can be saved and all seven complete Stages approved without seven separate confirmations.

C3 implementation is Windows-only: Product Wizard now exposes **«✅ ثبت کامل»**. It saves the current unlocked Stage first, then `StageCore.finalize_all_ready()` reuses the existing fail-closed `finalize()` validation with explicit manual approval across canonical `STAGE_ORDER`, including Publish Stage only as an approval state. Incomplete Stages remain blocked and are reported. The action never calls readiness queueing, Site publish, FTP/Bridge or Instagram.

Verification: focused Full Registration/Full Edit **3/3 PASS**; related Stage Finalization + Product Wizard + Site Publish + Unified Desktop + Slider **82/82 PASS**; 3 changed Python files compile; diff-check and Qt VerifyOnly PASS; Server/migration/template/static delta=0. The first focused run failed only because the new UI method omitted the existing `stage_locks` import; no real Catalog mutation occurred, import was added, and changed-condition rerun passed 3/3.

Publish incident evidence is bounded: batch `desktop_catalog_v85_20260922_171201` / UUID `32a25891-282c-498a-bed1-4498b4303059` contains **Product #536 only**, 7 local files, and receipt chain `batch_ready -> publish_started -> publish_failed`; there is no `desktop_ftp_uploaded` and no Bridge import. Product #588 had already failed earlier with the same quota class. Current local queue inventory is 15 Products; recovery must never blindly send the full queue.

Historical pre-recovery tunnel evidence: during the quota incident `127.0.0.1:22024` was absent and the only visible Host-IP session was **RetoucherTunnel**, which was correctly not reused. This condition is superseded by the verified PrintHubTunnel recovery below; another project's tunnel remains permanently prohibited.

Active phase: `docs/phases/PHASE50_A2Z_C3_FULL_REGISTRATION_QUOTA_RECOVERY.md`.

Runtime-bearing C3 SHA is `ac094945901cfd612dd6069fdd473a995c8a204a`, Local=GitHub exact and running in Qt from `D:\projects\3DPrintHub-a2y-converge\catalog_center\qt_launch.py`. Exact-SHA widget smoke **4/4 PASS** for Full Edit, Full Registration, seven-stage explicit approval without send, and Products Bulk AI presence.

Quota recovery is now Production-verified. Owner freed Host account space; control-panel usage is ~1.44 GB / 1.95 GB. Official PrintHubTunnel recovered with expected fingerprint `SHA256:vzNCviwq432S+qQXPsCIjvVuHN8xYYqOiHSqZEPVfnY`; Windows `127.0.0.1:22024` is reachable and authenticated bridge health passes. Host `.git/index.lock` is absent, Git worktree is clean, Host write-test passes, and the exact FTP publication path `/3dprinthub/imports/desktop_catalog/pending` passed `MKD + 1KB STOR + DELETE + RMD` using the real configured FTP account.

Real post-recovery Batch `desktop_catalog_v85_20260922_181511` / UUID `fd336bc1-4a04-416f-a6ea-8526dddfb4b2` uploaded all 31 files. Results: #140 updated, #151 updated, #210 updated, #536 created as Site Product #48, #588 created as Site Product #49; #152 and #178 failed only on stale Hero revision conflicts. #536 public Product HTTP 200 and main image HTTP 200/image-webp with SHA256 `6b264047f956c485047b9afe55b61f551ed01a63a0e5c8b8f79a7fb25952f58d`; republish parity is `ok=true`, media_count=1, profile_count=64. Local publish queue has fallen to 10.

Hardening rollback ref `backup/pre-a2z-c4-hero-social-preflight-20260922` points to exact clean baseline `cbec63e9b007a20b7e3070eece74b0328afc212a`.

Hero truth has now been read-only verified: #152 Local Hero #2 rev1 vs Site rev2; #178 Local Hero #4 rev3 vs Site rev5. Titles match operator intent, so the conflict is revision authority only. Windows publish now refreshes only `server_slider_revision` from current Site Hero truth before packaging; Product text, Slider SEO/image, Slider membership and Publish selection are not overwritten. Focused changed contracts 16/16 PASS; full Site+Social regression 65/65 PASS; 5 changed Python files compile; diff-check + Qt VerifyOnly PASS; Server/migration/template/static delta=0.

Instagram hardening is also Local-tested. Buffer channel `3dprinthub_ir` is connected/unlocked but currently reports `hasActiveMemberDevice=False`. New clickable-Link Story preflight reads this before any new Feed is created. If no mobile device exists, a new Product Social send stops before Feed creation; if the current Site ACK already has a Feed receipt, that Feed remains duplicate-protected and only Story remains blocked. Product #536 Feed is already live at `https://www.instagram.com/p/DdmXo5QlMEd/`. Its github_raw Story asset is exact at social-assets revision `eb33bf7ebb1835a6`, 1080×1920 PNG, SHA256 `d2ca7066f6970c90521a9580908d229c12f695f87dffc3427f0f1d92869e74c6`, rendered by the accepted Gold-Navy/IRANSans Story pipeline. A clickable Instagram Link Sticker cannot be delivered through Buffer notification until the same Buffer account has an active mobile reminder device; automatic/no-link fallback remains prohibited by owner contract.

Runtime-bearing hardening SHA `bed7b27a7851a925af6756f70f7bbc5b71ab1845` is Local=GitHub exact and running in Qt. Fresh pre-retry Catalog rollback: `D:\projects\3dprinthub-backups\pre-a2z-c3-hero-retry-20260922-221533\catalog-before-hero-retry.sqlite3`, quick_check=`ok`, SHA256 `31ef9ff91d864af9b0b9e3df531f3303582ff67dfbd915215d21c626b0895c31`. Fresh Production MySQL rollback: `/home/sfkilvrs/3dprinthub-deploy-backups/20260922-221700-phase50-a2z-c3-hero-retry/database-before-3i53.sql.gz`, size 3,081,973 bytes, gzip independently valid, SHA256 `a6e5b74b5125656d088b42603382c52611778ad541653750befac0249eb86ddd`.

Bounded retry Batch `desktop_catalog_v85_20260922_221736` / UUID `1dfaddfc-976e-42ca-b7a2-1d9464353c1a` published **2/2, failed 0**. #152 is now Site Product #50 / Hero #2 rev3 with 3 media and 48 profiles; #178 is Site Product #51 / Hero #4 rev6 with 2 media and 64 profiles. Both ACK republish parity objects are `ok=true`; independent Product and all five canonical media URLs return HTTP 200. Site Hero truth is active for both and desktop-owned. Pre/post operator-owned digests are byte-identical for both Products, proving revision reconciliation did not overwrite Product/Slider content or membership. Local queue is now 8. Post-accept Catalog rollback: `D:\projects\3dprinthub-backups\post-a2z-c3-hero-accept-20260922-221907\catalog-after-hero-accept.sqlite3`, quick_check=`ok`, SHA256 `712d54b026d6cc09113eb52d35c028e08c083fa2a0ecedf3c15e36e79f72e255`.

C3 is closed. Social application hardening is also GitHub-updated at the same SHA: clickable Story delivery preflights Buffer mobile capability before any new Feed createPost, and an existing Feed remains duplicate-protected. Live Buffer still reports `hasActiveMemberDevice=False`, so #536 Story cannot yet be handed to Instagram. #536 Feed remains live at `https://www.instagram.com/p/DdmXo5QlMEd/`; do not recreate it.

**Exact next external action:** owner signs into the Buffer mobile app with the same account, enables Buffer push notifications and resets/tests push notifications. After Buffer reports `hasActiveMemberDevice=True`: fresh Catalog backup -> retry #536 Social exactly once -> Feed must be reused/no createPost -> Story notification only -> operator opens Instagram, applies the Product Link Sticker from the prepared URL and publishes -> read provider/receipt state and record truthful Story completion.

**Next development phase after Story acceptance:** Phase50.A.2Z Catalog Data Completion: six-field Slider inventory/backfill with membership preserved -> #620/#625/#628 operator acceptance -> final Profile/Filament/Image gates -> one controlled same-identity re-publish -> strict browser/public parity.

**Immediately following phase:** A2Z-S changed-revision Social rollout across subsequent eligible Product revisions, then W5 manual Product creation under the master order.

## 2026-09-22 - Phase50.A.2Z-C1/C2 FULL EDIT + UNIFIED BULK COMPLETION GITHUB_UPDATED / WINDOWS_RUNTIME_ACCEPTED / CLOSED

Owner-requested Windows Catalog completion slice is implemented on clean baseline `494a222b64908563c5d6b953b4ef96f9782c8e0d`; rollback ref `backup/pre-a2z-full-edit-bulk-completion-20260922` preserves that exact baseline. No real Catalog, Site, Host or Production mutation has been performed by this slice.

C1 adds a top Product Wizard button **«✏ ویرایش کامل»**. It reuses the existing StageCore unlock authority/history to open every finalized stage together. Entering Full Edit only changes stage-lock state: it does not publish, toggle Slider membership, change Site-image membership, or mark an uploaded Product dirty merely by entering edit mode. Existing per-stage «اصلاح مرحله» remains unchanged.

C2 extends only the Products multi-select **«AI تکمیل همه موارد»** preparation/post-processing path. The single configured Product AI engine remains authoritative; after AI content, deterministic accepted project capabilities now run in sequence: validated Category repair for blank/`external-other`; MakerWorld factual Source Profile refresh with cached fallback; A2W multi-profile import preserving manual profiles; every current exact-family Local Filament for each Source material (e.g. all PLA offers for Source PLA); accepted physical Product-local SEO filename finalization; and A2X six-field Slider completeness from existing content-pack/Product data. `homepage_slider_enabled` and Publish remain operator-owned and are never toggled by this command.

Integration also exposed ERR-49-223: the old ASCII-only Category fold reduced Persian names to empty strings, allowing a Persian Source Category to match `external-other` before its real taxonomy row. Folded matching now requires non-empty folded values; direct Unicode name/slug equality remains first-class.

Accepted runtime-bearing SHA is `8629f8b72c416b364a618a5aeebe2dda8a81d440`, pushed exact Local=GitHub on `wip/phase50-a2z-image-social-authority-20260921`. Exact-SHA `RUN_QT.ps1 -VerifyOnly` PASS and real Qt runtime points to `D:\projects\3DPrintHub-a2y-converge\catalog_center\qt_launch.py`. Widget-level exact-SHA smoke PASS 2/2: Product Wizard exposes/enables «✏ ویرایش کامل» on a loaded Product; Products page retains the multi-select Bulk AI action and source selector. Idle real Catalog remained unchanged while Qt was running: Products 635, history/max_history 2646, quick_check `ok` before/after.

Verification retained: new focused contracts **3/3 PASS**; broader Stage/Image/Profile/Filament/Site rerun **129/130 PASS** with the sole failure exactly the historical ERR-49-203 Manufacturer-vs-Brand assertion; prior related gate **148/149 effective PASS** with the same sole baseline; unchanged AI/completion/Unified Desktop/Slider rerun **40/40 PASS**; 6 changed Python files compile; `git diff --check` and Qt VerifyOnly PASS; migration/dependency/Server/website/template/static delta = 0.

C1/C2 is closed. No Production deploy is required because this slice changes only Windows Catalog Center behavior; no real Product, Site, Host or Production data was mutated for acceptance.

**Exact next active phase: Phase50.A.2Z Catalog Data Completion.** Ordered operations: fresh integrity-checked Catalog backup -> authoritative six-field Slider inventory -> deterministic/no-AI backfill from saved content where possible while preserving every `homepage_slider_enabled` checkbox -> AI only for genuinely missing editorial fields -> real #620/#625/#628 operator acceptance including the new Full Edit/Bulk completion surfaces -> final Filament/Image/Profile gates -> fresh backup -> one controlled same-identity re-publish -> strict public Product/media/Profile/Variant/Slider parity + browser verification -> docs closure.

**Following phase:** A2Z-S changed-revision Instagram rollout/Story recovery under the already-recorded Social policy and duplicate guards.

## 2026-09-22 - Phase50.A.2Z ERR-49-221 PUBLISH-READINESS WAF HOTFIX LOCAL_TESTED / GITHUB + REAL #588 RETRY NEXT

Current authoritative Windows worktree is `D:\projects\3DPrintHub-a2y-converge` on `wip/phase50-a2z-image-social-authority-20260921`. Baseline before this hotfix is clean/exact Local=GitHub `0202bdcafc252b1d409310838831bb0ea35100ee`; rollback ref `backup/pre-err49-221-waf-readiness-retry-20260922` points to the same SHA.

Owner's real Product #588 publish attempt failed before Batch/FTP/import because public `/api/catalog-bridge/v1/publish-readiness/` returned BitNinja `Visitor anti-robot validation` HTTP 403 HTML. Product history proves #588 had just completed Commerce/Images/Publish finalization and `qt_bulk_publish_ready`, while no new desktop Batch/FTP receipts exist for that attempt. A changed-condition read-only probe with the real secure Bridge token now returns health HTTP 200 and publish-readiness HTTP 200 / `ready=true` for current, Catalog-UA and browser-UA requests, proving the 403 was transient WAF behavior rather than invalid credentials/receiver state.

Windows hotfix is intentionally narrow: Catalog Bridge requests now include a bounded Catalog User-Agent and no-cache header; only idempotent GET requests retry a positively identified BitNinja/anti-robot 403, with at most three total attempts and short backoff. POST import remains exactly one attempt and is never automatically retried. Persistent WAF HTML is reduced to a concise operator error instead of a multi-kilobyte HTML dump. Focused 13/13 PASS; corrected Publish/SiteConnection regression 86/86 PASS; py_compile, diff-check and RUN_QT VerifyOnly PASS. The first broad regression command used one nonexistent module name; 63 real tests passed and the corrected manifest passes 86/86; ERR-49-222 records the harness error.

No Catalog/Site/Production mutation was performed by the failed #588 publish or by this Local hotfix. Dedicated Host-management reverse tunnel `127.0.0.1:22024` is currently unavailable, so Host source deployment remains fail-closed; this Windows-only hotfix does not require a Host deploy.

Exact next: update docs/commit/push ERR-49-221 -> verify Local=GitHub exact SHA -> fresh integrity-checked Catalog SQLite backup -> exact-SHA Qt relaunch -> live readiness must be HTTP 200 / ready=true -> retry **only Product #588** once through the canonical Product publish action -> require exactly one new Batch/start/FTP/terminal ACK chain -> verify Site identity/revision, Profile/Variant/media parity and public Product/media HTTP. Do not publish the other 12 queued Products as part of this acceptance.

## 2026-09-21 - Phase50.A.2Z-S #609 INSTAGRAM TRANSPORT FIX LOCAL_TESTED / REAL SEND NEXT

Repository/worktree verified clean before change on `wip/phase50-a2z-image-social-authority-20260921 @ 16257767c3783472d69f770789f2c4889f0cb25b`. Production Site read-back is already newer than the stale section below: Desktop #609 maps to Site Product #42 / `ProductCatalogProfile.sync_revision=2`, exactly five ProductImages exist, and all five public `/media/p/609/<sha12>/...-01..05.webp` URLs are HTTP 200 with SHA256 exactly matching current Windows final SEO authority. Therefore no second Site re-publish was performed.

Social rules re-read from A2N/A2O/A2P/A2Q/A2S + master A2Z-S: Site-first; exact Site-selected set Primary first; Feed+companion Story; per-image ALT; Product-specific factual caption; max 8 relevant hashtags; UTM Product URL; nationwide-Iran shipping; no false free/download claims; 1080x1920 Gold/Navy IRANSans Story; duplicate-revision guard; approved Highlight target recorded with final Add-to-Highlight operator_required. Real #609 policy preflight passes: Buffer channel `3dprinthub_ir` connected, provider=buffer, host=`github_raw`, media=5, ALT=5, hashtags=8, forbidden-free=false, policy `instagram-product-v4-20260920`, Highlight target `قطعات سفارشی`, and zero Instagram receipts for current Site ACK/revision 2.

Fresh pre-social Catalog rollback: `D:\projects\3dprinthub-backups\pre-instagram-a2z-609-20260921-201631\catalog-before-instagram.sqlite3`; quick_check=`ok`, SHA256 `b80515a1776ccd7e1fae10ab25a66e60c0172f52b25529ae3e24f7175aa6cd6f`, revision 2, Instagram receipts 0.

Real preflight exposed ERR-49-219 before any Buffer post: Story's unnecessary intermediate Site FTP upload reset with WinError 10054. This is now corrected so `github_raw` renders Feed/Story locally and bypasses Site FTP; `site` mode preserves the old FTP path. Rehost still requires the clean dedicated `D:\projects\3DPrintHub-social-assets` worktree / `social-assets-buffer`, exact remote-head equality and public image MIME verification.

Verification: complete Social regression 35/35 PASS for the github_raw transport fix. Real #609 local-only render produced five Feed PNGs (all valid Instagram aspect sizes) and one 1,461,858-byte 1080x1920 Story in approved IRANSans style; receipt count remained 0. The resulting #609 social-assets commit `3294d817...` is an ancestor of current clean/exact `social-assets-buffer @ 2cc87108...`; all five Feed PNGs plus Story are public HTTP 200 `image/png` and byte-for-byte SHA256-equal to the manifest. A final Story-link compliance delta is now also Local-tested: clickable Product-link Story uses Buffer `schedulingType=notification`, carries explicit Link Sticker handoff text/UTM target, records `instagram_story_notification_ready` rather than falsely claiming live publication, and remains duplicate-guarded. Social regression with this delta is 36/36 PASS; compile/diff/Qt VerifyOnly PASS. No Buffer createPost has been called after these checks yet.

Real external acceptance has now started exactly once. Feed Buffer post `6ab16b897465bdab83a3fe40` reconciled read-only from `sending` to `sent` and is live at https://www.instagram.com/p/DdjtyiMG8RC/ with the exact five github_raw assets. A final `instagram_published` receipt was appended with `reconciled_without_repost=true`; Feed must never be recreated for this Site ACK.

Companion Story provider post `6ab16b959d554f7b28a44302` is not live. Buffer Post read-back proves `status=error`, no external link, and exact provider failure `No devices found for allowed reminder recipients to send push notification to!`. Therefore this is an external Buffer reminder-device prerequisite, not media/channel/policy failure. ERR-49-220 hardens recovery: provider error cannot be recorded as Story-ready; historical false-ready/error receipts are ignored by duplicate guard; after the Buffer mobile prerequisite changes, retry resumes Story only while Feed remains protected. Social 37/37 PASS + compile/diff/Qt VerifyOnly PASS.

ERR-49-220 recovery hardening is now committed/pushed exact at `c064c36f2d389bb0114489f958c9026b8573316b`. Post-send rollback is `D:\projects\3dprinthub-backups\post-instagram-feed-609-20260921-211603\catalog-after-feed.sqlite3`, quick_check=`ok`, SHA256 `a992c2de67d7d9c6da06f72f97c64e1aa7f35835ca28432a93e4d86cc3cb7d2b`, Product revision remains 2. Receipt truth is preserved: submitted Feed #334, historical false-ready/error Story #335, reconciled published Feed #336 with `reconciled_without_repost=true`.

**Exact next:** owner links/signs in to Buffer mobile for the same Buffer account and enables reminder notifications. After that changed condition: read-only Buffer channel/error-state gate -> fresh Catalog backup -> retry #609 exactly once through the normal Social action; Feed must reuse current receipt and issue no createPost, while only Story notification may create -> require non-error Buffer notification state -> operator completes Instagram Link Sticker handoff -> record truthful Story/Highlight result -> A2Z-S closure. Do not switch to automatic no-link Story.

**Following phase:** return to A2Z Catalog Slider completeness/backfill + final Windows operator acceptance, then continue bounded changed-revision Social rollout.

## 2026-09-21 - Phase50.A.2Z #609 REAL LOCAL MEDIA REPAIR COMPLETE / PUBLISH-GATE DRIFT FIX LOCAL_TESTED

Fresh rollback before #609 mutation: `D:\projects\3dprinthub-backups\phase50-a2z-609-pre-repair-20260921-194148`; SQLite quick_check=`ok`, SHA256 `eaa0ea055e8ba30bb05c1434ffda06874fbc5f93129ce2bf45d58303f123edf4`, full Product #609 media backup 36 files + manifest.

Using exact pushed Windows runtime `5336b6b71eac9758152814e8bf678b802926540f`, application-level `ImageCore.finalize(609)` repaired real #609 without SQL: selected 5, canonical 5, deterministic physical SEO names `goth-baroque-necklace-display-bust-3d-print-01.webp` through `-05.webp`; local screenshot/04/05 identities remapped to SEO basenames; selected source/cache bytes archived under `source_originals/`; DB quick_check remained ok. Site identity remains Product #42 revision 1; no Site publish has occurred yet.

First post-repair preflight correctly exposed ERR-49-218: all five were falsely tagged source-drift because active `source_local_file` SEO bytes were compared to original source SHA. Fix now prefers preserved `original_local_file` for source-drift. Focused changed-source/promotion/Batch 3/3 PASS and Image+Site Publish 51/51 PASS.

Exact next: compile/diff/Qt VerifyOnly -> commit/push ERR-49-218 fix -> Local=GitHub -> exact-SHA relaunch -> explicit `mark_ready_many([609])` -> verify five-media publish package -> verify reverse tunnel/Host/Production identity and fresh rollback -> same-identity Site #42 republish -> ProductImage count/name/SHA/public HTTP parity -> changed-revision Instagram Feed+Story with duplicate protection.

## 2026-09-21 - Phase50.A.2Z PHYSICAL SEO FILENAME + MULTI-IMAGE + SOCIAL HOTFIX LOCAL_TESTED

Owner clarified the required image contract beyond the first A2Z fix: «اصلاح اسم و سئو» must rename the actual Product-local physical files, not only metadata/cards and `seo_images`. The implementation now promotes each selected Product-local image to the deterministic SEO WebP basename in `images/`, archives the old source/cache bytes in `source_originals/`, persists the exact physical path, remaps local identities, and prevents duplicate SEO basenames. Removal remains recoverable for the new SEO-named local files.

#609 read-only evidence before real repair remains: five unique finalized SEO WebPs already exist `-01..-05`, while Product-local `images/` still contains legacy names such as `01.webp/02.webp/04.webp/05.webp` and hash-cache files. No real Catalog write has yet been made by this new physical-rename slice.

Verification after owner correction: direct rename/query-variant/recovery 3/3 PASS; combined Image/Publish/Windows/Social 109/109 PASS; 3 touched Python files compile; diff-check and Qt VerifyOnly PASS. The first broad run had exactly one stale assertion expecting `local://02.webp` to survive SEO; the new accepted contract correctly changes it to `local://table-lamp-3d-print-02.webp`, and the changed-condition rerun passed.

Exact next: docs -> commit/push exact A2Z physical-rename SHA -> Local=GitHub -> exact-SHA Qt relaunch -> fresh integrity-checked Catalog + full #609 local-media backup -> application-level SEO/authority repair for #609 -> prove physical `images/` names, canonical/selected metadata and publish gate -> same-identity Site #42 republish with all selected media -> Production media/filename parity -> changed-revision Instagram Feed+Story using reused social worktree and no duplicate receipt.

## 2026-09-21 - Phase50.A.2Z IMAGE + SOCIAL AUTHORITY HOTFIX LOCAL_TESTED

Owner screenshots on real Product #609 exposed three linked defects. Site publish failed closed because selected Local media `local://04.webp` and `local://05.webp` were not in canonical `images_json`; Instagram failed because `social-assets-buffer` was already registered to `D:\projects\3DPrintHub-social-assets`; and two query-variant source URLs could display the same SEO filename because UI metadata lookup collapsed exact URL identity.

Real #609 read-only audit: 5 selected media and 5 finalized physical SEO WebPs exist under `seo_images`, uniquely numbered `...-01.webp` through `...-05.webp`. The source/cache `images` directory intentionally retains provenance names such as `01.webp/02.webp/04.webp/05.webp`; public Batch/Site authority is the finalized `seo_images` set. Product #609 currently maps to Site Product #42 revision 1.

Local fix: Stage-3 Site selection promotes trusted Product-local media into canonical `images_json`; exact source URL metadata/SEO-slot identity wins before canonical-key fallback; Buffer media hosting reuses an existing registered worktree for `social-assets-buffer`. Batch regression proves four selected media become four uniquely named SEO WebPs in the publish package.

Verification: new focused gate 9/9 PASS; broad Image/Publish/Windows/Social gate 113/113 PASS; 7 touched Python files compile; diff-check and Qt VerifyOnly PASS. Two unrelated UI assertions reproduced identically on clean baseline `f5f40116...` and were aligned to the already-accepted separated Site-selection/source-refresh UI contract. No real Catalog or Production mutation has occurred yet.

Exact next: commit/push A2Z source -> exact-SHA Qt -> fresh Catalog + #609 local-media backup -> application-level #609 authority repair -> same-identity Site republish -> verify all selected public images and SEO filenames -> changed-revision Instagram Feed+Story acceptance. After this hotfix, continue A2Z Slider completeness/backfill.

## 2026-09-21 - Phase50.A.2Y PRODUCTION-SOURCE CONVERGENCE ACCEPTED / WINDOWS RUNTIME ACCEPTED / CLOSED

Authoritative forward worktree: `D:\projects\3DPrintHub-a2y-converge`, branch `wip/phase50-a2y-lineage-convergence-20260921`. Runtime-bearing merge commit is `f9a9c203ae3a0a5665dbf884ce0c3e4bf761110b` with parents `c593eaf4b9f23652986231ee1c5581bfee9a7d70` (latest Windows/A2Y planning lineage) and `e03bdd2b718fae3ce030df789c8b9db958d8d8ed` (accepted Server/Production closure). GitHub branch read-back matched the merge SHA exactly before runtime launch.

Exact-SHA Qt acceptance PASS from that unified SHA. `RUN_QT.ps1 -VerifyOnly` passed, and the live process tree is `pythonw.exe -> D:\projects\3DPrintHub-a2y-converge\catalog_center\qt_launch.py`. Both runtime processes were responsive. Shared Catalog stayed read-only through the launch: Products=635, product_history=2536, max history id=2536 and `PRAGMA quick_check=ok` before and after.

Desktop launchers are now intentionally cut over to the unified worktree only after runtime acceptance. Fresh shortcut rollback: `D:\projects\3dprinthub-backups\phase50-a2y-shortcut-20260921-183438`; pre-cutover SHA256 values: LNK `d37705a7bbb14c18d6ef6d4f2ce3144ec1817a63db612be685c5ec2153f0a7c3`, CMD `789346af71068279f523b6bbf86268b5d37fa0f895ec425903bcc51873aab02e`. Both Desktop launchers now resolve `D:\projects\3DPrintHub-a2y-converge\catalog_center\RUN_QT.ps1`.

A2Y acceptance evidence remains: Windows A2W/Slider/Image/Social 94/94 PASS; Server unified import/Profile/republish/payment/finance/Hero 52/52 PASS; broad Windows 115/116 with the sole known baseline ERR-49-203 Manufacturer-vs-Brand assertion; 46 changed Python files compile; Django check/no-drift, diff-check and Qt VerifyOnly PASS. Static Hero/template bytes equal the accepted Server `e03bdd2b...` versions, and there is no migration/dependency delta. ERR-49-215 records the stale 50.8.0 test assertion corrected to accepted 50.10.0.

No Catalog data backfill, Site re-publish, Host source promotion or Production DB write was performed for A2Y. Existing Production Server functionality remains accepted; convergence was a source-baseline and Windows-runtime operation.

**Exact next phase: Phase50.A.2Z — Catalog Data Completion + Windows Final Operator Acceptance.** Ordered operations: fresh integrity-checked Catalog backup -> inventory/recount all Slider gaps -> no-AI backfill from saved content packs while preserving every membership checkbox -> AI only for genuinely missing editorial fields -> verify all Products complete or explicitly blocked -> real Qt acceptance of #620/#625/#628 and Filament/Image flows -> fresh backup -> one controlled same-identity republish -> strict Site media/Profile/Variant/Slider parity + browser verification -> A2Z docs closure.

**Phase after A2Z:** A2Z-S changed-revision Site-first Instagram Feed+Story/Highlight queue acceptance.

## 2026-09-21 - Phase50.A.2Y LINEAGE CONVERGENCE LOCAL_TESTED / MERGE COMMIT + EXACT-SHA QT NEXT

Clean convergence worktree: `D:\projects\3DPrintHub-a2y-converge` on branch `wip/phase50-a2y-lineage-convergence-20260921`. It starts from A2Y planning head `c593eaf4b9f23652986231ee1c5581bfee9a7d70` (latest Windows parent `c86c66a1...`) and merges Production/Server closure `e03bdd2b718fae3ce030df789c8b9db958d8d8ed`. The pre-existing dirty planning worktree was deliberately left untouched.

Conflict policy was evidence-based: latest Windows/Qt/A2W/Slider workspace remained authoritative for Desktop conflicts; hardened A2S Social provider/policy deltas were retained; Store authoritative republish/payment/finance and Production Hero/public-media code came from the Server lineage. No Catalog/SQLite/Production mutation occurred.

Verification on the merged tree: Windows A2W/Slider/Image/Social focused gate **94/94 PASS**; Server unified import/Profile/republish/payment/finance/Hero gate **52/52 PASS** after correcting one stale baseline mobile-Hero cache assertion from 50.8.0 to accepted Production 50.10.0; broad Windows gate **115/116** with only the already-proven baseline ERR-49-203 Manufacturer-vs-Brand assertion; 46 changed Python files compile; Django check and no-migration-drift PASS; `git diff --check` PASS; Qt `RUN_QT.ps1 -VerifyOnly` PASS.

Production A2X closure behavior is present in the unified tree: material parity uses case-insensitive identity, Hero persistence uses Product-owned public media, authoritative Desktop SEO/re-publish remains fail-closed, A2S finance/reviewer code is retained, and current Slicebox cache contract is 50.10.0. No migration/dependency delta was introduced by conflict resolution.

Exact next in A2Y: create the convergence merge commit -> push and verify Local=GitHub -> launch Qt from that exact unified SHA -> retarget Desktop shortcut only after runtime smoke -> re-run final clean status/launcher proof -> documentation closure. Production deploy is not required merely for lineage convergence because Server runtime changes are already live; Catalog backfill remains A2Z.

## 2026-09-21 - Phase50.A.2Y MASTER RECONCILIATION / DOCUMENTATION TRUTH FROZEN

Repository/chat-archive audit found a real split forward state. Latest Windows/Product work is clean and remote-exact at `c86c66a11e2c62f8ca219bcb76abc19e5bfdcdbd` in `D:\projects\3DPrintHub-a2u-latest-windows`; the Desktop shortcut already points to that worktree. Current Production/Server closure is `e03bdd2b718fae3ce030df789c8b9db958d8d8ed` on Host branch `release/phase50-a2j-hero-20260915`. Neither head is an ancestor of the other; merge-base is `b1caeba0f20e711b29dfa9e0ff92a2f5186fb08d`. Therefore permanent feature work is blocked on A2Y convergence rather than choosing either lineage and risking regression.

The old primary clone `D:\projects\3DPrintHub` remains intentionally untouched because it has pre-existing local documentation changes and is behind its remote branch. A clean isolated planning worktree `D:\projects\3DPrintHub-a2y-plan` was created from exact latest Windows `c86c66a1...`; rollback ref `backup/pre-phase50-a2y-master-plan-20260921` points to the same baseline.

Real canonical Catalog read-only audit: SQLite integrity `ok`, 635 Products. Slider core fields are image/title/description/ALT/button/focus. Only 50 Products currently have all six; 585 have at least one missing field. This is a real data-completion task, not only a code task. #620/#625/#628 themselves currently show populated core Slider data, and W4.1 accepted dimension/PLA state remains recorded: #628 12x12x12 / 18x18x18 with all 16 active exact PLA offers; #625 5x5x5 + owner-estimated 4x4x4 with all 16 active exact PLA offers.

Full remaining-work sequence is now frozen in `docs/phases/PHASE50_A2Y_MASTER_RECONCILIATION_AND_REMAINING_WORK.md`: A2Y convergence -> A2Z Catalog/Windows completion -> A2Z-S Social -> A2Z-W5 manual Product -> A2Z-W6 video/Reel -> A2Z-C dynamic carriers -> A3 ZarinPal -> A4 Torob -> B1 Auth/Customer -> B2 Engagement -> B3 customer Telegram Bot/Mini App -> C1-C5 accounting stack -> D1 final release/UAT.

Historical Roadmap unchecked boxes are no longer treated mechanically as pending. Store Reset, manual card-transfer acceptance, finance/receipt audit, latest Windows recovery, image authority, A2W W1-W4.1 and A2X Server/Hero are completed milestones and must not be rerun merely because an older section still contains `[ ]`.

**Exact next phase: Phase50.A.2Y — Lineage Convergence.** Operations: merge current Windows `c86c66a1...` with current Server/Production fixes `e03bdd2b...` on the isolated A2Y lineage -> run Windows/Qt and Django parity/Hero regression -> no-drift/diff-check -> push exact merged SHA -> launch exact-SHA Qt -> only then make it the sole forward baseline. No Catalog mutation and no Production deployment are required merely for source convergence.

## 2026-09-21 - Phase50.A.2X Slider SEO + authoritative re-publish LOCAL_TESTED / GitHub promotion next

A2X is active on `wip/phase50-a2x-slider-authoritative-republish-20260921` from exact W4.1 baseline `7f2280eafe7a3293008a6dc7a4559b0ef92f114c`. Slider SEO/media completeness is now independent of homepage membership: every Product must carry Slider title/description/ALT/button/focus/image data, while only the operator checkbox controls actual homepage membership. Single-Product completion and multi-select SEO completion both fill Slider data without enabling the checkbox.

Published-Product edits now recognize either preserved Site linkage field and force same-identity re-publish. Server SEO sync no longer keeps stale Site SEO through old-value fallback. Existing Desktop media replacement and active Profile/Variant replacement remain authoritative and are regression-protected.

Real #620 evidence: membership is disabled and persisted Slider fields are empty, but its existing content pack already contains complete Slider SEO, so backfill can reuse saved AI output with zero new AI request. W4.1 real state is also verified before A2X: #628 = 12×12×12 / 18×18×18 with 16 PLA each; #625 = 5×5×5 preserved + owner-estimated 4×4×4, both with 16 PLA. Post-W4.1 snapshot: `D:\projects\3dprinthub-backups\phase50-a2w-w41-post-accept-20260921-152825\catalog-after-w41.sqlite3`, SHA256 `7743e63fba5d83b2991502ce320d21f7037a444dba0ef9bc2b240ad88c3ca8da`.

A2X Local verification: focused readiness/AI/Qt media 33/33 PASS; Server same-identity Slider/SEO/import 9/9 PASS; broad Catalog current run has one failure out of 116, exactly the previously proven baseline Manufacturer-vs-Brand assertion tracked by ERR-49-203. `git diff --check`, touched Python compile, Django check, migration drift check and `RUN_QT.ps1 -VerifyOnly` PASS. No migration or Production mutation has occurred.

Exact next: documentation checkpoint -> commit/push exact A2X SHA -> GitHub readback -> exact-SHA Qt -> fresh Catalog backup -> no-AI Slider backfill preserving membership -> real UI verification -> guarded Host deploy from GitHub through reverse tunnel -> one controlled same-identity re-publish proving full current Windows snapshot replacement.

## 2026-09-21 - Phase50.A.2W W4.1 Source dimensions REAL_DATA_PATCHED / A2X supersedes next acceptance

W4.1 extends the Source Profile contract for operator-ready dimensions and Filament defaults. MakerWorld Description evidence is parsed in source order and bound to Source Profiles only when the number of unambiguous size records equals the number of Source Profiles. Full L×W×H values are normalized to cm. Owner rule now requires a single factual dimension such as Height=12cm to populate all three operational Profile axes as 12×12×12; provenance still records Height as factual and Length/Width as `owner_equal_dimension_rule`. Manual Profiles still require complete positive dimensions.

Real Hydra evidence is proven from the latest local MakerWorld capture for Catalog Product #628 / external 3179519. The compact meta text contains `Small Version: Height = 120 mm` and `Large Version: Height = 180 mm2. Support...`; the parser treats the trailing `2.` as the next numbered section. Source facts remain Height=12/18cm, while operational Profiles become Small=12×12×12 and Large=18×18×18 under the owner equal-dimension rule.

Filament defaults are also owner-authoritative: if Source declares material family PLA, every active Local PLA offer is added/checked in the created Source Profile; exact-family matching excludes PLA-CF/HT-PLA-GF/PETG. Real Catalog currently has 16 active PLA offers. Read-only simulation proves #628 both Source Profiles receive all 16 PLA offers; #625 Profile 1 already has 16 real PLA offers and remains unchanged, while Profile 2 replaces its two brandless Source placeholders with the same 16 real PLA offers. Product #625 Profile 1 keeps operator-owned 5×5×5cm; Profile 2 receives only the explicit 4×4×4cm owner-estimated fallback. Pricing, weight/time and Site identity/revision are preserved.

Rollback ref before the owner correction is `backup/pre-phase50-a2w-w41-owner-dimension-filament-correction-20260921` -> `436d34f2e62532ea5890b44400d1d236ed3b53a1`. Owner-correction verification: focused Source Profile/Dimension 15/15 PASS; mature Commerce/Profile + W3/W4/W4.1 corrected gate 59/59 PASS; retained media/site 83/83 PASS; py_compile, git diff-check and RUN_QT VerifyOnly PASS. Real read-only simulation gives #628 12³/18³ + 16 PLA each and #625 5³/16 PLA preserved + 4³/16 PLA on Profile 2.

W4.1 correction is pushed at exact GitHub SHA `7f2280eafe7a3293008a6dc7a4559b0ef92f114c` and the controlled Local Catalog repairs are persisted: #628 = 12×12×12 / 18×18×18 with 16 PLA per Profile; #625 keeps 5×5×5 on Profile 1 and has owner-estimated 4×4×4 on Profile 2, both with 16 PLA. Post-repair integrity snapshot is `phase50-a2w-w41-post-accept-20260921-152825\catalog-after-w41.sqlite3`, SHA256 `7743e63fba5d83b2991502ce320d21f7037a444dba0ef9bc2b240ad88c3ca8da`. Site Product identity/revisions were not changed by W4.1. A2X now supersedes the next runtime/deploy acceptance; failed batch `26aa571c-...` remains separate and must not be silently retried.

## 2026-09-21 - Phase50.A.2W W4 WINDOWS_RUNTIME_ACCEPTED / real #625 Preview PASS

W4 implements a strictly read-only Source material/color -> real Local Filament/pricing review path. It does not write `sales_profile_ledger_json`, `source_print_profiles_json`, Stage locks, Site identity or publish state. Stage 2 adds `W4 تطبیق Filament محلی`; the review dialog shows each factual Source filament slot separately against active Local material-family-compatible offers, including Brand, Local color, explicit Local HEX/Palette evidence, stock, roll sale price, Source-slot material cost and—only for single-slot Profiles—the mature formula total. Localized color names are never converted to HEX for W4 authority.

Real Local inventory inspection found 16 active PLA offers across Bambulab, E-Sun/ESUN and PolyGround. Current active PLA operating rates are 3,500,000 purchase / 4,500,000 sale per 1kg roll, 150,000 print/hour and 50,000 supervision/hour; E-Sun/ESUN retain their existing preheat facts. Most Bambulab rows have no explicit HEX. The only current explicit PLA HEX in the inspected inventory is E-Sun white `#FAF8F6`; therefore neither Source `#FECC66` nor `#804003` has an exact Local HEX match and W4 must not auto-pick a named color.

The Multicolor Source Profile is deliberately not flattened into ordinary alternative `material_options`: its two simultaneous factual consumptions remain separate slots (11g `#804003` + 39g `#FECC66`). W4 computes per-slot material cost for review but does not fabricate a combined Ledger price before concrete Local offers are chosen. Single Color uses the existing `formula_price_breakdown()` authority for full-price preview.

Rollback ref before source work: `backup/pre-phase50-a2w-w4-material-mapping-20260921` -> `eda42e84b0bf39052fb76aa3c74e35b7dd0a85e5`. Verification: W4 focused 5/5 PASS; current mature Filament/Profile/Commerce + W3/W4 corrected gate 49/49 PASS; retained A2V/W1/W2 media/site gate 83/83 PASS; py_compile, diff-check and RUN_QT VerifyOnly PASS. Two tests in the broader 51-test commerce probe fail identically on the clean `eda42e84...` baseline and are not W4 regressions; ERR-49-203 records them. ERR-49-202 records the changed-condition read-only inventory probe correction, and ERR-49-204 records the pre-mutation PowerShell rollback-ref parser typo.

Real #625 W4 Preview is accepted. W4 source is pushed at exact GitHub SHA `27bb00a1d8a8dd34e033af9cfaba27f37384a0a0`; Local and remote matched exactly and Qt was launched from that SHA. Fresh pre-preview rollback `D:\projects\3dprinthub-backups\phase50-a2w-w4-pre-preview-20260921-114901\catalog-before-w4-preview.sqlite3` has integrity `ok` and SHA256 `a38f78d346e2b367eaaeed540837ff5e076dea890c26808ddc0437106f239f7e`. Real button-level W4 Preview PASS: 2 Profiles / 3 Source slots / 48 PLA candidates / exact HEX=0. Source facts, Sales Ledger, Stage locks, Site Product #39 revision 11 and product-history count were unchanged before/after Preview.

Current real #625 state is `workflow_status=batched`, `needs_update=1`, `upload_ready=1`, with Commerce currently locked. History proves this comes from an operator publish attempt before W4 acceptance: batch `26aa571c-1a0c-4ad4-9431-65e74c27d94f` recorded `qt_bulk_site_publish ok=0`; Site remained Product #39 revision 11. A later operator Commerce edit/finalize re-locked Commerce. W4 did not change or retry that publish state; ERR-49-206 tracks it separately.

Exact next: W4.1 owner follow-up on Source Profile dimensions. Preserve exact Source dimensions when available; for #625, when dimensions are absent, use the explicit owner-approved estimated fallback `4.0cm × 4.0cm × 4.0cm` instead of zero and mark it as estimated. Test this fallback before any publish recovery. Do not return to W1/W2/W3 and do not auto-retry the failed batch.

## 2026-09-21 - Phase50.A.2W W3 WINDOWS_RUNTIME_ACCEPTED / real #625 import PASS

W3 factual Source Print Profile import is implemented and pushed on the active A2W branch at exact source `36dbf3cf283fc1e5697091549e930416c671cbe7`; Local and GitHub remote matched exactly and the Qt runtime was launched from that SHA. MakerWorld `__NEXT_DATA__` is parsed deterministically into the existing `source_print_profiles_json` authority; no AI/inference is used. Source facts and operator Sales Ledger remain separate: factual refresh never overwrites manual Profiles, while explicit import uses deterministic `source-mw-<instance>` keys and preserves non-source ledger rows.

Real #625 evidence is exact: `Single Color Print Profile` instance 3609481/profile 943581967 = 4814s, 13g, PLA #FECC66, A1/N2S, 0.4mm nozzle, 0.16mm layer; `Multicolor Print Profile` instance 3609488/profile 943610448 = 15748s, 50g, PLA 11g #804003 + 39g #FECC66, same nozzle/layer. Exact seconds/fractional minutes remain in source facts; the current integer-minute Sales Ledger converts to nearest minute 80/262, not ceil.

Verification: dedicated W3 5/5 PASS; corrected retained A2V/W1/W2/bidirectional gate 83/83 PASS; py_compile, `git diff --check` and `RUN_QT.ps1 -VerifyOnly` PASS. An initial incorrectly reconstructed 83-test command included two known-obsolete modules and reproduced the already-documented 1 legacy image-limit assertion + 3 Windows temp-SQLite teardown errors; the command was not repeated unchanged and ERR-49-201 records the manifest correction.

Fresh pre-real-W3 rollback: `D:\projects\3dprinthub-backups\phase50-a2w-w3-pre-real-625-20260921-102142\catalog-before-w3-real-625.sqlite3`, source/backup integrity `ok`, SHA256 `ba7d70b04cf5b084bd7922bd0f93f321a55cc4c7c241795f32c6840235764401`. At backup time #625 remains Site Product #39 revision 11, uploaded, upload_ready=0, source profiles empty and Sales Ledger has one manual Standard Profile. `needs_update=1` predates W3: history event 2425 (`source_product_recovery`, 2026-09-21T06:18:25Z) changed source images 2→5 and needs_update 0→1 after revision-11 publish. W3 must not clear that state.

Real exact-SHA Stage-2 button smoke fetched a fresh MakerWorld capture and persisted exactly two factual Source Profiles while the operator-import dialog was answered No; Site #39/revision 11, workflow/dirty/ready state and the existing Sales Ledger stayed unchanged, with no FTP/Bridge/publish event. A second integrity-checked pre-import backup `D:\projects\3dprinthub-backups\phase50-a2w-w3-pre-ledger-import-20260921-103253\catalog-before-w3-ledger-import.sqlite3` (SHA256 `bbf3614285b79da354505775a3750db57257a8ab790171a953168895443f055e`) was then taken. Commerce was unlocked only through StageCore and the explicit W3 import added exactly `source-mw-3609481` and `source-mw-3609488`, preserving manual `ledger-dcff93fba1e9`; no invented Brand/Manufacturer/local pricing was introduced. Site identity/revision remained unchanged and only `qt_stage_unlocked` + `qt_profile_ledger_edit` history events were created. Commerce remains ready but intentionally unlocked for W4 mapping. Post-import DB integrity is `ok`; accepted snapshot `D:\projects\3dprinthub-backups\phase50-a2w-w3-post-ledger-import-20260921-103507\catalog-after-w3-ledger-import.sqlite3`, SHA256 `fbeeca44c9ebb46be75c1dc6a70ab2eaa6a34aa719483808578c56fb3be05a9d`. Read-only Qt Stage-2 UI verification shows exactly three Profiles and Source Profile count two. No Host/Production source, migration, Site revision or publish changed. Exact next: close W3 docs on GitHub, then W4 factual Source material/color → real Local Filament offer mapping/pricing for operator review; do not publish #625 as part of W4 bootstrap.

## 2026-09-21 - Phase50.A.2W W1/W2 LOCAL_TESTED / real #625 Truth Sync PASS

A2W is active on `wip/phase50-a2w-product-media-sync-20260921`, based on clean A2V closure `346baa135c62ff58a6596a80433678ebd622206b`; rollback ref is `backup/pre-phase50-a2w-product-media-sync-20260921`. W1 adds Product-specific `رفرش رسانه و وضعیت` truth sync/recovery in Stage 3. W2 flushes pending `ارسال سایت` UI state before Ready/Publish and only auto-finalizes newly selected, previously-unfinalized media while keeping stale SEO/final-file gates fail-closed.

Local verification: focused W1/W2 + publish/image regression 49/49 PASS; broader A2V Image/SEO/Packaging/Republish + bidirectional Site sync + A2W 83/83 PASS; py_compile, `git diff --check` and `RUN_QT.ps1 -VerifyOnly` PASS. Production release code was inspected read-only and already enforces exact `media.gallery_count`, filename and SHA parity with `REPUBLISH_PARITY_MISMATCH` rollback, so W1/W2 require no Host source delta, migration or restart.

Fresh Catalog rollback: `D:\projects\3dprinthub-backups\phase50-a2w-pre-truth-sync-20260921-093455\catalog-before-a2w-truth-sync.sqlite3`, integrity `ok`, SHA256 `0470eb8d64573b7e252756d2bb9f449ddd2b08b6f50e1eb39e39343b704320cb`.

Real #625 Truth Sync completed without FTP/import/publish. Product remains Site #39 revision 11, uploaded/clean, `needs_update=0`, `upload_ready=0`. Truth result: canonical DB media=2, locally displayable files=3, persisted `ارسال سایت`=1, live Site media=1, source-link count=0, recovered=0, mismatch=0. Selection/Primary remained exactly `local://04.webp`; Site identity/revision and dirty state were unchanged. This proves the current 3-card Windows view is not three Site-authoritative images.

Two temporary probe invocations failed before DB mutation (`PYTHONPATH` missing, then `Database` received `str` instead of `Path`); both causes were corrected before the successful run and are recorded in ERR-49-200. Production remains unchanged at `03042d0430ee6e688c992c875f12edc969df103d`. Exact GitHub source is now `ab1e9d1051aba6ff12a8b3c8b1f9bf04fb22be17`; Local and `git ls-remote` matched exactly, worktree was clean, and the Qt runtime was launched through repository `RUN_QT.ps1` from that SHA. Process tree is the verified venv launcher -> Python 3.12 child -> the A2W `qt_launch.py`. A real Qt button-level smoke clicked `رفرش رسانه و وضعیت` on #625 and returned the same truth snapshot (DB=2, Local=3, selected=1, Site=1, mismatch=0) with no Product identity/revision/dirty-state change. W1/W2 are therefore `GITHUB_UPDATED / WINDOWS_RUNTIME_ACCEPTED`; Production remains unchanged. Exact next: W3 factual source Profile evidence inspection and implementation of `دریافت پروفایل از محصول`.

## 2026-09-21 - Phase50.A.2V PRODUCTION_VERIFIED / closed

A2V is closed on Windows branch `wip/phase50-a2v-image-authority-20260920`. The tested source implementation remains exact commit `4e69ed6a5c0996c7249830fbe029cd01460ad5b1`; the prior documentation checkpoint was `318fb410c063df660767a9e8ff66d0847a765f03`. The operator runtime is A2U-derived v8.9.11 and the stable Image/SEO/Packaging/Republish gate is 72/72 PASS, with diff-check, py_compile and RUN_QT VerifyOnly PASS.

The revision-10 defect is fixed permanently: temporary bulk `ویرایش` selection is separate from persisted `ارسال سایت`; Site-selected media must belong to canonical `images_json`; and refetch preserves persisted Site-selected local files even when their legacy filenames are numbered.

Real #625 acceptance completed against the same Site Product #39. The persisted Site choice at publish time was exactly `local://04.webp`, Primary is the same URL, metadata is ready, and the final SEO file is `mini-articulated-skeletal-spinosaurus-3d-print-01.webp`. The controlled batch `desktop_catalog_v85_20260921_081158` / UUID `cb51fb28-acd2-45a7-8a86-40ea5268614c` advanced Product #39 exactly once from revision 10 to revision 11 with `republish_parity.ok=true`, one authoritative ProductImage and three authoritative active Variants.

Byte parity is exact end to end. Local final SEO, Batch image, Production stored main/ProductImage and a fresh public HTTPS download are all 36,162 bytes with SHA256 `cf6f0422f0cde915e9203ddbca6564df694fb4b6a97320e1af0e7f4117c68fff`. Public Product HTTP is 200 and the page contains the exact revision-11 image filename. Production Variant parity is exactly three active CC rows with 110 g material weight, 60 g final weight, 180 min print time and prices 1,095,000 / 1,215,000 / 1,215,000 Toman.

Production source itself remains clean and unchanged at `03042d0430ee6e688c992c875f12edc969df103d` on `release/phase50-a2j-hero-20260915`; A2V required no Host source deploy, migration, collectstatic or restart.

Backup note: the planned fresh pre-republish snapshot was not captured before revision 11 completed, so it is not falsely marked as done and revision 12 was not created merely to recreate ordering. The verified revision-10 A2V rollback remains `D:\projects\3dprinthub-backups\phase50-a2v-image-authority-20260921-005619\catalog-before-a2v.sqlite3` (integrity PASS, SHA256 `20bd5c1d6b776c14e90d9aa91a9866b909121614d9e042faeb252cbac75c0e9e`). A fresh post-revision-11 snapshot is `D:\projects\3dprinthub-backups\phase50-a2v-post-rev11-20260921-081557\catalog-after-rev11.sqlite3` (integrity PASS, SHA256 `1f6ecd4c9250ed9b46e612489294fea0f1fe7c6b57a6a02aa1493b738bc72869`).

No further #625 publish is required for A2V. Next project work should continue from this verified Windows lineage and the existing Phase50 roadmap, without selecting any unrecorded `phase49_3c_*` image by inference.

## 2026-09-20 - Phase50.A.2U ACCEPTED / latest Windows v8.9.11 restored

The actual latest Windows lineage is now the operator source: `D:\projects\3DPrintHub-a2u-latest-windows` on `wip/phase50-a2u-latest-windows-a2t-20260920`. Source implementation is pushed at `d77dfd95f5d3a9a707f9ad03f2aacff9e69ac2e2`.

The prior Desktop handoff incorrectly pointed to A2T, which carried newer Social code but did not descend from the latest Windows image/gallery/SEO/screenshot lineage. This was a lineage-selection/shortcut error; the newer Windows history was already in GitHub. A2U starts from exact latest Windows `f1b58645...`, preserving the complete image workspace ancestry including `20f483af`, `91d4c188`, `00f16237`, `a52cd52a`, `aaa5cb9f` and `ea1a4a79`, then ports only Social v5/Story-link handoff behavior.

Regression: Windows Image/SEO/Republish 74/74 PASS; Social/Buffer/Story 35/35 PASS; compile PASS; Qt verify PASS; repository RUN_QT VerifyOnly PASS. App reports v8.9.11 / build 2026.09.20.1. The Desktop .lnk/.cmd now target A2U and real launch smoke shows `3DPrintHub Catalog Center v8.9.11 - Qt 6`. Shortcut rollback: `D:\projects\3dprinthub-backups\phase50-a2u-shortcut-20260920-210723`.

#625 recovery: the old app actually imported Site Product #39 revision 9 successfully, then falsely failed only on its stale public-media verifier. Fresh atomic Catalog backup `D:\projects\3dprinthub-backups\phase50-a2u-pre-reconcile-625-20260920-210357` integrity PASS / SHA256 `9304640D9A6D53BB5210FCFD4D1438A102E74D38F80B0C507D861A39D112B32E`. Latest verifier proved Product HTTP 200 plus 2/2 canonical media HTTP 200, so #625 was reconciled locally without re-import to uploaded / needs_update=0 / upload_ready=0 / Site #39 revision 9. Production read-only confirms revision 9, exactly three active Variants, two ProductImages, 60 g final weight, 110 g material weight, 180 min and prices 1,095,000 / 1,215,000 / 1,215,000 Toman.

No Production source deploy, migration or restart occurred for A2U. A2U is now the current Windows operator lineage; future Windows work must start from A2U or a verified descendant.

## 2026-09-20 - A2Q Social SEO v4 sanitizer checkpoint

Status: `WIP GITHUB COMMITTED / CANONICAL WINDOWS FULL REGRESSION REQUIRED`.

- Windows/Social WIP branch is now `wip/phase50-a2l-owner-qa-20260917` at exact GitHub commit `1c77f671c8df1fcce716662339f3057378a96433`.
- Rollback branch `backup/pre-phase50-a2q-social-v4-sanitizer-20260920` preserves pre-fix `21a1ae27c8f57ce7dbd6cd78bf6a3d548e9bd158`.
- Fixed the social sanitizer punctuation defect that could emit a literal `\\1` after false-free cleanup.
- Extended false-free filtering to Persian `رایگان/مجانی` and bounded English free-download/free-print/free-shipping claims; hashtag candidates carrying those claims are dropped as whole units.
- Added focused regression coverage across Caption, hashtags, per-image ALT and Story copy, including a guard that preserves unrelated words such as `Freestyle`.
- GitHub source read-back and rollback comparison PASS: one commit ahead, zero behind, exactly four files changed.
- The canonical Windows full Social/Buffer/Story + Qt VerifyOnly gate has **not** been rerun on this new SHA because the paired Remote Desktop transport is temporarily unavailable due tool quota. Therefore this SHA is not promoted to release and no external Instagram post is sent.
- #625 revision 8 remains historical real Feed/Story evidence and must not be reposted.
- Site release remains separate at `65d42e40979830b306e92457093aefe068086f66`; Production is not mutated by this WIP change.

Exact next: canonical Windows pull of `1c77f671...` -> focused + broad Social/Buffer/Story tests -> Qt VerifyOnly -> only then selective release promotion. In parallel A2R payment/finance/admin audit may proceed read-only.

## 2026-09-20 - Phase50.A.2Q Hero shadow cache closure + Instagram SEO v4 IN_PROGRESS
Owner screenshot shows the historical Slicebox dark shadow strip under the Home Hero. Current Production is clean at 36a69e76f9cd553273862ee400f9391573f3dd01 and fresh Home HTML already serves 50.9.0 without id=shadow; A2Q therefore adds a cache-safe hard suppression/runtime removal contract and cache bump 50.10.0 rather than reintroducing or redesigning the slider.

Instagram itself is now proven real from A2P: #625 revision 8 Feed and companion Story were sent successfully through Buffer using the dedicated GitHub-hosted provider media boundary. A2Q does not repost #625. The next social policy version prioritizes Product focus keywords before generic tags, keeps max 8 hashtags, adds explicit 3DPrintHub.ir order copy, keeps nationwide shipping + UTM Product URL + per-image ALT, and strips false «رایگان» claims from caption/hashtags/ALT before provider submission.

Local A2Q social verification is now complete: 32/32 maintained Instagram/Buffer/Story/media-host tests PASS, changed files compile, diff-check PASS and Qt VerifyOnly PASS. Exact next: commit/push Windows and Site lineages -> guarded Hero deploy from GitHub through reverse tunnel -> Production browser acceptance -> exact-SHA Qt relaunch -> begin A2R payment/finance/admin closure.

## 2026-09-19 - Phase50.A.2P Buffer media-host automation + REAL Instagram acceptance
Production Site is clean at 36a69e76f9cd553273862ee400f9391573f3dd01. Fresh public Chromium on Hero 50.9.0 proves the owner-reported old Slicebox frame/shadow is no longer present: no #shadow DOM, slider/wrapper/root border=0 and box-shadow=none. Product #625 has also completed the authoritative same-identity path as Site Product #39 revision 8. Production read-back is exactly 3 active CC-P39 Variants, 0 active legacy Variants, 2 ProductImages; current prices are 1,095,000 / 1,215,000 Toman with 60 g final weight and 180 min print time.

Instagram acceptance is now real, not simulated. A fresh pre-social Catalog backup pre-instagram-a2o-625-20260919-214544 was integrity-ok. Buffer connection, policy instagram-product-v3-20260919, two non-empty ALT texts, eight bounded hashtags, UTM Product URL, nationwide-Iran shipping copy and Highlight target اسباب بازی were verified before publication. The first retry using site-hosted compatibility PNGs still failed because Buffer could not read the origin URLs even though owner-side HEAD/GET were HTTP 200 image/png. The exact same PNG bytes mirrored through the dedicated public GitHub social-assets branch were accepted: Feed 6aaed28f6e039ccbc8221fa8 is sent at https://www.instagram.com/p/DdepEh3if0N/ and Story 6aaed29a7fcdd8931977c3f1 is sent at https://www.instagram.com/stories/3dprinthub_ir/3989806967019651799. No duplicate #625 post was created.

A2P now automates that verified compatibility boundary. Windows can use buffer_media_host=github_raw, mirrors only generated social derivatives to the dedicated D:\projects\3DPrintHub-social-assets / social-assets-buffer worktree, verifies the pushed GitHub head and public image MIME, and preserves canonical Site media separately in audit receipts. Current social-assets head is 6561dc3e2709ccc2d2651d576d1e744b35058891. Feed submitted receipt was reconciled read-only to instagram_published without repost. Fresh pre-A2P data backup pre-a2p-social-host-runtime-20260919-220004 is integrity-ok. Current runtime setting is github_raw and Story style setting is 3dprinthub_instagram_gold_navy_v2_iransans.

Local candidate adds media-host automation, provider-host receipt evidence, submitted->sent reconciliation and Settings UI media-host selection. Focused and broader social regression 31/31 PASS, Python compile PASS, `git diff --check` PASS and Qt VerifyOnly PASS. Exact next: commit/push A2P -> exact-SHA Qt relaunch -> close A2O/A2P docs -> continue Phase50 payment/finance/admin and bounded Product workflow. Do not republish #625 revision 8 to Instagram.

## 2026-09-19 - Phase50.A.2O failed-republish identity preservation LOCAL_TESTED
The first changed-condition #625 retry after the A2M/A2N Production release exposed a Windows-side resilience defect, not another Host data bug. The receiver correctly rolled back on the then-stale parity rule, but Windows overwrote the last verified Site linkage/ACK with the failed ACK and reset `server_product_id/server_product_revision` to zero. That made the next retry lose the existing Product identity even though Site Product #39 still existed.

A2O changes failed-republish handling: every failed attempt is still recorded as a receipt and `product_sync_error/server_status=failed`, but the last verified Site asset/Product/slider ids, revisions and successful `server_ack_json` remain intact until a later confirmed publish replaces them. Local regression proves a failed retry preserves Product #39 revision 7 linkage. Catalog Site-publish suite 19/19 PASS; Instagram feed/Story/social suite 27/27 PASS; diff-check PASS. Production is already clean at `36a69e76...`, where Hero 50.9 shadow-frame removal and corrected profile-driven parity are live.

The owner screenshot issue is therefore fixed in current Production code: public HTML has cache key 50.9.0 and no `#shadow` element; real Chromium reports desktop Slicebox ready=1, 2 slides, 5 cuboids/30 sides on Next, and mobile ready=1 with nonzero 366x274.5 slider and zero document overflow. Exact next: commit/push A2O -> fresh Catalog backup -> restore only the verified #625 Site linkage from pre-failure evidence -> one official same-identity re-publish -> strict Product #39 read-back -> real Buffer compatibility PNG Feed+Story attempt and receipt verification.

Instagram remains not yet externally complete until Buffer returns successful Feed/Story receipts.

## 2026-09-19 - Phase50.A.2M authoritative re-publish replacement LOCAL_TESTED
Owner regression is reproduced on real Product #625 / Site Product #39. The 2026-09-19 revision-7 ACK is `status=updated`, `republish_parity.ok=true`, ProductImage count=2 and three current Windows sales profiles. Production read-only evidence nevertheless shows **5 active Variants**: three correct `CC-P39-...` rows plus stale `EP49-3F...` rows 5940/5945 carrying 1 g / 60 min / 104,500 Toman. That additive legacy state is why the public Product can still expose old weight/material/price after a successful Windows re-send.

A2M changes the contract from additive merge to authoritative active-state replacement whenever Windows supplies `sales_profiles_json`: current CC rows remain active, every older manual/MW-FIX/EP49/EP49-3F/removed CC row is retained for history but deactivated. Host sync now also fails closed if any stale non-CC Variant remains active or active CC count differs from the Windows profile count. Existing Product identity/slug/order history are preserved. ProductImage synchronization already rebuilds the current selected-image set exactly; Windows now also has an explicit `+ عکس از فایل` path that copies an owner file into the Product, selects it, marks an uploaded Product dirty and leaves the existing SEO-finalization gate authoritative before publish.

Local gates: compile PASS; Django check PASS with known CKEditor warning; no migration drift; Server profile/import/admin-sync 15/15 PASS; Windows image workspace 25/25 PASS. Production remains at `9ce01fdc4c61ce58730e77bbb4d70b78de07e585` until GitHub-first selective release/deploy. Current #625 Local source-of-truth contains exactly 3 sales profiles and 2 selected images; therefore the extra image the owner expected never entered the authoritative selected-image set and must not be fabricated. Exact next: commit/push A2M -> selective release -> fresh Production rollback -> reverse-tunnel deploy -> one #625 republish -> require exactly three active CC Variants + current public price/weight/materials/media -> Browser QA.

Instagram is **not complete**: Buffer still rejects the real #625 Feed before post creation with `Image could not be read from its URL`; no successful Feed/Story receipt exists yet.

## 2026-09-19 - ERR-49-178 Buffer feed media compatibility LOCAL_TESTED
After ERR-49-177, the first real Buffer Feed submission for #625 reached Buffer with the two verified canonical Product images but Buffer rejected both with `Invalid post: Image could not be read from its URL.` before creating a Feed receipt. Local/browser checks still showed both source URLs HTTP 200, `image/webp`, stable HTTPS and exact expected bytes. No Feed/Story duplicate was created.

The Buffer-specific compatibility boundary now derives PNG feed assets from the verified canonical Product images, preserves original aspect where already Instagram-safe, letterboxes extreme ratios into the accepted range without cropping, caps width at 1440, uploads under stable `/media/instagram/feed/products/<product>/<revision>/NN.png`, verifies each public image, and submits those provider media URLs while retaining the canonical Site URLs separately as `source_media_urls` in the receipt. Site Product media/SEO/public filenames are untouched.

Local compile + feed-asset/Buffer/Story/Instagram regression 21/21 PASS. Rollback: `backup/pre-err49-178-buffer-feed-media-20260919 @ b3321041...`. Exact next: commit/push -> fresh Catalog backup -> prepare real #625 compatibility PNGs -> one real Buffer Feed+Story attempt -> verify provider receipts/external links + Highlight target queue -> final runtime relaunch/docs. Production card-transfer settings remain pending because the authorized remote execution safety boundary currently refuses that financial-settings mutation.

## 2026-09-19 - #625 reconciled + Story renderer Windows race fixed LOCAL_TESTED
The already-successful #625 Site ACK was reconciled locally without FTP/Bridge re-import after re-running strict public verification against Production. Product #625 is now `uploaded, upload_ready=0, needs_update=0, server_product_id=39, server_product_revision=6, server_status=updated`, with `public_http_ok=true` and no sync error. A dedicated receipt/history event records `no_reimport=true`. Fresh pre-Instagram Catalog backup `pre-instagram-625-20260919-164751` is integrity-ok.

Browser QA on the deployed Site passed Home/Store/Product desktop+mobile headless captures and DOM checks: no `رایگان/free 3d print` text, no server-error markers, Store/Product use canonical `/media/p/`, Product contains both SEO image filenames, Toman price text and ordering UI. Desktop launcher was created at `C:\Users\Emad-PC\Desktop\3DPrintHub Catalog Center.lnk` plus the adjacent `.cmd`, both targeting repository-owned `catalog_center\RUN_QT.ps1`.

First real Instagram attempt stopped before Feed submission because the standard Story render remained a small near-white 18,240-byte screenshot. ERR-49-177 isolated a Windows Chrome launcher race: direct Python `subprocess.run(chrome.exe ...)` can return before the actual headless child writes the screenshot, and the temporary render workspace can disappear first. The correction keeps an isolated Chrome profile under the Product Story LocalAppData workspace, invokes Chrome through PowerShell `Start-Process -Wait`, removes stale PNG first and polls for the real output before cleanup. Real #625 Story render now PASS: 1080x1920, 1,178,712 bytes, 6,984 sampled colors, mean RGB about 65.8/60.1/56.1. Social/Story/publish regression 53/53 PASS, Qt VerifyOnly PASS, compile/diff-check PASS. Rollback: `backup/pre-err49-177-story-headless-profile-20260919 @ 7513d8fa...`.

Exact next: commit/push ERR-49-177 -> verify exact remote SHA -> fresh Catalog backup -> real Buffer Feed+Story once -> verify Feed/Story receipts and `highlight_target=اسباب بازی, highlight_status=operator_required` -> conservative Host backup cleanup -> final docs/runtime relaunch. Production card-transfer code is live but payment-settings activation remains pending because the remote execution safety layer blocks that financial-settings mutation.

## 2026-09-19 - Canonical public-media verifier LOCAL_TESTED
Production receiver work is separately deployed at `9ce01fdc4c61ce58730e77bbb4d70b78de07e585`: Product #39 canonical `/media/p/625/<sha12>/<seo>.webp` URLs now return HTTP 200/image while imported working-media remains 404. Real #625 receiver import had already passed `republish_parity.ok=true`, Product identity #39 and revision 6; the Local Catalog remained dirty only because the Windows verifier still recognized legacy `/media/store/products/` URLs.

Canonical Windows checker now accepts exactly two public Product namespaces: legacy `/media/store/products/` and content-addressed `/media/p/`. It intentionally does not accept `/media/store/imported-models/`. Dedicated public-verification regression 3/3 PASS; maintained publish/social scope 40/40 PASS. Rollback ref: `backup/pre-err49-176-public-media-verifier-20260919 @ 6b2536f...`.

Exact next: commit/push this Windows correction -> fresh Catalog backup -> reconcile the already-successful #625 ACK/public HTTP locally without another Site import -> require `uploaded, needs_update=0, upload_ready=0` -> then Feed+Story acceptance. Manual card-transfer Source is already implemented; Production payment settings activation is tracked on the Server release after verified DB rollback evidence.

## 2026-09-19 - Phase50.A.2L pricing + Instagram Story/Highlight LOCAL_TESTED
Status: `LOCAL_TESTED / TWO COMMITS + SERVER DEPLOY + DATA REPAIR NEXT`.

Real #625 resend is now fail-closed on the remaining pricing mismatch instead of returning a false success. ERR-49-174 has two parts: active PLA Filament rows drifted away from the owner-approved 2026-09-14 defaults, and the Site dynamic price engine did not consume the complete Desktop sales-profile formula. The integrity-checked post-default preview `phase50-filament-defaults-20260914-175618/catalog-preview.sqlite3` proves PLA defaults: purchase 3.5m, sale 4.5m, print 150k/hour, supervision 50k/hour while preserving per-offer preheat facts.

Windows publish now refreshes Product Filament/Profile snapshots from current inventory before Ready/Publish; Server Desktop-managed `CC-P...` Variants use the same material + print + supervision + preheat + assembly formula. Server targeted 5/5 PASS with no migration drift; Windows pricing/social/story 19/19 PASS plus Manufacturer-vs-Brand regression PASS. Companion Story remains default, final style ID is `3dprinthub_instagram_gold_navy_v2_iransans`, and #625 `toys-games` maps to Highlight target `اسباب بازی`. Official Buffer API has no Add-to-Highlight mutation, so the target is queued with `operator_required`.

Rollback refs: Windows `backup/pre-phase50-a2l-pricing-social-20260919 @ 585e20357a4d9268fb5dee71318f314504d096a0`; Server `backup/pre-phase50-a2l-pricing-engine-20260919 @ ba05c7fc479ae94d4a85676442008e018dbbcc67`. Dedicated reverse tunnel check at this checkpoint returned `127.0.0.1:22024=False`; no alternate tunnel/direct Host path was used. Exact next: commit/push both lineages -> restore/verify dedicated tunnel -> deploy Server -> fresh backups -> repair owner-approved active PLA -> refresh/republish #625 -> Product #39 read-back/browser -> real Feed+Story receipts/Highlight queue.

## 2026-09-18 — Screenshot SEO + edited-source media refresh PRODUCTION_PRODUCT_VERIFIED
- Runtime/source fix committed and pushed at exact GitHub SHA `89931e8958b3a738fbfb4b8d65c099124aa24de0`; Local and live GitHub matched exactly before runtime launch.
- Fresh pre-republish Catalog backup: `D:\projects\3dprinthub-backups\pre-republish-89931e8-20260918-191741\catalog.sqlite3`; source and backup integrity both `ok`, 635 Products, SHA256 `3d9a25bf7a565caf490d50bbb6830eac229ab6993d5e80f1d9d82646e176cfd8`.
- Canonical Qt was relaunched from `89931e8...`; visible child window `3DPrintHub Catalog Center v8.9.10 - Qt 6` is responsive.
- Real Product #625 remained linked to existing Site Product #39 / server asset 143. FTP PASS, Bridge v1.3.0 PASS, publish-readiness `ready=true`, all required migrations/schema/storage prerequisites healthy, and Product preflight had zero blockers.
- Guarded re-publish/update completed as batch `desktop_catalog_v85_20260918_192011`; server ACK is `status=updated`, Product revision advanced 4 -> 5, Store visibility/public HTTP checks PASS, and local state is now `uploaded, needs_update=0, upload_ready=0`.
- Public byte verification is exact: local final image 01 SHA256 `cb230bc60455edd7e49b2152c06ff2633b4180d56fae21e68b50b60d799b60cb` equals both public main/gallery copies; local final image 02 SHA256 `6dad7f5e7312ea6691ac8c9ed82094f7363520e0db2852b9546f501c0a4ab3fd` equals the public gallery copy. Public Product page HTTP 200 contains both SEO filenames and current Product title.
- The outer `publish_many` result reports `skipped/no new change` after guarded remote revision reconciliation, but the authoritative persisted ACK/batch/revision/public-byte evidence proves the same-identity update completed successfully.
- Screenshot SEO/source-refresh regression is therefore closed for the real Product path.
- Production application-source deploy for the pending Admin/Hero/template code remains a separate tunnel-only operation; no alternate cPanel/browser Host path is permitted.

## 2026-09-18 — Screenshot SEO + edited-source media refresh LOCAL_ACCEPTED
- Owner regression reproduced on real Product #625 / Site Product #39: per-card SEO opened empty fields for a manual Screenshot without metadata, while republish could reuse an old finalized WebP after the local source image bytes changed.
- Per-card SEO now seeds empty single-image fields from the Product semantic SEO identity (Alt/Title/Caption/Keywords) without auto-selecting the image for Site publication.
- Unselected editable images (including manual Screenshots) now keep operator SEO metadata persistently while remaining `metadata_ready=False` and without a final publishable WebP until the operator explicitly checks `در سایت`.
- The combined `اصلاح اسم و سئو` action uses the explicit operation subset when present; otherwise it covers every editable Product image, including unselected Screenshots, while preserving Site membership/Primary/Slider.
- Publish readiness now detects selected source-image byte drift against the stored `original_sha256`. Only already-finalized selected media with real byte drift is auto-refinalized before Ready; genuinely incomplete/unfinalized media remains fail-closed.
- Mature public identity/update behavior is preserved: the same Site Product is updated, not duplicated. Product #625 remains linked to Site Product #39.
- Two broad-suite failures were verified on a clean exact baseline worktree and were stale contracts, not regressions: legacy 4-column expectation while owner-approved runtime is 3-column, and Persian fallback Profile identity while current contract requires ASCII `Standard`. Tests were aligned to the accepted current contracts. A separate PETG-HF expectation was also corrected to preserve the established conservative exact-family recommendation contract.
- Verification: focused Image+Publish 41/41 PASS; stale-contract suites 77/77 PASS; final broad Windows regression 145/145 PASS; `RUN_QT.ps1 -VerifyOnly` PASS; Python compile PASS; Django check PASS with known CKEditor warning; no migration drift; `git diff --check` PASS.
- Rollback branch already exists: `backup/pre-card-seo-source-refresh-20260918` -> pre-fix base `ea1a4a7935792f6d42e84231bb6a6250fda38fa9`.
- Production source is still unchanged at this checkpoint. Next: commit/push exact candidate -> fresh Catalog backup -> exact-SHA Qt relaunch -> controlled Product #625 re-publish -> public Product/media verification. Host source deployment remains restricted to the dedicated reverse tunnel only.

## 2026-09-18 — Image name+SEO unification + in-place republish dirty-state LOCAL_ACCEPTED
- Verified clean Local/GitHub base `e8a980ddf1d94faef6549d053dc1f05518fb9ae1` on `wip/phase50-a2l-owner-qa-20260917`; rollback branch `backup/pre-image-name-seo-republish-update-20260918` preserves that exact base.
- Stage 3 now exposes one automatic `اصلاح اسم و سئو` action instead of separate automatic SEO and rename controls. Existing manual `SEO انتخابی` remains. The combined action uses temporary operation-selected images when present; with no operation subset it repairs all editable Site-selected images. It applies Product semantic Alt/Title/Caption/Keywords and then the mature source-title ASCII numbered WebP renumber path. Primary, Slider, Site membership, Screenshot and recovery behavior are unchanged.
- Root cause of owner-reported stale re-upload was not the Site importer: Site already updates an existing linked Product in place. The missing boundary was Windows direct mutations that bypass `StageCore.update`: image metadata/SEO, renumber, remove, Screenshot and Product operator edits could change an uploaded Product without setting `needs_update=1`.
- Added one shared dirty marker for explicit operator mutations. A Product with existing Site identity and `workflow_status=uploaded` now stays the same published identity but becomes `needs_update=1, upload_ready=0`; the existing Stage-7 send action then requeues it through guarded revision check -> Batch -> FTP -> Bridge -> same Site Product update.
- Server re-import acceptance was strengthened: same Asset/Product is imported, then Title/Description/SEO and finalized image are changed and the same Batch identity re-imported. Product PK and Asset PK stay identical, Product count remains one, content/meta/image are refreshed in place, and idempotent replay remains supported.
- Verification so far: Image workspace 22/22 PASS; Windows republish/site suites 59/59 PASS; Site real re-import 3/3 PASS; Profile/identity/admin-sync Django gate 23/23 PASS; changed-file compile and diff-check PASS.
- Real Catalog read-only: 20 server-linked rows. Product #628 is already `uploaded + needs_update=1` and remains linked to Site Product #38; Product #152 remains `batched + upload_ready=1` after the prior Host Request Timeout and is still the next Site-first publish target. #309/#301 remain uploaded and are not to be social-posted again.
- Production remains unchanged while dedicated reverse tunnel `127.0.0.1:22024` is down.
- Exact next: final Qt/Django gates -> commit/push exact candidate -> fresh Catalog backup + exact-SHA Qt relaunch -> reverse-tunnel recovery on verified local Router only -> Host identity/backup/migration gates -> deploy from GitHub -> verify Admin 504/Product page/Hero -> publish #152 to Site -> Instagram #152.

## 2026-09-18 — Site-first hotfix: Product Admin 504 + Profile identity + real Instagram ACK LOCAL_ACCEPTED
- Verified branch `wip/phase50-a2l-owner-qa-20260917` from clean Local/GitHub base `eec03119fe3d7c6b39cac9a1e9a5cfcb54dc309f`; rollback ref `backup/pre-site-admin-profile-instagram-20260918` preserves that exact base.
- Owner storefront request is already satisfied by current source: `templates/store/product_detail.html` contains no `filament_visual_options` / per-roll Filament card block. Production still renders that obsolete duplicate block because Production is on an older source; stale regression was aligned to require the block absent.
- Production Product edit 504 was isolated to the full `ProductVariantInline` inside Product change pages. Real Local benchmark at 37 Variants: 781 queries / 1.399s / 892118 bytes with the inline versus 60 queries / 0.075s / 277103 bytes without it. Final Product Admin composition removes only the Variant inline; ProductImage/Compatibility/FAQ/Profile and the dedicated ProductVariant admin remain.
- Product #625 real Catalog has one root profile with corrupted `???????` name/size and 64 material options. Runtime normalization now requires ASCII Profile identity: corrupt/Persian identity falls back to `Standard` or real `L x W x H cm`; Product #625 read-only acceptance now reports Name=`Standard`, Size=`Standard`, one production row and all 64 material options preserved.
- Real Site ACK for Products #309/#301 stores `images` as a numeric count and verified URLs under `public_http_checks.images`. Instagram parser now accepts that real shape, keeps Product main image first and filters fallback media to the current Product slug; real acceptance gives #309 five owned media and #301 three owned media with no cross-Product image leakage.
- Verification: Site/Admin focused 17/17 PASS; Catalog/Instagram/Qt 82/82 PASS; Hero/Slicebox 27/27 PASS; changed Python compile, both relevant Node syntax checks, Django check, no migration drift and diff-check PASS.
- Production is still unchanged. Dedicated reverse tunnel remains down; Windows OpenSSH/firewall/Host route are healthy, but the old public endpoint `37.255.236.184:443` is stale and current Ethernet WAN `37.255.247.160:443` has no working 443->22 DNAT. Current WinBox session is the separate MobinHoust router and must not be used for this NAT.
- Exact next: commit/push this candidate -> exact Local/GitHub verification -> Qt VerifyOnly + fresh Catalog backup/relaunch -> restore only the verified local-router 443 transport without guessing credentials -> authenticated Host identity/backups/gates -> GitHub deploy -> Production Product edit/Home/Product-page browser verification.

## 2026-09-18 — Image filename/four-row-scroll runtime pushed and verified
- Exact runtime commit `aaa5cb9f6d743becf3f1588501733ae835bd7451` is pushed to `wip/phase50-a2l-owner-qa-20260917`.
- Main development worktree acquired unrelated concurrent Instagram/Buffer changes after this commit, so exact runtime was launched from a separate clean Git worktree: `D:\projects\3dprinthub-runtime-aaa5cb9` at detached HEAD `aaa5cb9...`. No reset/stash/delete was applied to concurrent work.
- Fresh pre-launch Catalog backup: `D:\projects\3dprinthub-backups\pre-image-seo-scroll-aaa5cb9-20260918-125436\catalog.sqlite3`; source/backup integrity `ok`, 635 Products.
- Exact-SHA Qt launch is live from the clean worktree. Launcher PID 42752 delegates to Python child PID 58680; visible window `3DPrintHub Catalog Center v8.9.10 - Qt 6` is responsive.
- Post-launch read-only verification: Catalog integrity `ok`, 635 Products. Product #301 planned filename and stored finalized filename both equal `christmas-tree-minimalistic-japandi-decor-3d-print-01.webp`; Alt remains product-specific Persian, SEO title remains Persian, caption exists, keyword count remains 12.
- Runtime Source after `aaa5cb9...` is unchanged. Production is unchanged; Host work remains fail-closed while dedicated reverse tunnel is down.
- Exact next: owner visual smoke of Product #301/target Product for English filenames + four-row scroll reserve.

## 2026-09-18 — Restore English image filename authority + four-row scroll canvas LOCAL_TESTED
- Owner reported mixed/incorrect image naming and inaccessible lower-row controls. Real Product #301 (`Christmas Tree Minimalistic Japandi Decor`) was inspected read-only before code changes.
- Product #301 proves mature image SEO metadata is still healthy: existing final filename `christmas-tree-minimalistic-japandi-decor-3d-print-01.webp`, Persian product-specific Alt, Persian SEO title, non-empty caption, 12 keywords, and `metadata_ready=True`.
- Root cause of naming inconsistency was limited to `planned_seo_filename()`: commit `9b006bb...` changed fallback filename priority from source English title to `seo_title_fa`. Finalized older images still had English filenames while unfinalized/extra local images could receive a different Persian-derived planned name.
- Fix restores the mature filename contract only: `source_title` English -> ASCII slug -> numbered WebP. Alt/Title/Caption/Keywords generation, operator overrides, AI refresh, image finalization, Screenshot and selection logic are untouched.
- Gallery scroll contract is also narrowed: large Stage-3 gallery always reserves at least four 206px rows, even with zero/few images. Real isolated probe: host minimum 842px, viewport 652px, scrollbar max 190 with zero images.
- Read-only Product #301 acceptance after fix: planned filename `christmas-tree-minimalistic-japandi-decor-3d-print-01.webp`; existing metadata filename matches; Alt remains `دکور درخت کریسمس مینیمال جاپاندی از جلو`; caption remains present; keyword count remains 12.
- Verification: focused 4/4 PASS; broader Qt/ImageSEO/Site-publish regression 97/97 PASS; compile, diff-check and `RUN_QT.ps1 -VerifyOnly` PASS; no migration delta.
- Rollback ref: `backup/pre-image-seo-source-title-four-row-scroll-20260918` -> `55f6d2068b25f4bb8f56572f2f991323c3dc4aeb`.
- Production unchanged. Host work remains blocked/fail-closed while the dedicated reverse tunnel is down.

## 2026-09-18 — Stage-3 3×3 runtime pushed and relaunched
- Exact runtime commit `a52cd52a18a119f9aa2940ebc00f588828d1a558` is pushed to `wip/phase50-a2l-owner-qa-20260917`; Local/GitHub SHA matched before launch.
- Fresh pre-launch Catalog backup: `D:\projects\3dprinthub-backups\pre-stage3-3x3-a52cd52-20260918-123308\catalog.sqlite3`; source/backup integrity `ok`, both 635 Products.
- Canonical Qt was relaunched from the exact pushed source. Venv launcher PID 29816 delegates to Python child PID 53788; visible window `3DPrintHub Catalog Center v8.9.10 - Qt 6` is responsive.
- Post-launch read-only Catalog: integrity `ok`, 635 Products. Product #628 currently stores 2 selected images / 2 source images; the 3×3 layout capacity is verified separately with isolated 9-card acceptance.
- Dedicated reverse tunnel was rechecked only through Windows loopback `127.0.0.1:22024`: `TCP22024=False`. Per owner rule no cPanel/browser/alternate Host path is permitted, therefore Production site deployment remains BLOCKED/fail-closed.
- Exact next: owner visual smoke of the new compact Stage-3 layout. Site Slicebox deployment resumes only when the dedicated reverse tunnel and authenticated Host gates are healthy.

## 2026-09-18 — Owner correction: Stage-3 3×3 compact review LOCAL_TESTED
- Owner clarified the target: do NOT enlarge each image card. Stage 3 must show three images per row and, by default, three complete rows (up to nine cards) including SEO filename and per-image controls.
- Presentation-only correction: Product Wizard Stage 3 now uses 3 columns; review cards are 300–520px wide and fixed 206px high; image preview is 260x90 minimum / 94px max-height; filename stays visible; source filename + factual size are one compact metadata row; Previous/Next/SEO/Delete are one 22px action row. Existing selection, primary, slider, reorder, SEO, delete, screenshot and wheel-scroll callbacks are unchanged.
- Gallery minimum is 670px. Isolated 1400x670 9-card acceptance: viewport 1386x652, rows top at 4/216/428, third-row card bottom 634, third-row filename bottom 576, scrollbar maximum 0. Therefore all 3×3 cards, filenames and action rows are fully visible at once. With 12 cards the fourth row creates real scroll and wheel-over-preview regression still passes.
- Real Product-layout probe stays screen-bounded; compact card child controls end at y=202 inside the 206px card.
- Verification: focused 3×3/Wheel gate 4/4 PASS; maintained Qt/Gallery/Wizard/Screenshot gate 68/68 PASS; changed-file compile/diff-check PASS.
- Rollback ref: `backup/pre-stage3-three-column-20260918` -> `825f13ed35d6c83752e5e8d236e222f768924eec`.
- Host rule reconfirmed by owner: Production/Host access is ONLY through the dedicated 3DPrintHub reverse tunnel. Do not use Windows browser/cPanel/Terminal as an alternate Host channel. Current `127.0.0.1:22024` probe is down, therefore site deploy remains fail-closed until that same reverse tunnel becomes healthy.
- Exact next: commit/push this Windows design correction -> fresh Catalog backup -> exact-SHA Qt relaunch -> owner visual smoke. Site deployment resumes only after reverse-tunnel health/Host gates pass.

## 2026-09-18 — Owner design-only Windows compaction + real Example-4 Slicebox LOCAL_ACCEPTED
- Requested Delta is presentation-only for Catalog Center: Stage-3 image operations/modes/callbacks remain unchanged. The eight image toolbar actions are now one compact row (7pt / 26px controls), the bottom Save/Finalize/Unlock/Previous/Next controls are one row, and the vertical room released by those rows raises the image gallery minimum to 650px.
- Real-copy Product #628 RTL geometry acceptance at 1800x1000: page 1800x1009 (inside the real 1920x1032 Windows working area), Stage 3 1416x792, gallery 1398x652, visible image viewport 1384x634; all eight Stage-3 toolbar buttons share one Y coordinate and all five bottom controls share the exact same vertical center.
- Windows behavior gate remains green: maintained Qt/Gallery/Wizard/Screenshot suite 67/67 PASS; `RUN_QT.ps1 -VerifyOnly`, compile and scoped diff-check PASS. No image/SEO/Screenshot/selection business logic was changed by this design slice.
- Homepage top Hero keeps the vendored official Tympanus/Codrops Slicebox v1.1.0 and existing `HomepageHeroSlide` data, but the wrapper now uses the official Example-4 transition contract (`orientation:'r'`, random cuboids, `disperseFactor:30`), removes the non-reference Play/Pause controls, keeps screenshot-requested arrows/dots/shadow, and uses the site's own `#f6f9fc` background.
- Browser acceptance found and fixed the actual historical Hero startup defect: Slicebox v1.1.0 waits for every slide image before `onReady`, while the previous template marked hidden slides lazy. Hidden lazy images never loaded, leaving `pluginReady=False`, slider height 0 and controls hidden. All four Hero images are now `loading="eager"`; only the first retains `fetchpriority="high"`.
- Fresh Local Browser evidence after a Local Django restart: 4/4 images HTTP 200 and complete, `pluginReady=True`, slider height 416px, wrapper 840px, two visible 42x42 arrows, four dots, site background rgb(246,249,252), no nav-options, no browser/console errors. Clicking Next creates 5 cuboids / 30 3D sides and moves current slide 0 -> 1. Evidence: `D:\projects\3dprinthub-backups\visual-index4-ready-20260918-120143`.
- Site gates: selected Hero suites 27/27 PASS; Node syntax, Django check (existing CKEditor warning only), `makemigrations --check --dry-run` no changes. No DB/schema/Product/Hero row mutation is required by this presentation fix.
- Current branch base advanced concurrently through unrelated Instagram Story commits to `eb22a69f687be0b3f64fcfcc785b50da3d3776dc`; verified overlap with this change is NONE. Rollback ref for the exact post-Story base: `backup/pre-ui-layout-index4-post-story-20260918`.
- Production has not yet been changed. Exact next: commit/push this accepted delta -> fresh Catalog backup + exact-SHA Qt relaunch -> read-only verify the dedicated 3DPrintHub Host tunnel/current Production lineage -> deploy from GitHub only if Host gates pass.

## 2026-09-18 — Stage-3 scroll hotfix pushed / Qt relaunched
- Runtime hotfix `00f16237cf27eea2cdf7bef97fa7cc140014c947` is pushed to `wip/phase50-a2l-owner-qa-20260917`; Local/GitHub SHA matched before launch.
- Fresh pre-launch Catalog backup: `D:\projects\3dprinthub-backups\pre-stage3-scroll-00f1623-20260918-112042\catalog.sqlite3`; source/backup integrity `ok`, 635 Products.
- Exact runtime source under `catalog_center/qt6` and `catalog_center/app` had no working-tree diff before launch. Unrelated Story/Instagram work remained outside the runtime source and was preserved.
- Canonical `RUN_QT.ps1` launched the hotfix; Python child PID 36916 has visible responsive window `3DPrintHub Catalog Center v8.9.10 - Qt 6`.
- Owner acceptance now pending on the same Product: wheel directly over the large image must scroll to SEO filename / select / edit / delete controls, and the application must remain within the Windows desktop rather than clipping the lower gallery.
- Production/Host/schema remain unchanged.

## 2026-09-18 — Stage-3 visible-height / wheel-scroll repair LOCAL_TESTED
- Owner screenshot proved the lower image controls were still unreachable in the real Windows layout even though the internal gallery had a valid scroll range.
- Root cause was two-part: the Stage-3 gallery minimum height of 720px forced the Product Wizard beyond the 1920x1080 desktop working area, while `ClickableImageLabel` consumed wheel events over the large image preview so the gallery did not move when the pointer was on the image itself.
- Fix is presentation/input-only: keep large cards/previews and all image/SEO/Screenshot/selection logic unchanged; set the gallery minimum to 560px so the full Wizard stays inside the desktop, keep the gallery as the vertical-scroll owner, and explicitly forward wheel deltas from the image preview to the gallery scrollbar.
- Real-copy Product #628 geometry probe after the fix: rendered page 981px high in the bounded probe, gallery 562px high, viewport 544px, content host 2424px, scrollbar range 0..1880. Wheel-over-preview probe changed scrollbar 0 -> 270; viewport wheel also 0 -> 270.
- RTL probe on the real Product #628 copy rendered at 1000px with Stage-3 minimum hint 726px and visible internal scrolling. No DB/schema/media mutation is required by this repair.
- Verification: dedicated regression PASS; maintained Qt/Gallery/Wizard/Screenshot suite 67/67 PASS; changed-file `py_compile`, scoped `git diff --check`, and `RUN_QT.ps1 -VerifyOnly` PASS.
- Repository note: unrelated in-progress Instagram Story font/render changes were already present in the worktree and were explicitly preserved/excluded from this fix.
- Exact next: commit/push only this Stage-3 repair and docs -> verify remote SHA -> fresh Catalog backup -> relaunch Qt -> owner visual smoke on the same Product.

## 2026-09-18 — Stage-3 image workspace runtime pushed and relaunched
- Approved runtime commit: `91d4c188aa57c125e46d45f39a70d913085dcf6c` on `wip/phase50-a2l-owner-qa-20260917`; Local and live GitHub SHA match exactly.
- Fresh canonical Catalog online backup before launch: `D:\projects\3dprinthub-backups\pre-image-workspace-91d4c18-20260918-105013\catalog.sqlite3`; source and backup `integrity_check=ok`, Product count 635.
- `RUN_QT.ps1 -VerifyOnly` passed from the exact pushed source, then the canonical launcher opened the Qt runtime. Venv launcher PID 2608 delegates to Python 3.12 child PID 27156; the child has visible window title `3DPrintHub Catalog Center v8.9.10 - Qt 6`.
- Post-launch read-only Catalog verification: `integrity_check=ok`, Product count 635, Product #628 still has 11 persisted Site-selected images. Worktree remained clean at runtime SHA.
- Production, Host, schema and migrations remain unchanged by this Windows slice.
- Exact next: owner visual smoke Product #628 for larger review area, subset multi-select Edit/Delete, SEO filename labels and scroll behavior. Production promotion is not part of this Windows-only acceptance.

## 2026-09-18 — Stage-3 image workspace multi-select / SEO / Instagram cover LOCAL_TESTED
- Branch/base verified before work: `wip/phase50-a2l-owner-qa-20260917 @ e076efa350e727a45dcdbc5fcc500f925090b59c`; Local and live GitHub branch SHA matched. Rollback branch `backup/pre-image-workspace-multiselect-seo-instagram-primary-20260918` preserves that exact base.
- Owner-requested Stage-3 delta is implemented without changing Screenshot capture/naming: larger 2-column image cards/previews and a taller scroll viewport; compact top controls; an independent temporary `انتخاب` checkbox for bulk edit/delete separate from persistent `در سایت`; click-on-preview toggles the temporary bulk selection.
- Real numbered Product files under the trusted Product `images` directory are now addressable as safe `local://<filename>` media instead of remaining `display_only`. Legacy `local-display://...` identities normalize only when the real file exists. Removing such a numbered local file moves it to `removed_images` for recovery instead of deleting it permanently.
- Image cards show the deterministic SEO filename as the primary label and keep the source filename as secondary factual evidence. Current filename authority remains the 2026-09-15 Product-SEO-first planner (`seo_title_fa` when present); the old source-title-only regression assertion was corrected rather than reverting runtime naming policy.
- Operator SEO edit / `بازسازی نام‌های SEO` now preserve the exact operator image selection and do not apply publish-time perceptual dedup. The normal/default finalizer remains deduplicating for publication. An isolated first acceptance caught the old operator path reducing 11 selected images to 6; after the boundary fix, the isolated Product #628 acceptance keeps 11 -> 11, leaves zero `local-display://` selected identities, writes 11 unique SEO metadata rows, preserves Primary, and reports 15 visible / 15 editable / 15 SEO-named real files. Isolated acceptance root: `D:\projects\3dprinthub-backups\accept-gallery-seo-20260918-103512`; pre/post SQLite integrity `ok`.
- Instagram/Buffer canonical media now deterministically places verified `public_main_image_url` first so the Product main image is the feed cover/first carousel asset while retaining the remaining verified media.
- Verification: targeted new regression 9/9 PASS; maintained Qt/gallery/social gate 80/80 PASS; expanded image-pipeline + Site publish gate 107/107 PASS; changed-file `py_compile`, `git diff --check`, and `RUN_QT.ps1 -VerifyOnly` PASS. No migration-file delta. Canonical Catalog and Production were not mutated by acceptance.
- Exact next: document/commit/push the Local-tested candidate -> verify remote exact SHA -> fresh canonical Catalog backup -> relaunch Qt from that pushed runtime SHA -> Product #628 visual/runtime smoke. Production deploy remains separate and blocked by the documented Host-tunnel gate.

## 2026-09-18 — Screenshot button visibility regression fixed locally
- Owner report reproduced on the real Catalog without changing the canonical DB: Product #628 had multiple fresh `source-page-screenshot-*` files and matching `local://` entries, proving the button/capture path was executing.
- Root cause was the newer A2L numbered-image display resolver from `4375c007...`: when numbered Product files existed it returned early and intentionally hid non-numbered auxiliary files, so a newly captured Screenshot disappeared from the Qt Product gallery and could also be mistaken for a numbered source slot.
- Fix is deliberately narrow in `qt6/kernel.py`: explicitly persisted `local://source-page-screenshot...` files are appended to the numbered review result, and Screenshot pseudo-URLs are forbidden from stealing numbered source-slot identity. Capture implementation, Screenshot filename generation/crop, SEO generation, selection persistence, Product Wizard button wiring and gallery sizing are unchanged.
- New regression failed before the patch and passes after it. Full maintained Qt/Gallery/Wizard/Screenshot gate is 61/61 PASS; `py_compile`, `git diff --check` and `RUN_QT.ps1 -VerifyOnly` PASS.
- Copy-of-real-Catalog acceptance used `D:\\projects\\3dprinthub-backups\\pre-screenshot-resolver-20260918-095910\\catalog.sqlite3`; source/backup integrity are `ok`, and Product #628 resolves the persisted manual Screenshot items without mutating the canonical Catalog.
- Runtime fix is committed and pushed at `bab82e89e9e27722b8b1000a959b1161ee84e038`; Local/GitHub SHA matched exactly before launch. The canonical `RUN_QT.ps1` launcher then started the Qt app from that exact source; the live child process is responsive with window title `3DPrintHub Catalog Center v8.9.10 - Qt 6`.
- Production/schema remain unchanged. Exact next: owner smoke the Screenshot button on the same Product; a newly captured Screenshot must appear in the same Stage-3 gallery after refresh.

## 2026-09-18 — Owner correction: preserve image workflow, enlarge review only
- Owner rejected the `d564386` Stage-3 workflow/layout changes. The corrective Local candidate restores the prior image controls, prior screenshot action path, prior recover-limit behavior, prior slider panel and prior window-geometry behavior.
- Requested delta is now intentionally narrow: enlarge only the Product image review cards/preview area. Image naming, screenshot capture/naming, image ordering, selection, delete, SEO persistence, slider and recovery behavior are restored byte-for-byte to the pre-`d564386` implementation where applicable.
- The attempted gallery-label change was rejected and removed; filename display is again the mature pre-change behavior. Screenshot implementation and image SEO pipeline also have zero source diff from the verified pre-`d564386` baseline `bf87c11`.
- Corrective focused Qt/Gallery/Wizard/Screenshot regression: 60/60 PASS. Corrective runtime commit `20f483af983cad550b1e2473751798daf0e8d39b` is pushed to GitHub and Local/remote SHA match.
- Canonical Catalog online backup before relaunch: `D:\\projects\\3dprinthub-backups\\pre-owner-gallery-e50ee9b-20260918-094051\\catalog.sqlite3`; source and backup `integrity_check=ok`.
- Qt was relaunched after the correction; one visible `3DPrintHub Catalog Center v8.9.10 - Qt 6` window is running from the canonical repository path. Production and database schema remain unchanged.

## 2026-09-18 — A2L exact runtime relaunched / real Filament identity debt isolated
- Exact A2L candidate `4375c007874faa87c874f3806705532128814176` is on GitHub and the Windows Qt Catalog Center was closed/relaunched from that exact SHA after a fresh online Catalog backup (`pre-a2l-exact-launch-20260918-083025`, integrity `ok`, 635 Products).
- Real Product #628 runtime probe resolves 10 local Product images. Stage 3 is 2 large columns, 560 px minimum height, content minimum 2508 px and vertical scroll range 1964 px, confirming the owner screenshot with only two visible cards came from the stale pre-A2L process.
- Real Catalog audit found the remaining `Sync همه با سایت` blocker is data identity, not the sync transport: 71 Filament rows exist; 63 legacy rows have blank Brand, so fail-soft sync can send 8 valid rows and must reject 63 incomplete identities rather than invent Brand facts.
- Follow-up LOCAL_TESTED patch adds `تکمیل Brand انتخابی`: selected/filterable legacy rows can be assigned only an explicitly registered Brand, then the same guarded Site sync runs. Unknown/unregistered Brand values fail closed. The operator can filter by Material/Search, select visible rows, apply the factual Brand, then Sync all again.
- Copy-of-real-Catalog acceptance repaired legacy row #14 to registered `Bambulab` without touching canonical data; the old blank-Brand row was deactivated, the resulting ABS/Bambulab/color identity passed Site payload validation and SQLite integrity stayed `ok`.
- Follow-up focused Windows suite is 28/28 PASS and the full maintained A2L scoped Catalog gate is now 57/57 PASS; compile and `git diff --check` PASS.
- Canonical Catalog was not mutated by the repair acceptance; Production remains unchanged and dedicated `127.0.0.1:22024` tunnel is still down. Next: commit/push this follow-up -> relaunch exact SHA -> operator brand-repair UX smoke -> recover Host tunnel -> release/deploy/Production verification.

## 2026-09-18 — Phase50.A.2L owner QA local acceptance complete / exact candidate next
- Current development branch: `wip/phase50-a2l-owner-qa-20260917`; this slice extends the accepted A2K baseline without changing Production.
- Product Wizard Stage 3 now uses 2 large columns, always-on vertical scrolling and row-height expansion; canonical Product #628 resolves 10 real local Product images, so the owner screenshot showing only two cards is confirmed as an older running Qt process.
- Source-image recovery preserves operator commerce/SEO decisions, filters MakerWorld avatars/store assets, maps distinct page images and displays real downloaded files.
- Filament `Sync همه با سایت` is fail-soft per row; incomplete legacy identities are reported while valid rows continue. Single-row edit remains, plus selected/all-active bulk edit for print-hour, supervision and all preheat fields.
- Smart Profile material selection exposes an explicit auto-select action; decorative/display products default conservatively to PLA/PETG and do not auto-select PA12-CF/PLA-CF without matching evidence.
- AI production Preview reads source/link + saved Product images and can propose approximate dimensions/weight/print time; nothing is persisted before operator confirmation and existing operator values are preserved.
- Real Buffer/Instagram secure gate PASS from Windows Credential Store; configured Instagram channel is connected/unlocked. Feed keeps all verified media (5 means 5), tracked Product URL, SEO copy/alt/hashtags and companion Story link. Highlight assignment remains operator-required on the current Buffer contract.
- Manual bank transfer uses existing Store models: Pasargad / owner-approved card details are seeded only by explicit `--apply`; receipt upload enters admin review and operator notification fans out to Telegram/WhatsApp/Email where configured.
- Local acceptance: Catalog scoped 55/55 PASS; Store/checkout 11/11 PASS; manual-payment 4/4 PASS; `git diff --check`, changed-file compile, Django check/no model drift and `RUN_QT.ps1 -VerifyOnly` PASS. ERR-49-156/157 record repaired stale Store fixtures and the unsuitable historical broad-discovery harness.
- Production remains blocked by ERR-49-154 until dedicated `127.0.0.1:22024` reverse tunnel, Host identity, backup/rollback and readiness gates are restored. No card seed or A2L deploy has been applied to Production.
- Exact next: commit/push exact A2L candidate -> verify remote SHA -> close the old Qt window -> relaunch exact pushed SHA -> Product #628 visual/runtime check -> recover tunnel -> Production backup/readiness -> deploy from GitHub -> apply manual-payment seed -> public checkout/receipt/admin-notification verification.

## 2026-09-17 — Phase50.A.2K local/release accepted; Production transport blocked
- Owner-requested full Hero replacement is implemented with the exact vendored Tympanus/Codrops Slicebox v1.1.0 engine; legacy A2I/A2J public CSS/JS and Hero-only runners are removed.
- Redundant Product filament gallery is removed; the four-step order wizard now shows material description/applications/examples.
- Windows Catalog Product/Profile filament UX now supports Select All/Clear All and central Filament edit with registered Brand/Material/Color libraries plus material applications/examples.
- Canonical feature/GitHub: `71d34daae1571b4f46f05def91c86b1dcde173a6`; Production-based release/GitHub: `release/phase50-a2k-tympanus-20260917 @ 84d1a87c4ea632823743b9cc1c5fe3ba81b08843`.
- Acceptance: release Django changed suites `50/50 PASS`; Windows Catalog suite `18/18 PASS`; no model changes; canonical migration plan empty; Qt launcher PASS and modern Qt window reopened.
- Production remains unchanged at documented A2J release because dedicated `127.0.0.1:22024` tunnel is down. Windows sshd is healthy; last successful PrintHubTunnel auth is 2026-09-15. No deploy or destructive Hero DB reset has been executed.
- Exact next: restore dedicated Host watchdog/tunnel -> Host read-only gate -> fresh DB/Hero rollback backup -> deploy exact `84d1a87...` from GitHub -> confirmed A2K Hero reset -> collectstatic/restart -> public verification.
## 2026-09-17 - CANONICAL QT WINDOWS RUNTIME + PRODUCTION STORE RESET / A2J RE-ACCEPTED

Status: `WINDOWS_QT_LAUNCHED / STORE_EMPTY / A2J_PUBLIC_VERIFIED / PRODUCT_RESEND_READY`.

- Canonical Local branch and GitHub are exact at `b116a27add3ea4f08b68fb3c9c5e037068f576d3`; primary worktree is clean. `RUN_QT.ps1` was launched from the canonical path and the only remaining visible Qt window is `3DPrintHub Catalog Center v8.9.10 - Qt 6` from `D:\projects\3DPrintHub\catalog_center\qt_launch.py`.
- Unrelated unfinished Instagram/Buffer work was preserved, not discarded, on GitHub branch `wip/phase50-social-buffer-20260917` at `ea8a156` and removed from the primary runtime lineage.
- Canonical Catalog SQLite `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3` is integrity `ok`, contains 635 Products and 66 available Filament offers. Fresh online rollback backup: `D:\projects\3dprinthub-backups\pre-qt-runtime-b116-20260917-online\catalog.sqlite3`, integrity `ok`, 635 Products.
- Exact Product continuity gate PASS 5/5: same-identity dirty republish, explicit requeue of an uploaded Product, changed Profile/Filament/print-time propagation, Site-404 recreation after Store reset, and existing-Site update-in-place. Product #628 remains locally preserved and resend-ready; it was not republished so the owner receives an empty Store.
- Dedicated reverse tunnel authenticated health PASS on Windows `127.0.0.1:22024` -> Host bridge base `/home/sfkilvrs/3dprinthub`, bridge version `1.0.0`. Production repo is clean on `release/phase50-a2j-hero-20260915 @ 12e319ace1eb55c114d7117e1b5a2fa170b410ab`.
- Fresh verified Store-reset rollback: `/home/sfkilvrs/3dprinthub-deploy-backups/20260917-090106-final-store-product-reset`; manifest `639f67e78e053932d86a8f317cd73ea69e0d8aad0305f62301ae7c79cdd92940`, 37 Product-owned media files hash-verified, MySQL gzip valid at 3,108,367 bytes.
- Canonical `phase50-store-reset-v2` POST returned HTTP 200: before `8 Product / 2011 Variant / 29 Image / 0 Order / 0 InventoryMovement`; after `0 / 0 / 0 / 0 / 0`. 37 Product media files were deleted; 97 source assets, 17 Portfolio rows, 13 Materials, 5 Qualities and 64 Colors were preserved.
- `phase50_a2j_seed_hero` dry-run and `--apply` PASS. Exactly four active safe source-backed slides remain: assets `119,120,135,136` at sort `10,20,30,40`. Public Home, A2J CSS and A2J JS are HTTP 200; raw UTF-8 decode PASS; rendered HTML has four `data-p50j-slide` and four dots with `01/04` counter and Slicebox perspective/random/sequential contract.
- Production `migrate --plan` reports no planned migration operations. Known CKEditor / in-memory realtime / MySQL conditional-constraint warnings remain non-blocking debt.

- Final post-cleanup receiver gate: `publish_ready=true`, `publish_blockers=[]`, MySQL, 13 active Materials and 5 active PrintQualities. Store-reset preflight now reports only `store_already_empty`; Product/Variant/Image/Order/InventoryMovement/linked-asset counts remain zero.
Exact next: owner can finalize Products in the canonical Qt app and use explicit send/re-send. For every chosen Product, require current license/SEO/Profile facts, then Batch -> FTP -> Bridge strict ACK -> public media -> orderable Variant/Cart verification. Do not repopulate the Store with test Products.

## 2026-09-17 - QT WINDOWS OPERATOR RUNTIME / LEGACY-LAUNCH ROOT CAUSE RESOLVED

- Owner report that the old Windows UI opened instead of the newer Product/Filament application is reproduced and explained by repository truth: `catalog_center\RUN_DEBUG.ps1` and `RUN.ps1` intentionally still target legacy `launch.py`; the newer application is `qt_launch.py`.
- No Product/Filament/republish work was lost. Current source already contains explicit re-send, Site-404 recreation, update-in-place identity, and updated Profile/Filament/print-time Batch propagation.
- Legacy launchers remain preserved for rollback/side-by-side acceptance. New repository-owned operator launcher `catalog_center\RUN_QT.ps1` verifies `qt_launch.py` against canonical `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3` and launches Qt detached with `pythonw.exe` when available.
- The pre-existing unfinished Local fix that prevents implicit persistence when a hydrated legacy workspace is merely closed is preserved; its regression passes and no dirty work was reset or discarded.
- Pre-launch Catalog backup: `D:\projects\3dprinthub-backups\pre-qt-new-launch-20260917-001903\catalog.sqlite3`; source/backup SHA256 both `BE0C5F3140CA615739F9EE25B6E18D85E49A919809AF2BF9E02E257A2E97C775`.
- Corrected focused acceptance PASS: 40/40 Windows tests covering explicit Qt launcher separation, close-without-save, Qt foundation, Product resend/update/recreate, Profile/Filament/print-time republish and image workspace; `RUN_QT.ps1 -VerifyOnly`, Qt structural verify, touched `py_compile`, and `git diff --check` also PASS. One broader harness produced 92 runtime PASS plus two loader-only errors from retired test-module names; recorded as `ERR-49-151` and not repeated unchanged.
- GitHub rollback branch before this operator-launch slice: `backup/pre-windows-qt-operator-launch-20260917` -> `6a3a51aacdccff69a4999c4a470cb10807ceb648`.
- Production was not changed by this Windows slice. Next: commit/push exact Windows candidate, relaunch through `RUN_QT.ps1` from pushed SHA, then use the documented reverse tunnel for fresh read-only Store/reset/receiver verification before any Production write.

## 2026-09-16 - WINDOWS IMAGE REORDER LOCAL_TESTED / GITHUB PROMOTION NEXT

## 2026-09-17 - Exact-SHA Windows publisher runtime verification

- GitHub exact source is `67445d60f07625faeb0d384ebeec809cc54bf8f3` on `agent/phase49-3i18-operator-bulk-ai-rebuild`.
- `catalog_center/launch.py --verify-only` passed from that source: Catalog Center `8.9.10`, build `2026.09.02.1`, source root `D:\projects\3DPrintHub\catalog_center`.
- Before foreground launch, canonical persistent Catalog SQLite `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3` was backed up to `D:\projects\3dprinthub-backups\final-windows-publisher-20260917-000808\catalog-exact.sqlite3`; source and exact-copy SHA256 both `45B14FA296491769ABC7AEBCE4754697D727323342538CB3A3A071BE3167FFFF`; source/backup integrity checks PASS; 635 Products / 14 Ready.
- Canonical `catalog_center\RUN_DEBUG.ps1` launched the UI. Window title: `3DPrintHub Catalog Center v8.9.10 ? BUILD 2026.09.02.1`; process is responsive.
- Runtime transcript `D:\projects\3dprinthub-catalog-manager\logs\powershell-debug-20260917-000856.log` proves `DATABASE_PATH=D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`, `SQLITE_INTEGRITY=ok`, FTP login OK and Bridge health HTTP 200 (`version=1.3.0`, `schema_version=8.5`).
- Post-launch read-only DB verification: integrity `ok`, 635 Products, 14 Ready, 17 Uploaded, 2 Needs Update.
- Production A2J runtime files in the accepted release are behavior-equivalent to this SHA; `store/epic49_runtime_contract.py` differs only in explanatory docstring text, not executable fallback logic. No redundant Production source deploy was performed.
- Production Store destructive reset is still NOT executed: the automation safety layer blocked the canonical write call after the verified rollback backup was prepared. Live Store must still be treated as the preflight state until a new read-only verification proves otherwise.


## 2026-09-17 - Windows republish + empty-store Hero reconciliation (LOCAL_ACCEPTED / RESET_BACKUP_READY)

- Local branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`; baseline before this change: `3c6d295912bb5f305dccd978f07038d3e38d98bd`.
- Windows explicit re-publish continuity from `9b006bb` was re-verified: already-published products can be explicitly requeued; existing Site products update in place; Site 404 recreates from preserved Catalog asset identity; Profile/Filament/print-time data is carried in the new batch.
- Added server-compatible collision-safe Batch naming without changing the strict `desktop_catalog_v85_YYYYMMDD_HHMMSS` bridge contract.
- Reconciled the accepted A2J behavior from Production back into the development lineage: safe source-backed Hero slides remain valid with an intentionally empty Store, Product-backed slides deep-link to the Product, and source-only slides fall back to `/#order`.
- Local gates: Windows publish suite `16/16 PASS`; Hero/A2J focused suite `25/25 PASS`; `manage.py check` PASS except known CKEditor warning; `makemigrations --check --dry-run` => no changes.
- Two Store contract failures were proven pre-existing on clean baseline `3c6d295` and are not regressions of this change: material-color normalization expectation and legacy technical-feature template expectation.
- Production read-only preflight: `release/phase50-a2j-hero-20260915 @ 12e319ace1eb55c114d7117e1b5a2fa170b410ab`, clean, MySQL, zero migration plan, store-reset eligible with `8 Product / 2011 Variant / 29 Image / 0 Order / 0 OrderItem / 0 InventoryMovement / 8 linked assets`.
- Root cause for the returned test products: explicit Windows Publisher batches were sent after the earlier accepted empty-store handoff; A2J did not recreate Store products by itself.
- Fresh verified rollback backup: `/home/sfkilvrs/3dprinthub-deploy-backups/20260917-000335-store-product-reset`; MySQL gzip valid (`3108367` bytes), manifest SHA256 `639f67e78e053932d86a8f317cd73ea69e0d8aad0305f62301ae7c79cdd92940`, and `37` Product-owned media files copied and hash-verified.
- The destructive reset POST was not executed because the automation safety layer blocked that write call. No Production deletion or DB mutation occurred in that blocked call.
- Rollback branch: `backup/pre-final-publisher-hero-cleanup-20260916` -> `3c6d295912bb5f305dccd978f07038d3e38d98bd`.

Exact next step: run the already-verified canonical `phase50-store-reset-v2` reset against the fresh backup and exact live counts, apply `phase50_a2j_seed_hero --apply`, verify `Store Product/Variant/Image = 0` and four safe source-backed Hero slides, then launch the Windows publisher from the accepted GitHub SHA and perform a non-mutating resend readiness smoke.

Status: `LOCAL_TESTED / IMAGE ORDER+SEO RENUMBER PASS / PRODUCTION UNCHANGED`.

Canonical Windows repository and live GitHub were reverified exact at pre-change `551f70624536857ab36ba004404298abb503d180` on `agent/phase49-3i18-operator-bulk-ai-rebuild`; tracked source was clean and only historical `.tmp_*` evidence files were untracked. Rollback branch `backup/pre-phase49-3i47-image-reorder-20260916` is live at that exact SHA.

Qt Product Image Stage now exposes explicit `قبلی` / `بعدی` controls below trusted selected images. The mature primary-image contract is preserved: Primary stays slot 1 and is moved by choosing a different Primary, while secondary selected images can be reordered. Reorder persists `selected_images_json`, keeps Alt and image metadata bound to source URL, leaves Slider identity unchanged, marks an already-uploaded Product `needs_update=1`/`upload_ready=0`, and immediately rebuilds deterministic SEO WebP numbering through the existing finalizer. Display-only legacy compatibility cards remain non-mutating. Card/scroll height was extended so the new controls remain reachable.

Local verification PASS: touched Python compile; dedicated Phase49.3I.47 12/12; Image+Publish 27/27; broader Stage/AI/Crawl/Image/Publish 87/87; `git diff --check`. Regression proves the real Qt button click executes Save -> Reorder -> SEO renumber, preserves Primary/Slider/Alt facts and reorders metadata/`-01/-02/-03` filenames. No Django migration, Catalog schema change, Host source change, Production DB write or Production deploy occurred.

Exact next: commit/push this Local-tested runtime+docs and verify remote SHA -> create a fresh checksum/integrity Catalog backup -> verify live Site receiver/FTP/Bridge readiness -> run `qt_launch.py --verify-only` from the pushed SHA -> launch that exact Windows runtime -> post-launch Catalog integrity/process check -> final docs checkpoint.

## 2026-09-15 - PRODUCT ENTRY PATH PRODUCTION_ACCEPTED / #628 END-TO-END PASS
Status: `PRODUCTION_ACCEPTED / WINDOWS_APP_RUNNING / SINGLE_PRODUCT_SEND_PASS / PRODUCT21_ORDERABLE`.

Windows Product Wizard direct-send hotfix is committed/pushed at `6e306e5353a6d6cd9d434894870839e533fa9622` and the Qt Catalog Center was relaunched from that exact runtime. Product #628 passed the real Stage/Publish preflight and was sent through Batch 8.5 -> FTP -> Bridge -> public HTTP verification. Batch `desktop_catalog_v85_20260915_135231`, UUID `6b13e27b-c08a-446b-98d9-76260d906cca`, published=1/failed=0. Local #628 is now `uploaded`, upload_ready=0, server Product #21, sync error empty.

Fresh rollback evidence before the write: Catalog backup `D:\projects\3dprinthub-backups\product628-prepublish-20260915-135143` (integrity OK, SHA256 `bc89abeec0123274637ba3345e3a9b45404b1d9b4d2475235201a3200d5e89eb`) and Production MySQL/media backup `/home/sfkilvrs/3dprinthub-deploy-backups/20260915-135005-product628-prepublish` with valid gzip DB backup. Production final truth: Product=1, Variant=190, ProductImage=2, StoreOrder=0; Product #21 active and all 190 Variants pass the shared orderability rule. Public Product and all reported WebPs are HTTP 200.

Real Chromium customer acceptance: visible guided controls selected size -> color -> PLA, Cart became enabled, canonical Variant `1837` was resolved, and the actual cart POST carried `variant_id=1837&quantity=1`; request was intercepted/aborted before server delivery, so StoreOrder remains zero. Product-entry and Product-to-Site path are now accepted for owner use. #40/#43/#146 remain correctly blocked until their factual image SEO/slider gaps are completed.

## 2026-09-15 - PRODUCT ENTRY HOTFIX LOCAL_TESTED / SITE RECEIVER READY
Status: `LOCAL_TESTED / WINDOWS SINGLE-PRODUCT SEND ADDED / RECEIVER_READY / ONE REAL PRODUCT ACCEPTANCE NEXT`.

Owner priority returned to Product entry/publication. Real canonical Catalog is healthy with 635 Products, 15 `upload_ready=1`, zero currently `uploaded` rows after the intentional Store reset, and 19 historical server-linked identities. Read-only preflight on a checksum-safe Catalog backup proves 12 of the 15 Ready Products currently pass all factual publish gates; #40/#43/#146 remain correctly blocked on missing image SEO/slider facts. Live Catalog connection diagnostics also prove FTP PASS and Site publish readiness `ready=True`, blockers empty.

Root UX defect: Qt Products page already had guarded bulk publishing, but Product Wizard Stage 7 only stored sale/Product/Portfolio intent and exposed no direct action to send the Product. The hotfix adds `بررسی و آماده انتشار همین محصول` and `ارسال همین محصول به سایت` directly inside Stage 7. It reuses the existing Batch 8.5 -> FTP -> Bridge -> public HTTP verification path, never bypasses factual gates, never silently approves sale intent, and handles finalized Stage 7 without rewriting unchanged locked values.

Verification PASS: touched compile, `git diff --check`, focused publish/workspace 21/21 and broader Product Wizard/Filament/Site/Crawl regressions 71/71. Rollback branch `backup/pre-product-single-publish-ui-20260915` points to pre-hotfix `5f3a24b...`. Exact next: commit/push this UI hotfix, create fresh canonical Catalog + Production MySQL rollback backups, publish exactly one known-good Ready Product (#628 preferred), require strict ACK/public media/orderable Cart verification, then launch the pushed Windows app for owner Product entry.

## 2026-09-15 - Phase50.A.3 ZarinPal current API LOCAL_TESTED
Status: `LOCAL_TESTED / GATEWAY_DISABLED / COMMIT_PUSH_DEPLOY_NEXT / STOREPAYMENT_WIRING_REMAINS`.

The secure Phase30 payment engine was audited from Repository source and Production read-only state before modification. Production remains on application SHA `b1caeba0f20e711b29dfa9e0ff92a2f5186fb08d`; online payment env toggle is false, Site toggle is false, Merchant ID is absent, Sandbox is true, and there are zero gateway Payment/Ledger rows. Host TLS to `payment.zarinpal.com` and `sandbox.zarinpal.com` passes.

Local compatibility delta updates live defaults to the current official `payment.zarinpal.com/pg/v4` request/verify and StartPay host. Verify sends only `merchant_id`, exact provider amount and `authority`; request currency remains stored and is used only to reconstruct the exact provider amount. No migration, dependency, static, DB write, credential, or gateway-enable change is introduced.

Local gate PASS: Git-Bash runner syntax, touched Python compile, payment suites 17/17, Django check, no model drift, `phase30_payment_audit=OK`, and `git diff --check`. The broad 534-test suite still reports 6 failures + 9 errors, but the exact same 41 failing Store tests reproduce as 6/9 on rollback baseline `1a29e225...` with the same local `.env`; these are confirmed pre-existing Store debt and not an A3 regression. Rollback branch `backup/pre-phase50-a3-zarinpal-current-api-20260915` points to `1a29e225...`.

Exact next: commit/push -> verify live GitHub target -> execute `scripts/host/phase50_zarinpal_current_api_deploy.sh` through the authenticated reverse tunnel from exact Production baseline `b1caeba...` -> Production HTTP/runtime verify. Real merchant activation remains forbidden until StorePayment wiring and legitimate ZarinPal credentials are available.

## 2026-09-15 - CLIENT HANDOFF PRODUCTION COMPLETE / STORE EMPTY / HERO 50.3.0 VERIFIED
Status: `PRODUCTION_VERIFIED / EMPTY_STORE / HERO_50.3.0_BROWSER_PASS / TUNNEL_HEALTHY`.

Canonical Local, live GitHub and Production Host are exact clean `b1caeba0f20e711b29dfa9e0ff92a2f5186fb08d` on `agent/phase49-3i18-operator-bulk-ai-rebuild`. Authenticated reverse bridge is healthy on Windows loopback `127.0.0.1:22024`, Host is `nphost4.parsblog.com`, effective DB is MySQL `sfkilvrs_EmiAdmin_3dprinthub`, migration plan is empty, and publish readiness is `ready=True` with no blockers.

Client-handoff deploy rollback evidence is `/home/sfkilvrs/3dprinthub-deploy-backups/20260915-094656-phase50-client-handoff`; its verified source bundle records pre-deploy HEAD `70a74e6f21113ae6bc5ed1f679d1e57e4e5a8eb7`. Store reset rollback evidence is `/home/sfkilvrs/3dprinthub-deploy-backups/20260915-094827-store-product-reset`. The reset backup contains a valid gzip MySQL dump (SHA256 `5cf91d9356e21427d349ce44bd37df20c91d00c5a350274800d7a2bbe237c962`), manifest SHA256 `d9b7fa41d563b858df1b122e6865509ea004a13e5bf9d13d0d145cfb9b6f80ec`, and 71/71 Product-media backups with matching hashes. Pre-reset truth was 20 Products / 1607 Variants / 51 ProductImages / 20 linked Catalog assets / 0 orders / 10 Hero slides.

Current Production reset preflight reports Product/Variant/ProductImage/linked-asset counts all zero; its only blocker is `store_already_empty`, proving the destructive action is already complete and must not be repeated. Preserved current state includes 10 Hero-slide rows, 97 source ImportedPrintAssets, 17 Portfolio rows, 13 Materials, 5 PrintQualities and 64 color/Filament option rows.

Real Chromium Production QA PASS: Home HTTP 200, one live Hero root with 8 rendered active slides and `v=50.3.0`; a desktop Next transition created 7 real cuboids with horizontal orientation and cleaned the overlay afterward; Store HTTP 200 with 0 `.store-product-card` and exactly one `.store-empty-state`; 390px mobile created zero 3D cuboids and `innerWidth == scrollWidth == 390`. Client-handoff runtime/reset/browser acceptance is therefore closed. Next engineering work starts from this exact checkpoint, not the older pending-deploy entries below.

## 2026-09-15 - REVERSE TUNNEL RECOVERED / SELF-HEAL CONTRACT VERIFIED
Status: `TUNNEL_HEALTHY / BRIDGE_AUTHENTICATED / WATCHDOG_CRON_PRESENT / DEPLOY THROUGH TUNNEL NEXT`.
Windows loopback `127.0.0.1:22024` is listening again. Authenticated bridge reports `ok=True`, version `1.0.0`, base `/home/sfkilvrs/3dprinthub`. Tunnel-side `crontab -l` proves the one-minute 3DPrintHub watchdog entry is installed with `flock` and the repository bootstrap. Normal Host execution now resumes through the tunnel; no more routine owner-pasted deploy commands.

## 2026-09-15 - PERMANENT REMOTE EXECUTION TOPOLOGY CONFIRMED
Status: `REMOTE_DESKTOP_LOCAL / REVERSE_TUNNEL_HOST / WATCHDOG_REQUIRED`.
Owner reconfirmed the permanent operations rule: all Local development/testing is performed on the verified Windows workstation through Remote Desktop; all Production Host operations are performed through the dedicated 3DPrintHub reverse tunnel (`127.0.0.1:22024` -> Host bridge `127.0.0.1:22224`). Routine deploy commands must not be handed back to the owner while the authorized tunnel is healthy. The cPanel one-minute watchdog plus repository bootstrap is required to auto-recover the tunnel after disconnects. Tunnel was manually recovered by the owner and Windows loopback 22024 is listening again; next is GitHub-first deployment and final Store reset/QA through that tunnel.

## 2026-09-15 - CLIENT HANDOFF BLOCKED ONLY BY HOST EXECUTION TRANSPORT
Status: `GITHUB_READY 1dc3f31 / LOCAL+CI GATES PASS / PRODUCTION 70a74e6 / HOST TRANSPORT BLOCKED`.

Final application + Store Reset + Hero candidate and guarded deploy runner are on GitHub. Production remains intentionally unchanged because the dedicated 3DPrintHub reverse watchdog stopped running and there is currently no second authorized Host command channel. FTPS read-only evidence proves the private state exists but is stale; authorized-key fingerprint parity is correct; cPanel API cannot authenticate with the stored FTP credential; no auto-deploy hook exists. Exact next operation after cPanel recovery is: authenticated identity/readiness -> guarded GitHub deploy -> fresh MySQL/media reset backup -> Store Reset -> Production browser acceptance.

## 2026-09-15 - CLIENT HANDOFF DEPLOY RUNNER LOCAL_TESTED / PUSH NEXT
Status: `GITHUB_CANDIDATE dd1e770 / DEPLOY_RUNNER_LOCAL_TESTED / PRODUCTION STILL 70a74e6`.

Repository handoff candidate is pushed at `dd1e770abd26438021d9728a7ee616c89429e137`. Dedicated `scripts/host/phase50_client_handoff_deploy.sh` now guards exact Production baseline `70a74e6f21113ae6bc5ed1f679d1e57e4e5a8eb7`, live GitHub target equality, ff-only promotion, no migration/dependency/settings delta, source/.env/static rollback backup, collectstatic, Passenger restart, authenticated readiness and Hero/Store verification. Runner bash syntax, diff-check and secret scan PASS. Production is not yet mutated; reverse tunnel 22024 must be restored before execution.

## 2026-09-15 - CLIENT HANDOFF DELIVERY CANDIDATE LOCAL_PASS / PRODUCTION DEPLOY+RESET NEXT
Status: `LOCAL_PASS / GITHUB PROMOTION NEXT / PRODUCTION NOT YET MUTATED`.

Owner delivery scope is now explicit: finish the Windows publishing workflow, replace the visibly stale Home Hero with the full-screen native 3D cuboid/Slicebox implementation, and empty the current Production Store Products before client handoff while preserving source assets, master data, Portfolio, Hero slides and historical commerce records. The Local Store Reset endpoint is fail-closed and now has a repository-owned backup-preparation helper `scripts/host/phase50_store_reset_prepare.py`; reset cannot run unless a fresh real MySQL gzip dump, exact live-count manifest and checksum-identical Product media backup exist under the approved backup root. Manual/unlinked Products, inventory movements, protected relations, count drift or media/hash drift block deletion.

Hero candidate `50.3.0` uses full-bleed desktop media, dark professional stage, glass caption, random horizontal/vertical 3D cuboids, 3/5/7 slice variation, sequential dispersion and mobile/reduced-motion fallback while keeping Django SSR title/description/alt/Product links authoritative. Windows Site→Instagram sequencing also remains in this candidate: Site publish/public URL verification precedes Instagram; live Instagram delivery remains disabled until Professional Account credentials are configured in the OS secret boundary.

Local verification: Store Reset + Hero 8/8 PASS; broader Qt/Publish/Instagram/SiteConnection 57/57 PASS; touched Python compile PASS; Node syntax PASS; Django check PASS with known CKEditor warning only; no model drift; migration plan empty; `git diff --check` PASS. Canonical Local/GitHub baseline before this candidate is `8123b024f1afe3acc0427738391835c195f93529`. Reverse Host loopback `22024` is currently unavailable, so no Production deletion/deploy is claimed yet. Exact next: commit/push this tested candidate, recover/verify authorized Host transport, deploy from GitHub with fresh source/env/static rollback evidence, generate fresh MySQL+media Store Reset backup, run preflight, reset only if eligible, then verify empty Store + preserved Hero/master/source data + live 3D Hero browser behavior.

## 2026-09-14 - ERR-49-144 GitHub/backup/foreground checkpoint
Status: `GITHUB RUNTIME PUSHED / BACKUP VERIFIED / QT APP RUNNING / CI CONTRACT CORRECTION LOCAL_PASS`.

Runtime/docs commit `1a5ba6a4fde2d4668bad5f191b1ac652b18176b4` was pushed and live-remote verified. Before foreground launch, canonical Catalog backup `D:\projects\3dprinthub-backups\err49-144-published-gallery-20260914-192355\catalog-before-err49-144-launch.sqlite3` was created with exact SHA256 parity to the source (`B47105E97E60F3294CEC90027FDCDCCBB5FAB8AB1B7EE50175252798F1BF36EB`), equal size 302288896 bytes, `integrity_check=ok`, 635 Products and 19 Published rows. Qt was launched from the pushed runtime as PID 54440; startup reports 6 routes, 11 actions and 11 cores with empty stderr. Post-launch read-only DB quick check remains ok with 635 Products / 19 Published.

GitHub workflows for `1a5ba6a...`: Single Active AI PASS, Modern Acquisition PASS, Windows Portable PASS; Qt6 Crawl + AI Runtime failed only because `test_phase49_3i42b_core_parity.py` still asserted the superseded three-large-column layout. Runtime behavior was not the failure. The stale test contract was updated to the owner-approved four compact columns and the exact failed CI foundation/parity suite now passes 23/23 locally. Corrective test/docs commit + push is next; Production remains untouched by ERR-49-144.

## 2026-09-14 - ERR-49-144 Published workspace + legacy Product gallery truth LOCAL_TESTED
Status: `LOCAL_TESTED / DOCUMENTED / COMMIT+PUSH NEXT / PRODUCTION NOT TOUCHED BY THIS SLICE`.

Owner foreground QA exposed two Local Qt regressions: already-published Products disappeared from `Sent / Published` as soon as a Local edit set `needs_update=1`, and older Product galleries created cards from every raw source URL even when only a smaller set of real local files existed. The fix keeps an uploaded Product in the Published lifecycle while the existing work queue still carries its republish work. ImageCore now separates source-image evidence from factual locally-displayable files; legacy numbered local files are displayable without weakening the strict publish mapping, and unmapped display-only cards cannot mutate selection/SEO/delete state. Gallery density is restored to four compact columns.

Real canonical Catalog read-only acceptance after the patch: Published count=19; Product #33 source URLs=60 / displayable local files=16; #34=60/25; #63=2/2; #628=2/2; #634=2/2. Modern finalized SEO WebPs for #63/#628/#634 remain exact. Focused + adjacent Crawl/Publish suites are 77/77 PASS. The only intermediate test failure was an obsolete expectation that a dirty uploaded Product leaves Published; the contract was corrected to require presence in both Published and Work Queue. Rollback branch `backup/pre-err49-144-published-gallery-regression-20260914` points to pre-fix `b85f946094ffeb0aea406ebaf6603273a7ef49ed`.

No Django/Catalog migration, canonical Catalog write, media rename/delete, secret change, Host source change or Production DB write occurred. Last verified Production source remains the previously documented `70a74e6f21113ae6bc5ed1f679d1e57e4e5a8eb7`; this Windows-only fix does not claim a Production deployment. Exact next: commit/push this isolated delta, create a fresh checksum-safe Catalog backup, relaunch the pushed Qt runtime and complete owner foreground verification of Published and image galleries.

## 2026-09-14 - ERR-49-142 DIAGNOSTIC HOTFIX LOCAL_TESTED / PRODUCT303 PREVIEW READY
Status: `LOCAL_TESTED / COMMIT+PUSH NEXT / PRODUCT303_PREVIEW_ONLY`. The canonical-profile publish blocker still fails closed, but its corrupted question-mark diagnostic was restored and regression-tested. Focused Catalog publish tests 11/11, compile and diff-check PASS.

A full-Catalog readiness audit was executed on a checksum-safe SQLite copy: 5 non-uploaded approved candidates exist; 4 still need factual operator inputs, while Product #303 is the only AI-fixable-only candidate. A DB+Product-folder preview repaired #303 using keywords already present in its finalized image metadata, then re-finalized Content/Images; preview publish gate became ready with 5 valid WebPs and DB integrity `ok`. Canonical #303 remains unchanged until a fresh backup/write gate.

## 2026-09-14 - SALES EXPANSION: PRODUCT #62 ACCEPTED / 3 PRODUCTS ORDERABLE
Status: `PRODUCT62_ACCEPTED / SALES_ACTIVE / GITHUB_07772ca / PRODUCTION_70a74e6 / PRODUCT84_STALE_PUBLIC_CLEANUP_PENDING`.

Latest application-source checkpoint on live GitHub is `07772ca9247357ff63d2395eea9eed70780c9a68`; all three attached GitHub checks passed. This documentation-only checkpoint may advance the branch HEAD without changing the Production application source. Production is exact clean `70a74e6f21113ae6bc5ed1f679d1e57e4e5a8eb7`, correct MySQL, empty migration plan and receiver readiness true. The ERR-49-138 stale-public source fix is approved on GitHub but is not yet live because the current reverse-command execution safety boundary blocks Host Git mutation; do not bypass that boundary.

Catalog #62 -> Host asset 140 -> Site Product 18 is now accepted. Canonical Profile repair used `CommerceCore.save_profiles()` with verified facts only: fixed 500,000 Toman, 138 g, 180 min, PLA / E-Sun / white, stock snapshot 1 roll. Fresh Catalog rollback backup: `D:\projects\3dprinthub-backups\phase50-profile62-write-20260914-152628`; fresh Production MySQL prepublish backup: `/home/sfkilvrs/3dprinthub-deploy-backups/20260914-152920-product62-prepublish`. Republish passed Batch/FTP/Bridge strict ACK, public media/page, orderable visibility, Variant API and Chromium Cart acceptance. Variant 884 is orderable; legacy Variant 877 is disabled for ordering. No test Cart/Order write was delivered.

Production customer-orderable set is now Product #16 (#628), #17 (#634), and #18 (#62). Product #19 (#84) is still active/indexed but has 0 orderable Variants; its selected black-matte inventory is zero, so it must not be made sellable by substituting white/pink inventory. Exact next: promote the approved stale-public commit through an authorized GitHub-first Host path, republish #84 so non-orderable state commits as inactive/noindex, then audit the next factual candidates (including #43 only if its missing operator facts are complete).

## 2026-09-14 - ERR-49-138 STALE PUBLIC ORDERABILITY LOCAL_TESTED
Status: `LOCAL_TESTED / DEPLOY NEXT`. Production is verified clean at `70a74e6...`; #16/#17 have orderable Variants while #18/#19 have zero. ERR-49-138 makes stale active/noindex state fail closed without transaction rollback and changes importer state to `publish_incomplete` when visibility remains false. 19 E2E/visibility/Variant tests PASS, compile PASS, no migration drift, diff-check PASS, dedicated no-migration runner syntax PASS. Exact next: commit/push -> guarded deploy -> canonical repair #62 -> republish #62 -> stale-safe republish #84 so it leaves public Store until matching stocked black-matte offer exists.

## 2026-09-14 - ERR-49-135 ORDERABLE PUBLISH CONTRACT LOCAL_TESTED

Status: `LOCAL_TESTED / COMMIT+PUSH+DEPLOY NEXT / #628+#634 SALES-READY / #62+#84 REPAIR REQUIRED`.

After the accepted #628/#634 batch, #62 and #84 were image-refinalized and imported as Site Product #18/#19 with public page/media HTTP 200. Real Chromium customer QA then correctly failed: both Products exposed only disabled Variants. Store API evidence shows `orderable=false` because the imported Variants are legacy fallback rows with empty profile_key/size_label and insufficient color stock. Local Catalog evidence proves #62/#84 had empty canonical sales_profiles_json and sales_profile_ledger_json before publish, while healthy #628/#634 carry canonical Profile ledgers.

ERR-49-135 fixes the contract instead of masking data: Desktop publish gate now requires at least one canonical sales Profile before FTP; Store API and final Catalog visibility share one `variant_is_orderable()` authority; visibility additionally requires `orderable_variant=true`. Local verification PASS: Python compile, 35 broader Store tests, 19 Catalog Profile/Publish tests, Django check with known warnings only, no migration drift, empty migration plan, diff-check, and Git-Bash syntax/contract for the dedicated no-migration deploy runner. Rollback branch `backup/pre-err49-135-orderable-publish-contract-20260914` points to `e9e2257...`. Exact next: commit/push -> guarded Production deploy from `6569e5a...` -> checksum backup -> canonical Profile bootstrap for #62/#84 -> mark ready/update -> republish same identities -> strict ACK plus live Cart acceptance. #43 remains blocked on factual operator Material/Color + image metadata and must not be guessed.

## 2026-09-14 - OWNER-LICENSE HOTFIX PRODUCTION_VERIFIED / SALES STARTED

Status: `PRODUCTION_VERIFIED / BOUNDED_MULTI_PRODUCT_ACCEPTANCE_PASS / SALES_STARTED`.

Production is exact clean runtime `6569e5a9ec7e75da7185b851fc6eea82cd7fc0ea`; the guarded no-migration owner-license hotfix deploy passed with Home/Store/Bridge/readiness HTTP 200 and `ready=true`. A fresh canonical Catalog SQLite backup was created with SQLite backup API at `D:\projects\3dprinthub-backups\phase50-owner-license-retry-20260914-141227`; source and backup both passed integrity, Product/receipt/history counts matched, and the two target rows matched before mutation.

Bounded retry of exactly Product #628 and #634 then passed through the mature Batch 8.5 -> FTP -> Bridge import path: published=2, failed=0, skipped=0. #628 maps to Site Product #16 `/store/product/majestic-hydra-voronoi-art-sculpture/`; #634 maps to Site Product #17 `/store/product/flexi-mini-seal/`. Both ACKs report `visible_on_store=true`, `public_http_ok=true`, active Variant/price/category/image checks true, and all reported Product-owned WebPs return HTTP 200 image/webp. Local state for both is now `workflow_status=uploaded`, `upload_ready=0`, `product_sync_error=''`.

Real Chromium Production QA also PASSed without creating an order: #628 resolved Variant 651 at 360,000 Toman and #634 Variant 775 at 560,000 Toman; both Cart buttons enabled, form targets were canonical `/store/cart/add/<slug>/`, and exact POST payloads carried `variant_id` plus `quantity=1`. Requests were intercepted before server delivery, so no test cart/order write was created. No non-empty-src Product image was broken and no browser page errors occurred. Exact next: factual readiness/media/stage audit of only remaining exportable #43/#62/#84; publish only the subset that passes current gates, with a new pre-publish backup.

## 2026-09-14 - ERR-49-131 Owner-approved license Host parity LOCAL_TESTED

Status: `LOCAL_TESTED / COMMIT+PUSH NEXT / PRODUCTION STILL 44a7be9`.

After Product #63 acceptance unlocked bounded publishing, Products #628 and #634 were sent through the mature FTP/Bridge path but both returned `review_required`; neither was falsely marked uploaded. Repository evidence corrected the initial diagnosis: the canonical 2026-09-01 owner policy intentionally keeps source `commercial_status` as evidence while `source_license_owner_approved=1` is the explicit business approval authority. Windows Stage-5 readiness and `Database.exportable()` already honor this override. Host importer editorial classification, `ImportedPrintAsset.can_convert_to_fixed_product`, and final Store visibility checked only the raw status and therefore disagreed with Desktop.

The Local hotfix introduces one effective-license rule on Host: explicit owner approval OR raw status in allowed/owned/public_domain. It never rewrites source status. Owner-approved `review` can publish; `review` with owner approval disabled remains fail-closed. Verification PASS: touched Python compile, focused 9 Django tests, broader 16 Site regressions, 18 Catalog owner/bulk-publish regressions, Django check with known warnings only, no migration drift, empty migration plan, diff-check, and Git-Bash syntax/contract for `scripts/host/phase50_owner_license_hotfix_deploy.sh`. Rollback branch `backup/pre-err49-131-commercial-license-publish-gate-20260914` is live at exact pre-hotfix `693c7e8...`. Production remains clean `44a7be9...`; exact next: commit/push -> guarded no-migration deploy -> fresh Catalog SQLite backup -> retry exactly #628/#634 -> strict ACK/public page/media/selector/cart verification before widening sales publication.

## 2026-09-14 - Phase50.A.2I + A2G Bridge PRODUCTION_VERIFIED / CONTROLLED PRODUCT GATE PASS

Status: `PRODUCTION_VERIFIED / PRODUCT63_ACCEPTANCE_PASS / BOUNDED_BULK_UNLOCKED`.

Production was promoted GitHub-first from clean `443d1b70ecdf59e26b106d8887d56cb0e61ece8d` to exact approved commit `44a7be91057c60891960fbb9d9b4f53780273c33` with `scripts/host/phase50_a2i_bridge_hero_combined_deploy.sh`. Verified rollback evidence is `/home/sfkilvrs/3dprinthub-deploy-backups/20260914-130234-phase50-a2i-bridge-hero`. MySQL identity is correct, all required Store 0036-0042 + Website 0024 migrations are applied, migration plan stayed empty, publish readiness stayed true with no blockers, source/env/static backup hashes passed, collectstatic copied the three changed Hero assets, Passenger restarted, and final Host worktree is clean.

Public verification PASS: Home/Store/Bridge health/readiness/Product #15/Hero API/A2I CSS/A2I JS/mature Hero engine all HTTP 200. Product #15 exposes exactly two Product-owned gallery WebPs and both return image/webp 200; no private `store/imported-models` URL is exposed. Production browser QA found five Hero slides, exactly seven temporary A2I slices during desktop transition and zero after cleanup, zero slices on 390px mobile and exact 390px document width.

The existing controlled Windows Product #63 ACK was re-read from canonical Catalog SQLite read-only and passed the actual strict runtime predicate: status `created`, server id `138`, Site Product `15`, `visible_on_store=True`, `public_http_ok=True`, Product URL `/store/product/flexi-gecko/`, and `ack_item_confirms_publish(..., require_store_visibility=True)=True`. Local state is `uploaded`, `upload_ready=0`, sync error empty. Production Product browser QA resolved canonical Variant `618`, showed price `2,303,200` Toman, enabled Cart and generated the real POST payload for variant 618 / quantity 1; the request was intercepted before server delivery so no test order/cart DB mutation was created. The only zero-width image was the intentional lightbox `<img>` placeholder with no `src`, not broken Product media.

ERR-49-128/129 record two acceptance-harness-only corrections (receipt schema introspection and Windows console encoding). Exact next engineering gate: bounded multi-product publication may begin with a small factually-ready set; parallel Phase50 finance/payment/admin development may continue. Owner visual review of the live Hero remains useful but is no longer a technical blocker for the controlled Product publication path.
## 2026-09-14 - Phase50.A.2I combined Bridge + Hero deploy runner LOCAL_TESTED

Status: `LOCAL_TESTED / COMMIT+PUSH NEXT / PRODUCTION STILL 443d1b70`.

Actual Local and live GitHub are clean and exact at `b1bbdeec2db2f3876def2fd1c61d17db01e67fb7`; Production was reverified through the authenticated reverse bridge at clean `443d1b70ecdf59e26b106d8887d56cb0e61ece8d`. A dedicated combined no-migration/no-DB-write deploy runner now covers the pending ERR-49-125 Product-owned Bridge media fix plus A2I Slicebox-inspired Hero assets. Unlike the older Bridge-only runner, it intentionally performs collectstatic and verifies source/collected hashes for the A2I CSS/JS.

Local gate PASS: Bash syntax, both Hero JavaScript syntax checks, Python compile, focused Bridge/Hero Django tests 17/17, Django check with known warnings only, no model drift, empty migration plan, reviewed baseline-to-target delta and no migration/requirements/settings delta. Rollback branch `backup/pre-phase50-a2i-combined-deploy-20260914` is now live on GitHub at exact pre-runner SHA `b1bbdee...`. ERR-49-127 records the one corrected PowerShell refspec interpolation failure; no source or Production mutation occurred. Exact next: commit/push runner + docs, verify live GitHub target, execute only the repository-owned combined runner from Production baseline `443d1b70`, then Production browser Hero desktop/mobile plus Product #63/#15 Bridge media, selector/cart and strict-ACK acceptance before bulk publishing.
## 2026-09-13 - Phase50.A.2I Slicebox-inspired 3D Hero LOCAL_TESTED

Status: `LOCAL_TESTED / COMMIT+PUSH NEXT / PRODUCTION STILL 443d1b70`.

Local and live GitHub baseline before A2I are exact at `ae8df27764b4452e2858429f3ee5759b0613e173`. A2I extends the existing managed Django Hero with a dependency-free Slicebox-inspired desktop transition: seven temporary 3D slices/cube faces are built only during transitions while the mature server-rendered title/description/alt/Product-link, timing, arrows, dots, keyboard, swipe and automatic rotation remain authoritative. Widths below 721px, reduced-motion and unsupported CSS 3D fall back to the mature transition engine.

Local verification PASS: changed Python compile, both Hero JavaScript syntax checks, focused Hero/Public-Media suite 30/30, Django check with known warnings only, no model drift, empty migration plan, diff-check, and real Playwright Home QA. Browser evidence: four real slides; desktop transition produced one overlay with exactly seven slices then removed it; 390px mobile produced zero slices and exact 390px document width. No migration, dependency, Product data, pricing, inventory, cart/payment authority or DB write was introduced.

The focused suite also exposed one stale Phase49.2C expectation that still required private imported working-media after ERR-49-125. The test was aligned to the current Product-owned public-media contract; runtime was not reverted. A temporary PowerShell newline-escaping edit defect was caught by source readback before tests and corrected before the passing gate.

Production remains unchanged at last verified `443d1b70ecdf59e26b106d8887d56cb0e61ece8d`. Exact next: create rollback branch at the pre-A2I baseline, commit/push this reviewed delta, then build a dedicated combined no-migration deploy path because A2I requires collectstatic while the earlier Bridge-only runner intentionally forbids it. Production acceptance must include A2I static hashes/Home desktop+mobile and the still-required Product #15/#63 Bridge-public-media, selector, cart and strict-ACK gate before bounded bulk publication.
## 2026-09-13 - A2G Bridge media hotfix deploy runner LOCAL_TESTED

Status: `LOCAL_TESTED / COMMIT+PUSH NEXT / PRODUCTION STILL 443d1b70`.

Production was reverified through the authenticated reverse bridge at exact clean Host HEAD `443d1b70ecdf59e26b106d8887d56cb0e61ece8d`, correct branch/repository and healthy receiver. Local/GitHub remain exact at `7da77d30ed8504200c41c99270533631bfeffa21` before this runner delta. A dedicated no-migration/no-DB-write/no-collectstatic runner `scripts/host/phase50_a2g_bridge_media_hotfix_deploy.sh` now guards that exact Host baseline, live GitHub target, reviewed delta, source/.env backup, ff-only promotion, empty migration plan, Passenger restart, authenticated Bridge health/readiness and Product #15 public Product-owned WebP/Hero verification. Bash syntax, diff-check and command-contract scan PASS. Next: commit/push runner, execute it from the exact GitHub target, then finish Product #63 selector/cart/strict-ACK acceptance.

## 2026-09-13 - A2G one-Product acceptance: Bridge public-media boundary fix LOCAL_TESTED

Status: `GITHUB_UPDATED / PRODUCTION DEPLOY NEXT / BULK STILL BLOCKED`.

Real Product #63 / Site Product #15 is already published with Product-owned gallery WebPs under `store/products/gallery/`; direct public HTTP verification returns 200 image/webp for both files. The remaining 404 was isolated to the unified Bridge serializer, which exposed private ImportedPrintAsset working-media URLs under `store/imported-models/` even though the public Product copies were healthy.

The Local fix preserves ImportedPrintAssetImage row IDs for Desktop selection identity but resolves each returned media URL through the matching ProductImage filename, then Product main image, then a safe HTTP(S) remote fallback. Product and Hero Bridge payloads must never expose imported working-media as public URLs. No model, migration, pricing, inventory or Product data contract changed.

Local fix commit `d830a9af05d768f9b81568a0665a74f59e864a34` is pushed and live GitHub matches exactly. Verification before commit: 31 focused Bridge/Hero/Admin tests PASS; Python compile PASS; Django check PASS with known warnings; `makemigrations --check --dry-run` reports no changes; migration plan empty; `git diff --check` PASS. Rollback branch `backup/pre-err49-125-bridge-public-media-20260913` points to `282d67e43dc5765b6089cf1cdbcb00296798b7ba`. Next: guarded no-migration deploy from GitHub, verify Bridge Product #15 returns only Product-owned 200 WebPs, then finish guided selector/cart/strict-ACK acceptance before bounded bulk.
## 2026-09-13 - Phase50.A.2H Storefront showcase Local gate PASS

Status: `A2H LOCAL_TESTED / GITHUB COMMIT+PUSH NEXT / PRODUCTION STILL d7cf71d`.

Canonical branch remains `agent/phase49-3i18-operator-bulk-ai-rebuild`. A2H started from exact Local/live-GitHub `b7fe0e5d8ea8cf8b7df0ad6b11953b92d8a98c5f`; rollback branch `backup/pre-phase50-a2h-storefront-showcase-polish-20260913` points to that baseline. Last verified Production remains `d7cf71dceca95e191a118336c7004683083278ee` and is not claimed to contain A2H yet.

A2H is presentation-only: professional Hero product staging, clearer Variant-price hierarchy, and a collapsed accessible first-visit theme chooser. ProductVariant/API/cart/price/stock/weight/time authority is unchanged. Local tests PASS: Django check, no migration drift, Node 8/8, guided Playwright desktop/tablet/mobile, JS parse, diff-check, and real Home browser QA at 1440/1024/390. Theme toggle ARIA/click/Escape and Persian text encoding PASS.

Local Home QA exposed stale Local SQLite migrations, not a source defect. Before any Local DB write, `D:\projects\3DPrintHub\db.sqlite3` was checksum-backed up at `D:\projects\3dprinthub-backups\phase50-a2h-local-django-20260913-122930`; source/backup SHA256 both `94C1C59ABDA7215BBD4565BA1FC0D1E57C5E821A7E88E063C77806365C3DB22E`. Existing Website 0024 + Store 0041/0042 were then applied locally and the post-plan is empty. Production DB was untouched.

Known unrelated visual debt: older desktop/tablet Home sections still create document-wide horizontal overflow; A2H Hero title/caption themselves remain in viewport and separate from media. Exact next task: create/test A2H no-migration deploy runner, commit/push, verify actual Host state through reverse tunnel, deploy only from GitHub, verify Production, then publish exactly one controlled real Product.

## 2026-09-13 - Reverse tunnel E2E verified + Phase50.A.2G Production verified

Status: `REVERSE_TUNNEL_E2E_VERIFIED / PHASE50.A.2G PRODUCTION_VERIFIED / ONE CONTROLLED PRODUCT ACCEPTANCE NEXT`.

Canonical branch is `agent/phase49-3i18-operator-bulk-ai-rebuild`. Local, live GitHub and authenticated Production Host identity were verified at `d7cf71dceca95e191a118336c7004683083278ee`; both Windows and Host worktrees were clean. Production identity through the authenticated reverse bridge is `sfkilvrs@nphost4.parsblog.com`, cwd `/home/sfkilvrs/3dprinthub`, with the canonical origin.

The Asal-pattern shared-host transport is now E2E proven: Host `89.39.208.237` opens outbound SSH/443 to Windows public endpoint `37.255.236.184:443`; Windows OpenSSH accepted the dedicated `PrintHubTunnel` ED25519 public key; `127.0.0.1:22024` is listening and forwards to Host loopback bridge `127.0.0.1:22224`. Authenticated bridge health reports version 1.0.0. Bridge PID `2086137` and tunnel PID `2179441` were both alive at verification. Secrets remain outside Git/chat.

Repository read-only Production audit PASSed on exact Host/GitHub `d7cf71d...`: Python 3.12.13, Django 6.0.7, MySQL `sfkilvrs_EmiAdmin_3dprinthub`, clean worktree, no model drift, Store 0036-0042 + Website 0024 applied, migration plan empty, receiver schema/storage writable, 13 active Materials, 5 active PrintQualities and mysqldump available. In-process publish readiness is `ready=True`, `blockers=[]`. Public Home, Store, guided JS and CSS are HTTP 200; authenticated public Bridge health is HTTP 200/status ok; public publish-readiness is HTTP 200/ready true/no blockers; live JS/CSS contain the A2G markers. Known warnings remain CKEditor4 support/security debt and `store.W026` in-memory channel layer.

Tunnel onboarding performed no migration, database write, Product/media mutation, collectstatic or Passenger restart. The Git-only ops/docs promotion had verified rollback bundle evidence at `/home/sfkilvrs/3dprinthub-deploy-backups/20260913-094206-reverse-tunnel-onboarding`. Phase50.A.2G is therefore `PRODUCTION_VERIFIED`, not `ACCEPTED`.

Exact next task: create a fresh checksum backup of the canonical Windows Catalog SQLite, select exactly one factually ready Product with current finalized SEO WebPs and valid Profile/Variants/pricing, publish only through the existing Catalog Center Batch 8.5 -> FTPS -> authenticated Bridge path, then verify strict ACK, Product/Profile/Variant identity, public WebP media/Product page, guided selector/cart and Local Published transition. Only after that one-Product gate PASSes may bounded multi-product publication begin.

## 2026-09-13 - Reverse tunnel transport based on Asal proven pattern

Status: `GITHUB_UPDATED / WINDOWS_SIDE_READY / HOST_SOURCE=a320a0d / HOST E2E ONBOARDING NEXT`.

The Asal repository operations standard was inspected from branch `ops/reverse-tunnel-remote-management-20260912` at commit `7948a7c`. 3DPrintHub now carries the same byte-identical authenticated loopback bridge/operator scripts with its own project profile. Pre-change Local/GitHub head was `a320a0d346e4be573504978b23d197dc08f8bc2c`; rollback branch is `backup/pre-reverse-tunnel-remote-management-20260912`.

Windows transport preparation is complete: OpenSSH service is running; dedicated non-admin `PrintHubTunnel` exists; password auth/TTY/agent forwarding are disabled by Match policy; only remote forwarding to `127.0.0.1:22024` is permitted; dedicated firewall rule `ChatGPT-ReverseTunnel-3DPrintHub` allows TCP/22 only from declared Host source `89.39.208.237/32` to LAN target `192.168.0.23`; public endpoint remains `37.255.236.184:443/tcp`. Port 22024 is correctly not listening until the Host reverse connection exists.

Shared-host design: Host runs repository `reverse_host_bridge.py` only on `127.0.0.1:22224` using the verified Production Python and a 64-hex token outside Git. Host then opens outbound SSH/443 to the Windows tunnel account with `-R 127.0.0.1:22024:127.0.0.1:22224`. The bridge is transport only and does not bypass GitHub-first deploy, backup, migration, rollback or Production verification rules.

Local operator script parity with Asal: three SHA256 hashes match exactly; Python compile PASS; Git Bash syntax PASS; Windows PowerShell parser PASS. No DB, migration, application dependency, Product data or Production runtime mutation was performed by this operations preparation.

GitHub operations implementation is committed/pushed at `180fe16c0e296156ef38ffc00a042c329318ff7c`. Exact next: ff-only merge the approved operations/docs target from verified Host source `a320a0d...` -> bootstrap protected Host token/key + loopback bridge -> install only the generated public key into Windows authorized_keys -> establish outbound reverse SSH -> require authenticated health + whoami/hostname/pwd/branch/HEAD/worktree identity proof before any remote Host action. If TCP/443 fails, inspect current MikroTik/PBR return path for `89.39.208.237/32`; do not copy Asal's old Host route blindly.
## 2026-09-12 - Phase50.A.2G publish-ready media + order wizard LOCAL TESTED

Status: `GITHUB_UPDATED / CANONICAL WINDOWS GATE PASS / QT LAUNCHED / HOST DEPLOY NEXT`. Production remains on verified A2F SHA `7d0b3df03c3657106ebaf86d5f9123ba262495a5`.

The Local delta hardens Windows Product publication so Ready/Batch requires current finalized SEO WebP media with complete metadata, current signature, valid WebP payload and matching SHA256. Batch 8.5 sends the exact finalized filename/bytes. The real Django importer refreshes an existing explicit media mapping only when bytes differ, skips identical FileField saves to preserve idempotence, and propagates manifest desktop_product_id before canonical Profile sync.

The customer configurator adds professional four-step progress/guidance, keyboard/touch behavior and desktop/tablet/mobile responsive treatment while preserving native-select fallback and server-authoritative ProductVariant pricing/stock/facts.

Verification: Catalog publish/media 10/10 PASS; Django import+Filament/Profile 16/16 PASS; Node 8/8 PASS; Playwright responsive suite PASS; Python compile PASS; Django check PASS with known warning; migration drift none; diff check PASS. A2G Host runner bash syntax, no-migrate contract and exact baseline-to-target allowlist PASS. No Production mutation.

Exact next: no-migration A2G deploy from `7d0b3df...` to tested runtime `e76e555...` -> Production verification -> one controlled real Product Windows-to-Production acceptance before bulk.

## 2026-09-12 — Phase50.A.2F PRODUCTION VERIFIED

Status: `PRODUCTION_VERIFIED`.

Production deployment completed successfully from recovered baseline `e12fdaf281f7e08013e54c7cf936f8275127ab2b` to exact GitHub commit `7d0b3df03c3657106ebaf86d5f9123ba262495a5` using `scripts/host/phase50_a2f_storefront_production_deploy.sh`.

Verified Host evidence: MySQL `sfkilvrs_EmiAdmin_3dprinthub`; required Store 0036–0042 + Website 0024 migrations present; migration plan empty before and after promotion; publish-readiness ready=true with no blockers; verified source/.env/static backup at `/home/sfkilvrs/3dprinthub-deploy-backups/20260912-182234-phase50-a2f-storefront`; ff-only Git promotion; collectstatic; Passenger restart; Home/Store/Bridge health/readiness/new JS/new CSS all HTTP 200; final Host worktree clean.

Guided customer ordering is now live on Production: size → color → compatible material → print quality → canonical ProductVariant → server-authoritative price/stock/weight/time → cart. Native Variant select remains fallback.

Next exact acceptance: one controlled Product publish from Windows Catalog Center to the now-ready receiver, verify Product/Profile/Variant/images/public Store/strict ACK, then enable bounded multi-product publish. In parallel continue Phase50 finance/payment/admin work after this Product-publish acceptance.
## 2026-09-12 ? ERR-49-116 cPanel shell-exit behavior identified

The A2F failure did not indicate a network drop. Directly enabling `set -Eeuo pipefail` in the parent cPanel interactive shell caused the shell itself to exit when the guarded child deploy returned nonzero. Future Host bootstrap blocks isolate strict mode in a subshell so fail-closed deployment errors leave the operator Terminal connected. ERR-49-115 allowlist fix is pushed; Production remains on the unchanged recovered baseline pending safe retry.

## 2026-09-12 ? A2F first Production attempt stopped safely at reviewed-delta guard

Status: `PRODUCTION UNCHANGED / ERR-49-115 FIX LOCAL-TESTED / COMMIT+PUSH NEXT`.

The first cPanel A2F attempt reached the exact target-delta inspection and stopped with `unexpected_target_delta:PROJECT_CONTEXT.md`. This is a deploy-runner allowlist omission, not a terminal/network disconnect. The stop occurred before source promotion and before any database action; recovered Production baseline remains `e12fdaf281f7e08013e54c7cf936f8275127ab2b`. The fix is narrowly scoped to accepting root `PROJECT_CONTEXT.md` while preserving fail-closed behavior for every other unexpected target path.

## 2026-09-12 — Production recovery live-verified + Phase50.A.2F deploy gate ready

Status: `PRODUCTION 3I.53G VERIFIED COMPLETE / LOCAL+GITHUB 2F PASS / NO-MIGRATION DEPLOY RUNNER LOCAL-TESTED / COMMIT+PUSH NEXT`.

Repository: `farazha2203/3dprinthub`; branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`. Local and live GitHub were reverified clean at `38458ceee351add5db4bb4e84c5f1980e86bd5b5`; the canonical Windows gate then passed on that exact SHA with 139 + 34 + 68 tests, Playwright Chromium smoke, Qt/Legacy verify and a checksum-identical Catalog SQLite backup.

Production was re-audited from the live system rather than trusting the stale 2026-09-02 documentation. Explicit FTPS to the cPanel account succeeded over TLS. Production Git metadata shows branch `agent/phase49-3i18-operator-bulk-ai-rebuild` at `e12fdaf281f7e08013e54c7cf936f8275127ab2b`. The Host copy of corrected Store migration 0039 and `phase49_3i53_partial_0039_resume.sh` is byte-identical to Repository source. A 53G current-partial backup exists at `/home/sfkilvrs/3dprinthub-deploy-backups/20260910-131314-phase49-3i53g-partial`, and Passenger restart evidence is dated 2026-09-10 13:13:48.

The authenticated live Bridge proves recovery completion: health HTTP 200/status ok; publish-readiness HTTP 200 with `ready=true`, `blockers=[]`, MySQL vendor, 13 active Materials and 5 active PrintQualities. Store migrations 0036–0042 and Website 0024 are all reported applied, and all required receiver tables/columns are present. Therefore the old “partial 0039 recovery still pending” sections below are historical and must not be used as the current execution state.

Phase50.A.2F introduces no migration or dependency. Repository runner `scripts/host/phase50_a2f_storefront_production_deploy.sh` now guards exact Production baseline `e12fdaf...`, clean worktree, live GitHub target/FETCH_HEAD, empty migration plan and ready receiver; creates verified source/environment/static backups; permits only the reviewed 2F/docs/test/deploy-runner delta; performs ff-only deploy, collectstatic, Passenger restart, collected-static hash verification and public/Bridge/static HTTP verification. It contains no `manage.py migrate` command.

Exact next: review diff → rerun focused Storefront + deploy-runner syntax/contract gates → commit/push → verify remote SHA → execute the no-migration runner from cPanel shell only after its clean-host guard passes → Production browser/Product configurator verification → update docs with deployed SHA and backup path.

## 2026-09-12 — Phase50.A.2F guided Storefront configurator Local PASS

Status: `LOCAL DIRTY DELTA INSPECTED / GUIDED CONFIGURATOR AUTOMATED GATES PASS / COMMIT+PUSH NEXT / PRODUCTION 3I.53G RECOVERY STILL BLOCKING GENERIC DEPLOY`.

Repository: `farazha2203/3dprinthub`
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Verified pre-commit Local/remote HEAD: `e12fdaf281f7e08013e54c7cf936f8275127ab2b`.

The recovered Local worktree contained an intentional unfinished Storefront configurator delta rather than disposable changes. It progressively enhances the canonical Variant selector into size → color → compatible material → print quality, preserves the native selector as fallback, resolves only real orderable ProductVariants, and delegates final cart/price handoff to the mature Store listener.

Verification on the actual Windows checkout: Node guided state 8/8 PASS; focused Django Profile/Filament tests 15/15 PASS; isolated Playwright browser regression PASS on desktop/mobile/cart/fallback/stock/ambiguity/>100 Variant batching; Django check PASS with the known CKEditor warning; migration drift = none. No Local Django migration was applied by this work.

Parallel Windows Catalog Center remains at the repository 49.3I.52G contract until the canonical clean-head Local gate is rerun after this Storefront delta is committed. Production must not receive a generic pull: the last documented Host state is the 3I.53G partial MySQL 0039 recovery boundary and must be freshly read-only verified before any Host mutation.

Exact next: commit/push this tested 2F delta → verify remote SHA → run clean-head Windows Local gate → read-only Host reality audit → only then choose the guarded 3I.53G recovery/deploy path.
## 2026-09-02 — Phase49.3I.53G MySQL 0039 partial-migration recovery ready

Status: `PRODUCTION SOURCE=5f6c13ab / DB PARTIALLY MIGRATED / RECOVERY IMPLEMENTED + REAL MYSQL PROBE PASS / HOST RECOVERY NEXT`.

Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Production source HEAD from owner evidence: `5f6c13ab879558cb66db3e316e0522c5e5783ae0`.  
Exact tested recovery code: `66e940e6e659f86e3783d78d091b3ff00acbf5aa`.  
Pre-fix rollback branch: `backup/pre-phase49-3i53g-mysql-partial-0039-recovery-20260902` → `5f6c13ab879558cb66db3e316e0522c5e5783ae0`.

### Production evidence from owner
Phase49.3I.53F successfully:
- reverified the original pre-migration rollback set;
- fast-forwarded source to `5f6c13ab...`;
- proved Django can boot before httpx;
- installed and verified `httpx==0.28.1`;
- verified DB was still pre-migration;
- created and verified fresh pre-migration MySQL backup:
  `/home/sfkilvrs/3dprinthub-deploy-backups/20260902-212529-phase49-3i53-resume/database-before-3i53.sql.gz`;
- required the exact seven-migration plan.

Migration execution then produced:
- `website.0024_phase49_3i51_material_catalog_description` → OK;
- `store.0037_phase50_professional_commerce_policy` → OK;
- `store.0038_phase50_profile_matrix` → OK;
- `store.0039_phase50_filament_offer_pricing` → STOPPED with MySQL 1060 duplicate column `support_weight_grams`.

Because the failure occurred inside 0039:
- 0039 is not recorded as applied;
- 0040–0042 are not applied;
- collectstatic was not run;
- Passenger was not restarted;
- final public/Bridge readiness verification did not run.

### Root cause
Repository history proves `ProductVariant.support_weight_grams` was already created by `store.0033_phase49_3f_pricing_intelligence`. Migration 0039 incorrectly attempted a second `AddField` for the same database column.

This corrects the incomplete historical wording in ERR-50-016: 0039 was the intended later metadata contract, but it was not the original database-column creator; 0033 had already created the physical ProductVariant column.

On MySQL, DDL operations inside a migration are not reliably rolled back as one transaction. The 0039 operations preceding the duplicate-column failure may therefore remain physically present even though 0039 is not recorded. Recovery must inspect the exact schema before continuing.

### Recovery implementation
`store/migrations/0039_phase50_filament_offer_pricing.py` now:
- uses `AddFieldIfMissing` for the genuinely new 0039 columns so a persisted prefix from a failed MySQL run is safely recognized;
- changes ProductVariant `support_weight_grams` to `AlterField`, preserving state/metadata without trying to create the already-existing 0033 column again;
- keeps StoreOrderItem support/brand/manufacturer fields as idempotent adds.

Dedicated Host runner:
`scripts/host/phase49_3i53_partial_0039_resume.sh`.

Before any new DB mutation it:
1. requires current Host source exactly `5f6c13ab...` and clean worktree;
2. re-verifies both valid pre-migration backups;
3. verifies migration recorder is exactly the observed partial state;
4. introspects the 0039 schema shape and stops if it differs from the observed failure boundary;
5. creates a third fresh MySQL backup of the CURRENT PARTIAL state;
6. verifies live GitHub target + fast-forward ancestry + corrected 0039 contract;
7. ff-only applies source fix;
8. requires exact remaining plan 0039–0042;
9. migrates, verifies receiver readiness, collectstatic, Passenger restart, public Store and authenticated Bridge/readiness HTTP.

### Verification
- migration/recovery implementation commit: `bec98fc5a5e40ed534364cc3eb1047759c2a3cdc`;
- Variant/Profile CI `33664796042` PASS on the same migration implementation;
- final Product Admin workflow `33666085743` PASS:
  - main Product Admin job PASS;
  - 56 focused/site tests PASS;
  - SQLite migration through Store 0042 PASS;
  - real MySQL focused `AddFieldIfMissing` probe PASS:
    - `MYSQL_ADDFIELD_EXISTING_COLUMN_SKIP=PASS`;
    - `MYSQL_ADDFIELD_MISSING_COLUMN_ADD=PASS`;
    - `MYSQL_ADDFIELD_PROBE=PASS`;
    - `PHASE49_3I53G_REAL_MYSQL_ADDFIELD_PROBE=PASS`;
- final Single Active AI `33666085841` PASS.

### CI investigation notes
Two broad from-zero MySQL attempts crossed unrelated historical schema incompatibilities before reaching 0039:
- third-party `sb_admin_audit.0001` indexed TEXT/BLOB;
- old `store.0009` key length > MySQL 3072 bytes.
Those are not the current Production state and were not used as evidence for 0039. The test strategy was narrowed to a real MySQL probe of the exact custom AddField operation.
The first focused probe also had two harness-only issues (numeric migration module import syntax, then script-root import path); both conditions were changed and the final real MySQL probe passed.

### Exact next task
Do NOT rerun the 53F resume command. Run the 53G partial-0039 recovery runner from the current Host source `5f6c13ab...`. If its read-only schema forensics does not exactly match the expected failure boundary, it will stop before mutation and the output must be reviewed. If it passes, it creates a fresh partial-state DB backup before applying the corrected 0039–0042 chain.

## 2026-09-02 — Phase49.3I.53F Production source is promoted; DB migration paused on missing Host dependency

Status: `SOURCE DEPLOYED TO b372 / DB MIGRATIONS NOT RUN / COLLECTSTATIC NOT RUN / PASSENGER NOT RESTARTED / RECOVERY FIX CI PASS / RESUME NEXT`.

Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Current Production source HEAD from owner evidence: `b372586ab60234ec3faf3ce0624e07766db6ecce`.  
Production DB remains pre-migration: Store 0036 + Website 0023 applied; Store 0037–0042 + Website 0024 still pending.  
Verified pre-migration rollback backup: `/home/sfkilvrs/3dprinthub-deploy-backups/20260902-211013-phase49-3i53`.

### Owner deploy evidence
The third deploy attempt successfully:
- verified clean Host baseline `198fa8e...`;
- fetched target `b372586a...`;
- verified exact seven-file migration delta;
- verified MySQL/database baseline;
- created source bundle;
- created a real gzip MySQL backup;
- passed `gzip -t`;
- passed SHA256 checks for source bundle, database, .env and pending import tar;
- printed `PREDEPLOY_BACKUP_VERIFIED=YES`;
- fast-forwarded Production source to `b372586a...`.

It then stopped immediately at the first post-merge Django check with:
`ModuleNotFoundError: No module named 'httpx'`.

Therefore:
- source promotion HAS happened;
- database migrations have NOT happened;
- collectstatic has NOT happened;
- Passenger restart has NOT happened.

### Root cause
`requirements.txt` gained the exact new Production dependency `httpx==0.28.1`, but the original deploy runner did not reconcile target Python dependencies before executing target Django code. In addition, Site AI modules eagerly imported desktop provider transport during Django startup, so a missing optional AI transport dependency could block the entire Site startup path.

### Recovery implemented
- `ai.model_policy` now keeps provider transport lazy;
- `ai.product_content` now imports `AIContentService` only when an operator explicitly runs AI Generate;
- mature `ai.model_policy.AIProviderClient` patch seam is preserved through a lazy compatibility constructor;
- new regression proves `django.setup()` succeeds while `httpx` is deliberately unavailable;
- main deploy runner now installs/verifies exact target `httpx==0.28.1` after verified rollback backup and before target source execution;
- new `scripts/host/phase49_3i53_postmerge_resume.sh` safely resumes from the already-promoted `b372586a...` source state;
- resume runner re-verifies the existing valid rollback backup, fast-forwards only to the current GitHub target, proves boot safety before installing httpx, installs exact dependency + `pip check`, verifies DB is still pre-migration, creates a fresh pre-migration MySQL backup, requires the exact seven-migration plan, then migrates/collects static/restarts/verifies public + Bridge readiness.

### Verification
- first 53F Product Admin run `33663092964` failed because a mature test patched `ai.model_policy.AIProviderClient`, a compatibility symbol removed by the first lazy-import refactor;
- the failed condition was changed: the patch seam is restored as a lazy constructor, without restoring eager transport import;
- final Product Admin / Host recovery CI `33663316332` PASS;
- final Single Active AI `33663316324` PASS;
- recovery code checkpoint `ccd1b98997a8dd0c8389ccbe2b6c78b83dd7f176`.

### Safety / rollback
- verified source bundle still represents predeploy `198fa8e...`;
- verified MySQL dump from 21:10 remains valid pre-migration rollback evidence;
- GitHub rollback branch `rollback/phase49-3i53-predeploy-host-198fa8e-20260902` remains available;
- current-source rollback branch `rollback/phase49-3i53-postmerge-b372-before-deps-20260902` records the exact source state at which deployment paused;
- no automatic reverse migration is required because no new migration has run yet.

### Exact next task
Run the repository post-merge resume runner from current Host HEAD `b372586a...`. Do not rerun the old deploy runner, because its required starting baseline is no longer true. The resume must reach: rollback reverified → Django boot-safe without httpx → exact httpx install → fresh MySQL backup verified → exact migration plan → migrate → receiver readiness → collectstatic → Passenger restart → public/Bridge verification.

## 2026-09-02 — Phase49.3I.53E extracted backup helper project-root binding

Status: `GITHUB_UPDATED / BACKUP HELPER FIX CI PASS / PRODUCTION STILL AT VERIFIED BASELINE / DEPLOY RETRY NEXT`.

Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Verified Host baseline remains `198fa8e41ea4f4d87eb287ba69c91076acc78d62`.  
Current fix checkpoint: `2016b84ee1b053e792ceb44ede516b3d7a2dea7e`.

### Owner deploy attempt evidence
The corrected gzip helper was extracted from GitHub into the timestamped backup directory and executed from there. It failed before backup verification with:
`ModuleNotFoundError: No module named 'config'`.

The runner had not printed `PREDEPLOY_BACKUP_VERIFIED=YES`, therefore it had not ff-merged source, run migrations, collectstatic, or restarted Passenger. Production remains at the verified baseline.

### Root cause
Python sets `sys.path[0]` to the directory containing the executed script. Because the helper is intentionally copied into `/home/sfkilvrs/3dprinthub-deploy-backups/<timestamp>/`, the Production project root was not importable as `config` even though the shell working directory was the correct repository.

### Fix
- helper now requires `PHASE49_PROJECT_ROOT`;
- verifies `manage.py` and `config/__init__.py`;
- inserts the verified project root at `sys.path[0]` before importing Django;
- deploy runner passes `PHASE49_PROJECT_ROOT="$ROOT"` explicitly;
- self-test now covers project-root resolution/sys.path binding in addition to gzip round-trip.

### Verification
- Product Admin / deploy-helper CI `33661199115` PASS;
- Single Active AI `33661199159` PASS;
- `config/__init__.py` verified present at the approved target.

### Backup safety
The failed `20260902-204716-phase49-3i53` directory is evidence only; its MySQL backup did not complete and must not be used as restore evidence. The retry must create a new timestamped backup root and must reach `DATABASE_BACKUP_GZIP=VALID` and `PREDEPLOY_BACKUP_VERIFIED=YES` before source promotion.

### Exact next task
Retry the repository deploy runner from Host baseline `198fa8e...` against the current live GitHub target. Do not repeat the previous target/runner unchanged. Stop on any new error and preserve full output.

## 2026-09-02 — Phase49.3I.53D MySQL backup gzip boundary fixed before Production promotion

Status: `GITHUB_UPDATED / BACKUP FIX CI PASS / PRODUCTION STILL AT VERIFIED BASELINE / DEPLOY RETRY NEXT`.

Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Verified Host baseline remains `198fa8e41ea4f4d87eb287ba69c91076acc78d62`.  
Current backup/deploy fix checkpoint: `3b6254bf7700bb26b4af63d21e31e56e7700877c`.

### Owner deploy attempt evidence
The first 3I.53C Production runner correctly passed repository/branch/HEAD/live-target/fast-forward/migration-delta/MySQL-state/Django checks and created the source bundle. It then created:
`/home/sfkilvrs/3dprinthub-deploy-backups/20260902-203857-phase49-3i53/database-before-3i53.sql.gz`
with size 17,469,650 bytes, but `gzip -t` reported `not in gzip format`.

The runner stopped immediately at this backup-verification boundary. It did **not** print `PREDEPLOY_BACKUP_VERIFIED=YES`, did **not** ff-merge source, did **not** migrate, did **not** collectstatic and did **not** restart Passenger. Production therefore remains at the verified baseline.

### Root cause and fix
Passing a Python `gzip.GzipFile` object directly as `subprocess.run(..., stdout=target)` is unsafe: subprocess uses the underlying file descriptor and writes raw mysqldump bytes directly to the file, bypassing Python gzip encoding. The file had a `.gz` suffix without an actual gzip stream.

The deploy runner now extracts a repository-owned helper `scripts/host/phase49_3i53_mysql_backup.py` from the exact fetched target. The helper:
- starts mysqldump with `stdout=PIPE`;
- streams stdout through Python's gzip encoder with `shutil.copyfileobj`;
- redirects stderr to a private temporary file so pipe buffering cannot deadlock;
- fails closed on mysqldump error;
- verifies gzip magic and mysqldump payload signature before returning success;
- the shell runner still performs full `gzip -t` and SHA256 verification before source promotion.

### Verification
- intermediate self-test run `33659570675` failed because the synthetic 2MB fixture was embedded directly in one command-line argument and exceeded Linux argv size; this was a test-fixture error, not the Production backup algorithm;
- the failed condition was changed: the child now generates the fixture internally with a bounded command line;
- final Product Admin/backup-contract CI `33659707983` PASS;
- final Single Active AI `33659707957` PASS;
- helper self-test now proves gzip round-trip and mysqldump header validation.

### Backup safety
The failed 20260902-203857 backup directory is retained as evidence and its `database-before-3i53.sql.gz` must **not** be used as a MySQL restore artifact because it is not gzip. A retry creates a fresh timestamped backup root and must reach `PREDEPLOY_BACKUP_VERIFIED=YES` before any merge/migration.

### Exact next task
Re-run the current repository deploy runner from the live GitHub target while Host HEAD is still `198fa8e...` and worktree is clean. Do not reuse the old failed backup directory. Stop on any new failure; if successful, require final authenticated receiver readiness and then publish exactly one Product end-to-end before bulk publishing.

## 2026-09-02 — Phase49.3I.53C Production receiver deploy prepared after clean Host audit

Status: `GITHUB_UPDATED / HOST READ-ONLY AUDIT PASS / BACKUP+DEPLOY RUNNER CI PASS / PRODUCTION DEPLOY NEXT`.

Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Deploy-runner code checkpoint: `5c5f087ae26e78c106984cf3c92e9b322537f203`.  
Verified current Host baseline: `198fa8e41ea4f4d87eb287ba69c91076acc78d62`.  
Rollback GitHub branch: `rollback/phase49-3i53-predeploy-host-198fa8e-20260902` → `198fa8e41ea4f4d87eb287ba69c91076acc78d62`.

### Host audit accepted
Owner audit completed with:
- tracked Production worktree/index CLEAN after preserving old `ls-output.txt` outside the repo;
- Host HEAD `198fa8e...` is an ancestor of the approved GitHub branch;
- Production Python `3.12.13`, Django `6.0.7`;
- MySQL vendor and exact DB `sfkilvrs_EmiAdmin_3dprinthub`;
- `manage.py check` with only known warnings;
- `makemigrations --check --dry-run`: no model drift;
- actual Production migration state: Store `0036` applied, Website `0023` applied;
- pending receiver chain: Store `0037..0042` plus Website `0024`;
- active Materials: 13; active PrintQualities: 5;
- effective writable paths: Static `/home/sfkilvrs/public_html/static`, Media `/home/sfkilvrs/3dprinthub/media`, Private Media `/home/sfkilvrs/3dprinthub/private_media`, pending imports `/home/sfkilvrs/3dprinthub/imports/desktop_catalog/pending`;
- Bridge token configured (length 64, value not printed);
- disk: 531G available / 37% used; inode usage 15%;
- `mysqldump 8.0.45` available.

The old-source `migrate --plan` reported no operations because that checked-out baseline contains only migrations through Store 0036/Website 0023. The deployment runner therefore validates the exact migration-file delta again after fetching the approved target and validates the exact Django MigrationExecutor plan after ff-only source promotion.

### Deploy runner
Repository runner: `scripts/host/phase49_3i53_production_deploy.sh`.

It fails closed unless:
- current Host HEAD is exactly `198fa8e...`;
- worktree is clean;
- live GitHub SHA equals the supplied target;
- target is a fast-forward descendant;
- migration-file delta is exactly Store 0037–0042 + Website 0024;
- baseline DB migration recorder is unchanged.

Before source promotion it creates and verifies:
- Git bundle source backup;
- private `.env` backup when present;
- pending-import tar backup when present;
- gzip MySQL dump using the effective Django DB credentials without printing the password;
- SHA256 manifest checks.

After backup verification it performs:
ff-only merge → Django check/model-drift gate → exact MigrationExecutor-plan gate → `migrate --noinput` → in-process publish-readiness check → `collectstatic --noinput` → Passenger restart → Django check → authenticated public Bridge health/readiness + home/store HTTP verification.

No automatic destructive rollback is attempted on a migration/runtime failure; the verified Git bundle/MySQL dump and rollback branch are preserved for diagnosis/controlled restore.

### Verification
- deploy-runner syntax/contract + Product Admin CI `33658713537` PASS;
- Single Active AI `33658713594` PASS.

### Known warnings
- CKEditor4 unsupported/security-debt warning remains known and is not new to this deploy;
- in-memory realtime channel-layer warning remains known; Redis is a separate architecture task;
- MySQL conditional unique-constraint warnings are known platform limitations.

### Exact next task
Execute the repository deploy runner from the live GitHub target. Do not manually run migrations or edit Production source. Preserve the full output. If it reaches `PHASE49_3I53C_PRODUCTION_DEPLOY=PASS`, then run one controlled Catalog Center Product publish and verify Product page + images + strict ACK before widening to bulk publish.

## 2026-09-02 — Phase49.3I.53B Host baseline correction before receiver audit

Status: `GITHUB_UPDATED / SITE CI PASS / AUDIT RUNNER FIX PASS / HOST FORENSICS PARTIAL / PRODUCTION NOT CHANGED BY THIS PHASE`.

Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Current code checkpoint: `d0984e1f9e01d959c028d2714c4814b6556acd84`.  
Rollback: `backup/pre-phase49-3i53b-host-audit-baseline-fix-20260902` → `eb03396a926a0b99d22a880c17c8a39d55e684d4`.

### New Host evidence
Owner read-only Host output proved:
- root `/home/sfkilvrs/3dprinthub`;
- origin `https://github.com/farazha2203/3dprinthub.git`;
- branch `agent/phase49-3i18-operator-bulk-ai-rebuild`;
- actual Host HEAD `198fa8e41ea4f4d87eb287ba69c91076acc78d62`;
- tracked worktree unchanged and index unchanged;
- one untracked file `ls-output.txt`, 1,153,478 bytes / 20,891 lines, SHA256 `8e01c07fcdf242fdc9be7de5a3a9b86cd7f0244e37ace629bc22d10ac1bee738`, mtime 2026-08-27;
- system `python3` command is unavailable in the login shell.

GitHub ancestry verification proved `198fa8e...` is 23 commits ahead of the previously documented `c283864...` and remains an ancestor of the current target branch. Therefore the old documented Production HEAD was stale and must not be used for reset/rollback.

### Fix
The repository audit runner no longer hardcodes `c283864...`. It now requires the operator-verified current Production HEAD as its second argument and still requires the live GitHub target as its first argument. The runner continues to use the documented Production venv Python `/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python`, not `python3`.

### Verification
- Phase50 Product Admin / audit contract run `33656829478` PASS;
- Single Active AI `33656829551` PASS;
- shell syntax and explicit two-argument baseline contract PASS.

### Exact next task
Use Production venv Python to inspect only metadata/secret markers of `ls-output.txt` without printing its contents. If safe, move the file reversibly to a Host evidence directory outside the repo and verify its SHA256 unchanged. Then run the updated repository-owned read-only audit with:
1. live GitHub target resolved by `git ls-remote`;
2. verified Host baseline `198fa8e41ea4f4d87eb287ba69c91076acc78d62`.
Do not migrate/deploy until that audit output is reviewed.

## 2026-09-02 — Phase49.3I.53 Site publish receiver readiness + Host audit gate

Status: `GITHUB_UPDATED / SITE CI PASS / WINDOWS QT PASS / PORTABLE PASS / HOST READ-ONLY AUDIT NEXT / PRODUCTION NOT TOUCHED`.

Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Exact final code checkpoint: `62ce5c3393a888cc1a027e4ca6bbb88f189bc845`  
Pre-phase rollback: `backup/pre-phase49-3i53-site-publish-readiness-20260902` → `088379adb6e17d589c3e18a1a296a39ef7cf6aba`.  
Last verified Production application: `c283864290f9c989a9fcdf24ee8eef519560e917`.

### Requested delta
With Windows Product/Crawl recovery usable enough for the moment, move the active work to Site/Host so Catalog Center can publish Products safely to the real website.

### Implemented
- authenticated Bridge endpoint `/api/catalog-bridge/v1/publish-readiness/`;
- receiver readiness checks the live Django migration recorder, required schema columns, Bridge-token presence, pending import storage, media storage and active Material/PrintQuality prerequisites;
- Desktop bulk publish calls receiver readiness before revision guard, package build or FTP; blocked Host state cannot receive a batch;
- Settings Bridge test now reports Bridge health separately from receiver publish readiness;
- pre-deploy compatibility: if an older Site has Bridge health but no readiness endpoint yet, Settings reports receiver blocked instead of treating Bridge itself as disconnected;
- mature publish path after readiness remains unchanged: Ready Product → Batch v8.5 → FTP → authenticated Bridge import → canonical Product/Profile/Variant → public Store/media verification → ACK;
- no second Product database and no bypass around publish visibility/commerce gates;
- repository-owned Production read-only audit added at `scripts/host/phase49_3i53_production_readonly_audit.sh`;
- audit verifies exact root/repository/current HEAD/live GitHub target, clean worktree, Python/Django, MySQL vendor/name, Django check, migration drift/plan, effective storage paths, Bridge-token configured state without printing the secret, active Material/PrintQuality counts, schema evidence, disk/inodes and mysqldump availability;
- audit explicitly performs no fetch/merge/migrate/collectstatic/restart.

### Database truth
No new migration was introduced by 3I.53. Production is still last-verified only through Store `0035`; the receiver needs the already-reviewed chain `store.0036..0042` plus `website.0024` before readiness can become true. These migrations include additive fields/tables plus existing controlled data migrations in 0037/0041/0042, so a fresh verified MySQL backup remains mandatory before apply.

### Verification
- Site/Product Admin `33652584032` PASS, including new receiver endpoint tests and full migration apply in isolated CI;
- Variant/Profile Matrix `33652583964` PASS;
- audit-script syntax/contract + Site suite `33652996666` PASS;
- final Single Active AI `33653229219` PASS;
- final Qt/full parity `33653229142` PASS;
- final Windows Portable `33653229400` PASS;
- Portable regression: 235 tests PASS;
- artifact `9855771656`;
- EXE SHA256 `a6bebd3c10a56aac1c65a58d5ffb1029382e98c7b0782a4b034a315e60c2f1ed`.

### Error resolved
ERR-49-104: the first 3I.53 Qt run correctly exposed that the historical Bridge-only fixture mocked Bridge health but not the newly added readiness request, causing a real 404. Runtime was hardened so old Site health remains distinguishable from missing readiness, and the fixture now mocks both intentional calls. Final Qt/Portable gates PASS.

### Safety
- Production source: untouched;
- Production MySQL: untouched;
- migrations on Host: not run;
- media/import storage: not modified;
- no secret printed or committed;
- no deploy will start until fresh Host read-only evidence is reviewed.

### Exact next task
Run the repository-owned read-only Host audit against the exact live GitHub target. Review actual Production HEAD, branch, worktree, MySQL DB, `showmigrations`, `migrate --plan`, storage, prerequisites, disk and mysqldump. Only after that evidence is clean: create fresh source/environment/MySQL backups, verify checksums/non-empty dump, then perform an ff-only GitHub deploy and only the audited migration chain.

## 2026-09-02 — Phase49.3I.52G adaptive acquisition recovery

Status: `GITHUB_UPDATED / WINDOWS QT CI PASS / SINGLE ACTIVE AI PASS / WINDOWS PORTABLE PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT TOUCHED`.

Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Exact tested runtime: `bf1fafdb38233a23e13a5715ffac72f772412005`  
Rollback: `backup/pre-phase49-3i52g-adaptive-acquisition-observability-20260902` → `aa5ae5c9ff859b6fcd7630ef11b29254b7e2bcf3`.  
Catalog Center: `8.9.10` / build `2026.09.02.1`; Qt marker: `Phase49.3I.52G`.

Owner QA showed MakerWorld identities were discovered into Crawl but full Product recovery could still fail with no image. 52G now separates discovery from Product success, writes redacted per-method acquisition JSONL, validates meaningful Product data and real local-image evidence, tries distinct mature acquisition methods in order, promotes the successful method for later Products, and stops the selected batch after one Product exhausts all real methods instead of cascading failures.

Implemented methods: rich extractor, network capture, classic exact browser, public HTTP, attached Chrome; mature resilient image fallback is reused when page data exists but image acquisition leaves no local file. Invalid Product URL/source also triggers the circuit breaker. Existing operator Persian content, pricing, approval, publish state and mature Source Refresh behavior remain protected.

Verification:
- Qt/Crawl runtime CI `33644903042` PASS;
- dedicated Crawl/recovery suite 27 PASS;
- Single Active AI `33644902970` PASS;
- Windows Portable `33644902962` PASS;
- Portable regression 235 PASS;
- artifact `9852476786`;
- EXE SHA256 `f3e0bce9e5d3b40317b5fd37cff8a5fc6ff1d5a2cef6f5b1bf84dc6f6699c310`;
- EXE self-verify/browser smoke/hash gate PASS.

Errors fixed during implementation: ERR-49-102 restored accidentally removed Preview/refetch helpers; ERR-49-103 restored mature `qt46-legacy-*` identity and Source Refresh history after regression caught drift.

Safety: no Django/Catalog migration, no destructive media operation, no Host source change, no Production deploy, Production MySQL untouched.

Next: clean Local ff-only sync, canonical checksum-backed Local gate, then bounded foreground recovery of 2–5 previously failed MakerWorld rows and inspection of `logs\acquisition` only if a live failure remains.

## 2026-09-02 — Phase49.3I.52F bulk recovery for incomplete Crawl Products

Status: `GITHUB_UPDATED / WINDOWS QT CI PASS / SINGLE ACTIVE AI PASS / WINDOWS PORTABLE PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT TOUCHED`.

Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Exact tested runtime: `cf73f841418aac2eec1b78e0dbd682ceb2d3fef5`  
Rollback: `backup/pre-phase49-3i52f-bulk-recover-incomplete-20260902` → `f35bd3e409c4293a756ddfe2fc9d4f7dcb968445`.  
Catalog Center: `8.9.10` / build `2026.09.02.1`; Qt shell marker: `Phase49.3I.52F`.

### Owner request
The permanent Crawl inventory must be actionable even when a row has no usable title, description or image. The operator must be able to select many rows (for example 100), choose a target image count such as 5 or 10, and run one recovery operation. Existing local/database evidence should be reused first; incomplete records should be re-read from the original Product URL without opening each Product manually.

### Mature behavior reviewed
The previous Tk application already had `bulk_refetch_selected()`: selected Products were re-read from their source, downloaded images were refreshed, and `merge_refetch()` preserved human/operator edits. 3I.52F extends that mature safety contract into Qt Crawl inventory instead of inventing a parallel recovery path.

### Implemented
- permanent Crawl inventory has `انتخاب ناقص‌ها`;
- loaded rows lacking a Product, meaningful title/description, or local image are selected in one action;
- permanent inventory has a dedicated image target selector: 5 / 10 / 20;
- permanent inventory has `بازیابی دیتا + عکس`;
- controls are split into selection row + data-action row to avoid the crowded toolbar;
- `بازیابی` status action was renamed `بازگردانی به صف` so it is not confused with Product data recovery;
- recovery reuses existing local files without network when Product data is already complete and local image count meets the requested target;
- incomplete existing Products are force-refetched through the safe source recovery merge, preserving operator Persian content, final price, approval and publish state;
- orphan Crawl identities whose ledger says already collected but whose Product row is missing can be explicitly recovered from the original Product URL;
- rejected/blocked Product safety remains enforced: blocked Products are not silently revived by source recovery;
- Product URL slug is used as a readable fallback title before full receive; owner example `2953550-japandi-small-key-tray` displays `japandi small key tray` instead of an opaque id-only card;
- recovery progress reports queue id, item index/total and child image/data progress;
- no model/STL file download is triggered by this action; scope is Product data + images.

### Verification
- `33637452385` — Qt full parity PASS;
- dedicated 3I.52 visual/recovery suite: 19 tests PASS;
- explicit PASS: URL-slug identity before full receive;
- explicit PASS: incomplete-row selection;
- explicit PASS: complete local Product skips network;
- explicit PASS: incomplete existing Product uses forced safe source refetch with selected 10-image target;
- explicit PASS: orphan terminal ledger can be explicitly recovered;
- `33637452588` — Single Active AI PASS;
- `33637452243` — Windows Portable PASS;
- Portable release regression: 227 tests PASS;
- artifact id `9849484898`;
- EXE SHA256 `f0150359fd36c7ead84599ccd0b799797ed48e85e4c6eac1d191abc3f0315a64`;
- EXE self-verify and browser smoke PASS.

### Errors resolved during implementation
- ERR-49-100: first portable regression exposed a missing `QMessageBox` import in the new test fixture; import was added before rerun.
- ERR-49-101: next regression proved the mocked `run_single` lifetime ended before the captured Worker executed; fixture scope was corrected before final rerun.
- neither failed condition was rerun unchanged.

### Safety
- no Django migration;
- no Catalog migration;
- no destructive media operation;
- no direct Production/Host change;
- Production MySQL untouched;
- explicit source recovery remains robots-aware and sequential, not an aggressive parallel crawler.

### Exact next task
1. owner closes the currently running Catalog Center;
2. clean ff-only Local sync to the live GitHub branch;
3. run canonical Local gate with dynamic live HEAD and relaunch;
4. sidebar must report `Phase49.3I.52F`;
5. in permanent Crawl inventory, filter/load the target rows and click `انتخاب ناقص‌ها`;
6. choose 5 or 10 images, click `بازیابی دیتا + عکس`;
7. verify external id `2953550` becomes a readable Product with source title/description and requested images without manually opening its URL;
8. verify a Product already complete with enough local images is reported as local reuse rather than downloaded again;
9. Production remains blocked until owner Local acceptance.

## 2026-09-02 — Phase49.3I.52E Crawl preview recovery + mature refetch-folder image parity

Status: `GITHUB_UPDATED / WINDOWS QT CI PASS / SINGLE ACTIVE AI PASS / WINDOWS PORTABLE PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT TOUCHED`.

Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Exact tested runtime: `016e84ab98d2e5577633833cbc87cb96824dbbf0`  
Rollback: `backup/pre-phase49-3i52e-preview-legacy-variants-20260902` → `ef82abe775f88f6326c345b4e17c797471acbc27`.  
Catalog Center: `8.9.10` / build `2026.09.02.1`; Qt shell marker: `Phase49.3I.52E`.

### Owner QA evidence and clarified behavior
The owner screenshots show two different image states inside permanent Crawl inventory:
- rows such as external ids `2786975` and `2533481` already expose 5 local images;
- many recent rows are still `new` and show no Preview;
- several old/failed rows also have no visible image even though mature refetch flows may have written files to sibling refetch folders.

A `new` Crawl row is only discovered identity until full Product receive runs. It can still show a lightweight listing Preview, but that Preview depends on the listing DOM exposing a usable public image URL. Full local image count must only be claimed when real files exist.

### Additional root causes verified from mature source
The retained Tk runtime uses additional historical Product image folders:
- `<external_id>_refresh_latest`;
- `<external_id>_refetch_<timestamp>`;
- `<external_id>_bulk_refetch_<timestamp>`.

3I.52D only covered the exact `<external_id>` folder, so unlinked Crawl rows could still miss images stored in those mature sibling folders.

MakerWorld listing thumbnails can also be lazy-loaded through `srcset`, `picture/source srcset`, `data-src`, `data-original`, `data-lazy-src`, or CSS background-image. The Preview parser previously relied mainly on currentSrc/src/data-src and could therefore persist an empty candidate thumbnail even though the card was visibly imaged in the browser.

### Implemented
- read-only identity image lookup now includes exact Product folder plus mature `_refresh_latest`, `_refetch_*`, and `_bulk_refetch_*` siblings;
- newest refetch variants are evaluated first after exact/local_dir authority;
- no media file is moved, renamed, deleted or rewritten;
- queue selected-row Product lookup is source-code case-insensitive too;
- listing Preview extraction now preserves multiple lazy-image attributes and chooses a real HTTP image rather than stopping on data/blob placeholders;
- `srcset` selects the largest/right-most HTTP candidate;
- picture source and CSS background-image are supported;
- duplicate searches safely upsert the candidate Preview, so rerunning the same Search can backfill Preview images without duplicating Crawl identities;
- Qt shell marker is `Phase49.3I.52E`.

### Verification
- `33632062812` — Qt full parity PASS;
- dedicated 3I.52C/52D/52E suite: 15 tests PASS;
- explicit PASS: mature refetch variant folders without Product linkage;
- explicit PASS: lazy/srcset thumbnail recovery;
- explicit PASS: current `Phase49.3I.52E` shell marker;
- `33632062877` — Single Active AI PASS;
- `33632062880` — Windows Portable PASS;
- Portable release regression: 223 tests PASS;
- artifact id `9847317893`;
- EXE SHA256 `f9bcfc0770a38b0c8eabc9f2deab7c05b2c4d8b577fd25eb540ea9b65f7dc970`;
- EXE self-verify and browser smoke PASS.

### Error handled during implementation
A temporary edit to the raw JavaScript Preview string omitted its closing triple quote. The condition was corrected immediately before CI, not rerun unchanged. Final compile/full parity/portable all PASS. Recorded as ERR-49-099.

### Safety
- no Django migration;
- no Catalog migration;
- no DB repair required for display;
- no destructive media operation;
- Host/Production source and Production MySQL untouched.

### Exact next task
1. owner closes current `Phase49.3I.52C` app;
2. clean ff-only Local sync to current GitHub branch;
3. run canonical Local gate and relaunch; sidebar must report `Phase49.3I.52E`;
4. reopen permanent Crawl inventory and verify old refetch-backed rows now show their local thumbnail/count;
5. rerun the same bounded MakerWorld Search once so previously empty recent candidate Preview rows are backfilled from the improved lazy-image parser;
6. verify recent `new` rows show Preview when listing exposes one, while only actually downloaded rows show `N عکس دارد`;
7. if any exact external id still has no image after those two checks, inspect its DB identity + all matching on-disk folders read-only before any further code change.

## 2026-09-02 — Phase49.3I.52D Legacy downloaded-image path parity + Crawl numeric layout repair

Status: `GITHUB_UPDATED / WINDOWS QT CI PASS / SINGLE ACTIVE AI PASS / WINDOWS PORTABLE PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT TOUCHED`.

Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Exact tested runtime checkpoint: `a18b6f3036d41271cf3e8c1d9a0dfd8c271a53ce`  
Rollback: `backup/pre-phase49-3i52d-legacy-image-path-layout-20260902` → `28b51d2f95b272d3bf6311fb02f55a7a4fa808e4`.  
Catalog Center: `8.9.10` / build `2026.09.02.1`.

### Owner QA evidence
The owner screenshot of `Add Products / Crawl → Inventory` showed many MakerWorld rows with `Preview تصویر ندارد` even though older Catalog Center downloads already existed locally. The two numeric receive controls also rendered with RTL spin arrows/text colliding.

### Verified mature storage contract
The retained mature Tk runtime uses:
- persistent DB/data root: `D:\projects\3dprinthub-catalog-manager`;
- Product download directory: `D:\projects\3dprinthub-catalog-manager\collected\<source_code>\<external_id>\`;
- original images: `...\images\`;
- finalized SEO images when present: `...\seo_images\`.

The old installed application/source target `D:\projects\3dprinthub_catalog_center` is not the canonical active SQLite data root. It is retained only as a read-only compatibility fallback.

### Root cause
Qt Crawl inventory only asked the Product image resolver when a `discovered_urls` row had already resolved to a Product id. Old/stale Crawl rows without that linkage fell straight to the newer `discovery_previews` cache. Therefore a mature `collected/<source>/<external_id>/images` folder could contain real downloaded files while the card still reported no Preview. An additional compatibility gap made Product matching source-code case-sensitive.

The numeric QSpinBox controls inherited the application-wide RTL direction and generic padding, which put the Windows arrow subcontrol and digits into the same visual area.

### Implemented
- ImageCore now resolves the mature downloaded-image folder directly from the active Catalog SQLite parent + `collected/<source>/<external_id>`;
- it scans `seo_images` first and `images` second, read-only, with deduplication;
- the retained old `D:\projects\3dprinthub_catalog_center\collected` tree is accepted only as a secondary read-only fallback when it physically exists;
- Product local_dir remains first authority when available;
- Crawl inventory and current-search cards can now display/count real local downloaded images even before Product-id linkage is repaired;
- card text uses the requested `N عکس دارد` contract whenever real local files exist;
- single-item live review can display those local files even for an unlinked Crawl candidate;
- bounded Crawl→Product resolution is now case-insensitive for source_code, preserving old `MakerWorld` vs current `makerworld` rows;
- Product/business data is not rewritten by image-path discovery;
- `requested` and `image_limit` spinboxes are explicitly LTR, centered, width-bounded and padded away from Windows arrow buttons;
- Crawl control grid now has explicit horizontal/vertical spacing and balanced editable columns.

### Verification
Exact tested runtime: `a18b6f3036d41271cf3e8c1d9a0dfd8c271a53ce`.
- `33628825851` — Phase49.3I.42C3 Qt6 Crawl + AI Runtime CI — PASS;
- dedicated 3I.52C/52D suite: 13 tests PASS, including:
  - mature collected folder visible without Product linkage;
  - legacy Product source-code case mismatch resolves;
  - numeric spinboxes are LTR/non-cramped;
- `33628825772` — Single Active AI — PASS;
- `33628825715` — Windows Portable — PASS;
- Portable release regression gate: 221 tests PASS;
- artifact id: `9846044486`;
- EXE SHA256: `c08aa1e9d12926203cb59c580aab6c606c2b0e259ad83df37aa3b3abec86c22a`;
- EXE self-verify and browser smoke PASS.

### Database / media / Production safety
- no Django migration;
- no Catalog migration;
- no Product/Crawl row rewrite is required to show legacy images;
- no local downloaded file is moved/deleted/renamed by this repair;
- compatibility discovery is read-only;
- Host and Production source are untouched;
- Production MySQL is untouched.

### Exact next task
1. owner closes the running Qt app;
2. clean ff-only Local sync to the live GitHub branch;
3. run the canonical Local gate and relaunch Qt;
4. verify the same Crawl Inventory rows now show the actual downloaded thumbnail and `N عکس دارد`;
5. verify a single candidate opens the local image strip;
6. verify `100` and `5` numeric controls no longer overlap their arrow buttons;
7. if a specific row still has no image, capture its external id and the UI will be checked against its exact `collected/<source>/<external_id>` folder and DB identity without destructive repair.

## 2026-09-02 — Phase49.3I.52C Crawl visual review + multi-select + safe Product recovery

Status: `GITHUB_UPDATED / WINDOWS QT CI PASS / SINGLE ACTIVE AI PASS / WINDOWS PORTABLE PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT TOUCHED`.

Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Final tested runtime checkpoint: `f43c7aa464948832ba349543f94c94498490ab25`  
Pre-phase rollback: `backup/pre-phase49-3i52c-crawl-review-recovery-20260902` → `dfc883cc6ac68c49c589c0d5a6007d50a9a4719c`.  
Catalog Center: `8.9.10` / build `2026.09.02.1`.

### What changed
- current Crawl Search results are now a visual icon/card gallery, scoped to the active Search/Listing URL;
- each new Search clears the previous live-result cards before starting;
- Preview-first discovery shows Product title/thumbnail before full receive;
- stable discovery Preview cache is reused by Qt and persistent Crawl inventory;
- cards visibly report `Preview: 1 عکس`, `N عکس دارد` or the explicit no-preview state;
- rich receive emits per-Product image progress such as `عکس 3/5` and `عکس 5/5`;
- selected collected Product has a dedicated live image strip showing actual local images, total image count and locally displayable file count;
- dense receive/bulk controls were shortened to task labels (`شروع دریافت`, `موجودی Crawl`, `لینک پیش‌فرض`, `دریافت Product`, `افزودن انتخابی`, `حذف انتخابی`) while full explanations remain in tooltips;
- current Search and persistent Crawl gallery/table use explicit Qt MultiSelection with select-all/clear and selected-count feedback;
- selected candidates can be bulk-added/rejected; successful selected transfer returns Product ids and navigates to Products;
- already-collected identities stay mapped to their existing Product;
- persistent Crawl inventory is enriched with candidate title/thumbnail/status evidence;
- Product image/source stage exposes `دریافت داده و عکس بیشتر از لینک محصول`;
- safe recovery refreshes source-owned/source-derived data and images while preserving operator Persian title/description, final price, final-price flag, sale approval and publish decision;
- Crawl bulk actions are task-grouped with shorter operator labels rather than a dense row of long actions;
- the Qt sidebar/About phase marker no longer reports stale `Phase49.3I.48`; it reports `Phase49.3I.52C` so the owner can immediately verify the running shell is current.

### Verification
- `33625988684` — Phase49.3I.42C3 Qt6 Crawl + AI Runtime CI — PASS on final runtime `f43c7aa...`;
- dedicated 3I.52C regression covers visual Preview, image count, Search clearing/scoping, Qt MultiSelection, per-image progress, Product routing and safe source recovery;
- `33625988674` — Single Active AI — PASS;
- initial Portable `33624135587` failed because the new Qt regression imported PySide6 while that job installed only non-Qt requirements; recorded as ERR-49-097 and not rerun unchanged;
- CI dependency boundary was fixed at `b43880a763d00bfda52dc29c4bf080cb428b1230`; final visual/runtime shell checkpoint is `f43c7aa464948832ba349543f94c94498490ab25`;
- `33625988663` — Windows Portable — PASS;
- Portable release regression gate: 218 tests PASS;
- artifact `3DPrintHub-CatalogCenter-v8.9.10`, artifact id `9844889166`;
- EXE SHA256 `cd54431bd29bad76990c17eb818671e3f32c4d53a244cdc07132f5d93a532f4b`;
- EXE self-verify and browser smoke PASS.

### Database / media / Production
- no new Django migration in 3I.52C;
- no destructive Catalog schema/data operation;
- Preview cache is additive below the persistent Catalog data root;
- canonical Local Catalog SQLite remains `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`;
- no Host source change;
- no Production MySQL write or migration;
- last verified Production application commit remains `c283864290f9c989a9fcdf24ee8eef519560e917`;
- existing 3I.51 Site migration candidates remain pending until a later verified Host audit; nothing in 3I.52C claims they are applied.

### Documentation updated
- active Phase49.3I.52 document;
- CURRENT_STATE;
- ROADMAP;
- CHANGELOG;
- REQUESTS as REQ-49-089;
- ERRORS as ERR-49-097;
- PATHS;
- master roadmap and PROJECT_CONTEXT.

### Exact next task
1. close Catalog Center;
2. on Windows verify `D:\projects\3DPrintHub`, origin, active branch and clean worktree;
3. ff-only pull the latest `agent/phase49-3i18-operator-bulk-ai-rebuild`;
4. run root `RUN_PHASE49_3I42C_LOCAL_GATE.ps1` version `49.3I.52.2` with the exact live GitHub head and `-LaunchApp`;
5. foreground QA one bounded MakerWorld Search: prior cards clear, Preview title/image appears, each Product shows 3/5→5/5 progress and final image count;
6. select multiple candidates, add them, verify automatic navigation to Products and visible Product identity;
7. verify persistent Crawl inventory remains visual/multi-selectable;
8. in Product image/source stage run `دریافت داده و عکس بیشتر از لینک محصول` and verify source images/data refresh while operator Persian content/final price/publish state remain unchanged;
9. only after owner Local acceptance may the normal Host read-only audit/backups begin; Production deploy remains blocked.

## 2026-09-02 — Phase49.3I.52 Site authoring + Shared Host AI + Bidirectional Product sync

Status: `GITHUB_UPDATED / WINDOWS QT CI PASS / SITE ADMIN-BRIDGE CI PASS / PORTABLE PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT TOUCHED`.

Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Exact tested source checkpoint: `6d19bed7659b9ca4cd54ff1ffd1323ec423bea6a`  
Site/Admin runtime checkpoint: `d6450ca2d9016bbdb75b37b7a31d20d8c2b6d111`  
3I.52B rollback: `backup/pre-phase49-3i52b-bidirectional-site-sync-20260902` → `48290db404739f07e322a700b6baa71d6b801871`.

Implemented:
- Django Admin is now a first-class fallback Product authoring surface when Catalog Center is unavailable, while reusing the canonical Product, ProductCatalogProfile and ProductVariant authority;
- manual Site Products receive the same canonical ProductCatalogProfile and existing pricing/Profile/Variant engine; no parallel commerce database was created;
- Host Product AI reuses the mature Structured/semantic-validated Catalog provider stack through root `ai/`, with Preview-before-Apply and an explicit content/SEO-only safety boundary;
- Host AI secrets are environment-only; Windows may keep using the mature OS Credential Store boundary;
- automatic Product-model policy rejects variable OpenRouter routers, probes exact Structured models for real Persian output, prefers verified free models and only then a bounded low-cost fallback;
- Bridge Product payload now includes source identity, category slug, pricing strategy, pricing inputs and technical summary, plus bounded offset pagination;
- Products page now has `↻ دریافت تغییرات سایت` and pulls newer Site revisions into Windows through the authenticated Bridge;
- clean Local Products accept a newer Site revision; Local Products with unpublished edits are never overwritten automatically and instead receive an explicit revision conflict;
- Site-only Products become non-publishable Local mirrors (`reference_only=1`) until linked to a real acquisition/source identity;
- republish now verifies the current Site Product revision before Batch packaging; mismatch or revision-check failure stops closed instead of overwriting newer Site Admin work;
- existing Batch 8.5 → FTP → Bridge → Store/public HTTP verification remains unchanged after the revision gate.

Verification:
- `33619876564` — final Phase49.3I.42C3 Qt6 full parity on `6d19bed...` — PASS, including dedicated 3I.52B Site→Windows pull, conflict protection and publish revision guard plus all mature acquisition/Filament/Profile/Stage/launcher regressions;
- `33619876411` — Windows Portable on `6d19bed...` — PASS;
- `33619876317` — Single Active AI on `6d19bed...` — PASS;
- `33619558467` — Product Admin/Bridge/migration CI on runtime-equivalent `d6450ca...` — PASS, including new 3I.52B Bridge serialization/pagination/pricing round-trip tests;
- `33619558562` — Phase50 Variant2/Profile Matrix on `d6450ca...` — PASS;
- delta `d6450ca... → 6d19bed...` is only the isolated Windows 3I.52B test fixture, so Site/Admin runtime source did not change after the passing Admin/Bridge gate.

Errors resolved:
- initial 3I.52B Qt test exposed missing `utc_now` import in the new Site→Local apply helper;
- the next run proved the runtime fix and isolated the remaining failure to tests invoking the real Bridge settings boundary without a CI token;
- the test fixture was corrected to provide an isolated Bridge settings object while the network Product list remained mocked;
- final Qt full parity then passed. Recorded as ERR-49-096.

Database / Production safety:
- 3I.52/3I.52B add no new Django migration and no destructive Catalog migration;
- existing 3I.51 additive migration candidates remain `website.0024` and `store.0042`;
- pricing fields used by this sync already belong to the existing Store migration chain, including `store.0033`;
- Production MySQL has NOT been changed;
- Host/Production source has NOT been changed;
- last verified Production application commit remains `c283864290f9c989a9fcdf24ee8eef519560e917`;
- last verified Production Store migration evidence remains only through `store.0035`; no later migration is assumed.

Local acceptance:
- canonical runner: `RUN_PHASE49_3I42C_LOCAL_GATE.ps1`;
- runner version: `49.3I.52.1`;
- Windows PowerShell 5.1 ASCII/parser guard remains mandatory;
- the gate checksum-backs up `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3` before foreground QA.

Exact next task:
1. close Catalog Center;
2. verify Local repo/origin/branch/clean worktree and live GitHub head;
3. ff-only pull the final documentation head;
4. run the canonical 3I.52 Local gate with the exact final GitHub head and `-LaunchApp`;
5. foreground-QA Site Product pull, newer-clean revision acceptance, dirty-Local conflict protection and Site-only non-publishable mirror behavior together with the existing 3I.51 Product/Crawl/Profile/Filament checks;
6. only after owner Local acceptance start the read-only Host/MySQL/migration/disk/backup audit;
7. create and verify fresh source/environment/MySQL backups before any deploy or migration;
8. Production deploy remains blocked until those gates pass.

## 2026-09-02 — Phase49.3I.51 Windows + Site finalization

Status: `GITHUB_UPDATED / WINDOWS CI PASS / SITE CI PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT TOUCHED`.

Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Approved source checkpoint: `8f01ea264dea2771cf1eb2f592be794d0dc95bbf`  
Exact Windows/Qt checkpoint: `25981269c2859ba107aad1feaa04b711b5761ae5`  
Rollback: `backup/pre-phase49-3i51-windows-site-finalization-20260902` → `191e8ef83f9a804805dda4cdd3df66b8224264d6`.

Implemented:
- Product image review is larger while multi-image selection/bulk operations remain intact;
- Product editor keeps the fixed source-page open action;
- pasted MakerWorld Search/Product URLs auto-select MakerWorld instead of inheriting a stale GrabCAD selection;
- Crawl exposes live Discovery/Receive progress and persistent review data;
- missing source production facts create one explicit `پیش‌فرض` Profile using owner defaults 100 g model + 50 g support + 60 min;
- fallback Profile includes all active PLA/PETG-family Filaments and excludes unrelated materials;
- Filament workspace is split into Filaments / Materials / Brands / Colors;
- Brand/Material/Color are managed registries; rename propagates to assigned Filaments and collision is rejected before mutation;
- optional Filament/Brand/Material descriptions and Material reference price/kg are preserved;
- Filament description survives Qt table normalization/edit;
- Qt exposes selected/full Filament Site Sync over the existing authenticated Bridge; FTP is not required for this Bridge-only operation;
- full Site reconciliation includes inactive Local Filaments so stale active Site offers can be deactivated;
- Site Django models/Admin persist FilamentBrand and optional descriptions; Material Admin keeps price/kg plus print/supervision rates visible;
- existing selling-price authority remains sale price per roll ÷ roll weight.

Verification:
- `33611776817` — Qt6 full parity on `25981269...` — PASS, including dedicated 3I.51 finalization regression and mature acquisition/Filament/Profile/Stage/launcher/source guards;
- `33611776806` — Windows Portable on `25981269...` — PASS; artifact `3DPrintHub-CatalogCenter-v8.9.10`, artifact id `9839347209`;
- `33611776891` — Single Active AI/no-migration safety on `25981269...` — PASS;
- `33611936196` — Product Admin/Bridge/migration CI on final source `8f01ea26...` — PASS, including `website.0024` and `store.0042` on isolated CI SQLite and the 3I.51 Admin/Bridge regressions;
- `33611936216` — Single Active AI/no-migration safety on final source `8f01ea26...` — PASS;
- compare `25981269... → 8f01ea26...` changes only `website/admin.py` and `store/test_phase49_3i51_filament_registry_admin.py`; Windows runtime source did not change after the passing Qt checkpoint.

Known implementation failures were resolved and are recorded as ERR-49-093..095. No failed command was repeated under the same known-bad condition.

Database/Production safety:
- Catalog SQLite change is additive only: `available_filament_offers.description`;
- registry metadata remains in existing Catalog settings;
- new Django migrations are additive candidates `website.0024_phase49_3i51_material_catalog_description` and `store.0042_phase49_3i51_filament_registry_descriptions`;
- Production MySQL has NOT been migrated;
- Host/Production source has NOT been changed;
- last verified Production application commit remains `c283864290f9c989a9fcdf24ee8eef519560e917`;
- last verified Production migration evidence remains only through `store.0035`; no later migration is assumed;
- secrets remain in the existing secure Local/environment boundary.

Local acceptance:
- canonical runner: `RUN_PHASE49_3I42C_LOCAL_GATE.ps1`;
- runner version: `49.3I.51.1`;
- runner remains ASCII-only for Windows PowerShell 5.1;
- it must checksum-back up `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3` before foreground QA.

Exact next task:
1. close Catalog Center;
2. verify Local repository/origin/branch/clean worktree and live GitHub head;
3. ff-only pull the final documentation head;
4. run the canonical 3I.51 Local gate with `-ExpectedHead <final-doc-head> -LaunchApp`;
5. foreground-QA Product images/source link, MakerWorld Search-Link Source detection/live results, default Profile, Filament registries, descriptions and selected/full Site Sync controls without intentionally publishing a Product;
6. only after owner Local acceptance start the read-only Host/MySQL/migration/disk/backup audit;
7. Production deploy/migrations remain blocked until that audit and fresh verified backups are complete.

## 2026-09-02 — Phase49.3I.49 guarded multi-product site publish + full Slider/Admin sync

Status: `GITHUB_UPDATED / WINDOWS CI PASS / ADMIN CI PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT TOUCHED`.

Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Exact Windows/Local-gate source checkpoint: `f9f89643de883ff549a9c0089235e43f061c5d4d`  
Admin/Bridge checkpoint: `16cf7cfaf6be3e8594435e3489cb0615624fcb00`  
Rollback: `backup/pre-phase49-3i49-site-bulk-publish-admin-control-20260901` → `1f8910b6c8c7c601cfd50689d8c48af492f7c453`.

Requested delta:
- Products supports explicit multi-select `آماده انتشار` and guarded multi-product site publish;
- only factually complete Products can enter the publish queue;
- publish reuses the mature `Batch 8.5 → FTP → Bridge Import → Store/public HTTP verification` path;
- only a strict successful ACK/public verification moves Local state to `workflow_status=uploaded`, clears `upload_ready`, and therefore moves the Product into `ارسال / منتشرشده`;
- failures remain visible as failures and are never presented as Published;
- the complete existing Slider presentation contract now round-trips Desktop ↔ Bridge ↔ ProductCatalogProfile ↔ HomepageHeroSlide;
- Django Admin exposes the same site-relevant Product/Profile/Slider controls in task order instead of creating a duplicate settings store.

Site-relevant Slider round-trip now covers:
`presentation_mode`, object fit, focal position, image scale, X/Y position, background mode/color/blur, Desktop/Mobile max width/height, Persian Slider title/description/Alt/button/focus keyword, transition effect/duration, display duration, sort order, active state and optimistic sync revision.

Admin information architecture follows the repository professional-commerce design rules derived from the owner design references: task-first grouping, progressive disclosure for diagnostics, one explicit publish action, and responsive/motion controls separated from content/SEO.

Verification:
- `33596830380` — exact-head `qt6-full-parity-windows` on `f9f896...` — PASS, including the dedicated `Qt6 3I.49 bulk site publish parity` regression, mature acquisition/Filament/Profile/Stage regressions, offscreen Qt launch, legacy launcher and final source guards;
- `33596830268` — exact-head Single Active AI / no-migration safety — PASS;
- `33596562467` — Product Admin Workspace CI on `16cf7c...` — PASS: compile, Django check, `makemigrations --check --dry-run`, CI migration apply and Admin regressions including 3I.49;
- compare `16cf7c... → f9f896...`: only `RUN_PHASE49_3I42C_LOCAL_GATE.ps1` changed, so no Admin/Bridge source changed after the successful Admin run.

Local gate:
- `RUN_PHASE49_3I42C_LOCAL_GATE.ps1` now includes 3I.46 paging, 3I.47 workspace/image/bulk-AI, 3I.48 owner/Filament/Slider and 3I.49 bulk-publish regressions;
- success marker: `PHASE49_3I49_LOCAL_GATE=PASS`;
- existing checksum-verified backup of `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3` remains mandatory before Local QA.

Safety:
- Django migration added = NO;
- Catalog destructive schema change = NO;
- Production MySQL changed = NO;
- Production source changed = NO;
- Host touched = NO;
- secret storage changed = NO;
- FTP password and Bridge token remain in the existing secure Local/environment boundary and are not copied into Django Admin;
- last verified Production application commit remains `c283864290f9c989a9fcdf24ee8eef519560e917`;
- last verified Production migration evidence remains only `store.0034` and `store.0035`.

Exact next task:
1. owner closes Catalog Center;
2. verify Local repo/origin/branch/clean worktree and live GitHub head;
3. ff-only pull the final documentation head;
4. run the canonical Local gate with `-LaunchApp`;
5. verify ready-state visibility and multi-select behavior on disposable Products;
6. do NOT click the real site-publish action until the owner intentionally chooses a disposable Product and the current Production receiver/deploy state has been verified;
7. after Local acceptance, start the normal read-only Host/migration/backup/deploy chain from the approved GitHub commit.

# CURRENT PROJECT STATE

## Continuation checkpoint — 2026-09-01 / ERR-49-088 PS5.1 Local gate repair + professional commerce design standard

Status: `SOURCE TESTED ON WINDOWS CI / OWNER LOCAL 3I.47 RERUN NEXT / PRODUCTION NOT TOUCHED`

Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Exact tested source checkpoint: `36a710953276aae99fa668f477ad5569f8dc23ba`  
Owner Local runner: `RUN_PHASE49_3I42C_LOCAL_GATE.ps1` version `49.3I.47.2`  
Rollback: `backup/pre-err49-088-ps51-runner-ascii-20260901`

Owner evidence:
- the earlier 3I.46 Local gate completed successfully and produced checksum-identical Catalog SQLite source/backup SHA256 `041CAE222B2784F8CC36B266341A33220B16194E16F29397440F001DBD89E988`;
- backup: `D:\projects\3dprinthub-backups\phase49-3i42c-20260901-145303\catalog-before-qt42c-qa.sqlite3`;
- the first 3I.47 attempt stopped before tests because Windows PowerShell 5.1 could not parse one newly introduced non-ASCII QA string;
- this was a runner encoding regression, not a Product/Crawl/AI/database failure.

ERR-49-088 resolution:
- runner is ASCII-only again;
- CI now raw-byte checks the runner and parses it under Windows PowerShell 5.1 before the existing `pwsh` parser/stdin gate;
- exact source checkpoint `36a710...`:
  - `33511403943` Qt6 Full Parity Windows — PASS;
  - `33511403901` Single Active AI — PASS;
  - 3I.47 Product lifecycle / local thumbnail / bulk AI / all-image SEO / Acquisition workspace / Profile-Pricing regressions PASS.

Professional commerce design sources:
- the uploaded `webdesign1.zip` binary itself was not exposed as a readable archive mount in this execution environment, so no ZIP-extraction claim is made;
- constituent owner File Library books were read directly, including Practical UI 2nd Edition, Lean UX, UI/UX Web Design Simply Explained, 100 Things Every Designer Needs to Know About People, Designing Brand Identity, 3D Web Development with Three.js and Next, and NextJS Cookbook;
- source-grounded rules are registered in `docs/PROFESSIONAL_COMMERCE_DESIGN_ARCHITECTURE.md`;
- this does NOT authorize a Next.js/React rewrite. Current Django architecture remains authoritative.

Design direction now canonical:
- information architecture and customer task flow before decoration;
- one reusable design system across Storefront/Admin/Catalog Center;
- disciplined Persian typography scale and readable dense-operator typography;
- progressive disclosure/tabs instead of control walls and nested scroll traps;
- restrained specialist/industrial trust presentation rather than decorative neon;
- Product pages prioritize identity, media, technical fit, price/quote state, production facts and one primary CTA;
- no color-only status communication;
- optional 3D is lazy/progressive and may never block LCP, core content or purchase controls;
- SEO metadata/structured data must match visible server-rendered content.

Non-blocking warnings observed in the older Local gate:
- Qt offscreen `QFontDatabase` reports no PySide6 bundled font directory; this is not the parser failure and is queued for the typography/packaging audit;
- `QSortFilterProxyModel.invalidateFilter()` deprecation is technical debt;
- Pillow `Image.getdata()` deprecation is known technical debt;
- pip upgrade notice is informational.

Database/Host/Production:
- Django migration changed = NO;
- Production MySQL changed = NO;
- Host/Production source changed = NO;
- Catalog destructive migration = NO;
- Production remains on last verified application commit `c283864290f9c989a9fcdf24ee8eef519560e917`;
- only `store.0034` and `store.0035` remain last verified applied Production migrations; later migration state is not assumed.

Exact next task:
1. owner closes Catalog Center;
2. verify correct Local repo/branch/clean worktree and live remote head;
3. ff-only pull the final documentation head;
4. run `RUN_PHASE49_3I42C_LOCAL_GATE.ps1 -ExpectedHead <final-doc-head> -LaunchApp`;
5. confirm output reports runner `49.3I.47.2`;
6. perform foreground 3I.47 QA on Product lifecycle tabs, old/local thumbnails, sequential multi-select AI, all-image SEO numbering/metadata, Acquisition gallery/details workspaces and Profile/Pricing tabs;
7. if QA passes, continue typography/font packaging + 42D visual/accessibility polish under `docs/PROFESSIONAL_COMMERCE_DESIGN_ARCHITECTURE.md`;
8. Production remains blocked until explicit owner Local acceptance.


Updated: 2026-09-01

## Current active checkpoint — Phase49.3I.47

Status: `IMPLEMENTED + WINDOWS CI PASS + ADMIN CI PASS + STOREFRONT CI PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT TOUCHED`

Repository: `farazha2203/3dprinthub`
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Code checkpoint: `9984e3bb9ab5ff293ad275ecbe86dba3a96db4b1`
Documentation checkpoint before this file update: `b9c64874dcb4b6290f743af1b0550f6f82add845`
Rollback: `backup/pre-phase49-3i47-owner-workspace-20260901` → `ecfd9260c168140757781bb672eb57c77bcc4ee3`
Canonical phase document: `docs/phases/PHASE49_3I47_QT_WORKSPACE_IMAGE_BULK_AI_SITE_IA.md`

## What is implemented

### Products
- Product Gallery remains bounded/lazy from Phase49.3I.46.
- Four lifecycle workspaces are exposed: active, sent/published, archived, rejected/deleted.
- Product cards expose title, description excerpt and image count.
- legacy/local Product image fallback resolves older Products that have local image files but no modern URL mapping.
- multi-select Products can run `AI تکمیل همه موارد` sequentially through the one shared AICore and shared single-Product postprocessing path.

### Product images / SEO
- all selected Product images are finalized under one semantic SEO identity;
- every image receives the same intended alt/title/caption/keywords metadata set;
- physical SEO WebP files use deterministic unique sequence suffixes such as `-01`, `-02`, `-03`;
- dedicated regression verifies all physical files exist and metadata is consistent across the image set.

### Add Product / Crawl
- Operations is split into three focused workspace tabs instead of one tall control wall;
- persistent inventory is immediately usable;
- inventory has Windows-like gallery/image and details/table views;
- cards/rows can show local thumbnail, title, description excerpt and image count;
- bounded 100-row Crawl paging from Phase49.3I.46 remains authoritative.

### Profile / Pricing
Three full-height tabs are now used:
1. `پروفایل و روش قیمت`
2. `وزن و زمان تولید`
3. `فیلامنت، رنگ و قیمت قطعی`

Production and Filament/price tables have enough minimum height to avoid the previous clipped nested-scroll presentation.

### Django Admin / Website management
- shared responsive accessible tabbed change-form architecture;
- Product Sales / Source / SEO workspaces;
- Store pricing settings grouped by task;
- material/color pricing split into focused tabs;
- site settings and quote workspaces organized into tabs.

### Storefront
- Product information is organized into progressive accessible tabs;
- existing Variant/Profile/pricing business authority is preserved.

## Verification

Qt/Desktop code checkpoint `9984e3bb9ab5ff293ad275ecbe86dba3a96db4b1`:
- `qt6-full-parity-windows` — run `33506242569` — PASS;
- `phase49-3i17` — run `33506242669` — PASS.

Admin checkpoint `ef215ba09044cd421302f9057bf3c1565b99ef1e`:
- `product-admin-workspace` — run `33505851712` — PASS;
- `phase49-3i17` — run `33505851749` — PASS.

Storefront checkpoint `f4beec484f060063d00de4a5753a135a020cfea1`:
- `phase50-variant2-gallery` — run `33506122579` — PASS;
- `phase49-3i17` — run `33506122534` — PASS.

Dedicated regression:
`catalog_center/tests/test_phase49_3i47_qt_workspace_image_bulk_ai.py`

It locks multi-image SEO numbering/metadata, local image fallback, Operations tabs and Windows-like views, Profile/Pricing tabs, sequential Bulk AI, and Product lifecycle tabs.

## Error corrected in this checkpoint

`ERR-49-087` conceptual root cause: Phase49.3I.46 correctly solved bounded database paging but retained monolithic presentation and incomplete multi-image/legacy-UI parity. The correction is Phase49.3I.47. Detailed implementation/verification is recorded in the canonical phase document above.

Prevention rule: large list/workflow surfaces must combine bounded database access with task-oriented tabbed information architecture, legacy-data fallbacks and many-item regressions; lazy SQL alone is not sufficient UX parity.

## webdesign1.zip

The owner supplied `webdesign1.zip` for typography/layout/effects/SEO study. The attachment name was received, but the declared mounted path was not readable in this Chat runtime and the file was not present in the active sandbox. No claim is made that the archive was read. The current 3I.47 work uses the project’s already-registered UI/UX engineering references plus owner QA. Re-ingest the ZIP when it becomes readable before attributing further design decisions to those books.

## Database / Host / Production safety

- Django migration changed = NO.
- Production MySQL changed = NO.
- Catalog destructive migration = NO.
- Host source changed = NO.
- Production deploy = NO.
- default launcher cutover = NO.
- secrets changed = NO.

Last verified Production application commit remains `c283864290f9c989a9fcdf24ee8eef519560e917`.
Last verified Production DB evidence still confirms only `store.0034` and `store.0035`; do not assume later migrations are applied without a fresh read-only Host audit.

## Exact next task

1. Owner closes Catalog Center.
2. On `D:\projects\3DPrintHub`, verify correct repository, active branch, clean worktree and live GitHub head.
3. Pull only by ff-only to the final documentation head.
4. Run repository-owned `RUN_PHASE49_3I42C_LOCAL_GATE.ps1 -ExpectedHead <final-head> -LaunchApp`; the runner is version `49.3I.47.2` and creates a checksum-verified Catalog SQLite backup before QA.
5. Foreground QA on real Catalog data:
   - four Product lifecycle tabs;
   - old/local Product thumbnails + title/description/image count;
   - sequential multi-select full AI on disposable Products;
   - one Product with at least three images → all SEO files numbered and metadata consistent;
   - Add Product/Crawl three workspaces + gallery/details views;
   - Profile/Pricing three full-height tabs and all rows visible.
6. If any contract fails, patch only that failed contract with a focused regression.
7. Production remains blocked until explicit owner Local acceptance.

Historical checkpoints remain available in Git history and their dedicated `docs/phases/` documents.

## 2026-09-14 - LOCAL FILAMENT DEFAULTS / MANUAL REPUBLISH READY
Status: `LOCAL_DATA_UPDATED / TESTED / QT_LAUNCHED / NO PRODUCTION PUBLISH`.

Owner-requested Local Catalog defaults are applied to `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`. Fresh rollback backup: `D:\projects\3dprinthub-backups\phase50-filament-defaults-20260914-175618`. Source/backup/preview integrity and logical pre-write guards passed.

All 66 active Filament rows now have 1000 g roll weight, stock_roll_count=1, nonzero purchase/sale price and nonzero print/supervision rates. Owner overrides: PLA 3.5m/4.5m, PETG 4.5m/5.5m, HT-PLA-GF 4.5m/5.5m, PLA-CF 8.5m/9.5m Toman purchase/sale; print rates 150k/150k/150k/200k and supervision 50k. Specialist materials reuse existing project Material reference prices, with 150k/50k service fallback where the reference service fields were empty.

Every one of 635 Local Products now has a canonical Sales Profile; 636 Profiles total. Every Profile contains all 64 unique selectable Filament identities (66 inventory rows include two duplicate identities that the mature Core intentionally deduplicates). Twelve Commerce locks were opened through StageCore so dimensions can be edited. Nineteen previously uploaded Products are marked `needs_update=1` for same-identity republish.

Verification: Filament/Profile focused suites 34/34 PASS; Qt verify-only PASS; Catalog integrity `ok`; zero invalid/zero-price active Filament rows; zero Products without Profile. Catalog Center v8.9.10 Qt6 relaunched and responsive. No Product was published and Production DB/source was not changed by this Local policy update.

## 2026-09-17 — Buffer Instagram source registered
Status: `BUFFER_CHANNEL_CONNECTED / API_TRANSPORT_PENDING_CREDENTIAL`.
- Owner confirmed the Instagram Professional account is connected and logged in inside Buffer.
- Official integration source is now Buffer GraphQL API (`https://api.buffer.com`) because Meta for Developers is unavailable to the owner by location.
- Canonical project documentation lives under `docs/مستندات اتصال به اینستاگرام/` with API contract, security rules, official sources and GraphQL examples.
- Provider implementation is `catalog_center/app/buffer_publish.py`; Buffer secret authority is `BUFFER_API_KEY` through Windows Credential Store/environment only.
- `buffer-ker.txt` is explicitly Git-ignored and must never be committed.
- Current workstation verification found `buffer-ker.txt` empty (0 bytes) and no `BUFFER_API_KEY` in the secure store; therefore no live API/channel probe or real Instagram post is claimed yet.
- Publish order remains fail-closed: Site publish -> public HTTPS Product/media verification -> Buffer -> Instagram, with duplicate-public-revision protection.
