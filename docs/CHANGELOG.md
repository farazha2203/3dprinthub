## 2026-09-24 - A2Z-O2E Product Media Truth LOCAL_TESTED
- Unified Product Editor selected-media truth and Social media truth around `selected_images_json` plus exact files inside the current Product `local_dir`.
- Added shared exact selected-local resolver with Product-local containment and optional finalized SHA verification; historical/refetch sibling folders are recovery-only and no longer normal Gallery truth.
- Product Editor still shows trusted unregistered files physically inside the current Product folder so the operator can select/promote them; they do not become Social authority until persisted.
- Product Wizard Refresh is now local-truth/compare-only (`recover_site_media=False`); it no longer downloads Site media into Product DB merely by pressing Refresh.
- Social canonical payload aligns public Site media to selected Local media by canonical filename/SHA and fails closed on missing/stale/ambiguous media instead of sending a different image.
- Truth Sync reports exact selected-local count and SHA/mapping errors.
- Verification: direct Media baseline 10/10; O2E changed-condition/direct 14/14; fixture/legacy-contract regression 20/20; broad Image/Product/Social 99/99; compileall/Qt VerifyOnly/Django/no-drift/diff-check PASS.
- Real read-only audit: 543 Products have selected images; 93 resolve exact selected Local truth and 450 legacy rows need explicit recovery because exact files are absent. No bulk mutation was performed. #625 and #628 selected Local SHA/public Social media parity both PASS. Audit digest remained `1129de23233309efd5412f7d47ab286885bfa737586267459d97e68374c85a24`.
- Added planned O2G for target-aware MakerWorld lazy-scroll discovery and O2H for real guarded Crawl hard-delete; O2F follows them.

## 2026-09-24 - A2Z-O2D Product identity / dedup / consumed-Crawl suppression ACCEPTED
- Existing Product identity is rejected by new discovery and treated as terminal collected unless explicitly force-recovered.
- Add Products inventory/count/summary, live candidates, Preview thumbnail work and Batch pending Product fetch all suppress identities already present in Products.
- Discovery ledger rows remain as anti-recrawl identity memory; O2D does not physically delete consumed ledger rows.
- Product table/detail exposes canonical `source_code:external_id`.
- Final Local real Catalog: Products=790, ledger=1115, consumed hidden=650, unconsumed visible=465, ready-to-add=47, incomplete=418, visible mapped Products=0.
- Canonical duplicate audit: external-ID groups=0, normalized-URL groups=0, Source-pattern semantic-ID groups=0; no destructive dedup was warranted.
- Verification: changed-condition identity/batch/preview contracts PASS, focused 51/51, final broad 131/131, py_compile/compileall, Qt VerifyOnly, Django check, migration-drift and diff-check PASS.
- No Server/Production delta.
- Final hardening is GitHub-exact at `4e667f4f49358076b288bb8c8f6982b8a2b20bca`; Automatic acquisition was safely quiesced before cutover, with no force-kill of acquisition work.
- Fresh runtime rollback `phase50-a2z-o2d-runtime-acceptance-20260924-182115` passed source/backup quick_check and logical-digest parity; backup SHA256 `fb01aaab1253851e83e869d3ba012fbab9f9aee8718ffea30fd3a42dc293339e`.
- Exact-SHA runtime acceptance: Products=847; raw Crawl=1192; consumed hidden=707; Add Products visible=485 (50 ready / 435 incomplete); visible mapped Products=0; queue summary=485; canonical duplicate groups=0; Product identity visible in table/detail; before/after smoke digest unchanged at `870c0286f998eec21fcfea3728b5a3c924cf4e1c4791d353ebcb9a570f2339c3`.

## 2026-09-24 - A2Z-O2 Crawl Complete/Incomplete Views ACCEPTED
- Centralized Crawl completeness in AcquisitionCore; UI no longer owns a second completeness rule.
- Complete requires Product mapping + title + description + at least one physically displayable local image.
- Added Complete/Incomplete persistent-inventory filters; incomplete cards show exact missing reasons and complete cards show a positive marker.
- Shared ImageCore is injected into AcquisitionCore so Product/Crawl image truth stays one authority.
- Added first-hit filesystem image existence + per-scan identity cache. Real Catalog stayed exactly 1099 = 453 complete + 646 incomplete while cold Complete count improved from ~11.479s to ~2.402s; Incomplete ~3.464s.
- Verification: baseline Crawl 36/36, O2 focused 39/39, broader Crawl/Product/O1/O1B 128/128, compile/diff/Qt VerifyOnly/Django/no-drift PASS.
- Windows Catalog UI/Core only; no migration or Production mutation/deploy.
- GitHub-exact source `f04d5b05...`; fresh logical rollback quick_check/digest PASS, SHA256 `ca7b9ff29c70b741ac522146b8d79b23111b38bf569563283a05558c8a87356a`.
- One exact-SHA Catalog Center cutover completed. A five-second window-handle probe was early, so the same process was retained; delayed readiness exposed the expected Qt window without a second restart.
- Three Product rows (#779/#780/#781) were proven to have been created by acquisition still running in the previous instance before the O2 cutover; no pre-existing Product row changed.
- Final real runtime truth: quick_check=ok, Products=781, Crawl 1099 = 463 complete + 636 incomplete. Complete/Incomplete UI smoke loaded real cards and before/after logical digest remained exactly `f9cd3201bbc97f3d85d1085b63efca0a500a8c44b3158c82137d82f07df911b8`.

## 2026-09-24 - A2Z-O1B Recent Product Activity LOCAL_TESTED
- Added Product filters `آخرین ادیت‌شده‌ها` and `اخیراً دیده‌شده‌ها`.
- Recent edit sorting is based on explicit operator-save `product_history` events only; generic Product `updated_at` is not used because system sync/refetch can change it.
- Added persisted `product_viewed` history after successful Product Wizard load only. This writes no Product fields and cannot set `needs_update` or alter Site identity/revision.
- Recent activity filters force newest-first ordering and lock the Gallery sort selector to prevent UI/query disagreement.
- No schema migration: existing `product_history` is the auditable persistence authority.
- Real read-only Catalog baseline: quick_check=ok, recently_edited=523, recently_viewed=0 before first real post-O1B Editor open.
- Verification: focused 7/7 PASS; broad Product/Qt/O1 106/106 PASS; final Product/Page related 77/77 PASS; final broad 106/106 PASS; compile/diff/Qt VerifyOnly/Django no-drift gates PASS.
- Runtime acceptance: GitHub-exact source `a0d5ea46...`; fresh backup/clone quick_check=ok / 771 Products; real cloned MainWindow/ProductWizard open of #717 produced one `product_viewed`, made #717 top Recent View, kept Product row unchanged, and canonical DB stayed unpolluted; visible Catalog Center runtime smoke PASS.

## 2026-09-24 - A2Z-O1B Recent Product Activity requested
- Inserted O1B between accepted O1 and O2.
- Planned Products display options: `آخرین ادیت‌شده‌ها` newest-first by latest real operator-save history, and `اخیراً دیده‌شده‌ها` newest-first by actual Product Editor open/view activity.
- Generic Product `updated_at` is explicitly not the edit authority because sync/refetch/system work can modify it.
- Existing operator-save evidence includes `studio_save` and `qt_operator_edit`; implementation must inventory all accepted edit-save events before query freeze.
- No existing Product-view timestamp/history contract was found, so O1B will add explicit persisted view tracking on Product Editor open only; gallery render/selection/hover/search must not count and view tracking must never dirty Site/republish state.

## 2026-09-24 - A2Z-O1 Product operational filters + independent Instagram Post/Story
- Closed the mandatory Windows/Production lineage gate first: merge head `82862b4569b537406618523f7350cd3514c4c03f` contains both accepted lineages and preserves the Windows tree byte-for-byte.
- Added Product filters backed by canonical stage locks/receipts: ready 7/7, AI-completed 6/7, Site sent, Instagram Post published and Instagram Story published.
- Split the previous combined Social action into separate «ارسال پست Instagram» and «ارسال استوری Instagram» buttons with independent readiness/workers/results.
- Feed-only calls Buffer with `companion_story=False`; native Story mobile readiness cannot block Post-only.
- Story-only calls `publish_story_for_product` directly and the GitHub media host accepts a Story derivative without Feed derivatives; no Feed/Post is created.
- Verification: filter changed-condition 1/1, focused Product/Social/Buffer 24/24 and broader Product/Qt/Social 136/136 PASS; compile, diff-check and Qt VerifyOnly PASS.
- Real Catalog read-only counts: ready_7=2, ai_6=19, published=14, instagram_posted=4, instagram_story=2; quick_check=ok.
- No Product/Site/Social production mutation was performed by O1 tests.
- O1 source is GitHub-exact at `22bb0fb1ecca2f894e34bcbd7dda8b7d424b394e`; pre-runtime Catalog backup passed quick_check/771 Products, Catalog Center was closed exactly once and relaunched from that SHA, and live window/runtime smoke passed with post-restart quick_check=ok.

## 2026-09-24 - A2Z final acceptance
- #628 final successful Batch is receipt #433 / UUID `4976dd73-7d1d-44c5-8440-3e0eb142194c`: Site Product #38 revision 2, republish parity ok=true, media_count=2, profile_count=32 and public_http_ok=true.
- Independent Production readback confirms two active images, 32 active / 190 inactive historical variants, exact 12×12×12 113g/511min and 18×18×18 312g/991min profiles, price 3,063,500–6,479,000 and Slider disabled.
- #625/#620/#152/#178 collateral state remained unchanged.
- Real Playwright acceptance passed at Desktop 1440×1000 and Mobile 390×844: HTTP 200, two healthy #628 media, no stale Unicode path, no horizontal overflow and no page/console errors.
- Phase50.A.2Z is CLOSED / ACCEPTED. Production remains on selective Server head `2b48a593ace2e9a3703fa0f52b4c3c13b2751cf9`.

## 2026-09-24 - A2Z #628 exact Unicode root cause: Batch source path
- Rollback-only Production trace proved every importer stage, Product parity and Portfolio pass for failed Batch `desktop_catalog_v85_20260924_105415`; Site #38 stayed revision 1.
- Forced ASCII filesystem reproduction on that exact Batch produced the same `UnicodeEncodeError` at positions 127-131 when opening the Persian `local_image_files_json[0]`.
- Windows Batch packaging code is GitHub-exact at `7b1b447ab772e15f3ecdc1345e69e2e8771573f8`; it sends selected image files under deterministic ASCII-safe names while retaining the operator Unicode SEO filename in editorial metadata and preserving bytes/SHA.
- Existing ASCII filename behavior is unchanged; Windows and Server canonical helpers match exactly for #628.
- Gates PASS: focused 1/1, bulk/batch 33/33, broader 50/50, compile/diff/Qt VerifyOnly; real #628 clone dry-run generated two ASCII files with selected-order SHA parity and zero canonical Catalog logical change.
- Production remains clean at `2b48a593...`; no additional Server source deploy is required for this Windows-only source-path fix.

## 2026-09-24 - A2Z #625 Production parity + #628 Unicode media recovery
- Restored and authenticated the dedicated 3DPrintHub reverse tunnel; Host gate passed on clean Production `103f559c...`, MySQL identity and applied Store migrations.
- Created and verified fresh Production DB + full-media rollback before #625; published only #625. Site Product #39 advanced to revision 13 with strict ACK parity, one active ProductImage, 32 active Variants and no stale public media path.
- Created a second verified Production DB + full-media rollback before #628.
- First bounded #628 import failed rollback-safe with UnicodeEncodeError on a Persian media basename; no unchanged retry was made and Site revision stayed 1.
- Added one shared deterministic ASCII-safe Server/Public media basename contract while preserving Windows metadata, ALT/caption, selected identity and image bytes/SHA.
- Added Unicode Product+Portfolio regression and aligned republish parity to the same canonical server filename.
- Verification: Unicode 1/1, unified import 5/5, related visibility/profile/video 21/21, compile/check/no-drift/diff PASS.
- Runtime-bearing fix source: `b5980306400f3f0951804cab1ad049c1aab4a6d7`; selective Production release from exact `103f559c...` is next.

## 2026-09-23 - A2Z exact-SHA local acceptance and tunnel-safe stop
- Pushed exact A2Z source/docs checkpoint fde86e23...; Local=GitHub exact and Qt launched from that SHA.
- Reconciled #625 revision authority 11->12 from exact local publish_incomplete receipt only; operator digest unchanged.
- Re-ran #625 Ready core with no Profile/Filament/Image or price-range drift.
- Marked #628 Ready; preserved 12cm/18cm profile geometry, 16 PLA offers/profile and two selected media; refreshed pricing to 3,063,500-6,479,000.
- Captured post-local Catalog rollback phase50-a2z-post-local-gates-20260923-215515, quick_check=ok.
- Stopped before Production write because official 22024 reverse tunnel is down and therefore fresh Production DB/media rollback cannot be verified.

## 2026-09-23 - A2Z Catalog Data Completion local-tested checkpoint
- Opened `wip/phase50-a2z-catalog-data-completion-20260923` from clean unified head `56c569...`.
- Current Catalog is 771 Products; six-field Slider completeness is 61/771; only enabled Product #40 is missing a Slider image.
- Confirmed #152/#178 are already Site-reconciled and clean; no retry is warranted.
- Confirmed #620 is already public/clean; #625/#628 are the current `needs_update=1` bounded candidates.
- Added incomplete Crawl visibility/reasons and same-identity forced recovery while preserving complete Product no-refetch behavior.
- Fixed selected-row completeness false-negative by resolving canonical Product facts when queue selection carries only Product ID.
- Added exact-receipt revision-only reconciliation for an unabsorbed `publish_incomplete` Site revision; all other stale revisions stay fail-closed.
- #625 evidence: receipt #316 / Batch `26aa571c...` created Site Product #39 rev12 with `publish_incomplete`; Local content is not pulled or overwritten.
- Final related regression 153/153 PASS; Server 12/12 PASS; compile/check/no-drift/diff/Qt gates PASS.
- Fresh pre-mutation Catalog snapshot quick_check=ok with 771 Products at `phase50-a2z-data-completion-pre-mutation-20260923-202714`.

## 2026-09-23 - A2Z-LC A2R lineage convergence ACCEPTED
- Detected and blocked post-A2Y divergence between newest A2Z Windows development, Windows A2R motion-media and selective Production A2R.
- Preserved the dirty A2Z Data Completion worktree; convergence ran in a separate clean worktree/branch.
- Unified Product motion-media discovery/download/Site publish/import/render/public verification using the proven canonical A2R fields, including MakerWorld animated GIF media.
- Source re-crawl preserves operator video selection/local media; no parallel video authority is introduced.
- Current Buffer Feed/Story remains image-based; motion metadata is available but Reel/video Social delivery is still a separate future capability.
- Verification: 8 video + 41 Social + 40 Crawl/V84 + 55 Publish + 12 Server tests PASS; compile/check/no-drift/diff/runner/Qt gates PASS.
- Runtime-bearing source commit: `be00cc73d7745406b7219d323890f05222f17494`.
- Accepted Git ancestry merge: `05f29ba3a4de53fcf8b0a6fd73427a3653bb0ed3`, Local=GitHub exact; Windows A2R `03808add...` and Production A2R `103f559c...` are both ancestors.
- Production remains unchanged on healthy `103f559c...`; broad unified deployment is intentionally blocked because unrelated Server settings/ZarinPal deltas are present despite zero migration/dependency delta.

## 2026-09-23 - A2Z-S2 automatic Story + Shop Grid PRODUCTION ACCEPTED
- Runtime source exact at `447e81306a19d816042530f3d00989305a84bd2c`; exact-SHA Qt running.
- Live readiness passes without Buffer mobile under default `bio_shop_grid` / `buffer_shop_grid` contract.
- Real #536 retry reused existing Feed `6ab2c778...` and created **no duplicate Feed**.
- New Story `6ab383f9497d7707d81648c8` is Buffer `sent` and live at `https://www.instagram.com/stories/3dprinthub_ir/3992386891974821993`.
- Story is automatic, v5 policy, v3 Gold/Navy/IRANSans, 1080×1920; provider asset public SHA parity passes on social-assets commit `3fedd69e...`.
- Public Shop Grid already maps #536 to its exact Product UTM URL.
- Historical #536 Feed remains v4 because dedupe reused the live post; future v5 captions omit raw URLs. Buffer cannot edit already-published Instagram posts.

## 2026-09-23 - A2Z-S2 automatic Story + correct Instagram link semantics
- Historical #625 receipt proves automatic Buffer Story publication is the accepted working baseline.
- Default Story route restored to automatic Buffer publishing; mobile-dependent native Link Sticker is now optional only.
- Feed Product click-through remains in Buffer Shop Grid via `metadata.instagram.link`; raw URLs were removed from Caption because they are not clickable Instagram caption links.
- Story artwork no longer prints a raw Product URL; CTA now points users to the Bio/Shop Grid and keeps Gold/Navy + IRANSans branding.
- Policy bumped to `instagram-product-v5-20260923`; Story style/cache key bumped to `...v3_iransans_bio`.
- Focused 27/27 and complete Site+Social 70/70 PASS; 11 Python compile, diff and Qt VerifyOnly PASS; no Server delta.

## 2026-09-22 - A2Z-S Post + linked Story early-readiness hardening
- Reconfirmed real Instagram provider as Buffer GraphQL (`https://api.buffer.com`) on channel `3dprinthub_ir`; current media derivatives remain `github_raw`.
- Added `InstagramCore.delivery_readiness()` / `require_delivery_readiness()` so clickable Story mobile capability is verified before Site publication, Story/Feed rendering, GitHub rehost or Buffer createPost.
- Products UI now says **Post + Story لینک‌دار** and stops before starting its Worker when Buffer mobile is not active.
- Existing revision-scoped Feed duplicate protection and lower-level Buffer guard remain intact.
- Focused 22/22 and full Site+Social 69/69 PASS; 4 Python compile + diff + Qt VerifyOnly PASS; no Server/migration delta.
- Runtime-bearing SHA `ec05b77fec0d3316d8ee9663fb50b333cf437658` is Local=GitHub exact and running in Qt.
- Live provider on the accepted SHA still reports `hasActiveMemberDevice=False`; the new Core returns `ready=false` before Site/provider/media work, and no real external send was attempted by this change.

## 2026-09-22 - A2Z-C3 HERO RECOVERY ACCEPTED / SOCIAL MOBILE PREFLIGHT GITHUB_UPDATED
- Hardening source is exact at `bed7b27a7851a925af6756f70f7bbc5b71ab1845` and running in Qt.
- Fresh Catalog + Production MySQL rollbacks were verified before real retry.
- Bounded #152/#178 Batch `desktop_catalog_v85_20260922_221736` completed 2/2 with no failures.
- #152 -> Site #50 / Hero #2 rev3 / 3 media / 48 profiles; #178 -> Site #51 / Hero #4 rev6 / 2 media / 64 profiles.
- Operator-owned Product/Slider digests remained unchanged; both Hero rows are active/desktop-owned; Product and all canonical media HTTP 200.
- Queue reduced to 8; post-accept Catalog backup quick_check PASS.
- Buffer clickable-Story preflight remains correct; live channel still has no active member mobile device, so #536 Feed remains live/deduplicated while Story waits for mobile Link-Sticker handoff.

## 2026-09-22 - A2Z-C3 Hero revision + clickable-Story preflight hardening
- Added pre-publish Site Hero revision refresh using current Bridge truth; only local `server_slider_revision` changes, never Product/Slider editorial data or membership.
- Added Buffer `hasActiveMemberDevice` to channel health and fail-closed clickable-Story prerequisite before new Feed creation.
- Existing successful Feed receipt remains duplicate authority; when mobile reminder device is absent only Story stays blocked.
- Real #536 Feed is live at `https://www.instagram.com/p/DdmXo5QlMEd/`; branded Story asset is 1080×1920 github_raw, Gold-Navy/IRANSans pipeline, SHA `d2ca7066...`.
- Buffer currently reports `hasActiveMemberDevice=False`; automatic no-link Story is intentionally not substituted.
- Focused 16/16, Site+Social 65/65, py_compile/diff/Qt VerifyOnly PASS; no Server delta.

## 2026-09-22 - A2Z-C3 Full Registration + quota incident
- Added **«✅ ثبت کامل»** next to Full Edit in Product Wizard.
- The action saves the current editable Stage, then explicitly approves every complete canonical Stage through the existing StageCore validator; incomplete Stages remain blocked.
- Full Registration never marks ready, publishes, starts FTP/Bridge or sends Social content.
- Focused 3/3 and related regression 82/82 PASS; compile/diff/Qt VerifyOnly PASS; no Server/migration delta.
- Real Product #536 batch `desktop_catalog_v85_20260922_171201` failed at FTP directory creation with shared-account quota before any file-upload receipt or Bridge import; earlier #588 shows the same class.
- Official PrintHub reverse tunnel is down; current Host-IP SSH is RetoucherTunnel and is intentionally not used for 3DPrintHub cleanup.

## 2026-09-22 - A2Z-C1/C2 Full Edit + Unified Bulk Completion ACCEPTED
- Added top Product Wizard «✏ ویرایش کامل» using the existing audited stage-unlock authority; entering edit mode alone does not publish or mark Product data dirty.
- Products multi-select Bulk AI now composes accepted later-stage capabilities after its existing AI content run: factual Source Profiles, multi-profile Local Filament mapping, validated Category, physical SEO filenames and six-field Slider completeness.
- Bulk completion preserves manual Profiles, Site-image membership, Slider membership and Publish authority.
- Corrected Persian Category exact matching (ERR-49-223): empty ASCII folds can no longer falsely select the first Persian category.
- Runtime-bearing SHA `8629f8b72c416b364a618a5aeebe2dda8a81d440` is GitHub-exact and running in Qt.
- Exact-SHA widget smoke 2/2 PASS; idle real Catalog Products/history/quick_check remained unchanged.
- Verification: focused 3/3; broad rerun 129/130 with only historical ERR-49-203; prior 148/149 effective gate same baseline; unchanged-cycle rerun 40/40; compile/diff/Qt VerifyOnly PASS; no Server/migration/dependency delta.

## 2026-09-22 - ERR-49-221 transient WAF readiness hardening
- Real Product #588 Site publish was blocked before Batch/FTP by a transient BitNinja `Visitor anti-robot validation` HTTP 403 on Catalog Bridge publish-readiness.
- Read-only changed-condition probes with the real secure Bridge token now return health 200 and readiness 200/`ready=true`, confirming receiver/token health.
- Added bounded Catalog User-Agent/no-cache headers and up to three total retries only for idempotent GET requests positively identified as the WAF anti-robot page.
- Import POST remains single-attempt and is never blindly retried; existing timeout diagnostics/idempotency remain authoritative.
- Persistent WAF HTML is summarized into a concise operator error.
- Verification: focused 13/13; corrected Publish/SiteConnection 86/86; py_compile/diff-check/Qt VerifyOnly PASS.
- No new #588 Batch/FTP/import receipt exists from the failed attempt; no Site mutation occurred.
- Host-management reverse tunnel 22024 is currently down, so any future Host deployment remains blocked; no Host deploy is required for this Windows-only hotfix.

## 2026-09-21 - A2Z-S real #609 Feed live + notification-device recovery hardening
- Executed one guarded current-revision Social send after exact-SHA/pre-backup/public-media gates.
- Feed Buffer id `6ab16b897465bdab83a3fe40` is live at https://www.instagram.com/p/DdjtyiMG8RC/ with all five expected github_raw assets; submitted receipt reconciled to published without repost.
- Story notification id `6ab16b959d554f7b28a44302` failed at Buffer because no eligible linked mobile reminder device exists; media and Link Sticker metadata are valid.
- Added provider-error Post read-back, fail-closed Story handling and retry-safe duplicate semantics. Historical notification-ready receipts with `buffer_status=error` no longer suppress recovery.
- Social 37/37 PASS; compile/diff/Qt VerifyOnly PASS.
- Feed is permanently protected for this ACK; after Buffer mobile linking, retry is Story-only.

## 2026-09-21 - A2Z-S github_raw Social transport decoupled from Site FTP
- Real #609 Social preflight reproduced WinError 10054 during mandatory Story FTP upload before any Buffer post.
- `github_raw` now renders Feed/Story derivatives locally and publishes provider assets only through the dedicated GitHub social-assets worktree; canonical Site Product media are unchanged.
- `site` provider-media mode retains its existing FTP/public verification behavior.
- Buffer media host accepts local-only derivative metadata while preserving canonical source-media audit.
- Social 35/35 PASS; real #609 local-only render generated 5 Feed PNGs + approved 1080x1920 Story with zero receipt mutation.
- Real #609 GitHub rehost is public and exact: social-assets commit `3294d817...`; 5 Feed PNG + Story all HTTP 200 image/png and SHA-equal to manifest.
- Clickable Story handoff is now truthful: Buffer notification scheduling + explicit Link Sticker UTM metadata, `instagram_story_notification_ready` receipt, no false live-published state; automatic no-sticker mode remains supported. Expanded Social regression 36/36 PASS.
- Fresh rollback: `pre-instagram-a2z-609-20260921-201631`.

## 2026-09-21 - A2Z #609 physical repair + source-drift boundary
- Took fresh integrity-checked Catalog and full #609 media rollback before real mutation.
- Repaired #609 via ImageCore: five selected/canonical media now use five unique physical SEO WebP identities; original selected source/cache files preserved.
- Fixed publish source-drift to compare preserved original bytes against original SHA after physical SEO promotion.
- Focused 3/3 and Image+Site Publish 51/51 PASS.
- Site #42 remains revision 1 pending exact-SHA commit/push and guarded same-identity republish.

## 2026-09-21 - A2Z image/social authority hotfix Local-tested
- Fixed exact-URL image metadata lookup so query-variant cards keep distinct numbered SEO filenames.
- Trusted Local media checked for Site now joins canonical Product media at Stage-3 save.
- Social Git media hosting now reuses the worktree already registered for `social-assets-buffer`.
- Added regressions proving unique physical SEO WebPs and multi-image Batch packaging.
- Focused 9/9 and broad Image/Publish/Windows/Social 113/113 PASS; compile/diff/Qt VerifyOnly PASS.
- Real #609 has 5 finalized unique SEO WebPs; no Catalog/Production write has been performed by this code slice yet.

## 2026-09-21 - A2Z physical Product-local SEO filenames
- Extended A2Z image authority so applying Product image SEO renames/promotes the real Product-local physical media, not only metadata or publish derivatives.
- Historical source/cache bytes move to `source_originals/`; active Product media in `images/` uses deterministic unique `-01/-02/...` SEO WebP basenames.
- Exact physical path is persisted and local identities/page-extract mappings converge on the new filename.
- Removal/recovery now supports SEO-named local media, not just legacy numeric names.
- Verification: direct 3/3 + combined Image/Publish/Windows/Social 109/109 + compile/diff/Qt VerifyOnly PASS.
- Real #609 has not yet been mutated in this slice; backup-backed repair and Site/Instagram acceptance remain next.

## 2026-09-21 - A2Y lineage convergence accepted
- Created/pushed unified merge `f9a9c203ae3a0a5665dbf884ce0c3e4bf761110b` with latest Windows/A2Y and accepted Server/Production closure as its two parents.
- Exact-SHA Qt VerifyOnly + real runtime smoke PASS; running Qt points to the unified worktree and left the shared Catalog Product/history counts unchanged.
- Desktop LNK/CMD were backed up and retargeted from A2U to the unified launcher only after runtime acceptance.
- Shortcut rollback root: `phase50-a2y-shortcut-20260921-183438`.
- No Catalog backfill, Product publish, Host source deploy or Production DB write occurred in A2Y.
- A2Y is closed; A2Z now owns Catalog Slider completion and final Windows operator acceptance.

## 2026-09-21 - A2Y lineage convergence Local-tested
- Merged latest Windows/A2W/A2X Slider lineage with Production Server/A2X Hero/republish/finance lineage in a clean isolated worktree.
- Kept Windows operator/UI authority while retaining hardened A2S Social and current Server authoritative-republish/Hero public-media boundaries.
- Regression: Windows focused 94/94; Server focused 52/52; broad Windows 115/116 with only historical ERR-49-203.
- Static gates: 46 changed Python files compile; Django check/no-drift, diff-check and Qt VerifyOnly PASS.
- Corrected one stale baseline test that still asserted Hero asset cache 50.8.0 while accepted Production contract is 50.10.0.
- No Catalog, DB, Host or Production write was performed by A2Y convergence.

## 2026-09-21 - A2Y master reconciliation and remaining-work truth freeze
- Audited Repository phase docs, owner request ledger, available project chat archives, current Git branches/worktrees and canonical Catalog state.
- Recorded the split forward lineage: latest Windows `c86c66a1...` versus current Production/Server closure `e03bdd2b...`, merge-base `b1caeba...`; A2Y convergence is now the blocking next phase.
- Recorded real Catalog Slider completeness: 635 Products total, 50 core-complete, 585 incomplete.
- Carried forward still-open owner requests: changed-revision Social, manual Product, source video/Reel, dynamic carriers, secure Store ZarinPal, Torob, Google/local login + Customer account closure, Product engagement, full customer Telegram Bot/Mini App and the accounting stack.
- Updated project rules so every development report must name the exact next phase, ordered operations and test/backup/deploy/Production gates.
- No Product/SQLite/Production/runtime mutation occurred in this documentation phase.

## 2026-09-21 - Phase50.A.2X Slider completeness + same-identity authoritative re-publish
- Slider SEO/media readiness is now independent of the homepage membership checkbox.
- Added Slider title/description/ALT/button/focus/image to mandatory Product data completeness while leaving membership operator-controlled.
- Single-Product AI refresh/rebuild and selected-Product bulk SEO now persist Slider data without toggling membership.
- Missing Slider image can use current Primary/selected Product media.
- Published Product Slider edits now mark the same preserved Site identity for update even when only `server_product_id` is populated.
- Server Product SEO sync no longer preserves stale old Site values when the current Desktop snapshot should win.
- Added regressions for disabled-membership Slider fill, bulk content+slider scope, same-identity dirty marking and Slider on/off/on Server synchronization.
- Verification: focused 33/33, Server 9/9, broad 115/116 with only documented baseline ERR-49-203, plus compile/diff/Django/no-drift/Qt VerifyOnly PASS.
- Real #620 content pack already carries complete Slider SEO; no-AI backfill is the next data step.
- No Production mutation or migration yet.

## 2026-09-21 - Phase50.A.2W W4.1 owner correction — dimensions + PLA defaults Local tested
- Owner correction changes operational size behavior: when a Source Size exposes exactly one factual dimension (for example Height=12cm), the created Source Profile uses that same numeric value for all three operational axes, so Hydra Small becomes 12×12×12cm and Large becomes 18×18×18cm. Provenance still records Height as factual and Length/Width as `owner_equal_dimension_rule`.
- Source material-family defaults now hydrate real Local Filaments during Source Profile import/repair. If Source says PLA, every active exact-family Local PLA offer is selected/added; PLA-CF/HT-PLA-GF/PETG are excluded by exact family matching.
- Real Local Catalog currently has 16 active PLA offers across Bambulab, E-Sun/ESUN and PolyGround. Read-only simulation proves both #628 Source Profiles receive 16/16 PLA offers.
- #625 safety is preserved: Profile 1 keeps existing 5×5×5cm and receives/retains 16 PLA; Profile 2 receives 16 PLA and only its still-missing dimensions are eligible for the explicit owner 4×4×4 estimated fallback.
- Source placeholders without Brand are removed when concrete compatible Local offers exist; operator-owned concrete Filament choices are preserved/deduplicated.
- Verification: Source/Profile+dimension focused 15/15 PASS, W4 mapping 5/5 PASS, mature Commerce/Profile+W3/W4/W4.1 59/59 PASS, retained media/site 83/83 PASS, py_compile/diff-check/Qt VerifyOnly PASS.
- Rollback ref: `backup/pre-phase50-a2w-w41-owner-dimension-filament-correction-20260921` -> `436d34f2...`; source is pushed at `7f2280e...`. Real Local Catalog repair is accepted for #628/#625 with Site identity/revision unchanged; post snapshot SHA256 is `7743e63f...c3ca8da`.

## 2026-09-21 - Phase50.A.2W W4.1 Source dimension evidence — Local tested
- Added deterministic Description dimension extraction for labeled Source sizes and generic L×W×H values, with unit normalization to cm and no AI/inference.
- Added fail-closed ordered binding: Description size records map to Source Profiles only when counts match, preventing ambiguous multi-size guessing.
- Preserved partial factual dimensions. Unknown axes remain zero in storage but render as `نامشخص` in the Qt Profile editor; manual Profiles still require complete positive dimensions.
- Added dimension provenance fields including factual vs owner-estimated source, known axes, evidence text and per-axis authority.
- Added dimension-only Ledger patching that preserves existing pricing, Filament choices, weight/time, manual Profile data and Site identity.
- Real latest MakerWorld capture for Hydra #628 proves Small height 120mm -> 12cm and Large height 180mm -> 18cm. Fixed compact meta boundary `180 mm2. Support...` without loosening unrelated unit parsing.
- #625 fallback contract is protected by regression: existing 5×5×5 Profile 1 is preserved; only missing Profile 2 receives owner-approved estimated 4×4×4.
- Verification: focused 10/10, Commerce/Profile+W3/W4/W4.1 59/59, retained media/site 83/83, py_compile/diff-check/Qt VerifyOnly PASS.
- Rollback ref: `backup/pre-phase50-a2w-w41-source-dimensions-20260921` -> `f8a23ab0...`. No real DB/Host/Production mutation yet.

## 2026-09-21 - Phase50.A.2W W4 Smart Local Filament mapping — Windows runtime accepted
- Added read-only Source material/color slot -> active Local Filament offer/pricing preview; Preview never mutates Source facts, Sales Ledger, Stage locks or Site identity.
- Material family matching is exact/case-insensitive. Color matching uses only explicit Local HEX/Palette evidence; localized color names are never converted into inferred HEX.
- Preserved #625 Multicolor as two simultaneous Source slots (11g #804003 + 39g #FECC66) instead of flattening them into alternative material choices.
- Reused the existing mature commerce pricing formula for single-slot full-price preview; Multicolor reports per-slot material cost until real Local offers are chosen.
- Real Local inventory inspection found 16 active PLA offers; current Source colors #FECC66/#804003 have exact Local HEX match count zero.
- Added Stage-2 action `W4 تطبیق Filament محلی` and a read-only review dialog with Brand/color/HEX/stock/roll price/material-cost evidence.
- W4 focused 5/5 PASS; corrected mature Filament/Profile/Commerce + W3/W4 49/49 PASS; retained media/site 83/83 PASS; py_compile/diff-check/Qt VerifyOnly PASS.
- Clean-baseline reproduction proved two broader 51-test failures are pre-existing stale assertions, not W4 regressions; ERR-49-203 records the evidence.
- Pushed exact W4 source `27bb00a1d8a8dd34e033af9cfaba27f37384a0a0`, verified Local=remote and relaunched Qt from that exact SHA.
- Fresh pre-preview Catalog backup `phase50-a2w-w4-pre-preview-20260921-114901` integrity PASS / SHA256 `a38f78d346e2b367eaaeed540837ff5e076dea890c26808ddc0437106f239f7e`.
- Real #625 W4 button-level Preview PASS: 2 Profiles / 3 Source slots / 48 Local PLA candidates / exact HEX=0, with Source facts, Sales Ledger, Stage locks, Site #39 revision 11 and history count unchanged.
- W4 made no publish attempt. A separate pre-W4 failed batch `26aa571c-...` remains on Local state `batched / needs_update=1 / upload_ready=1` with Site revision 11; ERR-49-206 tracks it.
- Next owner follow-up W4.1 will replace missing #625 dimensions of zero with an explicit estimated 4.0cm × 4.0cm × 4.0cm fallback while preserving exact dimensions whenever available.

## 2026-09-21 - Phase50.A.2W W3 factual Source Print Profiles — Windows runtime accepted
- Added deterministic MakerWorld `__NEXT_DATA__` Print Profile extraction into existing `source_print_profiles_json`; no AI/inference is used for these production facts.
- Preserves multiple source Profiles separately and records exact source instance/profile ids, seconds/minutes, weight, plate count, material families, per-filament source color/usage, printer compatibility, nozzle, layer, walls and infill.
- Stage 2 now exposes `دریافت پروفایل از محصول`; Source refresh does not alter the Sales Ledger. Operator-confirmed import uses deterministic source keys, preserves manual Profiles and is idempotent.
- #625 factual proof: Single Color 3609481/943581967 = 4814s/13g/PLA #FECC66; Multicolor 3609488/943610448 = 15748s/50g/PLA 11g #804003 + 39g #FECC66; both A1/N2S, 0.4mm nozzle, 0.16mm layer.
- Source facts retain exact time; integer Sales Ledger uses nearest minute 80/262. Brand/local pricing are intentionally not invented; W4 owns real Local Filament mapping.
- W3 focused 5/5 PASS; corrected retained A2V/W1/W2/bidirectional gate 83/83 PASS; py_compile, diff-check and Qt VerifyOnly PASS.
- Fresh pre-real-W3 Catalog rollback `phase50-a2w-w3-pre-real-625-20260921-102142` integrity PASS / SHA256 `ba7d70b04cf5b084bd7922bd0f93f321a55cc4c7c241795f32c6840235764401`.
- Read-only history proves current #625 `needs_update=1` came from later source recovery images 2→5, not W3; Site Product remains #39 revision 11 and W3 has not published anything.
- Pushed exact W3 source `36dbf3cf283fc1e5697091549e930416c671cbe7`, verified Local=remote and launched Qt from that SHA.
- Real Stage-2 button smoke used a fresh MakerWorld capture, persisted exactly two Source Profiles and left Site #39/rev11 plus the existing Ledger unchanged when import confirmation was declined.
- Took a second pre-import integrity backup `phase50-a2w-w3-pre-ledger-import-20260921-103253` / SHA256 `bbf3614285b79da354505775a3750db57257a8ab790171a953168895443f055e`.
- Controlled StageCore Commerce unlock + real import preserved manual `ledger-dcff93fba1e9`, added exactly `source-mw-3609481` and `source-mw-3609488`, introduced no local Brand/pricing, and created no publish event.
- Post-import integrity/readback PASS; accepted snapshot `phase50-a2w-w3-post-ledger-import-20260921-103507` / SHA256 `fbeeca44c9ebb46be75c1dc6a70ab2eaa6a34aa719483808578c56fb3be05a9d`; Qt Stage 2 shows exactly three Profiles. Commerce remains intentionally unlocked for W4.

## 2026-09-21 - Phase50.A.2W W1/W2 media truth sync — Local tested
- Added Stage-3 `رفرش رسانه و وضعیت` to compare canonical DB media, persisted `ارسال سایت`, local displayable files and current live Site Product media.
- Added checksum-aware/idempotent recovery of Site media as local candidates without silently changing Site membership.
- Renamed source refresh action to `دریافت جدید از منبع` so Site truth refresh and source refetch are not conflated.
- Closed the pending-selection timer race by flushing current Stage-3 selection/Primary before Ready/Publish.
- Ready now auto-finalizes only newly selected/unfinalized media such as a fresh screenshot, while stale SEO signatures or missing finalized media remain fail-closed.
- Added A2W regressions; focused 49/49 and broader A2V+A2W+bidir 83/83 PASS; compile/diff/Qt VerifyOnly PASS.
- Fresh pre-Truth-Sync Catalog backup integrity PASS; real #625 Truth Sync reports DB=2, Local=3, Site-selected=1, Site=1, mismatch=0 with revision 11/identity/dirty state unchanged.
- Verified read-only that current Production receiver already enforces exact media gallery count + filename/SHA parity and transaction rollback on mismatch; no Host delta is required for W1/W2.

## 2026-09-21 - Phase50.A.2V image authority hardening — Production verified
- Hardened Windows Site-publish media authority: Site-selected media must be part of canonical Product images or publish fails closed.
- Renamed Qt image controls to distinguish temporary bulk `ویرایش` from persisted `ارسال سایت`.
- Preserved explicit Site-selected local images across source refetch, including legacy numbered image filenames; unselected numbered source-cache slots remain replaceable.
- Added regression coverage for authority drift, refetch ownership and UI contract; stable Image/SEO/Packaging/Republish gate 72/72 PASS plus compile/diff/Qt VerifyOnly PASS.
- Repaired #625 canonical image authority from persisted evidence after verified revision-10 rollback; no unrecorded `phase49_3c_*` media was guessed.
- Pushed exact source `4e69ed6a5c0996c7249830fbe029cd01460ad5b1` and ran the accepted A2V Qt runtime.
- Real acceptance persisted exactly one Site image, `local://04.webp`, and republished #625 in place to Site Product #39 revision 11 using batch `desktop_catalog_v85_20260921_081158` / `cb51fb28-acd2-45a7-8a86-40ea5268614c`.
- Local final SEO, Batch, Production stored media and fresh public HTTPS bytes are all 36,162 bytes with SHA256 `cf6f0422f0cde915e9203ddbca6564df694fb4b6a97320e1af0e7f4117c68fff`.
- Public Product/image verification is HTTP 200 and Production retains exactly 3 active current CC Variants with current weight/time/prices.
- Production source remains clean at `03042d0430ee6e688c992c875f12edc969df103d`; no Host source deploy/migration/restart was needed.
- The planned immediate pre-republish backup was missed before revision 11 completed; no duplicate revision was created. Existing verified revision-10 rollback was retained and a post-rev11 integrity-checked snapshot `phase50-a2v-post-rev11-20260921-081557` was created.

## 2026-09-20 - Phase50.A.2U latest Windows recovery
- Restored the actual latest Windows lineage (`f1b58645...`) instead of continuing from the divergent A2T worktree.
- Preserved all September 18 image/gallery/scroll/multiselect/SEO/screenshot fixes while porting only Social v5 / clickable Story notification behavior.
- Windows operator build is now v8.9.11 / build 2026.09.20.1.
- Image/SEO/Republish 74/74 PASS; Social/Buffer/Story 35/35 PASS; Qt and RUN_QT verification PASS.
- Pushed exact source candidate `d77dfd95f5d3a9a707f9ad03f2aacff9e69ac2e2`.
- Took a fresh atomic Catalog backup and reconciled #625 revision 9 without another Bridge import after current public verifier returned Product 200 + two media 200.
- Desktop .lnk/.cmd now launch `D:\projects\3DPrintHub-a2u-latest-windows\catalog_center\RUN_QT.ps1`; live window title verified as `3DPrintHub Catalog Center v8.9.11 - Qt 6`.
- No Production source/DB/migration/restart was performed.

## 2026-09-20 - A2Q Instagram SEO v4 sanitizer hardening
- Corrected social punctuation normalization so removed false-free copy cannot leave a literal \`\\1\`.
- Expanded false-free filtering across Caption/hashtags/ALT/Story for Persian \`رایگان/مجانی\` and bounded English free-download/free-print/free-shipping forms; malformed residual hashtags are dropped.
- Added focused regressions while preserving unrelated words such as \`Freestyle\`.
- This is a Windows/Social WIP change only; canonical Windows full regression is still required and Site/Production are unchanged.

## 2026-09-20 - Instagram Product SEO policy v4
- Product focus keyword and Product-specific keywords now outrank generic tags in the bounded hashtag set; maximum remains eight.
- Caption adds explicit 3DPrintHub.ir ordering copy while retaining Product SEO title/description, factual specs, nationwide-Iran shipping and UTM Product URL.
- Social-policy normalization removes false Persian free-print/free-download claims before caption, hashtag or ALT generation.
- Direct Instagram receipts now persist ALT texts, hashtags and policy version like the Buffer receipt path.
- Social regression 32/32 PASS and Qt VerifyOnly PASS. The first run exposed only the intentionally stale v3 policy-version assertion; the changed-condition rerun is green.
- Product #625 revision 8 remains historical acceptance evidence and is not reposted.

## 2026-09-19 - Real Instagram launch + provider-compatible Buffer media hosting
- Product #625 / Site #39 revision 8 passed authoritative same-identity acceptance with exactly 3 active CC profiles, zero active legacy Variants and 2 current ProductImages.
- Fresh Production Chromium confirms Hero 50.9 has no legacy Slicebox shadow/frame element and no slider/wrapper/root box-shadow or border.
- Real Instagram Feed and companion Story are sent through Buffer with Product SEO caption, 2/2 ALT texts, 8 bounded hashtags, UTM Product link and nationwide shipping copy.
- Feed: https://www.instagram.com/p/DdepEh3if0N/ ; Story: https://www.instagram.com/stories/3dprinthub_ir/3989806967019651799
- Site-hosted PNG derivatives remained unreadable to Buffer despite owner-side HTTP 200 image/png; identical GitHub-raw bytes were accepted, isolating the provider-to-origin media-host boundary.
- Added deterministic github_raw Buffer media-host automation on the dedicated social-assets-buffer worktree/branch, SHA/source manifest, remote-head/public-MIME guards and Settings UI selection.
- Added media-host/commit audit to social receipts and append-only submitted->sent reconciliation without reposting.
- Canonical Site Product media and SEO filenames remain unchanged.

## 2026-09-19 - Failed re-publish identity resilience
- Failed Site imports no longer erase the last verified Windows Site Product/slider ids, revisions or successful ACK.
- Failure receipts and `product_sync_error` remain complete, so diagnostics are preserved without degrading the next retry into a new/unknown Product path.
- Added regression covering an existing Product #39/revision-7 style retry that fails parity and must retain its prior linkage.
- Site-publish regression 19/19 and Instagram/social adjacent regression 27/27 PASS.
- Production Hero 50.9 verification confirms the legacy Slicebox shadow DOM is absent and desktop/mobile runtime remains healthy.

## 2026-09-19 - Authoritative existing-Product re-publish replacement
- Existing Site Product identity remains stable, but the latest Windows `sales_profiles_json` now fully replaces the active Store Variant matrix.
- Historical/manual/MW-FIX/EP49/EP49-3F/removed CC rows are retained but deactivated instead of remaining orderable.
- Added fail-closed sync checks so stale active non-CC rows or profile-count divergence cannot return a false successful update.
- Added explicit Windows local-file image addition that persists/selects the image and marks an uploaded Product dirty; normal SEO finalization/public-media gates still apply.
- Real #625 root cause verified: revision 7 had three correct CC Variants plus two stale active EP49-3F Variants.
- Local verification: Server 15/15, Windows image 25/25, compile/check/no-drift PASS.

## 2026-09-19 - Buffer-compatible feed media derivatives
- Added Buffer-only PNG compatibility assets derived from verified canonical Product media and hosted at stable public URLs.
- Original Product media remains the Site/SEO authority; social receipt keeps both provider URLs and canonical `source_media_urls`.
- Feed preparation preserves normal aspect ratios, letterboxes extreme inputs without crop, and caps output width at 1440.
- InstagramCore prepares verified feed assets before Buffer submission; direct Instagram path is unchanged.
- Focused social regression 21/21 PASS.

## 2026-09-19 - ERR-49-177 reliable Windows Story headless rendering
- Real #625 social acceptance exposed a Windows-only Chrome launcher race before any Feed submission: a direct Python Chrome process could exit while the headless child still owned screenshot generation.
- Story rendering now uses an isolated Product/revision workspace under LocalAppData, a dedicated Chrome user-data directory, PowerShell `Start-Process -Wait`, stale-output removal and bounded output polling.
- Real #625 standard Story now renders as a nonblank 1080x1920 PNG of 1,178,712 bytes; sampled image has 6,984 colors instead of the previous near-white 18,240-byte output.
- Social/Story/publish gate 53/53 PASS; Qt VerifyOnly and diff-check PASS.

## 2026-09-19 - Public Product verifier supports compact canonical media
- Windows post-publish HTTP verification now discovers both legacy `/media/store/products/...` and compact content-addressed `/media/p/...` Product images.
- Private `/media/store/imported-models/...` working-media remains excluded from public acceptance.
- Added regression containing all three namespaces and proving only the two public Product namespaces are requested.
- Focused verifier 3/3 and maintained publish/social 40/40 PASS.

## 2026-09-19 - Unified Product pricing + Instagram Story category queue
- Windows Site publish refreshes selected Filament/Profile snapshots from current inventory immediately before Ready/Publish and recalculates the Product price range from the canonical Catalog formula.
- Flattened sales profiles now carry pricing strategy, support-cost multiplier and assembly fee into the Site payload.
- Windows Filament Core preserves Manufacturer independently from Brand in local save and Site sync payload.
- Instagram policy v3 keeps the verified primary Site Product image first, per-image ALT, SEO caption, focused 3-8 hashtags, tracked Product URL and explicit nationwide-Iran shipping copy.
- Companion Story remains on by default; runtime evidence now reports final IRANSans style ID `3dprinthub_instagram_gold_navy_v2_iransans`.
- Added approved Highlight classifier: category first, semantic fallback second. #625/toys-games maps to `اسباب بازی`; receipts remain `operator_required` because Buffer public API does not support Add-to-Highlight.
- Local gates: Windows pricing/social/story 19/19 PASS plus Manufacturer regression PASS; Server pricing/mapping 5/5 PASS and no migration drift.

## 2026-09-18 - Product #625 real re-publish acceptance
- Promoted Screenshot SEO/source-byte refresh at exact GitHub SHA `89931e8958b3a738fbfb4b8d65c099124aa24de0`.
- Fresh Catalog rollback backup passed integrity with 635 Products; Qt relaunched from the pushed source.
- Product #625 kept Site Product #39 / server asset 143 and advanced to revision 5 through the mature FTP/Bridge path.
- Bridge/readiness/FTP/preflight all PASS; ACK batch `desktop_catalog_v85_20260918_192011` reports `updated` and public HTTP checks PASS.
- Public main/gallery image bytes exactly match Local finalized WebP SHA256 values for both selected images.
- No duplicate Product identity was created.

## 2026-09-18 - Screenshot SEO defaults + changed-source media refresh
- Per-card SEO editor now fills missing single-image Alt/Title/Caption/Keywords from the Product semantic SEO identity.
- SEO metadata for an unselected Screenshot is retained without changing Site membership and remains non-publishable until explicitly selected.
- `اصلاح اسم و سئو` now defaults to all editable Product images when no temporary operation subset is selected.
- Publish readiness compares selected source bytes with stored `original_sha256`; previously-finalized images whose source changed are rebuilt before Ready/Send.
- Incomplete/unfinalized media still fails closed rather than being silently auto-created.
- Updated stale tests to current owner-approved 3-column gallery and ASCII `Standard` Profile identity; conservative exact PLA/PETG recommendation behavior remains intact.
- Gates: focused 41/41, current-contract 77/77, broad Windows 145/145, Qt VerifyOnly, compile, Django check, no migration drift and diff-check PASS.

## 2026-09-18 - Combined image name+SEO repair and reliable in-place re-publish
- Stage-3 automatic image action is now `اصلاح اسم و سئو`: temporary operation selection scopes the repair; otherwise all editable Site-selected images are repaired. Product semantic SEO and deterministic English numbered WebP naming run together.
- Removed the redundant standalone automatic `نام‌گذاری SEO` toolbar action; manual `SEO انتخابی`, Screenshot, delete, selection, Primary, Slider, recovery and mature filename authority are unchanged.
- Added a shared Windows dirty-state boundary for already-uploaded Products after direct operator/image mutations that previously bypassed StageCore. Existing Site identity is retained while `needs_update=1` reopens guarded re-publish.
- Server E2E now changes Persian title/description/meta SEO plus finalized image on second import and verifies the same Product PK/Asset PK are updated in place with no duplicate.
- Local gates: Image 22/22, Windows/Site 59/59, real importer 3/3, Profile/identity/admin-sync 23/23 PASS; compile/diff-check PASS.

## 2026-09-18 - Site-first Product/Admin/Profile/Instagram hotfix
- Removed ProductVariant inline from Product change pages; dedicated ProductVariant admin remains the editing surface. Benchmark dropped a 37-Variant change page from 781 to 60 queries and 1.399s to 0.075s in the isolated comparison.
- Reconfirmed current Product detail source already omits the obsolete Filament roll-price card block shown on older Production; updated the stale regression to require it absent.
- Profile identity normalization now keeps name/size ASCII-only; corrupt/Persian identity falls back to Standard or numeric cm dimensions. Real Product #625 resolves to Standard/Standard while preserving 64 material options.
- Instagram canonical media now supports real Site ACKs where images is a count and verified image URLs live under public_http_checks.images; product-slug filtering prevents unrelated verified images from entering a carousel.
- Gates: 17/17 Site/Admin, 82/82 Catalog/Instagram/Qt, 27/27 Hero, compile/Node/check/no-drift/diff-check PASS. Production unchanged pending dedicated tunnel recovery.

## 2026-09-18 - Image filename/four-row runtime promotion
- Pushed runtime `aaa5cb9f6d743becf3f1588501733ae835bd7451`.
- Took fresh integrity-checked Catalog backup `pre-image-seo-scroll-aaa5cb9-20260918-125436`.
- Launched canonical Qt behavior from a clean detached Git worktree at the exact runtime SHA to avoid touching concurrent Instagram/Buffer edits in the main worktree.
- Post-launch Product #301 confirms English filename + preserved Persian Alt/SEO title/caption/12 keywords.

## 2026-09-18 - Restore English image filenames and four-row gallery scroll
- Restored Product image filename planning to the mature source-title-first rule: English `source_title` -> ASCII SEO slug -> numbered WebP.
- Did not change image Alt, SEO title, caption, keywords, AI refresh, operator metadata overrides, Screenshot or image operations.
- Stage-3 large gallery now reserves at least four rows of scrollable canvas even when empty or sparsely populated.
- Product #301 read-only verification and 97/97 regression gate PASS.

## 2026-09-18 - Stage-3 3×3 runtime promotion
- Pushed and launched exact Windows runtime `a52cd52a18a119f9aa2940ebc00f588828d1a558`.
- Took fresh integrity-checked Catalog backup `pre-stage3-3x3-a52cd52-20260918-123308`.
- Visible Qt child is responsive. Production site was not changed because the dedicated reverse tunnel remains down.
- No cPanel/browser alternate Host access was used after the owner reconfirmed tunnel-only operations.

## 2026-09-18 - Stage-3 three-column / three-row compact image review
- Replaced the oversized two-column 780px image-card presentation with 3-column fixed 206px review cards.
- Preview is intentionally smaller; SEO filename and metadata remain visible; Previous/Next/SEO/Delete share one compact action row.
- Gallery min-height is 670px and a 9-card acceptance proves all three rows fit with filename/actions visible. Row four and later remain scrollable.
- No image business logic, SEO persistence, Screenshot, selection, Primary/Slider or delete/reorder behavior changed.
- Focused 4/4 and maintained 68/68 Qt suites PASS.

## 2026-09-18 - Compact Windows image UI + functional Tympanus Example-4 Hero
- Catalog Center presentation only: Stage-3 action controls collapsed to one row, Stage footer/navigation collapsed to one row, and image review viewport enlarged to a 650px minimum without changing callbacks or image workflows.
- Homepage Slicebox wrapper aligned to the official Example-4 settings while retaining 3DPrintHub Hero data and site background; extra Play/Pause UI removed.
- Fixed the real Slicebox zero-height startup issue by eager-loading all four Hero images required by the vendor plugin's all-images-loaded ready gate.
- Local Browser smoke: 4 live local media images, plugin ready, 416px slider, two visible 42px arrows, four dots, 5 cuboids/30 faces during transition, no browser errors.
- Windows 67/67 PASS; Hero selected suites 27/27 PASS; Node/Django/check/no-migration/Qt VerifyOnly PASS. Production unchanged.

## 2026-09-18 - Stage-3 scroll hotfix runtime
- Pushed runtime `00f16237cf27eea2cdf7bef97fa7cc140014c947`.
- Took fresh integrity-checked Catalog backup `pre-stage3-scroll-00f1623-20260918-112042`.
- Relaunched canonical Qt app; visible child window is responsive.
- Production remains unchanged.

## 2026-09-18 - Stage-3 gallery visible-height and wheel-scroll repair
- Kept the large two-column Product image cards and previews.
- Reduced only the gallery container minimum height from 720px to 560px so the Product Wizard no longer overflows the 1920x1080 working area.
- Added explicit wheel forwarding from the clickable image preview to the gallery scrollbar; one wheel notch now moves the gallery by the same 270px step as the viewport.
- Product #628 copy geometry after the repair: 544px visible gallery viewport with full 0..1880 vertical range.
- Regression 67/67 PASS; compile, scoped diff-check and Qt launcher verification PASS. No DB/schema/Production change.

## 2026-09-18 - Stage-3 image workspace runtime promotion
- Pushed exact Windows runtime `91d4c188aa57c125e46d45f39a70d913085dcf6c`.
- Took a fresh integrity-checked Catalog backup before launch and relaunched the canonical Qt application from the pushed source.
- Verified the visible Qt child window, clean runtime worktree, Catalog integrity, 635 Products and Product #628 persistent selection count 11.
- Production/schema/migrations remain unchanged.

## 2026-09-18 - Stage-3 image multi-select / SEO naming / Instagram cover
- Added a separate temporary bulk-operation selection layer so Edit/Delete can target any subset without changing Product Site-image membership.
- Enlarged the Stage-3 review cards/preview/scroll viewport and reduced control typography/height.
- Trusted real legacy numbered files in the Product images directory are now editable via safe `local://` identities; recoverable removal moves the file to `removed_images`.
- Image cards now foreground the deterministic SEO filename and keep the factual source filename as a secondary label.
- Operator SEO/renumber uses the existing finalizer in non-deduplicating mode with the current selected count; normal publication finalization keeps the previous dedup/default limit behavior.
- Instagram/Buffer feed media now places the verified Product main image first while retaining the rest of the verified carousel.
- Real-copy Product #628 isolated acceptance keeps 11 selected images, produces 11 unique SEO metadata names, preserves Primary, and leaves all 15 real local gallery files editable.
- Regression gates: 9/9 targeted, 80/80 maintained, 107/107 expanded; compile, diff-check and Qt launcher verification PASS. No migration or Production change.

## 2026-09-18 — Qt Product Screenshot visibility repair
- Fixed the Product Wizard Screenshot action appearing to do nothing even though capture succeeded.
- Preserved the mature capture implementation, `source-page-screenshot-<timestamp>.png` naming/crop behavior, SEO pipeline, button wiring and Product image sizing.
- Updated only the Qt image resolver so explicitly persisted manual Screenshot files remain visible beside numbered Product images and cannot be misidentified as numbered source slots.
- Added a focused regression reproducing the hidden-Screenshot/slot-stealing case; full maintained Qt/Gallery/Wizard/Screenshot gate 61/61 PASS plus launcher verify/compile/diff-check PASS.
- Copy-of-real Product #628 acceptance passed on backup `pre-screenshot-resolver-20260918-095910`; canonical Catalog, schema and Production were not changed by the acceptance probe.
- Runtime fix committed/pushed as `bab82e89e9e27722b8b1000a959b1161ee84e038`, Local/GitHub SHA matched, and the canonical Qt app was relaunched from that source with a responsive `3DPrintHub Catalog Center v8.9.10 - Qt 6` window.

## 2026-09-18 — Stage-3 owner correction: workflow restored, gallery enlarged
- Restored the mature Product image control layout/wiring, Screenshot path, recover-limit behavior, slider panel, AI visibility behavior and normal saved window geometry after the rejected `d564386` UI repair.
- Kept the requested change presentation-only: larger two-column Product image cards/previews and sufficient scroll content height.
- Reverted the rejected filename-label override completely; image filenames and Screenshot capture/naming now remain the mature pre-change implementation. SEO generation/persistence was not modified.
- The only runtime delta versus verified pre-`d564386` baseline `bf87c11` is Gallery card/preview sizing and matching scroll-content height. Filename/Screenshot implementation has zero diff; focused regression 60/60 PASS. No DB/migration/Production change.

## 2026-09-18 — Phase50.A.2L real Filament identity repair follow-up
- Relaunched the exact pushed A2L Qt runtime and verified Product #628 now exposes all 10 local images through the large two-column scrollable Stage 3 workspace.
- Audited the real 71-row Filament catalog: 63 historical rows have no factual Brand, explaining why a true full Site sync cannot honestly publish every row.
- Added explicit selected-row registered-Brand repair; the app never guesses a missing Brand and rejects values outside the Brand registry.
- After repair, affected rows immediately reuse the guarded Site sync path. Copy-of-real-Catalog validation repaired a known duplicate identity and preserved integrity.
- Follow-up Windows focused gate 28/28 PASS; maintained A2L scoped Catalog gate 57/57 PASS.

## 2026-09-17 — Phase50.A.2K Tympanus Slicebox + Filament UX
- Replaced the complete homepage Hero runtime with the official vendored Tympanus/Codrops Slicebox v1.1.0 engine and reference assets; removed superseded A2I/A2J runtime assets/runners.
- Added explicit destructive Hero reset command guarded by confirmation and exact four-slide postcondition.
- Removed redundant Product filament gallery; enriched four-step order wizard with material description, usage and examples.
- Added Windows Product/Profile filament Select All/Clear All, central registry-backed editing and material usage/example registry fields + site sync.
- Feature commit `71d34da...`; Production-based release `84d1a87...`; Production deploy pending dedicated tunnel recovery.
## 2026-09-17 - Windows Qt runtime handoff and Production Store cleanup
- Fixed operator launch path operationally by using the repository-owned `RUN_QT.ps1` / `qt_launch.py` runtime from exact GitHub SHA `b116a27...`; only one canonical Qt v8.9.10 window remains running.
- Preserved unrelated unfinished Social/Buffer changes on separate GitHub WIP branch `ea8a156` instead of mixing them into Product runtime.
- Re-verified Product re-send/update/recreate behavior, including Profile/Filament/print-time propagation, 5/5 focused PASS.
- Took fresh Catalog and Production rollback backups, reset old/test Store Products to zero with the canonical guarded Store-reset contract, and preserved source/master/portfolio data.
- Re-seeded four safe A2J Hero slides and verified public Home + 3D Hero CSS/JS + UTF-8 rendering.

## 2026-09-17 - Explicit Qt operator launcher + close-without-save guard
- Added `catalog_center\RUN_QT.ps1` as the repository-owned operator entrypoint for the modern `qt_launch.py` runtime and canonical Catalog SQLite root.
- Kept `RUN.ps1` and `RUN_DEBUG.ps1` unchanged as intentional legacy `launch.py` rollback/side-by-side launchers, eliminating ambiguity about which Windows UI is being started.
- Removed implicit ProductStudio save-on-window-close so merely opening/hydrating and closing the legacy workspace cannot persist UI-derived/default values; explicit Save/Stage/Publish actions remain authoritative.
- Added regression coverage for launcher separation and close-without-save behavior. Product republish contracts remain intact: explicit requeue, same-identity update, Site-404 recreation, and changed Profile/Filament/print-time propagation. Corrected focused gate is 40/40 PASS; Qt launcher verify, touched compile and diff-check PASS. A stale broader harness named two retired test modules and is documented as ERR-49-151 rather than treated as runtime failure.
- Pre-change rollback branch: `backup/pre-windows-qt-operator-launch-20260917` at `6a3a51aacdccff69a4999c4a470cb10807ceb648`; Production unchanged by this Windows slice.

## 2026-09-16 - Qt Product image reorder + SEO renumber continuity
- Added explicit `قبلی` / `بعدی` controls below trusted selected image cards in Product Wizard Stage 3.
- Primary image remains the mature fixed slot-1 authority; secondary selected images can be reordered without changing Primary or Slider identity.
- Reorder preserves Alt/image metadata by source URL, marks already-uploaded Products for guarded republish, and regenerates deterministic SEO WebP sequence through the existing finalizer.
- Display-only legacy image cards remain non-mutating; gallery row height was extended so the added controls remain reachable through the existing vertical scroll.
- Added regressions for Core ordering, Alt/metadata/Slider preservation, `needs_update`, SEO `-01/-02/-03` regeneration and real Qt button-click wiring.
- Local gates PASS: Phase49.3I.47 12/12; Image+Publish 27/27; broader Windows 87/87; touched compile and `git diff --check`.
- Rollback branch: `backup/pre-phase49-3i47-image-reorder-20260916` -> `551f70624536857ab36ba004404298abb503d180`; Production unchanged by this Windows slice.

## 2026-09-15 - Product Wizard direct publish + real Production acceptance
- Added direct single-Product Ready and Site Send actions to Qt Product Wizard Stage 7 while reusing the mature Batch/FTP/Bridge/HTTP publisher.
- GitHub runtime `6e306e5353a6d6cd9d434894870839e533fa9622`; Windows Catalog Center relaunched from that SHA.
- Real #628 acceptance PASS: Site Product #21, 190 orderable Variants, 2 Product images, public media/page HTTP 200, browser Cart Variant 1837; no test order delivered.
- Fresh rollback sets: Local Catalog `product628-prepublish-20260915-135143`; Production `20260915-135005-product628-prepublish`.

## 2026-09-15 - Windows Product Wizard direct site publish hotfix
- Added direct `Ready this Product` and `Send this Product to Site` actions to Qt Product Wizard Stage 7.
- Single-Product publish uses the existing guarded publish Core: factual preflight, finalized SEO WebP package, receiver readiness, FTP, Bridge import, strict ACK and public HTTP verification.
- Operator sale/Product intent is never auto-invented; locked Stage 7 is not rewritten when values are unchanged.
- Real Catalog diagnostic: 635 Products, 15 Ready, 12 currently publishable; Site readiness true/no blockers; FTP PASS.
- 71 related regressions PASS.

## 2026-09-15 - Phase50.A.3 ZarinPal current API compatibility
- aligned default live ZarinPal request/verify/StartPay hosts with the current official `payment.zarinpal.com` v4 contract;
- Verify payload now sends `merchant_id`, exact provider amount and `authority` only; request currency remains a stored amount-reconstruction fact;
- added explicit live/sandbox endpoint regressions and no-currency Verify regression;
- payment security/idempotency suite 17/17 PASS, Django check/no-drift/payment audit/diff-check PASS;
- Production payment remains intentionally disabled with no Merchant ID and no payment data mutation;
- added guarded reverse-tunnel deploy runner with exact baseline/live-target/backup/TLS/AST/runtime/public gates and no migration/DB write/collectstatic/gateway enable;
- broad Store 6F/9E failures were reproduced identically on pre-patch baseline and recorded as unrelated regression debt.

## 2026-09-15 - Client handoff Production closeout
- verified Local/live-GitHub/Production exact clean `b1caeba0f20e711b29dfa9e0ff92a2f5186fb08d`;
- verified authenticated reverse-tunnel Host execution, correct MySQL DB, empty migration plan and receiver readiness;
- verified deploy rollback bundle `20260915-094656-phase50-client-handoff` from pre-deploy `70a74e6...`;
- verified Store reset rollback set `20260915-094827-store-product-reset`, real gzip DB dump, manifest and 71/71 media hashes;
- confirmed Production Store is already empty (Products/Variants/ProductImages/linked assets all zero) while Hero/master/source/Portfolio data remains present;
- real Chromium Production QA PASS: Home 200, Hero 50.3.0 desktop 7-cuboid 3D transition + cleanup, mobile 390px fallback/no overflow, Store 200 with zero Product cards and empty state;
- no repeat reset/deploy was performed after detecting the already-completed live state.

## 2026-09-15 - Host transport diagnosis before client handoff
- Diagnosed dead 3DPrintHub reverse-management transport without touching other project tunnels.
- Verified Host/Windows tunnel public-key fingerprints are identical.
- Verified private watchdog state stopped updating and final tunnel log ended with reset/broken pipe.
- Verified FTPS is file-only, stored FTP credential is rejected by cPanel API, and repository has no automatic cPanel/GitHub deploy hook.
- Production source/database/store remain unchanged pending restoration of the authorized 3DPrintHub Host execution channel.

## 2026-09-15 - Client handoff deployment gate
- Added dedicated `phase50_client_handoff_deploy.sh` for exact clean Production baseline `70a74e6...`.
- Deployment remains GitHub-first, ff-only, no-migration, backup-gated, collectstatic/restart/HTTP verified.
- Local Hero 50.3.0 browser QA confirms full-bleed desktop and native 3D cuboid transition with mobile fallback.

## 2026-09-15 - Client handoff Store Reset + Hero 50.3.0 candidate
- completed a fail-closed authenticated Store Reset API for imported Catalog Products only;
- reset preserves source ImportedPrintAsset records, master Material/Quality/Color/Brand data, Portfolio, Homepage Hero slides and historical commerce records; protected/manual/inventory-conflicted state blocks deletion;
- added `scripts/host/phase50_store_reset_prepare.py` to create exact live-count manifest plus checksum-identical Product-media rollback copies under an approved backup root; reset still additionally requires a verified real MySQL gzip dump;
- upgraded the pending Hero from flat segmented flips to true four-face 3D cuboids with randomized horizontal/vertical orientation, odd 3/5/7 slice counts, dispersion and full-bleed desktop presentation; mobile/reduced-motion keep the mature fallback;
- preserved SSR Hero title/description/alt/Product link authority and existing managed Hero data;
- Site→Instagram workflow now explicitly publishes/verifies the Site Product URL before social delivery; token remains in Windows Credential Store and live Instagram cannot run without configured Professional credentials;
- added ambiguous Bridge-import timeout reconciliation by exact batch UUID instead of blindly resubmitting the same import;
- local acceptance: Store Reset+Hero 8/8 PASS, broader Qt/Publish/Instagram/SiteConnection 57/57 PASS, compile/Node/Django/no-drift/empty-plan/diff-check PASS;
- Production not yet mutated; reverse Host loopback 22024 must be restored and Host state reverified before GitHub-first deployment/reset.

## 2026-09-14 - ERR-49-144 initial GitHub CI contract correction
- Pushed runtime/docs checkpoint `1a5ba6a...`; three workflows passed and Qt6 runtime CI exposed one stale test expectation.
- The failed test still required the superseded three-large-column image layout and failed only on `4 != 3`.
- Updated the parity test name/assertion to the accepted four compact columns; exact failed CI suite now passes 23/23 locally.
- Created checksum-identical Catalog rollback backup before launch and successfully launched the pushed Qt runtime with 6 routes / 11 actions / 11 cores.

## 2026-09-14 - ERR-49-144 Published lifecycle and factual local image gallery
- Published workspace now keeps uploaded Products visible after Local edits while the work queue still exposes republish work.
- Product gallery image counts/cards are based on real locally-displayable files, not every raw source URL.
- Legacy numbered local images can render through a display-only compatibility layer; strict publish mapping remains unchanged.
- Unmapped legacy display-only cards cannot change selection/primary/slider/SEO/delete state.
- Product image gallery is compact four-column again.
- Real Catalog acceptance: Published=19; #33=16 displayable files from 60 source URLs; #34=25/60; modern #63/#628/#634 remain 2/2.
- Focused + adjacent Qt/Crawl/Publish suites: 77/77 PASS; no migration or Production mutation.

## 2026-09-14 - Catalog publish diagnostic integrity / Product #303 preview
- restored the canonical Sales Profile blocker message after Windows encoding corruption;
- added exact regression preventing future `????` diagnostic corruption;
- focused Catalog publish suite 11/11 PASS;
- audited all approved non-uploaded Catalog Products on a copied SQLite database; #303 is the only candidate with AI-fixable-only missing data;
- preview-only #303 repair reused finalized image keywords and passed Content/Images/publish-media/publish-gate checks without mutating the canonical Catalog.

## 2026-09-14 - Product #62 canonical Profile repair and sales acceptance
- Added no new source schema or migration; used the existing canonical CommerceCore/Profile ledger runtime.
- Repaired Catalog #62 with verified fixed-price 500,000 Toman, 138 g / 180 min, PLA E-Sun white offer with one real roll.
- Preserved Host asset 140 and Site Product 18 identity; republish returned published=1 / failed=0 and visible/orderable true.
- Public Product and Product-owned WebPs return HTTP 200; Variant API exposes orderable Variant 884 at 500,000 Toman.
- Chromium default-selected Variant 884, enabled Cart and emitted variant_id=884 / quantity=1; request was intercepted before server delivery.
- Products 16/17/18 are now sales-ready. Product 19 remains non-orderable pending stale-public deployment and factual black-matte stock.

## 2026-09-14 - ERR-49-138 stale-public orderability
- Already-public Products that fail current Store orderability are now deactivated and noindexed instead of remaining stale-public after a transaction rollback.
- Catalog importer marks a committed non-visible republish as `publish_incomplete` and does not increment published Product count.
- Added regression proving stale active non-orderable Product is deactivated. No migration or dependency delta.

## 2026-09-14 - ERR-49-135 orderable publish contract
- Added Desktop fail-closed requirement for canonical sales Profile data before Product FTP/publish.
- Added shared Store `variant_is_orderable()` contract and reused it in Variant API plus Catalog visibility.
- Store visibility now requires at least one actually orderable active Variant, not only an active/priced Variant.
- Added regression coverage for missing canonical Profile and active/priced-but-nonorderable Variant.
- Added guarded no-migration Production runner from exact `6569e5a...` baseline.
- #62/#84 are not considered sales-ready until canonical Profile repair + republish + live Cart acceptance; #628/#634 remain accepted.

## 2026-09-14 - Bounded sales publication accepted
- Production owner-license hotfix verified at `6569e5a9ec7e75da7185b851fc6eea82cd7fc0ea`.
- Product #628 and #634 successfully republished to Site Products #16 and #17.
- Both strict ACK/public HTTP/media visibility contracts PASS; Local sync errors cleared and rows moved to uploaded.
- Browser QA: Variant 651 = 360,000 Toman; Variant 775 = 560,000 Toman; Cart POST wiring PASS without server-side test order creation.
- Added rollback-grade SQLite backup `phase50-owner-license-retry-20260914-141227`.

## 2026-09-14 - ERR-49-131 owner-license publication parity
- aligned Host importer, fixed-Product conversion and Store visibility with the existing explicit `source_license_owner_approved` authority;
- preserved raw source `commercial_status`/license evidence instead of rewriting `review` to an allowed value;
- retained fail-closed behavior when neither owner approval nor an allowed raw commercial status exists;
- added positive owner-approved-review and negative unapproved-review E2E/visibility regressions;
- added guarded no-migration/no-DB-write/no-collectstatic Production runner from verified `44a7be9...` baseline.

## 2026-09-14 - A2I + Bridge public-media Production verification
- Deployed exact GitHub commit `44a7be91057c60891960fbb9d9b4f53780273c33` from Production baseline `443d1b70...` with verified rollback bundle/environment/static evidence.
- Collected and hash-verified A2I CSS, A2I JS and mature Hero engine; restarted Passenger; Home/Store/Bridge/readiness/new assets all HTTP 200.
- Verified Product #15 exposes only Product-owned public WebPs; Product #63 stored strict ACK confirms public visibility and HTTP success.
- Real browser QA: seven desktop Hero slices with cleanup, mobile fallback at 390px, canonical Variant 618 + 2,303,200 Toman price, and intercepted Cart POST without server mutation.
## 2026-09-14 - Phase50.A.2I combined deploy gate
- Added `scripts/host/phase50_a2i_bridge_hero_combined_deploy.sh` for the exact Production `443d1b70...` -> current GitHub promotion.
- Runner combines ERR-49-125 Product-owned Bridge media correction with A2I Hero static deployment, verified backups, collectstatic hash checks, restart and authenticated/public verification.
- Local syntax/compile/focused Django/no-drift/empty-plan/delta safety gates PASS; Production unchanged pending GitHub promotion.
## 2026-09-13 - A2G Bridge media hotfix deploy gate
- Added `scripts/host/phase50_a2g_bridge_media_hotfix_deploy.sh` for the ERR-49-125 serializer promotion from exact Host baseline `443d1b70...`.
- Runner is no-migration/no-DB-write/no-collectstatic, creates verified source/.env rollback evidence, uses explicit live GitHub/FETCH_HEAD + ff-only promotion, and verifies authenticated Product #15/Hero public WebP media after Passenger restart.
- Local bash syntax, `git diff --check` and forbidden-command contract scan PASS.

## 2026-09-13 - Bridge Product media ownership regression fix
- Unified Product/hero Bridge payloads now resolve image URLs from Product-owned public media instead of imported working-media.
- Imported image IDs remain stable for Desktop selection/sync identity.
- Resolution order: matching ProductImage basename -> Product main image -> safe HTTP(S) source fallback.
- Added regressions proving Product/hero payloads do not expose `/media/store/imported-models/`.
- No migration, pricing, stock, Product-data or public-routing expansion.
- Local focused gate: 31 tests PASS; compile/check/no-drift/diff-check PASS.
## 2026-09-13 - Phase50.A.2H Storefront showcase polish
- added a dedicated professional Hero product stage with separate image/copy composition and responsive mobile stack;
- improved guided configurator price presentation while preserving server-authoritative Variant price/stock/facts;
- collapsed the first-visit theme chooser into an accessible default-closed toggle with click/Escape behavior;
- preserved all existing theme choices/persistence;
- synced stale Local-only Django SQLite through existing Website 0024 + Store 0041/0042 only after a checksum-identical backup; Production DB untouched;
- Django/no-drift, Node 8/8, Playwright responsive, JS parse, diff-check and real 1440/1024/390 Home browser QA PASS;
- known desktop/tablet page-wide overflow is from unrelated mature sections, not the new Hero.

## 2026-09-13 - Reverse tunnel E2E + Phase50.A.2G Production verification
- ff-only promoted reviewed reverse-management ops/docs to Production with verified rollback bundle `/home/sfkilvrs/3dprinthub-deploy-backups/20260913-094206-reverse-tunnel-onboarding`;
- established Host outbound SSH/443 -> dedicated Windows `PrintHubTunnel` -> loopback `22024` -> Host authenticated bridge `22224`;
- proved Windows OpenSSH accepted the Host `89.39.208.237` public-key connection and both bridge/tunnel processes are running;
- protected operator token was transferred outside Git/chat into the Windows local security boundary;
- authenticated Host identity/worktree proof PASS at exact `d7cf71dceca95e191a118336c7004683083278ee`;
- repository Production read-only audit PASS: Python 3.12.13, Django 6.0.7, exact MySQL DB, Store 0036-0042 + Website 0024 applied, no model drift, empty migration plan, storage/schema/prerequisites healthy;
- in-process and public publish readiness PASS with no blockers; public Home/Store/A2G JS/CSS and authenticated Bridge endpoints HTTP 200;
- A2G is now `PRODUCTION_VERIFIED`; one real Product E2E remains before acceptance/bulk publish;
- no DB migration/write, Product/media mutation, collectstatic or Passenger restart was performed by tunnel onboarding.

## 2026-09-13 - Reverse Host management transport based on Asal proven standard
- imported the Asal loopback-authenticated command bridge/operator scripts byte-for-byte;
- added a 3DPrintHub runbook and shared-cPanel Host bootstrap runner;
- prepared dedicated Windows non-admin `PrintHubTunnel`, remote-forward-only policy and firewall restriction for `89.39.208.237/32`;
- reserved Windows loopback `22024` and Host bridge loopback `22224`;
- verified Python compile, Git Bash syntax, PowerShell parse, no-DB/no-deploy bootstrap contract and Asal hash parity;
- no database migration, Product/media mutation or direct Production source edit is part of this transport work.

## 2026-09-12 - Phase50.A.2G Publish-ready Product media + responsive order wizard
- fail-closed Ready/Publish unless every selected Product image is a current finalized SEO WebP with complete metadata/signature/SHA;
- Batch packaging now copies the exact final SEO WebP name and bytes and no longer falls back to original/download media during publish;
- real Django importer refreshes explicit current-Batch media only when bytes differ, preventing stale media and duplicate storage suffix/revision churn;
- manifest desktop_product_id now reaches canonical Profile sync on first import;
- Storefront wizard adds four-step progress/guidance, active/completed/ready state, keyboard navigation, touch targets and desktop/tablet/mobile responsive behavior;
- regression: Catalog 10/10, Django 16/16, Node 8/8, Playwright responsive suite, compile/check/no drift/diff check PASS;
- A2G no-migration Host runner syntax/no-migrate/exact-delta contract PASS;
- Production remains unchanged at `7d0b3df...` pending commit/push and clean-head gate.

## 2026-09-12 — Phase50.A.2F PRODUCTION VERIFIED

Status: `PRODUCTION_VERIFIED`.

Production deployment completed successfully from recovered baseline `e12fdaf281f7e08013e54c7cf936f8275127ab2b` to exact GitHub commit `7d0b3df03c3657106ebaf86d5f9123ba262495a5` using `scripts/host/phase50_a2f_storefront_production_deploy.sh`.

Verified Host evidence: MySQL `sfkilvrs_EmiAdmin_3dprinthub`; required Store 0036–0042 + Website 0024 migrations present; migration plan empty before and after promotion; publish-readiness ready=true with no blockers; verified source/.env/static backup at `/home/sfkilvrs/3dprinthub-deploy-backups/20260912-182234-phase50-a2f-storefront`; ff-only Git promotion; collectstatic; Passenger restart; Home/Store/Bridge health/readiness/new JS/new CSS all HTTP 200; final Host worktree clean.

Guided customer ordering is now live on Production: size → color → compatible material → print quality → canonical ProductVariant → server-authoritative price/stock/weight/time → cart. Native Variant select remains fallback.

Next exact acceptance: one controlled Product publish from Windows Catalog Center to the now-ready receiver, verify Product/Profile/Variant/images/public Store/strict ACK, then enable bounded multi-product publish. In parallel continue Phase50 finance/payment/admin work after this Product-publish acceptance.
- 2026-09-12: ERR-49-115 ? A2F Production runner now recognizes reviewed root `PROJECT_CONTEXT.md`; first Host attempt had stopped safely before merge/DB write.
## 2026-09-12 — Phase50.A.2F production recovery revalidation and deploy guard

- Reverified Local/GitHub clean head `38458ce...`; canonical Windows gate passed with 139 + 34 + 68 tests and checksum-backed Catalog data.
- Re-established secure explicit FTPS access to the cPanel account and read Production Git metadata without modifying source.
- Corrected stale Production assumption: Host source is `e12fdaf...`, not `5f6c...`.
- Live authenticated publish-readiness proves MySQL recovery complete: Store 0036–0042 + Website 0024 applied, schema complete, `ready=true`, no blockers.
- Added `scripts/host/phase50_a2f_storefront_production_deploy.sh`, a no-migration guarded deployment path with source/env/static backup, explicit FETCH_HEAD/ff-only promotion, collectstatic/restart and public/Bridge/static verification.
- No Production source, DB, media or static file was changed while preparing this gate.

## 2026-09-12 — Phase50.A.2F guided Storefront configurator
- recovered and inspected the existing dirty Local worktree instead of resetting it;
- added four-step size → color → material → quality progressive enhancement over canonical ProductVariant data;
- preserved native select/API-failure fallback and mature cart listener;
- fail-closed unavailable/out-of-stock options and ambiguous duplicate paths;
- added canonical material/quality/color/stock API fields needed by the browser selector;
- added responsive sticky mobile cart, keyboard focus and reduced-motion treatment;
- added Node state-machine regression and isolated Playwright real-browser regression including >100 Variant batching;
- Local verification: Node 8/8 PASS, Django 15/15 PASS, Playwright PASS, Django check PASS with known warning, no migration drift;
- no Production/Host/DB mutation.
## 2026-09-02 — Phase49.3I.53G
- recorded Production partial migration state: Website 0024 + Store 0037/0038 applied; Store 0039 failed before recorder commit; 0040–0042 pending;
- found duplicate schema declaration: ProductVariant.support_weight_grams already exists from Store 0033 and was incorrectly AddField'ed again by 0039;
- changed 0039 ProductVariant support weight to AlterField;
- added `AddFieldIfMissing` for genuinely new 0039 columns to safely recover a persisted MySQL DDL prefix;
- added `scripts/host/phase49_3i53_partial_0039_resume.sh` with exact recorder/schema forensics and fresh partial-state backup before repair;
- added focused migration contract test and real MySQL AddField idempotence probe;
- broad MySQL-from-zero test attempts were retired after exposing unrelated old/third-party migration limitations before the 0039 boundary;
- final Product Admin workflow `33666085743` PASS including real MySQL probe; Single Active AI `33666085841` PASS; Variant/Profile `33664796042` PASS on same migration implementation.

## 2026-09-02 — Phase49.3I.53F
- recorded that Production source fast-forward to `b372586a...` succeeded before the deploy paused;
- DB migrations/static/restart remain unapplied;
- fixed Site bootstrap dependency on eager desktop AI transport imports;
- `ai.model_policy` provider client is lazy while preserving mature `AIProviderClient` patch seam;
- `ai.product_content` loads `AIContentService` only for explicit AI Generate;
- added Django-without-httpx startup regression;
- added exact `httpx==0.28.1` install/version/`pip check` gate to normal Production deploy;
- added `scripts/host/phase49_3i53_postmerge_resume.sh` for the current already-promoted source state;
- resume re-verifies valid rollback backup, creates fresh pre-migration DB backup, requires exact migration plan and completes receiver verification;
- first 53F CI exposed a compatibility test seam and was fixed before final PASS;
- Product Admin `33663316332` PASS; Single Active AI `33663316324` PASS.

## 2026-09-02 — Phase49.3I.53E
- fixed Production backup helper import context when executed from outside the repository;
- helper now requires `PHASE49_PROJECT_ROOT`, validates project markers and prepends the project root to `sys.path` before Django setup;
- deploy runner passes the verified Production root explicitly;
- self-test covers project-root/sys.path binding plus existing gzip round-trip;
- second Production attempt stopped before any merge/migration/restart;
- Product Admin CI `33661199115` PASS; Single Active AI `33661199159` PASS.

## 2026-09-02 — Phase49.3I.53D
- fixed Production MySQL backup compression: mysqldump stdout is now piped through the parent Python gzip encoder instead of being attached directly to a GzipFile descriptor;
- added `scripts/host/phase49_3i53_mysql_backup.py`;
- helper redirects stderr to a private file, removes partial output on error, verifies gzip magic and mysqldump/MariaDB dump signature;
- deploy runner extracts the exact helper from fetched GitHub target and still requires `gzip -t` + SHA256 before `PREDEPLOY_BACKUP_VERIFIED=YES`;
- first Production attempt stopped before merge/migrate when invalid gzip was detected;
- fixed CI self-test argv overflow by generating the large fixture in the child process;
- final Product Admin CI `33659707983` PASS and Single Active AI `33659707957` PASS.

## 2026-09-02 — Phase49.3I.53C
- accepted clean Production read-only audit: MySQL DB correct, Store 0036/Website 0023 applied, Store 0037–0042 + Website 0024 pending;
- corrected effective Production Media path evidence to `/home/sfkilvrs/3dprinthub/media`;
- recorded active Material=13, PrintQuality=5, Bridge token configured, disk/inode headroom and mysqldump availability;
- added `scripts/host/phase49_3i53_production_deploy.sh`;
- deploy runner verifies live target/ancestry/exact migration-file delta and baseline migration recorder;
- creates checksum-verified Git bundle, environment, pending-import and MySQL backups before source promotion;
- validates exact target MigrationExecutor plan before applying migrations;
- post-migration requires in-process publish readiness, collectstatic, Passenger restart, authenticated Bridge health/readiness and public home/store HTTP 200;
- no automatic destructive rollback on failure; verified restore evidence is preserved;
- deploy-runner CI `33658713537` PASS; Single Active AI `33658713594` PASS;
- rollback branch `rollback/phase49-3i53-predeploy-host-198fa8e-20260902` created at actual Host baseline.

## 2026-09-02 — Phase49.3I.53
- added authenticated Site publish-readiness endpoint;
- readiness checks required migration rows, required receiver schema, pending/media storage, Bridge token configuration and active Material/PrintQuality prerequisites;
- Desktop bulk Product publish checks readiness before FTP/package/import;
- Settings now distinguishes Bridge connectivity from receiver publish readiness;
- missing readiness endpoint on an older Site is reported as blocked receiver rather than broken Bridge;
- added Production read-only audit script under `scripts/host/`;
- audit checks repository/HEAD/worktree/runtime/MySQL/migrations/storage/prerequisites/disk/backup tooling and performs no deploy/migration/restart;
- no new Django migration;
- Site `33652584032`, Variant/Profile `33652583964`, audit contract `33652996666`, final Qt `33653229142`, Single Active AI `33653229219`, Portable `33653229400` PASS;
- Portable regression 235 PASS; artifact `9855771656`; SHA256 `a6bebd3c10a56aac1c65a58d5ffb1029382e98c7b0782a4b034a315e60c2f1ed`;
- ERR-49-104 fixed the pre-deploy Bridge-only test/compatibility regression;
- Production/Host/MySQL not changed.

## 2026-09-02 — Phase49.3I.52G
- added persistent redacted acquisition JSONL under the Catalog data root;
- added `پوشه لاگ Crawl` and recent method/quality/image diagnostics to Qt History/Report;
- separated `discovery_ready` from full Product acquisition success;
- added Product quality validation for meaningful title/data and actual local images;
- added adaptive failover across rich, network capture, classic exact, public HTTP and attached Chrome;
- reused mature resilient image fallback;
- successful method is preferred for following Products;
- added circuit breaker after all distinct methods fail or Product URL/source is invalid;
- later selected rows remain untouched/new after circuit break;
- permanent Crawl `بازیابی دیتا + عکس` opts into adaptive recovery;
- fixed ERR-49-102 and ERR-49-103 compatibility regressions;
- runtime `bf1fafdb38233a23e13a5715ffac72f772412005`: Qt `33644903042`, Single Active AI `33644902970`, Portable `33644902962` PASS;
- dedicated suite 27 PASS; portable regression 235 PASS; artifact `9852476786`; EXE SHA256 `f3e0bce9e5d3b40317b5fd37cff8a5fc6ff1d5a2cef6f5b1bf84dc6f6699c310`;
- no migration, destructive media operation, Host change or Production write.

## 2026-09-02 — Phase49.3I.52F
- added permanent Crawl `انتخاب ناقص‌ها` bulk selector;
- added 5/10/20 image recovery target;
- added `بازیابی دیتا + عکس` for selected Crawl rows;
- complete Product + sufficient local images are reused without network;
- incomplete existing Products use mature safe source refetch;
- orphan terminal identities can be explicitly rebuilt from Product URL;
- URL slug supplies readable identity before receive;
- split crowded queue actions into separate selection/data rows;
- renamed queue status recovery to `بازگردانی به صف`;
- Qt `33637452385`, Single Active AI `33637452588`, Portable `33637452243` PASS;
- 227 portable regressions PASS; artifact `9849484898`; SHA256 `f0150359fd36c7ead84599ccd0b799797ed48e85e4c6eac1d191abc3f0315a64`;
- no migration, destructive media operation, Host change or Production write.

## 2026-09-02 — Phase49.3I.52E
- fixed permanent Crawl inventory image misses from mature refetch/source-refresh sibling folders;
- added read-only lookup for `_refresh_latest`, `_refetch_*`, and `_bulk_refetch_*`;
- fixed lazy MakerWorld card Preview extraction for srcset/picture/data-lazy/background-image sources;
- duplicate Search reruns now refresh candidate Preview evidence without duplicating identity;
- Qt shell reports `Phase49.3I.52E`;
- Qt `33632062812`, Single Active AI `33632062877`, Portable `33632062880` PASS;
- 223 portable regressions PASS; artifact `9847317893`; SHA256 `f9bcfc0770a38b0c8eabc9f2deab7c05b2c4d8b577fd25eb540ea9b65f7dc970`;
- no migration, destructive media operation, Host change or Production write.

## 2026-09-02 — Phase49.3I.52D legacy image-path + Crawl numeric layout repair
- verified mature Windows storage: `D:\projects\3dprinthub-catalog-manager\collected\<source>\<external_id>\images`, with `seo_images` preferred when present;
- fixed Qt Crawl cards that could report no Preview while real downloaded files already existed in the mature collected tree;
- added read-only identity-path image discovery even when a Crawl row is not linked to a Product id yet;
- added case-insensitive source-code Product matching for legacy `MakerWorld`/current `makerworld` drift;
- cards and table now report the real local image count for those rows;
- live single-candidate review can show mature local images without Product linkage;
- retained `D:\projects\3dprinthub_catalog_center\collected` only as a secondary read-only compatibility fallback;
- fixed RTL QSpinBox crowding for requested Product count and per-Product image limit using LTR numeric controls, safe width/padding and explicit grid spacing;
- runtime `a18b6f3036d41271cf3e8c1d9a0dfd8c271a53ce`: Qt `33628825851` PASS, Single Active AI `33628825772` PASS, Portable `33628825715` PASS;
- Portable release regression 221 tests PASS; artifact `9846044486`; EXE SHA256 `c08aa1e9d12926203cb59c580aab6c606c2b0e259ad83df37aa3b3abec86c22a`;
- no migration, destructive file operation, Host change or Production write.

## 2026-09-02 — Phase49.3I.52C Crawl visual review recovery
- restored Preview-first visual cards in Add Product/Crawl so Product title/thumbnail is visible before full receive;
- current Search now clears the previous live result workspace and remains scoped to that Search/Listing URL;
- cards report image state/count and full receive emits per-image progress such as 3/5 and 5/5;
- selected collected Product now exposes an actual local image review strip with total image count and local-displayable file count;
- shortened dense receive/bulk button labels while keeping complete behavior descriptions in tooltips;
- corrected the Qt sidebar/About phase identity from stale `49.3I.48` to `49.3I.52C`;
- restored explicit Qt MultiSelection, select-all/clear and selected-count feedback for current Search and persistent Crawl inventory;
- selected transfer now returns Product ids and navigates to Products; already-collected identities route to their existing Product;
- persistent Crawl inventory reuses discovery-candidate/legacy Preview title and thumbnail evidence;
- added explicit Product source action `دریافت داده و عکس بیشتر از لینک محصول` with source-only safe recovery that preserves operator Persian content, final price, sale approval and publish state;
- added dedicated 3I.52C regression coverage;
- fixed ERR-49-097: Portable release regression now installs the Qt requirements required by the new Qt test instead of dropping the regression;
- final Qt run `33625988684`, Single Active AI `33625988674`, and Windows Portable `33625988663` PASS on `f43c7aa464948832ba349543f94c94498490ab25`;
- Portable release regression: 218 tests PASS; artifact id `9844889166`; EXE SHA256 `cd54431bd29bad76990c17eb818671e3f32c4d53a244cdc07132f5d93a532f4b`;
- no Django migration, Host change, Production deploy or Production MySQL write.

## 2026-09-02 — Phase49.3I.52 / 3I.52B
- made Django Admin a canonical fallback Product authoring surface using the existing Product/Profile/Variant commerce authority;
- added root `ai/` shared Product AI policy/playbook, Persian Structured model probe, verified-free-first/low-cost fallback policy and environment-only Host secret boundary;
- added Preview-before-Apply Site AI that cannot change operator-owned pricing/stock/material/color/license/factual production data or publish state;
- completed Bridge Product payload parity for source identity, category slug, pricing strategy, pricing inputs and technical summary;
- added bounded Product offset pagination for Site→Windows reconciliation;
- added Windows `دریافت تغییرات سایت`, Site-only non-publishable Local mirrors and revision-aware clean-update/dirty-conflict behavior;
- added fail-closed Site revision verification before republishing an existing Product;
- preserved the mature Batch 8.5 → FTP → Bridge → public HTTP verification path after the revision gate;
- owner Local gate is now `49.3I.52.1`;
- ERR-49-096 records the missing timestamp import and Bridge test-fixture correction;
- final tested source `6d19bed7659b9ca4cd54ff1ffd1323ec423bea6a`;
- Qt `33619876564`, Portable `33619876411`, Single Active AI `33619876317`, Admin/Bridge `33619558467`, Variant/Profile `33619558562` PASS;
- no new Django migration, no Production MySQL write, no Host/Production deploy.

## 2026-09-02 — Phase49.3I.51
- enlarged Product image review while preserving multi-image selection and bulk image actions;
- restored fixed source-page open behavior and MakerWorld URL Source auto-detection in Crawl;
- added live Discovery/Receive result presentation;
- added explicit `پیش‌فرض` Profile fallback using 100 g model, 50 g support and 60 min when source production facts are absent;
- fallback Profile now matches all active PLA/PETG-family Filaments, including variants such as PLA-CF/PLA Silk/PETG-HF;
- split Filament management into Filaments / Materials / Brands / Colors;
- changed Filament Brand/Material/Color identity to managed registry selection and added rename propagation/collision guards;
- preserved optional Filament/Brand/Material descriptions plus Material reference price/kg;
- restored Filament description through Qt table/edit normalization;
- added selected/full Filament Site Sync over the existing authenticated Bridge without requiring FTP;
- full Site reconciliation includes inactive Local Filaments;
- added persistent Site FilamentBrand and optional Brand/Material/Filament descriptions;
- kept Material print/supervision rates visible in Django Admin;
- Bridge contract is `phase49-filament-library-v3`;
- candidate migrations added: `website.0024`, `store.0042`;
- final Windows Qt `33611776817`, Portable `33611776806`, Site/Admin/Bridge `33611936196`, and Single Active AI `33611936216` PASS;
- Production/Host/MySQL remain untouched.

## 2026-09-02 — Phase49.3I.49
- added guarded multi-select Product ready/publish actions to Qt Products;
- added reusable bulk publish service over the mature Batch 8.5 / FTP / Bridge / public HTTP verification path;
- successful ACKs now move Local Products to the existing Published lifecycle state; failures never do;
- added explicit ready/published labels in Product Gallery/Table;
- completed full existing Slider presentation-field round-trip between Desktop, Bridge, ProductCatalogProfile and HomepageHeroSlide;
- reorganized ProductCatalogProfile and Hero Slider Admin around task-first content, responsive composition, motion/timing, publish and collapsed sync diagnostics;
- expanded owner Local gate through 3I.49;
- added dedicated Qt and Django regressions;
- Windows Qt run `33596830380`, Single Active AI run `33596830268` and Admin run `33596562467` PASS;
- no Django migration, Production deploy, Host change or secret migration.

# CHANGELOG

## 2026-09-18 — Phase50.A.2L owner QA media/filament/social/manual-payment local acceptance
- Enlarged Product Wizard Stage 3 to a two-column, scrollable, multi-select review surface with reachable controls for 5+ images and source-link recovery.
- Fixed source-media mapping/filtering so real Product images are displayed; Product #628 resolves 10 local MakerWorld images in the current runtime.
- Made full Filament Site sync fail-soft and added selected/all-active bulk operating-rate edits.
- Added conservative product-use material recommendation + explicit smart-selection UI and AI production Preview/confirm flow.
- Preserved Site-first Buffer Instagram contract, verified live connected channel, retained all verified media, tracked Product link, companion Story and approved gold/navy profile/Highlight base asset.
- Added dry-run-first Pasargad manual-payment seed and receipt operator notification across configured Telegram/WhatsApp/Email channels; admin review remains authoritative.
- Repaired stale Store test fixture contracts (`post` preset collision and shipping fee signature). Scoped acceptance is green; historical broad Catalog discovery debt is tracked separately.

## 2026-09-01 — ERR-49-088 Windows PowerShell 5.1 owner-gate repair
- fixed the Phase49.3I.47 Local runner ParserError caused by one non-ASCII Persian QA label violating the existing ASCII-only runner rule;
- runner is now `49.3I.47.2`;
- CI now rejects any non-ASCII byte and parses the owner gate under Windows PowerShell 5.1 before the existing `pwsh` parser/stdin regression;
- exact source `36a710953276aae99fa668f477ad5569f8dc23ba`: Qt full parity run `33511403943` PASS and Single Active AI run `33511403901` PASS;
- Production/Host/DB migrations untouched.

## 2026-09-01 — Professional specialist-commerce design architecture
- reviewed owner File Library constituent references for UX/IA, typography, design systems, brand identity, 3D UI and SEO/performance;
- added `docs/PROFESSIONAL_COMMERCE_DESIGN_ARCHITECTURE.md`;
- established IA-first, progressive-disclosure, restrained specialist trust, Persian typography, accessible state, server-rendered SEO and optional/lazy 3D principles;
- book framework examples do not replace the current Django architecture.


## 2026-09-01 — Phase49.3I.46 / ERR-49-086 Catalog lazy loading + acquisition parity

### Added
- incremental Product Gallery loading in 50-Product pages;
- incremental Product Table/Detail loading in 20-Product pages;
- incremental persistent Crawl inventory loading in 100-row pages;
- bounded Product/Crawl count/page APIs and planner indexes;
- restored Classic Isolated, Classic Exact, Network Capture, Chrome Attached 9222, Saved HTML, Browser DOM and Public HTTP acquisition choices;
- Chrome profile, 9222 launcher, multi-source harvest, public model-file option and source-refresh operations in Qt;
- source refresh history while preserving operator-owned editorial/pricing decisions.

### Changed
- Qt Product list surfaces use lightweight list projections rather than full Product payload reads;
- Product search/filter/sort is pushed to the database page boundary;
- Crawl page identity resolution is bounded to the displayed page;
- Gallery uses Qt batched layout plus `fetchMore` rather than eager full-list layout.

### Verification
- code `a659155da4a4a41e01e926b2ac1263a1756c24e6`;
- Qt Full Parity `33500317538` PASS;
- Windows Portable `33500317554` PASS;
- Single Active AI `33500317788` PASS.

### Safety
No Django migration, no Production/Host change, no destructive Catalog rewrite. Rollback: `backup/pre-phase49-3i46-catalog-lazy-acquisition-parity-20260901`.


## 2026-09-01 — Catalog Center 8.9.10 / ERR-49-085

### Added
- OpenRouter JSON-mode Product support with exact local JSON-schema validation.
- Persistent Qt Crawl inventory browser over existing `discovered_urls`.
- Product lifecycle + SEO readiness badges/borders.
- Bulk Product archive, reversible reject/tombstone and restore.
- Bulk Crawl queue add/reject/restore.
- Explicit Qt release markers for OpenRouter, semantic translation, final SEO WebP, Crawl inventory, Product lifecycle and Slider UX.

### Fixed
- bounded TLS/connect retry for transient OpenRouter handshake/connect failures;
- false equivalence between `response_format` and strict JSON Schema;
- semantically broken Persian lamp/Product titles such as the owner-reported Driftbloom example;
- `AI همه مراحل محتوایی` not reopening AI-owned finalized stages for explicit repair;
- Qt showing source/cache JPG/PNG instead of final SEO WebP;
- image SEO metadata edits not rebuilding the actual WebP/SEO filename;
- Stage 6 spin-arrow-heavy numeric input;
- hidden persistent Crawl records and unclear Product state;
- stale 8.9.9 release/version contracts after the 8.9.10 bump;
- Qt CI path filter now includes version/manifest/config/legacy-launcher contract changes.

### Verification
- runtime/package checkpoint `205ceff6b7033e2fcd6f03c25dc8a81720ae067d`;
- Qt CI-contract checkpoint `12284a255d27451b9160eeb48bc289f4f34fdc16`;
- Single Active AI `33488996741` PASS;
- Modern Acquisition `33488996767` PASS;
- Portable Release `33488996802` PASS;
- latest Single Active AI `33489296415` PASS;
- latest Qt full parity `33489296349` PASS.

### Artifact
`3DPrintHub-CatalogCenter-v8.9.10` — artifact ID `9793033040` — digest `sha256:68099747e151677fa355dcc4f0dad7d290a5f35ce8ad3ad5ff739dfba88e5533`.

Production/Host/Django migrations were not changed.


## 2026-08-31 — ERR-49-084 Product AI Link fallback + verified persistence
- isolated Product #309 MakerWorld 403 to the pre-Provider Link source fetch; changing OpenRouter models could not affect this failure;
- Link mode now falls back once to already persisted Product/Crawl evidence on explicit 403/429 instead of repeating the same blocked HTTP request;
- saved-data fallback remains grounded in existing source title/description/spec/category/author/license/metrics and does not invent operator-owned material/color/price/stock facts;
- added requested/effective source truth and a Qt status note when Link falls back to saved data;
- added pre-source scope guard so locked/no-work stages do not fetch the source or call a Provider;
- AI stage writes are now re-read and field-by-field verified before `changed_fields` can report success;
- all `openrouter/auto*` variable-router IDs, including `openrouter/auto-beta`, are rejected as deterministic Product defaults;
- regressions cover 403 fallback + real Stage-1 persistence, no-call locked scope, no-op DB write failure, and auto-beta rejection;
- code checkpoint `0c67fa30493d100b99ec37314586e0491ecbcda5`;
- CI `33409112402`, `33409112322`, `33409112381`, portable `33409112367` PASS;
- rollback `backup/pre-err49-084-ai-link-fallback-apply-verify-20260831`;
- no migration, Host, Production, secret or default-launcher change.

## 2026-08-31 — Phase49.3I.42C Classic + Hybrid acquisition controls + ERR-49-081 Local gate hardening

## 2026-08-31 — ERR-49-082 OpenRouter Product Model Gate
- Added output-modality and product-purpose filtering to the live AI model catalogue.
- Separated native Structured JSON support from Tools/Tool Calling.
- Excluded media/music/audio/image/embedding/rerank and coding-specialist models from Product recommendations.
- Changed OpenRouter Product Structured requests to strict JSON Schema with `require_parameters=true`.
- Removed OpenRouter prompt-only JSON compatibility fallback for Product Structured work.
- Added persisted non-secret verified model capability profile and Product AI preflight.
- Improved Settings badges/details for JSON✓, Tools-only, coding-specialist and non-text models.
- Added regressions reproducing the Lyria and North Mini Code failures.
- Final verification on `0421bccff040ced53513625af95d05e0c8c27a9a`: Qt/Crawl/AI `33399095190` PASS; Single Active AI `33399095198` PASS; Portable `33399095224` PASS.
- Production/Host/Django migrations/default launcher untouched.


## 2026-08-31 — Phase49.3I.42C3 Add Product + OpenRouter/Crawl parity

- Restored the visible Add Product/Crawl workflow in Qt with Automatic, Search/Listing, Category URL, Site Crawl and Direct Product modes.
- Preserved Classic browser continuation and Hybrid structured-first acquisition over the mature 3I.43–45 engine.
- Added live AI model catalogue enrichment: free flag, internal Persian ranking, Structured/JSON hints and Provider pricing.
- Added model filters, per-run AI cost estimation/confirmation and a real Persian structured Product probe.
- Added diagnostic dialogs for AI/Crawl errors with execution context and detailed copyable text.
- Extended the repository-owned Local gate and Qt CI markers/tests.
- Verification: `33394215803` PASS; Single Active AI `33394215742` PASS on code checkpoint `ba3d1358d91aa78719f618630c290abf97ee8427`.
- No Django migration, Production, Host, default-launcher or media change.


- migrated live acquisition controls into Qt Operations over the existing ApplicationKernel/AcquisitionCore;
- preserved the old `Classic` Search-Link + browser continuation behavior rather than replacing it;
- added explicit `Hybrid` strategy using the mature 3I.43–45 robots/pooling/cache/Sitemap/freshness/unseen intelligence before browser fallback;
- added direct single-Product and Listing batch receive, requested Product count, per-Product image cap, retry-failed, safe stop, queue reset, progress and recent-run status;
- rich Product receive persists source title/description, author, license, category/tags/specs/snapshot and bounded selected images into the existing Catalog authority;
- classic continuation, hybrid browser avoidance, rich receive, listing-scoped pending queue and robots denial have dedicated regressions;
- 42C code checkpoint `3f7038b52723aa2b70cd12d4c1a617c50d0ad4d8` passed the Windows Qt/full-parity, portable and Single Active AI checks;
- owner Local then passed repo guard, checksum DB backup and dependency verification but the pasted Playwright probe failed because multi-line Python was sent through Windows `python -c` quoting;
- added repository-owned `RUN_PHASE49_3I42C_LOCAL_GATE.ps1` at `71c55010bc900e8d3c1afd7cea71441193db68eb`, using Python stdin and installing Chromium only for a real missing-browser error;
- added Windows CI syntax + PowerShell→Python stdin regression guard at `e6980fcfb2bdc72846e007e9d935290225dcb39e`; Phase49.3I.42C run `33386654632` PASS;
- Production, Host, Django migrations and default launcher remain untouched.

## 2026-08-31 — Phase49.3I.42B2 requested Product/Settings parity

- Added shared Qt parity cores for categories, stage state, commerce/Profile, Filament, AI providers and Site connection.
- Added Filament create/edit/deactivate with mature inventory/rate/preheat fields.
- Added Product list description + real sorting and Persian/source title visibility.
- Added Profile Matrix: size/dimensions × multiple weight/support/time rows × many Filaments/colors/prices.
- Added image dimensions/file-size/Alt/SEO metadata view.
- Added full Content/SEO, Source/License/Specs, homepage slider and readiness/publish editors.
- Added red/pending/green stage truth and explicit save/finalize/unlock.
- Added one process-wide AICore wired to mature Link/Saved Data/Screenshot and exact saved Provider/Model/key.
- Added AvalAI/OpenRouter/Google Gemini/OpenAI Provider Hub with searchable model list/test/default selection.
- Added FTP/Bridge settings/test with secrets retained in Credential Store.
- Windows Qt run `33369749205` PASS; Single Active AI `33369749123` PASS.
- Code checkpoint: `c3b0105eaa6c6141eb6d6d8463a96d547101564c`.
- No Django migration, Host or Production change.
- Qt live Scan/Crawl/Acquisition controls remain Phase42C; legacy launcher remains default.

# PROJECT CHANGELOG

## 2026-08-30 — Phase49.3I.42B1 Qt Kernel + first Legacy parity adapters
- owner accepted the Qt6 shell/menu direction but correctly rejected the missing legacy capability parity;
- added a long-lived `ApplicationKernel` and `CoreRegistry`;
- registered one Product, Image, Filament, Acquisition, Publish and AI core per process;
- established one shared AI engine boundary for future Qt callers;
- restored folder-style Product presentation in Qt with local-only thumbnails and a detail image preview;
- added the first real editable Wizard adapter for Stage-1 title/category with mature Stage-lock protection and explicit unlock;
- added real local Product image presentation in Stage 3;
- preserved legacy `launch.py`, mature SQLite and all existing business/domain implementations;
- code checkpoint `0b826dccabcb3d98d5f5b4cca6543d7547ff8773`;
- Qt6 Windows CI `33319343447` PASS;
- Single Active AI CI `33319343464` PASS;
- rollback `backup/pre-phase49-3i42b-qt-core-parity-20260830` → `3d32c2510ee0fee2c5929e35acc79c32bdb05acb`;
- Production/Host/Django migrations untouched.


## 2026-08-30 — Phase49.3I.45 Incremental Discovery Intelligence
- reviewed the new owner-supplied GUI, FastAPI and web-scraping references and added a permanent engineering index;
- reconciled version-sensitive recommendations against current official Qt for Python, FastAPI, HTTPX, Playwright, Scrapy, RFC 9309 and Sitemaps documentation;
- preserved Django Production and the mature 3I.43/44 acquisition runtime instead of introducing a second web backend/crawler framework;
- added `acquisition_discovery_observations` to Catalog SQLite for metadata-only URL discovery history;
- added direct-child Sitemap XML parsing with `lastmod`, `changefreq`, and `priority`;
- newest nested Sitemaps are processed first inside the existing bounded document budget;
- unseen Catalog Products rank before already-known Products;
- custom sources without an exact regex can discover bounded model-like paths from Sitemaps;
- nested image/video extension `loc` entries are not treated as Product URLs;
- build advanced to `2026.08.30.3` while version stays `8.9.9`;
- dedicated Windows acquisition run `33313008595` PASS;
- Single Active AI run `33313008558` PASS;
- source checkpoint `846cb63038a79cfe450f5a60aa66e531cf6fe0de`;
- rollback `backup/pre-phase49-3i45-book-driven-discovery-intelligence-20260830` → `3616bf222f394b769cb2e3198164d735fca5267b`;
- ERR-49-078 fixed robots policy classification: 4xx-unavailable stays non-blocking, while 429/5xx/network-unreachable fail closed; Windows acquisition CI `33313008595` PASS includes the fix;
- no Host, Production MySQL, Django migration, media, secret or access-control change.


## 2026-08-30 — Phase49.3I.42 Qt 6 Desktop Modernization foundation
- reviewed two owner-purchased PyQt5 GUI references and added a project-specific architecture/UX knowledge index;
- selected current PySide6/Qt6 for the new presentation layer while preserving the mature Tk runtime;
- added isolated `catalog_center/qt6` presentation package and `qt_launch.py` preview launcher;
- added permanent sidebar routing, QMainWindow, QStackedWidget, seven-stage Product Wizard shell, QSplitter, menu, toolbar, status bar and QSettings persistence;
- added centralized QAction registry and Ctrl+K command palette;
- added Product/Filament Model/View tables and Filament proxy filtering;
- added light/dark QSS themes and RTL application direction;
- added QThreadPool/QRunnable signal worker contract for responsive long-running operations;
- pinned preview runtime to PySide6 6.11.2 in a separate requirements file;
- added Windows offscreen Qt6 CI and legacy-launcher regression protection;
- initial CI run `33299686593` failed before job creation due invalid `runner.temp` evaluation scope; fixed without repeating the same condition;
- corrected Qt6 run `33299745502` PASS; existing Single Active AI run `33299745499` PASS;
- no DB migration, Host, Production, default launcher, media or secret changes;
- rollback `backup/pre-phase49-3i42-qt6-desktop-foundation-20260830` → `753539b0d76ccf0d185e35add458925628812a44`.


## 2026-08-29 — Phase49.3I.41 Central Filament Library + grouped Product checklist + Site sync
- replaced the ambiguous Ctrl/Shift Stage-2 Filament selection surface with a grouped one-click checklist;
- added a dedicated Product selection pane showing all currently checked Filaments;
- material groups such as PLA/PETG can toggle all child Filaments in one click;
- moved normal Filament definition/editing into a new main-app `فیلامنت‌ها` library page;
- manufacturer, brand and material are reusable editable selector histories rather than mandatory retyping;
- central editor preserves color type, primary/secondary/tertiary HEX, image, roll weight, stock, purchase/sale/USD+FX, print/supervision and preheat facts;
- live final roll/per-gram calculation remains visible;
- Product checklist save preserves Product-specific fixed price while refreshing global operational Filament facts;
- Stage-2 confirmation now persists the Phase49.3I.41 checklist before readiness/finalization;
- added authenticated Site Bridge routes for global Filament list/upsert;
- Filament Save, Product Filament commit and soft deactivation synchronize to Site without making local save depend on network success;
- added Catalog and Django Bridge regression coverage;
- no new migration; Site contract uses existing `store.0039` and `store.0040`;
- rollback `backup/pre-phase49-3i41-filament-library-sync-20260829` → `92a3f4dfcf64d5fedaf837eb9a37dac028cabd59`;
- Production untouched; owner Local + local Site verification next.


## 2026-08-29 — ERR-49-075 Filament list refresh + authoritative price preview
- owner screenshots showed a newly saved Filament not appearing under the retained filter and a price preview row with zero material/print/supervision/preheat/total despite valid inventory rate;
- fixed the post-upsert return SELECT so immediately saved Filament objects include hourly/preheat/image operational fields;
- selected-Filament edit now delegates through the final 3I.40 editor rather than the stale 3I.39 closure;
- saving a Filament switches manufacturer/material filters to that exact Filament and selects/focuses it in the list;
- pricing resolver refreshes Product Filament snapshots from current global inventory without losing Product-specific fixed price;
- a currently selected unregistered Filament can be priced as a clearly marked draft before explicit Product registration;
- range mode no longer falls into formula component preview; it displays the stored range and directs the operator to formula mode when component calculation is wanted;
- added DB return-contract, pricing-context, editor-delegation and saved-row visibility regressions;
- rollback `backup/pre-err49-075-filament-refresh-pricing-preview-20260829` → `d66c68f36d1fd3e4143d461bccd999046c4baaf7`;
- Production untouched; quick Local QA next, then website receive/sync.


## 2026-08-29 — ERR-49-074 live Filament rate/final-price display restored
- owner ERR-49-073 gate on exact `954c051...`: Catalog backup + SHA256 PASS, compile PASS, exact image regressions 2/2 PASS, OpenRouter-only 4/4 PASS, full Windows stage suite 73/73 PASS, foreground launch/visual acceptance PASS;
- image Metadata issue is accepted fixed and Product reached ready-for-publication state locally;
- restored always-visible Stage-2 final amount for fixed, formula and range pricing;
- formula summary reuses the authoritative material + print + supervision + preheat + assembly calculation and shows min/max across valid Filament × production-row combinations;
- global Filament editor now shows live final roll basis and exact Toman/gram rate from sale-roll vs USD × explicitly entered FX;
- changed operator-facing `Offer` terminology to `Filament` while deliberately retaining internal `offer_*` compatibility identifiers;
- added regression tests for formula/fixed result math, final-rate basis and visible Filament labels;
- enlarged Filament editor for the new calculation surface;
- rollback `backup/pre-err49-074-filament-rate-final-display-20260829` → `954c0516661e6c70145d7f6f395b4e92ceeb40bd`;
- no DB/migration/Host/Production change; Local retest pending, then website receive/sync is next.


## 2026-08-29 — ERR-49-073 image Metadata refresh through confirmed Stage lock
- owner exact `6d5897e...`: ERR-49-071/072 exact 7/7 PASS, OpenRouter-only 4/4 PASS, full Windows stage suite 71/71 PASS, foreground launch PASS;
- explicit Stage confirmation now works outside Images; Stage-2 price/Profile intentionally left incomplete for this QA;
- isolated remaining Images defect: later Content/Source updates changed image SEO signatures, SEO files rebuilt, but image Stage lock blocked the derived DB metadata/signature write;
- added a strict finalizer-owned derived-image persistence boundary for only selected/primary/Alt/Metadata fields;
- Stage-3 confirmation now finalizes current image SEO/Metadata before locking;
- pressing confirm again on an already-confirmed Images Stage refreshes deterministic Metadata and keeps the lock;
- manual Metadata override save now refuses while Images is locked and directs the operator to `اصلاح مرحله`;
- rollback `backup/pre-err49-073-image-confirm-metadata-refresh-20260829` → `6d5897ecefc427c940c690daabc311f85cc6e044`;
- Production untouched; owner Local focused/full/foreground retest pending.


## 2026-08-29 — ERR-49-072 Stage-2 regression fixture schema alignment
- owner ERR-49-071 gate on exact `34c65bc...`: repo/head PASS, fresh Catalog SQLite backup + SHA256 PASS, changed-source compile PASS;
- exact 7-test gate stopped on one deterministic test error before OpenRouter/full-suite/foreground launch: `sqlite3.OperationalError: no such column: price_min`;
- root cause: the new clean test DB initialized minimal Database + Profile/Ledger schemas but omitted the real ProductWorkspace schema layers that create `price_min/price_max` and `pricing_strategy`;
- test helper now calls `ensure_epic49_desktop_schema()` and 3F pricing `ensure_schema()` before Profile/Ledger setup;
- runtime application source and real Catalog DB behavior unchanged;
- fix `1307f4c438de184a930041d365976c2ce018bff8`;
- rollback `backup/pre-err49-072-commerce-test-schema-20260829` → `34c65bc9e39d851b4fd3f7e0d2d4ec9627aed5b9`;
- owner Local rerun pending; Production untouched.


## 2026-08-29 — ERR-49-071 explicit Stage confirmation + historical layout recovery
- executable code/regression checkpoint: `6085ea70d1075c5a1abaca4b4b2efdebe1254829`; Stage-2 explicit confirmation also persists its visible Product type + dimensions before locking;
- current-head GitHub Actions: none attached; Local verification pending;
- owner exact `d4da997...`: backup PASS, compile PASS, exact regressions PASS, OpenRouter-only 4/4 PASS, full Windows stage suite 67/67 PASS, foreground launch PASS, **visual acceptance FAIL**;
- removed mounting of the rejected Stage-1 type/dimensions/use-case panel and returned those existing controls to Stage 2;
- stopped mounting the ERR-49-070 additive Stage-5 panel so the historical source/license surface remains visible authority;
- accepts deliberate `external-other / سایر محصولات` as a real category;
- separates `missing_data` from `pending_finalization` so confirmation does not inflate Product defect counts;
- green Stage tick now means explicitly confirmed; complete-but-unconfirmed is `◌`;
- added independent `✅ ثبت و تأیید مرحله →` footer action and permanently hides the repaint-prone legacy Next widget;
- confirmation persists current Stage before validation, writes its lock, refreshes and advances;
- actual visible title-only AI button now routes through the same Stage-1 runtime guard/OpenRouter-only engine;
- rollback `backup/pre-err49-071-stage-confirm-rollback-20260829` → `d4da99744659d06ebe5c04fd69532cd0e03db3e8`;
- Production untouched; owner Local retest pending.



## 2026-08-29 — ERR-49-070 Stage-5 clean-schema and visible-panel recovery
- owner ERR-49-069 Local gate: compile PASS, OpenRouter-only 4/4 PASS, 67-test Windows contract stopped before launch with one schema error and one missing-visible-contract failure;
- added `technical_summary_fa` to canonical Catalog SQLite self-schema;
- implemented Stage-5 `منبع و مجوز کامل` panel for source/designer, Persian license, technical summary and technical-features JSON;
- added persisted-state refresh for those controls;
- Stage-5 finalization now maps the visible Persian license label to the stored code;
- extended regressions for clean schema and real Stage-5 builder definitions;
- rollback: `backup/pre-err49-070-stage5-schema-panel-20260829` -> `382a34fa6e876dc7098c8152c98c7cb076d508e8`;
- Production untouched; owner Local rerun pending.



## 2026-08-29 — Catalog Center 8.9.8 Stage Contract + OpenRouter-only Recovery (ERR-49-069)
- owner exact Local `3f43260...` gate: backup/checksum PASS, compile PASS, 60/60 focused tests PASS, canonical foreground launch PASS;
- real Product 63/295 UI still reproduced late footer repaint, Stage ownership drift, out-of-scope AI defect counting, overlapping Product AI jobs and AvalAI fallback;
- base 3B refresh now always yields to final 3I.39 footer authority; legacy Next persists before readiness and delegates to final confirmation;
- restored Stage-1 Product type/dimensions/use-case controls and both stage-specific/global persistence;
- restored Stage-5 source/designer/license/technical summary/features controls and stage-specific persistence;
- legacy title-only AI delegates to the final Stage-1 engine; deferred error text is frozen safely;
- single-stage repair and 3I.40 completion progress now count only the selected Scope while whole-product runs keep global truth;
- one app/process Product-AI guard blocks concurrent Product Workspace AI jobs;
- Product AI candidates are now OpenRouter-only: saved model Primary + optional `openrouter/free`; AvalAI/Google/OpenAI are not fallback Providers;
- focused regressions updated for OpenRouter-only policy, late repaint protection, Stage-1/5 persistence, Scope-aware completion and single-job behavior;
- executable-code hotfix head `136011971dea907ac777b3e66190dd27982a0c38`;
- rollback `backup/pre-err49-069-stage-contract-openrouter-only-20260829` → `3f43260db669b458a682f594b5d50eb5221b9ef3`;
- Production/Host/Django schema/media/secrets untouched; owner Local retest pending.



## 2026-08-29 — Catalog Center 8.9.8 Windows Stage Confirmation Recovery (ERR-49-068)
- owner rerun on `0191a07...`: exact prior failure PASS, focused 43-test set PASS, canonical foreground launch PASS;
- real Product 63 still exposed a Windows workflow deadlock: manually filled Stage 1 had no practical visible confirm path and the mature Next flow read persisted readiness before saving current widget values;
- historical comparison confirmed the old 3B footer Next/AI flow and later 3I.36 separate stage-finalization rail had become disconnected in the final visible composition;
- restored fixed footer `✅ تأیید و مرحله بعد →`, `✨ پرکردن ناقص‌ها با AI`, and `✏ اصلاح مرحله`;
- confirm now uses stage-specific persist/finalize before advancing and is reasserted after Wizard refreshes;
- rebound actual already-created legacy Tk AI buttons across the whole Workspace to final 3I.39 callbacks;
- exact source identity tokens may remain inside otherwise-Persian SEO/title/description; arbitrary Latin remains invalid;
- prevented an OpenRouter-shaped key from being sent to another Provider and stopped fallback Providers from inheriting the primary Provider model;
- fixed deferred exception callback by freezing redacted error text before scheduling;
- rollback `backup/pre-err49-068-windows-stage-confirm-20260829` → `0191a07f980d3cf5ba48ed1379a1c9da98c39e1b`;
- Production/Host/Django schema untouched; owner Local focused test + foreground Product 63 QA pending.



## 2026-08-29 — ERR-49-067 Locked-stage Test Fixture Alignment
- owner Local pulled `9f3b765...`, created checksum-verified Catalog SQLite backup, and passed Python compile;
- focused gate ran 43 tests with one deterministic error before foreground launch;
- failing test was the locked Quick/Content immutability regression, but its mocked `seo_description_fa` contained Latin `AI`;
- ERR-49-066 intentionally requires Persian-only SEO title/description, so runtime validation correctly rejected the stale mock before lock behavior was exercised;
- runtime checker remains strict; only the fixture wording was changed to fully Persian placeholders at `38cb415bc12d7ec08943809fd14f3478b3ddac1b`;
- rollback `backup/pre-err49-067-seven-stage-test-fixture-20260829` → `9f3b765e28f9b9adda1e7713dbc48c1255a52c1c`;
- Production untouched; owner Local rerun pending.



## 2026-08-29 — Catalog Center 8.9.8 Readiness Ownership / Checker Alignment (ERR-49-066)
- owner Local retest of `c679c66...` passed 12 targeted tests but real Product 63 still remained red after persisted AI content;
- audit proved the final repair loop classified 5 Content defects as AI-fixable, accepted a fallback response, then changed 0 fields and stalled;
- removed duplicate readiness ownership: Persian title is Quick-only; selected-image Alt is Images-only; Content owns descriptions/SEO/search text;
- added persisted source-identity-aware Persian validation for title/description while keeping SEO and keyword/tag/hashtag text Persian-only;
- made `_field_needs_fill()` use the same semantic rules as the readiness checker, including invalid non-empty lists;
- changed guided-wizard red stars/icons/Next gating to use `data_ready/missing_data`, keeping explicit operator finalization separate;
- rebound mature full-AI/link/current-stage aliases to final 3I.39 seven-stage repair authority;
- added focused regressions for stage ownership, source identity, checker/repair agreement, data-ready navigation and final AI entrypoint authority;
- rollback `backup/pre-err49-066-readiness-checker-alignment-20260829` → `c679c66d8c6554ff14e5705b7eb3aada24495990`;
- no DB/schema/media/secret/Host/Production change; owner Local regression/foreground retest pending.



## 2026-08-29 — Catalog Center 8.9.8 SEO Readiness Reconciliation Hotfix (ERR-49-065)
- owner QA confirmed the new professional Stage-2 / seven-stage workspace renders after ERR-49-064;
- seven-stage AI persisted Persian/SEO fields but some red readiness/help widgets remained stale after completion;
- added a post-AI reconciliation boundary that rehydrates the Product from Catalog SQLite, reloads the workspace, refreshes lock/guided-wizard/readiness surfaces, and leaves 3I.40 readiness as the final painter;
- the same reconciliation runs again after a short UI settle delay for both whole-product and single-stage repair;
- source `b9eb9d74b0c0c0be49ca8d04a4333750e68e93f4`;
- regression `375961a1621c43f168b7c3fd76523c6d3c9c9a26`;
- rollback `backup/pre-err49-065-seo-post-ai-refresh-20260829` → `3edda5ffe98d8c37dd66e3e7fc0d6eab3ec6c554`;
- no Provider/source/Offer/Profile/schema/Host/Production change; owner Local targeted test + foreground retest pending.



## 2026-08-29 — Catalog Center 8.9.8 Owner Visual-QA Hotfix (ERR-49-064)
- foreground owner QA on canonical `D:\\projects\\3DPrintHub` proved the correct 8.9.8 source/branch was running;
- opening Product 63 raised a Tk `pack`/`grid` geometry conflict in `phase49_3i35_operator_ledger.build_material_actions()`;
- the exception occurred before 3I.39/3I.40 ProductWorkspace wrappers completed, explaining why the owner still saw the older Stage-2/SEO UI;
- modern material/color picker presence now suppresses the obsolete 3I.35 Listbox action row instead of mounting it into the grid-managed legacy card;
- added executable regression proving no obsolete `ttk.Frame` mount occurs when the modern picker marker exists;
- source fix `aa37dcf916dfab71409738f7087a171daffe4a0a`;
- regression `9a3ebd43b22a50ac1447b90cae159dcffb1ed451`;
- rollback `backup/pre-err49-064-stage2-geometry-20260829` → `c62df9dd1bbfee4cfa915beed6f9523efaa4937f`;
- Production untouched; owner Local retest is the next gate.


## 2026-08-29 — Catalog Center 8.9.8 / Phase49.3I.40 + Store 0040
- preserved the mature 3I.38 Crawl/Direct Link/parser/image/file acquisition path and extended only the final Stage-2/readiness boundaries;
- Stage 2 now follows manufacturer → filament/material → color → Product Offer registration → pricing → production rows → Profile identity/dimensions;
- fixed multi-brand selection scope so registering eSUN/Bambu/other filtered Offers does not erase previously selected manufacturer Offers;
- separated global filament Offer inventory/rates/preheat from Product-specific fixed price per exact Offer;
- added Catalog color preview with explicit HEX/name fallback and optional filament image access;
- kept production weight/print-time/support in the upstream production rows; Profile identity remains name/size/actual dimensions with snapshot registration;
- hardened readiness UX to distinguish real missing data from complete data waiting for operator finalization;
- blocked cosmetic terminal 100% until final `ai_fixable_count == 0`; remaining AI defects stop below 100 and are reported;
- kept AI source authority at Link / Saved-Crawled Data / Screenshot; Repair is an operation, not another source;
- added Store migration `0040_phase50_filament_offer_operations` for hourly print/supervision, preheat hours/temperature/cost and filament image URL;
- first Store 0040 run `33246706102` failed on Decimal string representation only; migration plan/apply/no-drift had already passed;
- corrected tests to compare Decimal values numerically; Store run `33246843145` PASS with full SQLite migration through 0040 and 21 regressions;
- Catalog targeted run `33247729316` PASS;
- final Single Active AI run `33247815007` PASS;
- Windows Portable run `33247815027` PASS on `55139b909f214f33994d76bc1e6fdfd028b5d6c7`;
- Catalog Center `8.9.8` / build `2026.08.29.2`;
- artifact `3DPrintHub-CatalogCenter-v8.9.8`, ID `9713426658`;
- artifact digest `sha256:776eebb4daa1039119721697988508558991c6c4ccd6a2b1cca8b50b6f3b57a2`;
- EXE SHA256 `2be8be49e05575cb20ea12f061d006935df070ec9abb0f87e4f00e4151d5f02a`;
- rollback branch `backup/pre-phase49-3i40-commerce-readiness-20260829` → `b59c93cf37dcb66d3e97f61d2669df6e1d1644a4`;
- Production untouched; owner Local SQLite 0040 + 31–40 visual/functional QA is next.


## 2026-08-27 — Catalog Center 8.9.6 / Phase49.3I.38
- preserved the mature Browser/Crawl/Parser/image/file receive pipeline and extended only its identity/continuation boundaries;
- added permanent crawled/received Product ledger UI over the existing `discovered_urls` authority;
- added persisted `crawl_listing_state` continuation cursor so repeated Listing scans go deeper instead of repeatedly stopping at the first fixed discovery window;
- verified the 100+next-100 contract: 100 previously collected identities are skipped and Products 101–200 become the next 100 pending entries;
- added `رد دائمی + حذف فایل‌ها و عکس‌های محلی`: local Product acquisition files are purged while source URL/external ID remain as a `rejected` tombstone;
- physical deletion is restricted to the Product directory below Catalog `collected/`; out-of-bound paths fail closed;
- fixed `ERR-49-062`: Direct Link now checks terminal rejected/blocked identity before browser/HTTP/image/file acquisition;
- fixed `ERR-49-063`: category/site crawl now persists bounded deeper scroll progress while keeping the mature `discover_classic()` implementation;
- explicit restore is required before a rejected identity can be received again;
- kept one Product AI engine with Link / Saved-Crawled Data / Screenshot inputs and the same configured Provider/Model/retry/fallback authority;
- added optional Stage write scope to the same resilient orchestrator;
- Products bulk Content/SEO now uses that same engine with Stage 4 scope rather than a separate AI path;
- added single-stage cleanup/completion; out-of-scope and finalized stages remain immutable;
- image-only scoped AI makes no Provider request when image SEO is already complete;
- runtime `c904193a7f0af9aad80365834ec3f0b856e77dc9`;
- Phase49.3I.31–38 run `33077213590` PASS with 84 tests;
- Single Active AI run `33077239617` PASS;
- Windows Portable run `33077239660` PASS;
- Catalog Center `8.9.6` / build `2026.08.27.8`;
- artifact `3DPrintHub-CatalogCenter-v8.9.6`, ID `9648474905`;
- EXE SHA256 `6490e4815f1e6e0d75f09c112bb6990041578616f170954f62fae037b98bd507`;
- artifact ZIP digest `sha256:13ae8582be09b71f90e607c2230075d875b7445f8a46b6462a9241edf9d52563`;
- browser smoke, portable self-verify and source URL preservation gate PASS;
- rollback branch `backup/pre-phase49-3i38-crawl-ledger-stage-ai-20260827` → `d1ed566a82d3818aa45a5c720df3e7efcb0044f3`;
- Production untouched; owner Local visual/functional 3I.38 QA remains the next gate.

## 2026-08-27 — Catalog Center 8.9.5 / Phase49.3I.37
- added one persisted Product AI source mode: Link / Saved Data / Screenshot;
- replaced visible per-run Product AI modes with one missing-only seven-stage orchestrator shared by single and selected-Product bulk runs;
- separated stage data completion (`✅`) from operator finalization (`🔒`) and persisted finalization locks in Catalog SQLite;
- AI now skips finalized stages and never owns Profile/price/material/color/brand/stock/publication fields;
- fixed `ERR-49-061`: both `sales_profile_ledger_json` and legacy `sales_profiles_json` are protected by the Commerce lock;
- unified Persian identity/SEO validation; `Twistmas Tree` is normalized to `درخت کریسمس اسپیرال`, with mixed Cyrillic/unrelated Latin SEO contamination rejected;
- kept image rename/WebP generation deterministic and separate from AI; AI image ownership is SEO metadata only when missing;
- upgraded Product-page Screenshot to a selected site image with SEO/metadata and preserved `source_page_url`;
- runtime `8d5e58a839c89eedbe258d9236889834fc02d9a9`; targeted run `33074245603` PASS (77 tests); Single Active AI `33074245489` PASS; Windows run `33074245604` PASS;
- artifact ID `9647216177`; EXE SHA256 `4a3e15a3c475460c2dac035cedcd8ccebb40107fec6360b7be6a313f69186079`;
- Production untouched; owner Local visual 3I.37 acceptance remains the next gate.


## 2026-08-27 — Catalog Center 8.9.3 Profile Workspace Binding Hotfix
- owner 8.9.2 diagnostic confirmed startup success, then Product 305/303 open callbacks failed with `AttributeError: ProductWorkspace has no attribute _profile_by_key`,
- recorded as `ERR-49-060`,
- fixed 3I.34 selected Profile loader to call installed namespaced `_phase49_3i34_profile_by_key`,
- added executable non-Tk wrapper-binding regression,
- backup anchor `backup/pre-err49-060-profile-matrix-bind-fix-20260827` → `6f9334705c74a65d47473580944d79d61d501293`,
- bumped release atomically to Catalog Center `8.9.3` / build `2026.08.27.5`,
- targeted run `33067612565` PASS,
- Single Active AI run `33067618639` PASS,
- Windows portable run `33067618679` PASS on `9637829a255a1d09800bc062c2f049cf5d92b585`,
- artifact `3DPrintHub-CatalogCenter-v8.9.3`, ID `9644438652`,
- EXE SHA256 `fd525fad977f592dc62e68fc3a4310bba98c7ed9689c5101cbdc35589fef7bed`,
- artifact ZIP digest `sha256:216b62072fd95a0a4d292b28ce99605fd60f3e4d9622d06987d6fe5b434e6141`,
- Production untouched; owner foreground Product Workspace QA remains required.


## 2026-08-27 — Catalog Center 8.9.2 Visible Startup Hotfix
- owner foreground 8.9.1 launch exposed a real Tk startup failure: 3I.35 AI-resilience settings used `grid` directly inside UX87 `settings_tab`, whose existing children use `pack`,
- root cause matches permanent `ERR-49-001`; incident recorded as `ERR-49-059`,
- fixed only the outer AI-resilience panel to `pack(fill="x", padx=8, pady=8)`; internal panel controls remain grid-managed safely,
- added regression `test_ai_resilience_settings_respects_pack_managed_settings_tab`,
- bumped release atomically to Catalog Center `8.9.2` / build `2026.08.27.4`,
- targeted 31–35 run `33066472847` PASS,
- Windows portable run `33066468014` PASS on `9bd9d0b4cd070a35c82c6ecefd6f6b3027b20284`,
- artifact `3DPrintHub-CatalogCenter-v8.9.2`, ID `9643957471`,
- EXE SHA256 `fac29fc610215cfc4115fcdb4c005fc69f99c3e6569b44c501d63ec82d6ba257`,
- artifact ZIP digest `sha256:78a371693563b3293d7b49e39e5acd8dbf3032be9f6fee1b5252fffc5a29d0fb`,
- Production untouched; owner foreground visual QA remains required.


## 2026-08-27 — Owner Local 3I.35 / 50.A.2E Automated Gate PASS
- owner Local root `D:\\projects\\3DPrintHub` verified exact repository/branch and clean worktree,
- Local fast-forwarded to `2cdb356fca6d6c4c4bcd0edf203acf8e24bab2b9`,
- effective Local Django DB verified as SQLite `D:\\projects\\3DPrintHub\\db.sqlite3`,
- fresh pre-0039 DB backup `D:\\projects\\3dprinthub-backups\\phase49-3i35-resume-20260827-142404\\django-local-before-0039.sqlite3` with matching SHA256,
- `store.0038` verified applied and `store.0039` verified pending before write,
- exact `0039_phase50_filament_offer_pricing` plan inspected, then `0039` applied successfully,
- 16 Store/Profile/Checkout regressions PASS,
- post-migration `makemigrations --check --dry-run` = no changes detected,
- Catalog Center 31–35 Local gate PASS with 107 tests, source URL invariant PASS, launcher verify PASS,
- Catalog Center `8.9.1` / build `2026.08.27.3` launched successfully,
- Production touched = NO.
- next gate is manual owner visual/functional QA; no Host/Production operation performed.


## 2026-08-27 — Local Owner Gate PowerShell DB Probe Runbook Fix
- owner Local checkout fast-forwarded cleanly to `35ab63105f30fdca42518d5273a424a3200977e3`,
- packaged-runtime/tooling ancestry and Catalog SQLite backup passed,
- the wrapper stopped before any new migration because multiline PowerShell `python -c` quoting corrupted the embedded Python DB detector,
- recorded as `ERR-49-057`; this is a command-transport defect, not a Django/schema failure,
- resume procedure now uses a single-quoted PowerShell here-string piped to Python stdin, then backs up the effective Local Django SQLite DB before migration,
- Production remains untouched.


## 2026-08-27 — Phase49.3I.35 / Phase50.A.2E — Operator Ledger, Resilient AI and Brand-aware Filament
- Catalog Center bumped to `8.9.1`, build `2026.08.27.3`,
- replaced duplicate Profile editing surface with accounting-style registered Profile ledger while preserving the mature 3I.34 transport,
- working form now registers independent Profile snapshots; new Profile can load the latest snapshot safely,
- production rows now model Product weight, print time and support weight,
- quick/basic Product page no longer owns fixed-price/weight/Profile authority,
- material/color UI adds select-all and local-register without full Products refresh,
- added material + brand + manufacturer + color + roll stock/purchase/sale/USD/explicit FX offer facts,
- dynamic formula pricing consumes effective brand/color sale rate; FX is never guessed,
- added observable AI preflight/progress/retry/failover and per-Product bulk isolation,
- added manual SEO readiness and source-review controls without commercial-license bypass,
- migration `0039_phase50_filament_offer_pricing` adds brand-aware offer fields, Variant support weight and immutable order support/brand/manufacturer snapshots,
- Storefront distinguishes same material/color across brands and exposes brand/manufacturer/support in selected Profile/API,
- fixed migration metadata drift `ERR-50-016` without creating a fake 0040,
- fixed stale 8.9.0 config + retired quick-price test contract `ERR-49-056`,
- Phase50 run `33059883188` PASS: no migration drift, clean CI migration through `0039`, 16 regressions PASS,
- Smart/Profile 31–35 run `33060613937` PASS,
- Single-AI run `33060613914` PASS,
- Windows portable run `33060047878` PASS on runtime `2622818d898e19b745c61ff653b80c03d22288f1`,
- artifact `3DPrintHub-CatalogCenter-v8.9.1`, ID `9641338334`,
- EXE SHA256 `3099b26713a460fbd55c1204ef750b37dbef542269b5520fd393526cd8c9476c`,
- Production remains unchanged at `c283864290f9c989a9fcdf24ee8eef519560e917`; last verified DB has `0034/0035` only and owner Local QA is required before any `0036 → 0037 → 0038 → 0039` Production work.


## 2026-08-27 — Product Profile Matrix 49.3I.34 / 50.A.2D — GitHub CI Tested
- Catalog Center 8.9.0 build 2026.08.27.2 now has a Step-2 Product Profile Matrix with add/clone/delete/edit profile workflow,
- every profile can independently own size, final/material weight, fixed price, print time, part dimensions, build, material, color, quality, package facts, stock/default/sort state,
- Desktop profile JSON travels through the mature batch/import boundary and idempotently becomes canonical Django ProductVariant rows; unrelated manual Variants are preserved,
- added compound customer modes including size→weight and 3-level size/weight/build flows,
- migration `0037` adds professional pricing/shipping/payment policy; migration `0038` adds profile descriptions, size↔weight modes and actual part dimensions with immutable order-item snapshot dimensions,
- Storefront selected Profile is the single product price/facts authority; navy/gold presentation aligns with the Catalog Center visual language,
- fixed Variant API callable price-contract bug (ERR-50-012),
- fixed saved-address checkout rejection in the shipping policy wrapper (ERR-50-013),
- fixed dependent selector hierarchy so downstream state cannot hide upstream choices and weight/profile prices are scoped to the selected size (ERR-50-014),
- added dedicated Node behavior gate `PHASE50_PROFILE_SELECTOR_HIERARCHY=PASS`,
- Web CI `33051311828` PASS on runtime snapshot `7d0a2a1125e8f38771ba325427d1efa8b8d07da6`; migrations through `0038` and 15 Store/Profile/Checkout tests PASS,
- Windows release trigger now watches mature Product studio files (ERR-50-015),
- Windows portable run `33051114515` PASS on `b3280dd67cd7772f337f6792036ea92d3f252747`; artifact ID `9637671099`; EXE SHA256 `32aed719e6d374447fc4b05f09a30fe12f0ce4dc05e570382f2e74036044900c`,
- Production remains unchanged at `c283864290f9c989a9fcdf24ee8eef519560e917`; Local owner QA + fresh Host/MySQL audit/backup are required before the pending `0036 → 0037 → 0038` chain.


## 2026-08-27 — Catalog Center Local Gate Self-Dirty Hotfix
- root cause of the reported “does not come up” log was not a startup exception: the gate stopped before `-LaunchApp` because a prior portable build left untracked `catalog_center/release/` output,
- added `/catalog_center/release/` to `.gitignore` without deleting existing local EXEs/manifests,
- added regression coverage so generated portable output stays outside Git status,
- Windows portable CI run `33042158052` PASS on `1a490fecb5a22b855c4f10a12bb74f04a28c57b9`; one-file build/self-verify and artifact upload PASS; release publication remains manual pending owner QA.

Record meaningful changes only. Older detailed entries remain available in Git history.

## 2026-08-26 — Phase49.3I.32 Canonical Product Source URL Guard — Packaged Windows CI PASS
- root cause confirmed in mature `ProductStudio.save()`: both mirrored URL controls could be temporarily blank and generic/silent Save would overwrite `source_url`, `normalized_url` and fingerprint with empty identity,
- silent Save is reused by close/refetch/AI/publish/layered Workspace actions, explaining why an unrelated button could appear to delete the Product link,
- added final additive `phase49_3i32_source_url_guard.py` after 49.3I.31; existing canonical URL is fed into both URL controls before the mature Save chain when both are blank,
- explicit non-empty main/spec URL edits remain supported,
- defensive post-save invariant restores canonical URL/normalized URL/fingerprint if a legacy layer still erases it,
- already damaged Products can recover the exact prior HTTP/HTTPS source URL locally from Product history, with matching `discovered_urls(source_code, external_id)` as fallback; no network or guessed/reconstructed URL,
- recovery is recorded in Product history/diagnostics,
- Catalog Center candidate remains `8.8.2`, build `2026.08.26.2`,
- targeted Phase49.3I.31-32 CI run `32996526852` PASS on `2ca69c4928333fc15247b99014a8fe77d781b50b`,
- first Windows packaged run `32996526842` failed only on one stale legacy test literal expecting 8.8.1; new source-link tests were already PASS,
- replaced stale release literal with runtime-version == package-manifest-version contract,
- Windows packaged rerun `32997106056` PASS on `5208aa4dd3b070e9a7c7c6d6dde9b60569879631`: full regression, launcher composition, source URL invariant, one-file EXE build/self-verify, release-manifest/SHA256 verification and immutable artifact upload PASS,
- Actions artifact `3DPrintHub-CatalogCenter-v8.8.2` created as artifact ID `9617048629`,
- automatic public release publication disabled; release is explicit/manual only after owner Local QA.

## 2026-08-26 — Catalog Center 8.8.2 Smart Link + Batch AI — GitHub Candidate
- Phase49.3I.29 Windows performance base: 48-card Product presentation paging, full SQLite result preservation, deferred global Product refresh and exact saved mother Provider/Model execution without hidden Product model scans,
- Phase49.3I.31 unified Product AI: exact Product URL validation/fetch, canonical source identity, safe source facts flattened into one heading-structured text body, Persian content/SEO and selected-image metadata/finalization,
- normal Product AI transmits only `source_title` + one `source_description` text field; raw HTML, auth/cookies/secrets and unrelated pricing/stock/workflow state stay local,
- main Product AI/link actions converge on the same grounded runtime boundary,
- Products Explorer supports selected-product batch AI using each Product's own exact source URL, isolated per-item errors/cancel and one global Products refresh at batch end,
- mother AI settings remain authoritative for AvalAI/OpenRouter/Google/OpenAI; no cross-provider fallback.

## 2026-08-26 — Phase50.A.2B Immutable Checkout/Profile/Shipping Snapshot — GitHub CI Tested
- added migration `store.0036_phase50_checkout_snapshot`,
- StoreOrderItem immutable profile/selection/final-weight/shipping-weight/print-time snapshots,
- existing `0034` size/build/packaging-weight/package-dimension snapshots populated during successful checkout,
- StoreOrder `insured_value` + normalized `shipping_quote_snapshot`,
- mature Phase6 validation/coupon/inventory/address/notifications/payment remains authoritative,
- checkout finalization uses outer atomic boundary, effective shipping weight and ShippingMethod fallback without inventing external carrier contracts,
- integration regressions prove snapshot immutability and payment/shipping synchronization,
- `Phase50 Variant2 Gallery CI` run `32966720475` PASS on `fba0631e60bce1f6e3f622317b70c2f7f35d978f`,
- Production remains at `c283864290f9c989a9fcdf24ee8eef519560e917`; `0036` not yet applied.

## 2026-08-26 — Phase50.A.1H + Phase50.A.2A Production Verified
- Production fast-forwarded to `c283864290f9c989a9fcdf24ee8eef519560e917`,
- rollback backup `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-143650`,
- MySQL `store.0034` + `0035` applied; no new migration executed,
- Admin shell stability and Storefront sales-profile selector deployed and verified,
- Home/Store/Admin/Product/static/Variant API healthy; public Home private imported-media refs = 0.

### Deployment-verifier incidents
- cPanel `/dev/fd` process-substitution failure corrected with Python enumeration (`ERR-50-010`),
- JSON verifier execution mistake corrected with `python - <json-path> ...` + `json.load` (`ERR-50-011`).

## 2026-08-26 — Phase50.A.1H Admin Shell Stability + Phase50.A.2A Storefront Profile Selector
- Admin CI `32958276378` PASS on `27335832e90c35dd95bb8a686dd89d1efd46dc8f`,
- Storefront CI `32958296546` PASS on `e3c57311c0c3980befeaf6012f3bb8fc502333bc`.

## 2026-08-26 — Phase50.A.1G Velzon Operator Surface V2
- on-demand filter drawer/full-width lists,
- CI `32955310832` PASS on `3687d0922959fca53f2118be6dacd32639159346`.

## 2026-08-26 — Phase50.A.1F Business Admin Navigation / Product Admin 500 Fix — Production Verified
- fixed Product changelist SafeString numeric-formatting 500,
- deployed/verified at `bc7b97f9c63432b8105f52f61cf5cdae1369689b`.

## 2026-08-26 — Phase50.A.1E Production Deployment Verified
- deployed `9cfbc54ed4196144864b5f4201976d8466a88134`,
- backup `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-114327`,
- `0034`/`0035` applied; HTTP/private-media gates PASS.

## 2026-08-26 — Phase50.A.1E Unified Product Admin Workspace
- business-ordered Product workspace preserving mature Product/Profile/Variant/SEO contracts,
- CI `32941662288` PASS on `f34eaa3bbad965b2092279291ff8adf93f3d908e`.

## 2026-08-25 — Phase50.A.1C Admin Media / Mobile / SEO / Windows Dimensions
- safe ImportedPrintAsset Admin public-media resolver, compact mobile Hero, homepage SEO audit and Windows image dimensions; CI PASS.

## 2026-08-25 — Phase50.A.1B Product Gallery + Variant 2.0 Foundation
- Product gallery/lightbox, Variant2 size/build/package fields, StoreOrderItem snapshots, `store.0034`; CI PASS.

## 2026-08-25 — Catalog Center Windows v8.8.1 Final Portable Release
- released `3DPrintHub-CatalogCenter-v8.8.1.exe`, build `2026.08.25.2`, SHA256 `c32f37affcbd2c6ffacb803247daf804a490fecd7c8162bc37c2729a2197e990`.

## 2026-08-25 — Phase50.A.1 Admin Storefront / Hero Parity
- Product/imported-asset Hero controls and Storefront/Coupon/Shipping/Pricing/address Admin surfaces.

## 2026-08-25 — Phase50.A Admin Command Center
- authenticated `/admin/command-center/` organized around Sales, Treasury, Accounting/Ledgers, Purchasing and Inventory/Production.

## 2026-08-25 — Phase49.3I Production closeout
- Product-owned public Hero media, structured web Product presentation and verified Production deploy; imported Catalog working-media remained private.

## 2026-09-14 - Phase50.A.2I Slicebox-inspired Hero
- Added dependency-free seven-slice CSS/JS 3D transition over the existing managed Hero.
- Preserved server-rendered Hero SEO/content/Product links and mature controls/rotation.
- Added mobile, reduced-motion and unsupported-3D fallback to the mature transition.
- Aligned the stale Hero media regression with ERR-49-125 Product-owned public-media policy.
- Local Hero/Public-Media suite 30/30 PASS; real Playwright desktop/mobile QA PASS; no migration/dependency/DB write.

## 2026-09-14 - Local Filament defaults + all-Product Profile preselection
- Backed up canonical Catalog SQLite before mutation.
- Set all 66 active Filament rows to one 1000 g roll and nonzero purchase/sale/print/supervision pricing.
- Applied owner pricing overrides for PLA, PETG, HT-PLA-GF and PLA-CF; specialist Material prices came from existing project Material reference data.
- Backfilled canonical Sales Profiles for all 635 Products and selected all 64 unique active Filament identities in every Profile.
- Opened 12 Commerce locks through StageCore so dimensions can be edited; 19 prior uploads now carry `needs_update=1` for republish/update.
- Focused Filament/Profile tests 34/34 PASS, Qt verify-only PASS, Catalog integrity `ok`.
- Relaunched Windows Catalog Center v8.9.10. No Production publish/deploy was performed.

## 2026-09-17 - Publisher republish continuity and A2J empty-store parity
- Added collision-safe second-resolution Catalog batch allocation while preserving the bridge naming contract.
- Reconciled A2J source-backed Hero fallback into the main development lineage.
- Added the accepted A2J seed command/tests and guarded host runner provenance.
- Verified Windows publish `16/16` and Hero focused `25/25`.
- Prepared and verified a fresh Production Store-reset rollback backup; destructive reset remains not executed because the automation safety layer blocked the write call.
## 2026-09-17 - Windows publisher exact-SHA runtime verification
- Launched Catalog Center 8.9.10 from GitHub exact SHA `67445d60...` using canonical `RUN_DEBUG.ps1`.
- Verified exact-copy rollback of persistent Catalog SQLite, runtime DB path, FTP login and Bridge health.
- No redundant A2J Production source deploy was needed because accepted Production runtime is behavior-equivalent.


## 2026-09-17 — Buffer Instagram integration source
- Registered Buffer as the project-preferred Instagram publishing provider after direct Meta Developer access failed by location.
- Added `catalog_center/app/buffer_publish.py` for Buffer GraphQL channel validation and Site-first Instagram post creation.
- Added explicit `BUFFER_API_KEY` secure-secret mapping and Git-ignore protection for the temporary `buffer-ker.txt` handoff file.
- Added `docs/مستندات اتصال به اینستاگرام/` containing architecture, API contract, security rules, official Buffer references and safe GraphQL examples.
- Added focused Buffer provider tests: healthy Instagram channel, `shareNow` public-media post input, and fail-closed missing-secret behavior.
- Buffer-side Instagram login is owner-confirmed; live API transport remains pending because the local handoff file and Credential Store currently contain no Buffer API key.
