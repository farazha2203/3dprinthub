# PROJECT ROADMAP

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Epic: `Phase49 — Unified Product / Slider / Catalog Sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.16 — Resilient Acquisition Fallback + Cached Candidate Reuse`
Status: `MERGED / ALL REQUIRED CI SUCCESS / WINDOWS QA NEXT`
Production: `UNTOUCHED / NOT APPROVED`

## Permanent Delivery Order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI → WINDOWS PULL --FF-ONLY → LOCAL GATE → MANUAL QA → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION BACKUP/DEPLOY/VERIFY`

## Immediate Business Priority
1. focused Windows test of merged 49.3I.16 resilient acquisition,
2. exactly one Local Publish E2E after focused QA PASS,
3. explicit owner approval,
4. verify Production branch/path/venv/MySQL/backup/rollback,
5. deploy approved GitHub snapshot and verify Production,
6. then Store ZarinPal integration + Sandbox E2E.

## Phase49.3I Path
`Discovery Review → PS5.1 Guard → Gallery/AI First-Paint → Live Git Snapshot → Explorer/Routing → Selection Guard → Credential Persistence → Provider/Preview Recovery → Observable AI → SEO/Source → AI Trace → Provider Schema → Exact-Page UI/Image Fit → Paste/Batch Recovery → Mature Scan Restoration → Bulk Exact-Page Images/Add-to-Products → Resilient Acquisition Fallback/Cached Reuse`.

## 49.3I.16 — Canonical Resilience Rule
A single crawler/browser/parser path is no longer allowed to be a release blocker when the same source has other verified acquisition routes or previously persisted candidates.

Discovery ladder:
`locator-safe → HTTP/HTML → attached Chrome 9222 → cached candidate DB`.

Image ladder per candidate:
`locator-safe fresh → HTTP parse/downloader → mature Classic DOM → attached Chrome 9222 → listing thumbnail`.

Contracts:
- no embedded `evaluate_all` at the new resilient discovery boundary,
- every failed method is traced before trying the next one,
- prior correct candidates for the same exact listing can be reused,
- local image staging remains required before a candidate is ready/addable,
- one candidate failure does not abort the rest,
- product max 100 / image max 20 unchanged,
- no Rich Direct Full Fetch dependency in the bulk path,
- Add-to-Products / Archive / Block / dedupe unchanged,
- AI/SEO/pricing/publish/FTP/Bridge/credentials unchanged.

## GitHub Validation / Merge
PR `#62` merged.
- final PR head `8f4fbe6d0264f673d0e6564a4ed1e383db023ab6`,
- merge commit `44216546162fead0b752d92cf6cae8d658f034f2`.

Final-head SUCCESS:
- 49.3I.16 `32645660164`,
- 49.3I `32645660154`,
- 49.3I.15 `32645660045`,
- 49.3I.14 `32645660071`,
- 49.3H `32645660135`,
- 49.3G `32645660118`,
- Full Phase49 + Windows Catalog regressions + Full Django `32645660123`.

Django migration: NONE.
Catalog candidate schema migration: NONE.
Production: untouched.

## Focused Windows Gate
1. clean worktree + live fetch/ff-only current Epic,
2. `RUN_PHASE49_3I16_FALLBACK_GATE.ps1 -LaunchApp`,
3. exact MakerWorld page with `10 products × 10 images`,
4. verify the run proceeds through fallback methods instead of aborting on the first error,
5. verify cached candidates are reused if live discovery cannot re-read the page,
6. select 2–3 staged rows → Add to Products without Direct Full Fetch,
7. Archive one row,
8. open one added Product and verify images.

If PASS, proceed immediately to exactly one Local Publish E2E and then Production gate/deploy.

## Next Product Phase
After Catalog Production verification: Store checkout ZarinPal request/callback/verify, Sandbox E2E, then one owner-approved low-value live payment while bank transfer remains available.
