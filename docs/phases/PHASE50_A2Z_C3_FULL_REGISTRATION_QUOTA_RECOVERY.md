# Phase50.A.2Z-C3 — Full Registration + Host Quota Recovery

Status: **FULL REGISTRATION + QUOTA ACCEPTED / HERO REVISION + SOCIAL MOBILE PREFLIGHT LOCAL_TESTED / GITHUB NEXT**
Date: 2026-09-22
Baseline: `7d6f738a05abf7de8b53905dcf755563ab9d09de`
Rollback refs: C3 baseline `backup/pre-a2z-confirm-all-quota-20260922`; Hero/Social hardening `backup/pre-a2z-c4-hero-social-preflight-20260922 @ cbec63e9b007a20b7e3070eece74b0328afc212a`
Worktree: `D:\projects\3DPrintHub-a2y-converge`
Branch: `wip/phase50-a2z-image-social-authority-20260921`

## Owner request

1. Add **«✅ ثبت کامل»** next to **«✏ ویرایش کامل»** on the Product Wizard.
2. One click must save the current editable Stage and approve all seven currently complete Stages, eliminating seven separate confirmation clicks after edits such as Profile/price work.
3. Existing Stage validation must remain fail-closed. An incomplete Stage must never become green merely because the bulk confirmation button was pressed.
4. Full Registration is approval only: it must not mark ready, publish, start FTP/Bridge, change Slider membership, or send Social content.
5. Diagnose the real Site-send failure without blindly retrying the 14/15 queued Products.

## C3 implementation

- Product identity row now owns **«✅ ثبت کامل»** beside Full Edit.
- Current editable Stage is saved first so the visible operator edit is persisted.
- `StageCore.finalize_all_ready(product_id)` walks the canonical seven `STAGE_ORDER` entries and reuses the mature `finalize()` validator with `manual_approval=True`.
- Already-finalized stages are preserved.
- Incomplete stages remain blocked and are summarized to the operator.
- Publish Stage may be approved only because this is an explicit owner action, but no Site publication API is called.
- No `mark_ready_many`, `publish_many`, FTP, Bridge or Instagram operation is part of this button.

## Verification

- Focused Full Registration / Full Edit: **3/3 PASS**.
- Related Stage Finalization + Product Wizard + Site Publish + Unified Desktop + Slider regression: **82/82 PASS**.
- Changed Python compile: **3 files PASS**.
- `git diff --check`: PASS.
- `RUN_QT.ps1 -VerifyOnly`: PASS.
- Server/migration/template/static delta: **0**.
- Initial focused run exposed a missing `stage_locks` import before any real mutation; the import was added and the changed-condition rerun passed 3/3.

## Publish quota incident

Real failed batch:
- batch: `desktop_catalog_v85_20260922_171201`
- batch UUID: `32a25891-282c-498a-bed1-4498b4303059`
- Product: **#536 only**
- local package: 7 files
- receipt chain: `desktop_batch_ready -> desktop_publish_started -> desktop_publish_failed`
- no `desktop_ftp_uploaded`
- no Bridge import
- failure: `550 Can't create directory: Disk quota exceeded`

The same quota class already failed Product #588 earlier on 2026-09-22. Current local queue inventory is 15 Products, but the #536 attempt contained only #536; the queue must not be bulk-retried as a recovery action.

## Host-management gate

- Historical pre-recovery evidence: project reverse tunnel `127.0.0.1:22024` was absent during the quota incident; it is superseded by the Production recovery evidence below.
- Windows `sshd` is Running/Automatic and listens on port 22.
- OpenSSH shows an established connection from Host IP `89.39.208.237`, but current log identity for that connection is **RetoucherTunnel**, not **PrintHubTunnel**.
- Last observed accepted **PrintHubTunnel** event is 2026-09-20.
- Project rules prohibit using another project's tunnel for Host cleanup.
- No FTP/cPanel/manual Host cleanup has been performed.
- ERR-49-213 already proves shared-account quota can be exhausted even when filesystem capacity itself is healthy.
- Whether current quota also prevented the PrintHub watchdog from reconnecting is not yet verified and must not be asserted until the official tunnel is restored.

## Production quota recovery evidence

- Owner freed Host account space; control-panel usage ~1.44 GB / 1.95 GB.
- Official PrintHubTunnel recovered with expected key fingerprint; Windows 22024 + authenticated bridge PASS.
- Host Git lock absent/worktree clean/write-test PASS.
- Exact FTP publication path passed MKD + 1KB STOR + DELETE + RMD.
- Real Batch `desktop_catalog_v85_20260922_181511` / `fd336bc1-4a04-416f-a6ea-8526dddfb4b2`: 31/31 files uploaded.
- Successful: #140/#151/#210 updated; #536/#588 created and public.
- Failed independently: #152 Hero 2 revision expected 1/current 2; #178 Hero 4 expected 3/current 5.
- #536 public page/image HTTP 200; parity ok; queue now 10.

## Hero + Social hardening checkpoint

- Read-only Site truth: #152 Hero #2 rev2 vs Local rev1; #178 Hero #4 rev5 vs Local rev3. Titles match; conflict is revision authority only.
- Windows publish now refreshes only `server_slider_revision` before Batch; no Product/Slider content or membership is pulled from Site.
- Buffer channel health now includes `hasActiveMemberDevice`; current real state is false.
- Clickable-Story Social send now blocks before any new Feed when mobile reminder delivery is unavailable. Existing Feed remains deduplicated and Story-only retryable.
- #536 Feed is live at `https://www.instagram.com/p/DdmXo5QlMEd/`; Story asset revision `eb33bf7ebb1835a6` is 1080×1920 Gold-Navy/IRANSans pipeline and SHA `d2ca7066f6970c90521a9580908d229c12f695f87dffc3427f0f1d92869e74c6`.
- Focused changed contracts 16/16 and complete Site+Social regression 65/65 PASS; 5 Python compile, diff-check and Qt VerifyOnly PASS; no Server delta.

## Exact next

1. commit/push Hero+Social preflight hardening and verify Local=GitHub exact SHA;
2. exact-SHA Qt relaunch;
3. fresh integrity Catalog backup;
4. bounded Site retry only #152/#178 using automatic revision-only preflight;
5. require terminal ACK + public Product/media parity for both;
6. close C3 and resume A2Z Catalog Data Completion;
7. Social remains blocked only on external Buffer mobile prerequisite; once `hasActiveMemberDevice=True`, fresh backup -> retry #536 Social once -> Feed reused/no createPost -> Story notification only -> operator Link Sticker completion -> truthful receipt.

## Following phase

Resume **Phase50.A.2Z Catalog Data Completion**: Slider completeness/backfill with membership preserved -> #620/#625/#628 operator acceptance -> final Profile/Filament/Image gates -> one controlled same-identity re-publish -> public/browser parity.
