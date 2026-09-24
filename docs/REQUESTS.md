## 2026-09-24 - Owner: Product filters, split Instagram actions, Crawl repair/delete recovery
Status: `O1+O1B+O2+O2D+O2E+O2G ACCEPTED -> O2H -> O2F -> O3`.

Owner requested the Product filter menu to expose: آماده انتشار for exact 7/7 completion, تکمیل هوش مصنوعی for AI-completed exact 6/7, ارسال‌شده سایت, ارسال پست Instagram and ارسال استوری Instagram. Social publication must no longer be one combined cycle: Post and Story need separate buttons and independent execution.

Owner also reported Crawl cards without images, Repair doing nothing, Delete not removing items, and requested complete/incomplete Crawl filters with missing reasons. Repair intent is a full local reset/refetch/remap for the selected Source identity so corrupted/mis-mapped local data cannot survive a repair.

Work is split into the existing bounded phases plus one inserted operator-activity microphase: O1 Product filters + split Social; O1B Recent Product Activity; O2 Crawl completeness + missing reasons; O3 guarded deep reset/refetch/remap; O4 Delete semantics; O5 Social receipt/operator acceptance; O6 integrated closure. O1 is accepted at GitHub-exact source `22bb0fb1...`; exact-SHA Qt VerifyOnly, integrity backup, one app restart and runtime smoke all passed. O1B is next.

O1B owner request is ACCEPTED: `آخرین ادیت‌شده‌ها` is newest-first from explicit operator-save history events, not generic Product `updated_at`; `اخیراً دیده‌شده‌ها` is newest-first from persisted `product_viewed` events recorded only after successful Product Editor load. Card display/selection/hover/search/source-link opening do not count as viewed, and View tracking never dirties Product/Site state. Source `a0d5ea46...` is GitHub-exact; cloned real MainWindow/ProductWizard acceptance and visible exact-SHA runtime smoke PASS.

O2 is ACCEPTED at GitHub-exact source `f04d5b05...`: Crawl Complete/Incomplete filtering and per-card missing reasons share one filesystem-aware AcquisitionCore/ImageCore authority. Final real runtime truth is quick_check=ok and 1099 Crawl rows = 463 complete + 636 incomplete; scoped before/after smoke digest proved zero Product/Crawl/History mutation.

New owner request is split into three independent slices before O3:
- O2D Product Identity/Dedup/Consumed-Crawl Suppression: an identity already present in Products must disappear from Add Products and must never automatically Preview/fetch as a new Product. Link/source identity memory must remain so it cannot be crawled again. Only proven same canonical identity may ever be deduplicated destructively.
- O2E Product Media Truth: Product Refresh must reload the exact canonical Local DB/files images for that Product and Instagram must use that same current image authority.
- O2G Search Crawl Pagination/Target Count: requested Product count such as 200/300 must drive MakerWorld lazy/infinite-scroll depth; the current fixed Preview `scroll_rounds=8` must not stop around the first ~15 cards.
- O2H Hard Delete Broken Crawl Identity: explicit delete must actually remove unconsumed Crawl/Candidate/Preview/cache/verified candidate-derived data. The current Reject path only marks `rejected` and is not deletion. Product-backed identities must fail closed.
- O2F Instagram disclosure/links: verify current provider capabilities, apply supported AI label/disclosure to Feed and Story, include original-source and 3DPrintHub order Product links in supported Product details/metadata, and implement Story link only through a real supported provider/native workflow.

O2D is ACCEPTED at GitHub-exact source `4e667f4f...`. Final exact-SHA runtime truth after safe-stop/quiescent backup is 1192 raw Crawl = 707 consumed identities hidden + 485 unconsumed Add identities (50 ready-to-add / 435 incomplete), visible mapped Products=0, and zero exact/normalized canonical Product duplicate groups. Product table/detail visibly exposes canonical `source_code:external_id`. No unsafe title-based deletion was performed because no same canonical identity duplicate exists. Legacy queue/summary, Batch pending, Preview candidate/thumbnail and normal single-product acquisition all share the same suppression contract.

O2E is ACCEPTED at GitHub-exact source `544e046b...`: Product Editor, Refresh and Instagram now share one exact selected Product-local media authority. Fresh rollback/integrity, graceful exact-SHA runtime cutover and real #625/#628 ProductWizard/Refresh/Social parity all PASS with unchanged target Product/History digest.

O2G is ACCEPTED at GitHub-exact source `436bca68...`. The real owner-reported MakerWorld `Lamp` search had only 15 persisted listing rows before the probe. On an isolated Catalog clone, HTTP returned 403 and correctly handed off to the documented Chrome 9222 route; progressive depth reached 48, saw 397 links and persisted exactly 200 requested unconsumed identities (not 313+). Section A layout is decompressed/aligned and its receive options are one row; section B is one six-button toolbar. Focused 49/49, Preview 3/3, related 98/98 and static/framework gates PASS. Exact-SHA Qt v8.9.11 launched once; exact-source render smoke verified target 1..500 and A/B row structure; canonical full logical digest stayed exact after launch/UI acceptance. Production was not changed. O2H is next.

## 2026-09-24 - Owner: close A2Z #628 with ASCII-safe Batch source and strict acceptance
Status: `WINDOWS FIX GITHUB_EXACT / BOUNDED RETRY NEXT`.

The remaining Phase 1 chain is locked: exact-SHA Qt gate -> fresh Catalog integrity backup -> Production identity/readiness + fresh DB/full-media rollback -> publish only #628 once using the new ASCII physical Batch filenames -> ACK + Product/Image/Profile/Variant/Slider/public HTTP parity -> collateral readback of #152/#178/#620/#625 without republish -> real Desktop/Mobile browser acceptance -> Phase 1 CLOSED.

Root cause is proven, not inferred: the exact failed Batch reproduces the same UnicodeEncodeError positions 127-131 when its Persian physical source filename is opened under an ASCII filesystem encoding. GitHub-exact Windows fix is `7b1b447ab772e15f3ecdc1345e69e2e8771573f8`; Production Server remains clean at `2b48a593...` and already contains destination canonicalization.

## 2026-09-24 - Owner: finish Phase 1 through selective Production release and browser acceptance
Status: `UNICODE FIX LOCAL_TESTED / SELECTIVE RELEASE NEXT`.

Owner requires the exact ordered chain to continue without broad publication: verify diff -> shared ASCII-safe Server/Public media naming -> Unicode regression -> related tests/compile/no-drift -> docs -> GitHub exact -> release branch from Production `103f559c...` with only Server delta -> fresh rollback -> deploy via official reverse tunnel -> receiver verify -> retry only #628 -> strict Product/Image/Profile/Variant/Slider and public HTTP/no-stale-media parity -> Desktop/Mobile acceptance -> Phase 1 CLOSED.

#625 is already Production-verified and must not be republished again. #628 had one transaction-rolled-back Unicode filename failure and must be retried only after the selective fix is deployed.

## 2026-09-23 - Owner: Phase 1 A2Z Catalog / Site Truth
Status: `LOCAL_TESTED / GITHUB PROMOTION NEXT`.

Owner requested Phase 1 to close #152/#178 Site truth, take a fresh Catalog rollback, stabilize same-identity full replacement, complete Profile/Filament/Image gates for #620/#625/#628, and finish only with Site/Public + Desktop/Mobile parity.

Verified truth changes the execution plan safely: #152/#178 are already correctly reconciled and clean, so they must not be retried. #620 is also already public/clean. #625 and #628 are the current bounded `needs_update=1` candidates. #625 Site rev12 is proven by exact local `publish_incomplete` receipt evidence, allowing revision-only reconciliation without pulling/overwriting operator Product data. No broad queue publish is permitted.

## 2026-09-23 - Owner: continue latest development directly on the Windows machine; split long execution into three bounded parts
Status: `A2Z-LC GITHUB_VERIFIED / ACCEPTED — A2Z DATA COMPLETION NEXT`.

Owner requested continuation from the latest development state, preferring direct Windows filesystem/shell access over GUI Remote Desktop, and asked that long work be split into three bounded execution parts. Direct filesystem/terminal access to `Emad-NewCom` was used; no GUI Remote Desktop was needed.

Repository truth exposed a post-A2Y lineage divergence, so feature work was stopped and a blocking micro-convergence was completed first. Dirty A2Z work was preserved; A2R motion-media was converged into newest A2Z without replacing Social v5 or newer operator behavior. Source commit is `be00cc73...`; accepted unified GitHub head is `05f29ba3...`. Production is healthy on selective `103f559c...` and was not broadly redeployed because unrelated Server deltas exist in the unified history.

Next requested execution is A2Z Catalog Data Completion from the unified head, carrying forward the preserved incomplete-product/re-crawl/video/Slider work only after local regression proof.

## 2026-09-23 - Owner: restore the previously working Post+Story route and fix Instagram links
Status: `A2Z-S2 PRODUCTION_VERIFIED / ACCEPTED — REAL #536 FEED+STORY COMPLETE, FUTURE LINKS CORRECTED`.

Owner explicitly challenged the mobile-notification-only assumption because the project had already published real Stories successfully. Repository/receipt evidence confirms this: #625 had a real Buffer-sent/live automatic Story. Owner also reported that links placed below Feed posts and on Story artwork were being handled incorrectly.

Requested/implemented contract is now Production-proven: normal Product Social action publishes Feed + Story automatically; Feed Product destination is stored through Buffer Shop Grid metadata rather than a raw caption URL; Caption and Story artwork use truthful Bio/Shop-Grid CTA; Story remains branded 1080×1920 Gold/Navy/IRANSans. Native Link Sticker notification is optional only. Real #536 recovery reused its existing Feed and published one automatic Story successfully with no Feed duplicate. Future v5 captions contain no raw URL. The historical #536 Feed caption is unchanged only because Buffer cannot edit an already-published Instagram post.

## 2026-09-22 - Owner: confirm exact Instagram API and make Post + linked Story reliable
Status: `A2Z-S GITHUB_UPDATED / WINDOWS_RUNTIME_ACCEPTED / BUFFER MOBILE EXTERNAL`.

Owner asked to reconfirm the exact Instagram path because the previous real attempt published Feed but did not complete Story. Required behavior remains the previously accepted contract: Windows action is one Product Social workflow; Site revision must be current/public first; Feed uses exact current Product media + Product-specific caption/hashtags/ALT/UTM; companion Story is branded 1080×1920 Gold/Navy/IRANSans and must carry the Product Link Sticker; same Site revision must never duplicate Feed; Highlight target is recorded and final Highlight placement is operator-required.

Verified provider is **Buffer GraphQL API**, not Meta Graph direct: channel `3dprinthub_ir`, endpoint `https://api.buffer.com`. Feed is automatic. Linked Story uses Buffer notification publishing because native Story Link Sticker is a mobile Instagram feature. New readiness hardening blocks the entire Site/Social action before any irreversible work when Buffer has no active mobile device, preventing another Feed-only partial success. Accepted runtime SHA is `ec05b77fec0d3316d8ee9663fb50b333cf437658`; live readiness on that exact SHA is currently blocked only by `hasActiveMemberDevice=False`.

## 2026-09-22 - Owner: finish #152/#178 and make Instagram Feed+linked Story reliable
Status: `A2Z-C3 ACCEPTED / HERO 2-OF-2 PRODUCTION_VERIFIED / SOCIAL CODE GITHUB_UPDATED / STORY WAITS ONLY FOR BUFFER MOBILE DEVICE`.

Owner requires final recovery of Hero conflicts #152/#178 and requires every Instagram Product send to include the branded IRANSans/Gold-Navy Story with a clickable Product link, without duplicate Feed. Current evidence: #536 Feed is already live and must never be recreated; its branded 1080×1920 Story asset is valid. Buffer itself reports `hasActiveMemberDevice=False`, so Link-Sticker notification cannot currently be handed to Instagram. Windows now checks this prerequisite before any new Feed and keeps existing Feed duplicate-safe. Once Buffer mobile is linked and notifications are enabled, normal retry must create only the Story notification.

## 2026-09-22 - Owner: one-click Full Registration + fix failed Site send
Status: `A2Z-C3 GITHUB_UPDATED / WINDOWS_RUNTIME_ACCEPTED / HOST QUOTA RECOVERY BLOCKED`.

Owner requires a **«✅ ثبت کامل»** button next to **«✏ ویرایش کامل»** so, after edits such as price/Profile changes, one action saves the current Stage and approves every complete Stage instead of requiring seven confirmation clicks. Existing validation must remain fail-closed and the button must not publish automatically.

Owner also reported Site send failure. Exact evidence: Product #536 only, batch `desktop_catalog_v85_20260922_171201`, failed before any FTP-upload receipt/Bridge import with `550 Disk quota exceeded`; #588 previously failed the same way. Queue inventory is 15 Products and must not be blindly retried. Official PrintHub tunnel 22024 is down and another project's RetoucherTunnel must not be used for Host cleanup.

## 2026-09-22 - Owner: Full Edit button + bring later completion capabilities into Products Bulk AI
Status: `A2Z-C1/C2 GITHUB_UPDATED / WINDOWS_RUNTIME_ACCEPTED / CLOSED — A2Z CATALOG COMPLETION NEXT`.

Owner requires one top Product button that opens every Product stage/options for editing together, without changing the existing stage/publish cycles. Owner also requires Products multi-select «AI تکمیل همه موارد» to include capabilities added later: factual Source Profile construction from source weight/time/print data, exact-family Local Filaments, complete Slider page SEO data, physical unique filename/SEO repair and correct local Category. Existing Publish, Site-media authority, Slider membership and Social flows must not be altered.

Implementation composes the already accepted A2W/A2X/Image authorities rather than creating parallel logic. Bulk AI opens Commerce only because this explicit full-completion action needs factual Profile/Filament merge; Publish remains locked. Slider membership remains manual. Runtime-bearing SHA `8629f8b72c416b364a618a5aeebe2dda8a81d440` is GitHub-exact and running; focused 3/3, widget smoke 2/2, broad 129/130 with only baseline ERR-49-203, unchanged-cycle 40/40 and static/Qt gates PASS. C1/C2 is closed.

## 2026-09-22 - Owner: Product #588 Site publish failed with Bridge HTTP 403 anti-robot page
Status: `A2Z ERR-49-221 LOCAL_TESTED / GITHUB + EXACT-SHA #588 RETRY NEXT`.

Owner attempted a real Site publish from the current unified Windows runtime and received BitNinja `Visitor anti-robot validation` HTML instead of Catalog Bridge publish-readiness JSON. Product #588 is the bounded acceptance target. The failed attempt occurred before Batch/FTP/import and must not be counted as a partial Site send. The Windows client must tolerate only narrowly identified transient WAF challenges on idempotent Bridge GET preflights; import POST must never be blindly retried. After exact-SHA promotion and a fresh Catalog backup, retry only #588 and verify one complete Batch/FTP/ACK/public parity chain. Do not publish the other queued Products as part of this recovery.

## 2026-09-21 - Owner: Instagram is broken; real Feed+Story must follow repository policy exactly
Status: `A2Z-S FEED LIVE / STORY BLOCKED ON BUFFER MOBILE DEVICE / RECOVERY HARDENING GITHUB_UPDATED`.

Owner requires the broken Instagram path to be repaired and the written project Social rules to be mandatory for every real send. For #609 this means Site-first revision 2, exact five Site-selected images Primary first, per-image ALT, Product-specific factual caption, bounded hashtags, UTM Product link, nationwide shipping, no false free/download claims, approved 1080x1920 Gold/Navy IRANSans Story, duplicate-ACK protection, provider receipts/external ids and approved Highlight target recording. Final Add-to-Highlight remains operator-required because the documented Buffer path cannot mutate Highlights.

The transport failure was fixed by ERR-49-219 and real #609 GitHub rehost passes public MIME/SHA 6/6. The one guarded external send has now published the Feed successfully at https://www.instagram.com/p/DdjtyiMG8RC/ with all five images. The required clickable companion Story did not go live: Buffer returned a provider error because no mobile reminder device is linked to the Buffer account. ERR-49-220 keeps this truthful and recoverable: error is never treated as ready, Feed stays duplicate-protected, and after the owner links/signs in to Buffer mobile with notifications enabled only Story may retry. The project rule remains notification/Link Sticker Story; do not silently downgrade to an automatic no-link Story.

## 2026-09-21 - Owner: fix #609 multi-image SEO filenames and Instagram delivery
Status: `A2Z LOCAL_TESTED / REAL ACCEPTANCE NEXT`.

Owner requires every selected Product image to be physically finalized with a unique SEO filename and carried to Site, not merely mapped in the UI; duplicate final filenames are forbidden. The raw source/cache may keep provenance names, but publishable Local files, Batch files and Site media must use the unique SEO WebP filenames. Product #609 must publish all selected images, preserve the same Site identity, then send the changed Site revision to Instagram Feed+Story. The existing `social-assets-buffer` worktree must be reused rather than recreated.

## 2026-09-21 - Owner: physical SEO rename, all Product images to Site, Instagram must actually send
Status: `A2Z PHYSICAL-RENAME LOCAL_TESTED / REAL #609 ACCEPTANCE NEXT`.

Owner requires «اصلاح اسم و سئو» to change the actual Product-local file names, reject/avoid duplicate basenames, and send the same unique SEO filenames to Site. If a Product has four/five selected Site images, all selected images must be carried to the same Site Product rather than only one. Instagram Post+Story must complete from the changed Site revision; Buffer Git worktree collision must not block publish and duplicate receipts/posts must remain prohibited.

## 2026-09-21 - Owner: execute A2Y lineage convergence before A2Z
Status: `ACCEPTED / CLOSED / A2Z NEXT`.

The Windows and Server/Production lineages now share one tested forward merge at runtime-bearing SHA `f9a9c203ae3a0a5665dbf884ce0c3e4bf761110b`. Exact-SHA Qt runtime and shortcut cutover are accepted without Catalog/Production mutation. The next owner request gate is A2Z: backup-backed Slider data completion across the Catalog, final Windows operator acceptance and one controlled same-identity re-publish.

## 2026-09-21 - Owner: audit all project chats, freeze remaining phases and always report the next phase
Status: `RECORDED / A2Y MASTER PLAN CREATED`.

Owner requires the remaining development phases to be explicit, complete and continuously updated from Repository truth plus project-chat history. Every future development reply must state the current phase, exact next phase, ordered operations inside that phase, required tests/backups/deploy/Production verification and the phase after it. Missing historical requests must be carried into the roadmap instead of disappearing when a newer task is developed.

Audit result: the next blocker is not another isolated feature. Latest Windows `c86c66a1...` and current Server/Production `e03bdd2b...` are divergent and must converge first. The real Catalog also has 585/635 Products missing at least one A2X Slider core field. Remaining owner requests carried forward include changed-revision Instagram Feed+Story/Highlight queue, manual/self-produced Product creation, source video/Reel, dynamic carriers, secure Store ZarinPal, Torob, Google/local login + customer account closure, Product engagement and the complete accounting/treasury/purchasing/sales/reporting stack.

Authoritative phase file: `docs/phases/PHASE50_A2Y_MASTER_RECONCILIATION_AND_REMAINING_WORK.md`.

## 2026-09-21 - Owner: Slider data must always be complete; membership remains manual; every Windows send fully refreshes Site Product
Status: `A2X LOCAL_TESTED / GITHUB PROMOTION + NO-AI BACKFILL + DEPLOY NEXT`.

Owner requires Slider title/description/ALT/focus/button/image data to be populated for every Product whether or not the homepage Slider checkbox is enabled. The checkbox itself must remain an explicit operator choice. The same rule applies to single-Product “complete all” and multi-select SEO completion.

Owner also requires every Windows → Site send to update the existing Site Product as the current Windows-owned snapshot: changed or unchanged fields are applied again, current selected images replace Site-managed Product images, current Profile/Variant state replaces active stale choices, SEO is current, and Slider membership/data follows Windows. Same Site identity must be preserved rather than creating a duplicate.

Real #620 proves saved AI Slider content already exists despite empty persisted Slider fields, so the first repair must backfill from existing content packs without spending another AI request and without changing membership checkboxes.

## 2026-09-21 - Owner: Product media truth refresh + Site/source recovery + future Profile/video/manual Product import
Status: `A2W W1/W2/W3/W4 WINDOWS_RUNTIME_ACCEPTED / W4.1 REAL_DATA_PATCHED / A2X ACTIVE`.

Owner reports Product #625 shows three media cards in Windows while the live Site Product has one image after re-publish. Required immediate behavior: add a Stage-3 `رفرش رسانه و وضعیت` action that compares Local DB authority, persisted `ارسال سایت`, physical Local files, current Site Product media and source media without silently changing operator Site membership. Public Site media missing locally must be recoverable into the trusted Product workspace as idempotent candidates.

Re-publish must continue using the exact persisted `ارسال سایت` set as authoritative replacement: selected new images/screenshots are added, deselected stale Site images disappear, order/Primary are preserved, SEO WebPs are current, and post-publish Site media count must match the Batch/ACK. Visible local cards alone must never imply Site selection.

Follow-up A2W scope records source video import for Site/Instagram, factual multi-Profile extraction from the Product link, material-family mapping and a manual/self-produced Product flow. W3 and W4 are runtime-accepted on real #625. W4 real Preview returned 2 Profiles / 3 Source slots / 48 Local PLA candidates / exact HEX=0 without mutating Source/Ledger/locks/Site identity. W4.1 owner correction is Local-tested: when a Source size gives a single dimension such as Height=12cm, the operational Profile must use 12×12×12cm (and 18×18×18cm for the 18cm size) instead of leaving other axes unknown. If Source material family is PLA, every active exact-family Local PLA Filament must be selected/added automatically to the created/repaired Source Profile. Real Catalog currently has 16 active PLA offers. #625 existing 5×5×5 Profile 1 must remain unchanged; only missing Profile 2 dimensions use the explicit 4×4×4cm owner-estimated fallback.

## 2026-09-21 - Owner: new Product images sent from Windows must replace the live Site images
Status: `A2V PRODUCTION_VERIFIED / CLOSED`.

The revision-10 stale-image path was traced to split Local image authority, not Site cache. A2V makes `ارسال سایت` the persisted Product-image authority, keeps bulk `ویرایش` independent, fails closed on authority drift and preserves persisted Site-selected local images across refetch.

Real acceptance is complete without guessing any unrecorded `phase49_3c_*` file. At publish time #625 persisted exactly `local://04.webp` as the Site image and Primary. Batch `desktop_catalog_v85_20260921_081158` / UUID `cb51fb28-acd2-45a7-8a86-40ea5268614c` updated the same Site Product #39 from revision 10 to 11 exactly once. Local final SEO, Batch, Production storage and public HTTPS image all match SHA256 `cf6f0422f0cde915e9203ddbca6564df694fb4b6a97320e1af0e7f4117c68fff`; public Product/image HTTP checks are 200 and exactly three current CC Variants remain active.

The requested fresh snapshot immediately before this publish was not captured before revision 11 completed. This is documented rather than hidden: the verified revision-10 A2V rollback remains available, a fresh post-revision-11 integrity-checked snapshot was created, and no unnecessary revision 12 was produced. A2V needs no further #625 publication.

## 2026-09-20 - Owner: restore the actual latest Windows Catalog Center
Status: `A2U ACCEPTED / v8.9.11 WINDOWS VERIFIED`.

Owner reported that the Desktop launcher reopened an older UI where the repaired Product image workspace/SEO behavior had regressed, and #625 again showed `PRODUCT_MEDIA_NOT_FOUND_IN_PUBLIC_HTML`. Repository history proved the latest Windows code already existed in GitHub on the `f1b58645...` lineage; the error came from selecting the wrong operator lineage, not from missing Git history.

A2U preserves the latest gallery/image/SEO/screenshot fixes, ports only the newer Social v5 handoff, and is pushed at `d77dfd95...`. #625 Site Product #39 revision 9 was already updated by the failed-looking attempt; latest verification found Product HTTP 200 and 2/2 canonical media HTTP 200, so Local state was reconciled to uploaded/clean without re-import. Desktop launchers now open the A2U v8.9.11 worktree.

## 2026-09-20 - Owner: finish Hero line, Instagram SEO and remaining phases
Status: `A2Q SOCIAL LOCAL_TESTED / HERO RELEASE LOCAL_TESTED / PUBLISH NEXT`.

Owner requests immediate removal of the remaining lower Hero line plus Instagram SEO hardening and continuation of the remaining phases. Instagram SEO v4 now uses Product-specific keyword priority, explicit 3DPrintHub ordering copy, UTM link, nationwide shipping, per-image ALT and bounded hashtags, and removes false «رایگان» claims before provider submission. The already-sent #625 revision-8 Feed/Story is protected by duplicate-revision guards and will not be recreated.

## 2026-09-19 - Owner: finish homepage frame, Instagram SEO and remaining publish phases
Status: `HERO PRODUCTION_PASS / A2O LOCAL_TESTED / PRODUCT+SOCIAL ACCEPTANCE NEXT`.

Owner supplied a homepage screenshot marking the lower rectangular line under the Slicebox and asked to finish remaining phases quickly, including Instagram Feed/Story and Instagram SEO. Current Production `36a69e76...` already carries Hero 50.9 where the legacy raster shadow node/runtime is removed; browser verification confirms no shadow DOM and healthy desktop/mobile slider behavior.

Before the social acceptance retry, Windows A2O closes a newly observed reliability gap: a failed same-Product republish must retain the last verified Site Product identity/ACK. After commit/push, restore #625 linkage from verified rollback evidence, re-publish exactly once, verify Product #39 current fields/media, then use only that current Site revision for Buffer-compatible Feed PNG + branded Story, Product SEO caption/ALT/bounded hashtags/UTM/nationwide shipping CTA and Highlight queue receipt.

## 2026-09-19 - Owner: re-send must completely update the existing Site Product
Status: `A2M LOCAL_TESTED / GITHUB+PRODUCTION NEXT`.

Owner reports that an already-published Product was edited in Windows (new image, weight, materials and price) and sent again, but the Site still showed the old configuration. Required permanent behavior: keep the same Site Product identity, but every current Windows field/setting becomes authoritative on re-publish; old active commerce choices must not coexist with the new snapshot.

Real #625 / Site #39 evidence proves the defect: revision 7 updated successfully, but two stale EP49-3F Variants remained active next to three current CC profiles. A2M changes re-publish to active-state replacement, preserves old rows inactive for history, keeps exact selected-image replacement and adds an explicit local-image import/select action in Windows. Current #625 has only two selected images in Local data, so an untracked third image is not guessed or fabricated.

Instagram remains unresolved externally: no successful #625 Buffer Feed/Story receipt exists yet.

## 2026-09-19 - Owner: remove homepage slider frame, finish Instagram/SEO, publish and continue phases
Status: SITE PASS / #625 SITE REV8 PASS / REAL INSTAGRAM FEED+STORY SENT / A2P LOCAL_TESTED.

The owner screenshot highlighted the old Slicebox lower frame/shadow and requested immediate completion of homepage, Instagram, Instagram SEO and remaining phases. Fresh Production Chromium now proves Hero 50.9 has no #shadow element and no slider/wrapper/root border or box-shadow. #625 remains the same Site Product #39 at revision 8 with exactly three current active profiles and no active legacy Variant.

Real Instagram publication is complete for this revision: Feed https://www.instagram.com/p/DdepEh3if0N/ and Story https://www.instagram.com/stories/3dprinthub_ir/3989806967019651799. Feed carries two non-empty ALT texts, eight bounded relevant hashtags, factual Product copy/specs, nationwide shipping and direct UTM Product URL. Story uses the approved 1080x1920 Gold/Navy IRANSans style and records Highlight target اسباب بازی; Buffer cannot perform the final Highlight placement, so that one Instagram UI action remains operator_required.

The remaining engineering request is now A2P repeatability: future Buffer posts must automatically mirror only generated social derivatives to the verified provider-compatible media host instead of depending on the current Site origin. After A2P exact-SHA runtime closure, continue Finance/Payment/Admin and bounded Product publication phases.

## 2026-09-19 - Owner: finish Site, Desktop launcher and real Instagram acceptance
Status: `SITE+PRODUCT PASS / WINDOWS STORY FIX LOCAL_TESTED / SOCIAL COMMIT+REAL PUBLISH NEXT`.

Owner requires the website publication to be finished and the Windows app to open from the Desktop. Product #625 is now reconciled from its existing revision-6 ACK without another Site import and Local state is clean/uploaded. Home/Store/Product Browser QA is green. Desktop now contains `3DPrintHub Catalog Center.lnk` and `3DPrintHub Catalog Center.cmd`, both launching the repository-owned Qt runner.

The first real Buffer action correctly stopped before Feed creation because the branded Story render was invalid. The Windows Chrome race is now fixed and a real nonblank 1080x1920 #625 Story passes local acceptance. Next external action is one exact-SHA Feed+Story publish, with Highlight target `اسباب بازی` recorded as `operator_required`.

## 2026-09-19 - Owner: make Product upload usable now
Status: `PUBLIC ROUTE PRODUCTION_PASS / WINDOWS CHECKER LOCAL_TESTED`.

Owner requires normal Product uploads to complete instead of remaining falsely failed after a successful receiver import. #625 proves the Site receiver and strict parity are healthy; Windows public verification must understand the compact canonical Product media namespace and must never treat private imported working-media as public. After this checker is promoted, #625 should be reconciled from its existing revision-6 ACK without sending the same Product to the receiver again.

## 2026-09-19 - Owner: finish #625 today and make every Product support Feed + Story + category Highlight queue
Status: `LOCAL_TESTED / GITHUB+DEPLOY+REAL ACCEPTANCE NEXT`.

Owner requires today's acceptance to finish the real #625 Site update and then publish its Instagram Feed + Story. Every Product social publish must use the primary verified Site Product image first, Product SEO copy, ALT text, relevant bounded hashtags, direct tracked purchase URL and explicit nationwide shipping across Iran. Companion Story is required by default and must use the registered 1080x1920 Gold/Navy IRANSans style and Product URL.

Story classification must follow the approved Highlight taxonomy. Product #625 is `toys-games` and therefore queues to Highlight `اسباب بازی`. Because the official Buffer API currently has no Add-to-Highlight mutation, the system must record the target automatically and queue the final Instagram UI operator step; it must not use private APIs or fabricate automatic Highlight completion.

Before social publication, #625 Site republish must pass strict Product parity after fixing the pricing authority and repairing owner-approved active PLA service rates from verified project data.

## 2026-09-18 - Owner: finish Screenshot SEO and ensure edited image bytes replace the live Site image
Status: `LOCAL_ACCEPTED / COMMIT+PUSH+REPUBLISH NEXT`.

Owner reported that the SEO button on a Screenshot still opened empty fields and that editing a local image then uploading the Product again did not visibly replace the live image. Required behavior: single-image SEO must be prefilled from Product SEO when metadata is absent; Screenshot SEO may be saved without forcing Site selection; the bulk `اصلاح اسم و سئو` must include all editable images when no explicit subset is selected; and re-publish must detect changed source bytes, rebuild the finalized SEO WebP, and update the same existing Site Product.

## 2026-09-18 - Owner: combine image filename+SEO repair and make re-upload update existing Site Product
Status: `LOCAL_ACCEPTED / FINAL GATE + GITHUB PROMOTION NEXT`.

Owner requires one Stage-3 action named `اصلاح اسم و سئو`: selected image(s) must receive complete Product image SEO and deterministic SEO filename together; when no temporary subset is selected, all Site-selected images should be standardized. Existing manual per-image/bulk SEO editing remains available.

Owner also requires a Product already published to Site to keep its existing Site identity: after any explicit Windows edit and re-send, the previous Product must be updated in place rather than remaining stale or creating a duplicate. Site remains the current priority; after deploy and verification, #152 is Site-first then Instagram, while #309/#301 must not be reposted.

## 2026-09-18 - Owner: site first / remove duplicate Filament cards / fix Product edit 504 / English Profile identity
Status: `LOCAL_ACCEPTED / COMMIT+PUSH+DEPLOY NEXT`.

Owner requires the public Product page to remove the duplicate “رنگ و Filament قابل سفارش” roll-price cards because the four-step selector is the ordering authority. Product Admin edit must stop returning 504. Windows Product Profile “نام پروفایل” and “سایز” must not be Persian/corrupt; use English/ASCII identity while preserving Product Material/Color data. Site publication has priority over further social work. After Site deploy, Product #152 must publish Site-first and then Instagram; existing #309/#301 Instagram posts must not be duplicated.

## 2026-09-18 - Owner image naming/scroll correction runtime status
Status: `GITHUB_UPDATED / QT_RELAUNCHED / OWNER_SMOKE NEXT`.

The requested mature image naming rule (English source title) and four-row scroll reserve are now running from exact GitHub runtime `aaa5cb9f6d743becf3f1588501733ae835bd7451`. Semantic image SEO/AI metadata remains unchanged and verified on Product #301.

## 2026-09-18 - Owner: restore prior image SEO naming; keep four-row scroll
Status: `LOCAL_TESTED / COMMIT+PUSH NEXT`.

Owner requires the previous mature image SEO path to remain intact: filenames based on the Product's English source title, plus Product-specific Alt/SEO image metadata. Only the filename planner was corrected; semantic image metadata and AI workflows must not be altered. The image gallery must retain scroll space for at least four rows even when empty.

## 2026-09-18 - Owner Stage-3 3×3 runtime status
Status: `GITHUB_UPDATED / QT_RELAUNCHED / OWNER_SMOKE NEXT`.

The requested three-column compact gallery is now running from exact GitHub commit `a52cd52a18a119f9aa2940ebc00f588828d1a558`. Owner visual smoke is the remaining Windows acceptance gate. Site deployment remains blocked strictly on the dedicated reverse tunnel, which currently does not listen on `127.0.0.1:22024`.

## 2026-09-18 - Owner correction: three images per row / three rows visible
Status: `LOCAL_TESTED / COMMIT+PUSH NEXT`.

Owner explicitly rejects oversized image cards. Required visual contract: three images per row; by default three complete rows visible with filename and menus below each image; the Gallery itself should consume the available vertical space. Existing operations/modes/SEO/Screenshot/select/delete/reorder behavior must not change.

Owner also reconfirmed the Host rule: assistant Host/Production work must use only the dedicated reverse tunnel. Windows browser/cPanel/Terminal is not an allowed alternate deployment path.

## 2026-09-18 - Owner: design only in Windows + exact Slicebox Example-4 homepage
Status: `LOCAL_ACCEPTED / GITHUB PROMOTION + HOST VERIFY NEXT`.

Owner explicitly requires no Windows workflow/mode/operation changes: only compact the Stage-3 controls into one row, compact the bottom stage/navigation controls into one row, and allocate the freed height to the image review area. For the public homepage, remove the appearance/behavior of the previous top slider and present Product-backed Hero data with the Tympanus/Codrops Slicebox Example-4 3D method, using the 3DPrintHub site background and the reference-style frame/arrows/shadow/dots.

Local acceptance is complete. The browser also exposed the actual reason the earlier Slicebox could appear absent: hidden lazy slides prevented the vendor all-images-ready gate from completing. The fix keeps Hero data unchanged and eagerly loads the four Hero images.

## 2026-09-18 - Owner Stage-3 scroll complaint runtime status
Status: `GITHUB_UPDATED / QT_RELAUNCHED / OWNER_SMOKE NEXT`.

The specific hotfix for the owner screenshot is now running: the Stage-3 gallery fits the desktop and mouse-wheel input over the image preview is forwarded to the gallery scrollbar. Owner smoke on the same Product is the remaining acceptance gate.

## 2026-09-18 - Owner screenshot: Stage-3 lower image controls still unreachable
Status: `LOCAL_TESTED / COMMIT+PUSH+RELAUNCH NEXT`.

Owner requires the image-review area to be visibly much larger in real use while keeping filename, selection, edit and delete controls reachable. The user screenshot shows large images but the lower controls are effectively off-screen and mouse-wheel scrolling over the image itself does not move the gallery. Acceptance is: keep image cards/previews large, keep existing image/SEO/Screenshot logic unchanged, fit the Product Wizard inside the real Windows working area, and make wheel scrolling work directly over the image surface.

## 2026-09-18 - Owner request: professional Stage-3 image workspace
Status: `LOCAL_TESTED / COMMIT+PUSH / EXACT-SHA RELAUNCH NEXT`.

Owner requires the Product image area to be substantially larger and easier to scroll/review, with smaller surrounding controls. Any subset of images must be selectable for bulk Edit/Delete without changing which images belong to the Site Product. Image names must follow the existing deterministic SEO naming rules rather than raw numeric source filenames. The Product main image must be the first/cover media for the Instagram feed while the remaining verified Product images stay available for the carousel.

Acceptance also includes legacy real numbered Product files: if the file physically exists in the trusted Product images directory it must be visible, selectable and editable; removal must remain recoverable. Screenshot capture/naming itself remains unchanged.

## 2026-09-18 - Owner report: Product Screenshot button still appears non-functional
Status: `GITHUB_UPDATED / EXACT-SHA QT RELAUNCHED / OWNER SMOKE NEXT`.
Owner reports the Product Screenshot button still does not work. Real Product #628 evidence proves capture itself is succeeding; the newer numbered-image resolver hides the persisted manual Screenshot after refresh. Acceptance is narrow: keep capture/naming/SEO/button behavior unchanged, make explicitly persisted `source-page-screenshot` images visible in the same Product gallery, prevent them from stealing numbered source-image identity, pass the maintained image/Qt regression gate, then push and relaunch. Production remains untouched.

## 2026-09-18 - Owner correction: only enlarge Product image display
Status: `LOCAL_TESTED / GITHUB PROMOTION + EXACT-SHA RELAUNCH NEXT`.
Owner explicitly requires all mature Stage-3 image workflows to remain exactly as they were, including image filename behavior and Screenshot capture/naming. Revert the recent control/layout/recover-limit/AI-visibility/window-geometry and filename-display changes; enlarge only the image review cards/preview surface. Production is untouched.

## 2026-09-18 - Owner continuation: real Windows image workspace + full Filament repair
Status: `LOCAL_TESTED / FOLLOW-UP PUSH+RELAUNCH NEXT / PRODUCTION TUNNEL BLOCKED`.
Owner asked development to continue after reporting that Product image review was too small/non-scrollable and `Sync همه با سایت` failed. Exact pushed A2L runtime now proves Product #628 has 10 locally viewable images in a two-column large-card scrolling workspace. Real Catalog audit found 63/71 legacy Filament rows missing Brand; the application must not invent those identities. Acceptance therefore includes fail-soft valid-row sync plus explicit selected-row repair from the registered Brand library, selected/all operating-rate edits, smart material rules and AI Preview already delivered in A2L. Follow-up regression gate is 57/57 PASS. Production remains gated by the dedicated 22024 reverse tunnel.

## 2026-09-17 - Owner requires the modern Windows app, not the legacy launcher
Status: `LOCAL_GATED / GITHUB PROMOTION + EXACT-SHA RELAUNCH NEXT`.
Owner explicitly requires the newer Qt Catalog Center containing the Product/Filament/image/publish work and does not accept the older UI opening by mistake. Repository forensics prove `RUN.ps1` / `RUN_DEBUG.ps1` are legacy `launch.py` entrypoints while the requested application is `qt_launch.py`. Acceptance is: preserve all modern Product/Filament/republish behavior, add one explicit operator Qt launcher, keep legacy launchers only for rollback, commit/push the tested candidate, close duplicate/stale app instances, and relaunch exactly one modern Qt process from the pushed SHA against the canonical Catalog DB. Production Product reset/receiver work follows only after fresh reverse-tunnel verification and rollback evidence.

## 2026-09-16 - Owner image workspace reorder + immediate Windows relaunch
Status: `LOCAL_TESTED / PUSH+BACKUP+RECEIVER+LAUNCH NEXT`.
Owner requires the remaining Windows image workspace gap to be closed before Product/image entry resumes. Stage 3 now has explicit per-image previous/next controls for trusted selected images; Primary remains slot 1, secondary order is persisted, URL-owned Alt/metadata/Slider facts stay attached, and SEO WebP numbering is rebuilt immediately. Uploaded Products become guarded republish work rather than duplicate Products. Local dedicated/broader gates are 12/12, 27/27 and 87/87 PASS. Acceptance still requires exact GitHub push, fresh Catalog rollback backup, live receiver verification, `qt_launch.py --verify-only` and launch from the pushed SHA.

## 2026-09-15 - Owner urgent Product-entry request ACCEPTED
Status: `PRODUCTION_ACCEPTED / WINDOWS DIRECT SEND LIVE`.
Owner requested immediate ability to enter Products in the Windows app and send them to the Site. Product Wizard Stage 7 now contains direct Ready/Send actions; runtime is pushed at `6e306e5...` and relaunched. Real #628 Windows -> FTP -> Bridge -> Store acceptance passed with Site Product #21, public WebP media, 190 orderable Variants and real browser Cart wiring. No test StoreOrder was created. Owner can proceed with Product entry; factual incomplete Products remain blocked rather than force-published.

## 2026-09-15 - Owner urgent Product entry + direct Product send request
Status: `LOCAL_TESTED / DIRECT SINGLE-PRODUCT SEND IMPLEMENTED / REAL PRODUCT ACCEPTANCE NEXT`.
Owner needs Catalog Center immediately for adding Products and expects both Windows and Site publication paths to work from the Product being edited. Stage 7 now provides direct Ready and Send-to-Site actions using the mature guarded publisher. Current live receiver is ready and FTP passes; 12 current Ready Products pass preflight. Acceptance requires one real known-good Product publish with strict public Product/media/Variant/Cart verification before wider publication.

## 2026-09-15 - Owner client-handoff request ACCEPTED on Production
Status: `PRODUCTION_ACCEPTED / EMPTY STORE / HERO 50.3.0 LIVE`.

The requested handoff outcome is now factual Production state: the current GitHub handoff source is live at `b1caeba0f20e711b29dfa9e0ff92a2f5186fb08d`; the prior Store catalog was removed only after verified MySQL + Product-media rollback evidence; Store currently has no Product cards; source/master/Portfolio/Hero data is preserved; and the new full-screen Hero 50.3.0 produces real randomized native 3D cuboids on capable desktop while mobile uses the safe fallback without horizontal overflow. Site?Instagram remains credential-gated and is not falsely claimed live without Professional Instagram credentials.

## 2026-09-15 - Owner client-handoff request: empty Store, finish prior app changes, replace stale Hero and publish
Status: `LOCAL_IMPLEMENTED + TESTED / GITHUB+PRODUCTION NEXT`.

Owner requires the client-facing site to stop showing the old Product catalog, all previously requested Windows publishing changes to be checked rather than assumed, and the visibly stale top slider to be replaced with the professional 3D implementation before handoff. Accepted execution order is GitHub-first and rollback-safe: deploy the tested source, create and verify fresh Production source/environment/static/MySQL/Product-media backups, run exact reset preflight, remove only eligible imported Store Products, preserve source assets/master data/Portfolio/Hero/history, then verify an empty Store plus the new live Hero in a real browser. Site→Instagram remains Site-first and cannot be claimed live until Professional Instagram credentials are configured.

## 2026-09-14 - Owner request: restore Published Products and real Product images in the Windows app
Status: `LOCAL_TESTED / COMMIT+PUSH+FOREGROUND ACCEPTANCE NEXT`.

Owner requires the `Sent / Published` workspace to continue showing Products already sent to the Site even when they have new Local edits, and Product image galleries must show the real downloaded/finalized files rather than dozens of broken placeholders generated from historical source URLs. The gallery should be compact and usable. The accepted implementation keeps dirty published Products visible while separately queueing republish, displays factual local files including legacy numbered media, protects unmapped compatibility files from mutation, and preserves the strict modern SEO/publish media contract. Real Catalog evidence and 77/77 related regressions PASS.

## 2026-09-14 - Owner sales-start request: expand only genuinely orderable Products
Owner requested that products/site stay current and sales begin immediately. Current accepted sales set is Site Product #16 (#628), #17 (#634), and #18 (#62). Continue widening only after strict Profile/media/license/orderability/Cart gates; do not expose Product #19 (#84) as sellable while its selected black-matte inventory is zero, and do not guess missing facts for #43.

## 2026-09-14 - Immediate sales truth
Owner wants current Products/site and immediate selling. The implementation must prefer a smaller actually-orderable catalog over public Products whose Cart is disabled. #62 is eligible for factual repair; #84 stays off Store until its selected black-matte filament has real stock; #43 remains blocked on factual Material/Color.

## 2026-09-14 - Start selling with current Products/site kept live and trustworthy
Owner priority is immediate sales start with Products and site kept current. Execution rule: widen publication only when Product pages, media, canonical Profile/Variant mapping, price and real customer Cart are all verified. #628/#634 are accepted sales-ready; #62/#84 require Profile repair + republish after ERR-49-135; #43 must not be completed by guessing missing Material/Color.

## 2026-09-14 - Start real sales publication
Owner requested direct continuation toward selling. Implemented bounded production publication after the owner-license parity hotfix: #628 and #634 are now publicly orderable and browser-verified. Remaining explicitly ready candidates are #43/#62/#84 and must still pass fresh factual stage/media/readiness gates before publication; do not widen beyond the passing subset automatically.

## 2026-09-14 - Start selling with bounded real Product publication
Status: `IN_PROGRESS / OWNER-LICENSE HOST PARITY LOCAL_TESTED`.
Owner requested continued development through direct Host access so the site can start selling. The current bounded publication blocker is ERR-49-131: Host must honor the repository's existing explicit owner source/license approval without falsifying source license evidence. Hotfix is Local-tested; next is guarded GitHub-first Production deployment and exact retry of Products #628/#634 before widening the sellable catalog.

## 2026-09-14 - Professional 3D slider + Product site-send issue Production-verified
Status: `TECHNICAL_GATE_PASS`.
The owner-reported regressions around the old/unprofessional slider and Product site-send path are now verified on Production: the managed Home Hero uses the new seven-slice A2I 3D transition on desktop with safe mobile fallback, and the controlled Product #63 is published as Site Product #15 with strict ACK, public Product-owned WebP media, canonical Variant selection and working Cart form wiring. No uncontrolled bulk publish has been started.
## 2026-09-14 - Continue current 3DPrintHub development from repository truth
Status: `IN_PROGRESS`.
The active requested continuation is to finish the professional 3D Hero/public Product publishing path from the verified repository state, not from chat memory. The immediate delivery gate is the combined A2I Hero + ERR-49-125 Bridge public-media Production promotion followed by Product #63 selector/cart/strict-ACK acceptance before any bounded bulk publication.
## 2026-09-13 - Controlled Product publish acceptance follow-up
Owner requested uninterrupted continuation through the first real Product acceptance. Product #63 is the controlled candidate. Current blocking defect is narrowed to Bridge public-media serialization; Local fix is tested and must be GitHub-deployed/Production-verified before final selector/cart/ACK acceptance. Multi-product publish remains intentionally locked until this Product passes end to end.
## REQ-50-032 - Professional Storefront product showcase and selected-price hierarchy
Date: 2026-09-13
Status: `LOCAL_TESTED / GITHUB+PRODUCTION NEXT`.

Acceptance: Home Hero must prioritize the Product image and keep editorial copy spatially clear across desktop/tablet/mobile; selected configurator price must be visually unambiguous while remaining sourced from the canonical real ProductVariant; the one-time theme chooser must not obscure the Product by default but must remain keyboard-accessible and retain existing choices/persistence. No pricing/business/migration authority may move into presentation JS/CSS. Local responsive/browser gates PASS; Production remains on the prior verified source until guarded GitHub-first deployment.

## 2026-09-13 - REQ-50-031/030 verification checkpoint
Reverse management transport is E2E verified and active at Windows loopback `22024` -> Host bridge `22224`; authenticated Production identity/worktree/audit pass at `d7cf71d...`. Phase50.A.2G is Production verified. Remaining request acceptance is one controlled real Product Windows-to-Site publish with strict ACK, finalized SEO WebP, Product/Profile/Variant, public page/media and cart verification.

## REQ-50-031 - Direct shared-Host management through proven reverse tunnel transport
Date: 2026-09-13
Status: `E2E_VERIFIED / ACTIVE OPERATIONS TRANSPORT`.

Required behavior: reuse the proven Asal shared-cPanel pattern instead of requiring inbound Host SSH. Host runs an authenticated loopback-only command bridge, opens outbound SSH/443 to the owner Windows PC, and exposes only project loopback `22024`. 3DPrintHub uses `PrintHubTunnel`, Host bridge `22224`, Windows public endpoint `37.255.236.184:443`, and Host source restriction `89.39.208.237/32`. Secrets stay outside Git/chat and transport never bypasses GitHub-first deploy, backup/rollback, migration or Production verification gates.

## REQ-50-030 - Publish-ready Product media + professional responsive ordering wizard
Date: 2026-09-12
Status: `PRODUCTION_VERIFIED / ONE CONTROLLED PRODUCT ACCEPTANCE NEXT`.

Acceptance: only finalized current SEO WebP media can become Ready; exact WebP filename/bytes must survive Windows-to-Batch-to-Host; changed explicit media refreshes the existing Site identity while identical bytes remain idempotent; desktop_product_id identity is stable from first import; customer ordering remains size -> color -> compatible material -> print quality with professional progress/guidance, keyboard/touch accessibility, mobile/tablet/desktop responsiveness and native canonical Variant fallback. Server price/stock/weight/time remain authoritative.

Local evidence: Catalog 10/10 PASS; Django 16/16 PASS; Node 8/8 PASS; Playwright responsive suite PASS; compile/check/no migration drift/diff check PASS; A2G deploy runner syntax/no-migrate/exact-delta PASS. Production is verified at `d7cf71d...`; authenticated audit/readiness/public A2G gates PASS. One controlled Product acceptance is required before bulk publication.

## REQ-50-029 — Customer guided Product configurator`r`nDate: 2026-09-12`r`nStatus: `PRODUCTION_VERIFIED`.

Required behavior:
- customer chooses size → color → compatible material → print quality instead of reasoning about internal Profile/Variant rows;
- each next choice is restricted only by valid upstream choices;
- changing upstream state clears incompatible downstream state;
- unavailable combinations cannot enable cart;
- duplicate combinations require an explicit canonical final Variant instead of silently choosing the wrong brand/profile;
- server/API price, stock, material, quality, weight and print time remain authoritative;
- native Variant selector remains usable when JavaScript/API enhancement fails;
- mobile layout remains usable without horizontal overflow;
- no new migration or parallel commerce model.

Local acceptance: Node 8/8, Django 15/15 and Playwright desktop/mobile/cart/fallback/stock/ambiguity/>100 PASS; no migration drift.
Production pre-deploy acceptance: live Bridge/readiness on 2026-09-12 reports MySQL ready with Store 0036–0042 + Website 0024 applied and no blockers; canonical Windows gate on 38458ce... passed 139 + 34 + 68 tests. Deployment is intentionally no-migration from verified Host baseline e12fdaf....
## REQ-49-097 — Recover Production safely from a partially executed MySQL 0039
Date: 2026-09-02  
Status: `IMPLEMENTED + REAL MYSQL PROBE PASS / HOST EXECUTION NEXT`.

Required behavior after the Production 1060 duplicate-column stop:
- do not fake migration 0039;
- do not blindly rerun old 0039;
- do not restore the whole DB unless current partial state cannot be reconciled safely;
- first verify migration recorder and exact physical columns;
- preserve the two valid pre-migration rollback dumps;
- create a fresh backup of the CURRENT partial DB before repair;
- correct historical duplicate ownership of ProductVariant support weight;
- safely reuse already-created prefix columns if the Host matches the observed failure boundary;
- apply only the exact remaining 0039–0042 plan;
- require receiver readiness, collectstatic, restart and public/Bridge verification before Product publishing.

Verification: `66e940e6e659f86e3783d78d091b3ff00acbf5aa`; Product Admin/MySQL `33666085743` PASS; Single Active AI `33666085841` PASS.

## REQ-49-096 — Resume Production safely after source promotion but before migrations
Date: 2026-09-02  
Status: `IMPLEMENTED + CI PASS / HOST RESUME NEXT`.

Required behavior:
- recognize that Production source already moved to `b372586a...`;
- do not pretend the old `198fa8e...` deploy baseline is still checked out;
- preserve/reverify the valid pre-migration rollback backup;
- restore ordinary Django startup even when optional AI transport is unavailable;
- install exactly the dependency declared by target requirements;
- take a fresh DB backup before migration;
- require the exact pending migration plan;
- then migrate, collectstatic, restart and verify receiver/public endpoints;
- no bulk Product publish until one end-to-end Product succeeds.

Verification: `ccd1b98997a8dd0c8389ccbe2b6c78b83dd7f176`; Product Admin `33663316332` PASS; Single Active AI `33663316324` PASS.

## REQ-49-095 — Backup helper must work before source promotion from an external backup directory
Date: 2026-09-02  
Status: `IMPLEMENTED + CI PASS / DEPLOY RETRY NEXT`.

Required behavior:
- backup helper remains outside the live repository before ff-only promotion;
- Django settings import must not depend on script location or shell cwd;
- exact Production project root is explicit and validated;
- no source promotion until MySQL backup is real gzip + checksum verified.

Verification: `2016b84ee1b053e792ceb44ede516b3d7a2dea7e`; Product Admin `33661199115` PASS; Single Active AI `33661199159` PASS.

## REQ-49-094 — Production receiver deploy must stop unless MySQL backup is a real verified gzip
Date: 2026-09-02  
Status: `IMPLEMENTED + CI PASS / DEPLOY RETRY NEXT`.

Accepted behavior:
- no source promotion before a valid MySQL rollback artifact exists;
- backup suffix alone is insufficient;
- mysqldump bytes must pass through a real gzip encoder;
- gzip magic, dump signature, full `gzip -t` and SHA256 must all pass;
- partial/invalid backup stops deployment;
- failed backup evidence is retained rather than silently reused;
- retry uses a new timestamped backup directory.

Verification: `3b6254bf7700bb26b4af63d21e31e56e7700877c`; Product Admin CI `33659707983` PASS; Single Active AI `33659707957` PASS.

## REQ-49-093 — Make the Site/Host ready to receive Products from Catalog Center
Date: 2026-09-02  
Status: `IMPLEMENTED + CI PASS / HOST READ-ONLY AUDIT NEXT / PRODUCTION NOT DEPLOYED`.

Owner request:
- move focus from the now-usable Windows Crawl/Product repair to the Site and Host;
- make the website receiver reliable enough that selected ready Products can be sent from Catalog Center;
- do not upload a Product into a Host that is missing migrations/schema/storage/prerequisites;
- keep the mature Batch/FTP/Bridge/public-verification workflow rather than inventing a second publishing system.

Acceptance implemented:
- authenticated live receiver-readiness endpoint;
- Desktop checks receiver before any FTP;
- exact blockers include migration/schema/storage/token/prerequisite state;
- Bridge connectivity remains separately visible;
- repository-owned Host read-only audit verifies real Production before deploy;
- current pending migration chain is explicitly known but not assumed applied;
- no Production change before fresh audit/backups.

Evidence: Site `33652584032`, Variant/Profile `33652583964`, Host-audit contract `33652996666`, Qt `33653229142`, Single Active AI `33653229219`, Portable `33653229400` PASS. Final code checkpoint `62ce5c3393a888cc1a027e4ca6bbb88f189bc845`.

## REQ-49-086 — Adaptive Product recovery + visible acquisition diagnostics
Date: 2026-09-02  
Status: `IMPLEMENTED + WINDOWS CI/PORTABLE PASS / OWNER LOCAL REAL-SOURCE QA NEXT`.

Acceptance implemented:
- discovering a Crawl URL/Preview does not claim full Product success;
- runtime logs method, source/external id, Product data/image evidence, failure reason and method transition;
- unusable Product data or no local image moves to another distinct mature method;
- aliases are not counted as fake additional retries;
- a successful method becomes first choice for later Products in that batch;
- after all real methods fail, later selected rows stay untouched instead of all becoming failed;
- invalid Product identities stop similarly;
- operator content/pricing/publish and mature Source Refresh contracts are preserved.

Verification: `bf1fafdb38233a23e13a5715ffac72f772412005`; Qt `33644903042`, Single Active AI `33644902970`, Portable `33644902962` PASS; dedicated 27-test suite and 235 portable regressions PASS.

## REQ-49-092 — Bulk recover incomplete Crawl Product data and images
Date: 2026-09-02  
Status: `IMPLEMENTED + GITHUB CI PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT DEPLOYED`.

Owner request:
- select many incomplete permanent Crawl rows at once;
- choose 5 or 10 Product images;
- use already-available DB/local images when sufficient;
- otherwise revisit the Product URL and recover title, description and images;
- do not require manually opening every Product URL;
- previously-collected-but-broken identities must be repairable without being permanently skipped by the terminal ledger.

Acceptance implemented:
- `انتخاب ناقص‌ها`;
- 5/10/20 image target;
- `بازیابی دیتا + عکس`;
- local reuse before network;
- forced explicit recovery bypasses terminal skip only for the operator-requested recovery action;
- existing Product refetch uses safe mature merge;
- URL-slug readable title fallback.

Verification: runtime `cf73f841418aac2eec1b78e0dbd682ceb2d3fef5`; Qt `33637452385` PASS; Portable `33637452243` PASS; 227 regressions.

## REQ-49-091 — Permanent Crawl inventory must show recent and historical images consistently
Date: 2026-09-02  
Status: `IMPLEMENTED + GITHUB CI PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT DEPLOYED`.

Owner evidence:
- permanent inventory shows images for some rows but not many recent rows and some historical rows;
- recent `new` identities need visual listing Preview before full receive;
- historical rows with already-downloaded files must reuse every mature storage variant.

Acceptance implemented:
- exact and mature refetch/source-refresh folders are resolved read-only;
- lazy MakerWorld listing image attributes are captured for Preview;
- same Search can be rerun to backfill empty Preview evidence without duplicate identities;
- local image count remains based on real files.

Verification: runtime `016e84ab98d2e5577633833cbc87cb96824dbbf0`; Qt `33632062812` PASS; Portable `33632062880` PASS; 223 regressions.

## REQ-49-090 — Show already-downloaded Crawl images and repair overlapped numeric inputs
Date: 2026-09-02  
Status: `IMPLEMENTED + GITHUB CI PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT DEPLOYED`.

Owner request:
- in Add Products / Crawl, show images that were already downloaded by the previous Catalog Center instead of reporting no Preview;
- reuse the previous program's real storage path rather than download the same images again;
- show `N عکس دارد` below each item;
- fix the overlapping requested-count and per-Product image-count numeric controls.

Acceptance implemented:
- verified mature image storage under `D:\projects\3dprinthub-catalog-manager\collected\<source>\<external_id>\images`;
- Qt reads mature local images directly even when the Crawl row is not linked to a Product id;
- `seo_images` is preferred when available;
- legacy source-code casing no longer hides matching Product rows;
- real local image count is visible in Crawl cards/table and single-item live review;
- no image re-download or destructive data move is needed;
- numeric spinboxes are LTR, centered, width-bounded and safely padded from arrow buttons.

Verification:
`a18b6f3036d41271cf3e8c1d9a0dfd8c271a53ce`; Qt `33628825851` PASS; Single Active AI `33628825772` PASS; Portable `33628825715` PASS with 221 release tests.

## REQ-49-089 — Restore visual Crawl review, multi-select transfer and safe Product image/data recovery
Date: 2026-09-02  
Status: `GITHUB_UPDATED + WINDOWS CI PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT DEPLOYED`.

Owner request:
- Crawl/Add Product must show Product images instead of text-only identities;
- every card must expose how many images are available/saved;
- while collecting a Product the operator must see image progress such as 3/5, 4/5, 5/5 and then move to the next Product;
- each new Search must clear the prior Search result area and show only the current Search candidates;
- multiple candidates must be selectable together for add/reject operations;
- selected collected Products must actually route into the Products workspace;
- persistent Crawl inventory must remain visual, not hide older products or thumbnails;
- Product editing must include an explicit action to fetch more source data/images from the Product link;
- source recovery must not overwrite operator-owned Persian content, price or publish state;
- controls must be task-focused and readable rather than a dense row of long labels;
- the app must visibly identify the current 3I.52C shell instead of showing the stale 3I.48 phase footer.

Acceptance implemented:
- current-search icon/card gallery with stable Preview thumbnails and image-count copy;
- selected collected Product exposes its real local image strip plus total/local-displayable image counts;
- long receive actions use compact labels with explanatory tooltips;
- new Search clears prior live cards;
- per-image acquisition progress callback;
- explicit MultiSelection + select-all/clear + selected-count state in current Search and persistent inventory;
- bulk selected transfer returns Product ids and navigates to Products;
- persistent inventory reuses candidate/legacy Preview title and thumbnail;
- Product image/source stage exposes `دریافت داده و عکس بیشتر از لینک محصول`;
- safe recovery updates source data/images and preserves operator title/description/final price/sale approval/publish decision.

Verification:
- Qt6 run `33625988684` PASS;
- Single Active AI `33625988674` PASS;
- Windows Portable `33625988663` PASS after correcting its Qt dependency boundary;
- portable regression gate 218 tests PASS;
- final runtime/CI checkpoint `f43c7aa464948832ba349543f94c94498490ab25`;
- Production untouched.

Owner Local foreground acceptance is still required before this request can be marked ACCEPTED.

## REQ-49-088 — Site fallback Product authoring, shared low-cost Persian AI and safe bidirectional Windows sync
Date: 2026-09-02  
Status: `IMPLEMENTED + GITHUB CI PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT DEPLOYED`.

Owner request:
- the Site must remain operable when the Windows application is unavailable;
- Product can be added/edited directly on Site, including the same pricing/Profile/Variant authority;
- Host gets the same Product AI method with a cheap/free Persian-capable model policy;
- AI implementation experience is collected under a root `ai/` folder for controlled reuse in other projects;
- later Windows work must reconcile Site edits rather than overwrite them.

Acceptance implemented:
- Site Admin reuses canonical Product/ProductCatalogProfile/ProductVariant, not a duplicate commerce store;
- shared Host AI reuses mature Structured + semantic validation, prefers a verified exact free Persian Structured model, then a bounded low-cost fallback;
- variable OpenRouter routers are not accepted as the final Product model;
- AI is Preview-before-Apply and cannot mutate operator-owned price/stock/material/color/license/factual production data/publish state;
- Host keys remain environment-only;
- Windows can explicitly pull Site Product changes through Bridge;
- newer Site revisions overwrite only clean Local mirrors; dirty Local edits produce an explicit conflict;
- Site-only Products are mirrored as non-publishable Local records until source identity is established;
- republish verifies the live Site revision before Batch packaging and fails closed on mismatch;
- full Pricing/Profile payload needed for this contract round-trips through Bridge.

Evidence:
`33619876564`, `33619876411`, `33619876317`, `33619558467`, `33619558562` PASS. Tested source: `6d19bed7659b9ca4cd54ff1ffd1323ec423bea6a`.

Cross-project note:
`ai/README.md` and `ai/PLAYBOOK_FA.md` are the canonical reusable policy/playbook. Other repositories must still be updated only after reading and verifying that repository's own `AGENTS.md`, architecture, secrets and tests; this change does not silently modify unrelated repositories.

## REQ-49-087 — Finalize Windows Product/Crawl/Profile/Filament parity and matching Site Filament management
Date: 2026-09-02  
Status: `IMPLEMENTED + WINDOWS/SITE CI PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT DEPLOYED`.

Owner request:
- keep the mature Windows Catalog workflow but finish the Product image/source/Crawl usability gaps;
- pasted MakerWorld links must not run under a stale GrabCAD Source;
- create a usable default Profile when source weight/time/dimensions/material evidence is incomplete;
- default production fallback is 100 g model + 50 g support + 60 minutes;
- match all active PLA/PETG-family Filaments for that fallback instead of one hard-coded offer;
- manage Filaments, Materials, Brands and Colors as separate reusable entities;
- Brand/Material/Color must be selected from managed registries inside Filament edit;
- add optional descriptions and Material reference price/kg;
- keep Site Admin concepts aligned with Windows;
- reuse the existing authenticated Filament Bridge rather than create a new sync architecture;
- keep pricing authority and Production safety unchanged.

Acceptance:
- Product source-page action and larger image review remain available;
- multi-image selection/bulk actions remain intact;
- MakerWorld URL auto-selects MakerWorld and live receive/discovery results are visible;
- explicit `پیش‌فرض` Profile is created only when source facts cannot create a usable source-grounded Profile;
- all active PLA/PETG-family Filaments are included, unrelated materials excluded;
- registry rename propagates to assigned Filaments or fails before mutation on collision;
- Filament descriptions survive list/edit round-trip;
- selected/full Site Sync uses the mature Bridge and does not require FTP credentials;
- full reconciliation can deactivate Site rows that are inactive locally;
- Site persists FilamentBrand and optional descriptions;
- Material Admin keeps price/kg and production rates;
- Windows Qt, Bridge/Admin, migration-drift, Single Active AI and portable gates pass;
- Production stays untouched until owner Local acceptance and Host audit.

Verification:
`33611776817`, `33611776806`, `33611776891`, `33611936196`, `33611936216` PASS.

## REQ-49-086 — Multi-product ready/publish workflow and site-equivalent Slider/Admin controls
Status: `IMPLEMENTED / GITHUB CI TESTED / OWNER LOCAL QA NEXT / PRODUCTION NOT DEPLOYED`

Owner request:
- from Products, select several Products at once;
- give only complete Products an explicit `آماده انتشار` state;
- publish multiple selected-ready Products in one operation;
- after a verified successful site publish, move them automatically into the existing Published area;
- keep failures outside Published and show the reason;
- expose site-relevant software/Product/Profile/Slider controls in Django Admin;
- make Slider controls on Site equivalent to the mature Windows controls;
- apply the project’s registered UI/UX book-derived task-first/progressive-disclosure rules to the Admin layout without inventing a second settings model.

Acceptance:
- factual Stage readiness is checked before `upload_ready=1`;
- publish uses the existing Batch8.5 → FTP → Bridge → public HTTP verification path;
- only strict ACK + Store visibility/public verification can produce `workflow_status=uploaded`;
- Gallery/Table visibly distinguish ready vs published;
- successful Products appear under `ارسال / منتشرشده`;
- ProductCatalogProfile and HomepageHeroSlide share the existing persistent Slider fields and optimistic revisions;
- Slider media/composition/responsive/motion/SEO fields round-trip in both directions;
- secrets are not copied into the web Admin;
- no duplicate Product/Slider database is created;
- Windows Qt, Django Admin, no-migration and launcher regressions pass before Local QA.

Verification:
`33596830380` PASS; `33596830268` PASS; `33596562467` PASS.

## 2026-09-01 — Professional specialist store + owner Local 3I.47 failure

Owner requirements:
- 3DPrintHub must present as a professional specialist 3D-printing store, not a generic template;
- use the owner's `webdesign1` / File Library design references for architecture, Persian typography, layout, spacing, effects, responsive behavior and SEO;
- prioritize sales confidence, technical product evaluation, material/size/production clarity and a strong custom-order path;
- keep Product/Admin/Catalog management task-oriented, tabbed and readable rather than long scroll/control walls;
- use 3D only when it improves product understanding and never at the cost of initial performance;
- preserve current Django/business/pricing authority; framework-specific book examples are reference patterns, not migration instructions.

Owner Local evidence:
- Phase49.3I.47 pull to `946b8594...` was clean;
- Local gate then stopped before tests with Windows PowerShell 5.1 `ParserError` on one non-ASCII runner label;
- requested outcome is a corrected, tested GitHub runner before rerunning Local acceptance.

Repository response:
- ERR-49-088 ASCII/PS5.1 runner repair implemented and Windows CI tested;
- professional source-grounded design standard registered in `docs/PROFESSIONAL_COMMERCE_DESIGN_ARCHITECTURE.md`;
- Production remains blocked pending owner Local acceptance.

# PROJECT REQUESTS

## REQ-49-085 — Fast progressive Product/Crawl loading + full pre-Qt acquisition controls
Date: 2026-09-01  
Status: `IMPLEMENTED + WINDOWS CI PASS / OWNER LOCAL QA NEXT`

Owner requires:
- Product Gallery to open quickly with roughly 5 columns × 10 rows, then load more while scrolling;
- Windows-style detail/table view to load about 20 rows first and append later rows;
- Crawl inventory to progressively expose all records actually present in SQLite rather than hiding or dropping old collected items;
- new Qt acquisition page to retain the working options/actions from the versions before the visual rewrite;
- database access to become genuinely lighter/faster rather than loading all data and merely hiding it;
- bulk/selection/archive/reject/restore behavior to keep working with the paged UI.

Implemented at code checkpoint `a659155da4a4a41e01e926b2ac1263a1756c24e6`; Windows runs `33500317538`, `33500317554`, `33500317788` PASS. Production untouched.


## REQ-50-028 — Qt Product AI semantic repair, final SEO WebP, persistent Crawl inventory and lifecycle UX
Status: `IMPLEMENTED / WINDOWS CI + PORTABLE PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT DEPLOYED`

Acceptance:
- OpenRouter exact selected models may use either verified strict Schema or verified JSON mode; JSON-mode Product output must still satisfy the exact local schema;
- transient TLS/connect failure receives only bounded retry with no infinite loop or silent model switch;
- obvious semantic translation failures are rejected before persistence;
- `AI همه مراحل محتوایی` can deliberately repair previously finalized AI-owned content without changing operator-owned price/Profile/Filament/license/publish state;
- final selected images use physical SEO WebP filenames and metadata, not just database-only SEO labels;
- Product list visibly distinguishes lifecycle and SEO readiness;
- Products support multi-select archive, reversible reject and restore;
- all existing persistent Crawl identities are visible from Qt and support selected add/reject/restore;
- rejected Product/Crawl identities remain durable so routine crawling does not silently re-add them;
- Stage 6 numeric inputs are easy to type directly;
- all version/manifest/launcher contracts agree on 8.9.10;
- Windows Qt, Single Active AI, modern acquisition and portable build gates pass before owner Local QA.

Verification:
`33488996741`, `33488996767`, `33488996802`, `33489296415`, `33489296349` PASS.

Remaining acceptance:
owner Local foreground QA on the final documentation HEAD. Production remains untouched.


## REQ-49-084 — Product AI must survive blocked Link acquisition and prove generated data was actually applied
Status: `IMPLEMENTED / GITHUB WINDOWS CI+PORTABLE PASS / OWNER LOCAL FOREGROUND RETEST NEXT`.

Acceptance:
- a MakerWorld 403 in Link mode must not make every OpenRouter model appear broken;
- the failed direct HTTP request must not be repeated unchanged;
- if the Product already has valid crawled/saved source facts, AI continues with those facts and visibly states that Link fell back to saved data;
- if no usable saved facts exist, stop with a clear source-data error instead of a Provider/model error;
- Stage AI does not call source/Provider when the scoped stage is locked or has no AI-owned work;
- AI never says a field changed merely because `update_product` was called; persisted SQLite values are re-read and verified;
- operator-owned Filament/material/color/price/stock/publish choices remain untouched;
- variable `openrouter/auto*` routers, including `openrouter/auto-beta`, cannot be Product defaults;
- exact Product-safe models remain usable.

Evidence: code `0c67fa30493d100b99ec37314586e0491ecbcda5`; runs `33409112402`, `33409112322`, `33409112381`, `33409112367` PASS.
Production/Host remain untouched.

## REQ-49-082 — Product-safe OpenRouter model selection and strict Structured output
Status: `IMPLEMENTED / GITHUB CI PASS / OWNER LOCAL RETEST NEXT`.

Acceptance:
- “connected” must not imply Product suitability;
- Product AI only accepts text-capable OpenRouter models with verified native Structured JSON support;
- media/music/audio/video/image/embedding/rerank/moderation models are not shown in Product-oriented filters;
- Tools-only models do not receive JSON✓;
- coding-specialist models are rejected for Product Persian translation/SEO;
- OpenRouter Product Structured calls use strict JSON Schema and require compatible endpoints;
- no prompt-only JSON fallback is allowed for OpenRouter Product work;
- selected model identity remains exact and no hidden cross-model fallback is introduced;
- live free/Persian/cost information remains visible;
- active model capability is stored as non-secret metadata so ordinary Product execution does not need a hidden model scan;
- existing fail-closed Product title/SEO validation remains authoritative.

Evidence: code `0421bccff040ced53513625af95d05e0c8c27a9a`; runs `33399095190`, `33399095198`, `33399095224` PASS.


## REQ-49-042C3 — Restore Add Product/Crawl legacy workflow and production-grade AI Provider diagnostics
Status: `IMPLEMENTED / GITHUB CI PASS / OWNER LOCAL FOREGROUND QA NEXT`.

Acceptance now implemented:
- visible Add Product/Crawl route with Automatic, Search/Listing, Category URL, Site Crawl and Direct Product modes;
- Classic repeated-Search continuation preserved alongside Hybrid structured-first acquisition;
- Product/image limits, source/query/start URL, retry/reset/progress and rich Product receive;
- live model list including free models, internal Persian suitability label, structured capability hint and Provider price metadata;
- filters for recommended, all, free, Persian and Structured/JSON models;
- real Persian structured Product probe keeps the exact selected Provider/Model;
- stage/all-content AI execution shows estimated cost before approval;
- AI/Crawl failures surface diagnostic dialogs with copyable details;
- no hidden model scan inside simple connection test;
- one shared Single Active AI authority remains intact.

Evidence:
- source checkpoint `ba3d1358d91aa78719f618630c290abf97ee8427`;
- Qt/Crawl/AI run `33394215803` PASS;
- Single Active AI run `33394215742` PASS;
- Production/Host/Django migration untouched.


## REQ-49-080 — Preserve the old Search-Link crawler and expose a stronger acquisition engine in Qt
Status: **IMPLEMENTED + WINDOWS_CI_TESTED / OWNER_LOCAL_FOREGROUND_QA_NEXT**

Requested:
- keep the mature old workflow where the operator gives a main Search/Listing link and later runs continue farther from that same link;
- do not lose the old browser crawler while modernizing the application;
- add a stronger/faster method when available;
- move crawling/scraping/data receive into the new Qt application with visible controls;
- apply useful techniques from the supplied scraping/GUI/FastAPI references without breaking the proven database/business contracts.

Delivered:
- `Classic` strategy preserves Search-Link + browser continuation and permanent terminal-identity skip;
- `Hybrid` strategy prefers robots-aware pooled HTTP/Sitemap + incremental freshness/unseen discovery and only falls back to Playwright when structured/static acquisition is insufficient;
- single Product direct receive and batch Listing receive;
- rich Product facts: source title/description, author, license, category/tags/specs/snapshot and bounded selected images;
- Product count + image count controls;
- start/progress/safe-stop/reset-failed/recent-run UI;
- Qt worker execution rather than blocking the event loop;
- the same Catalog SQLite, crawl ledger, 3I.43–45 transport/intelligence and source-specific fallbacks remain authoritative.

Code checkpoint: `3f7038b52723aa2b70cd12d4c1a617c50d0ad4d8`.

The first owner Local gate reached the Playwright smoke only after repo/backup/dependency guards passed; its failure was ERR-49-081 PowerShell probe quoting, not a crawler failure. A repository-owned corrected Local gate is now available.

Safety:
public/respectful acquisition only; robots and Retry-After remain enforced; no CAPTCHA/auth bypass, proxy evasion or live-site stress benchmark; Production/Host/Django migrations untouched.


## REQ-49-079 — Restore mature Catalog Center capabilities in the Qt application
Status: **IMPLEMENTED + WINDOWS_CI_TESTED / OWNER_LOCAL_QA_NEXT**

Requested:
- Filament add/edit;
- Product descriptions and sorting;
- image size/dimensions/SEO metadata;
- Persian + source/English titles;
- site category dropdown;
- red/pending/green stage readiness;
- Profile builder for multiple production weights/times/support × many Filaments/colors/prices per size;
- full Content/SEO;
- Source/License/Specs;
- homepage slider controls;
- mature Product AI source-mode actions;
- AI Provider/Model/key/test/default settings including AvalAI and Gemini;
- Site connection settings.

Result:
all requested surfaces above are implemented on the Qt shared-kernel path and pass Windows CI `33369749205` at code checkpoint `c3b0105eaa6c6141eb6d6d8463a96d547101564c`. Dedicated Single Active AI `33369749123` also passes.

Still separate:
Phase42C live Scan/Crawl/Acquisition controls and Phase42E packaging/default-launcher cutover remain open. Production is untouched.


## REQ-49-079 — Full Legacy capability parity on Qt6 through an object-oriented application kernel
Status: `IN_PROGRESS / 42B1 GITHUB+WINDOWS CI PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT TOUCHED`

Owner acceptance/feedback:
- Qt6 shell, menus and overall presentation direction are accepted;
- the text-only Qt Product list and read-only Wizard are not sufficient;
- all mature Catalog Center capabilities must be migrated rather than discarded;
- Products must again have folder/card-style image presentation and direct edit flow;
- every major subsystem must expose one reusable object-oriented Core/Engine owned by the application kernel;
- AI in particular must have one shared engine object used by every caller, not separate per-screen AI implementations;
- current mature Stage workflows, locks, history, image pipeline, Filament/pricing/Profile logic, crawl/discovery and publish contracts must be wrapped/reused rather than rewritten in parallel.

42B1 implementation:
- ApplicationKernel/CoreRegistry;
- Product/Image/Filament/Acquisition/Publish/AI cores;
- Qt Product gallery + local image preview;
- real Stage-1 title/category edit + explicit unlock;
- Stage-3 local image gallery;
- Qt CI `33319343447` PASS;
- Single Active AI `33319343464` PASS.

Next acceptance target is 42B2 Stage-2 full operator parity.


## REQ-49-078 — Apply new GUI/FastAPI/web-scraping books to the application and acquisition stack
Status: `IMPLEMENTED THROUGH 3I.45 + QT42C / WINDOWS CI TESTED / OWNER LOCAL FOREGROUND QA NEXT`

Requested:
- deeply review the newly supplied books;
- update development methods and commands using current best practices;
- improve speed, stability, quality and maintainability;
- improve web discovery/crawling/data extraction;
- update database structures where useful;
- keep a strong, comprehensive, wizard-driven desktop application.

Applied now:
- knowledge index for GUI/FastAPI/scraping;
- current official-doc verification for version-sensitive techniques;
- Phase49.3I.45 incremental Sitemap intelligence;
- Catalog discovery metadata ledger;
- freshness/unseen prioritization;
- preserved public/respectful acquisition policy;
- Qt42C Classic old Search-Link continuation + stronger Hybrid structured-first acquisition;
- rich Product receive, visible progress/safe stop, bounded image count and persistent continuation/queue state.

Not interpreted as permission to:
- replace Django Production with FastAPI without an explicit architecture gate;
- bypass CAPTCHA/authentication/access controls;
- use proxy evasion;
- stress-test third-party websites;
- deploy before Local acceptance.


## REQ-49-077 — Modern comprehensive wizard desktop application from purchased Qt references
Status: `IN_PROGRESS / FOUNDATION WINDOWS CI TESTED / OWNER LOCAL PREVIEW NEXT`

Requested:
- study and apply the two purchased PyQt5 GUI references;
- upgrade the desktop application architecture, interaction patterns and visual quality;
- provide strong wizard flows, complete menus, explicit routes and predictable actions;
- add reusable patterns that reduce ad-hoc UI errors and blocking behavior;
- keep the application comprehensive rather than hiding capability behind ambiguous controls.

Implementation direction:
- source concepts are applied through current PySide6/Qt6;
- legacy mature business logic is reused rather than rewritten;
- parallel Qt preview first, cutover only after side-by-side acceptance;
- full migration is split into 42A–42E and cannot be called complete at foundation stage.

References summarized in `docs/references/PYTHON_QT_GUI_REFERENCE_NOTES.md`.


## REQ-49-076 — Central reusable Filament library and clear multi-select
Status: `IMPLEMENTED / GITHUB_UPDATED / OWNER LOCAL TEST NEXT / PRODUCTION NOT DEPLOYED`

Requested behavior:
- maintain roughly any number of Filaments globally rather than redefining them per Product;
- group by Filament/material type (PLA, PETG, etc.);
- select one or many with a visible checklist, with a separate box showing Product selections;
- no Ctrl/Shift dependency;
- remember/reuse manufacturer, brand and material values;
- allow normal Filament management from the main application;
- sync newly created/updated Filaments to Site with roll weight, stock and operational rates;
- keep Product-specific fixed pricing Product-owned;
- when a Product is duplicated by a path that copies its persisted Product fields, its saved Filament selection can rehydrate from the same Product-owned selection JSON.

Implementation: Phase49.3I.41. No new migration; local/Site verification is required before Production.


## REQ-49-075 — last Stage-2 fixes before website
Status: `IMPLEMENTED ON GITHUB / QUICK LOCAL RETEST NEXT / PRODUCTION NOT DEPLOYED`

Requested acceptance:
- a newly saved Filament immediately appears in the list and is selected;
- selected Filament edit uses the final live-rate editor;
- price preview uses the currently authoritative Filament facts and does not show zeros when rates are present;
- a newly selected Filament can be previewed before explicit Product registration, but attachment to Product remains an explicit action;
- range and formula modes must not be conflated;
- once these pass, move directly to website receive/sync.


## REQ-49-074 — restore final pricing result and use Filament terminology
Status: `IMPLEMENTED ON GITHUB / LOCAL RETEST NEXT / PRODUCTION NOT DEPLOYED`

Acceptance:
- rate editor visibly shows the final calculated roll basis and rate per gram;
- Stage-2 pricing visibly shows the final amount/range without requiring the popup preview;
- formula result is based only on registered Filament facts + product weight/time/support + configured supervision/preheat/assembly;
- no hidden/default FX is invented;
- operator buttons/dialogs say `Filament`, not `Offer`;
- internal compatibility identifiers may remain `offer_*` and must not trigger a schema/API rename;
- after Local acceptance, website receiver must consume the same manufacturer/Filament/color/Profile/pricing facts.


Last Updated: 2026-08-29

Older detailed request history remains available in Git history. This file keeps active acceptance contracts.

## ERR-49-072 verification rule

The Stage-2 confirmation regression must use the same additive Catalog schemas as the real ProductWorkspace. Test-only schema setup may not be mistaken for a Product/runtime defect. After the fixture fix, rerun the full ERR-49-071 acceptance path before judging the visible Stage workflow.

## ERR-49-073 Images acceptance request

- Stage 3 must not require the operator to manually fight Metadata refresh after later Content/Source stages change.
- `ثبت و تأیید مرحله` on Images must finalize current SEO/Metadata and then confirm the Stage.
- If Images is already confirmed, pressing the same button may refresh deterministic Metadata without unlocking operator-approved selection.
- A confirmed image Stage remains protected from arbitrary AI/operator edits; manual Metadata overrides require `اصلاح مرحله`.
- Stale Metadata warnings must clear after successful deterministic rebuild.
- Do not change Stage-2 pricing/Profile/Offer behavior as part of this fix.

## ERR-49-071 owner acceptance request
Executable checkpoint: `6085ea70d1075c5a1abaca4b4b2efdebe1254829`. Stage-2 confirmation must persist the visible Product type/dimensions before it is marked confirmed.


- Restore the older Stage layout; do not place Product type/dimensions/use-case in Stage 1.
- Stage 1 must accept a deliberately selected `سایر محصولات` category.
- Every Stage must have one obvious permanent bottom `✅ ثبت و تأیید مرحله` action.
- Filled fields alone do not earn the final green check; `✅` appears after successful explicit confirmation.
- Clicking confirmation must persist the current UI first, validate it, confirm/lock the Stage, refresh the rail, then advance.
- Pending confirmation must not be counted as missing Product data.
- The legacy Next button must not be the authority because late wrappers repaint it.
- Title-only AI must obey the same global one-Product-AI-at-a-time/OpenRouter-only runtime guard.
- Preserve Stage-2 Offer/Profile/pricing, crawler/acquisition and current Product data.

## Preserved project contracts
- GitHub-first delivery; live branch/HEAD verification before Host operations.
- Product/SEO/media/Bridge security/idempotency and Product-owned public media remain intact.
- imported Catalog working-media is not a public Production namespace.
- healthy StoreOrder/Payment/Invoice/inventory/coupon/VAT behavior is extended rather than duplicated.
- no guessed carrier/gateway endpoint or tariff.


## REQ-50-028 — Professional Stage-2 Offer flow, Profile snapshot and truthful AI completion
Status: `IMPLEMENTED 49.3I.40 + STORE 0040 / BASELINE CI+PORTABLE PASS / ERR-49-069 STAGE-CONTRACT + OPENROUTER-ONLY HOTFIX GITHUB / OWNER LOCAL RETEST NEXT / PRODUCTION NOT DEPLOYED`

Acceptance:
- Stage 2 order is manufacturer/company → filament/material → color → register Offer → professional pricing → production rows → Profile identity/dimensions,
- registering Offers in a new manufacturer/material filter preserves selected Offers from other filters,
- global Offer editor owns stock, roll weight, purchase/sale/USD+explicit FX, hourly print/supervision, preheat and filament image/HEX,
- Product fixed price is separate and can differ per exact manufacturer/material/color Offer without changing the global filament rate,
- formula pricing consumes exact Offer facts and production weight/time/support; preheat is optional and costs zero when absent,
- same material/color from Bambu Lab, eSUN or another manufacturer stays distinct through Desktop sync and Storefront selection,
- Storefront selection is manufacturer → material → color, with exact price and orderability after the selection is known,
- insufficient Offer/color stock prevents orderability,
- colors show filament image when available, otherwise explicit/fallback swatch,
- production weight/print-time/support rows are not duplicated in the bottom Profile identity form,
- Profile registration uses operator name + size + actual dimensions and creates an immutable snapshot; later Profiles may reuse the working form without mutating previous registered Profiles,
- duplicate Profile identity is rejected,
- Product screenshot selected for Site is the top viewport reference rather than full-page,
- full Link completion repairs AI-owned readiness defects stage-by-stage and reports request/response/apply/before/fixed/remaining state,
- 100% is forbidden while `ai_fixable_count > 0`,
- data-ready-but-not-finalized is not displayed as a data defect,
- each stage remains editable by default, can be finalized by the operator and must be explicitly returned to edit before later AI changes,
- AI sources are exactly Link / Saved-Crawled Data / Screenshot; Repair is an operation on the same engine,
- mature Crawl/Direct Link/parser/image/file receive behavior must remain unchanged,
- Store migration `0040_phase50_filament_offer_operations` reaches Production only after Local backup/migration/regression, owner visual acceptance and fresh Production MySQL backup/rollback verification.

Verification:
- Catalog targeted `33247729316` PASS,
- Single Active AI `33247815007` PASS,
- Windows Portable `33247815027` PASS on `55139b909f214f33994d76bc1e6fdfd028b5d6c7`,
- Store/0040 `33246843145` PASS,
- Production untouched.
- Owner foreground QA on 2026-08-29 exposed `ERR-49-064`: the obsolete 3I.35 Listbox action row mixed `pack` into the modern grid-managed material/color card and aborted ProductWorkspace before 3I.39/3I.40 visible UI construction.
- Follow-up owner QA exposed `ERR-49-065`: AI-persisted SEO fields must immediately reconcile the visible readiness/help widgets; fixed by DB rehydration + final post-AI readiness repaint without auto-finalizing operator stages.
- Owner retest exposed `ERR-49-066`: each displayed defect must have exactly one Stage owner, AI-fixable defects must map to an actual write path, Stage UI must turn complete from persisted `data_ready` without requiring finalization, and all mature full-AI actions must route through the same final checker/repair engine.
- ERR-49-067 fixture correction remains valid, but its interim all-Latin SEO prohibition was superseded by real Product 63 evidence: exact source identity tokens may remain beside Persian SEO text; unrelated Latin still fails.
- ERR-49-068 restores the owner-requested visible Windows flow: the current Stage must always expose `✅ تأیید و مرحله بعد` plus AI fill/edit controls; manual values are persisted before readiness is checked, and success advances to the next Stage.
- A visible legacy AI button must execute the same final 3I.39 engine as the new controls; class-method rebinding alone is not sufficient for Tk Buttons created earlier.
- Provider fallback must never reuse a key or model that belongs to another Provider.
- ERR-49-069 owner contract: Product AI is OpenRouter-only. The saved OpenRouter model is primary; the only optional fallback is `openrouter/free` with the same OpenRouter key. AvalAI/Google/OpenAI must not be invoked by Product AI.
- Stage-specific AI completion is judged only against the selected Stage; unrelated defects in other Stages must not trigger retries or false incomplete status.
- Only one Product AI job may run in the process at a time; another Product Workspace must be blocked until the active job finishes/cancels.
- Stage 1 must visibly expose Product type, dimensions and use-case/class. Stage 5 must visibly expose source/designer, commercial license, technical summary and technical features. Stage confirm must persist every owned visible field before readiness/finalization.
- A late/deferred legacy Wizard callback must never restore the old read-before-save Next action after final composition.
- Hotfix source `aa37dcf916dfab71409738f7087a171daffe4a0a` + regression `9a3ebd43b22a50ac1447b90cae159dcffb1ed451`; owner Local retest remains required.

## REQ-50-001 — Complete business finance/accounting system
Status: `REQUESTED / PHASE50 ACTIVE`
Full GL/subledger, Treasury, Purchasing/Sales accounting, customer/supplier statements and management reports integrated with Store/service/inventory/production/payments.

## REQ-50-002 — Complete and reorganize Django Admin
Status: `PRODUCTION VERIFIED / VISUAL QA CONTINUES`
Professional Velzon operator console with business navigation, full-width lists, on-demand filters, Persian controls, stable footer, no document jump and approximately 290px readable right sidebar.

## REQ-50-003 — Preserve healthy commerce while adding accounting
Status: `ACTIVE CONSTRAINT`
StoreOrder, StorePayment, invoices, inventory, coupon/VAT, Product/Profile/Variant history and payment security remain compatible.

## REQ-50-004 — Dynamic delivery price
Status: `50.A.2B–2D GITHUB CI TESTED / PRODUCTION MIGRATION CHAIN NEXT AFTER LOCAL QA`
Shipping calculation must use the chosen profile/product effective shipping weight, packaging weight/dimensions and destination. Current ShippingMethod/rate rules remain the explicit fallback. Post/Tipax/Mahex adapters are allowed only after verified official current contracts/credentials.

## REQ-50-005 — Coupon + VAT checkout
Status: `PRESERVED / INCLUDED IN 50.A.2B REGRESSION BOUNDARY`
Do not duplicate current Coupon/VAT logic; shipping snapshot finalization must preserve discount, packaging, tax and payment totals.

## REQ-50-006 — Phishing-resistant comprehensive payment
Status: `50.A.3 IN_PROGRESS / MATURE QUOTE ENGINE VERIFIED / CURRENT-API COMPATIBILITY LOCAL_TESTED`
Server-owned amount, DB locking, callback identity, exact Authority, server-to-server verification and idempotency are already present in the mature quote-payment engine; never collect/store card/PIN/CVV. Current ZarinPal endpoint/Verify compatibility is Local-tested; StorePayment wiring and merchant activation remain separate gates.

## REQ-50-008 — Variant 2.0 size/build/packaging parity
Status: `PRODUCTION VERIFIED FOUNDATION`
`store.0034` and `store.0035` are applied; customer selector uses canonical ProductVariant state.

## REQ-50-009 — Torob marketplace integration
Status: `REQUESTED / 50.A.4 PLANNED`
Official Product API v3 with stable Product/Profile grouping, price/availability and image-quality rules.

## REQ-50-010 — ZarinPal Store checkout activation
Status: `50.A.3 IN_PROGRESS / PROVIDER COMPATIBILITY LOCAL_TESTED / STORE WIRING NEXT`
Current ZarinPal v4 provider defaults and Verify payload are Local-tested against the mature secure quote-payment engine. Connect canonical StorePayment checkout to that same architecture before any merchant activation; do not create a parallel payment authority.

## REQ-50-014 — Windows Product image pixel dimensions
Status: `SOURCE IMPLEMENTED / CI TESTED / INCLUDED IN NEXT OWNER-ACCEPTED EXE`
Each Product image card shows original width × height px.

## REQ-50-018 — Unified Product Admin workspace
Status: `PRODUCTION VERIFIED / VISUAL QA CONTINUES`
Product edit business order remains: `اطلاعات کالا | تصاویر | فروش و موجودی | پروفایل‌ها و سایز/وزن | قیمت‌گذاری | ارسال و بسته‌بندی | SEO | اسلایدر صفحه اول | منبع و لایسنس | همگام‌سازی ویندوز`.

## REQ-50-019 — Modern Velzon Admin interaction surface
Status: `PRODUCTION VERIFIED / VISUAL QA CONTINUES`
Full-width list, on-demand filter drawer, modern table/search/actions, section navigation, stable footer and internal-only sidebar scrolling.

## REQ-50-020 — Product likes, saved/favorites, comments and verified-buyer reviews
Status: `REQUESTED / NEXT SCHEMA-BUSINESS PACKAGE AFTER 50.A.2B`
Preserve ProductLike/ProductComment/ProductReview. Add Favorite/Save if absent, engagement counters/Admin visibility and qualifying purchased/paid Product checks for buyer feedback. Dedicated migration/tests/backup required.

## REQ-50-021 — Customer Product profile/size/weight/color/price selector
Status: `PRODUCTION VERIFIED`
Customer Product view obeys list/size/weight/build/size→build/build→size selection, exposes available profile dimensions and price/facts, keeps canonical ProductVariant ID and native fallback, and reuses `/store/api/variant-commerce-options/`.

## REQ-50-022 — Immutable selected-profile checkout and shipping snapshot
Status: `IMPLEMENTED / GITHUB CI TESTED / PRODUCTION MIGRATION NEXT`
Acceptance:
- finalized order item freezes profile name/key/label and customer-visible selection mode/value,
- freezes size/build/material/color/quality, final weight, packaging weight, effective shipping weight, print time and package dimensions,
- Cart/checkout effective weight includes packaging when there is no explicit shipping-weight override,
- order freezes `insured_value` and normalized `shipping_quote_snapshot`,
- current ShippingMethod/rate rules remain fallback; no external carrier claim,
- combined parcel geometry is not invented,
- coupon/VAT/inventory/payment/notification behavior remains authoritative,
- snapshot remains immutable after later ProductVariant edits,
- migration `store.0036_phase50_checkout_snapshot` requires exact Production MySQL verification, fresh backup and rollback.

CI: `Phase50 Variant2 Gallery CI` run `32966720475` PASS on `fba0631e60bce1f6e3f622317b70c2f7f35d978f`.

## REQ-50-023 — Fast Windows AI + exact-link grounding + selected-product batch AI
Status: `PRESERVED IN 8.9.0 / WINDOWS PACKAGED CI PASS / OWNER LOCAL QA PENDING`
Acceptance:
- Product edit/AI must not rebuild global Products gallery on every save/request,
- large catalog remains usable and older products are never discarded,
- exact saved mother AI Provider/Model/key controls Product AI including OpenRouter/AvalAI; no hidden fallback/model scan,
- normal Product AI factual payload contains only Product title + one bounded text body,
- exact source page facts are extracted first and organized under headings; unsupported facts are not invented,
- raw HTML/auth/cookies/secrets and unrelated price/stock/workflow state are excluded,
- main AI action completes Persian title/content/SEO and selected image alt/title/caption/metadata/finalization,
- selected Products support the same exact-link operation in batch,
- batch errors are isolated per Product, stop is operator-controlled and global Products refresh occurs once at batch end,
- Product price/stock/availability/business selections remain untouched by editorial AI,
- Windows regression + launcher + one-file build + frozen browser smoke must pass before Local owner QA.

Implementation: Phase49.3I.29 + 49.3I.31; version `8.8.2`, build `2026.08.26.2`. Targeted CI run `32996526852` PASS; Windows packaged run `32997106056` PASS on runtime snapshot `5208aa4dd3b070e9a7c7c6d6dde9b60569879631`.

## REQ-50-024 — Product source link must never disappear from unrelated actions
Status: `IMPLEMENTED 49.3I.32 / TARGETED + PACKAGED WINDOWS CI PASS / OWNER QA PENDING`
Acceptance:
- Save, silent Save, AI, close, refetch, image actions and publish-related flows must not erase an already persisted canonical Product source URL merely because mirrored URL controls are temporarily blank,
- intentional non-empty URL edits remain supported,
- a missing URL is never guessed,
- a Product already damaged by the old bug should recover the exact previous HTTP/HTTPS URL from local Product history, or matching discovery identity when history is unavailable,
- recovery does not use the network and updates canonical `source_url`, `normalized_url` and fingerprint consistently,
- recovery is recorded in Product history/diagnostics,
- no Product price/stock/material/color/business state or AI provider/model is changed by this guard.

Verification: targeted run `32996526852` PASS; packaged Windows run `32997106056` PASS. Remaining acceptance is Local owner QA of a healthy linked Product, the already affected Product, OpenRouter/AvalAI live exact-link AI and selected-Product batch behavior.

## REQ-50-025 — Product Profile Matrix shared by Windows and Storefront
Status: `IMPLEMENTED 49.3I.34 + 50.A.2D / GITHUB CI TESTED / OWNER LOCAL QA NEXT / PRODUCTION NOT DEPLOYED`

Acceptance:
- Product Step 2 can add a Profile or clone the selected Profile so Profile 2 initially equals Profile 1 and then diverges safely,
- each Profile owns its own size, final/material weight, price, print time, actual part dimensions, build mode, material, color, quality, package weight/dimensions, stock/default/sort state,
- examples such as size 20 with 100/150/200 g and size 30 with 150/200/300 g are represented as separate real orderable ProductVariants,
- customer selection supports size→weight and deeper configured hierarchies,
- selecting a size shows only valid downstream options for that size,
- later selections never hide valid upstream choices,
- price badges for a weight/profile are scoped to the selected upstream size/choices,
- selected Profile is the single Product detail price/facts authority,
- the same Desktop profile payload is persisted and transported through the existing Catalog batch boundary; no separate hidden Store dataset,
- manual server-side Variants outside the Desktop-managed namespace are preserved,
- selected Profile part dimensions and existing shipping/package facts are frozen on successful checkout,
- Profile content and Storefront presentation remain safe when JS/API progressive enhancement is unavailable,
- Production migration chain is verified and backed up before any schema write.

Verification:
- Windows Catalog Center 8.9.0 build `2026.08.27.2`, workflow `33051114515` PASS on `b3280dd67cd7772f337f6792036ea92d3f252747`; artifact ID `9637671099`, EXE SHA256 `32aed719e6d374447fc4b05f09a30fe12f0ce4dc05e570382f2e74036044900c`,
- Web runtime snapshot `7d0a2a1125e8f38771ba325427d1efa8b8d07da6`, Profile Matrix CI `33051311828` PASS, 15 Store/Profile/Checkout tests PASS and `PHASE50_PROFILE_SELECTOR_HIERARCHY=PASS`,
- pending Production migrations: `0036 → 0037 → 0038` subject to fresh read-only MySQL verify + backup.


## REQ-50-026 — Operator-ledger Profiles, resilient AI and brand-aware filament offers
Status: `IMPLEMENTED 49.3I.35 + 50.A.2E / SUPERSEDED BY CATALOG 8.9.6 QA TRACK / PRODUCTION NOT DEPLOYED`

Acceptance:
- Product Step 2 uses the upper controls as a working form and registered Profiles as the transport/publish authority,
- registering a Profile snapshots current fields; new Profile can load the latest snapshot without mutating older Profiles,
- Profile production supports multiple `weight | print time | support weight` rows,
- quick/basic Product page no longer owns fixed price/weight/Profile authority,
- material/color has select-all, clear and local-register actions without global Product-list refresh,
- material offers preserve material + brand + manufacturer + color + roll weight + stock rolls + purchase/sale/USD/FX facts,
- customer sale-rate uses the highest positive explicit sale basis; FX is never guessed,
- same material/color from different brands remains distinguishable and orderable,
- synchronized roll stock participates in color availability when no real spool rows exist,
- AI dialog exposes preflight/progress/send/wait/reply/apply state, retries up to the configured attempt count and uses only explicit configured fallbacks,
- bulk AI isolates Product errors and does not refresh the complete Products list per item,
- editorial AI does not own material/color,
- manual SEO review can accept complete actual Persian SEO without another AI call,
- manual source review cannot bypass invalid commercial-license policy,
- support weight + filament brand/manufacturer freeze into historical StoreOrderItem snapshots,
- migration `0039` reaches Production only after exact MySQL verification, fresh backup and rollback.

Verification:
- Store run `33059883188` PASS through migration `0039` and 16 regressions,
- Smart/Profile 31–35 run `33060613937` PASS,
- Single-AI run `33060613914` PASS,
- Windows portable run `33060047878` PASS,
- Catalog Center `8.9.1` / build `2026.08.27.3`,
- artifact ID `9641338334`,
- EXE SHA256 `3099b26713a460fbd55c1204ef750b37dbef542269b5520fd393526cd8c9476c`,
- Owner Local automated gate: PASS at `2cdb356fca6d6c4c4bcd0edf203acf8e24bab2b9`; Local SQLite `0039` applied; 16 Store regressions + 107 Catalog tests PASS; Production untouched,
- 8.9.1 foreground launch then exposed `ERR-49-059` before visible UI; 8.9.2 fixes the pack/grid parent collision,
- 8.9.2 startup hotfix run `33066468014` PASS, but owner Product Workspace QA then exposed `ERR-49-060`,
- 8.9.3 fixes `ERR-49-060` by using the installed namespaced Profile lookup,
- 8.9.3 run `33067618679` PASS; artifact `9644438652`; EXE SHA256 `fd525fad977f592dc62e68fc3a4310bba98c7ed9689c5101cbdc35589fef7bed`.

## REQ-50-027 — Permanent crawl ledger, reject/purge tombstones and one stage-scoped AI engine
Status: `IMPLEMENTED 49.3I.38 / GITHUB CI + WINDOWS PORTABLE PASS / OWNER LOCAL VISUAL QA NEXT / PRODUCTION NOT DEPLOYED`

Acceptance:
- healthy existing Browser/Crawl/Parser/image/file receive behavior is preserved and extended rather than replaced,
- every crawled/received Product identity remains durably known in the Catalog ledger,
- previously collected/rejected/blocked Product links do not become new receive work when the same source/listing is scanned again,
- a repeated Listing can continue deeper after already-known results so requesting another 100 Products can skip the first known 100 and queue the next 100 new identities,
- operator can permanently reject an unwanted Product, remove its local acquired files/images and still retain source URL/external ID as a rejection tombstone,
- physical purge is restricted to the Product directory below the canonical Catalog `collected/` root and fails closed outside that boundary,
- rejected/blocked Direct Link identities are checked before Browser/HTTP/image/file acquisition,
- explicit operator restore is the only action that permits a rejected identity to be received again,
- Product AI has one configured engine/Provider/Model/retry/fallback authority,
- Product AI source mode remains exactly Link / Saved-Crawled Data / Screenshot,
- selected-Product Bulk Content/SEO calls the same mother orchestrator rather than a separate AI implementation,
- a single Product can explicitly clean/complete only one selected unlocked Stage,
- Stage 4 cleanup may replace/clean Content/SEO but cannot change Profile, price, material, Source, images, slider or other out-of-scope stages,
- finalized/locked stages are immutable until the operator presses `اصلاح`,
- Commerce and Publish remain operator-owned,
- image-only AI work does not call a Provider when image SEO/metadata is already complete,
- no full Products Explorer rebuild occurs per Product during bulk AI.

Verification:
- runtime `c904193a7f0af9aad80365834ec3f0b856e77dc9`,
- Catalog Center `8.9.6` / build `2026.08.27.8`,
- Phase49.3I.31–38 run `33077213590` PASS with 84 tests,
- Single Active AI run `33077239617` PASS,
- Windows Portable run `33077239660` PASS,
- artifact `3DPrintHub-CatalogCenter-v8.9.6`, ID `9648474905`,
- EXE SHA256 `6490e4815f1e6e0d75f09c112bb6990041578616f170954f62fae037b98bd507`,
- source URL preservation, portable self-verify and browser smoke PASS,
- Production touched = NO.

Rollback:
- `backup/pre-phase49-3i38-crawl-ledger-stage-ai-20260827` → `d1ed566a82d3818aa45a5c720df3e7efcb0044f3`.

Current remaining acceptance:
- owner Local visual/functional QA on the final GitHub docs head,
- then and only then Host read-only audit/backups/deploy/Production verification.

## Change rule
New work extends/wraps mature behavior and must pass CI/Local gate before Production. No schema migration reaches Production without exact MySQL verification, migration plan, successful backup and rollback target. Production uses explicit live branch fetch to `FETCH_HEAD` because host remote-tracking refspec is stale/tag-only. Avoid `/dev/fd` process substitution on this cPanel host.

- ERR-49-070 completes the Stage-5 request end-to-end: clean Catalog DBs must contain `technical_summary_fa`, Stage 5 must visibly show source/designer + Persian license + technical summary + technical-features JSON, and the exact visible license selector must persist through stage confirmation.

## REQ-50-033 - Slicebox-inspired managed Hero
Date: 2026-09-14
Status: `LOCAL_TESTED / GITHUB+PRODUCTION NEXT`.

Acceptance: retain the managed Django Hero/SEO/Admin contract while adding a Slicebox-inspired seven-slice 3D transition on capable desktop browsers. Mobile, reduced-motion and unsupported CSS 3D must retain the mature fallback. No jQuery/runtime dependency, pricing/cart authority, migration or Product data mutation. Local focused regression and real Playwright QA PASS.

## 2026-09-14 - Owner request: simplify manual Product publication
Owner requested that every Local Filament have nonzero pricing and exactly one 1 kg roll of stock, and that all Filaments be preselected for every Product so manual preparation focuses mainly on dimensions. This is a Local Catalog policy only; ChatGPT must not auto-publish Products.

Implemented and verified: 66 active inventory rows, 64 unique selectable Filament identities, 635/635 Products with canonical Profiles, all Profiles preselected, and prior uploaded Products marked for same-identity update. Windows Catalog Center was relaunched for owner-driven publication.

## REQ-50-011 - Final Windows publisher resend/update + empty Store handoff
Requested behavior: clear old/test Store products; keep the professional standalone 3D Slicebox Hero; allow previously sent Windows Catalog products to be explicitly resent; update existing Site products in place when present; recreate safely when the old Site product was deleted; carry changed Profile, Filament, print time and other current product fields on republish.
Status 2026-09-17: source behavior locally accepted; Production reset preflight/backup ready; destructive reset not yet executed due automation safety guard.
