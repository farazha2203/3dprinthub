# Phase50.A.2Z-C3 — Full Registration + Host Quota Recovery

Status: **GITHUB_UPDATED / WINDOWS_RUNTIME_ACCEPTED / HOST QUOTA RECOVERY BLOCKED ON PRINTHUB TUNNEL**
Date: 2026-09-22
Baseline: `7d6f738a05abf7de8b53905dcf755563ab9d09de`
Rollback ref: `backup/pre-a2z-confirm-all-quota-20260922`
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

- Project reverse tunnel `127.0.0.1:22024` is currently absent.
- Windows `sshd` is Running/Automatic and listens on port 22.
- OpenSSH shows an established connection from Host IP `89.39.208.237`, but current log identity for that connection is **RetoucherTunnel**, not **PrintHubTunnel**.
- Last observed accepted **PrintHubTunnel** event is 2026-09-20.
- Project rules prohibit using another project's tunnel for Host cleanup.
- No FTP/cPanel/manual Host cleanup has been performed.
- ERR-49-213 already proves shared-account quota can be exhausted even when filesystem capacity itself is healthy.
- Whether current quota also prevented the PrintHub watchdog from reconnecting is not yet verified and must not be asserted until the official tunnel is restored.

## Exact next

1. runtime-bearing C3 commit `ac094945901cfd612dd6069fdd473a995c8a204a` is Local=GitHub exact;
2. exact-SHA Qt relaunch and widget smoke 4/4 PASS;
3. recover the official PrintHub reverse tunnel only through the documented project path;
4. read-only Host quota inventory through `22024`;
5. remove only verified disposable/incomplete/cache artifacts if required; preserve valid rollback/media;
6. prove account write headroom and FTP pending-directory creation;
7. fresh Catalog backup;
8. retry only the bounded failed Product, not the whole queue;
9. require one complete Batch -> FTP -> Bridge -> terminal ACK chain and public parity.

## Following phase

Resume **Phase50.A.2Z Catalog Data Completion**: Slider completeness/backfill with membership preserved -> #620/#625/#628 operator acceptance -> final Profile/Filament/Image gates -> one controlled same-identity re-publish -> public/browser parity.
