## ERR-49-223 - Persian Category names could falsely match external-other through an empty ASCII fold
**Date:** 2026-09-22
**Observed:** A2Z-C2 integration fed an exact configured Persian Category name (for example the configured automotive label) into `CategoryCore.infer_slug`, but the result could be `external-other` instead of the exact taxonomy row.
**Root cause:** legacy `fold()` intentionally retained only `[a-z0-9]`. Persian names therefore folded to an empty string. During the exact-match loop, `source_category_folded == fold(item.name)` became empty==empty and the first Persian row, `external-other`, won before direct comparison reached the intended row.
**Correct fix:** direct Unicode Category name/slug equality remains authoritative. Folded equality is evaluated only when the source folded value is non-empty, and folded-name equality additionally requires a non-empty target fold. Existing English/slug alias scoring and ambiguous-tie fail-closed behavior remain unchanged.
**Verification:** end-to-end full-completion test now resolves the exact configured Category while also proving Source Profiles, Filaments, Slider and physical SEO rename. New focused 3/3 PASS; related broad regression has no new failure.
**Prevention:** normalization helpers that intentionally discard non-Latin characters must never treat two empty normalized strings as an identity match.

## ERR-49-222 - Initial ERR-49-221 broad regression referenced a nonexistent test module
**Date:** 2026-09-22
**Observed:** the first broad Publish/SiteConnection regression command referenced `tests.test_phase49_3i49_site_publish`, while the repository module is `tests.test_phase49_3i49_site_bulk_publish`.
**Impact:** no application/DB/Site mutation. 63 real tests in the same run passed; only unittest module discovery failed.
**Correct fix:** do not repeat the unchanged command. Replace only the incorrect module name and rerun the same intended scope.
**Verification:** corrected Publish/SiteConnection regression passes 86/86.
**Prevention:** derive regression module names from the verified `catalog_center/tests` inventory instead of reconstructing names from feature terminology.

## ERR-49-221 - Transient BitNinja anti-robot 403 blocked Product #588 at publish-readiness before Batch/FTP
**Date:** 2026-09-22
**Observed:** owner attempted to publish real Product #588 from the current unified Windows runtime. `test_publish_readiness()` received HTTP 403 HTML titled `Visitor anti-robot validation` / BitNinja-WafPro instead of Catalog Bridge JSON. The large WAF HTML was surfaced in the Qt error dialog.
**Boundary evidence:** Product #588 was explicitly publish-ready in history, but there is no new `desktop_batch_ready`, `desktop_publish_started` or `desktop_ftp_uploaded` receipt for this failed attempt. Therefore the failure happened before Batch construction/FTP/import and produced no partial Site publish. A later read-only probe using the same configured Site URL and secure Bridge token returned HTTP 200 for both `/health/` and `/publish-readiness/`, with `ready=true`, under the current request shape, Catalog User-Agent and browser User-Agent. This proves a transient public WAF challenge rather than a bad token or missing receiver endpoint.
**Correct fix:** harden only idempotent Bridge GETs. Catalog Bridge JSON requests now send the bounded Catalog User-Agent + no-cache header; GET requests may retry an exact anti-robot/WAF 403 up to three total attempts with short backoff. POST import remains single-attempt and is never blindly retried. A persistent WAF challenge is summarized as a concise RuntimeError instead of dumping the full HTML page.
**Verification:** focused `test_epic49_final` 13/13 PASS including GET-retry and POST-no-retry assertions; corrected Publish/SiteConnection regression 86/86 PASS; py_compile, git diff-check and Qt VerifyOnly PASS. Live read-only Bridge health/readiness are currently HTTP 200 and readiness is true.
**Related infrastructure:** dedicated Host-management reverse tunnel `127.0.0.1:22024` is currently down. That does not cause this public Catalog Bridge readiness failure, but Host deploy/source mutation remains blocked by the permanent reverse-tunnel rule.
**Prevention:** classify public WAF challenges separately from Bridge authentication/readiness failures; safe GET preflight may retry only a narrowly identified transient WAF page, while import POST continues to use the existing non-duplicate timeout/diagnostic contract.

## ERR-49-220 - Buffer Story notification had no linked mobile reminder device and false-ready receipt could block recovery
**Date:** 2026-09-21
**Observed:** the one guarded #609 Social send successfully created Feed post `6ab16b897465bdab83a3fe40`; read-only Buffer reconciliation proves it reached `sent` at https://www.instagram.com/p/DdjtyiMG8RC/. Companion Story post `6ab16b959d554f7b28a44302` used the required notification/Link-Sticker mode but Buffer returned `status=error`. Direct Buffer Post read-back reports: `No devices found for allowed reminder recipients to send push notification to!` / user-facing message asking to link a mobile device.
**Root cause:** notification publishing is a real manual-handoff transport and the Buffer account currently has no eligible linked mobile reminder device. Product media, github_raw hosting, Story PNG, channel connection, policy v4 and sticker metadata are all healthy. A second local defect compounded this: the first notification implementation recorded `instagram_story_notification_ready` solely because a post id existed, even when the provider status was `error`, and the duplicate guard would then suppress recovery.
**Correct fix:** read Buffer Post state when Story createPost returns provider `error`, surface the provider failure instead of recording ready, and make duplicate protection ignore historical `instagram_story_notification_ready` receipts whose persisted `buffer_status=error`. Feed receipt stays authoritative, so recovery after the external device prerequisite is fixed retries Story only.
**Verification:** Social regression 37/37 PASS, changed Python compile PASS, diff-check PASS and Qt VerifyOnly PASS. Regression proves provider-error Story becomes `instagram_story_failed`, no false-ready receipt is created, a historical false-ready/error receipt does not block recovery, and the already-published Feed is not recreated.
**External prerequisite:** link/sign in to the Buffer mobile app for the same Buffer account/channel and enable the required notification delivery. Do not retry Story before this condition changes. Do not bypass with automatic/no-sticker Story because master A2Z-S requires Product-link notification/Link Sticker handoff.
**Prevention:** a provider post id is not proof of delivery readiness. Social receipts must incorporate provider status; notification-mode failures must remain retryable without invalidating successful Feed receipts.

## ERR-49-219 - github_raw Social path still depended on mandatory Site FTP derivative upload
**Date:** 2026-09-21
**Observed:** real #609 Social preflight had Buffer connected, five verified Site media, zero Instagram receipts and a clean exact `social-assets-buffer` worktree. Feed preparation completed, but Story preparation failed before any Buffer createPost with Windows `ConnectionResetError [WinError 10054]` while `ftp.storbinary` tried to upload the generated Story PNG to the Site origin.
**Root cause:** A2P established `github_raw` as the verified provider-delivery host after Buffer/origin incompatibility, but the mature Feed/Story preparation functions still required an intermediate FTP upload + Site-public verification before `rehost_buffer_assets`. Therefore the supposedly GitHub-hosted provider path could still be blocked by unrelated Site FTP/origin transport.
**Failed condition:** do not retry the same Story FTP upload unchanged. No Instagram Feed/Story receipt or provider post was created by the failed attempt.
**Correct fix:** preparation now always renders verified derivatives locally first. Site FTP/public derivative upload remains unchanged only when `buffer_media_host=site`; with `github_raw`, Feed/Story skip Site FTP entirely and the dedicated clean `social-assets-buffer` worktree becomes the only provider-delivery publication path. Canonical Product media remain Site-owned and unchanged.
**Verification:** Social regression 35/35 PASS. Real #609 local-only acceptance generated exactly 5 Feed PNGs plus one nonblank 1080x1920 Story using style `3dprinthub_instagram_gold_navy_v2_iransans`; Instagram receipt count remained 0 before/after. Fresh pre-social Catalog backup: `pre-instagram-a2z-609-20260921-201631`, quick_check=`ok`.
**Prevention:** provider-host selection must control derivative transport as well as final Buffer URLs. A `github_raw` provider path must not require Site FTP/WAF/origin success for generated social derivatives.

## ERR-49-218 - Physical SEO promotion caused false source-drift at publish gate
**Date:** 2026-09-21
**Observed:** after backup-backed real #609 physical SEO repair, all five selected/canonical media and physical SEO filenames were correct, but Site preflight rejected all five as `source image changed after finalization`.
**Root cause:** physical promotion intentionally makes `source_local_file` point to the active SEO WebP, whose encoded/embedded-metadata bytes differ from the original source SHA. The mature source-drift checker still compared this active SEO file against `original_sha256`.
**Correct fix:** when `original_local_file` exists, source-drift compares that preserved source/archive file to `original_sha256`; only pre-promotion records fall back to the legacy source resolver. The actual SEO WebP remains governed independently by `final_sha256`.
**Verification:** changed-source + physical-promotion + multi-image Batch focused 3/3 PASS; complete Image + Site Publish regression 51/51 PASS. Real #609 media gate no longer has media-drift blockers; before queuing, the only remaining state issue was the ordinary same-identity re-publish readiness transition.
**Prevention:** source provenance SHA and active Product-local SEO SHA are distinct authorities after physical promotion and must never be compared as if they were the same byte stream.

## ERR-49-217 - SEO action updated metadata/derivative name but not Product-local physical filename
**Date:** 2026-09-21
**Observed:** owner correctly reported that after «اصلاح اسم و سئو» the card/metadata could show SEO names while Product-local files still remained as names such as `01.webp`, `04.webp`, cache hashes or screenshot names. This also allowed confusing duplicate-looking local filenames even though `seo_images` derivatives were unique.
**Root cause:** the mature finalizer treated `seo_images` as publish authority but deliberately kept `images/` as source/cache provenance. That contract no longer matches the owner requirement that the Product-local physical file itself becomes the unique SEO-named WebP when SEO is applied.
**Correct fix:** after finalization, promote every selected Product-local image to a unique numbered SEO WebP in `images/`; archive the pre-SEO source under `source_originals/`; persist exact `source_local_file` / `product_local_filename`; remap `local://` identities to the new basename; update exact page-extract local-file mapping; make removal/recovery work for SEO-named local files as well as legacy numeric names.
**Verification:** direct rename/query-variant/recovery gate 3/3 PASS; complete Image/Publish/Windows/Social gate 109/109 PASS; 3 touched Python files compile; `git diff --check` and Qt VerifyOnly PASS.
**Prevention:** SEO filename is now a physical Product-local identity, not only display metadata or a publish derivative. Duplicate Product-local SEO basenames must fail closed and all selected filenames remain deterministic `-01, -02, ...`.

## ERR-49-216 - #609 selected media drift, duplicate displayed SEO filename and Buffer worktree collision
**Date:** 2026-09-21
**Observed:** Product #609 Site readiness failed because `local://04.webp` and `local://05.webp` were selected but absent from `images_json`; two query-variant image cards displayed the same `...-01.webp` SEO name; Instagram/Buffer failed with `social-assets-buffer is already used by worktree D:/projects/3DPrintHub-social-assets`.
**Root cause:** trusted Local Site-selection did not always join canonical media at the same save boundary; image-card metadata matched canonicalized asset keys before exact URL identity, collapsing two URL variants; Buffer helper always attempted the configured worktree path instead of reusing an already-registered worktree for the branch.
**Correct fix:** promote trusted Local Site media into canonical `images_json`; exact URL/alias metadata and selected-position lookup precedes canonical fallback; reuse the Git-registered branch worktree. Keep source/cache provenance filenames intact while final `seo_images`, Batch and Site media use unique numbered SEO WebP filenames.
**Verification:** real #609 read-only audit shows five unique finalized SEO files `-01..-05.webp`; focused regression 9/9 PASS; broad Image/Publish/Windows/Social 113/113 PASS; touched compile/diff/Qt VerifyOnly PASS. Two broad UI assertions were proven stale by identical failure on clean baseline `f5f40116...` before their test expectations were aligned.
**Prevention:** Site selection and canonical media authority must be synchronized at one boundary; per-image identity must never be inferred only from URL canonicalization; a named Git branch may have only one registered worktree and provider code must discover/reuse it.

## ERR-49-214 - Latest Windows and Production Server fixes exist on divergent forward lineages
**Date:** 2026-09-21
**Observed:** Repository audit after A2X closure found latest Windows/Product work at `c86c66a11e2c62f8ca219bcb76abc19e5bfdcdbd` while the Production Server parity/Hero closure is `e03bdd2b718fae3ce030df789c8b9db958d8d8ed`. Neither head is an ancestor of the other; merge-base is `b1caeba0f20e711b29dfa9e0ff92a2f5186fb08d`.
**Impact:** no current Production or Catalog corruption was found, but starting future features from either branch alone can silently drop accepted behavior from the other lineage and repeat the previously observed old-runtime regression class.
**Root cause:** urgent Server/Production hotfix work branched from the live release lineage while Windows A2V/A2W/A2X Slider work continued independently from the latest operator lineage.
**Correct fix:** Phase50.A.2Y must reconcile the two heads into one tested GitHub forward baseline before new permanent feature work. Do not solve this by replacing the latest Windows tree with the Server tree or vice versa; integrate only verified deltas and run both Windows/Qt and Django/Server regressions.
**Verification:** accepted merge `f9a9c203ae3a0a5665dbf884ce0c3e4bf761110b` has the A2Y/Windows planning lineage and Server/Production closure as its two parents. Windows focused 94/94 and Server focused 52/52 PASS; broad Windows 115/116 has only baseline ERR-49-203; compile/check/no-drift/diff/Qt VerifyOnly PASS; exact-SHA Qt runtime and Desktop shortcut cutover PASS with Catalog read-only counts unchanged.
**Prevention:** `AGENTS.md` now requires a forward-lineage check before each new feature phase and requires lineage convergence whenever latest Windows and current Production/Server fixes do not share one accepted forward head.

## ERR-49-215 - A2Y convergence exposed a stale mobile-Hero cache-version assertion
**Date:** 2026-09-21
**Observed:** the first merged Server regression ran 52 tests and only `website.test_phase50_mobile_hero_seo` failed because it still required cache marker `v=50.8.0`, while the accepted Server template and A2Q Production contract are already `50.10.0`.
**Impact:** no runtime, Catalog, DB or Production defect. The merged template matched current Production behavior.
**Root cause:** the mobile-Hero test was last updated during the older 50.8.0 presentation slice and was not advanced when A2N/A2Q moved the public Slicebox assets through 50.9.0 to 50.10.0.
**Correct fix:** update only the stale test assertion to the documented accepted `50.10.0` marker; do not roll runtime assets back to satisfy the historical assertion.
**Verification:** changed-condition test 1/1 PASS; full Server unified/profile/republish/payment/finance/Hero gate 52/52 PASS; Windows focused gate 94/94 PASS; broad Windows remains 115/116 with only independently documented ERR-49-203.
**Prevention:** presentation/cache assertions must track the latest accepted Production contract in CURRENT_STATE/ROADMAP, and a merge-time failure must be reproduced against its source baseline before being classified as a new regression.

## ERR-49-227 - Clickable Story failure was discoverable before Feed but Buffer mobile prerequisite was not preflighted
**Date:** 2026-09-22
**Observed:** Product #536 Feed published successfully, then companion Story notification failed because Buffer had no active mobile reminder device. Direct channel truth now reports `hasActiveMemberDevice=False`. #536 Feed is live at `https://www.instagram.com/p/DdmXo5QlMEd/`; its github_raw branded Story asset is valid 1080×1920 and not the cause.
**Root cause:** clickable Instagram Story links in the accepted Buffer path use notification/Link-Sticker handoff. The Windows flow previously discovered the missing reminder device only after Feed createPost, allowing partial Feed success.
**Correct fix:** include `hasActiveMemberDevice` in Buffer channel health; when companion clickable Story is required, verify the mobile prerequisite before any new Feed createPost. If missing and no Feed exists, fail before Feed. If current-ACK Feed already exists, preserve/deduplicate it and report Story-only blocker. Keep ERR-49-220 truthful provider-error handling for any later notification failure. A2Z-S adds the earlier Core/UI boundary too: readiness now runs before Site mutation, media rendering/rehost and Worker creation, while the lower Buffer guard remains as defense-in-depth.
**Verification:** real Buffer state false; dedicated readiness/Core/UI/Buffer gate 22/22 PASS; full Site+Social regression 69/69 PASS; compile/diff/Qt VerifyOnly PASS; tests prove missing mobile prevents Site call/Worker/provider work and current-revision Feed remains non-duplicating. Accepted runtime `ec05b77f...` is GitHub-exact/running and live Core readiness returns `ready=false` with `has_active_member_device=false` before any real send.
**External prerequisite:** sign in/link Buffer mobile for the same account/channel and enable notifications. Do not downgrade to automatic/no-link Story because owner requires a clickable Product link.
**Provider API boundary verified 2026-09-22:** Buffer's public GraphQL exposes `Channel.hasActiveMemberDevice` as a read-only capability and its documented public mutations do not expose mobile-device registration or Test Notification. A schema introspection attempt also returned `Failed to process introspection query`; do not repeat it unchanged. Device registration must therefore happen through Buffer mobile, and Test Notifications through Buffer UI after push registration.
**Prevention:** Social preflight must validate all required external delivery capabilities before the first irreversible provider action; never fabricate a device-registration mutation or retry a notification while `hasActiveMemberDevice=False`.

## ERR-49-226 - Post-quota batch exposed stale Hero revision conflicts for #152 and #178
**Date:** 2026-09-22
**Observed:** after Host quota recovery, real Batch `desktop_catalog_v85_20260922_181511` successfully uploaded 31/31 files and Bridge processed seven Products. Five succeeded, but #152 failed with `EPIC49_SYNC_CONFLICT entity=hero:2 expected=1 current=2` and #178 failed with `EPIC49_SYNC_CONFLICT entity=hero:4 expected=3 current=5`.
**Root cause class:** local Hero revision authority for these two Products is stale relative to current Site Hero state. This is independent of the resolved Host quota incident.
**Do not do:** do not repeat the same Batch unchanged; do not overwrite current Hero rows or force revisions; do not resend the whole queue.
**Correct recovery:** read current Site/Hero truth for #152/#178 and refresh only local accepted Hero revision authority before packaging; never overwrite operator-owned Product/Slider content or membership. Then take fresh Catalog backup, bounded retry only these two Products and require terminal ACK/public verification.
**Implementation/verification:** #152 Site Hero #2 rev2 and #178 Hero #4 rev5 were read read-only and match operator titles. New `refresh_hero_revision_authority()` changes only `server_slider_revision`/conflict metadata before Batch. Dedicated revision-only contract + publish integration PASS; full Site+Social regression 65/65 PASS. Real bounded retry Batch `desktop_catalog_v85_20260922_221736` completed 2/2: #152 -> Product #50/Hero rev3, #178 -> Product #51/Hero rev6, parity ok, all public Product/media HTTP 200, operator-owned digests unchanged. ERR-49-226 is CLOSED.
**Prevention:** every queued Product carrying a prior Hero ID must refresh current Hero revision authority before packaging and report verification failure per Product instead of deferring conflict detection to Bridge import.

## ERR-49-225 - Full Registration focused test initially missed stage_locks import
**Date:** 2026-09-22
**Observed:** first focused C3 test failed inside Product Wizard `_finalize_all()` with `NameError: stage_locks is not defined`.
**Root cause:** C3 reused the existing lock reader but the Product Wizard import list still imported only `STAGE_ORDER`.
**Correct fix:** import `stage_locks` from the existing stage-finalization authority. No runtime contract or database schema changed.
**Verification:** changed-condition focused rerun 3/3 PASS; related regression 82/82 PASS; compile/diff/Qt VerifyOnly PASS.
**Prevention:** UI wrappers around mature StageCore helpers must import their existing lock/readiness helpers explicitly and be exercised at widget level before GitHub promotion.

## ERR-49-224 - Site FTP batch mkdir blocked by shared-account quota; no upload/import occurred
**Date:** 2026-09-22
**Observed:** Product #536 batch `desktop_catalog_v85_20260922_171201` / UUID `32a25891-282c-498a-bed1-4498b4303059` failed in `_ensure_remote_dir()` while creating the remote pending batch directory: `550 Can't create directory: Disk quota exceeded`. Receipt chain is `desktop_batch_ready -> desktop_publish_started -> desktop_publish_failed`; there is no `desktop_ftp_uploaded` and no Bridge import. Product #588 had already failed earlier the same day with the same quota class.
**Scope:** #536 attempt contains only Product #536 and 7 local batch files. Current local queue inventory is 15 Products; the queue count is not evidence that all 15 were sent.
**Root cause:** shared Host account quota has no write headroom for the FTP pending directory. This is consistent with historical ERR-49-213, where account quota was exhausted while filesystem capacity remained healthy.
**Host-management blocker:** official 3DPrintHub reverse tunnel `127.0.0.1:22024` is absent. Windows OpenSSH is healthy and Host IP `89.39.208.237` has an established session, but current OpenSSH audit identifies it as `RetoucherTunnel`; last observed `PrintHubTunnel` acceptance is 2026-09-20. Project rules forbid using another project's tunnel. No FTP/cPanel/manual cleanup was performed.
**Correct recovery:** restore official PrintHub tunnel; inventory Host quota read-only; remove only verified disposable/incomplete/cache artifacts while preserving valid backups/media; prove write headroom; then fresh Catalog backup and retry only the bounded failed Product. Do not blindly retry the full queue and do not repeat the same mkdir while quota is unchanged.
**Unverified hypothesis:** quota may also interfere with watchdog log/lock writes, but this is not yet proven and must not be stated as root cause of the tunnel outage until Host evidence is available.
**Prevention:** Site publish diagnostics must distinguish local queue size from actual batch membership and treat quota errors as Host-capacity blockers rather than Product failures.

## ERR-49-213 - Full fresh Hero follow-up rollback hit Host quota after source bundle creation
**Date:** 2026-09-21
**Observed:** final A2X Hero follow-up pre-deploy backup created a valid ~13 MB source bundle and `.env`, then the required MySQL gzip stopped with `OSError: [Errno 122] Disk quota exceeded`. Source promotion had not started; Production remained clean at `143848eeeeac7be8ec64c33ab7aa4c95c9f42165`.
**Root cause:** the shared Host account quota did not have enough remaining headroom for another full Git bundle plus a fresh MySQL dump, even though filesystem capacity itself was healthy.
**Correct fix:** delete only the incomplete current attempt after proving it contained no database backup, leave every valid prior rollback intact, and create a fresh scoped rollback for this one-runtime-file delta. `/home/sfkilvrs/3dprinthub-deploy-backups/20260921-165608-phase50-a2x-hero-media-minimal` records the exact pre-change HEAD, exact pre-change `store/phase49_unified_sync.py`, protected `.env`, and a complete MySQL gzip; all recorded SHA256 values and gzip validation PASS.
**Verification:** after the changed backup strategy passed, exact GitHub SHA `94e53831be67368ec199c1ea5b3ab728cbfff445` deployed ff-only; migration plan stayed empty; Home/Store/Product HTTP 200; final Host worktree clean.
**Prevention:** for very small no-migration runtime deltas on a quota-constrained shared Host, a fresh checksum-verified changed-file + env + full-DB rollback may be used when the exact pre-change commit is retained in Git; never weaken the full MySQL backup requirement.

## ERR-49-212 - Hero record persisted private imported-media URL although runtime rendered Product media
**Date:** 2026-09-21
**Observed:** after successful Product #620 publish, HomepageHeroSlide #17 was active and Home rendered canonical Product media, but persisted `slide.image_url` pointed at the private `/media/store/imported-models/gallery/...` namespace and returned HTTP 404. Product #41 canonical `/media/p/620/...` image returned HTTP 200 with exact Windows SHA.
**Root cause:** unified Desktop->Hero persistence wrote ImportedPrintAssetImage working-media into the stored public Hero URL. Runtime ownership fallback protected rendering but did not normalize stored state.
**Correct fix:** resolve selected media to Product-owned ProductImage when possible, otherwise Product.main_image; persist source HTTP(S) only when no Product-owned public media exists.
**Verification:** Unified Sync/Hero ownership/import E2E 11/11 PASS; Home/Slicebox/Hero 16/16 PASS; Production `94e53831...` stored canonical Product media, revisions remained 1, and Playwright found 3 healthy Hero images with zero private imported refs/broken/page/console errors.
**Prevention:** public-media ownership must be correct both in persisted Hero state and at render/serializer boundaries.

## ERR-49-211 - Republish parity treated material-name case as a real mismatch
**Date:** 2026-09-21
**Observed:** Product #620 batch `desktop_catalog_v85_20260921_160339` / UUID `8be482aa-5469-439d-bad3-6dcab3f9f8de` rolled back only on material case mismatches such as expected `pla` vs actual `PLA` and `petg` vs `PETG`.
**Root cause:** Store resolves material rows case-insensitively, but the fail-closed republish verifier compared the raw Desktop material string with exact case-sensitive equality.
**Correct fix:** normalize only material identity with Unicode `casefold()`; keep Brand, Manufacturer, Color, stock, profile keys, media filename/SHA and numeric commerce checks strict.
**Verification:** mixed-case material regression PASS; stale-active-Variant rejection PASS; profile-price parity PASS; unified sync PASS; focused Server gate 6/6.
**Prevention:** post-import parity equality semantics must match resolver semantics for the same identity field.

## ERR-49-210 - A2X first integration gates exposed wiring gaps before any data mutation
**Date:** 2026-09-21
**Observed:** the first A2X focused run failed because the base readiness label map did not yet contain the new `slider` stage and two new fallback paths referenced helper names that did not exist in those modules. The first Django gate also hit the already-documented isolated-worktree missing-`.env` condition from ERR-49-155.
**Impact:** none to Catalog data, Site Product, Host or Production. Failures occurred in Local tests before any real Product mutation.
**Correct fix:** add the Slider label to the base seven-stage readiness map; reuse each module's existing JSON helper instead of introducing an undefined helper; for Django tests temporarily copy the canonical ignored Local `.env` exactly as documented by ERR-49-155 and remove it immediately afterward.
**Verification:** failed subset rerun 6/6 PASS; focused A2X gate 33/33 PASS; Server gate 9/9 PASS; broad current gate 115/116 with only the separately documented baseline ERR-49-203 failure; compile/diff/Django/no-drift/Qt VerifyOnly PASS.
**Prevention:** when adding a canonical stage, update label/order/readiness contracts together; reuse local helper contracts rather than assuming shared helper names; isolated worktrees must follow the documented temporary ignored-`.env` test procedure without committing secrets.

## ERR-49-209 - W4.1 first accepted UI still left unknown axes and Source Profiles without Local Filaments
**Date:** 2026-09-21
**Observed:** owner runtime on pushed W4.1 commit `436d34f2...` showed Hydra Small with Height=12cm but Length/Width as `نامشخص`, and saving failed because the Source Profile had no concrete Local Filament selected.
**Root cause:** the first W4.1 contract deliberately preserved only factual axes and kept W4 Local Filament mapping as a separate preview. The owner clarified the operational rule: a single Source size dimension should be copied to all three Profile axes, and a Source material family such as PLA should preselect every compatible active Local PLA offer in the created Profile.
**Correct fix:** derive operational dimensions through an explicit owner equal-dimension rule while preserving factual-axis provenance; hydrate Source Ledger Profiles with all active exact-family Local Filament offers during import/repair; replace brandless Source placeholders only when concrete Local matches exist; preserve operator concrete choices.
**Verification:** focused Source/Profile+dimension 15/15 PASS, W4 mapping 5/5 PASS, mature Commerce/Profile+W3/W4/W4.1 59/59 PASS, retained media/site 83/83 PASS, compile/diff/Qt VerifyOnly PASS. Read-only real-Catalog simulation gives #628 Small=12×12×12 + 16 PLA, Large=18×18×18 + 16 PLA, #625 Profile 1=5×5×5 +16 PLA preserved, Profile 2=16 PLA ready for 4×4×4 fallback.
**Prevention:** Source-fact storage and operator-ready Profile defaults are separate contracts. Owner-approved operational derivation must carry explicit provenance, and material-family Source imports must be regression-tested against the real Local Filament registry before runtime acceptance.

## ERR-49-208 - W4.1 real Hydra meta used compact numbered-section text after the unit
**Date:** 2026-09-21
**Observed:** synthetic Description tests passed, but the first real latest-capture Hydra gate returned two Source Profiles with no dimension enrichment.
**Root cause:** MakerWorld compacted the second value as `Large Version: Height = 180 mm2. Support Removal Tips`. The initial dimension regex required a word boundary after `mm`; because the next character was digit `2`, the Large match was rejected. With only one size record for two Profiles, ordered binding correctly failed closed.
**Correct fix:** keep strict unit parsing but allow an immediately-following numbered-list marker such as `2.`/`2)` as a valid unit terminator. Add the exact compact MakerWorld string as a regression.
**Verification:** focused W4.1 10/10 PASS and the exact latest Hydra capture returns Profile 3595936 -> Small height 12cm and Profile 3596024 -> Large height 18cm.
**Prevention:** Source parsers must regression-test minified/concatenated metadata boundaries, not only clean rendered Description text; ambiguous count mismatches continue to fail closed.

## ERR-49-207 - W4.1 temporary Windows python -c probes lost quoting before application execution
**Date:** 2026-09-21
**Observed:** two temporary read-only/test harness invocations embedded Windows paths/module names inside PowerShell `python -c`; shell quoting stripped Python string quotes and produced SyntaxError/NameError before DB/application execution.
**Impact:** none. No Catalog DB, Git source, Host or Production mutation occurred.
**Correct fix:** move multi-line operational probes/test manifests into short temporary UTF-8 Python files outside the repository, set verified `PYTHONPATH`, execute them, then delete them.
**Verification:** real Hydra parse and Commerce/Profile gates run successfully from temporary files; W4.1 focused/59-test/83-test gates all PASS.
**Prevention:** do not use PowerShell `python -c` for complex Windows paths or multi-module manifests; use temporary scripts after the first quoting failure and never repeat the unchanged failed form.

## ERR-49-206 - Product #625 had a failed publish attempt before W4 acceptance; Site revision stayed 11
**Date:** 2026-09-21
**Observed:** Product history and the owner screenshot show batch `26aa571c-1a0c-4ad4-9431-65e74c27d94f` with `qt_bulk_site_publish ok=0`. The dialog reports the ACK was received but the Product was not confirmed in the public Store.
**State impact:** Local #625 is now `workflow_status=batched`, `needs_update=1`, `upload_ready=1`; Site identity remains Product #39 revision 11. No successful revision advance occurred.
**Boundary:** this failed attempt predates W4 real Preview and is not caused by W4. W4 is read-only and preserved the exact pre-preview Product state byte-for-byte.
**Correct response:** do not silently retry/publish during W4. Preserve the failed batch evidence and keep Site revision 11 until a separate publish-recovery gate explicitly investigates the public-Store confirmation failure.
**Verification:** W4 real Preview kept Source facts, Ledger, Stage locks, Product identity/revision and product-history count unchanged; exact preview result is 2 Profiles / 3 Source slots / 48 PLA candidates / exact HEX=0.
**Prevention:** a failed public Store confirmation must remain a separate publish-recovery task; review/mapping phases must never auto-retry it.

## ERR-49-205 - First W4 real-preview probe reported false FAIL because zero was treated as missing
**Date:** 2026-09-21
**Observed:** the first exact-SHA W4 Preview printed the correct values (2 Profiles / 3 slots / 48 candidates / exact HEX=0, unchanged snapshots) but the probe summary printed `PASS=False`.
**Root cause:** the temporary assertion used `value or -1`; the valid value `0` for exact HEX was therefore replaced by `-1`.
**Impact:** none. The W4 application code, Catalog DB and Product state were not mutated.
**Correct fix:** distinguish `None` from numeric zero explicitly in the probe and rerun under the changed condition.
**Verification:** corrected button-level probe returns `W4_REAL_PREVIEW_PASS=True` with exact HEX=0 and byte-for-byte unchanged Source/Ledger/locks/Site identity/history count.
**Prevention:** operational probes must not use truthiness fallbacks for counters where zero is a valid acceptance value.

## ERR-49-204 - W4 rollback-ref bootstrap PowerShell parser typo before Git mutation
**Date:** 2026-09-21
**Observed:** the first rollback-ref helper command used an invalid PowerShell expression around `git show-ref` and stopped before creating/changing any Git ref.
**Impact:** none. No Git ref, source, DB or runtime mutation occurred.
**Correct fix:** split `git show-ref --verify --quiet` and `$LASTEXITCODE` evaluation into separate PowerShell statements, then create/verify the rollback ref only if absent.
**Verification:** `backup/pre-phase50-a2w-w4-material-mapping-20260921` was created/verified at exact `eda42e84b0bf39052fb76aa3c74e35b7dd0a85e5`.
**Prevention:** do not embed shell command execution inside boolean assignment syntax that PowerShell cannot parse; verify ref existence and ref SHA explicitly.

## ERR-49-203 - Two broader Commerce regression assertions are stale on the clean W4 baseline
**Date:** 2026-09-21
**Observed:** a broad 51-test Filament/Profile/Commerce + W3/W4 probe produced two failures: duplicate Profile identity behavior and a legacy Manufacturer-vs-Brand authority assertion.
**Impact:** no #625/DB/Site mutation. Both failures occur in paths untouched by W4.
**Root cause boundary:** both failures reproduce identically on a clean detached worktree at exact pre-W4 baseline `eda42e84b0bf39052fb76aa3c74e35b7dd0a85e5`.
**Correct response:** do not mutate W4 source or weaken current behavior to satisfy stale baseline assertions. Exclude only these two proven-baseline failures from the W4 commerce acceptance set.
**Verification:** corrected mature Filament/Profile/Commerce + W3/W4 gate passes 49/49; W4 focused passes 5/5; retained media/site gate passes 83/83.
**Prevention:** before assigning a broad-suite failure to a new phase, reproduce the exact failing test on the clean pre-phase baseline.

## ERR-49-202 - W4 read-only inventory probe assumed `active` instead of actual `is_active`
**Date:** 2026-09-21
**Observed:** the first Local Filament inventory query failed because it filtered on a guessed `active` column.
**Impact:** none; query was read-only and no DB mutation occurred.
**Root cause:** schema contract was not taken from `PRAGMA table_info(available_filament_offers)` before the query.
**Correct fix:** inspect the actual table schema and use `is_active=1`; the later probe used explicit read-only SQLite mode and no integrity write path.
**Verification:** real Local inventory reports 16 active PLA offers and the current PLA operating prices/rates used by W4 review.
**Prevention:** read SQLite table schema before operational ad-hoc queries; never infer column names from model/UI terminology.

## ERR-49-201 - Named 83-test A2W regression gate was initially reconstructed with two obsolete legacy modules
**Date:** 2026-09-21
**Observed:** the first W3 retained-regression run executed 83 tests but produced one legacy image-limit assertion (`DEFAULT_IMAGE_LIMIT` expected 10 while current runtime is 5) plus three Windows `WinError 32` temp-SQLite cleanup errors from the old SEO-execution module.
**Impact:** no Product/DB/Host mutation. All W3 focused tests were already green, and the four failures match the exact wider legacy pattern previously reproduced on clean A2U and documented under ERR-49-198.
**Root cause:** the named historical gate was documented by count/purpose but not by an explicit module manifest. During reconstruction, two obsolete modules (`test_epic49_phase49_3h_seo_execution`, `test_epic49_phase49_3h_image_limits`) were substituted for the actual stable A2V runtime/slider contract modules.
**Failed attempt:** the incorrect 83-module set was run once. It was not repeated unchanged after the mismatch was identified.
**Correct fix:** reconstruct the historical A2V gate from commit/test counts: current stable Image/SEO/Packaging/Republish core is 74 tests after the two W1/W2 additions; add `test_phase49_3i52b_bidirectional_site_sync` (7) and `test_phase50_a2w_product_media_sync` (2). The stable core uses `test_v871_slider_seo` and `test_v8_runtime_contract`, not the two obsolete modules above.
**Verification:** corrected retained gate ran exactly 83 tests and passed 83/83. W3 focused 5/5, py_compile, diff-check and RUN_QT VerifyOnly also PASS.
**Prevention:** every named/count-based regression gate must record its exact test-module manifest alongside the count so a later continuation never reconstructs it by semantic guesswork.

## ERR-49-200 - A2W standalone Truth-Sync probe bootstrap failed twice before DB access
**Date:** 2026-09-21
**Observed:** the first standalone #625 Truth-Sync probe failed with `ModuleNotFoundError: app`; after correcting import-path context, the second failed because `Database(...)` received a `str` instead of the repository contract `Path` object.
**Impact:** none to Product/Site state. Both failures occurred before the Truth Sync method could run; no FTP, Bridge import, publish, revision change or DB mutation occurred. The already-created integrity-checked Catalog rollback remained valid.
**Root cause:** the temporary probe lived outside `catalog_center`, so Python did not inherit the application package path; the follow-up invocation then used the wrong constructor type for `app.db.Database`.
**Failed attempts:** external probe without explicit `PYTHONPATH`; then explicit `PYTHONPATH` but `Database(str_path)`.
**Correct fix:** set `PYTHONPATH` explicitly to the canonical `catalog_center` root and construct `Database(Path(...))`. Do not repeat either failed command unchanged.
**Verification:** corrected probe completed real #625 Truth Sync successfully: DB=2, Local=3, selected=1, Site=1, mismatch=0, recovered=0; Site Product #39 revision 11, selection, Primary and dirty flags were unchanged.
**Prevention:** standalone operational probes must import through the verified repository package root and must follow actual constructor contracts from source instead of assuming generic string-path APIs.

## ERR-49-199 - Revision 11 completed before the planned fresh pre-republish Catalog snapshot
**Date:** 2026-09-21
**Observed:** the controlled #625 same-identity publish completed successfully as Product #39 revision 11 before the planned fresh Catalog snapshot immediately preceding that publish had been captured.
**Impact:** publish integrity itself is verified, but the requested operation ordering cannot truthfully be claimed. Creating revision 12 only to recreate the ordering would add an unnecessary Production mutation and violate the one-controlled-republish intent.
**Correct response:** do not re-publish. Retain the already integrity-checked revision-10 A2V rollback `D:\projects\3dprinthub-backups\phase50-a2v-image-authority-20260921-005619\catalog-before-a2v.sqlite3` (SHA256 `20bd5c1d6b776c14e90d9aa91a9866b909121614d9e042faeb252cbac75c0e9e`) and create an integrity-checked post-revision-11 snapshot `D:\projects\3dprinthub-backups\phase50-a2v-post-rev11-20260921-081557\catalog-after-rev11.sqlite3` (SHA256 `1f6ecd4c9250ed9b46e612489294fea0f1fe7c6b57a6a02aa1493b738bc72869`).
**Verification:** revision 11 ACK is successful with `republish_parity.ok=true`; Local/Batch/Production/public media SHA parity is exact; public Product and image are HTTP 200; Production has exactly three active current CC Variants.
**Prevention:** future controlled Product publish tooling must make rollback snapshot creation/integrity verification a programmatic precondition of the publish action rather than a manually sequenced operator step.

## ERR-49-198 - Re-publish revision advanced while Windows re-sent the previous image bytes
**Date:** 2026-09-21
**Observed:** #625 updated the same Site Product #39 to revision 10, but the live images remained unchanged. Production hashes proved revision 10 received the same finalized WebP bytes as before rather than serving stale cache.
**Root cause:** Local #625 had a split image authority: persisted `selected_images_json` contained `local://04.webp` and `local://05.webp`, while canonical `images_json` contained only the source-page screenshot. The old media gate validated SEO finalization for the selected URLs but never required selected URLs to belong to canonical authority. The Qt label `انتخاب` also represented temporary bulk-operation selection, which could be mistaken for persisted Site selection. Refetch rules could additionally treat a persisted Site-selected numbered local file as replaceable source cache.
**Correct fix:** A2V separates `ویرایش` from `ارسال سایت`, requires Site-selected URLs to be a subset of canonical image authority, preserves all persisted Site-selected local images through refetch regardless of legacy numbered filename, and keeps explicit manual/screenshot media Product-owned.
**Data repair:** after integrity-checked backup, #625 `images_json` was repaired only as the union of existing canonical media plus its already-persisted Site selections. Selection, primary, SEO metadata, server identity, revision and dirty state were unchanged; post-repair media gate PASS.
**Verification:** stable Image/SEO/Packaging/Republish 72/72 PASS; compile/diff/Qt VerifyOnly PASS; exact GitHub source `4e69ed6a...`. A wider legacy test probe’s 1 fail + 3 SQLite teardown errors reproduce identically on clean A2U baseline and are not A2V regressions. Real acceptance then persisted exactly `local://04.webp`, republished #625 in place to Product #39 revision 11, and proved exact SHA256 `cf6f0422f0cde915e9203ddbca6564df694fb4b6a97320e1af0e7f4117c68fff` across Local final SEO, Batch, Production storage and public HTTPS download.
**Prevention:** never equate temporary editing selection with publish selection; persisted Site-selected media must always be canonical, refetch must preserve operator Site selections, and every image-changing republish must prove Local final bytes = Batch bytes = Production stored bytes before closure.

## ERR-49-197 - Desktop launcher selected a newer Social branch that was older in Windows UI history
**Date:** 2026-09-20
**Observed:** owner opened the Desktop Catalog Center and saw the older image-workspace layout again; the repaired image display/SEO/screenshot controls were missing. Sending #625 then surfaced `PRODUCT_MEDIA_NOT_FOUND_IN_PUBLIC_HTML` again.
**Root cause:** the shortcut was retargeted to `D:\projects\3DPrintHub-a2t-windows`. That worktree had newer A2T Social changes but did not descend from the actual latest Windows lineage. The latest Windows fixes were already in GitHub under `f1b58645...`, including `20f483af/91d4c188/00f16237/a52cd52a/aaa5cb9f/ea1a4a79`.
**Correct fix:** build A2U from `f1b58645...`, preserve its UI, port only bounded Social v5 changes, run explicit Gallery/SEO/Republish/Social/Qt gates, push the exact source, and only then retarget the Desktop launcher.
**#625 recovery:** the old app had already imported Site Product #39 revision 9. The stale verifier rejected canonical media afterward. Fresh backup was taken; latest verifier returned Product 200 plus 2/2 media 200; Local state was reconciled without re-import.
**Verification:** Image/SEO/Republish 74/74 PASS; Social 35/35 PASS; Qt/RUN_QT verify PASS; running A2U window title v8.9.11; Production read-only revision 9 with 3 active Variants and 2 ProductImages.
**Prevention:** Windows operator worktree selection must be based on ancestry against the latest accepted Windows UI fixes, not commit date alone. Never retarget the Desktop launcher until gallery/image/SEO/screenshot regression gates pass on the exact pushed SHA.

## ERR-49-184 - Social false-free sanitizer could emit literal backreference and malformed tags
**Date:** 2026-09-20  
**Observed:** A2Q source audit found that punctuation cleanup used a replacement equivalent to literal `\\1`, so text such as a removed free claim before Persian punctuation could leak `\\1` into social copy. Persian false-free removal could also leave malformed hashtag residue such as a truncated download tag, and English free-download/free-print forms were not covered.  
**Root cause:** replacement escaping was wrong and the sanitizer treated hashtag fragments as ordinary prose after claim removal. The false-free vocabulary was also too narrow.  
**Correct fix:** use the actual regex backreference `\1`; add bounded English claim patterns plus Persian `مجانی`; reject false-free hashtag candidates before normalization; keep unrelated terms such as `Freestyle` untouched.  
**Verification:** exact GitHub WIP source read-back at `1c77f671...` and rollback diff PASS; focused logic was independently exercised before commit. Canonical Windows full Social/Buffer/Story + Qt regression is still required before promotion.  
**Prevention:** social policy changes that touch claim filtering must carry Caption + hashtag + ALT + Story regression and a non-target-word preservation case in the same commit. Do not promote Social WIP without canonical Windows regression evidence.

## ERR-49-183 - Instagram SEO v4 first regression run retained the old policy-version assertion
**Date:** 2026-09-20
**Observed:** the first A2Q social regression run executed 32 tests and failed exactly one stable-receipt assertion because it still expected instagram-product-v3-20260919 after the deliberate policy bump to v4.
**Root cause:** test contract staleness caused by the intentional policy-version change; no provider, caption, media, receipt or runtime behavior failed.
**Correct fix:** update only the version assertion to instagram-product-v4-20260920 and rerun the same social scope after the condition changed.
**Verification:** changed-condition social suite 32/32 PASS; Qt VerifyOnly PASS.
**Prevention:** whenever the persisted social policy version changes intentionally, update the receipt-stability test in the same commit; never weaken content/duplicate/media assertions to make a version bump pass.

## ERR-49-183 - Buffer could not ingest valid social PNGs from the current Site origin
**Date:** 2026-09-19
**Observed:** after the WebP-specific compatibility fix, #625 generated valid Buffer-only PNG derivatives. Direct owner-side HEAD/GET returned HTTP 200, Content-Type image/png, stable Content-Length and cache headers, including with a Buffer-like User-Agent, but Buffer createPost still rejected both images as unreadable. No Feed receipt/post was created by that failed attempt.
**Boundary evidence:** 3dprinthub.ir resolves to 89.39.208.237 and the media response is fronted by BitNinja-WafPro via Caddy. The exact origin/WAF rule responsible is not proven because no provider request log was available. The exact same PNG bytes mirrored to public raw.githubusercontent.com were accepted immediately by Buffer; Feed and Story both reached sent.
**Correct fix:** separate canonical Product media from provider-delivery media. Keep Product WebPs and SEO filenames on 3DPrintHub unchanged, and publish only generated social derivatives through a configurable Buffer media host. The verified launch host is a dedicated public GitHub branch/worktree, with deterministic per-revision paths, source URL/SHA manifest, clean-worktree guard, exact remote-head check and public image MIME verification.
**Real verification:** Feed id 6aaed28f6e039ccbc8221fa8 -> https://www.instagram.com/p/DdepEh3if0N/; Story id 6aaed29a7fcdd8931977c3f1 -> https://www.instagram.com/stories/3dprinthub_ir/3989806967019651799. Feed receipt was later reconciled from sending to sent without repost.
**Prevention:** Site HTTP validity is not sufficient evidence that an external social provider can ingest the URL. Provider-delivery assets require a provider-compatible public host and a real external acceptance gate. Never weaken canonical Site-media checks or duplicate the Product post to test status.

## ERR-49-182 - Failed re-publish erased the last verified Windows Site identity
**Date:** 2026-09-19
**Observed:** after a controlled #625 retry failed closed on a parity mismatch, Local Product #625 changed from the existing Site linkage (#39 / revision 7) to `server_product_id=0`, `server_product_revision=0`, and replaced its good public ACK with the failed ACK. The Site transaction itself had rolled back and Product #39 still existed.
**Root cause:** the Windows bulk-publish ACK handler wrote incoming identity/revision fields unconditionally. A failed ACK normally contains no Product/slider ids, so zeros overwrote the last verified linkage.
**Correct fix:** always record the failed receipt/error, but update Site identity/revisions and canonical `server_ack_json` only when `ack_item_confirms_publish()` succeeds. On failure preserve the previous verified asset/Product/slider identity and ACK so the next retry stays on the same Site Product.
**Verification:** dedicated regression plus full Site-publish module 19/19 PASS; Instagram/social adjacent suite 27/27 PASS; diff-check PASS.
**Prevention:** failure diagnostics belong in receipts/error state; never treat absent ids in a failed transaction as authoritative deletion of an existing remote identity.

## ERR-49-179 - Successful re-publish left stale legacy Variants active
**Date:** 2026-09-19
**Observed:** Product #625 re-published successfully to the same Site Product #39 at revision 7 with `republish_parity.ok=true`, three current Desktop profiles and current media, but the public Store still exposed stale weight/material/price behavior.
**Real Production evidence:** Product #39 had 190 historical Variant rows and five active rows. Three active `CC-P39-...` rows correctly carried current Windows values (60 g, material+support 110 g, 180 min, 1,095,000/1,215,000 Toman). Two stale `EP49-3F...` rows 5940/5945 were also active with 1 g, 60 min and 104,500 Toman.
**Root cause:** Desktop profile synchronization only deactivated removed Desktop-managed rows; the older EP49-3F generator ran in another compatibility path and legacy/manual rows could survive as active. The ACK parity counted current Desktop profiles but did not reject unrelated active Store Variants.
**Correct fix:** when a current Windows `sales_profiles_json` exists, treat it as the sole active commerce matrix. Upsert current CC rows, deactivate every Product Variant not in that exact active-code set, retain rows for historical FK/order rollback, and fail closed if a non-CC row remains active or active CC count differs from Windows.
**Image boundary:** Site ProductImage sync already rebuilds exactly the current selected-image set. The reported new image did not appear because Local #625 still contains only two selected images; no third selected image is present to publish. Windows now exposes an explicit local-file add/select path so this cannot silently depend on an indirect image workflow.
**Verification:** compile/check/no-drift PASS; Server profile/import/admin-sync 15/15 PASS; Windows image workspace 25/25 PASS.
**Prevention:** a successful re-publish must verify *exclusive* active Variant authority, not only existence/count of expected CC rows. Never merge stale active commerce rows into a current Windows snapshot.

## ERR-49-178 - Buffer could not read canonical Product images despite public HTTP 200
**Date:** 2026-09-19
**Observed:** first real #625 Buffer Feed attempt after Story rendering was repaired submitted the two canonical Product image URLs and failed before a post id with `Invalid post: Image could not be read from its URL., Image could not be read from its URL.`. Both URLs independently returned HTTP 200, Content-Type image/webp and the expected byte sizes; no Feed receipt existed before or after the failed call.
**Root cause boundary:** the Product media is valid for the Site, but Buffer's remote media ingestion did not accept/read those canonical WebP-through-application URLs reliably. This is a provider-ingestion compatibility boundary, not a reason to weaken Site media verification or rename the Product assets.
**Correct fix:** generate Buffer-only PNG derivatives from the already-verified canonical images, normalize only when aspect/width requires it, host them as stable public static social assets, verify them over HTTPS, submit them to Buffer and retain canonical Product URLs separately as audit source media.
**Verification:** compile + feed-asset/Buffer/Story/Instagram focused gate 21/21 PASS. No Product DB/media/SEO mutation is part of this fix.
**Prevention:** external social providers must receive provider-compatible stable media URLs; Site media validity alone is not sufficient evidence of provider ingest compatibility.

## ERR-49-177 - Windows Chrome launcher returned before companion Story screenshot was complete
**Date:** 2026-09-19
**Observed:** after #625 Site/public reconciliation and Buffer connectivity PASS, the first real social action stopped before Feed submission with `رندر Story خروجی معتبر تولید نکرد.`. Existing Story PNGs were 1080x1920 but only 18,240 bytes and sampled almost entirely white (mean RGB ~254.7).
**Root cause:** on this Windows runtime, invoking `chrome.exe --headless ... --screenshot` directly from Python can return success from Chrome's launcher process before the actual headless child has written the screenshot. A system-temp Chrome profile/workspace could then be cleaned up before the child finished. The file-size guard correctly failed instead of publishing a blank Story.
**Correct fix:** keep a per-Product/revision render workspace under LocalAppData, use an isolated Chrome `--user-data-dir`, remove any stale PNG before each render, invoke Chrome through PowerShell `Start-Process -Wait`, and bounded-poll for a >=50KB screenshot before workspace cleanup.
**Verification:** real #625 render PASS at 1080x1920 / 1,178,712 bytes / 6,984 sampled colors / mean RGB ~65.8,60.1,56.1. Social/Story/publish 53/53 PASS; Qt VerifyOnly/compile/diff-check PASS.
**Prevention:** never treat the Chrome launcher process exit as screenshot completion on Windows. Story publication must retain the existing size/content gate and use an isolated, waitable render process/workspace.

## ERR-49-176 - Windows public verifier lagged compact Product media namespace
**Date:** 2026-09-19
**Observed:** real #625 receiver import passed full transactional Product parity and returned Product #39 revision 6, but Windows kept the Product in failed/dirty state because public verification first reported no Product media. After discovering the canonical paths, the Server-side URL issue was separately corrected so `/media/p/...` returns HTTP 200/image.
**Root cause:** Windows `STORE_MEDIA_RE` still recognized only legacy `/media/store/products/...`, while ERR-49-173 intentionally moved canonical repeated-publish media to compact `/media/p/<desktop-id>/<sha12>/<seo-basename>`.
**Correct fix:** recognize exactly legacy public Product media plus canonical `/media/p/`; do not widen acceptance to imported working-media.
**Verification:** dedicated checker regression 3/3 PASS and maintained publish/social scope 40/40 PASS. Live Product HTML contains two canonical #625 media URLs.
**Prevention:** any public media namespace change must update receiver storage, public route and Desktop post-publish verifier in one acceptance matrix.

## ERR-49-175 - Companion Story lacked deterministic Highlight target and final style evidence
**Date:** 2026-09-19
**Observed:** companion Story infrastructure and Buffer receipts existed, but Product rows such as #625 had no explicit `instagram_highlight`; receipt target could therefore be empty. Runtime Story used IRANSans but still reported an older `..._v2` style ID instead of the final documented IRANSans style ID.
**Root cause:** social policy had no approved category-to-Highlight classifier, and the runtime evidence constant lagged behind `STORY_STYLE_STANDARD.md`.
**Correct fix:** add the approved eight-Highlight taxonomy, resolve explicit approved override first, then Product category slug, then semantic tags/title fallback. #625 `toys-games` deterministically resolves to `اسباب بازی`. Story runtime now reports `3dprinthub_instagram_gold_navy_v2_iransans`.
**Verification:** Windows pricing/social/feed/story suite 19/19 PASS plus Story asset and retry-idempotency coverage. Product link remains in Buffer metadata and visibly rendered Story copy; nationwide shipping is present.
**Platform limitation:** Buffer public API exposes Story creation but no Add-to-Highlight mutation. Receipt records `highlight_target` and `highlight_status=operator_required`; private Instagram APIs are prohibited.
**Prevention:** every successful Product Story must have a non-empty approved Highlight target and final style ID before social closure.

## ERR-49-174 - Active PLA service rates drifted and Site pricing diverged from Catalog formula
**Date:** 2026-09-19
**Observed:** real #625 republish reached the new strict parity gate and rolled back with Windows range 705000-825000 versus Site 104500-675000 instead of falsely succeeding.
**Root cause A:** current active PLA inventory drifted to print_hourly_rate=0 and supervision_hourly_rate=70000. The integrity-checked post-default preview from 2026-09-14 proves the owner-approved PLA defaults are purchase 3500000, sale 4500000, print 150000/hour and supervision 50000/hour while preserving offer-specific preheat.
**Root cause B:** Site dynamic pricing for Desktop-managed Variants did not consume the same complete sales-profile inputs as Catalog and public range could include unrelated historical/manual Variants.
**Correct fix:** Windows refreshes selected Product Filament/Profile snapshots from current inventory before Ready/Publish. Server `CC-P...` Variants use the same Catalog formula: material sale cost + print + supervision + preheat + assembly, with exact part/support weights and profile inputs. If Desktop-managed Variants exist, they alone define the Catalog Product public range.
**Verification:** Server targeted pricing/mapping/API 5/5 PASS with no migration drift; Windows Ready-refresh regression PASS. Owner-default data repair is intentionally deferred until a fresh Catalog backup is taken after the tested source is committed.
**Prevention:** publish must refresh mutable Filament facts immediately before Batch creation and strict parity must compare the resulting Site range; never weaken parity to accept divergent pricing.

## ERR-49-172 - Screenshot SEO fields empty and edited source image could re-publish stale finalized WebP
**Date:** 2026-09-18
**Observed:** owner opened per-card SEO on a manually captured Screenshot and Alt/Title/Caption/Keywords were empty. Separately, editing a local image file and re-sending the already-published Product could leave the previous live image bytes on Site.
**Root cause A:** manual Screenshot can exist as a trusted editable local image before image metadata has ever been built. The per-card SEO dialog only read stored metadata and had no Product-SEO fallback. Non-Site metadata could also be lost when the selected-image finalizer rewrote the metadata list.
**Root cause B:** publish media gate validated the finalized WebP and its own hash/signature, but did not compare current selected source bytes with the stored `original_sha256`. A source file edited after finalization could therefore remain hidden behind a still-valid old final WebP.
**Fix:** seed missing single-image SEO editor values from Product semantic SEO; persist unselected editable image metadata without toggling Site membership and keep it non-publishable until selected. For Ready/Send, detect source-byte drift only on previously-finalized selected media and automatically re-finalize that media before preflight. Genuinely missing/unfinalized media remains fail-closed.
**Verification:** focused Image+Publish 41/41 PASS; current-contract 77/77 PASS; final broad Windows 145/145 PASS; Qt VerifyOnly, compile, Django check, no migration drift and diff-check PASS.
**Prevention:** per-card SEO must support metadata-less trusted local images; selected publish media must validate both final bytes and source-to-final freshness. Never auto-select a Screenshot or weaken the incomplete-media fail-closed gate.

## ERR-49-171 - Direct Windows edits after publish did not always queue the existing Site Product for update
**Date:** 2026-09-18
**Observed:** owner could publish a Product, edit it in Windows, send again and still see stale Site data. The Site importer already had update-in-place logic, so duplicate creation was not the primary defect.
**Root cause:** Stage-owned edits correctly passed through `StageCore.update()` and marked an uploaded Product `needs_update=1`, but several explicit direct mutation boundaries bypassed StageCore: Product operator fields, image metadata/SEO, SEO renumber, image removal and manual Screenshot capture. Those writes could preserve `workflow_status=uploaded` with `needs_update=0`, so normal work-queue/update semantics did not reflect the local change.
**Fix:** add one shared local dirty marker used only by explicit operator mutations. If an existing server identity is present and the Product was uploaded, keep the same server identity and set `needs_update=1, upload_ready=0`. The existing Stage-7 Send action then explicitly requeues through revision guard and the mature Batch/FTP/Bridge importer.
**Server verification:** strengthened unified-import E2E publishes once, edits title/description/meta SEO and finalized image, reimports the same source/Desktop identity and verifies the same Asset PK and Product PK are updated, Product count remains one, and public fields/media refresh in place.
**Windows verification:** published image SEO edit and direct Product operator edit both preserve server IDs and set `needs_update=1`; Image workspace 22/22, Windows/Site 59/59, unified importer 3/3 and profile/identity/admin-sync 23/23 PASS.
**Prevention:** every explicit post-publish Windows mutation must either use StageCore or invoke the shared dirty marker. Never change Site identity merely to force an update, and never bypass revision guard on re-publish.

## ERR-49-170 - Real Site ACK stored images as a count and crashed Instagram media parsing
**Date:** 2026-09-18
**Observed:** real Product #309/#301 Instagram preflight raised `TypeError: 'int' object is not iterable` although Mock social tests passed.
**Root cause:** `canonical_site_payload()` assumed `server_ack_json.images` was a list. Real Site ACK uses `images=<count>` and stores verified public media under `public_http_checks.images`; that verified list may also contain unrelated cross-Product checks.
**Fix:** accept list-shaped legacy/public media when present; otherwise read `public_http_checks.images`, keep the verified main image first and filter fallback URLs to the current Product slug before carousel construction.
**Verification:** dedicated real-shape regression PASS; real #309 returns 5 owned media and #301 returns 3 owned media; combined social/Qt gate 82/82 PASS.
**Prevention:** social regressions must include the current strict Site ACK shape, not only synthetic list-shaped ACK fixtures.

## ERR-49-169 - Product profile identity contained corrupt/Persian values where ASCII identity is required
**Date:** 2026-09-18
**Observed:** real Product #625 displayed `???????` for Profile name and size; canonical ledger itself stored those corrupt values and flattened 64 combinations inherited them.
**Root cause:** profile normalization accepted arbitrary localized/corrupt strings for the two identity fields and older fallback/bootstrap paths generated Persian Profile identity.
**Fix:** Profile name and size are now normalized as ASCII-only identity. Invalid/corrupt/localized values fall back to `Standard`, `Profile N`, or factual numeric `L x W x H cm`; Material/Color/content remain localized and untouched.
**Verification:** Product #625 read-only runtime acceptance reports `Standard / Standard`, ASCII true, one production row and all 64 material options preserved; combined Catalog/Qt gate 82/82 PASS.
**Prevention:** Profile identity fields are transport/selection identifiers and must remain ASCII; Persian remains appropriate for customer-facing Product/Material/Color copy.

## ERR-49-168 - Product Admin change page 504 from full ProductVariant inline expansion
**Date:** 2026-09-18
**Observed:** Production Product edit page intermittently returned 504, especially for Products with many generated variants.
**Root cause:** final Product Admin composition kept the entire `ProductVariantInline` in every Product change page even though a dedicated Variant/Profile admin already exists. A Local 37-Variant benchmark produced 781 queries, 1.399s and 892118 bytes of HTML.
**Fix:** remove only `ProductVariantInline` from Product change pages; preserve ProductImage/Compatibility/FAQ/Profile inlines and keep all Variant/Profile editing in the existing dedicated ProductVariant admin linked from the Product workspace.
**Verification:** same Local page after final composition is ~60-63 queries and 277103 bytes; focused Site/Admin 17/17 PASS. Production verification remains pending the guarded deploy.
**Prevention:** do not embed unbounded generated commerce rows in Product change forms. Large child collections must use dedicated filtered admin surfaces.

## ERR-49-166 - Planned filenames diverged from mature English source-title naming
**Date:** 2026-09-18
**Observed:** finalized images could retain English source-title filenames while extra/unfinalized local images displayed a different planned filename derived from Persian Product SEO title, creating mixed naming in one Product.
**Root cause:** `9b006bb...` changed `planned_seo_filename()` authority from `source_title` to `seo_title_fa or source_title` while older finalized metadata remained source-title based.
**Fix:** restore only filename planning to the mature source-title-first ASCII rule. Leave Product-specific Alt/Title/Caption/Keywords, AI refresh, operator overrides and finalizer behavior unchanged.
**Verification:** Product #301 planned and existing finalized filename both resolve to `christmas-tree-minimalistic-japandi-decor-3d-print-01.webp`; Alt/SEO title/caption/12 keywords remain intact; 97/97 regression PASS.
**Prevention:** filename authority and semantic image metadata are separate contracts. Do not change filename authority while modifying Product SEO/content unless the owner explicitly requests a naming-policy change.

## ERR-49-167 - Sparse gallery had no lower scroll reserve
**Date:** 2026-09-18
**Observed:** with few images, the large gallery content height collapsed to the factual row count, so lower card controls could become awkward/unreachable and the owner had no extra scroll room.
**Fix:** large Stage-3 gallery always reserves at least four 206px rows plus spacing, even with zero/few images.
**Verification:** empty gallery host minimum 842px vs 652px viewport, scrollbar max 190; focused and 97-test gates PASS.
**Prevention:** Stage-3 scroll capacity is a minimum workspace contract, not only a function of current image count.

## ERR-49-165 - Gallery-area request was incorrectly implemented by enlarging each image card
**Date:** 2026-09-18
**Observed:** Stage 3 showed only two huge images at a time; even after scroll fixes, filenames and per-image controls were inconvenient because each card itself was ~780px tall.
**Root cause:** the owner request to make the image-review *area* larger was conflated with making each image/card larger. Two large columns consumed the viewport instead of increasing information density.
**Correct fix:** use three columns and fixed 206px review cards; keep preview around 90px high; keep SEO filename visible; compact metadata and per-image actions; use a 670px gallery that displays three complete rows (nine cards) before scrolling.
**Verification:** isolated 9-card viewport proves row-three bottom 634 <= viewport 652 and filename bottom 576 <= viewport; 12-card wheel-scroll gate PASS; maintained Qt suite 68/68 PASS.
**Prevention:** distinguish viewport size from card/media size. For owner image-review UX, acceptance must assert columns, number of fully visible rows, filename visibility and action-row visibility—not only card width/height or scrollbar range.

## ERR-49-164 - Slicebox stayed at zero height because hidden slides were lazy-loaded
**Date:** 2026-09-18
**Observed:** the Home template contained four valid Hero rows and all media URLs returned HTTP 200, but the rendered Slicebox stayed height 0, `pluginReady=False`, no `sb-current` item existed and navigation stayed hidden.
**Root cause:** vendored Slicebox v1.1.0 calls its bundled `imagesLoaded` gate and waits for every slide image before `onReady`. The template used eager loading only for slide 1 and `loading="lazy"` for slides 2-4. Those slides are hidden before Slicebox readiness, so Chromium deferred their lazy image requests and the plugin waited indefinitely.
**Fix:** mark all four Hero images `loading="eager"` while keeping `fetchpriority="high"` only on the first image. No model/query/Hero-row mutation is needed.
**Verification:** after restarting the Local Django process, all four images became complete with non-zero natural dimensions, `pluginReady=True`, slider height 416px, arrows/dots visible; browser Next generated 5 cuboids / 30 sides and advanced slide 0 -> 1 with no console/page errors.
**Prevention:** components that synchronously wait for all images must not combine their pre-ready hidden state with browser lazy loading. Browser acceptance must assert vendor-ready state and non-zero rendered geometry, not only DOM presence.

## ERR-49-163 - Large image preview swallowed wheel scrolling and Stage-3 minimum height pushed controls off-screen
**Date:** 2026-09-18
**Observed:** owner could see the large Product images but could not reach filename / multi-select / SEO / delete controls below them. Dragging/scrolling while the pointer was on the image appeared to do nothing.
**Root cause:** `ClickableImageLabel` handled the wheel event without forwarding it to the owning `QScrollArea`. Separately, `image_grid.setMinimumHeight(720)` made the Product Wizard exceed the real 1920x1080 desktop working height, so the lower gallery/action area could fall outside the visible application window even though the internal scrollbar itself had a non-zero range.
**Fix:** keep card/preview size and image workflow unchanged; reduce only the gallery container minimum to 560px so the window remains screen-bounded, and forward preview wheel deltas into the gallery vertical scrollbar.
**Verification:** real Product #628 copy: host 2424px, viewport 544px, scrollbar 0..1880; wheel on preview now moves 0 -> 270. Qt/Gallery/Wizard/Screenshot regression 67/67 PASS plus compile/diff-check/Qt VerifyOnly PASS.
**Prevention:** when enlarging child cards, verify the top-level rendered window against the actual desktop working area and test wheel input on the child surface itself, not only direct scrollbar range or empty viewport scrolling.

## ERR-49-162 - Operator SEO renumber reused publish dedup and could shrink the selected image set
**Date:** 2026-09-18
**Observed:** isolated Product #628 acceptance initially entered `بازسازی نام‌های SEO` with 11 selected images and returned only 6 because the generic finalizer removed one perceptual duplicate Product image plus several visually-similar screenshots.
**Root cause:** the operator rename/metadata action and the final publication dedup gate reused the same unconditional finalizer mode even though they have different authority. Operator SEO editing must not silently change the operator's selection.
**Fix:** keep `finalize_selected_images()` default behavior unchanged for publication, but add explicit optional `deduplicate=False` / selected-count limit only for Qt operator metadata/renumber calls. Normalize trusted legacy local identities before that operator pass.
**Verification:** isolated copy acceptance now keeps 11 -> 11, produces 11 unique SEO filenames, preserves Primary and SQLite integrity; expanded regression gate 107/107 PASS.
**Prevention:** never reuse a destructive/normalizing publication gate for a metadata-only operator action unless selection mutation is explicitly part of the command contract.

## ERR-49-161 - Stage-3 site membership was being used as the bulk-operation selector
**Date:** 2026-09-18
**Observed:** most Product images were already checked for Site publication, so bulk Edit/Delete behaved like all-or-nothing. Real numbered legacy files could also be shown as `display_only`, preventing subset operations.
**Root cause:** one checkbox carried two separate meanings: persistent Product Site membership and temporary operator targeting. The legacy display resolver also treated unmapped-but-real numbered Product files as non-mutating compatibility cards.
**Fix:** add independent temporary operation selection; preserve `در سایت` as the persistent selection contract; make only physically-present numbered files in the trusted Product images directory addressable by safe local identity and recoverable removal.
**Verification:** dedicated regressions prove arbitrary subset selection, delete/SEO only on the chosen subset, Site membership remains unchanged, and trusted legacy removal is recoverable. Real #628 copy exposes all 15 real files as editable.
**Prevention:** UI action targeting, persisted publication membership and source identity are separate contracts and must not share a single state bit.

### ERR-49-160B - Historical Phase49.3C filename assertion lagged current SEO-title-first authority
**Date:** 2026-09-18
**Observed:** the expanded 107-test gate had one failure expecting `fanart-solidarity-bear-3d-print-...` even when the row contained a newer authoritative `seo_title_fa`.
**Root cause:** runtime filename authority changed on 2026-09-15 (`9b006bbb...`) to Product SEO first while that older test still hard-coded the pre-change source-title filename.
**Fix:** keep runtime naming policy unchanged and update the stale regression to compare the actual deterministic planner output. The direct source-title fallback test remains intact.
**Verification:** the formerly failing test passes alone and the expanded 107/107 gate is green.
**Prevention:** filename-policy tests should assert the current planner authority rather than duplicate an obsolete priority order.

## ERR-49-160 — Qt Screenshot captured successfully but disappeared from Product gallery
**Date:** 2026-09-18
**Observed:** pressing «دریافت اسکرین‌شات صفحه محصول» created real `source-page-screenshot-*` files and updated `images_json`, but after refresh the new Screenshot was not visible in the Qt Product image grid, making the button appear non-functional.
**Root cause:** the A2L numbered-file resolver introduced at `4375c007...` returned numbered Product files before explicit non-numbered Screenshot mappings were considered. Its numbered fallback could also bind a `local://source-page-screenshot...` pseudo-URL to a numbered Product file slot.
**Fix:** keep the existing capture/naming pipeline untouched; append only explicitly persisted `local://source-page-screenshot...` files to numbered gallery results and never use those pseudo-URLs as numbered source-slot identities.
**Verification:** dedicated regression failed before the patch and passes after; maintained Qt/Gallery/Wizard/Screenshot suite 61/61 PASS; copy-of-real Product #628 resolves its persisted Screenshot items from an integrity-checked Catalog backup.
**Prevention:** display resolvers may filter arbitrary auxiliary files, but an image explicitly persisted in Product `images_json` by an operator action must remain observable in the same Product workspace. Derived/manual pseudo-URLs must never be reused as source-gallery slot identity.

## ERR-49-159 — Stage-3 size fix unintentionally changed mature image controls
**Date:** 2026-09-18
**Observed:** the attempted image-workspace repair also changed button labels/layout, recover-limit behavior, AI-bar visibility and restored-window geometry; owner also observed raw numbered filenames and loss of the expected screenshot workflow.
**Root cause:** a visual-space request was implemented across unrelated Stage-3/window behavior instead of keeping the delta presentation-only.
**Fix:** restore the mature control/screenshot/window behavior and the mature filename display exactly; keep image naming, screenshot naming/capture and SEO persistence untouched; enlarge only image cards/previews. The rejected `planned_filename` display override was removed.
**Prevention:** for owner UI sizing requests, define `Must-Not-Touch` as all existing button wiring, action order, filename display/generation, persistence, screenshot/recovery logic and global window behavior unless separately requested.

## ERR-49-158 — Real Catalog full Filament sync exposed 63 legacy blank-Brand identities
**Date:** 2026-09-18
**Observed:** exact A2L runtime no longer aborts the whole batch, but a read-only simulation of the real 71-row Catalog could legitimately sync only 8 rows; 63 historical rows have Material+Color but blank Brand and therefore fail the Site identity contract.
**Root cause:** old inventory rows predate the Brand-as-identity contract. This is data debt, not a Bridge/network defect and not a reason to invent a manufacturer.
**Fix:** keep fail-soft per-row sync, add selected/filterable bulk `تکمیل Brand انتخابی` using only Brand values already registered in the Catalog, then immediately reuse the normal Site sync path. Unknown Brand input is rejected. Copy-of-real-Catalog acceptance repaired row #14 to registered Bambulab and produced a valid ABS/Bambulab/color Site payload while deactivating the superseded blank identity.
**Prevention:** never auto-fill a missing Brand from material alone. Bulk identity repair must be an explicit operator choice from the registered Brand library; only evidence-backed exact duplicates may be suggested in future tooling.

## ERR-49-157 — Historical broad Catalog discovery is not a valid A2L release gate
**Date:** 2026-09-18
**Observed:** `unittest discover -s tests -p test_*.py` produced several legacy failures/errors and then remained blocked for more than three minutes without new output.
**Response:** the unchanged broad command was terminated and not repeated. A2L release evidence uses the exact scoped contracts: Catalog 55/55 PASS, Store/checkout 11/11 PASS, manual-payment 4/4 PASS, Qt launcher PASS, compile and diff-check PASS.
**Prevention:** release gates must target maintained modules/contracts; legacy/interactive historical discovery debt must be repaired independently rather than weakening current runtime assertions.

## ERR-49-156 — Store checkout fixtures drifted behind current migration/runtime contracts
**Date:** 2026-09-18
**Observed:** fresh test DB seeded ShippingMethod `post` in migration 0037 while `store.tests` attempted a duplicate `.create()`, then one test called the obsolete one-argument `calculate_fee()` signature.
**Fix:** make the fixture idempotent with `update_or_create` and call `calculate_fee(subtotal, total_weight_grams)`. Changed-condition rerun: 11/11 PASS.
**Related:** Pasargad seed dry-run initially hit Windows `cp1252` on a Persian console line; command output was changed to ASCII-safe status + card suffix only and dry-run then PASS.

## ERR-49-154 — 3DPrintHub dedicated reverse tunnel did not recover after Windows sshd restart (2026-09-17)
**Symptom:** `127.0.0.1:22024` is not listening, so the authenticated repository bridge cannot reach the 3DPrintHub Host.
**Evidence:** Windows `sshd` is Running/Automatic and listens on port 22; OpenSSH shows other project tunnel authentications after the restart, but the last successful `PrintHubTunnel` authentication from `89.39.208.237` is 2026-09-15 with expected fingerprint `SHA256:vzNCviwq432S+qQXPsCIjvVuHN8xYYqOiHSqZEPVfnY`. No new PrintHubTunnel attempt appears after the 2026-09-17 restart.
**Root-cause boundary:** Windows listener/user/key contract is not the current failure signal; recovery is blocked on the Host-side 3DPrintHub watchdog/tunnel path. Do not restart shared sshd or modify other project tunnel users.
**Rule:** Production deploy remains fail-closed until dedicated 22024 authenticated health is restored and Host identity/status is re-verified.

## ERR-49-155 — Isolated A2K release worktree test environment mismatch (2026-09-17)
**Symptoms:** Catalog unittest initially raised `No module named app`; isolated release Django initially raised missing `DJANGO_SECRET_KEY`; a manual test-conflict resolution briefly created a concatenated assertion SyntaxError.
**Resolution:** run Catalog tests with canonical `catalog_center` on `PYTHONPATH`; temporarily copy the canonical ignored `.env` only for local release tests and remove it immediately; fix/compile the reconciled test before rerunning. Release result: Django changed suites `50/50 PASS`, Catalog `18/18 PASS`, worktree clean.
**Prevention:** never interpret environment-loader failures as runtime regressions; never commit secrets; py_compile conflict-resolved Python before full gates.
## 2026-09-17 - ERR-49-153 nested PowerShell wrapper quoting corrupted read-only probes
A few early Desktop Commander probes nested `cmd / powershell` quoting and caused PowerShell to reinterpret pipeline/property syntax. Those probes failed locally before any Host mutation and did not change Repository, Catalog DB or Production.

Correction/prevention: do not nest an additional PowerShell command inside Desktop Commander's PowerShell shell. Use direct cmdlets, repository-owned operator scripts, or a literal here-string for Python. A failed quoting form must not be repeated unchanged.

## 2026-09-17 - ERR-49-152 Store-reset backup helper order created an existing-root collision
The first fresh reset-backup attempt ran `phase49_3i53_mysql_backup.py` before `phase50_store_reset_prepare.py`. The MySQL helper correctly created the target directory and a valid gzip dump, then the prepare helper failed with `FileExistsError` because it intentionally owns creation of the Store-reset root with `exist_ok=False`. No reset or DB deletion had occurred.

Correction: preserve the first DB-only backup, choose a new absent `*-store-product-reset` target, run `phase50_store_reset_prepare.py` first so media+manifest are captured, then run `phase49_3i53_mysql_backup.py` into that existing prepared root. Final root `/home/sfkilvrs/3dprinthub-deploy-backups/20260917-090106-final-store-product-reset` passed manifest/media and MySQL gzip verification before reset.

Prevention: for future Store reset operations the enforced order is `VERIFY EMPTY TARGET -> STORE RESET PREPARE -> MYSQL BACKUP INTO SAME ROOT -> EXACT LIVE PREFLIGHT -> RESET`. Do not repeat MySQL-first against the same prepare target.

## ERR-49-151 - Windows broad-gate command referenced retired test modules
Date: 2026-09-17
Status: `RESOLVED AS HARNESS SELECTION / RUNTIME TESTS PASSING`.

A broad Local Windows regression command executed 94 unittest entries and produced 92 PASS plus two loader errors because it still named `tests.test_phase50_social_publish_providers` and `tests.test_phase50_image_workspace_responsive`, which are not present in the current test package. The failures occurred at unittest module import and did not execute Product/Qt/Site runtime code. The same run already PASSed the live republish contracts for existing-product update-in-place, explicit requeue of an uploaded Product, Site-404 recreation, current SEO WebP packaging and changed Profile/Filament/print-time propagation.

Correction/prevention: do not rerun the stale command unchanged. Use only test modules verified in the current repository and keep harness/module-selection failures separate from runtime regressions. Missing test-module names must be removed from the gate rather than interpreted as a Product failure.

## ERR-49-150 - Product #628 acceptance diagnostic harness corrections
Date: 2026-09-15
Status: `RESOLVED / ACCEPTANCE PASS / NO TEST ORDER WRITE`.

During final #628 acceptance, one Host read-only diagnostic tried `ProductVariant.price`, which is not a model field, after already proving Product=1 and 190/190 Variants orderable. The failed probe performed no write and was not repeated unchanged; the corrected final probe used only verified model/orderability contracts and confirmed Product=1, Variant=190, Image=2, StoreOrder=0. The first browser harness also targeted numeric `data-step` values, while the live guided selector uses `data-dimension`; it therefore left Cart disabled without proving a runtime defect. The corrected browser condition drove the visible `data-dimension` controls, enabled Cart and resolved Variant 1837.

Prevention: acceptance harnesses must follow the live user-visible selector contract and must introspect/use verified model fields instead of guessing diagnostic attributes. A harness failure is not a Product/runtime failure until reproduced through the real contract.

## ERR-49-149 - Product Wizard had publish intent but no direct send action
Date: 2026-09-15
Status: `RESOLVED LOCAL / PRODUCTION PRODUCT ACCEPTANCE NEXT`.

Observed: the owner could mark a Product for sale/site publication inside the Product Wizard, but Stage 7 had no action to publish that Product. The only Qt send action lived back on the Products multi-select page. This made the Product-detail workflow appear broken even though the mature Batch/FTP/Bridge publisher existed.

Reality audit: canonical Catalog integrity is OK; 15 rows are currently `upload_ready=1`; 12 pass the actual publish gate. Live Site receiver readiness is true with no blockers and FTP connection passes. Therefore the current blocker is not Host readiness. Three Ready rows (#40/#43/#146) are correctly blocked by missing image SEO/slider evidence and must not be force-published.

Fix: Stage 7 now exposes explicit single-Product ready/publish actions. It persists only explicit operator intent, calls the same mature PublishCore used by bulk publishing, shows exact gate failures, prevents concurrent duplicate clicks, and reports success only when strict Bridge/public HTTP verification returns one published Product. A finalized Stage 7 can publish unchanged values without an unnecessary locked-stage write.

Verification: first new test run reached the runtime successfully but the new fixture omitted `QMessageBox` import; the condition was corrected before rerun. Final focused 21/21 and broader 71/71 regressions PASS; compile/diff-check PASS. Rollback `backup/pre-product-single-publish-ui-20260915` -> `5f3a24b...`.

Prevention: every operator-owned final workflow stage must expose the actual next action in the same workspace or clearly route to it; UI intent flags alone are not an acceptable publish workflow. Keep single and bulk publication on one shared guarded Core.

## ERR-49-148 - Phase50.A.3 gate harness and baseline Store regression classification
Date: 2026-09-15
Status: `A3 RESOLVED / BASELINE STORE DEBT OPEN / NO PRODUCTION WRITE`.

During the ZarinPal compatibility gate, several operator-harness issues were caught before commit/deploy: PowerShell colon interpolation produced one invalid rollback push refspec; generic `bash` resolved to the WSL stub without a distro; one Git probe wrapper mangled a PowerShell variable; an inline Python runner edit failed on quoting before write; and an inline PowerShell documentation write interpreted Markdown backticks as escape sequences. The first git commit wrapper also parsed the parenthesized commit message as PowerShell syntax; no commit was created, and the retry uses a shell-safe message. Each failed condition was changed before retry. The verified rollback branch is live at exact `1a29e225...`; Git-Bash syntax now uses `C:\Program Files\Git\bin\bash.exe`; runner edits/docs were completed with direct UTF-8 local helpers and readback.

The full Django suite ran 534 tests and reported 6 failures + 9 errors. The affected Store modules were isolated to 41 tests. Current patch: 6F/9E. Exact rollback baseline `1a29e225...`, in a detached worktree with the same local `.env`: the same 6F/9E. Therefore these failures predate and are independent of the ZarinPal delta. Payment-specific suites remain 17/17 PASS, Django check/no-drift and `phase30_payment_audit` PASS.

Prevention: do not classify a broad-suite failure as a new feature regression without exact-baseline reproduction when touched surfaces are disjoint. On Windows, use explicit Git Bash, avoid variable/colon ambiguity, do not inline Markdown backticks through PowerShell, and require UTF-8 file readback after documentation edits.

## ERR-49-147 ? Continuation QA wrapper encoding/interpolation failures
Date: 2026-09-15
Status: `RESOLVED / NO PRODUCTION WRITE`.

Two verification-harness failures occurred after the handoff runtime was already live. First, the initial Playwright Production probe reached Home HTTP 200 and then Windows CP1252 stdout failed while printing the Persian page title (`UnicodeEncodeError`). The rerun changed the condition by setting `PYTHONIOENCODING=utf-8` and completed the entire desktop/mobile/Store browser gate successfully. Second, a double-quoted PowerShell wrapper eagerly expanded remote `$R` before sending the backup-verification command, so remote Python received an empty reset-backup path and raised `FileNotFoundError`. The retry used a single-quoted here-string/literal Host path and verified the intended backup.

Prevention: browser/CLI probes that can emit Persian must force UTF-8 output; nested Windows?Host commands must not rely on `$variable` names inside double-quoted PowerShell transport strings; use single-quoted here-strings or explicit literal/argument passing. A failed verification command is never rerun unchanged. Neither incident mutated Source, DB, media, static files or Production runtime.

## 2026-09-15 - ERR-49-146 RECOVERED / watchdog contract reverified
Owner ran the repository bootstrap once from cPanel. `127.0.0.1:22024` returned to LISTENING and authenticated bridge health is `ok=True`, version `1.0.0`, base `/home/sfkilvrs/3dprinthub`. A tunnel-side `crontab -l` probe then proved the required one-minute `3DPrintHub reverse tunnel watchdog` entry is installed exactly with `flock` and `phase50_reverse_tunnel_bootstrap.sh`. Normal operations therefore return to Remote-Desktop Local work + reverse-tunnel Host deployment; owner cPanel entry is break-glass only.

## 2026-09-15 - ERR-49-146 3DPrintHub reverse watchdog stopped; no authorized Host execution channel
**Observed:** Windows `127.0.0.1:22024` is closed. Host private `watchdog.log` and `tunnel.pid` stopped updating on 2026-09-14; `tunnel.log` ends with `Connection reset by peer` / `Broken pipe`. Windows authorized-key fingerprint exactly matches the Host tunnel-key fingerprint, and Windows OpenSSH is healthy for the same Host source IP through another isolated project identity, so the 3DPrintHub failure is not a key mismatch or global Windows SSH outage.

**Root cause boundary:** the accepted one-minute cPanel cron/watchdog is no longer executing. FTPS exposes files only and advertises no command execution. The stored FTP credential is not a cPanel API credential (HTTPS 2083 read-only probe returns 401). Repository has no `.cpanel.yml`, GitHub deploy workflow, or alternate direct inbound Host SSH path.

**Safety response:** do not upload permanent source over FTPS, do not borrow Asal/Retoucher tunnels, do not bypass cPanel authentication, and do not mutate Production DB/Store until GitHub-first Host execution is restored.

**Recovery:** restore only the documented 3DPrintHub cPanel cron or run the repository bootstrap from the cPanel Terminal; then require `22024` listener + authenticated bridge identity before running `phase50_client_handoff_deploy.sh`.

## 2026-09-14 - ERR-49-145 Qt6 CI retained obsolete three-large-column gallery assertion
**Observed:** GitHub run `34864938351` for ERR-49-144 failed one test: `test_image_stage_uses_three_large_column_cards_with_size_and_seo_facts`, asserting `grid.columns == 3` while the accepted runtime intentionally uses four compact columns. All neighboring tests in that job passed; three other workflows on the same commit also passed.

**Root cause:** the visual contract test from the earlier large-card layout was not included in the first focused 77-test regression set. The implementation and owner requirement had moved to a compact four-column gallery, but this older parity assertion still encoded the superseded design.

**Correction:** rename/update only that parity contract to require four compact columns while preserving its image width/height/bytes/Alt and Slider assertions. No runtime, database, migration, publish or media behavior changed by this correction.

**Verification:** exact failed GitHub suite (`tests.test_phase49_3i42_qt6_foundation` + `tests.test_phase49_3i42b_core_parity`) now passes 23/23 locally. Do not rerun the failed GitHub command unchanged; push the changed test condition and require a fresh green workflow.

**Prevention:** when an owner-requested visual contract intentionally changes density/layout, search all parity tests for the old design wording and assertions in addition to running the focused feature suite.

## 2026-09-14 - ERR-49-144 Published lifecycle and Product gallery conflated dirty/source state with customer-visible state
**Observed:** already-published Products disappeared from the Qt `Sent / Published` workspace after any Local edit set `needs_update=1`. Older Products could also show roughly 60 broken/empty image cards because the gallery iterated raw source URLs even when only 16 or 25 local files actually existed; the three-column cards were unnecessarily large.

**Root cause:** the Published filter and lifecycle badge treated `needs_update=0` as part of publication identity instead of as a separate republish state. Separately, Qt display count/card construction conflated source URL evidence with locally renderable media. The strict publish resolver intentionally refuses index guessing, but that strict mutation/publish rule was incorrectly reused as the only UI display path for legacy files.

**Correct fix:** an uploaded Product with a server identity remains in Published regardless of `needs_update`; the existing Work Queue simultaneously carries dirty/ready republish work. ImageCore now has a UI-only factual local-file resolver and separate source-image count. Exact current mappings remain preferred; legacy local numbered files can be shown read-only; unmapped display-only cards have selection/primary/slider/SEO/delete controls disabled. The strict SEO/publish mapping in `phase49_3c_image_pipeline` is unchanged. Gallery density returns to four compact columns.

**Verification:** canonical Catalog read-only probe: Published=19; Product #33 source=60/display=16, #34=60/25, #63/#628/#634=2/2 with their finalized SEO WebPs preserved. Dedicated 3I.47 regression is 9/9 PASS; combined 3I.47 + 3I.42C3 + 3I.49 + 3I.52C suite is 77/77 PASS. One first broader run failed only because the old republish test asserted Published count=0 after a dirty edit; after review, the test contract was changed to require the same Product in both Published and Work Queue. No failed runtime command was repeated unchanged.

**Rollback:** `backup/pre-err49-144-published-gallery-regression-20260914` -> `b85f946094ffeb0aea406ebaf6603273a7ef49ed`.

**Prevention:** lifecycle identity, republish dirtiness, source media evidence, local-display media and strict publish media are distinct contracts. Tests must cover all five explicitly; never make a UI visibility/count rule stronger by reusing a fail-closed publication rule.

## 2026-09-14 - ERR-49-143 focused unittest invoked from wrong module root
**Observed:** the first focused ERR-49-142 regression command ran from repository root and failed before executing tests with `ModuleNotFoundError: No module named app`.

**Root cause / correction:** Catalog Center tests import the mature `app.*` package relative to the `catalog_center` runtime root. The failed condition was not repeated unchanged; the suite was rerun from `D:\\projects\\3DPrintHub\\catalog_center` with the verified project venv and passed 11/11.

**Prevention:** run Catalog Center unittest modules from the Catalog Center runtime root (or set the equivalent verified import path); do not classify import-root harness failures as runtime defects.

## 2026-09-14 - ERR-49-142 publish-gate canonical-profile blocker text was corrupted
**Observed:** the fail-closed canonical Sales Profile check worked, but its operator-facing missing-data message in `phase49_3i49_site_publish.py` had been persisted as question marks.

**Root cause / correction:** prior Windows text-boundary corruption affected only the diagnostic literal. The blocker was restored to a Persian UTF-8 message and the regression now asserts the exact message and rejects `????` corruption.

**Verification:** focused Catalog bulk-publish suite 11/11 PASS, touched compile PASS, `git diff --check` PASS. Rollback branch `backup/pre-err49-142-publish-gate-message-20260914` points to `1ccc0ae...`. No Catalog/Production data or Host runtime was changed by this source hotfix.

## 2026-09-14 - ERR-49-139 Product #62 repair harness safety catches
**Observed:** the first preview used system Python and stopped on missing Pillow before any backup/write. A later preview proved all numeric/Offer facts but Persian inline literals crossed PowerShell as `????`; this affected only the disposable preview copy. A byte-SHA guard later found the canonical SQLite file bytes differed from the backup even though no intended write had occurred.

**Root cause / correction:** use the verified project venv (`D:\projects\3DPrintHub\.venv\Scripts\python.exe`), pass Persian test literals as ASCII-safe Unicode escapes, and never infer SQLite logical mutation from file SHA alone. The byte mismatch was investigated read-only: integrity OK, schema equal, 22/22 table logical hashes equal, Products #62/#84/#628/#634 equal, relevant Offers equal, page/freelist counts equal. Only after that proof was a fresh backup taken and the canonical CommerceCore write allowed.

**Prevention:** Product repair previews must run against a copy first, use the project runtime, use encoding-safe payloads, and require logical SQLite forensics when a checksum changes unexpectedly. Never disable the checksum guard merely to continue.

## 2026-09-14 - ERR-49-140 stale-public deploy transport blocked before Host Git mutation
**Observed:** Local/live GitHub reached `07772ca...` and CI passed, but the current remote-command safety layer rejected Host Git mutation commands. Read-only Host probes and backup creation still work. Production therefore intentionally remains clean `70a74e6...`.

**Correction / prevention:** do not bypass the execution safety boundary and do not edit Production source directly. Keep the verified rollback bundle `/home/sfkilvrs/3dprinthub-deploy-backups/20260914-151721-phase50-stale-public-orderability`, and promote the approved GitHub commit only through an authorized project-standard Host execution path.

## 2026-09-14 - ERR-49-141 repeated Host `/dev/fd` incompatibility in a premerge probe
**Observed:** a read-only premerge allowlist probe used Bash process substitution and stopped with `/dev/fd/63: No such file or directory`. The printed delta was correct and no merge/DB write occurred.

**Root cause / prevention:** this is the already-known ERR-50-010 Host constraint. Do not use `< <(...)` on this cPanel Host; use normal temporary files or Python. The failed command must not be rerun unchanged.

### ERR-49-137 ? PowerShell wrapper reported failure after remote runner had already PASSed
**Date:** 2026-09-14
The orderable-contract runner completed with remote `ok=True`, `returncode=0`, exact final HEAD `70a74e6...`, clean worktree and `PHASE50_ORDERABLE_PUBLISH_CONTRACT_DEPLOY=PASS`, but the outer Windows command checked stale/unreliable `$LASTEXITCODE` after invoking a PowerShell script and threw `remote orderability deploy failed`. Production was verified read-only afterward and was healthy. Do not rerun the deploy. Prevention: inspect the structured Bridge result (`ok` + `returncode`) for `.ps1` operator calls instead of `$LASTEXITCODE`.

### ERR-49-138 ? Previously active non-orderable Product could remain public after visibility failure
**Date:** 2026-09-14
**Observed:** Production #18/#19 were already active from the older weak visibility contract but each had zero truly orderable Variants. The new visibility function raised inside `transaction.atomic()`, which is correct for a new invalid publish but would roll back any attempted deactivation of a stale public Product.

**Root cause:** visibility rejection and stale-public cleanup shared the same exception path.

**Fix:** if the Product was already public/indexed, clear `is_active`, `robots_index`, and `robots_follow`, save that state, return the non-visible decision and let the importer commit it as `publish_incomplete`. New invalid Products still raise before publication. Importer only increments Product count for `visibility.visible=True`.

**Verification:** compile PASS; 19 visibility/unified-import/Variant tests PASS; no migration drift; diff-check and dedicated runner Bash syntax PASS. Rollback `backup/pre-err49-138-stale-public-orderability-20260914` -> `70a74e6...`.

### ERR-49-135 ? Store visibility ACK could pass while every customer Variant was non-orderable
**Date:** 2026-09-14
**Observed:** #62/#84 imported successfully, public Product/media returned HTTP 200 and ACK reported `visible_on_store=true`; real browser QA found Cart disabled. Variant API returned `orderable=false` for every Variant.

**Root cause:** older Catalog rows had empty `sales_profiles_json` / `sales_profile_ledger_json`, but Desktop publish gate did not require canonical Profile data. Host therefore created legacy fallback Variants. Final Store visibility required active Variant + price but did not reuse the real customer orderability rule (stock status + tracked inventory/backorder + filament color stock).

**Correct fix:** require at least one canonical sales Profile before Desktop FTP; centralize customer orderability in `store.phase50_orderability.variant_is_orderable`; use the same helper in Variant API and final Catalog visibility; require `orderable_variant=true` before Store-visible ACK. Repair already-published #62/#84 through mature Commerce Profile bootstrap and republish the same source/Site identities; do not hand-edit Production Variants.

**Safety:** no migration, no price invention, no inventory invention, no direct Production source edit. #43 stays blocked because Material/Color are factual operator inputs. Rollback branch: `backup/pre-err49-135-orderable-publish-contract-20260914` -> `e9e2257...`.

**Verification:** local Python compile PASS; Store 35 tests PASS; Catalog Profile/Publish 19 tests PASS; Django check PASS with known warnings; no migration drift; migration plan empty; diff-check; dedicated runner Bash syntax/contract PASS. Production deploy and #62/#84 repair remain next.

**Prevention:** strict Product publication acceptance must mean at least one Variant can actually be ordered by the same rule the customer API uses. Public HTTP 200 + active/priced Variant alone is insufficient.

### ERR-49-136 ? exact-text fixture patch anchors failed before write
**Date:** 2026-09-14
Several local test-fixture edit attempts used Unicode/line-ending-sensitive exact anchors and stopped with anchor-not-found errors before writing the file. The failed commands were not repeated unchanged. The fixture was patched using deterministic line/ASCII field anchors instead, then `git diff --check` and tests passed. Prevention: for mixed Persian/CRLF files, prefer line-structured or ASCII-key anchors over large exact Unicode blocks.

### ERR-49-134 - Live browser DOM diagnostic embedded invalid inline JavaScript
**Date:** 2026-09-14
**Observed:** after correcting the hidden-select issue, a diagnostic-only `evaluate_all` expression failed with JavaScript `SyntaxError` before reading the Product DOM.
**Root cause:** nested quote/escape complexity in the inline diagnostic expression; Production page was not the failing boundary.
**Correct fix:** do not rerun the expression unchanged; read DOM nodes with Playwright's Python locator API instead. The corrected DOM inspection returned HTTP 200, real guided steps and canonical Cart form.
**Prevention:** prefer locator APIs for acceptance diagnostics; reserve inline `evaluate` for small syntax-stable expressions.

### ERR-49-133 - Live browser acceptance tried normal select on intentionally hidden native fallback
**Date:** 2026-09-14
**Observed:** first live Product browser QA timed out at `select_option` because `#variant-select` is intentionally hidden after guided progressive enhancement.
**Root cause:** harness treated the native fallback as the primary visible control even though the Phase50 guided selector correctly hides it when JS is ready.
**Correct fix:** do not repeat unchanged. Inspect the live guided DOM and drive visible `[data-step]` buttons; keep the native select only as fallback contract. Final QA for #628/#634 PASSed through visible customer controls and intercepted Cart POST.
**Prevention:** Production browser acceptance must follow the user-visible enhanced path first; hidden native controls are fallback evidence, not the default interaction target.

### ERR-49-132 - Local Bash syntax gate selected WSL stub instead of Git Bash
**Date:** 2026-09-14
**Observed:** deploy-runner syntax validation stopped before parsing the runner because `Get-Command bash` resolved to the Windows WSL launcher and no Linux distribution is installed.
**Root cause:** the validation harness treated a generic `bash` command name as an implementation guarantee on this Windows machine.
**Correct fix:** do not rerun the unchanged command; select the verified Git for Windows executable explicitly (`C:\Program Files\Git\bin\bash.exe`) and run `-n` there.
**Verification:** Git Bash parsed `phase50_owner_license_hotfix_deploy.sh` successfully; no-migrate/no-collectstatic and required deployment markers also PASS.
**Prevention:** Windows repository Bash syntax gates must use the verified Git Bash path unless a real WSL distribution is explicitly verified first.

### ERR-49-131 - Host ignored explicit owner source/license approval during bounded Product publish
**Date:** 2026-09-14
**Observed:** the first bounded retry candidates Product #628 and #634 passed all Windows stages/media and reached FTP/Bridge, but Host ACK returned `review_required`; `published=0`, so neither was falsely transitioned to uploaded.
**Initial diagnosis corrected:** blocking every raw `commercial_status=review` on Windows would contradict the repository's explicit 2026-09-01 owner policy. `source_license_owner_approved=1` is the separate business approval authority; source license status/text must remain evidence and must not be fabricated.
**Root cause:** Windows readiness and `Database.exportable()` already accepted owner approval, but Host `phase37_import_catalog_center`, `ImportedPrintAsset.can_convert_to_fixed_product`, and `phase49_catalog_visibility` checked only the raw commercial status. The same Batch therefore passed Desktop but failed Host.
**Correct fix:** define one Host effective-license rule: explicit owner approval OR raw status in `allowed/owned/public_domain`; preserve `commercial_status` unchanged. Persisted Batch owner approval is read from `source_payload.desktop_catalog_v85` for the mature conversion property. `review` without owner approval remains blocked.
**Regression path:** the first positive E2E exposed the old conversion-property gate via ValidationError, so that underlying condition was fixed before rerun. The next run reached successful conversion and exposed only a stale test expectation (`editorial_status` becomes mature lifecycle `product`, not interim `printable`); test was aligned without weakening runtime.
**Verification:** focused 9 Django PASS; broader 16 Site PASS; 18 Catalog owner-policy/bulk-publish PASS; compile/check/no migration drift/empty plan/diff-check PASS.
**Prevention:** every business approval override accepted by Windows export must be represented explicitly in the Batch and enforced identically by Host import, conversion and Store visibility; never translate that approval into fabricated source-license evidence.

### ERR-49-130 - Production documentation update repeated the reserved PowerShell `$Host` variable failure
**Date:** 2026-09-14
**Observed:** after successful Production deploy/acceptance, a multi-document PowerShell update again attempted to assign a here-string to `$Host` and stopped after writing the documents that appeared earlier in the command. This is the same underlying condition already documented by ERR-49-119.
**Root cause:** the new documentation command violated the existing prevention rule and reused the read-only automatic variable name `$Host`.
**Correct fix:** do not reset valid partial writes. Inspect `git status`/diff and file readback, then continue only the missing document with a non-reserved variable name (`$hostEntry`).
**Verification:** CURRENT_STATE/ROADMAP/master/CHANGELOG/REQUESTS/PROJECT_CONTEXT/PATHS partial writes were confirmed intact; HOST_CONSTRAINTS was then updated separately. No source/runtime/Production mutation was caused by this documentation harness error.
**Prevention:** PowerShell documentation payload variables must never use automatic/reserved names; reuse the ERR-49-119 safe naming rule explicitly in future multi-file edits.

### ERR-49-129 - Production browser QA output hit Windows cp1252 on Persian text
**Date:** 2026-09-14
**Observed:** Product page loaded HTTP 200 and Hero QA had already passed, but the first Product browser harness stopped while printing the Persian H1 with `UnicodeEncodeError` from the Windows cp1252 console boundary.
**Root cause:** the diagnostic script printed Persian text directly to a legacy console encoding; the web page/runtime itself was healthy.
**Correct fix:** keep browser behavior unchanged and make diagnostic output ASCII-safe with `json.dumps(..., ensure_ascii=True)` before continuing Product controls/image/cart inspection.
**Verification:** corrected harness completed Product page inspection, selector/price/cart wiring and media diagnostics successfully.
**Prevention:** Remote Windows acceptance scripts should serialize non-ASCII UI text safely instead of relying on the process console code page.

### ERR-49-128 - Read-only Product #63 receipt probe guessed a nonexistent `event_type` column
**Date:** 2026-09-14
**Observed:** the first read-only acceptance query successfully returned Product #63 state, then failed on `sync_receipts.event_type` because the actual table uses `status`.
**Root cause:** the diagnostic query guessed the receipt schema instead of introspecting it first.
**Correct fix:** do not rerun the guessed query. Inspect `PRAGMA table_info(sync_receipts)` read-only, then query the verified columns `id, product_id, batch_uuid, status, server_id, payload_json, created_at`.
**Verification:** the corrected read-only query recovered the real successful ACK and the runtime strict predicate returned `True` with Product #63 still `uploaded` and sync error empty.
**Prevention:** SQLite diagnostic/acceptance probes must introspect actual schema before referencing columns, even when similar event-ledger tables use different names.
### ERR-49-127 - PowerShell rollback push refspec was corrupted by colon interpolation
**Date:** 2026-09-14
**Observed:** the first rollback-branch push failed locally with `fatal: invalid refspec 'refs/heads//heads/backup/pre-phase50-a2i-combined-deploy-20260914'`. The local rollback branch itself had already been created correctly at `b1bbdeec2db2f3876def2fd1c61d17db01e67fb7`; no source, Production or database mutation occurred.
**Root cause:** PowerShell parsed `$rb:refs` inside a double-quoted refspec as a colon-qualified variable expression instead of the intended `$rb` value followed by a literal colon.
**Correct fix:** inspect the partial result, verify the local rollback ref and SHA, then change the command condition to use explicit `${rb}` boundaries in `refs/heads/${rb}:refs/heads/${rb}`. The corrected push created the remote rollback branch at the exact expected SHA.
**Verification:** `git show-ref`, `git rev-parse` and live `git ls-remote` all report the rollback branch at `b1bbdeec2db2f3876def2fd1c61d17db01e67fb7`.
**Prevention:** when a PowerShell interpolated variable is immediately adjacent to `:`, delimit the variable with `${...}` or construct the refspec from separate literal components; never rerun the malformed refspec unchanged.
### ERR-49-126 - A2G deploy-runner contract scan initially matched a descriptive NO COLLECTSTATIC banner
**Date:** 2026-09-13
**Observed:** the first Local runner gate passed compile, focused Bridge tests, Django check and no-migration drift, then the safety scan stopped on `FORBIDDEN_COLLECTSTATIC_FOUND` even though the runner contained no collectstatic command.
**Root cause:** the test scanned for the bare word `collectstatic` and matched the banner text `NO ... COLLECTSTATIC`.
**Correct fix:** change only the test condition to search for an executable `manage.py collectstatic` command boundary; keep the runtime runner unchanged. Also verify `manage.py migrate` independently.
**Verification:** Bash syntax, `git diff --check`, `manage.py migrate` absence and `manage.py collectstatic` absence PASS.
**Prevention:** safety scanners must match executable command forms rather than descriptive denial text; do not weaken the runner to satisfy a naive grep.

### ERR-49-125 - Unified Bridge exposed private imported working-media URLs for a published Product
**Date:** 2026-09-13
**Observed:** controlled Product #63 was publicly healthy under `store/products/gallery/`, but Bridge Product image payloads still returned `/media/store/imported-models/gallery/...`, which correctly returned HTTP 404 on Production.
**Root cause:** `catalog_bridge.unified_views._image_rows()` and Hero `selected_image_url` serialized `ImportedPrintAssetImage.image.url` directly. That field is working-media identity, not a public Store media contract.
**Correct fix:** preserve ImportedPrintAssetImage IDs for Desktop sync identity, but resolve the public URL by matching the imported image basename to Product-owned `ProductImage`; fall back to Product main image and only then a safe HTTP(S) remote source. Never widen Production routing to expose imported working-media.
**Verification:** both real Product-owned Flexi Gecko gallery WebPs return HTTP 200/image-webp while the imported working-media URL remains correctly 404; Local Bridge/Hero/Admin focused suite 31/31 PASS; no migration drift.
**Prevention:** every Bridge surface that represents public Product/Hero media must obey the same Product-owned media boundary as the Storefront. Tests must assert both the expected public URL and absence of `/media/store/imported-models/`.
### ERR-49-124 - Browser JS was initially executed as Node runtime during A2H validation
**Date:** 2026-09-13
**Observed:** direct `node static/js/theme-preview.js` reached valid browser code and failed with `ReferenceError: document is not defined`.
**Root cause:** a browser DOM script was executed as a Node application instead of syntax-parsed.
**Correct fix / prevention:** do not repeat the runtime command. Use `node --check` for syntax and the real Playwright browser gate for DOM behavior. Both now PASS.

### ERR-49-123 - New Persian theme-toggle literal was corrupted at the PowerShell write boundary
**Date:** 2026-09-13
**Observed:** the first compact theme-toggle edit rendered `????` even though layout behavior worked.
**Root cause:** Persian literal text crossed the remote PowerShell text boundary used for the source edit.
**Correct fix / prevention:** restore mature Persian strings from Git HEAD and encode the newly inserted short label as HTML numeric entities; verify no question-mark corruption and then verify browser-visible Persian text. Final browser gate PASS.

### ERR-49-122 - Local Django SQLite lag blocked A2H Home visual QA
**Date:** 2026-09-13
**Observed:** Local `/` returned HTTP 500 with `no such column: website_material.catalog_description` while A2H Hero code itself parsed correctly.
**Root cause:** effective Local SQLite had not applied already-existing Website 0024 and Store 0041/0042 migrations.
**Correct fix / safety:** verify SQLite identity and exact migration plan; create checksum-identical backup `D:\projects\3dprinthub-backups\phase50-a2h-local-django-20260913-122930`; then apply only the existing pending Local chain. Post-plan is empty and Home returns 200. Production DB was never touched.
**Prevention:** real Local browser QA must verify Local migration plan first when source references schema newer than the developer SQLite; never interpret a stale Local schema as a Hero/template defect.

### ERR-49-121 - cPanel FTPS root is account-chrooted for private tunnel state
**Date:** 2026-09-13
**Environment:** WinSCP explicit FTPS to the Production cPanel account.

**Observed:** requesting `/home/sfkilvrs/.config/reverse-host-bridge/3dprinthub/...` failed even though bootstrap had created the private state. Listing `/.config/reverse-host-bridge/3dprinthub/` succeeded.

**Root cause:** the FTPS session root maps to `/home/sfkilvrs`; supplying the absolute filesystem home path duplicated the account-home prefix at the FTP boundary.

**Correct fix / prevention:** keep filesystem paths and FTPS-chroot paths distinct. For shell/bridge use `/home/sfkilvrs/...`; for this WinSCP account use `/.config/...`. Never infer one namespace from the other without verification.

### ERR-49-120 - Unelevated Windows `sshd -t` returned 255 despite healthy service/config
**Date:** 2026-09-13
**Environment:** owner Windows OpenSSH validation through a non-elevated Remote Desktop process.

**Observed:** manual `sshd -t` returned 255 with no parser diagnostic while the `sshd` service remained Running and listening. Host private-key ACL checks returned Access Denied. Windows OpenSSH Event Log then proved successful public-key authentication from Production Host `89.39.208.237`.

**Root cause:** the non-elevated process could not read protected `C:\ProgramData\ssh\ssh_host_*_key` private keys; the return code alone was not evidence of invalid `sshd_config`.

**Correct fix / prevention:** validate config elevated when required, or distinguish parser failure from host-key ACL by service/listener/Event Log evidence. Never tear down a working tunnel profile solely because unelevated `sshd -t` returns 255.

### ERR-49-119 - PowerShell reserved `$Host` variable stopped tunnel documentation update safely
**Date:** 2026-09-13
**Environment:** Windows repository documentation update through Remote Desktop Commander.

**Observed:** the first multi-document update wrote CURRENT_STATE/ROADMAP/PATHS, then stopped when the script attempted to assign a here-string to `$Host`, a read-only automatic PowerShell variable. Later files were not written by that command.

**Correct fix:** inspect and preserve the valid partial diff, continue with non-reserved variable names and absolute repository-rooted paths, and do not reset the earlier valid writes.

**Prevention:** never use PowerShell automatic/reserved names such as `$Host` for document payload variables; fail-fast and inspect partial writes before continuation.

### ERR-49-118 - First elevated Windows tunnel bootstrap stopped after backup before security mutation
**Date:** 2026-09-13
**Environment:** owner Windows OpenSSH onboarding for 3DPrintHub reverse management.

**Observed:** bootstrap v1 returned nonzero after creating only an `sshd_config` backup; tunnel user, Match block, authorized-key file and firewall rule were absent and sshd remained healthy.

**Root cause:** the initial user-creation path relied on `net user` empty-password semantics that were not valid in this environment.

**Correct fix:** change the condition before retry: use `New-LocalUser -NoPassword`, retain dedicated non-admin/no-group identity, validate `sshd -t`, then create the source-restricted firewall rule and restart sshd. Bootstrap v2 passed; `PrintHubTunnel` exists, only remote forwarding to `127.0.0.1:22024` is allowed, firewall is restricted to `89.39.208.237/32`, and sshd is running.

**Prevention:** use verified LocalAccounts cmdlets on this Windows host and prove no partial security mutation before retrying a failed elevated bootstrap.

### ERR-49-117 - Explicit Batch media refresh caused storage suffix churn on identical re-import
**Date:** 2026-09-12
**Environment:** Local Django importer regression for Phase50.A.2G Windows-to-Site media publishing.

**Observed:** After making explicit current-Batch image mappings authoritative, a real changed SEO WebP correctly refreshed Host media and advanced the Hero/Slider visual revision. Re-importing the exact same refreshed Batch advanced the revision again (`2 -> 3`) even though the incoming media bytes had not changed. The same investigation also showed that a manifest-level `desktop_product_id` was not available to first canonical Profile sync when it was absent from `desktop_editorial.json`.

**Root cause:** Django storage `FileField.save()` was called unconditionally for every explicit mapping. When a same-name file already existed, storage generated a suffixed filename, so downstream visual identity appeared changed even with identical bytes. Separately, the importer resolved manifest Desktop identity for reconciliation but did not propagate it into the data passed to Profile sync.

**Correct fix:** propagate manifest `desktop_product_id` into the editorial data before canonical sync. For explicit media mappings compare incoming and currently stored SHA256 first: save only when bytes differ; identical bytes reuse the existing FileField. A real media change remains authoritative and advances the visual revision once; an identical third import is idempotent. No historical media file is destructively deleted.

**Verification:** focused import E2E PASS for initial import -> changed SEO WebP re-publish -> identical third re-import; combined Django import/Filament/Profile 16/16 PASS; Catalog publish-media 10/10 PASS; no migration drift.

**Prevention:** current Batch authority means reconcile content, not unconditional FileField save. Media import regressions must prove both changed-content refresh and same-content idempotence, and Desktop identity must reach canonical sync on the first import.

### ERR-49-116 ? cPanel interactive shell exited when bootstrap enabled errexit globally
**Date:** 2026-09-12
**Environment:** cPanel web Terminal interactive login shell.

**Observed:** When the guarded A2F runner returned Exit Code 1, the cPanel Terminal UI immediately showed Reconnect, making the safe deployment stop look like a network/session disconnect.

**Root cause:** the pasted bootstrap executed `set -Eeuo pipefail` directly in the interactive login shell. Therefore a deliberate fail-closed nonzero status triggered `errexit` in the parent interactive shell and terminated that shell session.

**Correct fix:** run strict-mode bootstrap logic inside a subshell `( set -Eeuo pipefail; ... )`, capture/report its return code outside the subshell, and keep the parent cPanel Terminal flags unchanged. Repository deploy runners may keep strict mode because they execute as child `bash` processes.

**Prevention:** never enable `set -e`/`set -Eeuo pipefail` globally in an operator's interactive Production shell. All pasted guarded blocks must isolate strict mode in a subshell or execute a repository-owned child script.

### ERR-49-115 ? Phase50.A.2F deploy delta allowlist omitted root PROJECT_CONTEXT.md
**Date:** 2026-09-12
**Environment:** Production cPanel guarded no-migration deploy from recovered baseline `e12fdaf...`.

**Observed:** The runner correctly verified the live target and printed the reviewed target delta, then stopped with `PHASE50_A2F_DEPLOY_FAIL=unexpected_target_delta:PROJECT_CONTEXT.md` and Exit Code 1.

**Root cause:** `PROJECT_CONTEXT.md` is a legitimate repository-root documentation file changed by the same reviewed A2F documentation checkpoint, but the runner allowlist accepted `docs/*` and forgot this root document.

**Safety result:** failure happened in the target-delta gate before the backup/ff-only merge stage. Production source remained on `e12fdaf...`; no migration or database write was run. The printed BACKUP_ROOT was only the precomputed path at the fail boundary.

**Correct fix:** explicitly allow only root `PROJECT_CONTEXT.md` in addition to the existing reviewed paths; keep the default `unexpected_target_delta` fail-closed rule for every other unreviewed path.

**Prevention:** deployment allowlist tests must cover every intentionally changed root-level documentation file in the exact baseline-to-target delta before a Host run.

### ERR-49-114 — Production documentation lagged behind completed 3I.53G recovery
**Date:** 2026-09-12
**Environment:** Production cPanel Host + authenticated live Bridge readiness.

**Observed:** Repository documentation still described Production as Host HEAD `5f6c13ab...` with Store 0039 failed/pending. Fresh read-only FTPS Git metadata instead showed Host branch HEAD `e12fdaf...`; a 53G current-partial backup dated 2026-09-10 existed, Passenger restart evidence followed it, and authenticated `/api/catalog-bridge/v1/publish-readiness/` returned HTTP 200, `ready=true`, `blockers=[]`, MySQL, Store 0036–0042 + Website 0024 applied, and complete receiver schema.

**Root cause:** recovery execution advanced Production after the last documentation checkpoint, but repository state docs were not updated with that later Host evidence. Relying on the stale checkpoint would have encouraged rerunning a recovery runner whose starting assumptions were no longer true.

**Failed/unsafe condition avoided:** the old 53G runner was not rerun against `e12fdaf...`; no fake migration, manual recorder write, duplicate-column change, or direct FTPS source deployment was performed.

**Correct fix:** treat live read-only Production evidence as reality, record 3I.53G as recovered, and use a new Phase50.A.2F no-migration deploy runner that requires exact recovered baseline `e12fdaf...`, empty migration plan and `publish_readiness.ready=true` before source promotion.

**Verification:** Host migration/recovery files are byte-identical to GitHub; Bridge health HTTP 200/status ok; publish-readiness HTTP 200/ready true/no blockers; required migrations and schema all present. Local/GitHub configurator SHA `38458ce...` passed the canonical Windows gate.

**Prevention:** every completed Production recovery/deploy must update CURRENT_STATE/HOST_CONSTRAINTS/PATHS/ROADMAP with the exact final Host SHA, migration recorder state, backup path and restart/readiness evidence before later deployment planning.
### ERR-49-113 — Desktop Commander PowerShell location did not change .NET relative-path resolution
**Date:** 2026-09-12
**Environment:** owner Windows Local documentation update through Remote Desktop Commander.

**Observed:** a documentation update command began with `Set-Location D:\projects\3DPrintHub` but direct `[IO.File]::ReadAllText('docs\\...')` calls still resolved below the Desktop Commander npm process directory. Missing-path exceptions occurred and a non-fail-fast script printed a misleading final success marker. No repository document changed in that failed command.

**Root cause:** PowerShell provider location and the host process current directory are not a safe shared contract for direct .NET relative-path APIs in this remote execution boundary.

**Failed condition:** the same relative-path command was not repeated.

**Correct fix:** direct .NET file APIs use absolute paths rooted at the already-verified `D:\projects\3DPrintHub` and update commands use `Stop='Stop'` before any success marker.

**Verification:** corrected absolute-path write is followed by Git diff/readback before commit.

**Prevention:** repository commands may use `Set-Location` for Git/PowerShell cmdlets, but direct .NET/Python helper paths must be explicitly repository-rooted and fail-fast.
### ERR-49-112 — MySQL recovery CI initially crossed unrelated historical migrations and had probe harness import errors
**Date:** 2026-09-02
**Environment:** GitHub Actions while adding real-MySQL coverage for ERR-49-111.

**Observed:**
- a full all-app MySQL-from-zero job stopped in third-party `sb_admin_audit.0001` because MySQL rejected an indexed TEXT/BLOB `object_id`;
- a Store-targeted from-zero job stopped at historical `store.0009` with MySQL key length > 3072 bytes;
- the first focused 0039 probe then failed compile because Python cannot use direct import syntax for module component `0039_...`;
- the next probe executed by pathname from `scripts/ci` and could not import project package `config`.

**Root cause:** the first CI strategy was too broad for a Production incident occurring on a mature database whose historical migrations are already applied. The focused test harness then repeated two Python execution-boundary mistakes already seen elsewhere: numeric migration modules require `importlib`, and an external script path must explicitly place Repository root on `sys.path`.

**Failed conditions:** none of these failed jobs were rerun unchanged.

**Correct fix:** scope real-MySQL evidence to the exact 0039 idempotent AddField operation. Import `store.migrations.0039_phase50_filament_offer_pricing` through `importlib.import_module`, and bind the Repository root before `django.setup()`.

**Verification:** exact tested checkpoint `66e940e6e659f86e3783d78d091b3ff00acbf5aa`; Product Admin workflow `33666085743` PASS; MySQL probe markers `MYSQL_ADDFIELD_EXISTING_COLUMN_SKIP=PASS`, `MYSQL_ADDFIELD_MISSING_COLUMN_ADD=PASS`, `MYSQL_ADDFIELD_PROBE=PASS`; Single Active AI `33666085841` PASS.

**Prevention:** incident CI must reproduce the failing boundary, not unnecessarily replay unrelated historical migrations. Numeric migration modules are imported with `importlib`; repository scripts executed by pathname must bind Repository root explicitly before Django setup.


### ERR-49-111 — MySQL 0039 duplicated ProductVariant.support_weight_grams and left a partial migration
**Date:** 2026-09-02
**Environment:** Production MySQL `sfkilvrs_EmiAdmin_3dprinthub`, Phase49.3I.53F resume.

**Observed:** exact migration plan was accepted. Website 0024, Store 0037 and Store 0038 applied successfully. Store 0039 then stopped with:
`django.db.utils.OperationalError: (1060, "Duplicate column name 'support_weight_grams'")`.

**Root cause:** `store.0033_phase49_3f_pricing_intelligence` already creates physical column `ProductVariant.support_weight_grams`. Store 0039 later declared another `AddField` for the same ProductVariant field. SQLite-focused migration gates did not expose the MySQL duplicate-column boundary.

**Historical correction:** ERR-50-016 correctly identified metadata drift around the same runtime field, but its wording treated 0039 as the migration authority without noting that 0033 had already created the physical column. The real schema history is: 0033 creates the ProductVariant column; 0039 must only align its migration state/metadata for that field while adding the new filament/order fields.

**Partial-state risk:** MySQL schema DDL is not a single safely rollbackable transaction across this migration. Operations executed before the duplicate-column statement may persist although Django does not record 0039 as applied. Never fake 0039 and never blindly rerun the old migration.

**Correct fix:**
- ProductVariant `support_weight_grams` in 0039 is now `AlterField`, not `AddField`;
- new 0039 columns use `AddFieldIfMissing`, which introspects the target table and skips only a column that already physically exists;
- dedicated recovery runner verifies the exact migration-recorder + physical-schema boundary before mutation;
- it re-verifies prior rollback dumps and creates a fresh CURRENT-PARTIAL MySQL dump before applying the corrected chain.

**Verification:** implementation `bec98fc5a5e40ed534364cc3eb1047759c2a3cdc`; Variant/Profile `33664796042` PASS; final Product Admin + focused real MySQL probe `33666085743` PASS; Single Active AI `33666085841` PASS; exact tested checkpoint `66e940e6e659f86e3783d78d091b3ff00acbf5aa`.

**Prevention:** before adding a field in a later migration, search all historical migrations for the same physical model/column. Production MySQL migration gates must include a real-MySQL operation probe for recovery-sensitive custom schema operations. A failed MySQL migration must be treated as possible partial DDL until recorder and table schema are both inspected.

### ERR-49-110 — lazy transport refactor temporarily removed mature AIProviderClient patch seam
**Date:** 2026-09-02
**Environment:** GitHub Product Admin CI `33663092964`.

**Observed:** after fixing Host startup import safety, mature test `test_auto_policy_prefers_exact_verified_free_persian_structured_model` failed because it patches `ai.model_policy.AIProviderClient`, but the first lazy-import implementation had removed that module attribute.

**Root cause:** import-safety refactor preserved runtime behavior but unintentionally broke a mature testing/extension seam.

**Failed condition:** the failed CI was not rerun unchanged.

**Correct fix:** restore `ai.model_policy.AIProviderClient` as a lazy compatibility constructor that imports the real transport class only when called. `_provider_client` delegates through that symbol, so existing patches keep working while Django startup remains independent of httpx.

**Verification:** `ccd1b98997a8dd0c8389ccbe2b6c78b83dd7f176`; Product Admin `33663316332` PASS; Single Active AI `33663316324` PASS.

**Prevention:** when converting eager imports to lazy factories, preserve mature public/patchable module seams unless there is an explicit deprecation contract.


### ERR-49-109 — target source promoted before required httpx dependency was installed
**Date:** 2026-09-02
**Environment:** Production Host third Phase49.3I.53 deploy attempt.

**Observed:** valid source/MySQL/.env/pending backups were fully verified and source fast-forwarded from `198fa8e...` to `b372586a...`. The first post-merge `manage.py check` then failed:
`ModuleNotFoundError: No module named 'httpx'`.

**Root cause:** target `requirements.txt` adds `httpx==0.28.1`, but the deploy runner did not reconcile target runtime dependencies before invoking target Django code. The failure was amplified by eager Site-AI imports: `store.apps.ready` imports Site authoring AI, which imported `ai.model_policy` and `ai.product_content`; those imported desktop provider modules requiring httpx even for ordinary Django startup.

**Production state:** source is already at `b372586a...`; DB migrations did not run; collectstatic and Passenger restart did not run. The verified 21:10 pre-migration backup is valid and preserved.

**Failed condition:** do not rerun the old deploy runner from baseline `198fa8e...` because Host source is no longer at that baseline. Do not run migrations manually before dependency/startup recovery.

**Correct fix:**
- make provider/client imports lazy at the Site AI boundary;
- preserve existing `AIProviderClient` patch seam through a lazy compatibility constructor;
- add regression proving Django setup does not import httpx;
- make normal deploy install/verify exact target httpx after rollback backup and before target source execution;
- add a dedicated post-merge resume runner for current `b372586a...` state that re-verifies rollback evidence, applies source boot-safety fix, installs exact dependency, creates a fresh DB backup, verifies migration state/plan and only then migrates/restarts.

**Verification:** recovery checkpoint `ccd1b98997a8dd0c8389ccbe2b6c78b83dd7f176`; Product Admin `33663316332` PASS; Single Active AI `33663316324` PASS.

**Prevention:** Production deploys must treat requirements/runtime dependency delta as a first-class gate between verified rollback backup and execution of target Django code. Optional operator AI transport must not be imported during normal Site bootstrap.

### ERR-49-108 — extracted MySQL backup helper could not import Production Django config
**Date:** 2026-09-02
**Environment:** Production Host second Phase49.3I.53 deploy attempt.

**Observed:** gzip helper execution stopped with `ModuleNotFoundError: No module named 'config'` while running from the timestamped backup directory.

**Root cause:** the helper is deliberately extracted outside the repository before source promotion. Executing a Python script by pathname makes the script directory the first import path entry; the Production repository root was not explicitly on `sys.path`. Shell `cd` alone was not a reliable import contract.

**Safety result:** failure occurred before `PREDEPLOY_BACKUP_VERIFIED=YES`; no source merge, migration, collectstatic, or Passenger restart occurred.

**Failed condition:** do not rerun the previous helper/target unchanged.

**Correct fix:** require explicit `PHASE49_PROJECT_ROOT`, validate `manage.py` + `config/__init__.py`, insert that verified root at the front of `sys.path`, and have the deploy runner pass the known Production root. Keep the helper outside the repository so backup still precedes source promotion.

**Verification:** code `2016b84ee1b053e792ceb44ede516b3d7a2dea7e`; Product Admin CI `33661199115` PASS; Single Active AI `33661199159` PASS.

**Prevention:** any repository helper copied/executed outside the repository must receive its project root explicitly; never rely on current working directory to define Python import semantics.

### ERR-49-107 — MySQL gzip helper self-test exceeded Linux argv limit
**Date:** 2026-09-02
**Environment:** GitHub Product Admin CI `33659570675`.

**Symptom:** the newly added backup helper self-test failed with `OSError: [Errno 7] Argument list too long`.

**Root cause:** the test embedded a multi-megabyte synthetic mysqldump payload directly inside one `python -c` argv element. The Production helper itself does not do this.

**Failed condition:** the same oversized-argv test was not rerun unchanged.

**Correct fix:** keep the child command bounded and generate the large synthetic payload inside the child process; continue exercising the same stdout-pipe → gzip encoder → round-trip verification boundary.

**Verification:** `3b6254bf7700bb26b4af63d21e31e56e7700877c`; Product Admin CI `33659707983` PASS; Single Active AI `33659707957` PASS.

**Prevention:** subprocess compression tests must stream large payloads through stdin/stdout/files, not encode them into argv or environment variables.


### ERR-49-106 — mysqldump was written raw through a GzipFile descriptor
**Date:** 2026-09-02
**Environment:** Production Host first Phase49.3I.53C deploy attempt.

**Observed:** all predeploy gates passed and mysqldump reported a 17,469,650-byte file at `.../20260902-203857-phase49-3i53/database-before-3i53.sql.gz`, then `gzip -t` failed with `not in gzip format`.

**Root cause:** the runner opened a Python `gzip.GzipFile` and passed that object directly as `subprocess.run(stdout=target)`. Subprocess consumes its OS file descriptor, so mysqldump wrote raw SQL bytes directly to the underlying file and bypassed the gzip encoder.

**Safety result:** the runner stopped before `PREDEPLOY_BACKUP_VERIFIED=YES`; no ff-merge, migration, collectstatic or restart occurred. The failed artifact is evidence only and is not a valid compressed restore backup.

**Failed condition:** do not repeat the old runner unchanged and do not trust a `.gz` suffix without gzip verification.

**Correct fix:** repository helper `scripts/host/phase49_3i53_mysql_backup.py` launches mysqldump with `stdout=PIPE`, streams bytes through `gzip.open(...)` in the parent process, keeps stderr out of a pipe, validates gzip magic + mysqldump payload signature, and then the runner performs `gzip -t` + SHA256 manifest verification.

**Verification:** final code `3b6254bf7700bb26b4af63d21e31e56e7700877c`; Product Admin/backup CI `33659707983` PASS; Single Active AI `33659707957` PASS.

**Prevention:** never pass compression wrapper objects directly to subprocess stdout/stderr expecting the child process to execute the wrapper's codec. Child-process output must be piped through the parent codec or written plain then compressed in a separate verified step.

### ERR-49-105 — Host forensic helper used unavailable system python3 and stale audit baseline
**Date:** 2026-09-02
**Environment:** cPanel Host `/home/sfkilvrs/3dprinthub`.

**Observed:** the first read-only deploy audit stopped on a dirty worktree because of untracked `ls-output.txt`. Follow-up forensics proved tracked files/index were clean and actual Host HEAD was `198fa8e41ea4f4d87eb287ba69c91076acc78d62`, but the helper then stopped at `bash: python3: command not found` before secret-marker scanning, ancestry and live-target checks completed.

**Root cause:** two assumptions were stale/wrong:
1. the ad-hoc forensic helper used generic `python3` instead of the documented Production venv Python;
2. the repository audit runner still hardcoded historical Production HEAD `c283864...`, while GitHub comparison proves the actual Host HEAD `198fa8e...` is 23 commits ahead of it and on the same ancestry chain.

**Failed condition:** do not rerun the same helper with `python3`; do not reset Host to `c283864...`; do not rerun the old hardcoded audit script unchanged.

**Correct fix:** use `/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python` for Host Python probes; parameterize the audit runner so the operator-verified current Host HEAD is passed explicitly as argument 2; keep live GitHub target as argument 1; preserve strict clean-worktree and no-deploy semantics.

**Verification:** commit `d0984e1f9e01d959c028d2714c4814b6556acd84`; Product Admin/audit CI `33656829478` PASS; Single Active AI `33656829551` PASS.

**Prevention:** Host operational scripts must use the verified project venv interpreter and must accept a read-only verified baseline rather than freezing an old Production SHA in source.

### ERR-49-104 — Bridge-only Windows fixture crossed the new Site readiness boundary
**Date:** 2026-09-02
**Environment:** first Phase49.3I.53 Windows Qt run `33652583946` on code `bca8aceee9b08935e82aea36f82d3f331e079d83`.

**Symptom:** 3I.51 finalization parity failed in `test_bridge_only_settings_and_test_do_not_require_ftp_credentials`. The fixture mocked mature Bridge health only; `ConnectionCore.test_bridge()` now also queried the new publish-readiness endpoint, so the test unintentionally made a live request to the currently older Production Site and received HTTP 404.

**Root cause:** the new readiness check was intentionally added to the Bridge operator test, but the historical fixture did not isolate that second network boundary. Runtime also needed a clean compatibility state for the valid transition period where Bridge health exists but the new readiness endpoint has not yet been deployed.

**Failed condition:** the same failed workflow was not blindly rerun.

**Correct fix:**
- keep `publish_many()` fail-closed: a missing/failed readiness endpoint still blocks Product upload before FTP;
- make the Settings Bridge-health test catch readiness-request failure and report `ready=false` / endpoint unavailable while preserving the successful Bridge-health result;
- update the isolated Windows test to mock both Bridge health and readiness;
- add a regression proving Bridge health survives an old Site 404 while publishing remains blocked.

**Verification:** final code `62ce5c3393a888cc1a027e4ca6bbb88f189bc845`; Qt `33653229142` PASS; Portable `33653229400` PASS; Single Active AI `33653229219` PASS.

**Prevention:** connection health and business-operation readiness are separate contracts. Transitional compatibility may report a missing capability, but a mutating operation must continue to fail closed until that capability is proven.

### ERR-49-103 — 52G drifted mature legacy acquisition identity and Source Refresh history
**Date:** 2026-09-02

Intermediate Windows acquisition regression on `0dcc2053d75a3e50fa341ed61d8a2d075b3dc52a` showed Saved HTML persisted `qt52g-saved_html` instead of accepted `qt46-legacy-saved_html`, and Source Refresh no longer emitted the mature `source_refresh` history event.

Root cause: adaptive recovery widened persisted method naming and replaced an unrelated mature Source Refresh implementation. The failed condition was not rerun unchanged.

Fix: restore historical `qt46-legacy-<method>` provenance and the mature Source Refresh implementation; keep adaptive failover scoped to Product receive/recovery. Final runtime `bf1fafdb38233a23e13a5715ffac72f772412005` passed Qt `33644903042`, Single Active AI `33644902970`, Portable `33644902962`.

Prevention: resilience work wraps mature operators; it must not silently rename persisted provenance or replace unrelated refresh semantics.


### ERR-49-102 — first 52G block edit removed existing Preview/refetch helpers
**Date:** 2026-09-02

First 52G portable regression on `d4763fa3716917d15c5bcaad20136a4d187cf8c4` stopped because `_cache_candidate_thumbnail` was missing; source comparison also found `_preview_listing_candidates`, `_mark_candidate_result` and synchronous `refetch_product_from_source` removed.

Root cause: a broad Python block replacement crossed mature helper definitions. The same failed command was not repeated unchanged.

Fix: compare the exact pre-change runtime and restore all four helpers unchanged, then continue regression testing. Final runtime `bf1fafdb38233a23e13a5715ffac72f772412005` passed all three Windows workflows.

Prevention: before/after top-level function inventories are required for broad region edits; prefer smaller Extend/Patch/Wrap boundaries.

## ERR-49-101 — bulk recovery test mock expired before captured Worker execution
**Date:** 2026-09-02
**Environment:** Windows Portable regression for Phase49.3I.52F.

**Observed:**
After fixing the missing QMessageBox import, the incomplete-existing-Product recovery test still reported `recovered=0`.

**Root cause:**
The test patched `AcquisitionCore.run_single`, queued the Worker, exited the patch context, and only then executed the captured Worker function. The real recovery path therefore ran outside the mock boundary.

**Correct fix:**
Execute the captured Worker while the `run_single` patch is still active.

**Verification:**
Final runtime `cf73f841418aac2eec1b78e0dbd682ceb2d3fef5`: dedicated visual/recovery suite 19 tests PASS; Qt `33637452385` PASS; Portable `33637452243` PASS with 227 release regressions.

**Prevention:**
For deferred Worker tests, mock lifetime must cover Worker execution, not merely Worker construction.

---

## ERR-49-100 — new bulk recovery tests omitted QMessageBox import
**Date:** 2026-09-02
**Environment:** Windows Portable regression for Phase49.3I.52F.

**Observed:**
The first 3I.52F portable regression stopped with `NameError: QMessageBox is not defined` in the two new recovery-confirmation tests.

**Root cause:**
The test module used `QMessageBox.question` but its QtWidgets import list had not been extended.

**Correct fix:**
Add `QMessageBox` to the explicit PySide6.QtWidgets test import.

**Verification:**
The next run crossed that boundary and exposed ERR-49-101; after both conditions were corrected, final Qt/Portable gates passed.

**Prevention:**
New concrete Qt widgets referenced by tests must be imported explicitly and exercised in the same Windows suite.

---

## ERR-49-099 — Preview recovery raw JavaScript string temporarily lost its closing triple quote
**Date:** 2026-09-02
**Environment:** GitHub source edit during Phase49.3I.52E.

**Observed:**
While extending the listing Preview DOM payload, an intermediate edit to `phase49_3i_preview_recovery.py` omitted the closing Python raw-string delimiter around `PREVIEW_CARD_EVAL_JS`.

**Root cause:**
The file update replaced the JavaScript block by text slicing and consumed the original closing triple quote.

**Response:**
The malformed condition was inspected immediately and corrected before the final CI run. The broken condition was not used for owner Local QA and was not deployed.

**Correct fix:**
Restore the explicit closing `"""` and keep the JavaScript newline represented as escaped `\n` inside the raw Python string.

**Verification:**
Final runtime `016e84ab98d2e5577633833cbc87cb96824dbbf0`: compile/full Qt parity `33632062812` PASS; Portable `33632062880` PASS; 223 release regressions PASS.

**Prevention:**
Any future edit of embedded JavaScript in Python must be covered by compileall plus the existing Windows Preview regression before acceptance.

---

## ERR-49-098 — Qt Crawl inventory ignored mature downloaded images when Product linkage was missing
**Date:** 2026-09-02
**Environment:** owner foreground Windows QA, Catalog Center 8.9.10 / Qt6.

**Observed evidence:**
The Crawl inventory showed rows such as MakerWorld external ids with `Preview تصویر ندارد` even though the mature Catalog Center had already downloaded image files. The same owner screenshot also showed the requested-count and image-limit QSpinBox digits colliding with RTL arrow controls.

**Verified mature storage contract:**
The retained Tk runtime stores persistent data in `D:\projects\3dprinthub-catalog-manager`, and Product downloads in `collected\<source_code>\<external_id>\images` with optional finalized `seo_images`. The old installed application target `D:\projects\3dprinthub_catalog_center` is not the canonical active SQLite data root.

**Root cause:**
The Qt queue image path was gated by `product_id`. If a `discovered_urls` row was old/unlinked, Qt skipped the mature Product image resolver and only checked the newer `discovery_previews` cache. Therefore real files could exist under the mature collected tree while the UI still claimed no Preview. Product resolution also compared `source_code` case-sensitively, so legacy `MakerWorld` vs current `makerworld` could keep a valid Product row unlinked. Separately, global RTL layout + generic QSpinBox padding caused Windows arrow/text overlap.

**Correct fix:**
- add read-only ImageCore identity resolution rooted at the actual Catalog SQLite parent;
- scan mature `seo_images` then `images` for `<source>/<external_id>` even before Product linkage;
- preserve DB `local_dir` as first authority;
- accept the old retained install tree only as a secondary read-only fallback if physically present;
- make bounded Crawl Product matching source-code case-insensitive;
- use actual local-file count/icon in queue/current-search cards regardless of Product linkage;
- make the two receive spinboxes explicitly LTR, centered, width-bounded and padded away from the arrow subcontrol.

**Failed attempts / prevention:**
Do not solve this by downloading the same images again or moving/deleting old folders. The existing mature files are authoritative evidence. UI image lookup must resolve the existing storage contract before triggering acquisition.

**Implementation:** `a18b6f3036d41271cf3e8c1d9a0dfd8c271a53ce`.

**Verification:**
- `33628825851` Qt full parity PASS;
- dedicated 3I.52C/52D suite: 13 tests PASS, including mature-folder-without-Product-link, source-code case mismatch and non-cramped numeric controls;
- `33628825772` Single Active AI PASS;
- `33628825715` Portable PASS, 221 release regressions;
- artifact `9846044486`;
- EXE SHA256 `c08aa1e9d12926203cb59c580aab6c606c2b0e259ad83df37aa3b3abec86c22a`.

**Safety:** no migration, no Product data rewrite, no image move/delete, no Host/Production change.

---

## ERR-49-097 — 3I.52C Qt regression was added to Portable release gate without the Qt runtime dependency
**Date:** 2026-09-02
**Environment:** GitHub Actions `Catalog Center Windows Portable Release`, run `33624135587`.

**Observed evidence:**
The new 3I.52C regression was intentionally added to the portable release regression gate. The job installed only `catalog_center/requirements.txt`, then failed while importing `test_phase49_3i52c_crawl_review_recovery` with `ModuleNotFoundError: No module named 'PySide6'`. Compile had already passed; packaging did not start.

**Root cause:**
The release regression set crossed the Qt test boundary but its dependency install step still described the older non-Qt portable environment. The dedicated Qt workflow already installed `requirements-qt6.txt`; the portable regression workflow did not.

**Failed condition was not repeated unchanged.**
The workflow dependency boundary was changed before rerun.

**Correct fix:**
- cache both `catalog_center/requirements.txt` and `catalog_center/requirements-qt6.txt`;
- install `catalog_center/requirements-qt6.txt` in the portable regression environment so the explicit Qt regression can import the same PySide6 runtime used by the dedicated Qt gate;
- do not weaken or remove the new 3I.52C regression.

**Implementation:** `b43880a763d00bfda52dc29c4bf080cb428b1230`.

**Verification:**
- `33625043651` — Windows Portable — PASS;
- release regression gate: 215 tests PASS;
- EXE self-verify PASS;
- browser smoke PASS;
- artifact id `9844568575`;
- EXE SHA256 `97bbb9bd485b2b82da2d83fe9e8c193d62dd47210233626772afee5f36e58a8f`.

**Prevention:**
Whenever a shared release regression gate imports a framework-specific test suite, that job must install the dependency contract required by that suite. Do not solve dependency drift by deleting the regression that exposed it.

---

## ERR-49-096 — New 3I.52B Site-pull regression missed one import and the isolated test crossed the real Bridge settings boundary
**Date:** 2026-09-02
**Environment:** GitHub Windows Qt CI during Phase49.3I.52B.

**Observed evidence:**
- run `33619483446` reached the new 3I.52B test only after all mature Qt regressions through 3I.51 passed;
- `apply_server_product_to_local()` raised `NameError: utc_now is not defined`;
- Site-pull orchestration tests then raised the existing ConnectionCore validation that Site URL + Bridge token must be configured;
- after importing `utc_now`, run `33619558541` proved the runtime mapping test passed and only the three Site-pull fixture cases still crossed the real Bridge settings boundary.

**Root cause:**
1. the newly expanded Site→Local helper called the mature Catalog timestamp helper without importing it;
2. the new orchestration tests mocked the remote Product list but still called the real `ConnectionCore.bridge_settings()`, which correctly refuses an unconfigured Bridge token.

**Failed attempts / rule:**
- the first failed test was not rerun unchanged;
- after the import fix, the remaining failure was reclassified as a test-isolation/configuration-boundary issue rather than weakening the production Bridge credential guard.

**Correct fix:**
- commit `d6450ca2d9016bbdb75b37b7a31d20d8c2b6d111` imports `utc_now`;
- commit `6d19bed7659b9ca4cd54ff1ffd1323ec423bea6a` provides an isolated `bridge_settings` fixture while keeping the remote Product list mocked;
- no fake secret is persisted and the real Bridge settings validation remains unchanged.

**Verification:**
- `33619876564` final Qt full parity PASS, including 3I.52B plus all mature acquisition/Filament/Profile/Stage/launcher regressions;
- `33619876317` Single Active AI PASS;
- `33619876411` Windows Portable PASS;
- `33619558467` Product Admin/Bridge/migration CI PASS on runtime-equivalent source.

**Prevention:**
Cross-boundary Qt orchestration tests must provide the complete local configuration boundary they intentionally traverse, even when the remote transport function itself is mocked. Production credential validation must never be weakened merely to make an isolated test pass.

# PROJECT ERROR KNOWLEDGE BASE

## ERR-49-095 — Filament Bridge v3 palette normalization overwrote explicit legacy HEX slots
**Date:** 2026-09-02
**Environment:** GitHub Product Admin/Bridge CI during Phase49.3I.51.

**Observed CI evidence:**
Run `33610330120` failed only in `test_invalid_color_type_is_normalized_and_inactive_sync_updates_same_row`: expected legacy `secondary_hex=#112233` but the Bridge persisted `#445566`.

**Root cause:**
The v3 Bridge normalized `palette_hexes` correctly for the modern palette contract, but then reused palette positions to overwrite explicit compatibility fields `secondary_hex`/`tertiary_hex`. Those compatibility slots are independently supplied by mature callers and must not be silently remapped.

**Failed condition was not repeated unchanged.**
The Bridge parsing/persistence boundary was changed before rerun.

**Correct fix:**
Normalize explicit single HEX fields separately; keep `palette_hexes` authoritative for the modern palette while preserving valid explicit compatibility slots when supplied.

**Implementation:** `ca89533d6d4546a008c04b31efa56c8cf6efe3a1`.

**Verification:**
Final Site/Admin/Bridge run `33611936196` PASS, including Bridge v3 regressions.

**Prevention rule:**
When modernizing a payload, do not infer that a compatibility field is merely an alias of a new aggregate field unless the mature contract explicitly says so.

---

## ERR-49-094 — Phase49.3I.51 Filament editor description field crashed because QPlainTextEdit was not imported
**Date:** 2026-09-02
**Environment:** GitHub Windows Qt CI.

**Observed CI evidence:**
Run `33610057719` reached the real offscreen Filament editor construction and failed with:
`NameError: name 'QPlainTextEdit' is not defined` in `catalog_center/qt6/parity_dialogs.py`.

**Root cause:**
Phase49.3I.51 added the optional Filament description editor but omitted `QPlainTextEdit` from the PySide6 QtWidgets import list. Compile-only validation could not detect the runtime symbol lookup.

**Failed condition was not repeated unchanged.**
The import was added before the next full Qt run.

**Correct fix:**
Import the concrete Qt widget and keep offscreen dialog construction in the regression suite.

**Implementation:** `ca89533d6d4546a008c04b31efa56c8cf6efe3a1`.

**Verification:**
Final Windows Qt run `33611776817` PASS, including 3I.48 and 3I.51 Filament editor construction/behavior.

**Prevention rule:**
Every newly introduced concrete Qt widget must be exercised by offscreen construction; compileall alone is not a sufficient GUI dependency test.

---

## ERR-49-093 — Phase49.3I.51 fallback regression referenced a helper that does not exist in that test class
**Date:** 2026-09-02
**Environment:** GitHub Windows Qt CI / Phase49.3I.51 regression alignment.

**Observed CI evidence:**
The first updated source-profile fallback regression attempted to call a Product helper that belongs to a different test class and stopped before testing the actual owner fallback contract.

**Root cause:**
The test contract changed from “do not create a fallback Profile” to the owner-requested explicit default Profile, but the rewritten fixture accidentally reused a helper unavailable in that class.

**Failed condition was not repeated unchanged.**
The fixture was corrected before rerun.

**Correct fix:**
Create the Product through the same `Database.upsert_product` path already used by the suite, then resolve its id from the kernel Product list.

**Implementation:** `f3dd80bd7fc6293c73aa4f9353aad6e40eb9dc9d`.

**Verification:**
Dedicated 3I.51 regression and final Qt run `33611776817` PASS.

**Prevention rule:**
When an acceptance contract changes, keep fixture construction local to the test class or use a shared verified fixture helper; do not copy helper calls across suites without resolving ownership.

---

## ERR-49-092 — Phase49.3I.50 Crawl technical-fact regression used a bare test schema and failed on a pre-existing image metadata column
**Date:** 2026-09-02
**Environment:** GitHub Windows Qt CI / exact code checkpoint `7aadf4830061c2104cda6b4164e0f9b1351f8893`.

**Observed CI evidence:**
- Qt foundation/full parity passed;
- the acquisition strategy step failed only in the newly-added Crawl technical-fact test;
- traceback: `sqlite3.OperationalError: no such column: image_metadata_json` from `Database.discovered_items_page()`;
- `image_metadata_json` was already a mature Qt image-pipeline column before 3I.50.

**Root cause:**
The new test created a bare `Database()` and installed only the Epic49 desktop schema. Real Qt startup composes `ensure_qt_parity_schema()`, which also installs the mature image/profile/slider/stage schemas. The regression therefore exercised an impossible partial runtime schema rather than the application contract.

**Failed condition was not repeated unchanged.**
The fixture was changed before the next CI run.

**Correct fix:**
Initialize the regression through the same `ensure_qt_parity_schema()` composition used by `build_kernel()`.

**Implementation:** `b6bc5b08903e6880d01dc0fd27d7f8c2b17fab47`.

**Verification:**
- `33601229888` — Qt full parity — PASS;
- `33601229884` — Windows Portable — PASS;
- later runner-only checkpoint `d45730990cc90002fb1da1236380e033a379db7a`: `33601382428` Qt full parity PASS.

**Prevention rule:** clean-schema tests for Qt surfaces must initialize the real composed Qt schema, not an arbitrary subset, unless the test explicitly targets that lower-level subset.

---

## ERR-49-091 — Phase49.3I.50 Color registry crashed in CI because the canonical palette normalizer was not imported
**Date:** 2026-09-02
**Environment:** GitHub Windows Qt CI / early 3I.50 Brand/Color registry implementation.

**Observed CI evidence:**
- compile succeeded;
- constructing the real MainWindow/FilamentsPage failed at runtime;
- `NameError: normalize_palette_hexes is not defined` in `FilamentParityCore.color_presets()`;
- failing Qt run: `33600561989`.

**Root cause:**
The new registry reused the mature palette-normalization function but the symbol was omitted from `qt6/parity_core.py` imports. Static compile could not detect this runtime name lookup.

**Failed condition was not repeated unchanged.**
The canonical import was added before rerun.

**Correct fix:** import `normalize_palette_hexes` from `app.epic49_desktop_schema` rather than duplicating palette logic.

**Implementation:** `65cded6d1f22c653ff63e0c6c62f89743a805871`.

**Verification:**
- `33600690429` — Qt full parity — PASS;
- `33600690527` — Single Active AI — PASS;
- final 3I.50 Qt run `33601382428` — PASS.

**Prevention rule:** reusable UI registries must import and test the same canonical normalizers used by persisted Filament data; full MainWindow construction remains a mandatory runtime regression.

---

## ERR-49-090 — Hybrid Listing HTTP 403 stopped before the existing robots-gated Browser fallback
**Date:** 2026-09-02
**Environment:** owner Local Windows Qt6 / GrabCAD public library URL.

**Observed owner evidence:**
`AccessDeniedError: HTTP 403 for https://grabcad.com/library` was raised by `discover_conditional_http` and propagated from `_discover_listing`, so the already-existing browser acquisition path was never reached.

**Root cause:**
Hybrid discovery re-raised `AccessDeniedError` together with fail-closed robots/rate-limit errors even though the browser branch already had its own `_browser_robots_gate`.

**Correct fix:**
- continue only once from static HTTP AccessDenied into the mature browser collector;
- do not retry the same blocked static request;
- keep `RobotsDeniedError` and `RateLimitedError` fail-closed;
- run the existing browser robots gate before navigation.

**Implementation:** `98badc4d43f34dd991fe5c5ebcee1946342c88e0`.

**Verification:**
- regression proves one blocked HTTP attempt → one robots gate → one browser discovery;
- final Qt full run `33601382428` PASS;
- Modern Acquisition run `33600888264` PASS on the implemented acquisition subset.

**Safety:** this is a fallback, not an access-control bypass. Login/CAPTCHA/robots restrictions remain enforced.

**Prevention rule:** an HTTP access-denied response from a public Listing is not equivalent to a robots denial. Fallback may occur only through an independently robots-gated browser path and must never repeat the unchanged blocked request.

---

## ERR-49-089 — Filament editor crashed because QWidget was used but not imported
**Date:** 2026-09-02
**Environment:** owner Local Windows Qt6 / Filament Library.

**Observed owner evidence:**
Repeated traceback from `FilamentEditorDialog`:
`NameError: name 'QWidget' is not defined` at `palette_host = QWidget()`.

**Root cause:**
`catalog_center/qt6/parity_dialogs.py` used `QWidget` for palette/image/Profile containers but its QtWidgets import list omitted `QWidget`.

**Correct fix:** restore the PySide6 `QWidget` import and add a regression that constructs the Filament editor offscreen.

**Implementation:** `789d07b75b70ab34042e35a5b1ca57848774ac03`.

**Verification:**
- dedicated Filament editor construction regression PASS;
- 3I.48 Filament/registry stage in final run `33601382428` PASS.

**Prevention rule:** every Qt dialog introduced or expanded with concrete widgets must be instantiated in offscreen CI; compile-only validation is insufficient for missing runtime symbols.

---


## ERR-49-088 — Phase49.3I.47 owner Local gate broke on Windows PowerShell 5.1 because a non-ASCII QA label violated the established ASCII-only runner contract
**Date:** 2026-09-01
**Environment:** owner Local Windows PowerShell 5.1 / canonical branch / exact head `946b8594f0ee001bd9833973e23eb47803c98bac`.

**Observed owner evidence:**
- the owner cleanly fast-forwarded from `ecfd9260...` to `946b8594...`;
- repository, branch and remote-head guards all passed;
- execution stopped before the 3I.47 tests with `ParserError` / `TerminatorExpectedAtEndOfString` at `RUN_PHASE49_3I42C_LOCAL_GATE.ps1:376`;
- the affected line was a manual-QA `Write-Host` string containing Persian text;
- the prior 3I.46 Local gate had already passed on the same machine and had created a checksum-matching Catalog SQLite backup.

**Root cause:**
- `ERR-49-016` already established that Windows runner scripts must remain ASCII-only because Windows PowerShell 5.1 does not use UTF-8 as its default script/text boundary;
- Phase49.3I.47 introduced exactly one non-ASCII Persian line into an otherwise ASCII runner;
- the Qt workflow parsed the runner under `pwsh` (PowerShell Core), whose UTF-8 behavior did not reproduce the owner's Windows PowerShell 5.1 parser path;
- therefore CI had a coverage gap even though the project already had the correct prevention rule.

**Failed condition was not repeated unchanged.**
The stale command against `946b8594...` was not rerun. The runner and CI boundary were changed first.

**Correct fix:**
- replace the Persian QA label with an ASCII-only equivalent without changing the QA meaning;
- enforce an exact raw-byte ASCII check for the owner Local runner;
- parse the runner under real `shell: powershell` / Windows PowerShell 5.1 before the existing `pwsh` parser/stdin regression;
- retain the existing PowerShell→Python stdin boundary from ERR-49-081;
- bump the runner identity to `49.3I.47.2` so owner evidence can distinguish the repaired gate from the broken `49.3I.47.1`.

**Implementation:**
- `1a4a8add5fa8afbdf87ce9bada389be3d0199e11` — runner restored to ASCII-only;
- `d71e3a8be012ed0e2759c99d0c37a0a01c7428d8` — Windows PowerShell 5.1 ASCII/parser CI guard;
- `36a710953276aae99fa668f477ad5569f8dc23ba` — repaired runner versioned as `49.3I.47.2`.

**Verification:**
- exact source checkpoint `36a710953276aae99fa668f477ad5569f8dc23ba`;
- `33511403943` — `qt6-full-parity-windows` — PASS;
- the explicit `Validate owner Local gate on Windows PowerShell 5.1` step PASS;
- existing `pwsh` parser/stdin step PASS;
- Qt foundation, acquisition, AI/Crawl, bounded paging, 3I.47 workspace/image/bulk-AI, mature acquisition, Filament, Profile/Commerce/Stages, Single Active AI, offscreen launch, legacy launcher and final source guards all PASS;
- `33511403901` — Phase49.3I.17 Single Active AI — PASS.

**Rollback:** `backup/pre-err49-088-ps51-runner-ascii-20260901` → pre-hotfix 3I.47 branch state.

**Safety:** no Django migration, no Catalog data rewrite, no Host/Production source change, no Production DB write, no secret change.

**Prevention rule:** every owner-facing `.ps1` that must run on Windows PowerShell 5.1 remains ASCII-only unless the project explicitly changes the runtime contract. CI must validate the actual owner shell, not only `pwsh`.

---

## ERR-49-087 — Phase49.3I.46 stabilized Catalog paging/acquisition but owner workflow presentation parity was still incomplete
**Date:** 2026-09-01
**Environment:** owner Local/visual QA request after Phase49.3I.46.

**Observed owner requirements/regressions:**
- Add Product / Crawl controls consumed too much vertical space and hid the inventory;
- the inventory lacked a usable Windows-like image/details presentation with Product thumbnail, title, description and image count;
- Product management needed explicit Active / Sent-Published / Archived / Rejected-Deleted workspaces;
- old Products with usable local media could still appear without thumbnails;
- multi-select Products needed the same full-content AI completion used by a single Product;
- image finalization had to apply the same semantic SEO identity to every selected Product image while producing distinct ordered filenames;
- Profile/Pricing nested-scroll layout clipped production rows;
- Admin/Storefront information architecture needed the same task-oriented hierarchy without changing business authority.

**Root cause:**
Phase49.3I.46 correctly fixed bounded data loading and restored acquisition Core parity, but presentation/workflow parity was intentionally not the same task. The healthy data/acquisition Core therefore existed underneath a still-dense operator layout.

**Correct fix — Phase49.3I.47:**
- task-oriented tabs/workspaces instead of one tall acquisition control wall;
- gallery/details inventory views with Product facts and local-thumbnail fallback;
- lifecycle Product workspaces;
- sequential multi-select full-content AI through the existing shared `AICore`;
- all selected Product images receive consistent semantic SEO metadata and unique numbered final WebP names (`-01`, `-02`, `-03`, ...);
- Profile/Pricing split into full-height task tabs;
- Admin/Storefront task-oriented tabs added as presentation architecture only; pricing/business authority remains unchanged.

**Verification:** dedicated `test_phase49_3i47_qt_workspace_image_bulk_ai.py`, Phase50 Product Admin workspace regression and Storefront Product tabs regression passed in GitHub CI. The same 3I.47 Qt regression is also included in the full Windows parity run `33511403943`.

**Safety:** no Production deploy, no Host write, no Django migration introduced by this presentation slice.

**Prevention rule:** performance/core stabilization and operator information architecture are separate acceptance contracts. Do not declare presentation parity from backend/Core availability alone.

---


## ERR-49-085 — Qt Product AI JSON-mode/TLS, semantic translation, final SEO WebP and hidden Crawl/Product lifecycle parity
**Date:** 2026-09-01
**Environment:** owner Local Windows Qt6 screenshots/traces + GitHub Windows CI.

**Observed owner evidence:**
1. `openai/gpt-oss-20b` could terminate at `httpx.ConnectTimeout / _ssl.c:993 handshake operation timed out` before an HTTP response.
2. `google/gemma-4-31b-it:free` returned OpenRouter 404 `No endpoints found that can handle the requested parameters` because the Product path forced strict JSON Schema routing.
3. `Driftbloom Table Lamp Organic Ambient Desk Lamp` was rendered as a nonsensical Persian title.
4. `AI همه مراحل محتوایی` could leave finalized bad translation/SEO untouched.
5. Image SEO fields could look correct in the dialog while the visible/physical file still used an old downloaded JPG/PNG name.
6. Stage 6 numeric controls exposed awkward spinner buttons.
7. Product cards did not make lifecycle/SEO state obvious and lacked requested bulk lifecycle actions.
8. Existing persistent Crawl records were present in SQLite but not exposed as a manageable inventory.

**Root cause:**
- OpenRouter model capability classification treated generic `response_format` as if it guaranteed strict JSON Schema;
- transient connect/TLS failure had no bounded stale-pool reset/retry boundary;
- semantic title guard was too shallow for compound Product identity/meaning;
- full-content AI respected finalization locks even when the operator explicitly requested repair;
- Qt image presentation preferred source/cache media before mature finalized SEO media and metadata save did not re-run the binary finalizer;
- Qt Product/Crawl pages did not expose mature persistent ledger/lifecycle state;
- release bump initially changed `app/version.py` without all independent manifest/config/launcher/workflow version contracts;
- Qt CI path filters did not guarantee a full-parity rerun when those release-contract files changed.

**Correct fix:**
- distinguish strict Schema vs JSON mode; use provider JSON-object mode where supported, then enforce the exact schema locally;
- keep `provider.require_parameters=true`, exact model identity and Product safety gate;
- bounded two-attempt connect/TLS retry with pooled-client reset only after connect-class failure;
- semantic guard for Table/Desk Lamp, Organic and Ambient while preserving proper-name identity;
- explicit full-content repair reopens only `quick/content/slider`;
- prefer/rebuild final SEO WebP and preserve operator image metadata overrides;
- add persistent Crawl inventory + Product lifecycle/SEO surfaces with reversible bulk actions;
- hide Slider spin buttons and keep direct typed values/units;
- align all 8.9.10 version contracts;
- include release/version contract files in the Qt full-parity workflow trigger.

**Intermediate failed condition — not repeated unchanged:**
Runs `33488612681`, `33488612733`, `33488612771` and Qt run `33488612672` failed on stale 8.9.9 release contracts. Functional ERR-49-085 Qt tests themselves were already passing. The stale manifest/config/launcher/workflow contracts were corrected before new CI was accepted.

**Implementation checkpoints:**
- `2bfefffa96adf1451e754a8f6ab35cd9ef9e0b7c` — OpenRouter JSON mode/TLS + semantic translation;
- `202e018c26e49d90734b87709ff2e7104473b3d3` — visible Qt content repair/final SEO WebP/Slider UX;
- `1aefbcfd43e2f88fcef46f1925f27c0bf7075f52` — lifecycle + persistent Crawl cores;
- `235712d7530ae26ae9e3af74a7bd0a8dedd06ff9` — visible Crawl inventory + bulk Product lifecycle UI;
- `0a3660c00d2483fa219e5e7121c7f0e06fa8fab0` — 8.9.10 release bump;
- `205ceff6b7033e2fcd6f03c25dc8a81720ae067d` — complete 8.9.10 version-contract alignment;
- `12284a255d27451b9160eeb48bc289f4f34fdc16` — Qt full-parity trigger prevention for release-contract changes.

**Final verification:**
- `33488996741` Single Active AI — PASS;
- `33488996767` Modern Acquisition — PASS;
- `33488996802` Portable Release — PASS;
- `33489296415` latest Single Active AI — PASS;
- `33489296349` latest Qt6 Crawl + AI Runtime full parity — PASS.

**Release artifact:** `3DPrintHub-CatalogCenter-v8.9.10`, ID `9793033040`, digest `sha256:68099747e151677fa355dcc4f0dad7d290a5f35ce8ad3ad5ff739dfba88e5533`.

**Rollback:**
- `backup/pre-err49-085-openrouter-jsonmode-image-qt-parity-20260901` → `f1c4fe58c04510d1721e3af2b3366925893fe1dc`;
- `backup/pre-err49-085-8-9-10-release-20260901` → `235712d7530ae26ae9e3af74a7bd0a8dedd06ff9`.

**Safety:** no Django migration, no Production MySQL write, no Host/Production source change, no secret change, no hard Product delete, no CAPTCHA/auth/proxy bypass.

**Prevention rule:** provider capability, release-version contracts and user-visible lifecycle/media state are separate contracts. Never infer strict Schema from generic JSON-mode support; never report/display final SEO media from a source cache when a finalized artifact exists; and every release bump must be validated simultaneously by manifest/config/launcher + the full Qt regression trigger set.


## ERR-49-084 — Product AI Link mode failed on MakerWorld 403 before Provider execution and apply success was not persistence-verified
**Date:** 2026-08-31
**Environment:** owner Local Windows Qt6 / Product #309 / Stage 1 `quick`.

**Observed owner evidence:**
- `provider=openrouter, model=openrouter/auto-beta, source_mode=link, stage=quick` failed at `crawler.public_http` with HTTP 403;
- exact `openai/gpt-oss-20b` failed at the identical stack location;
- the trace never reached `generate_translation_pack` / the OpenRouter request boundary;
- prior runs could receive AI output yet fail to produce the expected visible Product change.

**Root cause:**
1. Qt Product AI called `orchestrate_once` directly. Link mode resolved the source with `live_source_for_ai`, which used the direct public HTTP path and had no saved-data fallback for an explicit upstream 403/429.
2. The same blocked request could therefore make every AI model appear broken even though the Provider had not been called.
3. `changed_fields` was extended immediately after calling `db.update_product`; there was no post-write re-read proving the requested values persisted.
4. the previous variable-router gate matched exact `openrouter/auto` but did not catch the observed `openrouter/auto-beta` variant.
5. scoped locked/no-work stages could enter source acquisition before proving an AI request was actually needed.

**Correct fix:**
- Link remains live-first;
- catch only explicit `BlockedError` for blocked/rate-limited public HTTP and do not repeat that failed request unchanged;
- on that condition, use already persisted, sanitized Product/Crawl facts when they contain a valid source title;
- if persisted facts are insufficient, fail with an explicit source-data message and preserve the original block as the cause;
- expose requested vs effective source mode and show the fallback in Qt;
- run scope/no-work checks before live HTTP/Provider work;
- re-read SQLite after each AI stage update and compare every requested field before reporting it as changed;
- fail loudly when persistence cannot be verified;
- classify all `openrouter/auto*` IDs, including `openrouter/auto-beta`, as variable routers.

**Regression coverage added:**
- Link 403 → saved Product data fallback → Stage-1 Persian title actually persists;
- locked scoped Stage 1 performs no source fetch and no Provider generation call;
- a simulated no-op DB update raises instead of claiming success;
- both `openrouter/auto` and `openrouter/auto-beta` fail the Product default compatibility gate.

**Verification on exact code checkpoint `0c67fa30493d100b99ec37314586e0491ecbcda5`:**
- `33409112402` — Qt6 Crawl + AI Runtime CI — PASS;
- `33409112322` — Single Active AI CI — PASS;
- `33409112381` — Stage Finalization + Commerce Precision CI — PASS;
- `33409112367` — Windows Portable build/self-verify/artifact upload — PASS.

**Rollback:** `backup/pre-err49-084-ai-link-fallback-apply-verify-20260831` → `4802f8ba0ca7920f6ee047ebd4ffb57e45025d0a`.

**Safety:** no Django/Catalog migration, no Host/Production write, no secret change, no source/media bulk rewrite, no CAPTCHA/auth/proxy bypass.

**Prevention rule:** a source acquisition failure must never be presented as an AI-model failure. Link-mode AI must distinguish requested source from effective evidence source, must not retry a known blocked request unchanged, and must never report a field as applied until the persisted database value has been re-read and verified.

## ERR-49-082 — OpenRouter Product AI accepted media/tools-only models and could fall back to unconstrained text
**Date:** 2026-08-31
**Environment:** owner Local Windows Qt6 foreground QA after Phase49.3I.42C3.

**Observed owner evidence:**
1. Provider test used `google/lyria-3-clip-preview` and the Structured Product JSON path received timed Persian song lyrics instead of a JSON object, ending in `JSONDecodeError`.
2. Product #309 with `cohere/north-mini-code:free`, source mode `link`, failed because `SEO Title فارسی` returned empty.
3. Product #309 with the same model, source mode `data`, failed because the Persian title was generic/invalid and did not preserve source identity.

The existing downstream content validators behaved correctly: they rejected empty SEO and generic Product identity before bad content could be saved.

**Root cause:**
- model suitability ranking did not use live output modality/product-purpose metadata;
- `tools` / `tool_choice` were incorrectly treated as equivalent to native `response_format` / Structured JSON support;
- a music/media model could therefore appear usable for Product text work;
- a tools-only coding model could receive an overly strong Product/JSON badge;
- OpenRouter Structured calls used a weaker `json_object` request and could fall back to prompt-only JSON when a model rejected `response_format`, allowing unconstrained prose/song/code output;
- active Product AI did not require a previously verified live OpenRouter model capability profile before execution.

**Correct fix:**
- classify live model input/output modalities and exclude non-text media/embedding/rerank/moderation models from Product filters;
- separate native Structured JSON support from tool-calling support;
- mark coding-specialist models as unsuitable for Persian Product SEO/content;
- Product recommendation/sort now prioritizes text-capable + native Structured + Persian quality, then free/cost;
- OpenRouter Structured Product calls use strict `json_schema` and `provider.require_parameters=true`;
- OpenRouter no longer falls back to prompt-only JSON when the required Structured contract is unsupported;
- Structured Product calls use latency-first routing while ordinary bulk/content paths retain their existing routing intent;
- saving an OpenRouter Product model requires a live loaded model catalogue entry and stores a non-secret capability snapshot;
- Product AI estimate/execute preflight rejects stale/unverified/incompatible OpenRouter models before the mature orchestrator runs;
- settings UI now distinguishes `JSON✓`, Tools-only, coding-specialist and non-text models, and Product filters hide non-text models.

**Regression coverage:**
- Lyria/music model is rejected as non-text Product model;
- `cohere/north-mini-code:free` is rejected as tools-only/code-specialized Product Structured candidate;
- OpenRouter Structured request carries strict JSON Schema + `require_parameters`;
- exact selected model remains preserved;
- simple connection test still performs no hidden model-catalog scan;
- mature Qt/Crawl/Filament/Profile/Stage/Single-AI/legacy launcher regressions remain green.

**Intermediate failed condition:** run `33398832365` failed only because an older 42B2 regression still expected Structured Product routing to use `throughput`. The runtime condition had intentionally changed to latency-first. The stale test was corrected rather than rerunning the same failing expectation unchanged.

**Final verified code checkpoint:** `0421bccff040ced53513625af95d05e0c8c27a9a`.
- `33399095190` — Phase49.3I.42C3 Qt6 Crawl + AI Runtime CI — PASS;
- `33399095198` — Phase49.3I.17 Single Active AI CI — PASS;
- `33399095224` — Catalog Center Windows Portable Release — PASS.

**Rollback:** `backup/pre-err49-082-openrouter-product-model-gate-20260831` → `26761c81d04bbd74dc2c978b08e77f3250b0518b`.

**Safety:** no Django migration, no Catalog schema migration, no Product/media rewrite, no secret persistence, no Host/Production change, and no default launcher cutover.

**Prevention rule:** a Provider connection success is not a Product-model acceptance test. Product AI must require a text-capable model with verified native Structured JSON support and a real Persian Product probe; tool calling, free pricing or generic multilingual capability alone must never imply Product suitability.


## ERR-49-081 — Windows Playwright smoke probe was corrupted at the PowerShell/native `python -c` boundary
Status: `FIXED IN REPOSITORY / WINDOWS CI PASS / OWNER LOCAL RERUN NEXT`

Observed:
- owner Local was clean on the canonical branch and correctly advanced to `3f7038b52723aa2b70cd12d4c1a617c50d0ad4d8`;
- Catalog SQLite backup completed and source/backup SHA256 both matched `F0C1341C764074423A2214F0DFF80EEB9E1248DA69F5FE9470D1FDDA0B1A5422`;
- Python 3.12.10, PySide6 6.11.2, HTTPX 0.28.1, Protego and Playwright imports were healthy;
- the gate then stopped at the Playwright smoke marker with `NameError: name 'OK' is not defined`, and the retry produced the same class of error for `OK_AFTER_INSTALL`.

Root cause:
the Local runbook passed a multi-line Python here-string through the native-process `python -c` argument boundary. Windows PowerShell/native quoting transformed the quoted marker before Python evaluated it. The gate incorrectly classified this probe-code failure as a missing Chromium runtime and attempted an unnecessary browser install.

This was not evidence of a Qt acquisition/runtime defect. The Python traceback reached the marker line after `p.chromium.launch(headless=True)`, so the first browser launch itself had already succeeded.

Correct fix:
- repository-owned `RUN_PHASE49_3I42C_LOCAL_GATE.ps1` now sends multi-line Python through stdin: `$Script | & $Py -`;
- Chromium installation is attempted only when the actual Playwright error explicitly reports a missing executable / `playwright install`;
- other probe failures stop without a blind reinstall;
- the Qt Windows workflow now parses the Local gate with PowerShell's parser and regression-tests the exact PowerShell → Python stdin boundary.

Implementation:
- `71c55010bc900e8d3c1afd7cea71441193db68eb` — resilient owner Local gate;
- `e6980fcfb2bdc72846e007e9d935290225dcb39e` — CI syntax/stdin guard;
- Single Active AI run `33386654622` PASS;
- Phase49.3I.42C workflow run `33386654632` PASS, including PowerShell parser validation, the exact PowerShell → Python stdin regression boundary, Qt/acquisition regressions and launcher guards.

Prevention:
- do not send multi-line Python containing nested quoting through `python -c` in Windows Local gates;
- use stdin or a repository script for multi-line Python;
- only install Playwright browsers when the failure is actually a missing-browser failure;
- a probe/quoting error must never be relabeled as a dependency error;
- do not repeat the failed inline command unchanged.

## ERR-49-080 — Qt42B2 rollout CI exposed generated-source and guessed-test-name defects
Status: `FIXED / FINAL WINDOWS CI PASS`

Observed:
1. run `33369083134` stopped at compile because `qt6/__init__.py` contained literal escaped-newline text and the Stage-5 saver missed an opening call parenthesis;
2. run `33369290159` then reached mature regressions but referenced nonexistent `tests.test_phase49_3i35_operator_ledger`;
3. run `33369521548` passed compile/Qt/Filament/Profile/Stage regressions but referenced nonexistent `tests.test_phase49_3i17_single_active_ai_runtime`.

Root cause:
- one generated source blob serialized newlines incorrectly and one generated call site lost punctuation;
- the aggregate Qt workflow guessed two unittest module names instead of verifying the real Repository test names / canonical Single Active AI workflow.

Failed conditions were not repeated unchanged.

Correct fixes:
- `74e95a943d3324f3d00b4e61bd9a265efcca4e3f`: fixed real newlines and Stage-5 call syntax;
- `d433395cabc8ed488431f3b873adc337acb7d6b6`: switched to existing `tests.test_phase49_3i35_operator_workflow`;
- `c3b0105eaa6c6141eb6d6d8463a96d547101564c`: switched to canonical `tests.test_epic49_phase49_3i17_single_active_ai_runtime`.

Verification:
- final Windows Qt run `33369749205` PASS with every job step successful;
- dedicated Single Active AI run `33369749123` PASS;
- compile, Qt parity, mature Filament/Profile/Stage/AI regressions, Qt launcher, legacy launcher and source guards all passed.

Rollback anchors:
- `backup/pre-phase49-3i42b2-full-legacy-parity-20260830` → `6260f94cee531124446cf1b3e19ce0d95554d594`;
- `backup/pre-err49-080-qt42b2-compile-hotfix-20260831` → `fc4edfd3ccab089ac242e84f291dd6454b85d7d7`.

Prevention:
- generated source blobs must compile before functional tests;
- workflow test module names must be verified from the actual Repository tree or canonical workflow, never inferred;
- a failed CI command is not rerun until its root condition changes.


## ERR-49-079 — Qt Local preview gate used an obsolete ExpectedHead
Status: `FIXED / PREVENTION RULE ADDED`

Observed:
- owner Local checkout started clean on the canonical branch at `92a3f4df...`;
- `git fetch` + `git pull --ff-only` correctly advanced Local to live GitHub `3d32c251...`;
- the old 42A runbook still expected historical `fde58f38...`;
- the guard stopped with `UNEXPECTED HEAD - STOP` before backup/install/compile/Qt launch.

Root cause:
the runbook pinned a previously valid 42A documentation HEAD while the same canonical branch had legitimately advanced through 3I.43–45.

Resolution:
- do not rerun the stale command;
- verify the live remote branch SHA first;
- only then use the current approved GitHub HEAD in the guarded Local pull/test command.

Prevention:
every Local/Host runbook that pins a commit must compare its expected SHA to the live GitHub branch before write/install/migration/test steps. A mismatch is a stale-runbook stop, not an application failure.


### ERR-49-078 — robots.txt unreachable policy was incorrectly treated as unavailable
**Date:** 2026-08-30
**Environment:** Catalog Center 8.9.9 / Phase49.3I.43–45 public acquisition.

**Symptom/Risk:** the pre-fix `robots_policy()` generic exception path returned `allowed=True`. A robots 5xx/network failure could therefore be treated the same as a genuine robots 4xx-unavailable resource and allow acquisition while policy was temporarily unreachable.

**Root Cause:** robots resource states were collapsed into one catch-all branch instead of distinguishing unavailable, unreachable and rate-limited outcomes.

**Correct Fix:** commit `11379ca343c64c251e9c34dd907dffa5f7529e12` makes the robots gate explicit:
- genuine robots 4xx unavailable → `known=False`, `allowed=True`, status `unavailable`;
- HTTP 429 → `known=True`, `allowed=False`, status `rate_limited`;
- transient 5xx/network/transport failure → `known=True`, `allowed=False`, status `unreachable`;
- unexpected robots fetch/parse failure → conservative fail-closed `unreachable`.

Existing conditional-cache, Retry-After/cooldown and robots pacing behavior remain intact.

**Regression:** `tests/test_phase49_3i43_modern_acquisition_intelligence.py` now covers unreachable fail-closed, 4xx unavailable/non-blocking and 429 fail-closed states.

**Verification:** dedicated Windows workflow `33313008595` PASS on `846cb63038a79cfe450f5a60aa66e531cf6fe0de`, which contains this fix, plus all 3I.43/3I.45 modern acquisition tests and mature 3I.16/3I.38 acquisition regressions.

**Rollback:** `backup/pre-err49-078-rfc9309-robots-failclosed-20260830` → `3616bf222f394b769cb2e3198164d735fca5267b`.

**Prevention:** acquisition policy code must model unavailable, unreachable, rate-limited and explicitly denied states separately. A temporary network/server failure must never silently become permission.

### ERR-49-077 — Qt6 workflow referenced runner context before a runner/job existed
**Date:** 2026-08-30
**Environment:** new Phase49.3I.42 GitHub Actions workflow.

**Symptom:** run `33299686593` failed immediately and contained zero jobs.

**Root Cause:** `runner.temp` was referenced in job-level `env`. The runner context is not available at that workflow evaluation boundary, so GitHub rejected the job before execution.

**Failed condition:** do not rerun the same workflow definition unchanged.

**Correct Fix:** keep only static `QT_QPA_PLATFORM=offscreen` in job env and resolve `CATALOG_DATA_ROOT` inside the Windows PowerShell step using `$env:RUNNER_TEMP` after the runner is created.

**Verification:** corrected run `33299745502` PASS across dependency install, compile, Qt tests, 3I.41 regression, offscreen launcher, legacy launcher guard and no-Tk source guard.

**Prevention:** GitHub contexts with runner lifecycle scope must be resolved at step runtime unless documentation explicitly permits their use at the earlier evaluation boundary.


### ERR-49-076 — Stage-2 multi-Filament selection was technically possible but operationally ambiguous
**Date:** 2026-08-29
**Environment:** Catalog Center 8.9.8 / Stage 2 after ERR-49-075.

**Symptom:** an inventory with many Filaments could only be managed through an extended Treeview selection whose multi-select behavior depended on Ctrl/Shift. The operator could not clearly see the complete Product selection set, global Filament definition was mixed into Product editing, and repeated Products encouraged repeated manufacturer/material typing.

**Root Cause:** the older UI modeled global Filament inventory and per-Product assignment as one filtered table. The data model already had reusable global inventory, but the final operator surface did not expose that ownership boundary.

**Correct Fix:** Phase49.3I.41:
- global main-app Filament Library;
- grouped PLA/PETG/etc. rows;
- one-click child/group checklist;
- dedicated Product selected-Filament pane;
- reusable manufacturer/brand/material selectors;
- explicit Product commit;
- Product fixed-price preservation;
- Site Bridge Filament entity synchronization.

**Site consistency:** Save/update/deactivate uses authenticated Bridge Filament upsert. Local save remains successful if the Site is temporarily unreachable; status is reported truthfully and Sync All is available.

**Migration safety:** no new migration. The bridge endpoint depends on existing `store.0039` + `0040`; do not deploy to Production until actual Host migration state and backups are verified.

**Rollback:** `backup/pre-phase49-3i41-filament-library-sync-20260829` → `92a3f4dfcf64d5fedaf837eb9a37dac028cabd59`.

**Prevention:** global reference/master data must have a dedicated management surface; Product forms should select from it and separately display the Product-owned selection state rather than overload native multi-select keyboard semantics.


### ERR-49-075 — saved Filament hidden after save and price preview used stale/zero facts
**Date:** 2026-08-29
**Environment:** Catalog Center 8.9.8 / Phase49.3I.40 after ERR-49-074 owner visual QA.

**Owner visual evidence:**
- a newly created Filament saved successfully but did not become visible in the current list;
- the main inventory row showed a valid sale rate (example owner evidence: `4,200 تومان/گرم`) while the price preview opened on a different/stale Filament and showed material/print/supervision/preheat/total as zero;
- the selected-Filament editor was still the older 3I.39 dialog (including the Product fixed-price field) instead of the final 3I.40 global Filament editor with live rate calculation;
- current mode could be `range`, while the popup still attempted formula-style component rows, which was misleading.

**Root Cause:**
1. `add_available_material_color()` wrote all operational fields but its immediate post-upsert SELECT omitted `print_hourly_rate`, `supervision_hourly_rate`, preheat fields and `filament_image_url`; a just-saved in-memory snapshot therefore lost those facts until a later full inventory reload.
2. `edit_selected_offer()` directly called the local 3I.39 `open_offer_editor` closure, bypassing the final 3I.40 method override.
3. after save, the current manufacturer/material filters were not switched to the saved Filament, so a valid new row could be hidden by the previous filter.
4. pricing preview/summary primarily used the persisted Product Filament snapshot; it did not refresh that snapshot from current global Filament facts and did not use an unregistered currently selected Filament as a draft preview.
5. `range` preview fell through to the formula table instead of explaining the active range mode.

**Correct Fix:**
- return the complete operational Filament row immediately after upsert;
- route selected-Filament editing through the final composed 3I.40 editor;
- after save, switch company/material filters to the saved Filament, refresh the list, select/focus/scroll to the exact row;
- resolve pricing from fresh global Filament facts while preserving Product-only fixed price;
- if the operator selects a not-yet-registered Filament, use it as a clearly marked draft price preview;
- make range preview show the stored range and explicitly instruct switching to formula mode for component calculation;
- keep the explicit `ثبت Filamentهای انتخابی روی محصول` boundary; saving a global Filament does not silently attach it to the Product.

**Code:** `38d030024463a2057a10ad338abff5b030eb7e50`, `ab5f35523cbd76c79ed81344be57eb6b7485b075`, `cb78cb3ceb771fab54fcb8876dcd080516dcd462`, ttk fix `93b6e5c017965e50e62052afea37bfb30a86cc9d`.

**Regressions:** `ed4784f3019b2cf48c212ea429cb1b67420cbc97`, `58aac85bfd4bc0875d21c107515c8050fe0ddf74`, `7e7f8fcf3c07b5aeae9bc59684cc6fac97699f2d`, `d8661288273834a98627a1ec257b838b4a4ab086`.

**Rollback:** `backup/pre-err49-075-filament-refresh-pricing-preview-20260829` → `d66c68f36d1fd3e4143d461bccd999046c4baaf7`.

**Verification status:** GitHub source/tests updated. Owner Local compile + focused/full regression + short foreground Stage-2 QA is required. Production untouched.

**Prevention:** any DB upsert helper used to hydrate UI state must return the same operational facts that a full list/read returns; final composed UI callbacks must delegate through the class method override rather than close over an earlier implementation.


### ERR-49-074 — final Stage-2 price/rate calculation disappeared from the visible operator surface
**Date:** 2026-08-29
**Environment:** Catalog Center 8.9.8 / Phase49.3I.40 after owner acceptance of ERR-49-073.

**Owner evidence before change:** exact ERR-49-073 regressions 2/2 PASS, OpenRouter-only 4/4 PASS, full Windows stage regression 73/73 PASS, foreground launch PASS. The image Metadata refresh issue cleared and the owner reported the Product ready for publication. Remaining Stage-2 usability regression: the mature calculation logic still existed, but the always-visible final amount/rate result had been removed from the final 3I.39/3I.40 composition. The visible buttons also still said `Offer`, while the operator terminology requested is `Filament`.

**Root Cause:** Phase49.3I.39 retained `formula_price_breakdown()` and a popup preview, and 3I.40 retained the exact global filament-rate facts, but the final visible Stage-2 card no longer exposed the computed final amount continuously. User-facing labels inherited internal historical `offer_*` naming.

**Correct Fix:**
- restore an always-visible final price summary for fixed, formula and range modes;
- formula summary uses the existing exact material + print + supervision + preheat + assembly calculation across registered Filaments and valid production rows;
- global Filament editor now shows the live final roll basis and exact Toman/gram rate from explicit sale price versus USD × explicit FX; no FX is invented;
- visible buttons/dialogs/readiness say `Filament`, not `Offer`;
- retain internal `offer_*` function/schema/API identifiers for backward compatibility; no storage/schema rename;
- enlarge the Filament editor so the added calculation panel and action buttons remain visible.

**Code:** `9540558468cc75bf0248547e7440f3647eeb4cd3`, `0c795bc0b7084b2e175f47f34533aa596d90fb03`, `267dc565b25ca74f3971334b7ad37d5c919a98ac`, regressions `109aaea748e7750bb22295aedf94de34ce617d88` + `4efc5a8350a3e9fbb7ade41f1098bc9cb9c80a7c`, layout `e4c1f3345bf9416bde11b6b6c7c7d31f6cdfd09c`.

**Rollback:** `backup/pre-err49-074-filament-rate-final-display-20260829` → `954c0516661e6c70145d7f6f395b4e92ceeb40bd`.

**Must not touch:** Catalog DB schema, Product identity, image/SEO finalization, OpenRouter AI contract, crawler/acquisition, Django migrations, Production.

**Verification status:** GitHub code/regressions updated. Owner Local focused/full/foreground retest is required before starting the website receive/deploy batch.

**Prevention:** final UI composition tests must assert not only that pricing math exists, but that the operator can continuously see the authoritative result and the requested domain terminology.


### ERR-50-017 — Store 0040 CI froze Decimal string presentation instead of numeric value
**Date:** 2026-08-29
**Environment:** GitHub Actions `Phase50 Variant2 + Profile Matrix CI`, migration `store.0040_phase50_filament_offer_operations`.

**Symptoms:** compile, Storefront JavaScript, Django check, `makemigrations --check --dry-run`, migration plan and full CI SQLite migration all passed, but the regression step had two failures:
- `preheat_hours`: expected string `24.00`, runtime serialization returned `24`,
- `current_stock_grams`: expected string `3000`, runtime serialization returned `3000.0000`.

**Root Cause:** tests asserted a presentation-specific Decimal string even though the business/API contract is the numeric value. Equivalent Decimal values can have different textual scales.

**Failed Attempt:** do not rerun workflow `33246706102` unchanged; the deterministic assertions would fail again.

**Correct Fix:** compare the Decimal facts numerically rather than freezing insignificant trailing-zero formatting.

**Verification:** fix commit `b59c93cf37dcb66d3e97f61d2669df6e1d1644a4`; Phase50 workflow `33246843145` PASS, including full migration through 0040 and 21 Store/Profile/Checkout/Offer regressions.

**Prevention:** only assert exact decimal string formatting when formatting itself is an explicit public contract. For numeric commerce facts, normalize/compare numerically.

# ERROR KNOWLEDGE BASE

Search this file before troubleshooting. Never repeat a failed action unchanged. Detailed incident transcripts remain in Git history; this file keeps the current operational root-cause/fix/prevention knowledge.

## RESOLVED / CANONICAL PHASE49 ERRORS
- **ERR-49-001 — Tk pack/grid collision:** one geometry manager per parent; use holder frames.
- **ERR-49-002 — delayed thumbnail callback after widget destruction:** verify widget lifetime before async UI mutation.
- **ERR-49-003 — destroyed ProductWorkspace used as messagebox parent:** async result must verify parent existence.
- **ERR-49-004 — missing optional shell attributes:** guarded access only.
- **ERR-49-005 — image SEO semantic signature false-stale:** normalize structured JSON before hashing.
- **ERR-49-006 — dynamic consultation flag overwritten:** downstream state uses contract-aware merge/OR.
- **ERR-49-007 — PS5.1 NativeCommandError despite exit 0:** native exit code is truth.
- **ERR-49-008 — trace Bearer redaction order leak:** mask Bearer credentials first.
- **ERR-49-009 — later phase installed inside older independent installer:** compose phases at launch/runtime root.
- **ERR-49-010 — Bridge main-image materialization failure:** target Media ownership is a publish prerequisite.
- **ERR-49-011 — test guessed upsert return contract:** resolve persisted product by real identity.
- **ERR-49-012 — security test coupled to one mask format:** assert secret absence semantically.
- **ERR-49-013 — explicit MakerWorld Search URL ignored:** explicit valid operator URL is authoritative.
- **ERR-49-014 — discovery full-fetched before review:** Preview and acquisition are separate.
- **ERR-49-015 — runtime pricing choices caused phantom migration:** never mutate migration-owned Django field metadata at runtime.
- **ERR-49-016 — PS5.1 runner encoding failure:** Windows runners are ASCII-only and CI-enforced.
- **ERR-49-017 — Products UI patch missed real UX87 boundary:** patch/test final visible composition boundary.
- **ERR-49-018 — AI progress painted after blocking preflight:** first-paint before blocking work.
- **ERR-49-019 — stale Chat-pinned HEAD:** live fetch + clean exact branch + ff-only + Local HEAD == Remote HEAD.
- **ERR-49-020 — product images clipped:** pixel viewport must not use Tk text-unit dimensions.
- **ERR-49-021 — page/group URL misclassified as Product:** source model URL pattern is authoritative.
- **ERR-49-022 — Treeview selection feedback loop:** one-way selection sync + reentrancy guards.
- **ERR-49-023 — secure credentials looked lost:** hydrate real visible controls from secure storage.
- **ERR-49-024 — Preview embedded JS invalid escaping:** embedded browser JavaScript escaping is regression-tested.
- **ERR-49-025 — Provider Hub keys/models missing visually:** hydrate current Provider Hub widgets.
- **ERR-49-026 — visible All-Fields bypassed Task Center:** exact visible action routes to bounded observable AI.
- **ERR-49-027 — AI rerun could not refresh generated fields:** refresh AI-owned values, preserve manual edits, reject generic titles.
- **ERR-49-028 — HTTP success then delayed Tk callback crash:** freeze exception values; bounded trace/watchdog.
- **ERR-49-029 — provider JSON schema mismatch / busy state:** exact schema + one repair + immediate abort release.
- **ERR-49-030 — exact-page discovery worked but UI hid state/results:** final UX87 boundary + live state + contain-fit images.
- **ERR-49-031 — Windows URL paste + batch browser flashing:** explicit paste, headless batch, visible per-candidate error.
- **ERR-49-032 — new UI hid mature scan controls and forced 403-prone route:** restore mature controls; optional paths additive.
- **ERR-49-033 — correct listing links still depended on fragile per-product Full Fetch:** bulk staging/Add-to-Products removes Rich Direct dependency.
- **ERR-49-034 — Locator.evaluate_all SyntaxError aborted discovery:** resilient discovery/image fallback ladder; never one technique as sole gate.
- **ERR-49-035 — Product AI mixed saved identity with provider fallback/model probes:** exactly one saved Provider/Model/key; no hidden model scan or AI-on-open.
- **ERR-49-036 — generic discovery title poisoned Product identity/SEO:** canonical source identity before persistence and before AI.
- **ERR-49-037 — Product AI could wait 210 seconds with weak start diagnostics:** bounded provider timeout + request-start/success/error/timeout trace.
- **ERR-49-038 — worker crossed Tk/Tcl thread boundary:** queue worker completions to the Tk main thread and snapshot Tk state before worker start.
- **ERR-49-039 — AvalAI Product request contract mismatch:** exact saved model + schema-first structured output + deterministic source fetch.
- **ERR-49-040 — diagnostics call rejected provider/model kwargs:** provider/model belong in sanitized detail; provider HTTP trace uses the dedicated AI request logger.
- **ERR-49-041 — hidden startup provider model scans:** model discovery is process-lifetime operator-explicit only.
- **ERR-49-042 — non-text model accepted for Product content:** reject obvious audio/music/image/video/embedding/moderation routes.
- **ERR-49-043 — exact-link AI triggered layered save storm:** persist only prerequisites before background generation.
- **ERR-49-044 — diagnostics/Product writes shared SQLite transaction connection:** dedicated diagnostics connection + serialized common DB writes.
- **ERR-49-045 — finite runtime log rotation conflicted with cumulative troubleshooting:** append-only runtime logging.
- **ERR-49-046 — delayed old gallery callback restored horizontal layout:** patch the final delayed layout callback at the outer composition boundary.
- **ERR-49-047 — Product AI completion depended on hidden image downloads:** text AI and source-image network acquisition are separate boundaries.
- **ERR-49-048 — readiness locking conflicted with canonical stage order:** readiness blocks publish, not navigation.

### ERR-49-049 — Exact-link category lookup called nonexistent `Database.categories()`
Correct fix: compatibility bridge delegates to mature `App.get_all_categories()` provider.

### ERR-49-050 — Exact-link canonical title helper bound `current_title` twice
Correct fix: delegate with named arguments matching the mature signature.

### ERR-49-051 — Production Hero referenced internal imported-catalog media
Correct fix: public Hero uses Product-owned gallery/main media or safe remote fallback; never widen public routing to imported working-media.

### ERR-49-052 — Product Save/AI rebuilt the entire Products gallery and thumbnails
**Date:** 2026-08-26
**Environment:** Windows Catalog Center with a large Product catalog.

**Symptoms:** pressing AI or editing a Product visibly refreshed the Products page; repeated actions became expensive with many cards/images.

**Root Cause:** mature `ProductStudio.save()` called global Product refresh/load methods even for silent Save; AI preflight reused silent Save and the Product Explorer rebuilt cards/thumbnails.

**Correct Fix:** Phase49.3I.29 defers global refresh and pages visible Products to 48 cards while retaining the full result set; Phase49.3I.31 batch refreshes once at the batch boundary.

**Prevention:** Product-scoped Save/AI must not rebuild the global Products Explorer. Batch may refresh once at completion.

### ERR-49-053 — Generic/silent Product Save could erase the canonical source URL
**Date:** 2026-08-26
**Environment:** Windows Catalog Center Product Workspace.

**Symptom:** after pressing an apparently unrelated Product action, the saved Product source link disappeared.

**Root Cause:** mature `ProductStudio.save()` calculated the canonical link only as `source_url.get().strip() or spec_source_url.get().strip()`. When both mirrored UI controls were temporarily blank, generic/silent Save wrote an empty `source_url`, recomputed `normalized_url` and regenerated fingerprint from empty identity. Silent Save is reused by close, refetch, AI preflight, publish and layered Workspace actions.

**Important previous condition:** this was not a crawler/OpenRouter/AvalAI deletion. The destructive write happened at the common Save boundary.

**Correct Fix — Phase49.3I.32:**
- final Workspace Save wrapper after all older layers,
- explicit non-empty link edits remain valid,
- transient dual-blank UI state preserves an already stored DB source URL,
- resolved canonical URL is fed back into both controls before mature Save,
- post-save invariant restores `source_url`, `normalized_url` and fingerprint if any legacy layer still clears them,
- already damaged Products recover only an exact previously stored HTTP/HTTPS URL: `product_history` first, matching `discovered_urls(source_code, external_id)` second,
- recovery is local-only, uses no network and never guesses/reconstructs a URL,
- recovery is recorded in Product history/diagnostics.

**Verification:** targeted CI run `32996526852` PASS and packaged Windows run `32997106056` PASS.

**Prevention:** generic Save, silent Save, AI, close, refetch, image or publish-related flows are never destructive unlink operations. Clearing a canonical source URL requires a future explicit separately confirmed unlink action.

### ERR-49-054 — First Catalog Center 8.8.2 Windows release gate retained stale `8.8.1` test literal
**Date:** 2026-08-26
**Environment:** GitHub Actions `Catalog Center Windows Portable Release`, run `32996526842`.

**Symptom:** Windows compile passed and all new Phase49.3I.32 source-link tests passed, but the regression stage failed after 112 tests with one failure: `Epic49OperatorUIContractTests.test_current_release_and_resilient_staged_exe_build_are_enabled` asserted `APP_VERSION == "8.8.1"` while runtime version was correctly `8.8.2`. Launcher/build/artifact steps were skipped because the gate stopped correctly.

**Root Cause:** a historical UI contract test hard-coded the previous release version instead of checking atomic release identity. The application/launcher/manifest/config had already moved to 8.8.2.

**Failed Attempt:** do not rerun `32996526842` unchanged; the failing condition was deterministic and unrelated to the source-link runtime fix.

**Correct Fix:** replace the stale literal with `APP_VERSION == PACKAGE_MANIFEST["version"]`; the dedicated launcher/config/version consistency test continues to verify the rest of the atomic release identity.

**Verification:** Windows rerun `32997106056` PASS on `5208aa4dd3b070e9a7c7c6d6dde9b60569879631`: full regression, launcher composition, source-link invariant, one-file PyInstaller build/self-verify, release manifest/SHA256 and artifact upload all PASS. Public Release publication was intentionally skipped pending owner QA.

**Prevention:** release tests must compare canonical identity sources, not freeze a previous version literal. Version bumps are atomic across runtime, launcher, manifest, config and tests.


### ERR-49-055 — Generated portable release output made the Local gate block its own next run
**Date:** 2026-08-27
**Environment:** canonical Windows checkout `D:\projects\3DPrintHub`.

**Symptom:** after a successful `-BuildExe` run, `catalog_center/release/` appeared as an untracked path. The next Phase49.3I.31-32 gate stopped at `WORKTREE DIRTY` before reaching `-LaunchApp`, so the new head was never actually launched.

**Root Cause:** `build_portable_exe.py` intentionally writes versioned EXE/manifest/SHA files under `catalog_center/release/<version>/`, but `.gitignore` ignored `build/` and `dist/` without ignoring the generated `catalog_center/release/` output. The gate correctly rejects real source dirt, but could not distinguish its own generated release output.

**Failed Attempt / Important distinction:** do not treat this log as an application startup crash. In the reported run the gate exited before the launcher step. Do not reset/stash/delete the generated EXE as a cleanup shortcut.

**Correct Fix:** add `/catalog_center/release/` to the repository `.gitignore` and regression-test that the generated release path stays excluded from Git status. Existing release files are preserved locally; no source/database/Production state is removed.

**Verification:** dedicated regression added in `catalog_center/tests/test_epic49_operator_workflow.py`; Windows CI run `33042158052` is the verification gate for the fix.

**Prevention:** any deterministic build/release output created inside the working tree must be explicitly ignored (or written outside the repository) before a clean-worktree gate depends on `git status`.


## RESOLVED PHASE50 / RELEASE INCIDENTS

### ERR-50-001 — Phase50 Admin CI used non-canonical Django environment names
Use `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`.

### ERR-50-002 — Dynamic ModelAdmin URL patch unstable at final URL boundary
Use explicit project-level routes wrapped by `admin.site.admin_view`.

### ERR-50-003 — Phase50/Catalog release identity mismatch class
Version identity is atomic across app version, launcher, manifest, config and tests; do not keep stale literal expectations.

### ERR-50-004 — Frozen portable verification assumed launcher source file
Frozen verification tests import/runtime contracts, not physical `.py` presence.

### ERR-50-005 — Admin media patch replaced mature list contract
Extend final mature ModelAdmin composition; preserve dependent list/edit/link invariants.

### ERR-50-006 — Unified Product Admin regression assumed stale `seo_status`
Correct fix: preserve mature Product list and assert current boundary-owned invariants. CI run `32941662288` PASS.

### ERR-50-007 — Production `git fetch --prune origin` left active branch remote-tracking ref stale
**Date:** 2026-08-26
**Environment:** `/home/sfkilvrs/3dprinthub`.
**Root Cause:** host `remote.origin.fetch` tracked only `+refs/tags/v0.33.0:refs/tags/v0.33.0`; normal fetch did not advance branch refs.
**Correct Fix:** verify `git ls-remote`, explicitly fetch active branch to `FETCH_HEAD`, verify exact SHA/ancestry, ff-only merge.
**Prevention:** never trust `origin/<branch>` on this host without checking refspec/upstream.

### ERR-50-008 — Legacy permanent Django filter column crushed modern Admin changelists
Keep native filter semantics but move node into an on-demand Velzon drawer; Product Admin CI `32955310832` PASS.

### ERR-50-009 — Velzon absolute footer and document-level active-menu scroll caused refresh flash/page jump
Correct fix: normal-flow footer, stable flex shell, 290px sidebar, internal sidebar/SimpleBar scrolling only. Admin CI `32958276378` PASS; deployed at `c283864290f9c989a9fcdf24ee8eef519560e917`.

### ERR-50-010 — cPanel Bash process substitution failed because `/dev/fd` was unavailable
Use Production Python or portable temp-file/pipeline enumeration; do not depend on `< <(...)` on this Host.

### ERR-50-011 — Variant API verifier executed JSON as Python source
Invoke `python - <json-path> ...` and parse data with `json.load`; JSON payloads are arguments/data, never executable source.

### ERR-50-012 — Profile Variant API treated `price_breakdown` callable as a dict
**Date:** 2026-08-27
**Environment:** Phase50 Profile Matrix CI.

**Symptom:** `/store/api/variant-commerce-options/` raised `AttributeError: 'function' object has no attribute 'get'` when the Profile Matrix test requested the selected Variant price.

**Root Cause:** `ProductVariant.price_breakdown` is the mature callable pricing contract. The new API serialization boundary read the method object with `getattr(...)` but did not execute it before using `.get("unit_price")`.

**Failed condition:** do not rerun the failing Profile Matrix CI unchanged; the failure is deterministic at the API boundary.

**Correct Fix:** resolve `price_contract = variant.price_breakdown`, execute it when callable, then serialize the returned pricing dict. This preserves the canonical Phase50 pricing policy wrapper and avoids duplicating price logic in the endpoint.

**Verification:** Profile Matrix/Checkout CI run `33051311828` PASS; profile fixed-price API regression returns the expected Variant price.

**Prevention:** API serializers must execute mature no-argument domain contracts before reading their returned mapping; do not treat bound methods as data.

### ERR-50-013 — Saved-address checkout was rejected by the new shipping policy wrapper
**Date:** 2026-08-27
**Environment:** Phase50 Checkout regression.

**Symptom:** checkout using a valid saved address returned HTTP 200 with form errors instead of the expected 302 success. Two immutable-checkout tests failed.

**Root Cause:** mature `CheckoutOperationsForm.clean()` intentionally returns early when `saved_address` is selected. The Phase50 commerce wrapper then validated `cleaned["address"]` / `postal_code` / location fields, which are empty in that mature saved-address flow.

**Correct Fix:** when `saved_address` exists, shipping scope/address/postal rules resolve province/county/city/address/postal code from that persisted address object; only new-address checkout uses raw cleaned form fields.

**Verification:** CI run `33051311828` PASS, including both immutable checkout tests and saved-address checkout redirect.

**Prevention:** wrappers around mature forms must honor the mature form's alternate data source/early-return semantics instead of assuming every field is populated in `cleaned_data`.

### ERR-50-014 — Downstream Profile state hid valid size/weight choices and could show another size's price
**Date:** 2026-08-27
**Environment:** Storefront dependent Profile selector.

**Risk/Symptom:** after a customer changed size, the currently selected downstream weight/build could constrain the option list for an upstream dimension. Price badges for a weight were also calculated from every Product Variant with that weight, so a 150 g price from size 20 could appear while viewing size 30.

**Root Cause:** option rendering used the complete current state for every dimension and calculated option-price pools globally by dimension value.

**Correct Fix:** each dimension now filters only by selections that occur **before** it in the configured Profile hierarchy. Clicking an upstream option clears downstream state before choosing a valid canonical Variant. Weight/Profile price badges are computed from the upstream-scoped candidate pool.

**Verification:** dedicated Node behavior gate `PHASE50_PROFILE_SELECTOR_HIERARCHY=PASS` plus full Store run `33051311828` PASS. The gate proves size 30 exposes all of its 150/200/300 g rows and uses the size-30 price for 150 g.

**Prevention:** dependent option matrices are prefix trees: later selections never determine the availability or price of earlier-level options.

### ERR-50-015 — Windows portable workflow did not watch mature Product studio publish-gate files
**Date:** 2026-08-27
**Environment:** GitHub Actions Windows portable release.

**Risk:** Profile Matrix publish-readiness fixes in `catalog_center/app/product_studio.py` and `catalog_center/app/epic49_product_studio.py` could pass targeted CI without automatically producing a fresh immutable Windows artifact.

**Root Cause:** `Catalog Center Windows Portable Release` path filters watched the newer 3I modules but omitted those two mature Product studio files even though the packaged application imports them.

**Correct Fix:** add both mature Product studio files to the Windows release workflow trigger.

**Verification:** Windows portable run `33051114515` PASS on `b3280dd67cd7772f337f6792036ea92d3f252747`; artifact ID `9637671099`; EXE SHA256 `32aed719e6d374447fc4b05f09a30fe12f0ce4dc05e570382f2e74036044900c`.

**Prevention:** immutable release workflows must watch every source boundary that materially changes the packaged runtime, including mature wrapped files.


### ERR-50-016 — `support_weight_grams` runtime metadata drifted from migration 0039
**Date:** 2026-08-27
**Environment:** GitHub Actions `Phase50 Variant2 + Profile Matrix CI`, failed run `33059803005`.

**Symptom:** `python manage.py makemigrations --check --dry-run` proposed an unapproved `0040_alter_productvariant_support_weight_grams.py`.

**Root Cause:** the mature `phase49_3f_pricing` runtime contributes `ProductVariant.support_weight_grams` before the newer Phase50 filament runtime sees the model. The field shape matched migration 0039 except its `verbose_name` was `وزن ساپورت (گرم)`, while migration 0039 declared `وزن ساپورت مصرفی`. Django therefore detected model-state metadata drift.

**Failed condition:** the failing migration gate was not rerun unchanged and no fake 0040 migration was accepted.

**Correct Fix:** align the mature runtime-contributed field metadata exactly with migration `0039_phase50_filament_offer_pricing`; keep one schema field and one migration authority.

**Verification:** commit `d519a360e65b79db4b62af206b95f63c3539bc12`; Phase50 run `33059883188` PASS, including no migration drift, migration through 0039 and 16 Store/Profile/Checkout tests.

**Prevention:** when a later formal migration owns a field that an older runtime layer may dynamically contribute first, field metadata (`type/max_digits/decimal_places/default/null/blank/verbose_name`) must remain identical. Always gate with `makemigrations --check --dry-run` before Production.

### ERR-49-056 — Catalog Center 8.9.1 Windows gate retained stale quick-price and package-version expectations
**Date:** 2026-08-27
**Environment:** GitHub Actions `Catalog Center Windows Portable Release`, failed run `33059799929`.

**Symptoms:**
- `test_phase49_3i33_operator_workflow` still required the removed `قیمت قطعی فروش (تومان)` quick-page authority,
- `test_v854_launcher` detected `config.example.json.package_version = 8.9.0` while Manifest/App/Launcher were already 8.9.1.

**Root Cause:** the 3I.35 redesign intentionally moved price/weight/Profile authority out of the quick page, but the older UI contract test still asserted the retired control. The release bump also updated App/Manifest/Launcher before the example config version.

**Failed condition:** the failing Windows command was not rerun unchanged.

**Correct Fix:** update the test to assert the new invariant — quick-page fixed-price authority is absent and price/weight/Profile live only in the order/pricing/options stage — and align `config.example.json.package_version` to 8.9.1.

**Verification:** exact runtime snapshot `2622818d898e19b745c61ff653b80c03d22288f1`; Windows run `33060047878` PASS through regression, launcher, source URL guard, one-file EXE, browser smoke, self verify and artifact SHA.

**Prevention:** a Catalog version bump is an atomic contract across `app/version.py`, `launch.py`, `PACKAGE_MANIFEST.json`, `config.example.json` and launcher tests. Contract tests must represent current business ownership, not require intentionally retired UI controls.


### ERR-49-057 — PowerShell multiline `python -c` DB probe stripped Python quotes in Local owner gate
**Date:** 2026-08-27
**Environment:** canonical Windows checkout `D:\projects\3DPrintHub`, owner Local QA wrapper at branch HEAD `35ab63105f30fdca42518d5273a424a3200977e3`.

**Symptom:** Local owner gate passed repository verification, live GitHub verification and Catalog SQLite backup, then failed before any new migration with:
`SyntaxError: unterminated string literal` while executing the embedded Python DB detector. The received Python text had lost quote characters around mapping keys/strings (for example `db.get(ENGINE)` instead of `db.get("ENGINE")`).

**Root Cause:** a PowerShell expandable multiline here-string was passed directly as a native `python -c` argument. Native argument quoting/serialization changed the embedded Python quoting. This is a wrapper/command transport defect, not a Django/database/schema failure.

**Failed condition:** do not repeat the same multiline `& $Py -c @"..."@` probe unchanged.

**Correct Fix:** feed a single-quoted PowerShell here-string to Python standard input (`... | & $Py -`) or use a simple one-line command whose quoting is unambiguous. Continue from the failed DB-verification boundary after re-verifying exact branch/head/clean worktree. Create a fresh backup of the effective Local Django SQLite file before applying any pending migration.

**Safety:** the failed owner run stopped before its migration stage, therefore that failed run did not apply `0039`. An earlier Local run at `ca9cc116...` had already applied `0034..0038` and passed 15 Store/Profile/Checkout tests.

**Prevention:** Windows operational runbooks must not pass nontrivial multiline Python source as an expandable native `-c` argument. Prefer stdin with a single-quoted here-string for read-only probes.


### ERR-49-058 — Local gate `CATALOG_CENTER_LAUNCHED=YES` did not prove visible owner UI launch
**Date:** 2026-08-27
**Environment:** Windows owner Local QA, Catalog Center 8.9.1.

**Symptom:** automated gate ended with `CATALOG_CENTER_LAUNCHED=YES`, but the owner did not see the new UI and could not perform visual acceptance.

**Root Cause:** `RUN_PHASE49_3I31_SMART_AI_GATE.ps1 -LaunchApp` uses PowerShell `Start-Process`, which starts Catalog Center as a detached process and immediately prints the launch marker. The marker proves the process-start command was issued; it does not prove the window was visible/focused or that owner visual QA occurred.

**Correct Fix:** for owner visual QA, launch the exact GitHub-synced source in the foreground with the canonical venv Python and `launch.py --debug`. Keep the terminal attached so startup/runtime errors remain visible. The 3I.35 UI is inside the Product workspace/order-pricing-options surface, not a replacement for the home screen.

**Prevention:** do not use `CATALOG_CENTER_LAUNCHED=YES` as evidence of visual acceptance. Automated launch verification and owner-visible UI QA are separate gates.


### ERR-49-059 — 3I.35 AI resilience panel mixed `grid` into the pack-managed Settings parent
**Date:** 2026-08-27
**Environment:** owner foreground Local launch of Catalog Center 8.9.1 on `D:\projects\3DPrintHub`.

**Symptom:** foreground `launch.py --debug` reached real application initialization and then aborted before any window became usable with:
`_tkinter.TclError: cannot use geometry manager grid inside ...!frame10 which already has slaves managed by pack`.

**Root Cause:** UX87 `settings_tab` is a pack-managed parent. Phase49.3I.35 created the new “پایداری AI گروهی — تنظیمات مادر” LabelFrame directly under `settings_tab` but called `panel.grid(...)`. This violated the existing `ERR-49-001` rule: one geometry manager per parent.

**Correct Fix:** keep the outer 3I.35 AI settings panel on the parent’s existing manager with `panel.pack(fill="x", padx=8, pady=8)`. Internal controls may continue using `grid` because they are children of the panel, not siblings in `settings_tab`.

**Regression:** `test_ai_resilience_settings_respects_pack_managed_settings_tab` asserts the outer panel uses `pack` and that the old direct `panel.grid(row=50,...)` contract does not return.

**Verification:** targeted Phase49.3I.31–35 run `33066472847` PASS; Single Active AI run on the final release head PASS; Windows one-file run `33066468014` PASS on runtime `9bd9d0b4cd070a35c82c6ecefd6f6b3027b20284`, including compile, Phase49 regression, launcher composition, source URL guard, one-file build/self-verify, manifest/SHA and artifact upload.

**Release:** Catalog Center `8.9.2` / build `2026.08.27.4`; artifact `9643957471`; EXE SHA256 `fac29fc610215cfc4115fcdb4c005fc69f99c3e6569b44c501d63ec82d6ba257`.

**Prevention:** any additive UI layer must inspect the final visible parent’s existing geometry manager before mounting widgets. A launch marker or `--verify-only` does not replace foreground owner startup QA.


### ERR-49-060 — Profile Matrix selection callback called an unbound short-name helper
**Date:** 2026-08-27
**Environment:** owner foreground Local QA of Catalog Center 8.9.2 after `ERR-49-059` startup geometry fix.

**Symptom:** Catalog Center 8.9.2 itself started successfully, but opening real Products 305 and 303 emitted repeated Tk callback failures and prevented the Profile/Order workspace from becoming usable:
`AttributeError: 'ProductWorkspace' object has no attribute '_profile_by_key'`.

**Evidence:** owner diagnostic generated at local 14:54:17 showed 8.9.2/build 2026.08.27.4 startup success, Product Workspace open events for 305 and 303, then four repeated callback failures at 14:53:54 and 14:54:00. The current-session hidden-model-scan warnings are expected safeguards, not this failure.

**Root Cause:** `phase49_3i34_profile_matrix.install_workspace()` defined local helper `_profile_by_key` but installed it on the wrapped class only as `_phase49_3i34_profile_by_key`. `_load_selected()` incorrectly called `self._profile_by_key(key)`, a name never installed on `ProductWorkspace`. Other Profile Matrix call sites already used the correct namespaced method.

**Correct Fix:** change the selected-profile lookup to `self._phase49_3i34_profile_by_key(key)`. No schema, Product data, Store migration or Host behavior changed.

**Regression:** `test_selected_profile_loader_uses_installed_namespaced_lookup` installs the real 3I.34 wrapper on a minimal class and executes the selected-profile loader without Tk; the old call raises and the corrected namespaced binding succeeds.

**Verification:** targeted Phase49.3I.31–35 run `33067612565` PASS; final-head Single Active AI run `33067618639` PASS; Windows one-file run `33067618679` PASS on runtime `9637829a255a1d09800bc062c2f049cf5d92b585`, including full Phase49 regression, launcher composition, source URL guard, one-file build/self-verify, manifest/SHA and artifact upload.

**Release:** Catalog Center `8.9.3` / build `2026.08.27.5`; artifact `9644438652`; EXE SHA256 `fd525fad977f592dc62e68fc3a4310bba98c7ed9689c5101cbdc35589fef7bed`; artifact ZIP digest `sha256:216b62072fd95a0a4d292b28ce99605fd60f3e4d9622d06987d6fe5b434e6141`.

**Rollback anchor:** `backup/pre-err49-060-profile-matrix-bind-fix-20260827` → `6f9334705c74a65d47473580944d79d61d501293`.

**Prevention:** nested UI helper methods must be called through the exact namespaced attribute actually installed on the final wrapped class. Static presence tests are insufficient for wrapped callback binding; execute callback contracts on a minimal installed class.

### ERR-49-061 — Commerce lock protected ledger JSON but missed legacy plural Profile transport
**Date:** 2026-08-27
**Environment:** Phase49.3I.36/3I.37 Catalog Center regression gate.

**Symptom:** the finalized-Commerce regression showed `sales_profile_ledger_json` stayed protected while the mature legacy transport `sales_profiles_json` could still be overwritten to `[]` after the Commerce stage was locked. This matched the owner-visible risk that a later AI/Save path could make previously registered Profiles disappear.

**Root Cause:** the stage ownership mapper recognized fields beginning with `sales_profile_`, but the older transport is plural `sales_profiles_json`; that key did not match the prefix and therefore escaped the Commerce write lock.

**Failed condition:** do not weaken the lock regression or treat only the newest ledger field as authoritative persistence protection. Both mature transports remain part of the current synchronization path.

**Correct Fix:** classify both `sales_profile_` and `sales_profiles_` prefixes as Commerce-owned. The final `Database.update_product()` guard now blocks both transports while Stage 2 is finalized.

**Regression:** `test_stage_field_ownership_keeps_profile_and_slider_separate` asserts both transports map to Commerce, and `test_finalized_commerce_protects_registered_profile_ledger` proves both remain unchanged under the lock.

**Verification:** Phase49.3I.31–37 run `33074245603` PASS with 77 tests; Single Active AI run `33074245489` PASS; Windows Portable run `33074245604` PASS on runtime `8d5e58a839c89eedbe258d9236889834fc02d9a9`.

**Prevention:** write-scope/lock mappings must cover every mature alias/transport that can persist the same business object, not only the newest authoritative field name.

### ERR-49-062 — Rejected/blocked Direct Link identity was checked only after acquisition
**Date:** 2026-08-27
**Environment:** Catalog Center Direct Link import.

**Symptom/Risk:** a Product that was already blocked/rejected could still enter `extract_direct_link()` and reopen browser/HTTP/image acquisition. The later DB upsert guard could prevent the Product record from becoming active, but local images/files might already have been downloaded again.

**Root Cause:** terminal Product identity was enforced at the persistence boundary, not at the network/binary acquisition boundary.

**Correct Fix:** resolve source code + external ID, query the permanent crawl/Product tombstone with `terminal_identity_state()`, and return before `extract_direct_link()` for terminal states. Successful Direct Link acquisition records `collected` in the mature discovery ledger.

**Regression:** 3I.38 static execution-order regression asserts the terminal identity check occurs before the Direct Link extractor; reject/purge integration proves a rejected identity remains terminal.

**Verification:** Phase49.3I.31–38 run `33077213590` PASS with 84 tests; Single Active AI `33077239617` PASS; Windows Portable `33077239660` PASS on runtime `c904193a7f0af9aad80365834ec3f0b856e77dc9`.

**Prevention:** any permanent skip/block/reject decision must be evaluated before browser, HTTP, image or file acquisition—not only before DB persistence.

### ERR-49-063 — Category/site crawl repeatedly exposed the same fixed first discovery window
**Date:** 2026-08-27
**Environment:** Catalog Center category/site crawl.

**Symptom/Risk:** `category/site_crawl` used one discovery pass with a fixed `scroll_rounds=8`. Although `discovered_urls` correctly rejected already-known Product identities, re-running the same Listing could repeatedly rediscover the first visible set instead of moving deeper to new Products.

**Root Cause:** deduplication was durable but Listing traversal depth was not. The mature discoverer had no persisted continuation state.

**Correct Fix:** keep `discover_classic()` unchanged and add a separate `crawl_listing_state` cursor. Same-Listing runs progress 8 → 16 → 24 … up to 96 scroll rounds. Every discovered identity still passes through the existing `add_discovered()` ledger, and four consecutive deeper no-growth attempts stop the current run.

**Regression:** the 3I.38 tests prove 100 previously collected IDs are skipped while 101–200 become the next 100 pending items, and prove the continuation cursor advances across runs.

**Verification:** Phase49.3I.31–38 run `33077213590` PASS; Windows Portable `33077239660` PASS.

**Prevention:** keep Product identity dedupe and Listing traversal progress as separate durable concerns; never replace a healthy parser/downloader just to continue past previously seen results.


### ERR-49-064 — 3I.35 legacy material actions aborted ProductWorkspace before 3I.39/3I.40 UI
**Date:** 2026-08-29
**Environment:** owner foreground Local QA, Catalog Center 8.9.8 / build 2026.08.29.2, canonical checkout `D:\\projects\\3DPrintHub`.

**Symptom:** the owner opened a real Product Workspace and still saw the older Stage-2/SEO surface even though launcher verification printed every 3I.39/3I.40 feature marker. Foreground diagnostics then raised:
`TclError: cannot use geometry manager pack inside ...!labelframe which already has slaves managed by grid`.

**Root Cause:** `phase49_material_color_picker` had already replaced the mature material/color Listbox surface with a grid-managed checkbox picker. During the later 3I.35 wrapper, `build_material_actions()` still treated the obsolete `material_color_list` parent as an active pack-managed host and tried to mount another Frame with `pack`. ProductWorkspace construction stopped inside the 3I.35 constructor, so the already-created older widgets remained visible while 3I.39 Professional Commerce and 3I.40 Commerce Precision never reached their UI-build steps.

**Failed condition:** do not interpret launcher feature markers or the 8.9.8 title as proof that the final wrapped ProductWorkspace constructor completed. A callback exception after partial construction can leave an older surface visible.

**Correct Fix:** when the modern checkbox picker is installed (`_epic49_materials_box` exists), 3I.35 now skips mounting the obsolete Listbox action row entirely. The 3I.35 business methods/data remain intact, and 3I.39 remains the final visible Stage-2 authority.

**Regression:** `test_operator_ledger_skips_obsolete_listbox_actions_when_modern_picker_is_installed` installs the real 3I.35 wrapper on a minimal workspace and proves no `ttk.Frame` is created for the obsolete action row when the modern picker marker exists.

**Git hotfix:** source fix `aa37dcf916dfab71409738f7087a171daffe4a0a`; regression `9a3ebd43b22a50ac1447b90cae159dcffb1ed451`.

**Rollback anchor:** `backup/pre-err49-064-stage2-geometry-20260829` → `c62df9dd1bbfee4cfa915beed6f9523efaa4937f`.

**Verification status:** GitHub source/regression update complete. Owner Local ff-only pull + targeted tests + foreground ProductWorkspace retest are still required before this incident is marked fully verified. Production untouched.

**Prevention:** every additive wrapper must inspect whether the surface it is extending is still the active visible generation. Never mount legacy controls into a parent that a newer layer has already replaced; and do not use feature-marker prints as a substitute for successful final constructor completion.


### ERR-49-065 — AI filled SEO fields but stale readiness/UI still showed them as missing
**Date:** 2026-08-29
**Environment:** owner foreground Local QA after ERR-49-064, Catalog Center 8.9.8 / Phase49.3I.40.

**Symptom:** the seven-stage AI completed and persisted Persian/SEO fields, but the Product Workspace still showed red/missing SEO items and stale stage icons. The owner correctly observed that the Product appeared to need a post-AI refresh before publish readiness reflected the saved fields.

**Root Cause:** the 3I.39 completion worker queued a generic `reload()` and one lock refresh after the AI loop. Multiple mature wrappers keep cached readiness/help state; the older guided-wizard painter could repaint its cached `ready/missing` state after the final 3I.40 data-readiness renderer. Persisted SQLite values were therefore newer than some visible readiness widgets.

**Correct Fix:** add one explicit post-AI reconciliation boundary that rehydrates the Product row from SQLite, reloads the workspace, refreshes stage locks and the guided wizard, and deliberately leaves the final `_phase49_refresh_readiness` call as the last painter. Run the same reconciliation again after a short UI-settle delay. Apply this to both whole-product and single-stage repair completion paths.

**Scope:** no Provider/model/source semantics, no AI field ownership, no Commerce/Profile/Offer mutation, no auto-finalization, no migration/schema, no Host or Production change.

**Git hotfix:** source `b9eb9d74b0c0c0be49ca8d04a4333750e68e93f4`; regression `375961a1621c43f168b7c3fd76523c6d3c9c9a26`.

**Regression:** `test_post_ai_refresh_rehydrates_db_and_leaves_final_readiness_as_last_painter` verifies DB rehydration and that final readiness is the last UI painter after reload/lock/wizard refresh.

**Rollback anchor:** `backup/pre-err49-065-seo-post-ai-refresh-20260829` → `3edda5ffe98d8c37dd66e3e7fc0d6eab3ec6c554`.

**Verification status:** Owner Local pulled `c679c66d8c6554ff14e5705b7eb3aada24495990`; the 3I.39/3I.40 targeted set passed 12/12 and foreground 8.9.8 launched correctly. The visible bug nevertheless persisted. The repaint fix is retained, but it was insufficient because a deeper checker/stage-ownership mismatch remained; see ERR-49-066. Production untouched.

**Prevention:** after background AI writes, do not assume one generic reload synchronizes every wrapped readiness surface. Rehydrate from persisted state and define one final painter for the visible readiness contract; then verify the checker and fixer use the same stage/field semantics.


### ERR-49-066 — Readiness checker, stage ownership and AI repair disagreed
**Date:** 2026-08-29
**Environment:** owner foreground Local QA on `c679c66d8c6554ff14e5705b7eb3aada24495990`, Catalog Center 8.9.8 / Phase49.3I.40.

**Owner evidence:** Local fast-forward and 12 targeted tests passed, then the real Product 63 run proved the remaining defect. The first visible full-AI action still executed the older 3I.31 path and persisted title/content/SEO/image fields. The later 3I.39 readiness loop reported `7` data defects / `5` AI-fixable defects, scoped only Stage 4, accepted a fallback AvalAI response, then reported `0` defects fixed and stalled with the same `5` AI-fixable defects.

**Root Causes:**
1. `title_fa` was checked in both Quick and Content even though final field ownership assigns it to Quick.
2. image Alt was checked in Content even though final field ownership assigns it to Images.
3. the persisted Persian readiness checker rejected every Latin character, while the title/description AI path legitimately permits the true source identity (for example `Flexi Gecko`) beside Persian text.
4. non-empty but invalid keyword/tag/hashtag lists were reported by readiness but `_field_needs_fill()` treated them as complete because it only used blank-value repair logic.
5. the guided wizard painted/navigation-gated on `ready` (operator-finalized) instead of `data_ready` (actual data completeness), so Stage 1 could remain X/★ even with all required values present.
6. some visible mature AI buttons still resolved to the older 3I.31/3E execution path rather than the final 3I.39 checker/repair authority.

**Correct Fix:**
- one authoritative readiness owner per field: title → Quick, Alt → Images, SEO/content fields → Content;
- persisted title/description may contain only Latin tokens that are actual tokens of `source_title`; SEO title/description and SEO keyword/tag/hashtag lists remain Persian-only;
- `_field_needs_fill()` now uses the same semantic checks as readiness, including non-empty invalid lists;
- guided-wizard red stars, Next gating and stage icons use `data_ready/missing_data` when available; operator `ثبت` remains a separate finalization lock;
- final 3I.39 installation rebinds mature full-AI/link/current-stage entry points to the same seven-stage repair engine.

**Touched surfaces:** `phase49_readiness_wizard.py`, `phase49_3c_persian_content.py`, `phase49_3b_guided_wizard.py`, `phase49_3i37_seven_stage_ai.py`, `phase49_3i39_completion_loop.py`, plus focused regressions.

**Must not touch:** Product Offer/Profile/pricing ownership, crawler/parser/download, source URL guard, Provider secrets/configuration, image binaries, Django schema/migrations, Host and Production.

**Git changes:**
- checker/source-identity alignment `3b4ad0c8741f794ee5c338e5ddba8971bf9c3487`,
- single field/stage ownership `2fff3f7edfecb2d6a0acc6c3d52c14817b177e82`,
- Persian defect ownership `046191ac562ecce878dfab263f4f6255d5f12bcf`,
- data-ready guided wizard `11dfefdbb02a6281c1b6a6721cbf254785e2e216`,
- checker/fixer agreement `39fcd2f9e335a57d76079f6f18ebaad3ac406f97`,
- final AI entrypoint authority `b9ef5f1f6d887520c1613f09cbcf947fc1058e12`,
- regressions `5a14318e52244fd0b9de8de15daafe03e204c5fb`, `b5f1a9d50435c04fc382e4783355f23e64987823`, `7c047c834163235455e24a58eb43c134b4ccecc0`, `8bb6e1f7b30039f709b627d3a5aaa7691ec004c3`, `7874dd2d63a8a8e51bd5d9f72668332e9d7c7861`.

**Rollback anchor:** `backup/pre-err49-066-readiness-checker-alignment-20260829` → `c679c66d8c6554ff14e5705b7eb3aada24495990`.

**Verification status:** GitHub source/regressions updated. No GitHub Actions run is attached yet to the current code head; owner Local targeted regression + foreground Product 63 retest is required before acceptance. Production untouched.

**Prevention:** a readiness defect must map to exactly one owning Stage and to at least one executable repair path when labeled AI-fixable. UI completion indicators must distinguish persisted data completeness from operator finalization.


### ERR-49-067 — Locked-stage regression fixture violated the new Persian SEO contract
**Date:** 2026-08-29
**Environment:** owner Local ERR-49-066 focused gate on `9f3b765e28f9b9adda1e7713dbc48c1255a52c1c`.

**Symptom:** compile passed, then the 43-test focused suite stopped with exactly one error in `test_locked_quick_and_content_are_not_rewritten_by_orchestrator`. The exception occurred before the lock assertion path:
`RuntimeError: خروجی AI برای seo_description_fa باید SEO فارسی باشد و متن لاتین نداشته باشد.`

**Root Cause:** ERR-49-066 intentionally strengthened the production SEO contract so `seo_title_fa` and `seo_description_fa` cannot contain Latin text. The older regression fixture still mocked its generated SEO description as `توضیح فارسی AI درباره ...`. The literal Latin token `AI` made the mock payload invalid, so validation correctly rejected it before the test could reach the behavior it was actually intended to verify: locked Quick/Content stages are not rewritten.

**Correct Fix:** keep the stricter runtime contract unchanged and repair only the stale test fixture. Replace the mock Latin `AI` wording with fully Persian generated-content placeholders. This preserves the purpose of the regression and avoids weakening real SEO validation merely to satisfy a stale fixture.

**Git:** test-fixture correction `38cb415bc12d7ec08943809fd14f3478b3ddac1b`.

**Rollback anchor:** `backup/pre-err49-067-seven-stage-test-fixture-20260829` → `9f3b765e28f9b9adda1e7713dbc48c1255a52c1c`.

**Verification status:** owner Local evidence before the correction: repository/branch/head verified, Catalog SQLite backup created with SHA256 `AE475E39040B8BF8F7BEF7B13D3176F2B83BBA956E2121D53CC2F5CC087F185F`, compile PASS, 43 focused tests ran with 1 deterministic fixture error, foreground launch correctly did not run. Owner must ff-only pull the corrected head and rerun the same focused gate; do not rerun the failed head unchanged. Production untouched.

**Superseded detail:** the fixture-only correction itself remains valid, but the interim assumption that SEO title/description must reject every Latin token was too strict for real product identity. Owner runtime evidence immediately after this gate showed legitimate source identity such as `Flexi Gecko` being rejected. ERR-49-068 replaces that rule with: Persian SEO may preserve exact Latin tokens from `source_title`; unrelated Latin remains invalid.

**Prevention:** regression fixtures that feed production validators must themselves satisfy the current production contract unless the test explicitly verifies rejection. A lock/immutability test must use a valid AI payload so validation does not mask the behavior under test.


### ERR-49-068 — Windows stage confirmation deadlock + stale Tk callbacks + AI fallback identity mismatch
**Date:** 2026-08-29
**Environment:** owner foreground Windows QA on exact Local head `0191a07f980d3cf5ba48ed1379a1c9da98c39e1b`, Catalog Center 8.9.8 / build 2026.08.29.2 / Product 63.

**Owner evidence:** the corrected ERR-49-067 gate passed the previously failing test and then all 43 focused tests. The canonical source launched successfully. In the real Product Workspace, Stage 1 fields could be visibly complete or manually edited but the Stage stayed unconfirmed/red, the expected bottom confirmation control was not available in the visible workflow, and the operator could not naturally advance. The same runtime trace also showed:
- initial readiness `6` data defects / `4` AI-fixable,
- OpenRouter returned no output text on repeated attempts,
- AvalAI returned structured output but legitimate source identity in SEO was rejected, then one request timed out,
- an OpenRouter-shaped key/model was later attempted under the OpenAI fallback and received HTTP 401,
- the failure UI then raised `cannot access free variable 'exc' where it is not associated with a value in enclosing scope`,
- a later explicit Product save persisted many fields successfully, proving the database write path itself was alive.

**Historical comparison:** the original 3B guided wizard commit `eb865e78c70b862f51e6918dee074c8bb9c0536f` had a persistent footer Next action and visible AI helper. 3I.36 commit `8d6e9ca1bee40da3ffbd57ec328ef77de451c781` introduced separate stage finalization/locking and moved `ثبت` into a seven-row rail panel. The mature 3B Next path still evaluated readiness before its later `save(silent=True)`; once readiness depended on persisted stage data/finalization, manual widget edits could never pass the pre-save gate. In current layout the rail finalization panel was not a reliable visible operator control, producing a practical deadlock.

**Root Causes:**
1. Manual stage progression evaluated persisted readiness before persisting current UI values.
2. Stage finalization existed only in the separate 3I.36 rail panel; the fixed footer no longer provided the old obvious confirm/advance workflow.
3. Older Tk Buttons captured bound callback objects when they were created. Later 3I.39 class alias reassignment did not change those already-created widget commands; the rebind scan covered only Content, not the whole Workspace.
4. SEO validation rejected every Latin token instead of allowing the exact real source identity tokens already present in `source_title`.
5. fallback candidate construction could reuse a key/model belonging to another Provider. The observed OpenAI attempt used an OpenRouter-shaped key and an OpenRouter/Nvidia model.
6. a deferred lambda closed over `exc` from an `except` block; Python clears that exception binding after the block, causing the secondary UI error.

**Correct Fix:**
- restore a persistent visible footer action `✅ تأیید و مرحله بعد →` that calls the 3I.36 stage-specific persist/finalize method first and advances only after success;
- add adjacent visible `✨ پرکردن ناقص‌ها با AI` and `✏ اصلاح مرحله` actions;
- wrap the mature Wizard refresh so later refreshes cannot silently replace the fixed confirm command/text with the old read-before-save Next behavior;
- rebind actual already-created legacy AI buttons across the whole Workspace to the final 3I.39 engine rather than relying only on class aliases;
- allow exact Latin tokens from `source_title` in Persian title/description/SEO fields while continuing to reject unrelated Latin; keyword/tag/hashtag lists remain Persian editorial text;
- skip positively identifiable cross-provider keys and require fallback models to be saved for that exact Provider rather than inheriting the primary model;
- freeze the redacted exception text before scheduling the deferred footer callback.

**Git changes:**
- source-aware SEO readiness `7e4fbd198af0252bb83f613a984e1bf675237158`,
- source-aware AI SEO validator/repair `e0e08c668acbed3cbb084b82728994ee3e22299d`,
- visible footer confirm/AI/edit + deferred exception fix `6ece94c2c8a9431517ee08c0ffd131863e844d0c`,
- actual legacy Tk button rebind `d0514357907a96c96edc4151cc845dd08f2a1bfc`,
- footer authority retained after Wizard refresh `d461ab981b7ce490fb24c68ac8ea92c39a8046fa`,
- cross-provider key guard `0856868ea057b2cc9f0081ceeef723df4fd95702`,
- provider-specific fallback model guard `c1746545f0fb8c591f01591c91487d9c721bbcc6`,
- regressions `8d31f0dd011028c407eb609e3a58b5e03e6430ce`, `21913aa409757e1b3a9b41136d434fc498801dc0`, `ef6b2f033cd4d0aac359df0497bd8e593ed9d2bc`, `3822d407438b21a1bccd9484805fe937bf789b51`, `e184e629d3ac55a62c1f501d1ab684bc8c212701`, `dbe10616c691292e4e74358a08a9de2d43fdf333`, `4d6426f8f2a4ea01643bb763cf00a2dae3947e3f`.

**Rollback anchor:** `backup/pre-err49-068-windows-stage-confirm-20260829` → `0191a07f980d3cf5ba48ed1379a1c9da98c39e1b`.

**Touched surfaces:** Windows Catalog Center stage footer/navigation, 3I.39 AI button routing, Persian/source-identity readiness and repair validation, fallback candidate safety, focused tests and documentation.

**Must not touch:** Stage-2 Offer/Profile/pricing ownership, crawler/parser/download identity, Product media binaries, Django schema/migrations, Production Host, secure key values themselves.

**Verification status:** GitHub hotfix/regressions are committed. The last owner Local runtime at `0191a07...` passed 43 focused tests but predates this ERR-49-068 delta. Current hotfix requires a new Local pull, compile/regression gate and foreground Product 63 QA. Production untouched.

**Prevention:** a visible Windows workflow must have an executable persist → validate → confirm → advance path in the same viewport; do not make progress depend on an off-screen/secondary control. Tk widget commands created before later wrappers must be explicitly rebound at the final visible composition boundary. Provider fallbacks must keep key and model identities provider-specific.


### ERR-49-069 — late Wizard repaint, incomplete stage ownership UI and AvalAI fallback after 60/60 Local PASS
**Date:** 2026-08-29
**Environment:** owner foreground Windows QA on exact Local head `3f43260db669b458a682f594b5d50eb5221b9ef3`, Catalog Center 8.9.8 / build 2026.08.29.2.

**Owner evidence:** the ERR-49-068 Local gate verified the canonical checkout, created backup `D:\projects\3dprinthub-backups\err49-068-20260829-174512\catalog-before-err49-068-qa.sqlite3` with SHA256 `5A6DB948ADACA81014DEDFA7FF117A0C4AF26364936575ACB15D21D632D4C321`, passed compile and 60/60 focused tests, then launched the exact 8.9.8 source. Real Product 63/295 QA still showed:
- the visible footer reverted to the old `مرحله بعد برای انتشار →` action after final composition,
- Stage 1 could be data-complete yet stay practically unconfirmed/not advance,
- Stage-1-owned Product type/dimensions/use-case controls were not all visible in Stage 1,
- Stage-5-owned source/license/technical controls were split across older Stage 2/7 surfaces,
- Stage-specific AI reported global defects from unrelated Stages, so a completed Stage 1 run could still claim 4 AI-fixable defects remained,
- Product 63 and Product 295 AI jobs overlapped,
- despite OpenRouter being the saved active Provider, resilient fallback still invoked AvalAI,
- OpenRouter primary model was intermittently 404/403/no-text but also produced valid 3–5k-token responses, so the correct policy is same-Provider fallback rather than changing Provider automatically.

**Root Causes:**
1. `phase49_3i26_operator_completion` scheduled an `after_idle` callback that captured the older `_phase49_3b_refresh_wizard` before 3I.39 finished installing. That late callback could repaint the footer after 3I.39 had configured it.
2. The old 3B Next handler still had a read-before-save fallback path. Rebinding the visible Button alone was therefore insufficient.
3. Canonical field ownership and visible stage composition had drifted: Quick owns `product_type/dimensions/use_case_class`, but those controls lived in the older Commerce form; Specs owns source/license/technical fields, but some controls remained elsewhere.
4. `persist_stage_from_ui()` did not persist every field declared/visible for Quick and Specs.
5. `repair_until_stable()` used global `ai_fixable_count` for stage-scoped completion, causing false retry/stall/incomplete reporting from defects outside the requested Stage.
6. AI busy state was per Workspace, allowing concurrent Product AI jobs in the same process.
7. 3I.35 resilience still treated AvalAI/Google/OpenAI as Product-AI fallback candidates even when the owner explicitly selected OpenRouter.

**Correct Fix:**
- make the base guided refresh itself call the final 3I.39 footer-sync hook, so even already-captured old callbacks finish by restoring `✅ تأیید و مرحله بعد →`;
- make legacy `_phase49_3b_go_next` delegate to final stage confirmation and, for any legacy-only fallback, persist before readiness evaluation;
- route the old title-only button through final Stage-1 AI when 3I.39 exists and freeze legacy exception text before deferred Tk callbacks;
- restore an additive Stage-1 identity panel with Product type, dimensions and use-case/class; persist all Quick-owned fields both in stage-specific finalization and normal Workspace Save;
- restore an additive Stage-5 panel for source/designer, commercial license, Persian technical summary and technical-features JSON; persist those fields before finalization and keep compatibility editors synchronized;
- make repair counts, terminal messages and 3I.40 progress scope-aware for single-stage AI while retaining global truth for whole-product AI;
- add one process/app-level Product-AI runtime guard so another Product Workspace cannot start a second Product AI job until the first finishes/cancels;
- make Product AI **OpenRouter-only**: exact saved OpenRouter model is Primary; optional fallback is only `openrouter/free` with the same OpenRouter key. AvalAI/Google/OpenAI are not Product-AI fallbacks. No model is guessed or silently changed.

**Git changes:** source changes begin at `3ea7033bfe46d892d72d96eb47cbe3e7c02b63d8` and currently extend through `136011971dea907ac777b3e66190dd27982a0c38`; focused regression updates are included in the same branch history.

**Rollback anchor:** `backup/pre-err49-069-stage-contract-openrouter-only-20260829` → `3f43260db669b458a682f594b5d50eb5221b9ef3`.

**Touched surfaces:** Windows Catalog stage footer/navigation, Stage 1 and Stage 5 operator controls/persistence, stage-scoped AI completion accounting, Product-AI concurrency guard, Product-AI Provider resilience, focused tests/documentation.

**Must not touch:** Stage-2 Offer/Profile pricing authority, crawler/parser/acquisition identity, Product media binaries, secure key values, Django schema/migrations, Host or Production.

**Verification status:** owner Local evidence on the rollback head is 60/60 PASS and foreground failure reproduced. ERR-49-069 source/tests are committed on GitHub but **have not yet been pulled/tested on the owner Windows checkout**. Production remains untouched.

**Prevention:** final visible composition must be tested against deferred callbacks, not only class method aliases. Every Stage must have a single ownership table that matches visible controls, stage-specific persistence and readiness. Stage-scoped AI must judge only its Scope. Product-AI Provider policy is explicit and must not silently cross providers.



### ERR-49-070 — clean Stage-5 schema/panel gap exposed by owner Local gate
**Date:** 2026-08-29

Owner Local on `382a34fa6e876dc7098c8152c98c7cb076d508e8` passed compile and the 4 OpenRouter-only tests, then the 67-test Windows contract stopped before launch with:
- `sqlite3.OperationalError: no such column: technical_summary_fa` on a clean temporary Catalog DB;
- missing Stage-5 visible contract text. Source review confirmed `add_specs_contract_panel` and `refresh_specs_contract` were referenced/assigned but not implemented.

Root cause:
1. `technical_summary_fa` became Stage-5 authority without being added to the canonical clean Catalog schema.
2. ERR-49-069 wired Stage-5 builder names without their function bodies.
3. Stage-specific finalization needed to translate the visible Persian license label to the stored license code.

Fix:
- add `technical_summary_fa` to Catalog self-schema;
- implement `منبع و مجوز کامل` in `specs_tab` with source/designer, Persian license selector, technical summary, and technical-features JSON;
- hydrate those controls from SQLite;
- persist the Persian license selector through `LICENSE_LABEL_TO_CODE`;
- extend regressions for clean schema and builder presence.

Git: `0da7ffead4401a6080226de1dbfc229176973af9`, `b84c33605fd22b32a3602707b84367f1ad431b04`, `db5948c23f8a7b55898e9aa42f4b4b6e587caf67`, `d0ddbc61820bca2b0222f1773de7cafd0c26cafa`, `1b2ed24dd67729855dda3714700f570f28c5619f`.

Rollback: `backup/pre-err49-070-stage5-schema-panel-20260829` -> `382a34fa6e876dc7098c8152c98c7cb076d508e8`.

Verification: GitHub updated; owner Local rerun pending. Production untouched.

Prevention: a new Stage-owned field must land together in clean schema, upgrade path, visible control, stage persistence and regression coverage.


### ERR-49-071 — 67/67 PASS but Stage confirmation UX still broken and false missing count exploded
**Executable checkpoint:** `6085ea70d1075c5a1abaca4b4b2efdebe1254829`. Stage-2 confirmation persists visible Product type/dimensions before locking. No current-head Actions run is attached; owner Local verification remains pending.

**Date:** 2026-08-29
**Environment:** owner foreground Windows QA on exact Local head `d4da99744659d06ebe5c04fd69532cd0e03db3e8`, Catalog Center 8.9.8 / build 2026.08.29.2.

**Owner evidence:** repository/branch/head verification PASS; fresh Catalog backup `D:\projects\3dprinthub-backups\err49-070-20260829-185545\catalog-before-err49-070-qa.sqlite3` with SHA256 `C1538C91C9F9E2173E7CA4E28B3F60DFCC1E38449A276F96845BC065CE689033`; compile PASS; exact two ERR-49-070 regressions PASS; OpenRouter-only 4/4 PASS; full Windows stage contract 67/67 PASS; foreground launch PASS. Visual QA nevertheless failed.

Observed UI/runtime:
- Stage 1 title and category were visibly filled but the rail still showed a red X and did not provide the simple explicit confirmation path the operator expects.
- ERR-49-069 had inserted `نوع محصول / ابعاد / کاربری` into Stage 1 even though those controls historically belong to the commerce/order surface; the owner explicitly rejected this relocation.
- explicit category `سایر محصولات` maps to `external-other`, but readiness treated that exact selected category as missing.
- every unlocked Stage appended `تأیید نهایی اپراتور (ثبت مرحله)` into its generic missing list; older/base readiness UI then counted pending confirmations as product-data defects, inflating the visible missing count to dozens.
- the visual rail used data completeness as a green check in some layers while the requested contract is: complete data may be pending, but the green check appears only after explicit `ثبت و تأیید`.
- the visible legacy Next button continued to be repainted by older layers, so rebinding that same widget remained fragile.
- while Product 63 Product-AI was still running, the visible title-only action on Product 286 started a second direct OpenRouter request. The title-only Tk callback had been created before the final runtime guard and was not included in the actual-widget rebind sweep.

**Root Cause:**
1. ERR-49-066 changed guided progress from confirmed `ready` to raw `data_ready`, which made visual completion semantics diverge from the operator's explicit approval workflow.
2. ERR-49-069 incorrectly moved Product type/dimensions/use-case into Stage 1 instead of preserving the historical visible stage layout.
3. 3I.36 and 3I.39 mixed operator-finalization markers into `state["missing"]`, so a confirmation workflow was reported as missing Product data.
4. Stage-1 category validation treated `external-other` as a placeholder even when `سایر محصولات` was a deliberate operator selection.
5. The final footer tried to mutate the legacy Next widget instead of owning an independent confirmation widget, allowing late callbacks to repaint it.
6. The title-only button retained a direct legacy callback and bypassed the app-level Product-AI runtime guard.

**Correct Fix — targeted rollback of the bad UX, not a broad source rollback:**
- restore Stage 1 to the historical visible responsibility: Persian title + site category; remove mounting of the added type/dimensions/use-case panel;
- keep Product type/dimensions/use-case in the existing Stage-2 commerce surface;
- stop mounting the added Stage-5 panel from ERR-49-070; retain the historical source/license surface and keep the additive DB column harmless;
- treat any explicit non-empty category, including `external-other / سایر محصولات`, as a valid Stage-1 category;
- separate real `missing_data` from `pending_finalization`; pending confirmation must never inflate the missing-data count;
- green `✅` means the Stage is data-complete **and explicitly confirmed**; data-complete but unconfirmed is `◌`;
- hide the repaint-prone legacy Next widget and create an independent permanent bottom action `✅ ثبت و تأیید مرحله →`; clicking it persists the current Stage, validates, writes the Stage lock, refreshes the rail, then advances;
- keep `✨ پرکردن ناقص‌ها با AI` and `✏ اصلاح مرحله` adjacent to the new confirmation action;
- rebind the actual visible `ترجمه فقط عنوان فارسی` Tk button to the same final Stage-1 AI runner so the app-level one-Product-AI-at-a-time guard and OpenRouter-only policy apply.

**Git source/test sequence:** starts at `a6f4d9d34d9a3963f34da7fe62fd206f0cd3364c` and currently extends through `950824d4104a7c0585ce417e9e57a498d5e2f4cf` before documentation commits.

**Rollback anchor:** `backup/pre-err49-071-stage-confirm-rollback-20260829` → `d4da99744659d06ebe5c04fd69532cd0e03db3e8`.

**Touched surfaces:** Windows guided Stage rail, Stage-1 readiness/category rule, stage ownership map/persistence, bottom confirmation controls, base/final readiness summaries, actual-widget AI callback rebinding, focused regressions and documentation.

**Must not touch:** Stage-2 Offer/Profile/pricing implementation itself, OpenRouter-only Provider policy, crawler/parser/acquisition, Product media binaries, secure key values, Django schema/migrations, Host or Production.

**Verification status:** owner proved the pre-fix head had 67/67 automated PASS but failed visual acceptance. ERR-49-071 code/regressions are on GitHub; new Local pull/test/foreground acceptance is mandatory. Production untouched.

**Prevention:** a visual acceptance gate must test the exact operator meaning of icons/actions, not just data persistence. A green Stage check is an explicit business-state transition and must not be inferred from field population. Pending approval and missing data are separate domains. Final-composition controls that must survive old callbacks should own independent widgets rather than repeatedly mutating legacy widgets.


### ERR-49-072 — new Stage-2 regression fixture used an incomplete clean Catalog schema
**Date:** 2026-08-29
**Environment:** owner Local Windows, exact branch/head `34c65bc9e39d851b4fd3f7e0d2d4ec9627aed5b9`, ERR-49-071 gate.

**Owner evidence:** canonical repo/branch/head PASS; fresh real Catalog SQLite backup created at `D:\projects\3dprinthub-backups\err49-071-20260829-193034\catalog-before-err49-071-qa.sqlite3` with SHA256 `0FA06AF7884F005A8820A420DBDC6C42B883E836A554F9C315E1D559854362F0`; changed-source compile PASS. The exact 7-test ERR-49-071 set stopped on one deterministic error before OpenRouter/full-suite/foreground launch:
`sqlite3.OperationalError: no such column: price_min`
inside `test_commerce_stage_persists_visible_product_type_and_dimensions`.

**Root Cause:** the new test reused the minimal `Database` bootstrap plus Profile/Ledger schema only. That fixture did not initialize the two real ProductWorkspace commerce schema layers:
- `epic49_desktop_schema.ensure_epic49_desktop_schema()` owns `price_min / price_max`;
- `phase49_3f_workspace.ensure_schema()` owns `pricing_strategy`.
The real ProductWorkspace initializes those schemas before Stage-2 editing, so this was a regression-fixture composition error, not evidence that the owner's existing Catalog database lost commerce columns.

**Failed condition:** do not rerun the same ERR-49-071 command on `34c65bc...`; its fixture is known incomplete.

**Correct Fix:** make the Stage-finalization test helper initialize the same Epic49 desktop + 3F pricing schemas as real ProductWorkspace construction before Profile/Ledger schemas. No runtime application source, Product data, Django schema/migration, Host or Production behavior is changed.

**Source/test fix:** `1307f4c438de184a930041d365976c2ce018bff8`.

**Rollback:** `backup/pre-err49-072-commerce-test-schema-20260829` → `34c65bc9e39d851b4fd3f7e0d2d4ec9627aed5b9`.

**Verification status:** GitHub updated; no current-head GitHub Actions run is attached. Owner must ff-only pull the new docs-final head, rerun the changed exact regression gate, then OpenRouter/full Windows suite, and foreground launch only if all pass. Production untouched.

**Prevention:** any clean temporary Catalog DB test that exercises a mature Workspace layer must initialize the same schema composition that the runtime initializes; do not assume the minimal `Database._init()` contains every additive Epic49/3F column.


### ERR-49-073 — image Stage confirms, then downstream Content/Source makes Metadata look stale while lock blocks refresh
**Date:** 2026-08-29
**Environment:** owner Windows foreground QA on exact `6d5897ecefc427c940c690daabc311f85cc6e044`, Catalog Center 8.9.8 / build 2026.08.29.2.

**Owner verification before defect:** exact ERR-49-071/072 regressions 7/7 PASS, OpenRouter-only 4/4 PASS, full Windows stage suite 71/71 PASS, foreground launch PASS. Stage 1/Content/Source/Slider confirmation worked. Owner intentionally left Stage-2 price/profile incomplete.

**Observed image defect:** Stage 3 could be finalized, but after later Content/SEO and Source/License stages changed, the image task surface reported `Metadata تصویر 1/2 • بروزرسانی Metadata`. The runtime repeatedly logged `stage_locked_write_blocked` around successful `images seo_finalize` events. Manual Metadata editor could also attempt a save against the already-confirmed image Stage.

**Root Cause:** image SEO signature intentionally includes later Product SEO/source facts. After those later stages change, deterministic image files are regenerated with the new facts, but `finalize_selected_images()` persisted its derived `image_metadata_json / image_alt_texts_json / selected_images_json / primary_image_url` through the normal guarded Product update. Because Images was already locked, the lock guard discarded those derived DB updates. Files were rebuilt, but the persisted signature stayed old, so the UI continuously reported stale Metadata. This is not a missing image-selection problem and not an AI-provider problem.

**Correct Fix:**
- add a strict derived-image persistence boundary that may use the existing raw DB updater only for the four finalizer-owned image fields;
- keep Stage lock protection for arbitrary operator/AI edits;
- when first confirming Images, run deterministic image finalization before readiness/lock;
- when Images is already confirmed and the owner presses `ثبت و تأیید مرحله` again, rebuild current SEO/Metadata under the derived-state exception and keep the Stage confirmed;
- in the final manual Metadata editor, block manual override saves while Images is locked and instruct the operator to use `اصلاح مرحله` for real edits; for stale derived Metadata, use Confirm or `نهایی‌سازی فایل‌های SEO`.

**Git changes:** derived refresh `b3eab828db5b09d1ac3a94fad4abdaa511e3c208`; image-confirm refresh `a1776471c773be3cdb221070d9b8f543d6701986`; locked editor guard `a97cf94772bb4422e5aa68fa2bed171f5a830ccf`; locked-image refresh regression `10b4dcd65407754deacc9bed45276623971f4dd9`; image-confirm finalization regression `b807cf837af6b6f46ca16149fec1acc031f4f890`.

**Rollback:** `backup/pre-err49-073-image-confirm-metadata-refresh-20260829` → `6d5897ecefc427c940c690daabc311f85cc6e044`.

**Must not touch:** Stage-2 pricing/Profile/Offer logic, OpenRouter-only AI, image selection itself, crawler/acquisition, secure keys, Django schema/migrations, Host/Production.

**Verification status:** code/regressions on GitHub; owner Local rerun required. Production untouched.

**Prevention:** distinguish immutable operator choices from deterministic derived artifacts. A Stage lock may block editing the approved inputs, but must not prevent the system from refreshing derived fingerprints/files when downstream authoritative metadata changes.

### ERR-49-086 — eager Product/Crawl reads and missing pre-Qt acquisition parity made the new Qt surface slower/incomplete on real Catalog data
**Date:** 2026-09-01
**Environment:** Qt Catalog Center branch `agent/phase49-3i18-operator-bulk-ai-rebuild`.

**Owner evidence / symptom:**
- Product/Crawl screens were expected to become faster than the old UI but still loaded large result sets eagerly;
- Product Gallery/Table did not provide the requested 5×10 / 20-row progressive loading behavior;
- persistent Crawl inventory could render thousands of rows at once;
- the new Qt acquisition screen did not expose several working controls/methods present before the Qt visual rewrite.

**Root cause:**
1. `ProductTableModel.refresh()` and `ProductGalleryModel.refresh()` were backed by full Product result sets.
2. Qt list surfaces paid for heavy Product JSON/text columns that cards/tables did not need.
3. Crawl inventory used a large one-shot query and broad Product identity join.
4. acquisition modernization preserved Classic/Hybrid internals but did not restore the full operator-facing method/action parity from the mature pre-Qt UI.
5. Listing continuation filtering needed an indexed `discovered_from` boundary for large ledgers.

**Correct fix:**
- add Product count/page APIs with lightweight list columns;
- use Qt `canFetchMore/fetchMore`: Gallery 50, Table 20;
- page Crawl inventory at 100 rows and resolve Product identities only for the current page;
- add planner indexes for lifecycle/source/status/listing access;
- expose mature old acquisition methods through headless `AcquisitionCore/acquisition_runtime`, never through Tk calls;
- preserve operator-owned Product edits during Source Refresh and record `source_refresh` history;
- retain compatibility full-row Product APIs for mature non-Qt callers.

**Verification:** exact code `a659155da4a4a41e01e926b2ac1263a1756c24e6`; runs `33500317538`, `33500317554`, `33500317788` PASS. Dedicated Windows tests cover 50/20/100 paging, Saved HTML, exact legacy routing, Source Refresh preservation and existing mature acquisition regressions.

**Rollback:** `backup/pre-phase49-3i46-catalog-lazy-acquisition-parity-20260901` → pre-change code checkpoint `e093bf8897aea06480fb62c05aa015d819cebf12`.

**Prevention:** list/view surfaces must request bounded DTO-style database pages; do not emulate lazy loading after a full SQL read. Any presentation migration must inventory working operator capabilities in the previous accepted runtime and preserve them through headless Core boundaries.


## OPEN / SEPARATE ITEMS
### ERR-OPEN-001 — Local `/api/v1/catalog/sitemap/` returns 404
Outside current release gate. Public SEO sitemap is `/sitemap.xml`; verify internal route/client contract before adding duplicate endpoint.

### ERR-OPEN-002 — AI request cost may be unknown
Never invent cost; use provider response/verified lookup or mark unknown.

### ERR-OPEN-003 — Historical image-limit inconsistency
Canonical controlled hard maximum is 20. New acquisition defaults to 5.

### ERR-OPEN-004 — Historical Product Admin 500
Resolved and Production verified; do not treat as open without fresh evidence.

## WARNING DEBT
- CKEditor4 security/maintenance warning.
- `store.W026`: in-memory realtime is not a production multi-process solution; Redis/polling is separate debt.
- Pillow `Image.getdata()` deprecation.
- Google membership credential warning when intentionally unset in CI.
- Social preview enhancement: dedicated `twitter:title`, `twitter:description`, `twitter:image` and `og:image:alt` remain open; core meta/OG/canonical/schema/sitemap are present.

## ERR-49-149 - PowerShell UTF-8 pipeline can corrupt Persian source while patching publisher
**Observed:** a local dirty edit of `catalog_center/app/phase49_3i49_site_publish.py` contained mojibake in Persian user-facing strings.
**Root cause:** passing UTF-8/Persian source content through the Windows PowerShell 5.1 text pipeline.
**Recovery:** backed up the dirty file and diff outside the repository, restored source bytes from Git HEAD, then applied an ASCII-only surgical patch. `git diff --check` and focused tests passed.
**Prevention:** never round-trip UTF-8 source files through default PowerShell 5.1 text encoding; use byte-preserving Git/Python UTF-8 operations.

## ERR-49-150 - Two Store operator contract tests are baseline debt, not this regression
**Observed:** combined Hero/Store gate reported two failures in `store.test_epic49_operator_publish`.
**Baseline proof:** the exact two tests fail unchanged in a detached clean worktree at `3c6d295912bb5f305dccd978f07038d3e38d98bd`.
**Scope:** material-color payload normalization expectation and a legacy template token expectation.
**Prevention:** keep them out of the causal attribution for A2J/republish changes until their owning Store phase is repaired.

## ERR-49-151 - Production reset write blocked by automation safety layer
**Observed:** after a fully eligible read-only preflight and a verified MySQL/media rollback backup, the tool layer blocked the destructive reset POST before execution.
**Impact:** no Product deletion, DB write, or media deletion occurred. Production remains unchanged at the preflight counts.
**Recovery:** preserve the verified backup and exact expected counts; execute only the canonical `phase50-store-reset-v2` contract when a permitted write path is available.
