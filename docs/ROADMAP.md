# PROJECT ROADMAP

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Epic: `Phase49 — Unified Product / Slider / Catalog Sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.14 — Restore Mature Scan Controls + Single-Product Route`
Status: `PR #60 MERGED / ALL REQUIRED CI SUCCESS / FOCUSED WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Permanent Delivery Order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI → WINDOWS PULL --FF-ONLY → LOCAL GATE → MANUAL QA → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION BACKUP/DEPLOY/VERIFY`

## Immediate Business Priority
1. focused Windows QA of 49.3I.14,
2. exactly one Local Publish E2E,
3. explicit owner approval,
4. Host/branch/MySQL/backup/rollback verification + Production deploy from GitHub,
5. then normal Store-cart ZarinPal integration and Sandbox E2E.

## Phase49.3I Path
`Discovery Review → PS5.1 Encoding → Gallery/First Paint → Live Git Snapshot → Explorer/URL Routing → Selection Guard → Credential Hydration → Preview/Provider Recovery → Observable All-Fields → AI Refresh/SEO → AI Trace → Provider Schema Recovery → Exact-Page Operator/Image Fit → Paste/Batch Recovery → Mature Scan Restoration`.

## 49.3I.14 Final Runtime
The release regression recorded as `ERR-49-032` is fixed by restoring mature acquisition beside the new Review UX:
- restore `شروع اسکن`, `توقف محترمانه`, `دریافت هوشمند از لینک`, `کشف جدیدها`,
- bind `شروع اسکن` to original BaseApp mature scan worker,
- route manual single-product acquisition through the same mature `mode=single` worker,
- keep Rich Direct intake optional,
- keep Preview/Approve/Archive/Paste/error-detail intact,
- no new crawler/extractor, migration, DB/media rewrite or Production change.

## GitHub Validation
PR #60: MERGED.
Final PR head: `f12a25e1fe50fb16a03a1324c84912c830a2608e`.
Merge commit: `124662cf2436dfcce245282b01b2da694802aa55`.

Successful final PR-head runs:
- Phase49.3I.14 Legacy Scan Restore `32636771174` — SUCCESS,
- Phase49.3I `32636771071` — SUCCESS,
- Phase49.3H `32636771154` — SUCCESS,
- Phase49.3G `32636771049` — SUCCESS,
- Full Phase49 + Full Django `32636771103` — SUCCESS.

Django migration: NONE.
Catalog schema migration: NONE.
Production: untouched.

## Focused Employee Catalog Release Gate — NEXT
1. clean Windows worktree,
2. live fetch/prune + ff-only pull current Epic,
3. run `RUN_PHASE49_3I14_HOTFIX_GATE.ps1 -LaunchApp`,
4. confirm mature top actions are visible,
5. MakerWorld + `single` + `auto` + known Product URL → `شروع اسکن` uses mature acquisition,
6. new `دریافت محصول تکی` uses the same mature route and does not force the Rich Direct 403 path,
7. confirm exact-page Preview/Approve remains present.

No broad repeat QA unless one of these focused contracts fails.

## After Windows PASS
Run exactly one `LOCAL PUBLISH ONLY` + Local Django Store/Admin E2E. If title/SEO/source/images/pricing/visibility are correct and owner approves, verify Production state/backup/rollback and deploy the approved GitHub snapshot.

## Next Product Phase
Normal Store checkout is still manual bank transfer. Next implementation is ZarinPal request/callback/verify using mature Phase30 security semantics and Sandbox E2E before live activation.
