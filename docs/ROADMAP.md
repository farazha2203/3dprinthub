# PROJECT ROADMAP

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Epic: `Phase49 — Unified Product / Slider / Catalog Sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.14 — Restore Mature Scan Controls + Single-Product Route`
Status: `IMPLEMENTED / PR #60 OPEN / ALL REQUIRED CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Permanent Delivery Order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI → WINDOWS PULL --FF-ONLY → LOCAL GATE → MANUAL QA → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION BACKUP/DEPLOY/VERIFY`

## Immediate Business Priority
1. merge 49.3I.14 after successful CI,
2. focused Windows QA of restored mature acquisition only,
3. exactly one Local Publish E2E,
4. explicit owner approval,
5. Host/branch/MySQL/backup/rollback verification + Production deploy from GitHub,
6. then normal Store-cart ZarinPal integration and Sandbox E2E.

## Phase49.3I Path
`Discovery Review → PS5.1 Encoding → Gallery/First Paint → Live Git Snapshot → Explorer/URL Routing → Selection Guard → Credential Hydration → Preview/Provider Recovery → Observable All-Fields → AI Refresh/SEO → AI Trace → Provider Schema Recovery → Exact-Page Operator/Image Fit → Paste/Batch Recovery → Mature Scan Restoration`.

## 49.3I.14 — Current Runtime Delta
Windows QA showed that 49.3I.12 had hidden healthy mature acquisition buttons and the 49.3I Preview layer had shadowed the old `start_scan`. The new single-product action also forced Rich Direct Intake and hit MakerWorld HTTP 403.

49.3I.14 is intentionally narrow:
- restore `شروع اسکن`, `توقف محترمانه`, `دریافت هوشمند از لینک`, `کشف جدیدها`,
- rebind `شروع اسکن` to original BaseApp mature scan worker,
- route new manual single-product action through the same mature `mode=single` path,
- keep Rich Direct Intake optional rather than mandatory,
- keep Preview/Approve/Archive/Paste/error-detail UI intact,
- add no crawler/extractor, migration, DB/media rewrite or Production change.

## GitHub Validation — Feature Head
Feature head: `bb6f456b50c1e12bbf6fc5c6b6cc3289f35ee6c8`.
PR: `#60` OPEN.

Successful runs:
- Phase49.3I.14 Legacy Scan Restore `32636391530` — SUCCESS,
- Phase49.3I `32636391489` — SUCCESS,
- Phase49.3H `32636391571` — SUCCESS,
- Phase49.3G `32636391563` — SUCCESS,
- Full Phase49 + Full Django `32636391518` — SUCCESS.

The first 49.3I.14 targeted test run correctly failed on an MRO-resolution defect; code was changed before a fresh successful run. Canonical incident: `ERR-49-032`.

Django migration: NONE.
Catalog schema migration: NONE.
Production: untouched.

## Focused Employee Catalog Release Gate — NEXT
After PR merge:
1. clean Windows worktree,
2. live fetch/prune + ff-only pull current Epic,
3. run `RUN_PHASE49_3I14_HOTFIX_GATE.ps1 -LaunchApp`,
4. confirm mature top actions are visible,
5. MakerWorld + `single` + `auto` + known product URL → `شروع اسکن` uses the old mature acquisition path,
6. new `دریافت محصول تکی` uses that same mature path and no longer forces the Rich Direct HTTP-403 route,
7. confirm the existing exact-page Preview/Approve UI remains present.

No broad repeat QA unless one of these contracts fails.

## After Windows PASS
Immediately run exactly one `LOCAL PUBLISH ONLY` + Local Django Store/Admin E2E. If title/SEO/source/images/pricing/visibility are correct and owner approves, verify Production state/backup/rollback and deploy the approved GitHub snapshot.

## Next Product Phase
Normal Store checkout is still manual bank transfer. Next implementation is ZarinPal request/callback/verify using mature Phase30 security semantics and Sandbox E2E before live activation.
