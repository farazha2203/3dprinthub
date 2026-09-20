# Phase50.A.2T — Windows Launcher + Instagram Link Handoff + Republish Closure

Status: LOCAL_TESTED / GITHUB NEXT
Date: 2026-09-20
Base: `03042d0430ee6e688c992c875f12edc969df103d`
Branch: `wip/phase50-a2t-windows-social-republish-20260920`

## Owner request
- Give one exact way to open the Windows Catalog Center.
- Finish Instagram Feed/Story publication rules and explain why the previous Product URL was not clickable.
- Use a visible CTA such as «لینک محصول» where Instagram supports it.
- Guarantee that republishing an existing Product replaces current Desktop-owned Product/Profile/Variant state instead of leaving stale active data.
- Do not repost Product #625 revision 8.

## Verified starting state
- Existing Desktop shortcut still targeted the older primary clone `D:\projects\3DPrintHub @ 21a1ae27...`.
- Current accepted lineage is `03042d04...`; canonical primary clone is intentionally dirty only with unrelated documentation work and is not reset.
- Current Catalog data remains `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`.
- Product #625 mirrors Site Product #39 revision 8, local `needs_update=0`, three current sales Profiles; Site Product #39 has three active Variants and two images.
- Same-ACK duplicate guards for #625 Feed and Story are true.

## Windows launcher
- Repository-owned `catalog_center/RUN_QT.ps1` added to the A2T lineage.
- It uses the existing verified venv, shared Catalog data root, executes `qt_launch.py --verify-only`, and only then launches the Qt app with `pythonw`.
- `RUN_QT.ps1 -VerifyOnly` PASS.
- Desktop .lnk/.cmd are updated only after exact commit/push and retain local rollback copies.

## Instagram policy v5
- Feed remains automatic Buffer/Instagram publication.
- Raw Product URLs are no longer placed in the Feed caption as if clickable.
- Feed CTA now says «لینک محصول» and directs the customer to the Story link or profile link.
- Hashtags are bounded to 5.
- Story artwork CTA now says «لینک محصول».
- Clickable Story mode defaults ON and uses Buffer notification publishing.
- Buffer receives the Product tracking URL plus handoff text for a native Instagram Link Sticker labelled «لینک محصول».
- A notification Story is recorded as `instagram_story_notification_ready`, never falsely as live/published until the operator completes it in Instagram.
- The UI reports how many Story notifications still need mobile completion.
- Fully automatic Story remains an explicit optional mode when clickable Story link is OFF.
- Same-ACK notification/published/submitted receipts all protect against duplicate Story creation.

## Republish contract
No new server rewrite is required: Phase50.A.2M authoritative republish is already in the Production ancestry.
- Existing identity is updated, not duplicated.
- Explicit Desktop `sales_profiles_json` suppresses legacy regeneration.
- Stale active Variants are deactivated; historical rows remain only for FK/order safety.
- Active Variant parity rejects any extra server Variant and rolls back incomplete mutation.
- Windows Product edits mark the Product for republish; unchanged uploaded Products are not resent.

## Local verification
- Windows Catalog republish: 29/29 PASS.
- Server authoritative/unified republish: 14/14 PASS.
- Social policy/provider: 33/33 PASS.
- Qt regressions: 32/32 PASS.
- Settings construction PASS.
- `qt_launch.py --verify-only` PASS.
- `RUN_QT.ps1 -VerifyOnly` PASS.
- Django check + no migration drift PASS with known warnings only.
- Real Buffer credential/channel connection read-only PASS.
- #625 Feed duplicate guard=true and Story duplicate guard=true; no publication performed.

## Exact next
Documentation + diff hygiene -> commit/push exact A2T -> guarded Host desktop/docs-only fast-forward (no DB/migration/restart) -> back up and retarget Windows Desktop shortcut to this exact worktree -> launcher smoke -> handoff to owner.
