# Phase50.A.2U — Latest Windows Recovery + A2T Port

Status: ACCEPTED / WINDOWS OPERATOR VERIFIED
Date: 2026-09-20
Base Windows lineage: `f1b586457f91e229e7928688766d5cb6f13dddc6`
Source candidate: `d77dfd95f5d3a9a707f9ad03f2aacff9e69ac2e2`
Branch: `wip/phase50-a2u-latest-windows-a2t-20260920`

## Requested delta
- Recover the actual latest Windows Catalog Center, including the repaired image workspace/SEO/screenshot behavior.
- Keep all latest Windows UI fixes; do not replace them with the older A2T lineage.
- Port only the newer Social v5 / Story Link Sticker handoff behavior onto the latest Windows lineage.
- Reconcile Product #625 after a successful Site revision-9 import was falsely marked failed by the old Windows public-media verifier.
- Retarget the Desktop launcher only after the latest Windows candidate is tested and pushed.

## Root cause
The prior Desktop handoff pointed to `D:\projects\3DPrintHub-a2t-windows`, a lineage that contained the newer A2T Social changes but did not descend from the latest Windows UI branch. The actual latest Windows lineage was already present in GitHub at `f1b58645...` and includes the image workspace fixes `d5643864 -> e50ee9b9 -> 20f483af -> 91d4c188 -> 00f16237 -> a52cd52a -> aaa5cb9f -> ea1a4a79` plus later republish/social resilience.

This was a lineage-selection/shortcut error, not missing GitHub history.

## Must not touch
- Existing latest gallery/image/SEO/screenshot UX.
- Shared Catalog authority at `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3` except the explicitly backed-up #625 reconciliation.
- Production source/DB/migrations for this Windows-only phase.
- #625 Instagram revision-8 duplicate evidence; no repost.

## Implemented
- Preserved the complete latest Windows UI ancestry.
- Ported Social v5 clickable Story notification handoff without replacing gallery/image UI.
- Bumped Windows operator build to v8.9.11 / build 2026.09.20.1.
- Kept Buffer Feed automatic; clickable Story uses notification handoff and honest `instagram_story_notification_ready` state.
- Preserved authoritative Site republish behavior and current public-media verifier supporting canonical `/media/p/...`.
- Reconciled #625 revision 9 locally without Bridge re-import after current verifier proved Product HTTP 200 + 2/2 media HTTP 200.

## #625 recovery evidence
Fresh atomic Catalog backup:
`D:\projects\3dprinthub-backups\phase50-a2u-pre-reconcile-625-20260920-210357`
- source integrity: OK
- backup integrity: OK
- backup Product rows: 635
- SHA256: `9304640D9A6D53BB5210FCFD4D1438A102E74D38F80B0C507D861A39D112B32E`

Before reconciliation:
- workflow=batched
- needs_update=1
- upload_ready=1
- Site Product #39 / revision 9
- server_status=updated
- sync error=`PRODUCT_MEDIA_NOT_FOUND_IN_PUBLIC_HTML`

Latest verifier:
- Product HTTP=200
- public media=2
- media HTTP=200,200
- canonical main image under `/media/p/625/...`

After reconciliation:
- workflow=uploaded
- needs_update=0
- upload_ready=0
- Site Product #39 / revision 9
- public_http_ok=true
- receipt=`public_reconciled`
- history event=`public_reconcile_no_reimport`

Production read-only:
- Site revision=9
- active Variants=3
- ProductImages=2
- final weights=60,60,60 g
- material weights=110,110,110 g
- print time=180,180,180 min
- prices=1,095,000 / 1,215,000 / 1,215,000 Toman

## Verification
- Image/SEO/Republish Windows scope: 74/74 PASS.
- Social/Buffer/Story scope: 35/35 PASS.
- Python compile PASS.
- Qt `qt_launch.py --verify-only` PASS.
- Repository `RUN_QT.ps1 -VerifyOnly` PASS.
- v8.9.11 / build 2026.09.20.1 verified.
- Real Desktop shortcut launch PASS; running main window title is `3DPrintHub Catalog Center v8.9.11 - Qt 6`.
- No Production source deploy, migration or restart.

## Operator path
Current Windows worktree:
`D:\projects\3DPrintHub-a2u-latest-windows`

Desktop launchers target:
`D:\projects\3DPrintHub-a2u-latest-windows\catalog_center\RUN_QT.ps1`

Shortcut rollback:
`D:\projects\3dprinthub-backups\phase50-a2u-shortcut-20260920-210723`

## Closure
A2U is the current Windows operator lineage. Do not point the Desktop shortcut back to A2T or the older primary clone. Future Windows changes start from A2U (or a verified descendant) and must preserve its image/gallery/SEO/screenshot behavior.
