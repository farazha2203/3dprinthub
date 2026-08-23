# CURRENT PROJECT STATE

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Branch: `epic/phase49-unified-product-slider-sync`
Active Phase: `49.3I`
Active Hotfix: `49.3I.14 — Restore Mature Scan Controls + Single-Product Route`
Status: `IMPLEMENTED / PR #60 OPEN / ALL REQUIRED CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Current Position
Real Windows QA after 49.3I.13 exposed a regression in the Discovery screen that blocks Catalog release:
- Phase49.3I.12 had explicitly hidden healthy mature controls including `شروع اسکن`, `توقف محترمانه`, `دریافت هوشمند از لینک` and `کشف جدیدها`,
- the earlier 49.3I Preview layer had also replaced `App87.start_scan`, so simply showing the old `شروع اسکن` button would still route it to Preview instead of the mature collector,
- the new manual `دریافت محصول تکی` action forced Rich Direct Intake / `RichPageExtractor`; the real MakerWorld product URL `400767` returned `RuntimeError: HTTP 403`, while the owner reports the previous top mature scan path was the working path.

The release is therefore NOT accepted. Local Publish and Production remain blocked until Windows verifies the restored mature route.

## Root Cause — ERR-49-032
This was a regression caused by replacing/hiding healthy acquisition behavior while adding the new Preview/Approve UX. The correct invariant is now explicit: **new discovery controls are additive; mature scan controls and their original collector must remain available and unchanged unless separately approved.**

## Phase49.3I.14 Delta
PR `#60` restores only the broken acquisition boundary:
- old top controls are restored instead of deleted/replaced,
- visible `شروع اسکن` is rebound to the original BaseApp mature `start_scan` worker,
- manual `دریافت محصول تکی` validates the configured Product URL pattern, sets `mode=single`, then uses the same mature BaseApp scan path,
- `دریافت هوشمند از لینک` remains available as an optional independent tool; it is no longer forced by the new single-product button,
- new exact-page Preview / candidate review / Approve / Archive / Paste / error-detail controls remain intact,
- no new crawler/extractor was added.

## CI Incident During Implementation
Initial 49.3I.14 CI correctly failed because the first MRO resolver selected an intermediate Preview override instead of the mature BaseApp method. The failed command was not repeated unchanged. The resolver was corrected to choose the deepest project `start_scan` implementation, then a new commit triggered fresh CI.

Successful current feature-head workflows (`bb6f456b50c1e12bbf6fc5c6b6cc3289f35ee6c8`):
- Phase49.3I.14 Legacy Scan Restore CI — Run `32636391530` — SUCCESS,
- Phase49.3I Discovery Review Pricing CI — Run `32636391489` — SUCCESS,
- Phase49.3H SEO Cost Image Limit CI — Run `32636391571` — SUCCESS,
- Phase49.3G Workspace Usability CI — Run `32636391563` — SUCCESS,
- Phase49 Epic Unified CI / Full Django — Run `32636391518` — SUCCESS.

Validated:
- restored mature scan method resolution,
- single-product mature route,
- preservation of the legacy action set,
- preservation of 49.3I.12/13 Preview/Approve/Paste behavior,
- compile,
- PowerShell ASCII/safety gate,
- Django check + no-migration contract,
- Windows Catalog Epic49 tests,
- Full Django suite.

## Database / Migration / Media / Secret Safety
- Django migration: `NONE`,
- Catalog schema migration: `NONE`,
- no DB reset/drop/truncate,
- no candidate/history/media rewrite/delete,
- no credential changes,
- no FTP/Bridge/Production action.

## Windows QA Required After PR Merge
1. close Catalog Center completely,
2. require clean Local worktree,
3. live fetch/prune + ff-only pull current Epic,
4. run repository hotfix gate `RUN_PHASE49_3I14_HOTFIX_GATE.ps1 -LaunchApp`,
5. verify the mature top controls are visible again,
6. MakerWorld + `single` + `auto` + the same real product URL → use `شروع اسکن`; it must run the old mature collector,
7. test the new `دریافت محصول تکی`; it must route to the same mature collector and must not force the Rich Direct `HTTP 403` path,
8. confirm exact-page Preview/Approve still exists and works.

Do not broaden QA again unless one of these restored contracts fails.

## Next Gate
Immediately after this focused Windows QA passes:
- exactly one `LOCAL PUBLISH ONLY`,
- Local Django Store/Admin E2E,
- verify title/SEO/source/images/pricing/visibility,
- explicit owner approval,
- then read-only Production state/branch/MySQL/backup/rollback verification and GitHub-only deploy.

## Next Product Phase
After Catalog acceptance/deploy, proceed to normal Store ZarinPal checkout request/callback/verify + Sandbox E2E.
