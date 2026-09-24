## 2026-09-24 - Phase50.A.2Z-O Catalog Operator Controls — six bounded phases
- [x] O1: converge Windows/Production lineage with no tree regression.
- [x] O1: Product filters for 7/7 ready, AI-completed 6/7, Site sent, Instagram Post sent and Instagram Story sent.
- [x] O1: split Instagram Post and Story into independent buttons/readiness/workers; Story-only does not create Feed and Feed-only does not create Story.
- [x] O1: focused 24/24 + broader Product/Qt/Social 136/136 + compile/diff/Qt VerifyOnly; real Catalog filter counts and quick_check pass.
- [x] O1: source/docs commit `22bb0fb1...`, Local=Remote, exact-SHA VerifyOnly, integrity backup, one Catalog Center restart and runtime smoke PASS.
- [x] O1B ACCEPTED: "آخرین ادیت‌شده‌ها" and "اخیراً دیده‌شده‌ها" are GitHub-exact at source `a0d5ea46...`; final 106/106 regression, cloned real MainWindow/ProductWizard no-dirty acceptance, fresh backup and visible exact-SHA runtime smoke all PASS.
- [x] O2 ACCEPTED: shared filesystem-aware complete/incomplete contract, exact missing reasons, source `f04d5b05...` GitHub-exact, rollback/integrity PASS, one exact-SHA restart, real runtime partition 1099 = 463 complete + 636 incomplete, scoped no-mutation digest PASS, visible Qt runtime PASS.
- [ ] O3: guarded deep repair — backup, bounded derived-data purge, full source refetch and same-identity remap.
- [ ] O4: fix Delete semantics and prove visible removal/tombstone/restore behavior.
- [ ] O5: independent Social receipt reconciliation and operator acceptance for Post vs Story.
- [ ] O6: integrated regression, any required GitHub-first Production gates, final docs and closure.

## 2026-09-24 - A2Z final Production closure gate
- [x] Restore/authenticate dedicated 3DPrintHub reverse tunnel and pass Host read-only identity/DB/migration gate.
- [x] Fresh Production DB + full-media rollback before #625.
- [x] Publish only #625 and verify Product #39 rev13, active media/Variants/Profile pricing and stale-media removal.
- [x] Fresh Production DB + full-media rollback before #628.
- [x] Capture rollback-safe #628 Unicode filename failure without retry.
- [x] Implement shared ASCII-safe Server/Public media filename contract and parity alignment at `b5980306...`.
- [x] Unicode 1/1 + unified import 5/5 + related server 21/21 + compile/check/no-drift/diff gates.
- [x] Build selective release from exact Production `103f559c...`; deploy only verified Server delta `2b48a593...` from GitHub with fresh rollback/readiness/public smoke.
- [x] Retry only #628 once after receiver verification; same UnicodeEncodeError persisted with transaction rollback, so no unchanged retry.
- [x] Run rollback-only stage tracer and exact ASCII-filesystem reproduction: importer stages/parity all pass; raw Unicode Batch source path reproduces the exact Production positions 127-131 error.
- [x] Harden Windows Batch packaging so physical FTP/local-image source names are ASCII-safe while Unicode SEO metadata and media SHA remain unchanged; real #628 clone dry-run PASS. No new Server deploy required because `2b48a593...` already owns destination canonicalization.
- [x] Commit/push Windows packaging fix as GitHub-exact `7b1b447a...`; Local=Remote verified.
- [x] Exact-SHA runtime gate + changed-condition bounded retry only #628; final Batch succeeded as Site Product #38 revision 2.
- [x] Verify #628 Product/Image/Profile/Variant/Slider parity and public HTTP/no stale media.
- [x] Recheck #152/#178/#620/#625 for collateral changes without republishing them.
- [x] Complete real Desktop/Mobile Playwright acceptance and close Phase50.A.2Z as ACCEPTED.

## 2026-09-23 - A2Z exact-SHA local acceptance / Production gate
- [x] Commit/push A2Z checkpoint fde86e23... and verify Local=GitHub exact.
- [x] Launch Qt from exact pushed SHA.
- [x] Reconcile #625 revision 11->12 from exact receipt proof; operator digest unchanged.
- [x] Re-run #625 Ready core; preserve profiles/16 PLA/media/pricing.
- [x] Mark #628 Ready; preserve 12/18cm profiles, 16 PLA/profile and two selected media; refresh current pricing.
- [x] Capture post-local integrity rollback phase50-a2z-post-local-gates-20260923-215515.
- [ ] Restore official 3DPrintHub reverse tunnel; no alternate Host path.
- [ ] Fresh Production DB/media rollback.
- [ ] Republish #625 alone and verify strict replacement parity/public HTTP.
- [ ] Fresh rollback, republish #628 alone and verify strict replacement parity/public HTTP.
- [ ] Desktop/Mobile browser acceptance and A2Z closure.

## 2026-09-23 - Phase50.A.2Z Catalog Data Completion
- [x] Start from clean unified A2Z/A2R head `56c569...`; preserve dirty precursor untouched.
- [x] Re-read required docs and verify real Local/GitHub/Catalog/Site state.
- [x] Inventory real Catalog: 771 Products; Slider complete 61 / incomplete 710; enabled incomplete exactly #40 image.
- [x] Verify #152/#178 already reconciled on Site; no duplicate retry.
- [x] Verify #620 already public/clean with current complete Slider data.
- [x] Make incomplete Crawl Products visible/actionable and same-identity recoverable without refetching complete Products.
- [x] Preserve canonical A2R video authority; do not port obsolete parallel video fields.
- [x] Add fail-closed revision-only reconciliation from exact matching local `publish_incomplete` receipt.
- [x] Prove #625 Site rev12 is from exact Desktop Batch `26aa571c...`; unknown revision remains blocked.
- [x] Catalog/Profile/Filament/Image/Slider/Site related 153/153 PASS; Server 12/12 PASS; static/Qt gates PASS.
- [x] Fresh integrity Catalog rollback before mutation: `phase50-a2z-data-completion-pre-mutation-20260923-202714`.
- [ ] Commit/push tested source/docs and verify Local=GitHub exact.
- [ ] Relaunch exact-SHA Qt.
- [ ] Reconcile #625 revision authority only; prove Product/operator digest unchanged.
- [ ] Real #620/#625/#628 operator acceptance; preserve Profile/Filament/Image authority.
- [ ] Mark #628 Ready only after exact-SHA acceptance; do not send broad queue.
- [ ] Fresh pre-republish rollback and bounded same-identity republish.
- [ ] Strict Site Product/media/Profile/Variant/Slider parity + public HTTP.
- [ ] Real Desktop/Mobile browser acceptance.
- [ ] Final docs closure.

## 2026-09-23 - Phase50.A.2Z-LC A2R lineage convergence
- [x] Stop A2Z feature mutation when post-A2Y Windows/Production divergence is proven.
- [x] Preserve dirty A2Z Data Completion worktree with external rollback patch + status evidence.
- [x] Create clean convergence worktree from newest accepted A2Z head `3de2af09...`.
- [x] Port only evidence-backed A2R motion-media deltas; preserve newer A2Z Social v5 and operator flows.
- [x] Establish one canonical video authority: `video_links_json / selected_video_links_json / local_video_files_json`.
- [x] Preserve MakerWorld animated GIF motion media and safe provider-CDN download boundary.
- [x] Integrate Site Batch/import/render/public verification for motion media.
- [x] Keep Source re-crawl operator-safe; discovery may refresh source video links without silently replacing selected/local video.
- [x] Prove Buffer Social remains image-based; do not claim Reel/video completion.
- [x] Catalog video 8/8 + Social 41/41 + Crawl/V84 40/40 + Publish 55/55 + Server 12/12 PASS.
- [x] Compile/check/no-drift/diff/runner-syntax/Qt VerifyOnly PASS.
- [x] Source commit `be00cc73d7745406b7219d323890f05222f17494`.
- [x] Record Git ancestry from Windows A2R `03808add...` and Production A2R `103f559c...` without replacing tested A2Z tree.
- [x] Unified merge head `05f29ba3a4de53fcf8b0a6fd73427a3653bb0ed3`; Local=GitHub exact.
- [x] Production read-only verification healthy on `103f559c...`; #536 public motion GIF HTTP 200.
- [x] Audit unified-vs-Production Server delta; migration/dependency delta 0, unrelated settings/ZarinPal delta exists -> no broad deploy.
- [ ] Resume A2Z Catalog Data Completion only from unified forward head; port preserved dirty work selectively and test before Catalog mutation.

## 2026-09-23 - Phase50.A.2Z-S2 automatic Story + Shop Grid Product links
- [x] Prove historical #625 Story was genuinely Buffer-sent/live without the later mobile-notification contract.
- [x] Restore default companion Story to Buffer automatic publication; keep native Link Sticker notification as optional mode only.
- [x] Preserve Feed `metadata.instagram.link` as Product-specific Buffer Shop Grid link.
- [x] Remove raw Product URL from Feed Caption; use Bio/Shop-Grid CTA instead.
- [x] Remove raw Product URL from Story artwork; use «خرید از لینک بیو» + @3dprinthub_ir.
- [x] Bump Social policy to v5 and Story style/cache identity to v3 so old URL-bearing cached Story cannot be reused.
- [x] Preserve current-revision Feed/Story duplicate receipts and Story-only recovery semantics.
- [x] Focused 27/27 PASS; complete Site+Social 70/70 PASS after one documented stale-link assertion update.
- [x] 11 Python compile + diff-check + Qt VerifyOnly PASS; Server delta 0.
- [x] Commit/push exact S2 runtime `447e81306a19d816042530f3d00989305a84bd2c`; exact-SHA Qt PASS/running.
- [x] Live readiness proof: `bio_shop_grid`, `buffer_shop_grid`, mobile handoff false, ready=true despite Buffer mobile false.
- [x] Fresh Catalog backup + bounded #536 Story-only real acceptance; existing Feed reused, zero duplicate Feed.
- [x] Story `6ab383f9497d7707d81648c8` Buffer sent/live; Instagram Story URL verified; v3 asset 1080×1920 public SHA parity PASS.
- [x] Buffer Shop Grid public page HTTP 200 and #536 tile points to exact tracked Product URL.
- [x] Post-accept Catalog backup quick_check PASS; A2Z-S2 CLOSED/ACCEPTED.
- [ ] Historical #536 Feed caption visual cleanup, if desired, must be edited directly in Instagram; future v5 captions are already corrected.

## 2026-09-22 - Phase50.A.2Z-S Instagram Post + linked Story readiness
- [x] Re-verify provider from live Catalog: Buffer GraphQL `https://api.buffer.com`, channel `3dprinthub_ir`, media host `github_raw`.
- [x] Preserve accepted Feed contract: Site-first current revision, Product caption/SEO, per-image ALT, bounded hashtags, UTM, nationwide shipping, no false free claims.
- [x] Preserve accepted Story contract: branded 1080×1920 Gold/Navy + IRANSans, Product link, independent receipt, Highlight target recorded/operator placement.
- [x] Add global Buffer delivery readiness before Site mutation, media render/rehost or provider createPost.
- [x] Require `hasActiveMemberDevice=True` when clickable Story/Link Sticker is enabled.
- [x] Keep lower-level Buffer guard + current-revision Feed duplicate protection.
- [x] Update Products action to **Post + Story لینک‌دار** and block Worker creation when readiness fails.
- [x] Focused 22/22 + full Site/Social 69/69 + compile/diff/Qt VerifyOnly PASS; Server delta 0.
- [x] Commit/push exact Social-readiness SHA `ec05b77fec0d3316d8ee9663fb50b333cf437658`; exact-SHA Qt VerifyOnly/launch PASS.
- [ ] External: link same Buffer account on mobile, enable/reset push and pass Test Notification until API reports `hasActiveMemberDevice=True`.
- [ ] Then perform one bounded real Product Social acceptance: current Site revision -> Feed (or reuse existing Feed) -> linked Story notification -> Instagram Link Sticker -> truthful receipts -> Highlight operator step.

## 2026-09-22 - Phase50.A.2Z-C3 Full Registration + FTP Quota Recovery
- [x] Verify clean Local=GitHub baseline `7d6f738a...`; rollback ref `backup/pre-a2z-confirm-all-quota-20260922`.
- [x] Add top Product **«✅ ثبت کامل»** beside Full Edit.
- [x] Save current editable Stage before all-stage approval.
- [x] Reuse existing StageCore `finalize()` validation for all seven canonical Stages with explicit manual approval.
- [x] Keep incomplete Stages blocked; summarize blockers.
- [x] Prove Full Registration does not call mark-ready/publish/FTP/Bridge/Social.
- [x] Focused 3/3 PASS.
- [x] Related Stage/Product/Site/Slider regression 82/82 PASS.
- [x] 3 Python files compile; diff-check + Qt VerifyOnly PASS; Server delta 0.
- [x] Prove failed 17:12 batch targets only Product #536 and stopped before FTP upload/Bridge import.
- [x] Prove same quota class also affected #588; current queue inventory is 15 but must not be bulk retried.
- [x] Prove official PrintHub tunnel 22024 absent; current Host-IP session is RetoucherTunnel and must not be reused.
- [x] Commit/push C3 exact at `ac094945901cfd612dd6069fdd473a995c8a204a`; Local=GitHub exact.
- [x] Exact-SHA Qt relaunch + widget smoke 4/4 PASS.
- [x] Restore official PrintHub tunnel; expected key fingerprint and authenticated bridge PASS.
- [x] Verify Host write headroom and exact FTP pending-path MKD/STOR/DELETE/RMD PASS.
- [x] Production-verify quota recovery with real Batch `desktop_catalog_v85_20260922_181511` / 31 uploaded files.
- [x] Verify #140/#151/#210 updated, #536/#588 created and public; queue reduced to 10.
- [x] Read current Site Hero truth for #152/#178; conflicts are revision-only (2:1→2 and 4:3→5).
- [x] Local-test pre-publish Hero revision refresh that changes only `server_slider_revision`; focused + integration contracts PASS.
- [x] Local-test Buffer clickable-Story mobile prerequisite before Feed; no partial new Feed when device missing; existing Feed stays deduplicated.
- [x] Verify real #536 Feed live and branded Story asset 1080×1920; Buffer currently `hasActiveMemberDevice=False`.
- [x] Site+Social regression 65/65 + compile/diff/Qt VerifyOnly PASS.
- [x] Commit/push hardening exact at `bed7b27a7851a925af6756f70f7bbc5b71ab1845`; exact-SHA Qt PASS/running.
- [x] Fresh Catalog + Production MySQL rollback verified before retry.
- [x] Bounded Batch `desktop_catalog_v85_20260922_221736` published #152/#178 2/2, failed 0.
- [x] Verify active Hero truth + operator digest unchanged + public Product/media HTTP 200 for both; queue=8.
- [x] Close C3 Site/Full-Registration/quota/Hero recovery.
- [ ] External: owner links Buffer mobile + enables/resets push notifications until `hasActiveMemberDevice=True`.
- [ ] Then retry #536 Social Story only; Feed must remain existing/no createPost; finish Link Sticker in Instagram and record truthful Story receipt.

## 2026-09-22 - Phase50.A.2Z-C1/C2 Full Edit + Unified Bulk Completion
- [x] Verify exact clean baseline `494a222b...`; create rollback ref `backup/pre-a2z-full-edit-bulk-completion-20260922`.
- [x] Add top Product Wizard **«✏ ویرایش کامل»** action using mature StageCore unlock authority.
- [x] Full Edit opens all finalized stages without Publish/data mutation or automatic dirty-state change.
- [x] Keep existing per-stage correction path unchanged.
- [x] Extend only Products multi-select Bulk AI preparation to open Commerce in addition to editorial stages; keep Publish locked.
- [x] Reuse factual MakerWorld Source Profile refresh/cached fallback.
- [x] Reuse A2W multi-profile import and preserve manual Profiles.
- [x] Reuse exact-family Filament mapping so Source PLA selects every current Local PLA offer and excludes PETG/PLA-CF families.
- [x] Reuse physical Product-local image SEO rename/finalizer.
- [x] Fill only missing official six Slider core fields; preserve `homepage_slider_enabled`.
- [x] Repair ERR-49-223 Persian Category exact-match bug without weakening ambiguous-category fail-closed behavior.
- [x] New focused 3/3 PASS.
- [x] Related Stage/Image/Profile/Filament/Site 148/149 effective PASS; sole failure = known ERR-49-203 baseline.
- [x] Existing AI/completion/Unified Desktop/Slider 38/38 PASS.
- [x] 6 changed Python files compile; diff-check + Qt VerifyOnly PASS; migration/dependency/Server delta 0.
- [x] Commit/push exact C1/C2 SHA `8629f8b72c416b364a618a5aeebe2dda8a81d440`; Local=GitHub exact.
- [x] Exact-SHA Qt relaunch + widget smoke 2/2 + idle Catalog no-mutation proof.
- [x] Close C1/C2; resume A2Z Catalog Data Completion.

## 2026-09-22 - Phase50.A.2Z ERR-49-221 Product #588 publish-readiness recovery
- [x] Verify current unified worktree/branch/HEAD and clean baseline `0202bdca...`.
- [x] Prove real #588 failure occurred before Batch/FTP/import; no partial Site mutation from this attempt.
- [x] Changed-condition real Bridge probe: health HTTP 200 and publish-readiness HTTP 200 / ready=true.
- [x] Add bounded WAF-challenge retry only for idempotent GET requests; keep POST import single-attempt.
- [x] Add concise persistent-WAF operator error instead of raw HTML dump.
- [x] Focused 13/13 PASS.
- [x] Corrected Publish/SiteConnection regression 86/86 PASS.
- [x] py_compile / diff-check / Qt VerifyOnly PASS.
- [ ] Commit/push ERR-49-221 and verify Local=GitHub exact SHA.
- [ ] Fresh integrity-checked Catalog SQLite backup.
- [ ] Exact-SHA Qt relaunch and live readiness 200/ready=true.
- [ ] Retry only Product #588 once; require one new Batch/start/FTP/terminal ACK chain.
- [ ] Verify Site Product identity/revision, media/Profile/Variant parity and public Product/media HTTP.
- [ ] Keep Host deployment blocked until dedicated reverse tunnel 22024 is healthy; this Windows hotfix needs no Host deploy.

## 2026-09-21 - Phase50.A.2Z-S #609 Instagram transport/acceptance
- [x] Re-read A2N/A2O/A2P/A2Q/A2S + master A2Z-S Social rules.
- [x] Verify Site #42 revision 2 already owns exactly five #609 SEO ProductImages; public HTTP/SHA parity 5/5 PASS.
- [x] Verify Buffer channel connected, provider=Buffer, media host=github_raw, current-ACK Instagram receipts=0.
- [x] Verify policy v4: Primary first, five ALT, 8 bounded hashtags, UTM, nationwide shipping, no false free claims.
- [x] Verify Story policy: 1080x1920 Gold/Navy IRANSans; Highlight target=قطعات سفارشی / final placement operator_required.
- [x] Fresh integrity-checked pre-social Catalog backup.
- [x] Reproduce ERR-49-219 before provider post: Story FTP WinError 10054.
- [x] Remove mandatory Site FTP derivative dependency from github_raw mode while preserving site mode.
- [x] Social regression 35/35 PASS.
- [x] Real #609 local-only render: Feed PNG 5/5 + valid nonblank Story; receipts unchanged at 0.
- [x] Compile/diff/Qt VerifyOnly + first github_raw transport fix commit/push exact SHA `d6b0de52...` -> Local=GitHub.
- [x] Real github_raw rehost -> #609 social-assets commit `3294d817...`; current branch remote exact at `2cc87108...`; public MIME/SHA 6/6 PASS.
- [x] Local-test truthful clickable Story handoff: notification-mode + Link Sticker UTM metadata + notification-ready receipt; Social 36/36 PASS.
- [x] Commit/push Story handoff delta at `bc96c52f...`; exact-SHA Qt acceptance PASS before real send.
- [x] Execute exactly one current-ACK Social attempt: Feed post created once; Story notification post created once.
- [x] Reconcile Feed submitted->sent read-only; no repost. Live Feed: https://www.instagram.com/p/DdjtyiMG8RC/
- [x] Diagnose Story provider error from Buffer Post read-back: no eligible linked mobile reminder device.
- [x] Local-test ERR-49-220 recovery: provider error != ready; historical false-ready/error does not block Story-only retry; Feed stays deduplicated. Social 37/37 PASS.
- [x] Commit/push ERR-49-220 exact at `c064c36f...`; post-send Catalog backup integrity PASS.
- [ ] External prerequisite: link/sign in Buffer mobile + enable reminder notifications for this account.
- [ ] Changed-condition Story-only retry; require provider notification accepted, no Feed recreation.
- [ ] Operator completes Instagram Link Sticker handoff; record truthful Story/Highlight receipt state.
- [ ] Close A2Z-S docs and continue A2Z Catalog completion.

## 2026-09-21 - Phase50.A.2Z #609 Real Media Repair + Publish Gate
- [x] Fresh integrity-checked Catalog + full #609 media rollback.
- [x] Repair real #609 through application ImageCore; no SQL/direct DB hand-edit.
- [x] Real selected=5 and canonical=5 with physical SEO `-01..-05.webp`.
- [x] Preserve old selected source bytes under `source_originals/`.
- [x] Detect and fix false source-drift between archived original and active SEO WebP (ERR-49-218).
- [x] Focused source-drift/promotion/Batch 3/3 PASS.
- [x] Image + Site Publish 51/51 PASS.
- [ ] Compile/diff/Qt VerifyOnly + commit/push exact drift-fix SHA.
- [ ] Exact-SHA Qt relaunch and explicit mark-ready #609.
- [ ] Verify reverse tunnel/Host identity + fresh Production rollback.
- [ ] Same-identity Site Product #42 republish with all five images.
- [ ] Verify five ProductImages, SEO basenames, SHA/public HTTP parity.
- [ ] Changed-revision Instagram Feed + Story; prevent duplicate revision.
- [ ] Resume A2Z Slider completeness/backfill.

## 2026-09-21 - Phase50.A.2Z Physical SEO Filename + Image/Social Authority Hotfix
- [x] Preserve earlier A2Z selected/canonical media + Buffer worktree fixes.
- [x] Make «اصلاح اسم و سئو» rename/promote real Product-local files to unique numbered SEO WebPs under `images/`.
- [x] Archive prior source/cache bytes under `source_originals/` for rollback/provenance.
- [x] Persist exact physical `source_local_file` and remap `local://` identity to SEO basename.
- [x] Update page-extract exact file mappings and make removal/recovery support SEO-named files.
- [x] Enforce duplicate SEO basename fail-closed.
- [x] Direct rename/query-variant/recovery 3/3 PASS.
- [x] Combined Image/Publish/Windows/Social 109/109 PASS.
- [x] Compile/diff/Qt VerifyOnly PASS.
- [ ] Commit/push exact physical-rename SHA and verify Local=GitHub.
- [ ] Relaunch exact-SHA Qt.
- [ ] Fresh Catalog + #609 media backup.
- [ ] Repair real #609 through application authority; verify `images/` physical SEO names and five selected canonical media.
- [ ] Same-identity Site #42 republish; verify every selected public image and basename.
- [ ] Changed-revision Instagram Feed+Story acceptance; no duplicate feed/story.
- [ ] Resume A2Z Slider completeness/backfill after #609 acceptance.

## 2026-09-21 - Phase50.A.2Z Image + Social Authority Hotfix
- [x] Reproduce #609 selected/canonical media drift and duplicate displayed SEO filename.
- [x] Verify 5 unique finalized physical SEO WebPs already exist for #609.
- [x] Make trusted Local Site selection enter canonical Product media.
- [x] Preserve exact URL identity for per-image metadata/SEO slot before canonical fallback.
- [x] Reuse existing registered `social-assets-buffer` worktree.
- [x] Add multi-image Batch regression proving all selected media use unique SEO filenames.
- [x] Focused 9/9 + broad 113/113 + compile/diff/Qt VerifyOnly PASS.
- [ ] Commit/push exact source and verify Local=GitHub.
- [ ] Launch exact-SHA Qt.
- [ ] Fresh Catalog + #609 media backup; repair real #609 through application APIs.
- [ ] Same-identity Site #42 republish; verify all selected public media/SEO filenames.
- [ ] Changed-revision Instagram Feed+Story acceptance with no duplicate post.
- [ ] Resume A2Z Slider completeness/backfill.

## 2026-09-21 - Phase50.A.2Y Lineage Convergence ACCEPTED / CLOSED
- [x] Create clean isolated convergence worktree from A2Y planning head / latest Windows lineage.
- [x] Merge Server/Production closure lineage `e03bdd2b...` with evidence-backed conflict resolution.
- [x] Preserve A2W Source Profiles/dimensions/material mapping, A2X Slider/Image authority, hardened Social, Store authoritative republish, payment/finance and Hero public-media behavior.
- [x] Windows focused A2W/Slider/Image/Social 94/94 PASS.
- [x] Server unified/republish/payment/finance/Hero 52/52 PASS.
- [x] Broad Windows 115/116 with only documented baseline ERR-49-203.
- [x] Compile 46 changed Python files + Django check/no-drift + diff-check + Qt VerifyOnly PASS.
- [x] Correct stale pre-existing mobile Hero test cache assertion to accepted 50.10.0 contract (ERR-49-215).
- [x] Create/push exact convergence merge `f9a9c203ae3a0a5665dbf884ce0c3e4bf761110b`; Local=GitHub.
- [x] Launch Qt from exact pushed unified SHA; process path and responsiveness PASS; Catalog Products/history unchanged.
- [x] Backup and retarget Desktop LNK/CMD to unified worktree after runtime smoke.
- [x] Freeze unified worktree/branch as sole forward development baseline.
- [x] Close A2Y without Catalog or Production mutation.
- [ ] Begin A2Z with fresh Catalog backup and read-only completeness inventory.

## 2026-09-21 - Phase50.A.2Y Lineage Convergence LOCAL_TESTED
- [x] Create clean isolated convergence worktree from A2Y planning head / latest Windows lineage.
- [x] Merge Server/Production closure lineage `e03bdd2b...` with evidence-backed conflict resolution.
- [x] Preserve A2W Source Profiles/dimensions/material mapping, A2X Slider/Image authority, hardened Social, Store authoritative republish, payment/finance and Hero public-media behavior.
- [x] Windows focused A2W/Slider/Image/Social 94/94 PASS.
- [x] Server unified/republish/payment/finance/Hero 52/52 PASS.
- [x] Broad Windows 115/116 with only documented baseline ERR-49-203.
- [x] Compile 46 changed Python files + Django check/no-drift + diff-check + Qt VerifyOnly PASS.
- [x] Correct stale pre-existing mobile Hero test cache assertion to accepted 50.10.0 contract (ERR-49-215).
- [ ] Create/push exact convergence merge commit and verify Local=GitHub.
- [ ] Launch Qt from exact pushed unified SHA.
- [ ] Retarget Desktop shortcut to unified worktree only after runtime smoke.
- [ ] Close A2Y docs and make unified SHA the only forward development baseline.
- [ ] Begin A2Z only after A2Y closure; no Catalog backfill before then.

## 2026-09-21 - AUTHORITATIVE REMAINING WORK — Phase50.A.2Y+

The authoritative remaining-work plan is `docs/phases/PHASE50_A2Y_MASTER_RECONCILIATION_AND_REMAINING_WORK.md`. Historical unchecked boxes below are retained as evidence and are not automatically pending; only items explicitly carried into the master plan remain active.

Current blocking fact: latest Windows `c86c66a11e2c62f8ca219bcb76abc19e5bfdcdbd` and current Server/Production docs head `e03bdd2b718fae3ce030df789c8b9db958d8d8ed` are divergent descendants of merge-base `b1caeba0f20e711b29dfa9e0ff92a2f5186fb08d`.

Remaining sequence:
- [ ] **A2Y** — converge Windows + Server lineages into one tested GitHub head; launch exact-SHA Qt; freeze one forward baseline.
- [ ] **A2Z** — Catalog Slider data completion + Windows operator acceptance; 635 Products total, only 50 currently core-complete, 585 incomplete.
- [ ] **A2Z-S** — changed-revision Site-first Instagram Feed+Story automation + Highlight queue acceptance.
- [ ] **A2Z-W5** — manual/self-produced Product creation.
- [ ] **A2Z-W6** — source video + Site video + Reel/Story handoff.
- [ ] **A2Z-C** — dynamic Post/Tipax/Mahex provider activation on top of existing shipping fallback.
- [ ] **A3** — canonical StorePayment -> secure ZarinPal wiring, Sandbox UAT, then explicitly approved Live activation.
- [ ] **A4** — Torob official Product API integration using real Product/Profile availability and price.
- [ ] **B1** — Google OAuth/local login + Customer account/order-history closure.
- [ ] **B2** — Product Like/Favorite/Comment/verified-buyer Review package.
- [ ] **B3** — customer Telegram Bot/Mini App tied to the same account/order authority; operator notification alone does not count as this feature.
- [ ] **C1-C5** — Accounting Core -> Treasury -> Purchasing/Payables -> Sales/Receivables -> Reports/Close.
- [ ] **D1** — final Windows package/shortcut + large-catalog soak + full Production UAT/release closure.

Completed items that must not be rerun as pending: A2R manual transfer, A2S finance/receipt audit, A2U latest Windows recovery, A2V image authority, A2W W1-W4.1 real data repair, A2X Server parity/Hero persistence, 2026-09-15 Store Reset, and the already-receipted #625 Feed+Story revision.

Exact next: **A2Y lineage convergence**. No new feature or Production mutation before that gate.

## 2026-09-21 - Phase50.A.2X Slider SEO Readiness + Authoritative Re-publish
- [x] Verify exact W4.1 baseline `7f2280e...` and real repaired #628/#625 state.
- [x] Make Slider SEO/media data required for all Products independent of membership checkbox.
- [x] Keep membership operator-only; AI/bulk completion must never enable it.
- [x] Extend multi-select SEO completion from content-only to content + slider.
- [x] Make Slider edits on server-linked Products requeue the same Site identity.
- [x] Remove stale Site SEO preservation fallback; retain exact Desktop media/Profile replacement contracts.
- [x] Focused 33/33 + Server 9/9 + compile/diff/check/no-drift/Qt VerifyOnly PASS.
- [x] Broad current gate reduced to sole known baseline ERR-49-203 failure.
- [ ] Commit/push exact A2X SHA and verify GitHub remote equality.
- [ ] Launch exact-SHA Qt and take fresh integrity-checked Catalog backup.
- [ ] Backfill saved Slider data without AI while preserving all membership checkboxes.
- [ ] Verify #620 and sampled bulk Products in Qt.
- [ ] Guarded Server deploy from GitHub via dedicated reverse tunnel.
- [ ] One controlled same-identity re-publish + Production parity verification.
- [ ] Close A2X docs and continue remaining Phase50 backlog.

## 2026-09-21 - Phase50.A.2W Product Media Truth Sync + Source Profile Import
- [x] Open A2W from A2V closure with rollback ref.
- [x] Define W1 Refresh/Media truth contract and W2 authoritative Site-media contract.
- [x] Add Stage-3 `رفرش رسانه و وضعیت` and separate `دریافت جدید از منبع` action.
- [x] Preserve `ارسال سایت` as the only Site membership authority; refresh never auto-selects visible candidates.
- [x] Add checksum-aware, idempotent Site-media candidate recovery.
- [x] Flush pending Site-selection UI before Ready/Publish to close the timer race.
- [x] Auto-finalize only newly selected/unfinalized media; preserve stale SEO/final-file fail-closed behavior.
- [x] Focused regression 49/49 PASS; broader A2V+A2W+bidirectional gate 83/83 PASS.
- [x] py_compile / diff-check / RUN_QT VerifyOnly PASS.
- [x] Verify Production receiver already enforces exact media count + filename/SHA parity; no Server delta required.
- [x] Take fresh integrity-checked Catalog backup before real #625 Truth Sync.
- [x] Real #625 Truth Sync PASS without publish: DB=2, Local=3, Site-selected=1, live Site=1, mismatch=0, identity unchanged.
- [x] Commit/push exact A2W SHA `ab1e9d1051aba6ff12a8b3c8b1f9bf04fb22be17` and verify GitHub remote exact match.
- [x] Relaunch Qt from exact pushed SHA and smoke the new Stage-3 button on #625; button-level real Bridge truth sync PASS.
- [x] Mark W1/W2 `GITHUB_UPDATED / WINDOWS_RUNTIME_ACCEPTED`.
- [x] W3: inspect factual source-profile evidence for #625 and existing extractor boundaries; exact MakerWorld `__NEXT_DATA__` proves two distinct factual profiles.
- [x] W3: implement `دریافت پروفایل از محصول` with separate Source-fact authority, operator-confirmed deterministic Ledger merge and no invented Brand/price facts.
- [x] W3 focused regression 5/5 PASS; corrected retained W1/W2/A2V/bidirectional regression 83/83 PASS.
- [x] W3 py_compile / diff-check / RUN_QT VerifyOnly PASS.
- [x] Fresh pre-real-W3 Catalog backup integrity PASS: `phase50-a2w-w3-pre-real-625-20260921-102142`, SHA256 `ba7d70b0...64401`.
- [x] Prove #625 `needs_update=1` predates W3 and came from source recovery images 2→5; preserve it.
- [x] Commit/push W3 source `36dbf3cf283fc1e5697091549e930416c671cbe7` and verify GitHub exact SHA.
- [x] Relaunch Qt from exact W3 source SHA and perform real #625 `دریافت پروفایل از محصول` smoke: fresh capture, exactly two factual profiles, no publish/revision/Ledger change.
- [x] Take second pre-import integrity backup, controlled Commerce unlock, import exactly two deterministic source Profiles while preserving manual Profile and zero/blank local commerce facts.
- [x] Verify post-import DB integrity + snapshot and Qt Stage-2 readback: exactly 3 Ledger Profiles, Source count 2, Site #39 revision 11 unchanged, no publish event.
- [x] W4 Local implementation: read-only Source slot → real Local Filament/pricing preview; material family exact-match, explicit HEX/Palette-only color evidence, no localized-name color inference.
- [x] W4 preserves Multicolor factual slots separately; no fake combined Ledger mapping/price before real Local offer selection.
- [x] W4 focused 5/5 PASS; corrected mature Filament/Profile/Commerce + W3/W4 49/49 PASS; retained A2V/W1/W2 media/site 83/83 PASS.
- [x] W4 py_compile / diff-check / RUN_QT VerifyOnly PASS; rollback ref `backup/pre-phase50-a2w-w4-material-mapping-20260921` -> `eda42e84...`.
- [x] Commit/push W4 source `27bb00a1d8a8dd34e033af9cfaba27f37384a0a0` and verify GitHub exact SHA.
- [x] Fresh pre-preview Catalog backup + exact-SHA Qt relaunch + real #625 W4 Preview PASS: 2 Profiles / 3 slots / 48 PLA candidates / exact HEX=0; Source/Ledger/locks/Site #39 revision 11/history unchanged.
- [x] Keep #625 unpublished by W4; preserve failed batch `26aa571c-...` separately with no revision advance.
- [x] W4.1 parse factual Source Description dimensions and bind ordered size evidence only when unambiguous.
- [x] Owner correction: when Source gives exactly one size dimension, copy that numeric value to all three operational Profile axes while preserving factual-vs-owner-rule provenance; Hydra becomes 12×12×12 and 18×18×18.
- [x] Owner correction: Source material family PLA auto-selects/adds every active Local PLA Filament; exact-family matching excludes PLA-CF/HT-PLA-GF/PETG.
- [x] Real Local inventory=16 active PLA; read-only real-state simulation proves #628 gets 16 PLA on both Profiles and #625 Profile 2 repairs to 16 while Profile 1 remains unchanged.
- [x] #625 fallback remains scoped: preserve Profile 1 5×5×5; fill only Profile 2 missing dimensions with estimated 4×4×4.
- [x] Focused 15/15; corrected Commerce/Profile+W3/W4/W4.1 59/59; retained media/site 83/83; py_compile/diff-check/Qt VerifyOnly PASS.
- [x] W4.1 exact GitHub SHA `7f2280e...` + controlled real #628/#625 Profile repair + integrity-checked post snapshot; A2X now owns next runtime/deploy acceptance.
- [ ] After W4.1 real-data acceptance, investigate failed batch `26aa571c-...` as a separate publish-recovery task; do not auto-retry it.

## 2026-09-21 - Phase50.A.2V image authority hardening — PRODUCTION_VERIFIED / CLOSED
- [x] Continue from accepted A2U v8.9.11 ancestry.
- [x] Reproduce #625 revision-10 stale-image path and prove unchanged Production image SHA values.
- [x] Add fail-closed selected-image ⊆ canonical-image authority gate.
- [x] Separate temporary `ویرایش` selection from persisted `ارسال سایت` selection in Qt.
- [x] Preserve persisted Site-selected local images through refetch, including legacy numbered filenames.
- [x] Take integrity-checked revision-10 Catalog rollback and repair only #625 canonical image authority from persisted evidence.
- [x] Stable Image/SEO/Packaging/Republish regression 72/72 PASS; compile/diff/Qt VerifyOnly PASS.
- [x] Commit/push exact source `4e69ed6a5c0996c7249830fbe029cd01460ad5b1` and launch exact-SHA Qt.
- [x] Capture Production #39 revision-10 baseline and live media SHA values.
- [x] Persisted Site selection at acceptance is explicit and non-inferred: exactly `local://04.webp`; Primary is the same image.
- [x] Verify selected-set SEO metadata/current bytes: metadata ready, 36,162 bytes, SHA256 `cf6f0422...c68fff`.
- [x] Perform one same-identity #625 → #39 republish: batch `desktop_catalog_v85_20260921_081158`, UUID `cb51fb28-acd2-45a7-8a86-40ea5268614c`, revision 10 → 11 once.
- [x] Require Local → Batch → Production stored → public-download SHA equality: exact `cf6f0422f0cde915e9203ddbca6564df694fb4b6a97320e1af0e7f4117c68fff`.
- [x] Verify public Product HTTP 200, public image 200/image-webp, one authoritative ProductImage and exactly 3 active current CC Variants.
- [x] Preserve Production source unchanged/clean at `03042d0430ee6e688c992c875f12edc969df103d`; no A2V Host source deploy/migration/restart.
- [x] Record backup-ordering exception instead of creating a duplicate revision: the fresh pre-republish snapshot was missed; verified revision-10 rollback remains available and a fresh integrity-checked post-rev11 snapshot was taken.
- [x] Close CURRENT_STATE / ROADMAP / CHANGELOG / ERRORS / REQUESTS / A2V phase and push closure docs.

## 2026-09-20 - Phase50.A.2U latest Windows recovery
- [x] Identify actual latest Windows lineage at `f1b58645...`.
- [x] Prove image/gallery/SEO/screenshot fix ancestry is present.
- [x] Preserve latest Windows UI while porting only Social v5/Story notification changes.
- [x] Bump operator app to v8.9.11 / build 2026.09.20.1.
- [x] Windows Image/SEO/Republish 74/74 PASS.
- [x] Social/Buffer/Story 35/35 PASS.
- [x] Qt and RUN_QT VerifyOnly PASS.
- [x] Push source candidate `d77dfd95f5d3a9a707f9ad03f2aacff9e69ac2e2`.
- [x] Take fresh atomic Catalog backup before #625 local reconciliation.
- [x] Reverify Site Product #39 revision 9 public page + 2/2 media.
- [x] Reconcile #625 locally without Bridge re-import; uploaded / needs_update=0.
- [x] Retarget Desktop .lnk/.cmd to A2U with rollback backup.
- [x] Real launcher smoke confirms v8.9.11 window.
- [x] Production read-only confirms revision 9, 3 active Variants and 2 images.
- [x] Final documentation commit/push closure prepared on the accepted A2U branch.

## 2026-09-20 - A2Q social sanitizer follow-up

- [x] Preserve rollback branch at pre-fix Windows/Social WIP SHA `21a1ae27...`.
- [x] Fix literal `\\1` punctuation-normalization defect.
- [x] Extend false-free social filtering to Persian `رایگان/مجانی` and bounded English free download/print/shipping forms.
- [x] Drop false-free hashtag candidates atomically and add Caption/hashtag/ALT/Story regressions.
- [x] Commit/push WIP checkpoint `1c77f671c8df1fcce716662339f3057378a96433` and verify exact GitHub read-back/delta.
- [ ] Pull exact WIP SHA on canonical Windows Local and rerun full Social/Buffer/Story regression + Qt VerifyOnly.
- [ ] Promote only the tested selective Social delta to the release lineage; do not merge the divergent historical WIP branch wholesale.
- [ ] Keep #625 revision 8 duplicate guard intact; no repost.
- [ ] Continue A2R payment/finance/admin from existing manual-transfer/ZarinPal/finance foundations.

## 2026-09-20 - Phase50.A.2Q Hero shadow/cache + Instagram SEO v4
- [x] Reverify main Windows branch clean/pushed and Production baseline 36a69e76.
- [x] Inspect owner screenshot and match the dark lower band to the retired Slicebox shadow strip.
- [x] Keep current server template shadow-free; add explicit legacy #shadow CSS/runtime suppression and Hero cache 50.10.0 on release lineage.
- [x] Start Instagram policy v4: Product focus-keyword-first hashtags, 3DPrintHub order copy, nationwide shipping, UTM URL, ALT preservation and false «رایگان» claim removal.
- [x] Complete focused/broad Local regressions and diff-check on both lineages: social 32/32 + Qt VerifyOnly; Hero 19/19 + Django/no-drift/Node/Bash.
- [ ] Commit/push release + Windows candidates and verify exact remote SHAs/rollback refs.
- [ ] Guarded Production Hero deploy through dedicated reverse tunnel and desktop/mobile browser acceptance.
- [ ] Exact-SHA Qt VerifyOnly/relaunch; never repost #625 revision 8.
- [ ] Close A2Q docs and start A2R payment/finance/admin closure.

## 2026-09-19 - Phase50.A.2P Buffer provider-compatible media host
- [x] Verify current Production Hero 50.9 has no legacy shadow/frame DOM/style on a fresh browser.
- [x] Verify #625 / Site #39 revision 8: exactly 3 active CC rows, 0 active legacy rows, 2 current ProductImages.
- [x] Fresh integrity-checked Catalog backup before real Instagram acceptance.
- [x] Verify SEO caption, 2/2 ALT, 8 hashtags, UTM Product URL, nationwide shipping and Highlight target.
- [x] Reproduce Buffer failure with site-hosted compatibility PNG despite public HTTP 200 image/png.
- [x] Prove provider-host boundary by publishing the exact same current PNG derivatives through public GitHub raw hosting.
- [x] Real Feed sent: 6aaed28f6e039ccbc8221fa8 / https://www.instagram.com/p/DdepEh3if0N/
- [x] Real Story sent: 6aaed29a7fcdd8931977c3f1 / https://www.instagram.com/stories/3dprinthub_ir/3989806967019651799
- [x] Add deterministic dedicated social-assets-buffer worktree/branch automation; canonical Site media remains unchanged.
- [x] Add Buffer media-host selector + receipt host/commit audit + append-only submitted->sent reconciliation.
- [x] Reconcile current Feed to instagram_published without repost.
- [x] Focused social 21/21 + Qt VerifyOnly PASS.
- [x] Run broader social suite 31/31 + compile + diff-check + Qt VerifyOnly PASS.
- [ ] Commit/push exact A2P candidate; verify live GitHub SHA and relaunch exact Qt runtime.
- [ ] Close A2O/A2P docs; never recreate #625 revision-8 Feed/Story.
- [ ] Continue remaining Phase50 payment/finance/admin closure and bounded Product/social workflow.

## 2026-09-19 - Phase50.A.2O re-publish resilience + Instagram acceptance
- [x] Verify Production is exact clean `36a69e76...` and Hero 50.9/no-shadow is live.
- [x] Browser-verify desktop Slicebox transition and mobile nonzero Hero/no document overflow.
- [x] Reproduce #625 failed-retry linkage loss on Windows.
- [x] Preserve last verified Site ids/revisions/ACK on failed publish while keeping failure receipt/error.
- [x] Site-publish 19/19 + Instagram/social 27/27 + diff-check PASS.
- [ ] Commit/push exact Windows A2O candidate and verify GitHub SHA.
- [ ] Fresh Catalog rollback; restore only #625 verified Site linkage from pre-failure backup.
- [ ] One official #625 same-identity re-publish against Production 36a69e76.
- [ ] Require Product #39 strict parity, exactly 3 active CC rows, no stale active Variant, current media and public Browser/API PASS.
- [ ] Generate Buffer compatibility PNGs from current verified Site media and submit one Feed+Story.
- [ ] Require provider post ids/external links, ALT/SEO/hashtags/UTM/nationwide-shipping receipt audit and Highlight target queue.
- [ ] Close A2O docs and proceed to the next remaining Phase50 backlog only after these acceptance gates.

## 2026-09-19 - Phase50.A.2M authoritative re-publish replacement
- [x] Reproduce owner regression against real #625 / Site #39.
- [x] Prove revision-7 ACK succeeded while two stale EP49-3F Variants remained active beside three current CC rows.
- [x] Make Windows sales-profile matrix the sole active commerce authority on re-publish; retain stale rows only inactive for history/rollback.
- [x] Add fail-closed post-sync assertions for stale active non-CC Variants and active-profile count.
- [x] Preserve exact-current ProductImage replacement behavior.
- [x] Add explicit Windows local-image import/selection/dirty-state path; existing SEO finalization remains mandatory.
- [x] Compile/check/no-drift + Server 15/15 + Windows image 25/25 PASS.
- [ ] Commit/push exact A2M candidate and rollback refs.
- [ ] Promote only required Site/server delta to Production release lineage.
- [ ] Fresh Host DB/source rollback + guarded reverse-tunnel deploy.
- [ ] Re-publish #625 once and verify exactly three active CC Variants, no stale active variants and current price/weight/material/time.
- [ ] Verify current selected images/public Product media + desktop/mobile Browser QA.
- [ ] Close A2M docs, then resume external Buffer media-ingestion investigation.

## 2026-09-19 - ERR-49-178 Buffer feed compatibility
- [x] Run exactly one real #625 Buffer attempt after Story render fix; no prior social receipt existed.
- [x] Confirm failure is provider media fetch/read: both canonical Product URLs remain public HTTP 200 image/webp.
- [x] Add Buffer-only stable PNG derivative hosting under `/media/instagram/feed/products/<id>/<revision>/`.
- [x] Preserve canonical Site media separately in receipt audit and never replace Product media.
- [x] Normalize extreme aspect ratios without crop and cap width to 1440.
- [x] Compile + Buffer/feed-asset/Story/Instagram focused regression 21/21 PASS.
- [ ] Commit/push exact candidate + rollback ref.
- [ ] Fresh Catalog backup and real #625 compatibility asset preparation.
- [ ] Publish exactly one Feed + companion Story and verify receipts/external links/Highlight queue.
- [ ] Final exact-SHA Qt relaunch + docs closure.

## 2026-09-19 - #625 final launch closure / ERR-49-177 Story render
- [x] Reconcile existing #625 revision-6 ACK after canonical public-media fix; no FTP/Bridge re-import.
- [x] Verify Local #625 is uploaded/clean with strict public HTTP confirmation.
- [x] Create fresh integrity-checked pre-Instagram Catalog backup.
- [x] Browser QA Home/Store/Product on desktop+mobile; canonical media/order UI/no-free-copy checks PASS.
- [x] Create Desktop `.lnk` + `.cmd` launcher targeting tracked `RUN_QT.ps1`.
- [x] Reproduce first social attempt failure before Feed submission: Story screenshot invalid/near-white.
- [x] Isolate Windows Chrome launcher/headless-child race and stale temporary render workspace.
- [x] Use isolated LocalAppData render workspace + PowerShell Start-Process -Wait + stale-PNG removal/poll.
- [x] Real #625 Story 1080x1920 / 1,178,712 bytes / nonblank visual statistics PASS.
- [x] Social/Story/publish regression 53/53 + Qt VerifyOnly + compile/diff-check PASS.
- [ ] Commit/push exact ERR-49-177 candidate and rollback ref.
- [ ] Fresh exact-SHA Catalog backup/runtime verification.
- [ ] Publish exactly one real Buffer Feed + companion Story; verify receipts/external links/Highlight queue.
- [ ] Apply manual-payment Production settings only through an allowed guarded mutation path.
- [ ] Retain current/milestone Host rollback sets, delete redundant deploy backups and record reclaimed bytes.
- [ ] Final CURRENT_STATE/ROADMAP/CHANGELOG/phase closure.

## 2026-09-19 - ERR-49-176 canonical public-media verifier
- [x] Prove receiver strict parity already succeeded for #625 / Site Product #39 revision 6.
- [x] Prove current public Product HTML uses canonical `/media/p/...` rather than only legacy `/media/store/products/...`.
- [x] Accept legacy + canonical public Product media in Windows verification while excluding imported working-media.
- [x] Public-verification focused 3/3 PASS; maintained publish/social regression 40/40 PASS.
- [x] Create rollback `backup/pre-err49-176-public-media-verifier-20260919 @ 6b2536f...`.
- [ ] Commit/push exact Windows checker SHA.
- [ ] Fresh Catalog backup and exact-SHA runtime verification/relaunch.
- [ ] Reconcile #625 Local receipt without another receiver import.
- [ ] Verify Local uploaded/clean + Product #39 public media, then Feed+Story.

## 2026-09-19 - #625 pricing + Instagram Story/Highlight closure
- [x] Reproduce #625 fail-closed pricing mismatch after media-path fix.
- [x] Verify owner-approved PLA defaults from integrity-checked post-default preview: 3.5m/4.5m purchase/sale, 150k print, 50k supervision; preserve per-offer preheat.
- [x] Refresh Windows Product Filament/Profile pricing snapshot before Ready/Publish without reopening Product UI.
- [x] Make Site Desktop-managed pricing match Catalog formula and managed Variants authoritative for public Catalog range.
- [x] Preserve distinct Manufacturer from Brand through Windows Filament save/site payload.
- [x] Server targeted 5/5 PASS + no migration drift; Windows pricing/social/story 19/19 PASS + Manufacturer regression PASS.
- [x] Require companion Story by default with primary verified Product image, IRANSans Gold/Navy 1080x1920, Product link and nationwide shipping.
- [x] Derive approved Highlight target automatically; #625 toys-games -> اسباب بازی; keep Add-to-Highlight operator-required under official Buffer API.
- [ ] Commit/push exact Windows and Server candidates.
- [ ] Restore/verify dedicated reverse tunnel 22024 and deploy exact Server SHA.
- [ ] Fresh Catalog + Production MySQL/Product-media backups.
- [ ] Repair active PLA through Filament Core using owner-approved defaults while preserving other offer facts.
- [ ] Refresh #625 and perform exactly one official mark_ready_many -> publish_many attempt.
- [ ] Read back Product #39 full media/SHA/pricing/Profile/Variant/material/brand/manufacturer/color/weight/time/dimensions and browser verify.
- [ ] Publish real Buffer Feed + companion Story; verify receipts/external links and Highlight target اسباب بازی.
- [ ] Final docs + exact-SHA Qt relaunch.

## 2026-09-18 — Screenshot SEO + source-byte refresh closure
- [x] Reproduce empty per-card SEO fields on manual Screenshot.
- [x] Seed empty single-image SEO editor from Product SEO without changing Site selection.
- [x] Preserve SEO metadata for unselected editable images without making them publish-ready.
- [x] Make `اصلاح اسم و سئو` cover every editable image when no operation subset exists.
- [x] Detect selected source-byte drift after finalization.
- [x] Auto-refinalize only previously-finalized media whose source bytes actually changed.
- [x] Keep genuinely incomplete/unfinalized media fail-closed.
- [x] Focused 41/41 + current-contract 77/77 + broad 145/145 PASS.
- [x] Qt VerifyOnly / compile / Django check / no migration drift / diff-check PASS.
- [x] Commit/push exact candidate `89931e8958b3a738fbfb4b8d65c099124aa24de0`.
- [x] Fresh Catalog backup + exact-SHA Qt relaunch.
- [x] Controlled Product #625 same-identity update -> Site Product #39 revision 5.
- [x] Public Product/media verification with exact Local/Public SHA256 parity.
- [ ] Production application-source deploy only through dedicated reverse tunnel after Host gates pass.

## 2026-09-18 — Image repair + reliable in-place re-publish
- [x] Preserve mature filename authority, Screenshot, Primary/Slider and image membership behavior.
- [x] Replace separate automatic image SEO/renumber controls with `اصلاح اسم و سئو`.
- [x] Operation subset => repair subset; no operation subset => repair all editable Site-selected images.
- [x] Mark uploaded Products dirty after explicit image metadata/renumber/remove/Screenshot and direct Product operator edits.
- [x] Prove Stage/Profile edits still use existing StageCore dirty boundary.
- [x] Prove Stage-7 single-product Send requeues uploaded Product through guarded publish flow.
- [x] Strengthen server E2E: changed title/description/SEO/image re-import updates same Product PK and same Asset.
- [x] Image 22/22 + Windows/Site 59/59 + Server E2E 3/3 + Django profile/sync 23/23 PASS.
- [ ] Final VerifyOnly/check/no-migration/diff gate.
- [ ] Commit/push exact candidate + fresh Catalog backup + exact-SHA Qt relaunch.
- [ ] Restore dedicated reverse tunnel only on verified local Router.
- [ ] Deploy from GitHub; verify Product Admin 504, duplicate Filament removal and Hero.
- [ ] Publish #152 to Site, then Instagram #152; never duplicate #309/#301.

## 2026-09-18 — Site-first Product/Admin release
- [x] Reproduce Production duplicate Filament card block and prove current source already omits it.
- [x] Isolate Product Admin 504 to ProductVariant inline query/HTML explosion.
- [x] Remove only ProductVariant inline; preserve dedicated Variant/Profile admin and other Product inlines.
- [x] Enforce ASCII/English Profile name + size identity and verify real Product #625 resolves to Standard/Standard with 64 material options preserved.
- [x] Repair Instagram canonical media parser for real Site ACK count shape and Product-owned media filtering.
- [x] Site/Admin 17/17, Catalog/Instagram/Qt 82/82, Hero 27/27, compile/check/drift/diff-check PASS.
- [ ] Commit/push exact candidate and verify remote SHA.
- [ ] Fresh Catalog backup + exact-SHA Qt VerifyOnly/relaunch.
- [ ] Restore dedicated reverse tunnel on the verified local-router path; do not use MobinHoust or alternate Host access.
- [ ] Guarded Production deploy from GitHub + Product edit 504/Home/Product detail browser verification.
- [ ] Publish Product #152 Site-first, then one corrected Instagram feed/Story; do not duplicate #309/#301.

## 2026-09-18 — Filename/four-row runtime promotion
- [x] Commit/push runtime `aaa5cb9f6d743becf3f1588501733ae835bd7451`.
- [x] Fresh Catalog backup with source/backup integrity `ok`, 635 Products.
- [x] Preserve concurrent Instagram/Buffer work by launching from clean exact-SHA worktree instead of reset/stash.
- [x] Relaunch Qt from clean `aaa5cb9...` worktree; visible child responsive.
- [x] Post-launch Product #301 read-only SEO verification PASS.
- [ ] Owner visual smoke.
- [ ] Production remains unchanged until dedicated reverse tunnel is healthy.

## 2026-09-18 — Image filename/scroll correction
- [x] Verify Product #301 real metadata before changes.
- [x] Restore source English title as filename authority only.
- [x] Preserve Alt/Title/Caption/Keywords/AI/operator override behavior.
- [x] Force four-row scroll canvas even with zero/few images.
- [x] Focused 4/4 and broader 97/97 regressions PASS.
- [x] Compile/diff-check/Qt VerifyOnly PASS; no migration delta.
- [ ] Commit/push exact candidate.
- [ ] Fresh Catalog backup and exact-SHA Qt relaunch.
- [ ] Owner visual smoke.
- [ ] Production remains blocked until dedicated reverse tunnel is healthy.

## 2026-09-18 — Stage-3 3×3 runtime promotion
- [x] Commit `a52cd52a18a119f9aa2940ebc00f588828d1a558`.
- [x] Push and verify exact Local/GitHub SHA.
- [x] Fresh Catalog backup; source/backup integrity `ok`, 635 Products.
- [x] Relaunch canonical Qt from exact pushed source; visible child window responsive.
- [x] Post-launch Catalog read-only integrity PASS.
- [ ] Owner visual smoke of 3-column compact cards / filename / controls.
- [ ] Site deploy remains blocked while dedicated reverse tunnel `127.0.0.1:22024` is down; no cPanel/browser fallback.

## 2026-09-18 — Stage-3 3×3 owner correction
- [x] Restore three image cards per row.
- [x] Make review cards smaller instead of enlarging individual images.
- [x] Keep SEO filename visible on every card.
- [x] Put Previous/Next/SEO/Delete in one compact row per card.
- [x] Show three full rows / nine cards at once in a 670px gallery viewport.
- [x] Keep fourth row and beyond scrollable; wheel over image still scrolls.
- [x] Preserve all image operations/modes/callbacks.
- [x] Focused 4/4 + maintained 68/68 Qt regressions PASS.
- [ ] Commit/push exact candidate and relaunch Qt from pushed SHA.
- [ ] Owner visual smoke.
- [ ] Site deploy only through dedicated reverse tunnel after `127.0.0.1:22024` + authenticated Host gates pass; no cPanel/browser fallback.

## 2026-09-18 — Active design-only UI + Example-4 homepage Hero
- [x] Preserve all Stage-3 image operations/modes; change layout only.
- [x] Put eight Stage-3 image actions in one compact row with text fitting inside controls.
- [x] Put Save/Finalize/Unlock/Previous/Next in one compact bottom row.
- [x] Give freed vertical space to image gallery (650px min; real viewport 634px) while remaining inside 1920x1032 working area.
- [x] Qt regression 67/67 + Qt VerifyOnly/compile/diff-check PASS.
- [x] Keep official vendored Slicebox engine and current HomepageHeroSlide data.
- [x] Match official Example-4 runtime: random right/vertical cuboids + disperse 30; remove extra Play/Pause.
- [x] Use 3DPrintHub background, reference arrows/shadow/caption and screenshot-requested dots.
- [x] Fix hidden-lazy Slicebox startup deadlock by eager-loading the four Hero images.
- [x] Browser real-runtime smoke: 4 slides, 42px arrows, 4 dots, 416px slider, 5 cuboids/30 faces, slide 0 -> 1, zero browser errors.
- [x] Hero/Django selected gate 27/27; check/no-migration PASS.
- [ ] Commit/push exact accepted candidate.
- [ ] Fresh Catalog backup and exact-SHA Qt relaunch.
- [ ] Verify live 3DPrintHub tunnel/Host Production truth read-only.
- [ ] Deploy homepage from GitHub only after Host backup/rollback/readiness gates pass.
- [ ] Verify Production DOM/assets/3D transition visually.

## 2026-09-18 — Stage-3 scroll runtime promotion
- [x] Commit hotfix `00f16237cf27eea2cdf7bef97fa7cc140014c947`.
- [x] Push and verify Local/GitHub exact SHA.
- [x] Fresh Catalog backup with source/backup integrity `ok`.
- [x] Verify runtime source tree clean for `catalog_center/qt6` + `catalog_center/app` while preserving unrelated Story work.
- [x] Relaunch canonical Qt runtime; visible child window responsive.
- [ ] Owner visual smoke: wheel on image reaches filename/select/edit/delete and Stage 3 no longer clips below screen.

## 2026-09-18 — Stage-3 visibility/scroll hotfix
- [x] Reproduce real geometry with Product #628 copy and prove internal scrollbar range exists.
- [x] Prove wheel on preview fails before fix while wheel on viewport succeeds.
- [x] Keep large cards/previews; reduce only gallery container minimum so the Wizard fits the 1920x1080 working area.
- [x] Forward preview wheel delta into the gallery vertical scrollbar.
- [x] Real-copy geometry/wheel probes PASS.
- [x] Maintained Qt/Gallery/Wizard/Screenshot regression 67/67 PASS.
- [x] Compile, scoped diff-check and Qt VerifyOnly PASS.
- [ ] Commit/push exact hotfix without staging unrelated Instagram Story work.
- [ ] Fresh Catalog backup and exact-SHA Qt relaunch.
- [ ] Owner visual smoke on Product #628.

## 2026-09-18 — Stage-3 image runtime promotion
- [x] Commit runtime/docs candidate `91d4c188aa57c125e46d45f39a70d913085dcf6c`.
- [x] Push and verify Local/GitHub exact SHA match.
- [x] Create fresh canonical Catalog online backup with source/backup integrity `ok`.
- [x] Run exact-SHA `RUN_QT.ps1 -VerifyOnly`.
- [x] Launch canonical Qt runtime from pushed source; visible child window verified.
- [x] Post-launch Catalog read-only integrity/Product-count/#628 selection verification.
- [ ] Owner visual smoke on Product #628.
- [ ] Keep Production unchanged until separate Host/tunnel/deploy gates are explicitly resumed.

## 2026-09-18 — Active owner gate: Stage-3 image workspace
- [x] Verify Local/GitHub base `e076efa...` and push rollback branch before edits.
- [x] Separate temporary bulk-operation image selection from persistent `در سایت` membership.
- [x] Make trusted legacy numbered Product images selectable/editable/recoverable without inventing remote source URLs.
- [x] Enlarge the image review/scroll workspace and compact the toolbar/control typography.
- [x] Show deterministic SEO filename with source filename retained as secondary evidence.
- [x] Preserve operator-selected image count during SEO edit/renumber; keep publish-time default dedup unchanged.
- [x] Put verified Product main image first in Instagram/Buffer feed media.
- [x] Real-copy acceptance Product #628: 11 -> 11 selected, unique SEO names, Primary preserved, 15/15 real gallery items editable.
- [x] Targeted 9/9, maintained 80/80, expanded 107/107, compile/diff-check/Qt verify PASS.
- [ ] Commit/push exact candidate and verify remote SHA.
- [ ] Fresh canonical Catalog backup and exact-SHA Qt relaunch.
- [ ] Owner visual smoke on Product #628.

## 2026-09-18 — Immediate Screenshot-button repair
- [x] Prove on real Product #628 whether capture executes: multiple fresh Screenshot files + DB `local://` entries exist.
- [x] Identify display-only regression in the A2L numbered-image resolver rather than changing capture/naming again.
- [x] Add failing regression for hidden manual Screenshot + numbered-slot identity theft.
- [x] Patch only the Qt resolver; preserve Screenshot capture/naming/crop, SEO, button wiring and gallery sizing.
- [x] Maintained Qt/Gallery/Wizard/Screenshot gate 61/61 PASS; launcher verify, compile and diff-check PASS.
- [x] Copy-of-real Catalog acceptance PASS with integrity-checked backup; canonical Catalog untouched.
- [x] Commit/push runtime SHA `bab82e89e9e27722b8b1000a959b1161ee84e038` and verify Local/GitHub exact match.
- [x] Relaunch one canonical Qt runtime from that exact pushed SHA; live Qt child is responsive with the expected Catalog Center window title.
- [ ] Owner-smoke the Screenshot button on the same Product and confirm the newly captured Screenshot appears in Stage 3.

## 2026-09-18 — Immediate owner correction: Stage-3 image review only
- [x] Restore pre-`d564386` image button workflow, Screenshot action path, recover-limit behavior, slider panel, AI visibility and normal window geometry.
- [x] Enlarge only Product image cards/previews and preserve vertical scrolling.
- [x] Revert the rejected filename-display override; preserve mature image filename and Screenshot capture/naming behavior exactly.
- [x] Rerun focused Qt/Gallery/Wizard/Screenshot regression with only sizing delta present: 60/60 PASS.
- [x] Commit/push corrective runtime SHA `20f483af983cad550b1e2473751798daf0e8d39b`, verify remote match, and relaunch one visible Qt runtime from the canonical repository.
- [ ] Owner visual smoke on the affected Product: larger image surface with original controls, original filenames and original Screenshot behavior.

## 2026-09-18 — Active execution: Phase50.A.2L owner QA / Filament identity repair
- [x] Push/relaunch exact A2L candidate `4375c00...`.
- [x] Verify real #628 image workspace: 10 local images, 2-column large-card grid, reachable vertical scroll.
- [x] Audit real full Filament sync: 71 rows, 8 complete identities, 63 legacy rows missing Brand.
- [x] Keep sync fail-soft; never invent Brand for incomplete legacy rows.
- [x] Add selected-row registered-Brand repair workflow and verify copy-of-real-Catalog repair.
- [x] Maintained A2L scoped Catalog gate 57/57 PASS after follow-up.
- [ ] Commit/push follow-up exact SHA and relaunch Windows app from that SHA.
- [ ] Owner/real-data repair of factual Brand values for remaining legacy rows, then full Site sync.
- [ ] Recover dedicated 3DPrintHub reverse tunnel; Host read-only gate + backup/readiness.
- [ ] Build Production release from verified Production/A2K lineage, deploy A2K+A2L from GitHub, apply guarded manual-payment seed, and verify public Hero/Store/receipt/notification paths.

## 2026-09-17 — Active execution: Phase50.A.2K
`A2K SOURCE/RELEASE ACCEPTED -> RESTORE 3DPRINTHUB TUNNEL -> HOST MYSQL/READINESS GATE -> VERIFIED BACKUP -> GITHUB RELEASE DEPLOY -> DESTROY OLD HERO DATA + SEED 4 A2K SLIDES -> STATIC/RESTART -> PUBLIC VISUAL/DOM VERIFY -> DOC CLOSE`
## 2026-09-17 - Canonical Qt launch + empty Production Store handoff
- [x] Promote and verify the modern Windows Qt launcher on GitHub: `b116a27...`.
- [x] Preserve unrelated Social/Buffer WIP on separate GitHub branch `wip/phase50-social-buffer-20260917 @ ea8a156`; restore primary Product runtime to clean exact source.
- [x] Launch one canonical Qt v8.9.10 instance against the real Catalog DB; verify integrity `ok`, 635 Products and current Filament inventory.
- [x] Re-run exact resend/update/recreate contracts: 5/5 PASS.
- [x] Authenticated reverse-tunnel health and Production read-only preflight PASS.
- [x] Create fresh verified MySQL + 37-media rollback backup for exact live Store counts.
- [x] Execute canonical Store reset: 8/2011/29 -> 0/0/0 with zero Orders/Inventory movements and master/source data preserved.
- [x] Re-apply and verify A2J safe Hero: four active source assets 119/120/135/136; public Home/CSS/JS HTTP 200 and four rendered slides/dots.
- [x] Verify Production migration plan is empty.
- [ ] Owner selects finalized Products for real publication from the Windows app; validate strict ACK, public media, Variant and Cart per Product.

- [x] Final receiver gate after cleanup: publish readiness `true` with zero blockers; reset preflight blocked only because Store is already empty.
## 2026-09-17 - Correct Qt Windows operator launch + immediate Product entry
- [x] Verify Local repository/branch and live GitHub are exact at pre-change `6a3a51aacdccff69a4999c4a470cb10807ceb648`.
- [x] Preserve existing dirty Local work instead of reset/delete; archive `.tmp_*` evidence outside the repo and backup the two modified tracked files.
- [x] Prove root cause: prior `RUN_DEBUG.ps1` launches legacy `launch.py`; new Product/Filament application is `qt_launch.py`.
- [x] Create rollback branch `backup/pre-windows-qt-operator-launch-20260917`.
- [x] Add explicit `catalog_center\RUN_QT.ps1` with canonical Catalog path, Qt verify gate and detached Qt launch.
- [x] Preserve legacy `RUN.ps1` / `RUN_DEBUG.ps1` unchanged as rollback-only launchers.
- [x] Corrected focused Windows acceptance: 40/40 PASS across launcher/Qt/republish/image contracts; Qt verify, launcher verify, touched compile and diff-check PASS. Retired-module harness names are recorded under ERR-49-151.
- [ ] Commit/push exact candidate and verify live GitHub SHA.
- [ ] Relaunch Qt from that pushed SHA and verify window/process + Catalog integrity.
- [ ] Reverse-tunnel read-only Production Store/receiver/reset eligibility verification.
- [ ] If eligible, fresh rollback backup then canonical Store reset to empty; verify A2J four safe Hero slides and zero old Store Products.
- [ ] Keep Product republish/update path available for owner Product entry immediately after reset.

## 2026-09-16 - Windows image ordering + launch readiness
- [x] Reverify canonical Local/GitHub at pre-change `551f70624536857ab36ba004404298abb503d180` and preserve dirty-state evidence without reset.
- [x] Push rollback branch `backup/pre-phase49-3i47-image-reorder-20260916` at the exact pre-change SHA.
- [x] Add explicit previous/next controls below each trusted selected Product image.
- [x] Preserve mature Primary=slot-1 authority; reorder only secondary selected images and keep Slider/Alt/metadata bound by URL.
- [x] Rebuild deterministic SEO WebP numbering after each actual reorder and mark uploaded Products for guarded republish.
- [x] Dedicated Phase49.3I.47 12/12, Image+Publish 27/27, broader Windows 87/87, compile/diff-check PASS.
- [ ] Commit/push exact runtime+docs and verify live GitHub SHA.
- [ ] Create fresh checksum/integrity backup of canonical Catalog SQLite.
- [ ] Verify current Site Receiver + FTP/Bridge readiness without exposing credentials.
- [ ] Run pushed `qt_launch.py --verify-only`, then launch exact approved SHA and verify process + Catalog integrity.
- [ ] Record final Windows runtime/backup/receiver evidence and owner-ready Product/image entry status.

## 2026-09-15 - Product entry / single Product publish gate CLOSED
- [x] Add direct Ready + Send actions inside Product Wizard Stage 7.
- [x] Focused/broader Windows regressions PASS: 21/21 and 71/71.
- [x] Commit/push Windows runtime `6e306e5353a6d6cd9d434894870839e533fa9622` and relaunch Catalog Center.
- [x] Fresh Catalog + Production MySQL/media rollback backups before real publish.
- [x] Publish exactly Catalog #628 through Batch/FTP/Bridge/public HTTP; published=1, failed=0.
- [x] Production Product #21 active with 190/190 orderable Variants and 2 Product images.
- [x] Browser guided selector + Cart wiring PASS; Variant 1837, quantity 1, POST intercepted before server write.
- [x] StoreOrder remains 0 after acceptance.
- [ ] Owner may now enter/publish Products; incomplete Product gates remain fail-closed.

## 2026-09-15 - Urgent Product entry/publication recovery
- [x] Verify canonical Windows Catalog integrity and real Ready queue.
- [x] Verify Site publish readiness = true/no blockers and FTP connection PASS.
- [x] Prove 12/15 currently Ready Products pass actual publish preflight; keep #40/#43/#146 blocked on factual media/slider gaps.
- [x] Add direct single-Product Ready + Send-to-Site controls inside Product Wizard Stage 7.
- [x] Reuse mature Batch/FTP/Bridge/public-HTTP strict ACK path; no parallel publisher.
- [x] Run 71 related Qt/Product/Site regressions PASS.
- [ ] Commit/push exact hotfix and verify GitHub head.
- [ ] Fresh Catalog + Production MySQL backups before real publish.
- [ ] Publish exactly one known-good Product (#628) and verify public Product/media/Variant/Cart.
- [ ] Launch pushed Catalog Center for owner and continue bounded Product entry/publication.

## 2026-09-15 - Phase50.A.3 secure ZarinPal current-API gate
- [x] Audit mature Phase30 quote-payment security/idempotency architecture from source.
- [x] Read-only verify Production payment state: env/site gateway disabled, no Merchant ID, Sandbox on, zero gateway Payment/Ledger rows.
- [x] Re-verify current official ZarinPal v4 live/sandbox hosts and Host outbound TLS.
- [x] Update live request/verify/StartPay defaults and remove request-only currency from Verify payload.
- [x] Add live/sandbox endpoint and Verify-payload regressions; payment suite 17/17 PASS.
- [x] Classify broad-suite 6F/9E as pre-existing by exact baseline worktree reproduction.
- [x] Add guarded no-migration/no-DB-write/no-collectstatic/no-enable Production runner from `b1caeba...`.
- [ ] Commit/push exact candidate and verify live GitHub SHA.
- [ ] Guarded reverse-tunnel Production deployment + runtime/public verification.
- [ ] Wire canonical StorePayment checkout into the mature secure gateway architecture before merchant activation.
- [ ] Configure/test legitimate Merchant ID in Sandbox, then separately approve Live activation.

## 2026-09-15 - CLIENT HANDOFF GATE CLOSED
- [x] Local/GitHub exact clean head verified: `b1caeba0f20e711b29dfa9e0ff92a2f5186fb08d`.
- [x] Dedicated reverse tunnel/bridge authenticated and Host identity verified.
- [x] Production exact clean head verified at the same GitHub SHA; MySQL identity/readiness/empty migration plan PASS.
- [x] Guarded client-handoff deployment completed with rollback bundle `20260915-094656-phase50-client-handoff`.
- [x] Fresh Store-reset MySQL/media manifest backup verified at `20260915-094827-store-product-reset`; 71/71 Product media hashes PASS.
- [x] Eligible imported Store catalog reset completed: 20 Products / 1607 Variants / 51 ProductImages -> 0 / 0 / 0; master/source/Portfolio/Hero preserved.
- [x] Production browser QA: Hero 50.3.0 desktop 3D cuboid transition PASS; mobile fallback/390px no-overflow PASS; Store empty-state PASS.
- [x] Client-handoff milestone complete.
- [ ] Next Phase50 engineering: re-enter the planned commerce/finance roadmap from this clean handoff baseline; do not repopulate Store until a Product is intentionally re-approved/published.

## 2026-09-15 - Host transport recovery
- [x] Restore dedicated 3DPrintHub reverse tunnel and verify Windows `127.0.0.1:22024` listening.
- [x] Verify authenticated Host bridge identity/base.
- [x] Verify one-minute cPanel watchdog cron entry is present and uses `flock` + repository bootstrap.
- [ ] Deploy current GitHub handoff head through the reverse tunnel.
- [ ] Create fresh MySQL/media reset backup, execute eligible Store reset, and complete Production browser QA.

## 2026-09-15 - Client handoff transport blocker
- [x] Push application candidate and dedicated guarded deploy runner.
- [x] Prove Local Hero 50.3.0 in Chromium and Store Reset regression gates.
- [x] Diagnose reverse tunnel: Host bridge state exists; authorized-key fingerprint matches; Windows loopback 22024 closed.
- [x] Prove watchdog/cron stopped updating and FTPS has no command channel.
- [x] Prove stored FTP credential is not accepted by cPanel API and no `.cpanel.yml`/GitHub auto-deploy exists.
- [ ] Restore only 3DPrintHub cPanel watchdog/bootstrap execution.
- [ ] Run guarded GitHub deploy, verified reset backup, Store Reset and Production browser acceptance.

## 2026-09-15 - Client handoff deploy runner checkpoint
- [x] Push application candidate `dd1e770...` to canonical branch.
- [x] Browser-verify Local Hero 50.3.0: 1440x823 full-bleed, real temporary 3D cuboids, mobile fallback.
- [x] Add dedicated exact-baseline handoff deploy runner.
- [x] Runner bash syntax, diff-check and secret scan PASS.
- [ ] Commit/push runner and require GitHub checks green.
- [ ] Restore PrintHubTunnel only; verify Host branch/HEAD/worktree/MySQL/readiness.
- [ ] Run guarded GitHub deploy, create verified MySQL/media reset backup, reset Store if eligible, then Production browser acceptance.

## 2026-09-15 - Client handoff delivery gate
- [x] Re-read repository rules/state/errors/paths/active Phase from source of truth.
- [x] Preserve the existing dirty worktree and inspect Store Reset, Hero, publish/Instagram and timeout-reconciliation deltas instead of resetting them.
- [x] Complete fail-closed Store Reset API that preserves source assets/master data/Portfolio/Hero/history and refuses protected/manual/inventory-conflicted state.
- [x] Add repository-owned Store Reset backup-manifest/media helper with exact MySQL identity and checksum boundaries.
- [x] Upgrade Home Hero candidate to full-screen native 3D cuboids with random horizontal/vertical transitions and mobile/reduced-motion fallback.
- [x] Verify Site→Instagram order remains Site publish/public URL first, Instagram second; no social post without configured Professional credentials.
- [x] Local gates: 8/8 Store Reset+Hero, 57/57 broader Qt/Publish/Instagram/SiteConnection, compile, Node syntax, Django check, no drift, empty migration plan, diff-check PASS.
- [ ] Commit/push exact candidate and verify live GitHub SHA.
- [ ] Re-establish authorized reverse Host transport and verify Host root/branch/HEAD/worktree/MySQL/readiness read-only.
- [ ] Deploy only the GitHub candidate with fresh source/env/static rollback evidence.
- [ ] Generate fresh real MySQL gzip + Store Reset manifest/media backup and verify hashes/counts.
- [ ] Run Production reset only if preflight is eligible; verify Store Product/Variant/Image count reaches zero and protected/master/source/Hero data is unchanged.
- [ ] Browser-verify Production Hero desktop 3D transition, mobile fallback and public Home/Store HTTP after reset.
- [ ] Update final docs with deployed SHA, backup root, reset counts and browser acceptance before client handoff.

## 2026-09-14 - ERR-49-144 GitHub CI correction follow-up
- [x] Runtime/docs commit `1a5ba6a...` pushed and remote verified.
- [x] Fresh checksum-identical Catalog backup created and SQLite integrity/count parity verified.
- [x] Pushed Qt runtime launched successfully; startup structural contract PASS and DB post-launch quick check PASS.
- [x] Three GitHub workflows PASS on `1a5ba6a...`.
- [x] Diagnose Qt6 CI failure as stale three-column test expectation, not runtime regression.
- [x] Update parity test to the accepted four compact columns.
- [x] Run exact failed CI foundation/parity suite locally: 23/23 PASS.
- [ ] Push corrective test/docs checkpoint and require GitHub Qt6 CI PASS.
- [ ] After green CI, preserve the currently running owner foreground app for visual acceptance.

## 2026-09-14 - ERR-49-144 Published/gallery regression
- [x] Preserve `workflow_status=uploaded` Products in the Published lifecycle even when Local edits set `needs_update=1`.
- [x] Preserve republish discoverability through the existing Work Queue at the same time.
- [x] Count/render actual locally-displayable Product media instead of raw source URL count.
- [x] Reuse legacy numbered local WebPs read-only without weakening strict publish media mapping.
- [x] Disable mutating controls for legacy display-only files that lack trustworthy source URL identity.
- [x] Restore a compact four-column Product image gallery.
- [x] Verify real Catalog: Published=19; #33=16 real files; #34=25; #63/#628/#634=2 each.
- [x] Run focused + adjacent Qt/Crawl/Publish regression: 77/77 PASS.
- [ ] Commit/push exact isolated delta and verify live GitHub SHA.
- [ ] Create fresh Catalog rollback backup and relaunch the pushed Qt runtime for owner foreground acceptance.

## 2026-09-14 - Product #303 bounded sales candidate
- [x] Audit all approved non-uploaded candidates on a copied Catalog DB.
- [x] Identify #303 as the only candidate with no operator-only missing facts.
- [x] Preview keyword backfill from existing finalized image metadata on copied DB + copied Product folder.
- [x] Preview Content/Images finalization, media gate and publish gate PASS.
- [ ] Create fresh canonical Catalog + Product-media rollback backup.
- [ ] Apply the same StageCore repair to canonical #303 and verify no unrelated Product changed.
- [ ] Mark ready, receiver/FTP/Bridge gate, publish exactly #303, then strict public Variant/orderability/cart acceptance.

## 2026-09-14 - Sales expansion checkpoint: Product #62 accepted
- [x] Repair Catalog #62 with one canonical factual Profile using the mature CommerceCore ledger path.
- [x] Preserve existing Host/Site identity: asset 140 / Product 18.
- [x] Create fresh Catalog + Production MySQL rollback backups before writes.
- [x] Republish #62 through Batch 8.5 -> FTP -> Bridge; strict visibility/orderability/public-media checks PASS.
- [x] Real Chromium Cart acceptance: Variant 884, 500,000 Toman, quantity 1; POST intercepted before server.
- [x] Confirm current orderable Production set: Site Products 16, 17, 18.
- [ ] Deploy GitHub-approved `07772ca...` stale-public lifecycle fix through an authorized Host execution path.
- [ ] Republish #84; keep Product 19 inactive/noindex while selected black-matte stock remains zero.
- [ ] Audit the next factual ready subset; do not guess #43 Material/Color/image metadata.

## 2026-09-14 - ERR-49-138 stale-public gate
- [x] Prove #18/#19 active but 0 orderable Variants on Production.
- [x] Add committed deactivation/noindex path for already-public non-orderable Products.
- [x] Importer reports `publish_incomplete` and excludes non-visible Product from published count.
- [x] 19 focused E2E/visibility/Variant tests + no-drift PASS.
- [x] Commit/push ERR-49-138 source from exact `70a74e6...` baseline to GitHub (`07772ca...`).
- [x] Repair #62 with factual fixed-price/PLA-white/Profile data and republish; Chromium Cart acceptance PASS.
- [ ] Deploy `07772ca...` to Production through an authorized Host mutation path.
- [ ] Republish #84 fail-closed; keep off Store until selected black-matte inventory is real.

## 2026-09-14 - Active sales gate: ERR-49-135 real orderability
- [x] #628/#634 strict ACK + live customer Cart acceptance.
- [x] Detect #62/#84 false-positive visibility: public but no orderable Variant.
- [x] Local contract fix: canonical Profile required before FTP + shared Store orderability + visibility orderable gate.
- [x] Local compile/tests/check/no-drift/runner syntax gates PASS.
- [x] Commit/push exact orderability hotfix and verify GitHub head/CI.
- [x] Guarded no-migration Production deploy from exact `6569e5a...` to `70a74e6...`.
- [x] Backup Catalog and repair/re-publish #62 same identity; live Cart PASS.
- [ ] Repair/republish #84 only when lifecycle fix is live; current selected black-matte stock is zero.
- [ ] Keep #43 blocked until factual Material/Color and current image metadata are complete.

## 2026-09-14 - Sales launch gate passed
- [x] Deploy owner-license Host parity at `6569e5a...`.
- [x] Fresh Catalog backup before bounded retry.
- [x] Publish exactly #628/#634: strict ACK/public media/Product visibility PASS.
- [x] Real browser Variant/price/Cart wiring PASS with POST intercepted before server.
- [ ] Audit remaining ready #43/#62/#84 against current factual gates.
- [ ] Publish only passing subset, then verify strict ACK/public pages/media/cart before any larger batch.

## 2026-09-14 - Active sales-unblock gate: ERR-49-131 owner-license Host parity

The first bounded two-Product publish exposed a contract mismatch, not a legal-status rewrite requirement. Project owner policy already marks every reviewed Catalog source/license stage through explicit `source_license_owner_approved`; Windows readiness/export honors it, while the Host importer/conversion/visibility path ignored it and returned `review_required` for #628/#634. Local hotfix preserves raw license evidence and honors the separate owner approval at every Host gate. Automated Site/Catalog/no-drift/deploy-runner gates PASS. Next: GitHub-first no-migration Production promotion from `44a7be9...`, then retry only #628/#634 from a fresh checksum Catalog backup. Broader Product publishing remains bounded until both receive strict Store-visible ACK and live cart verification.

## 2026-09-14 - Controlled Product gate PASS; bounded publishing unlocked

Production is now exact clean `44a7be9...` with the ERR-49-125 Product-owned public-media fix and A2I seven-slice Hero deployed through verified backup/ff-only/collectstatic/restart gates. Desktop/mobile Hero browser QA, public Bridge/media, strict stored ACK for Windows Product #63 -> Site Product #15, canonical Variant 618 selector and intercepted no-write Cart POST all PASS. The one-Product prerequisite that blocked broader publishing is closed. Next: publish only a bounded small set of factually ready Products with the same strict ACK/public-media/cart verification, while continuing Phase50 finance/payment/admin work.
## 2026-09-14 - A2I + Bridge public-media combined Production gate

The A2I 3D Hero is already committed/pushed at `b1bbdee...`, while Production remains clean at A2H source `443d1b70...`. The pending ERR-49-125 Bridge public-media fix and A2I static assets must move together because the old Bridge-only runner forbids collectstatic. A new combined fail-closed runner is Local-tested: exact baseline/live target/ff-only guards, MySQL/readiness/empty-plan checks, verified source/env/static backup, collectstatic with hash equality, Passenger restart, authenticated Product #15/Hero public-media verification and live A2I static/Home markers. No migration or DB write is allowed. Next: commit/push -> GitHub-first deploy -> Production browser Hero + Product #63 selector/cart/strict ACK -> bounded bulk only after PASS.
## 2026-09-13 - A2G Bridge media hotfix deployment gate

A dedicated fail-closed Production runner is Local-tested for the ERR-49-125 public-media serializer fix. It requires exact clean Host baseline `443d1b70...`, live target equality and ff-only ancestry, forbids migration/dependency/settings drift, creates verified source/environment rollback evidence, performs no DB migration/write or collectstatic, restarts Passenger and verifies Product #15/Hero use only Product-owned public WebPs. Next: commit/push -> guarded Host deploy -> Product #63 selector/cart/strict ACK -> bounded multi-product publish.

## 2026-09-13 - A2G controlled Product acceptance: public Bridge media hotfix

Product #63 reached Production with valid Product-owned WebP gallery files, but the unified Bridge read contract still serialized ImportedPrintAsset working-media URLs. A narrow no-migration fix now maps imported image identity to Product-owned public gallery media and applies the same rule to Hero selected media. Local focused regression is green and the fix is on live GitHub at `d830a9af05d768f9b81568a0665a74f59e864a34`. Next: guarded no-migration Host promotion -> authenticated Bridge/public HTTP verification -> Product #63 guided cart + strict ACK. Bulk remains blocked until that acceptance passes.
## 2026-09-13 - Active gate: Phase50.A.2H Storefront Showcase Polish

A2G remains Production-verified at `d7cf71d...`; A2H is the Local-tested visual follow-up. It improves Hero product staging, selected-Variant price presentation and the first-visit theme chooser without changing commerce authority or introducing a migration. Local Django/no-drift, Node 8/8, Playwright responsive and real Home desktop/tablet/mobile gates PASS. Next: dedicated no-migration GitHub-first deploy and Production verification, then the already-required one-Product end-to-end publish acceptance before bulk.

## 2026-09-13 - Reverse management + A2G Production gate complete

Reverse Host management is E2E verified and active: authenticated Windows loopback `127.0.0.1:22024` reaches the Host-only bridge `127.0.0.1:22224`, with Host source restricted to `89.39.208.237/32`. Exact Production/Local/GitHub source at acceptance is `d7cf71dceca95e191a118336c7004683083278ee`. The repository read-only Production audit, MySQL identity, Store 0036-0042 + Website 0024 recorder state, empty migration plan, receiver readiness, public Bridge and A2G static HTTP gates all PASS.

Phase50.A.2G is now `PRODUCTION_VERIFIED`. Next is exactly one controlled Product Windows-to-Production acceptance with finalized SEO WebPs, strict ACK, canonical Product/Profile/Variant, public media/page and guided cart verification. Bulk Product publication remains blocked until that one Product passes. The tunnel changes transport only; development remains Local -> tests -> GitHub -> Host ff-only -> Production verify.

## 2026-09-13 - Operations gate: 3DPrintHub reverse Host management

Adopt the repository-published Asal reverse-management standard for this shared cPanel Host: loopback authenticated command bridge on Host `127.0.0.1:22224`, outbound Host SSH/443 to the verified Windows public endpoint, and Windows loopback operator port `22024`. Windows side is prepared and source-restricted for declared Host IP `89.39.208.237/32`; Repository operations implementation `180fe16c0e296156ef38ffc00a042c329318ff7c` is on live GitHub. Host onboarding/E2E identity proof is next. This is transport only; normal Local test -> GitHub -> Host ff-only deploy -> Production verify remains mandatory.
## 2026-09-12 - Active gate: Phase50.A.2G Publish-ready Media + Professional Order Wizard

A2F is Production verified at `7d0b3df...`. A2G closes the final pre-bulk Product-publication boundary: only current finalized SEO WebP files may enter a Product Batch, exact media bytes/names survive Windows-to-Host, identical re-import is idempotent, and changed media advances visual revision only once. The Storefront wizard is responsive across desktop/tablet/mobile with progress, guidance, keyboard/touch support and canonical Variant fallback.

Local gates pass: Catalog 10/10, Django 16/16, Node 8/8, Playwright responsive suite, compile/check/no-migration-drift/diff-check and A2G Host-runner syntax/no-migrate/exact-delta contract. Exact runtime `e76e555...` passed the canonical checksum-backed Windows gate and Catalog Center launched. Host source has since advanced to `a320a0d...`; public Home/Store/new JS/CSS are HTTP 200. Next: complete reverse-tunnel E2E + authenticated Host worktree/Bridge/readiness acceptance, then publish one controlled Product and verify Product/Profile/Variant/WebP/public page/strict ACK before bounded bulk.

## 2026-09-12 — Phase50.A.2F PRODUCTION VERIFIED

Status: `PRODUCTION_VERIFIED`.

Production deployment completed successfully from recovered baseline `e12fdaf281f7e08013e54c7cf936f8275127ab2b` to exact GitHub commit `7d0b3df03c3657106ebaf86d5f9123ba262495a5` using `scripts/host/phase50_a2f_storefront_production_deploy.sh`.

Verified Host evidence: MySQL `sfkilvrs_EmiAdmin_3dprinthub`; required Store 0036–0042 + Website 0024 migrations present; migration plan empty before and after promotion; publish-readiness ready=true with no blockers; verified source/.env/static backup at `/home/sfkilvrs/3dprinthub-deploy-backups/20260912-182234-phase50-a2f-storefront`; ff-only Git promotion; collectstatic; Passenger restart; Home/Store/Bridge health/readiness/new JS/new CSS all HTTP 200; final Host worktree clean.

Guided customer ordering is now live on Production: size → color → compatible material → print quality → canonical ProductVariant → server-authoritative price/stock/weight/time → cart. Native Variant select remains fallback.

Next exact acceptance: one controlled Product publish from Windows Catalog Center to the now-ready receiver, verify Product/Profile/Variant/images/public Store/strict ACK, then enable bounded multi-product publish. In parallel continue Phase50 finance/payment/admin work after this Product-publish acceptance.
- 2026-09-12 A2F deploy follow-up: fix/test ERR-49-115 root-document allowlist, push a new exact GitHub target, then retry the no-migration guarded Host deploy from unchanged `e12fdaf...` baseline.
## 2026-09-12 — Production recovery verified; 2F deployment is the active gate

Live Bridge/readiness evidence supersedes the older partial-0039 roadmap state: Production MySQL is ready, Store 0036–0042 and Website 0024 are applied, receiver schema/storage prerequisites pass with no blockers, and Production source is `e12fdaf...`. Do not rerun 53G.

Phase50.A.2F is Local-tested and GitHub-tested at `38458ce...`; next is the repository-owned no-migration deploy gate. The deployment must start from exact clean Host baseline `e12fdaf...`, fetch the live branch explicitly to `FETCH_HEAD`, make verified source/env/static backups, prove no migration/requirements/settings delta, ff-only promote, collectstatic/restart and verify public Store + Bridge + new guided JS/CSS. After Production verification, continue Phase50 commerce/finance work.

## 2026-09-12 — Active Local gate: Phase50.A.2F Guided Storefront Configurator

Phase50 customer ordering now advances from the internal Profile Matrix toward a four-step guided Storefront flow: size → color → compatible material → print quality. Canonical ProductVariant, server price, stock, weight/time and native fallback remain authoritative. Local Node/Django/Playwright gates pass and no migration is introduced.

Immediate sequence: commit/push exact Local delta; run canonical Windows Catalog Center Local gate on the clean GitHub HEAD; re-audit actual Host/partial MySQL state; complete 3I.53G recovery before any normal Production deployment. Finance/ZarinPal/Torob work remains after the current commerce/receiver safety gates.
## 2026-09-02 — Phase49.3I.53G recover partial MySQL migration 0039

Status: `IMPLEMENTED + REAL MYSQL PROBE PASS / HOST PARTIAL-STATE RECOVERY NEXT`.

Production source is `5f6c13ab...`. Website 0024 and Store 0037/0038 are applied. Store 0039 stopped on duplicate `ProductVariant.support_weight_grams`; 0040–0042 remain pending.

Root cause is confirmed in Repository history: 0033 already creates ProductVariant support weight; 0039 incorrectly attempted a second AddField. 0039 is corrected to AlterField for that existing ProductVariant column and idempotent AddFieldIfMissing for the truly new columns.

Recovery is encoded in `scripts/host/phase49_3i53_partial_0039_resume.sh`: exact recorder/schema forensics → reverify old rollback sets → fresh backup of current partial DB → ff-only source fix → exact 0039–0042 plan → migrate → readiness → static/restart/public verification.

Evidence: Variant/Profile `33664796042` PASS; Product Admin + real MySQL focused recovery probe `33666085743` PASS; Single Active AI `33666085841` PASS; tested recovery code `66e940e6e659f86e3783d78d091b3ff00acbf5aa`.

Next: run 53G recovery on Host. If physical partial state differs from the observed failure boundary, stop and inspect; no fake migration.

## 2026-09-02 — Phase49.3I.53F post-merge dependency/startup recovery

Status: `IMPLEMENTED + CI PASS / PRODUCTION RESUME NEXT`.

Production source is already at `b372586a...`, but DB remains unchanged because the deploy stopped at post-merge Django startup on missing `httpx==0.28.1`.

Recovery now:
- makes Site AI provider/content transport imports lazy;
- preserves mature AIProviderClient patchability;
- proves Django bootstrap does not require httpx;
- adds target dependency install/verify to normal deployment;
- adds a dedicated post-merge resume runner that reuses/re-verifies the valid rollback backup, then installs exact dependency, takes a fresh DB backup, verifies the exact migration plan and completes migration/static/restart/readiness.

Evidence: `ccd1b98997a8dd0c8389ccbe2b6c78b83dd7f176`; Product Admin `33663316332` PASS; Single Active AI `33663316324` PASS.

Next: execute post-merge resume from Host HEAD `b372586a...`; do not rerun the original baseline deploy runner.

## 2026-09-02 — Phase49.3I.53E backup helper import-boundary fix

Status: `IMPLEMENTED + CI PASS / PRODUCTION DEPLOY RETRY NEXT`.

Second deploy attempt stopped safely before source promotion because the extracted backup helper could not import `config` from outside the repository. The helper now receives and validates the exact Production project root and prepends it to Python import paths before Django setup.

Production remains on `198fa8e41ea4f4d87eb287ba69c91076acc78d62`.

Evidence: `2016b84ee1b053e792ceb44ede516b3d7a2dea7e`; Product Admin CI `33661199115` PASS; Single Active AI `33661199159` PASS.

Next: fresh timestamped backup and deploy retry against the current live GitHub target.

## 2026-09-02 — Phase49.3I.53D verified MySQL backup streaming fix

Status: `IMPLEMENTED + CI PASS / PRODUCTION DEPLOY RETRY NEXT`.

The first audited deploy stopped safely before source promotion because the MySQL file had a `.gz` suffix but raw mysqldump contents. The backup boundary has been corrected with a repository helper that pipes mysqldump output through the actual gzip encoder and verifies gzip magic/header before the existing `gzip -t` + SHA256 gate.

Production remains at `198fa8e41ea4f4d87eb287ba69c91076acc78d62`; no migration or restart occurred.

Final fix `3b6254bf7700bb26b4af63d21e31e56e7700877c`; Product Admin/backup CI `33659707983` PASS; Single Active AI `33659707957` PASS.

Next: fresh timestamped backup + controlled deploy retry. Do not reuse the invalid 20260902-203857 MySQL artifact.

## 2026-09-02 — Phase49.3I.53C audited Production receiver deployment

Status: `DEPLOY RUNNER READY + CI PASS / PRODUCTION EXECUTION NEXT`.

Host audit proved the exact Production baseline and pending receiver migration chain. A repository-owned deployment runner now enforces verified backups, exact migration-file/plan gates, ff-only promotion, migration, collectstatic, Passenger restart and authenticated receiver/public HTTP verification.

Current Host DB state: Store 0036 + Website 0023 applied; Store 0037–0042 + Website 0024 pending. Active Material/PrintQuality prerequisites and storage/token/disk/backup tooling are ready.

Evidence: read-only Host audit PASS from owner output; deploy runner `5c5f087ae26e78c106984cf3c92e9b322537f203`; Product Admin/audit CI `33658713537` PASS; Single Active AI `33658713594` PASS.

Next: execute deploy runner from GitHub. After receiver PASS, publish exactly one controlled Product from Catalog Center and verify site Product/image/ACK before bulk enablement.

## 2026-09-02 — Phase49.3I.53 Site publish receiver + Host deployment gate

Status: `IMPLEMENTED + SITE/WINDOWS CI PASS / HOST READ-ONLY AUDIT NEXT / PRODUCTION NOT DEPLOYED`.

Completed:
- added authenticated receiver-readiness endpoint for Desktop Product publish;
- checks required Store/Website migration state, schema, token presence, pending/media storage and Product-import prerequisites;
- Desktop publish fails closed before FTP when the live Site receiver is not ready;
- Bridge health and publish readiness are separate operator states;
- old Site without the new endpoint is shown as Bridge-connected but publish-blocked;
- added repository-owned Production read-only audit with no source/DB/runtime mutation;
- reviewed the pending Production migration chain 0036..0042 + website.0024; no new 3I.53 migration.

Evidence: Site `33652584032` PASS; Variant/Profile `33652583964` PASS; Host-audit contract `33652996666` PASS; final Qt `33653229142` PASS; final Single Active AI `33653229219` PASS; final Portable `33653229400` PASS with 235 regressions; artifact `9855771656`; EXE SHA256 `a6bebd3c10a56aac1c65a58d5ffb1029382e98c7b0782a4b034a315e60c2f1ed`.

Next: read-only Production audit, then fresh verified backups, then controlled ff-only deploy/migration/collectstatic/restart/receiver+Product verification. Production remains untouched until audit evidence is reviewed.

## 2026-09-02 — Phase49.3I.52G adaptive Product recovery

Status: `IMPLEMENTED + WINDOWS QT/PARITY PASS + PORTABLE PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT DEPLOYED`.

Completed:
- discovery success is separate from full Product data/image success;
- redacted per-method acquisition tracing + Qt log-folder access;
- factual Product quality gates for meaningful title/data and real local image evidence;
- ordered failover across distinct mature receive methods;
- successful method becomes preferred for following Products;
- all-method exhaustion or invalid Product identity stops the batch and leaves later rows untouched;
- partial-success batches with a later circuit break are reported failed;
- permanent Crawl bulk recovery opts into adaptive failover while preserving mature safe merge behavior.

Evidence: runtime `bf1fafdb38233a23e13a5715ffac72f772412005`; Qt `33644903042` PASS; dedicated suite 27 PASS; Single Active AI `33644902970` PASS; Portable `33644902962` PASS; 235 portable regressions; artifact `9852476786`; SHA256 `f3e0bce9e5d3b40317b5fd37cff8a5fc6ff1d5a2cef6f5b1bf84dc6f6699c310`.

Next: owner Local 2–5 Product real-source QA and log inspection if a live failure remains. Production stays blocked.

## 2026-09-02 — Phase49.3I.52F bulk incomplete Product recovery

Status: `IMPLEMENTED + WINDOWS QT/PARITY PASS + PORTABLE PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT DEPLOYED`.

Completed:
- restored the mature previous-version bulk refetch intent inside Qt permanent Crawl inventory;
- `انتخاب ناقص‌ها` selects loaded rows missing Product/data/image evidence;
- image target selector supports 5/10/20;
- `بازیابی دیتا + عکس` reuses complete local evidence first and force-refetches only incomplete Products;
- safe refetch preserves operator Persian content, pricing, approval and publish decisions;
- orphan collected-ledger identities can be explicitly rebuilt from their Product URL;
- URL slug gives a readable temporary Product identity before full receive;
- queue actions are split across two rows and `بازگردانی به صف` is distinct from data recovery.

Evidence: runtime `cf73f841418aac2eec1b78e0dbd682ceb2d3fef5`; Qt `33637452385` PASS; Single Active AI `33637452588` PASS; Portable `33637452243` PASS; 227 release regressions; artifact `9849484898`; SHA256 `f0150359fd36c7ead84599ccd0b799797ed48e85e4c6eac1d191abc3f0315a64`.

Next: owner Local sync/gate, then select incomplete permanent Crawl rows and recover 5/10 images in one batch. Production remains blocked.

## 2026-09-02 — Phase49.3I.52E Crawl preview + historical refetch image parity

Status: `IMPLEMENTED + WINDOWS QT/PARITY PASS + PORTABLE PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT DEPLOYED`.

Completed:
- include mature `<id>_refresh_latest`, `<id>_refetch_*`, and `<id>_bulk_refetch_*` image folders in read-only Crawl image resolution;
- preserve exact Product/local_dir authority and do not move media;
- recover MakerWorld lazy listing thumbnails from srcset, picture source, data-src/data-original/data-lazy-src and CSS background-image;
- allow same Search rerun to backfill candidate Preview without duplicating Crawl identity;
- keep local image counts factual: only real local files produce `N عکس دارد`;
- expose `Phase49.3I.52E` in Qt shell.

Evidence: runtime `016e84ab98d2e5577633833cbc87cb96824dbbf0`; Qt `33632062812` PASS; Single Active AI `33632062877` PASS; Portable `33632062880` PASS; 223 portable regressions; artifact `9847317893`; SHA256 `f9bcfc0770a38b0c8eabc9f2deab7c05b2c4d8b577fd25eb540ea9b65f7dc970`.

Next: owner Local sync/gate, then permanent inventory + same-search Preview backfill foreground QA. Production remains blocked.

## 2026-09-02 — Phase49.3I.52D legacy image-path parity + numeric control repair

Status: `IMPLEMENTED + WINDOWS QT/PARITY PASS + PORTABLE PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT DEPLOYED`.

Completed:
- verified the mature Catalog download layout from the retained Tk runtime instead of inventing a new path;
- canonical downloaded images remain under `D:\projects\3dprinthub-catalog-manager\collected\<source>\<external_id>\images`;
- Qt Crawl inventory now reads that mature folder directly even when an old Crawl row is not yet linked to a Product id;
- finalized `seo_images` are preferred before original `images`;
- legacy source-code casing differences no longer hide matching Product rows;
- actual local image count is shown as `N عکس دارد` for unlinked candidates too;
- live single-candidate review exposes real downloaded files from the mature collected tree;
- old retained `D:\projects\3dprinthub_catalog_center\collected` is a read-only secondary compatibility fallback only;
- Product/price/SEO/publish state is not mutated by this image lookup;
- Crawl `requested` and per-Product image-count spinboxes are LTR, centered, width-bounded and padded to prevent Windows RTL arrow/text overlap;
- control grid spacing is explicit.

Evidence:
- exact runtime `a18b6f3036d41271cf3e8c1d9a0dfd8c271a53ce`;
- Qt `33628825851` PASS;
- dedicated 3I.52C/52D 13-test suite PASS;
- Single Active AI `33628825772` PASS;
- Windows Portable `33628825715` PASS with 221 release regressions;
- artifact `9846044486`;
- EXE SHA256 `c08aa1e9d12926203cb59c580aab6c606c2b0e259ad83df37aa3b3abec86c22a`;
- rollback `backup/pre-phase49-3i52d-legacy-image-path-layout-20260902` → `28b51d2f95b272d3bf6311fb02f55a7a4fa808e4`.

Immediate next:
1. owner Local clean ff-only sync;
2. canonical Local gate + foreground Qt launch;
3. verify the exact owner screenshot area now displays mature downloaded images/counts;
4. verify the 100/5 spinboxes are visually separated from arrow controls;
5. if any one external id still misses, inspect that exact DB/local_dir/collected identity read-only before any further change;
6. Production stays blocked.

## 2026-09-02 — Phase49.3I.52C Crawl visual review + bulk transfer recovery

Status: `IMPLEMENTED + WINDOWS QT/PARITY PASS + PORTABLE PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT DEPLOYED`.

Completed:
- Preview-first Product cards in the current Crawl Search workspace;
- stable candidate thumbnail reuse and visible image-count state;
- per-Product image progress during full receive;
- selected collected Product local image review strip with real local files and explicit counts;
- compact receive/bulk action labels with full tooltips;
- Qt shell phase identity updated from stale 3I.48 to current 3I.52C;
- new Search clears prior live Search cards;
- explicit multi-select/select-all/clear/bulk add/reject in current Search and persistent Crawl inventory;
- successful bulk transfer navigates to Products and preserves existing collected identity;
- safe Product source-data/more-images recovery that preserves operator/business-owned fields;
- shorter task-oriented Crawl bulk actions and explicit selected-count feedback;
- dedicated 3I.52C regressions;
- Portable CI dependency correction after ERR-49-097.

Evidence:
- final runtime/CI checkpoint `f43c7aa464948832ba349543f94c94498490ab25`;
- Qt `33625988684` PASS;
- Single Active AI `33625988674` PASS;
- Windows Portable `33625988663` PASS, 218 release regressions;
- artifact id `9844889166`, EXE SHA256 `cd54431bd29bad76990c17eb818671e3f32c4d53a244cdc07132f5d93a532f4b`;
- pre-phase rollback `backup/pre-phase49-3i52c-crawl-review-recovery-20260902` → `dfc883cc6ac68c49c589c0d5a6007d50a9a4719c`.

Immediate next:
1. owner clean ff-only Local pull;
2. canonical `RUN_PHASE49_3I42C_LOCAL_GATE.ps1` / runner `49.3I.52.2` with exact final GitHub head and `-LaunchApp`;
3. foreground QA with one bounded MakerWorld Search: Preview image/title, 3/5→5/5 progress, image-count labels, multi-select transfer and Products navigation;
4. verify persistent Crawl inventory thumbnails/multi-select;
5. verify Product `دریافت داده و عکس بیشتر از لینک محصول` without operator price/content/publish clobber;
6. only after owner acceptance start the normal Host read-only audit/backups. Production remains blocked.

## 2026-09-02 — Phase49.3I.52 Site fallback authoring + Shared AI + bidirectional Product sync

Status: `IMPLEMENTED + WINDOWS QT CI PASS + SITE/ADMIN CI PASS + PORTABLE PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT DEPLOYED`.

Completed:
- canonical Site Product authoring when Windows Catalog Center is unavailable;
- same Product/Profile/Variant pricing authority on Site and Desktop;
- root `ai/` shared policy/playbook with environment-only Host secrets, exact-model Product safety, Persian Structured probe, verified-free-first and bounded low-cost fallback;
- Site AI Preview → explicit Apply, limited to Product content/SEO;
- Bridge source identity + category + pricing/Profile payload parity and bounded Product pagination;
- explicit Windows `دریافت تغییرات سایت` Product pull;
- Site-only non-publishable Local mirrors;
- dirty-Local/newer-Site conflict protection;
- pre-publish Site revision verification that fails closed on mismatch or Bridge verification failure;
- mature Batch/FTP/Bridge/public verification path retained after the guard;
- owner Local gate upgraded to `49.3I.52.1`.

Evidence:
- tested source `6d19bed7659b9ca4cd54ff1ffd1323ec423bea6a`;
- Qt full parity `33619876564` PASS;
- Windows Portable `33619876411` PASS;
- Single Active AI `33619876317` PASS;
- Product Admin/Bridge/migration `33619558467` PASS on runtime-equivalent `d6450ca2...`;
- Variant/Profile Matrix `33619558562` PASS;
- rollback `backup/pre-phase49-3i52b-bidirectional-site-sync-20260902` → `48290db4...`.

Immediate next:
1. owner Local 3I.52 checksum-backed gate + foreground QA;
2. if PASS, read-only Host audit of actual root/HEAD/worktree/Python/Django/MySQL/migrations/disk/backup tools;
3. fresh source + environment + MySQL backups with non-empty/checksum verification;
4. deploy only the owner-approved GitHub commit;
5. apply only the migration plan proven by the live Host audit;
6. Production verify Admin, Bridge, Product page, pricing/Profile and AI environment boundary.

Production remains blocked until Local acceptance and Host audit.

## 2026-09-02 — Phase49.3I.51 Windows + Site finalization

Status: `IMPLEMENTED + WINDOWS CI PASS + SITE CI PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT DEPLOYED`.

Completed:
- final Product image/source-link/Crawl Source-detection/live-result parity;
- explicit source-missing default Profile with owner fallback production facts;
- PLA/PETG-family fallback Filament matching;
- four-part Filament registry workspace with managed Material/Brand/Color identities;
- optional descriptions and Material reference price/kg;
- registry rename propagation/collision protection;
- selected and full Site Filament reconciliation over the mature authenticated Bridge, including inactive offers;
- persistent Site FilamentBrand + Material/Filament descriptions;
- task-focused Django Admin parity while preserving Material production rates;
- additive Django migration candidates `website.0024` and `store.0042`;
- canonical owner gate upgraded to `49.3I.51.1`.

Evidence:
- Windows Qt `33611776817` PASS;
- Windows Portable `33611776806` PASS;
- Single Active AI `33611776891` PASS;
- final Site/Admin/Bridge `33611936196` PASS on `8f01ea264dea2771cf1eb2f592be794d0dc95bbf`;
- final Single Active AI `33611936216` PASS;
- rollback branch verified identical to pre-phase `191e8ef83f9a804805dda4cdd3df66b8224264d6`.

Immediate next:
1. owner Local 3I.51 gate + foreground QA;
2. if PASS, read-only Host audit of root/HEAD/worktree/Python/Django/MySQL/migration state/disk/backup tools;
3. fresh source + environment + MySQL backup with checksum/non-empty verification;
4. deploy only the owner-approved GitHub commit;
5. apply only the verified migration chain;
6. Production runtime/Admin/Bridge/Product verification;
7. then continue visual/accessibility/typography polish and remaining stability work.

Production remains blocked until Local acceptance and Host audit.

## 2026-09-02 — Phase49.3I.49 site publish + Slider/Admin parity

Status: `IMPLEMENTED + WINDOWS CI PASS + ADMIN CI PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT DEPLOYED`.

Completed:
- explicit Product multi-select ready-for-publish gate;
- selected-ready-only bulk publish;
- mature Batch8.5/FTP/Bridge/public-HTTP verification retained;
- successful publish automatically enters the existing Published lifecycle workspace;
- failed/skipped Products remain outside Published with diagnostics;
- full existing Slider composition/SEO/motion/timing fields round-trip Desktop ↔ Site;
- HomepageHeroSlide and ProductCatalogProfile Admin organized by operator task, with sync diagnostics collapsed;
- Local gate expanded through 3I.49.

Evidence:
- exact final Windows Qt CI `33596830380` PASS on `f9f89643de883ff549a9c0089235e43f061c5d4d`;
- exact final Single Active AI/no-migration CI `33596830268` PASS;
- Admin/Bridge CI `33596562467` PASS on `16cf7cfaf6be3e8594435e3489cb0615624fcb00`;
- the only later delta from `16cf7c...` to `f9f896...` is the repository-owned Local gate.

Owner acceptance next:
1. clean ff-only pull on `D:\projects\3DPrintHub`;
2. checksum-backed Local gate + foreground launch;
3. verify multi-select Ready state, blocked-Gate explanation and Published workspace transition;
4. verify Slider controls are present in Qt and, after a later approved site deploy, in Django Admin;
5. no Production publish/deploy until explicit owner acceptance and the normal Host audit/backup sequence.

No new Django migration or secret-store contract is introduced by 3I.49.

# ROADMAP

## 2026-09-18 — Phase50.A.2L owner QA promotion path
Status: `LOCAL_ACCEPTED / COMMIT_PUSH_RELAUNCH_NEXT / PRODUCTION_BLOCKED_ERR-49-154`.

Immediate sequence: freeze the tested A2L source+docs+brand asset -> commit/push exact WIP candidate -> verify GitHub SHA -> relaunch Qt from that SHA and visually confirm #628 10-image scrolling/multi-select + Filament bulk/sync UI -> restore dedicated 22024 tunnel -> Host read-only identity/migration/readiness gate -> fresh MySQL/media rollback backup -> deploy exact GitHub release -> explicit Pasargad payment seed apply -> public bank-transfer receipt/admin notification acceptance. Podium/Farataz automation stays deferred to a separate verified source audit.

## 2026-09-01 — Phase49.3I.47 owner rerun + professional commerce design-system track

Status: `PS5.1 GATE FIXED + EXACT WINDOWS CI PASS / OWNER LOCAL RERUN NEXT / PRODUCTION NOT DEPLOYED`.

Immediate accepted source checkpoint:
- `36a710953276aae99fa668f477ad5569f8dc23ba`;
- runner `49.3I.47.2`;
- `33511403943` Qt6 Full Parity Windows PASS;
- `33511403901` Single Active AI PASS;
- explicit Windows PowerShell 5.1 ASCII/parser guard PASS.

Owner acceptance still required:
- lifecycle Product tabs and local thumbnail fallback;
- sequential multi-select full-content AI;
- every image final SEO metadata + numbered WebP identity;
- Acquisition workspaces with gallery/details views;
- Profile/Pricing full-height tabs.

Professional commerce architecture is now registered in:
`docs/PROFESSIONAL_COMMERCE_DESIGN_ARCHITECTURE.md`.

Source-guided next design slices after owner acceptance:
1. Persian typography/font-runtime and packaging audit; solve the Qt/system-font experience without committing licensed font binaries;
2. shared visual tokens/components and accessibility states for Catalog Center;
3. Admin design-system consolidation;
4. Storefront IA for discovery → technical fit → price/quote → trust → variant/custom order → CTA;
5. Product-detail technical/trust hierarchy and responsive intermediate-width QA;
6. performance-safe optional 3D preview only where it materially improves product evaluation;
7. SEO/accessibility/performance regression gates;
8. remaining Catalog stability work: worker/read connection discipline, serialized/batched writes, bulk discovery persistence, slow-query/health auditing and resume/soak testing.

Guardrails:
- Django remains authoritative; book examples do not imply framework migration;
- no visual phase may change pricing/business authority implicitly;
- critical SEO/Product text remains server-rendered/crawlable;
- no Production deployment before owner Local approval and the normal Host read-only audit/backup/deploy chain.


Updated: 2026-09-01

## Current Windows/Desktop track — Phase49.3I.47

Status: `IMPLEMENTED + WINDOWS CI PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT DEPLOYED`.

Current code checkpoint: `9984e3bb9ab5ff293ad275ecbe86dba3a96db4b1`.
Canonical phase: `docs/phases/PHASE49_3I47_QT_WORKSPACE_IMAGE_BULK_AI_SITE_IA.md`.
Rollback: `backup/pre-phase49-3i47-owner-workspace-20260901` → `ecfd9260c168140757781bb672eb57c77bcc4ee3`.

### Completed in 49.3I.46
- Product Gallery bounded SQL paging: initial 50 + incremental fetch.
- Product Table/Detail bounded SQL paging: initial 20 + incremental fetch.
- Crawl inventory bounded paging: initial 100 + incremental fetch.
- lightweight Product list projection, SQL-backed search/sort/filter and planner indexes.
- mature pre-Qt acquisition methods restored through headless Core/runtime.

### Completed in 49.3I.47
- Products reorganized into active, sent/published, archived and rejected/deleted lifecycle workspaces.
- legacy/local Product thumbnail fallback for old records without modern URL mapping.
- Product cards expose description excerpt + image count.
- sequential multi-select `AI تکمیل همه موارد` through one shared AICore and shared single-Product finalization path.
- every selected Product image receives consistent SEO metadata and unique numbered WebP filenames (`-01`, `-02`, `-03`, ...).
- Add Product/Crawl split into focused inventory/receive/history workspaces.
- Crawl inventory gains Windows-like gallery/image and details/table views with Product preview facts.
- Profile/Pricing split into three full-height task tabs with production/filament rows no longer clipped by nested scrolling.
- Django Admin adopts shared accessible task tabs for Product sales/source/SEO, pricing, material/color rates, site settings and quotes.
- Storefront Product information adopts progressive accessible tabs while preserving existing Variant/Profile/pricing authority.

### Verification
Qt/Desktop on `9984e3bb9ab5ff293ad275ecbe86dba3a96db4b1`:
- `33506242569` — `qt6-full-parity-windows` — PASS.
- `33506242669` — `phase49-3i17` — PASS.

Admin on `ef215ba09044cd421302f9057bf3c1565b99ef1e`:
- `33505851712` — `product-admin-workspace` — PASS.
- `33505851749` — `phase49-3i17` — PASS.

Storefront on `f4beec484f060063d00de4a5753a135a020cfea1`:
- `33506122579` — `phase50-variant2-gallery` — PASS.
- `33506122534` — `phase49-3i17` — PASS.

## Immediate acceptance gate
1. Owner clean ff-only pull on `D:\projects\3DPrintHub` to the final docs HEAD.
2. Run repository-owned `RUN_PHASE49_3I42C_LOCAL_GATE.ps1 -ExpectedHead <final-head> -LaunchApp`; runner version is `49.3I.47.1` and backs up/checksums the real Catalog SQLite before QA.
3. Verify four Product lifecycle tabs, old thumbnails, card description/image count and sequential Bulk AI on disposable Products.
4. Verify one disposable Product with at least three images produces consistent SEO metadata and distinct numbered SEO files for every image.
5. Verify Add Product/Crawl three workspaces plus Gallery/Details inventory views and bounded scroll continuation.
6. Verify Profile/Pricing three full-height tabs and all production/filament rows.
7. Record owner Local foreground evidence.
8. Do not deploy Production from this gate.

## Next engineering slice after owner acceptance
- remaining Catalog stability work: worker/read connection discipline, serialized/batched writes, bulk discovery persistence, query auditor/slow-query health and resume/soak testing;
- Phase42D visual/accessibility polish based on real owner QA;
- owner File Library constituent design books have now been reviewed directly; apply grounded refinements through `docs/PROFESSIONAL_COMMERCE_DESIGN_ARCHITECTURE.md`;
- only later evaluate 42E default-launcher/package cutover.

## Web / Admin track
Current Admin/Storefront information architecture is implemented and CI-tested but not Production-deployed. Any later Host work must start with read-only verification of root/branch/HEAD/worktree/live SHA/Python/Django/MySQL/migration state, followed by exact migration plan, fresh backups/checksums and deploy only from the owner-approved GitHub commit.

Last verified Production application commit remains `c283864290f9c989a9fcdf24ee8eef519560e917`.
Last verified Production migration evidence remains only `store.0034` and `store.0035`; no later migration is assumed applied.

Historical roadmap checkpoints remain available in Git history and dedicated `docs/phases/` documents.

## 2026-09-14 - Phase50.A.2I Slicebox-inspired 3D Hero

Status: `LOCAL_TESTED / GITHUB PROMOTION NEXT`. The existing managed Django Hero now has an optional dependency-free seven-slice 3D transition inspired by Codrops Slicebox. Existing SSR content, Product links, timing, arrows, dots, keyboard/swipe and mobile/reduced-motion fallback remain authoritative. Focused Hero/Public-Media regression 30/30 PASS and real Playwright desktop/mobile QA PASS. No migration, dependency or commerce-authority change. Next: commit/push the reviewed A2I delta, then combine it with the already-tested A2G Bridge public-media fix for guarded Production deployment and Product #63 final cart/ACK acceptance.

## 2026-09-14 - Manual publication simplification checkpoint
- [x] Give every active Local Filament one 1000 g roll of stock.
- [x] Remove zero purchase/sale/service pricing from active Local Filaments using owner overrides + existing Material reference authority.
- [x] Ensure every Local Product has a canonical Sales Profile.
- [x] Preselect every unique active Filament identity in every Product Profile.
- [x] Preserve existing factual Profile rows; use fallback production facts only where Profile/production data was absent.
- [x] Mark previously uploaded Products for same-identity republish instead of duplicate publication.
- [x] Focused Filament/Profile tests 34/34 + Qt verification PASS; relaunch Windows Catalog Center.
- [ ] Owner manually adjusts Product dimensions/finalizes required stages and publishes selected Products from Windows.
- [ ] Continue the separate Store Reset feature before claiming the Production Store is empty; do not conflate that pending source work with this Local data policy.

## 2026-09-17 checkpoint
- Phase50 Windows re-publish/update-in-place: LOCAL ACCEPTED; commit/push pending at time of this checkpoint.
- Phase50.A2J standalone sliced Hero: Production accepted release reconciled back into development lineage; local focused gate PASS.
- Store cleanup: preflight READY and fresh verified rollback backup READY; destructive reset still pending because the automation safety layer blocked the write operation.
- Next: canonical reset -> safe Hero seed -> Production verification -> Windows app exact-SHA launch.
## 2026-09-17 runtime gate
- Windows Publisher exact-SHA runtime: PASS and foreground UI launched.
- Production test-product reset: still pending solely because the automation safety layer blocked the destructive write; verified rollback backup already exists.

