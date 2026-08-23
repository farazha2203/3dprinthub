# PROJECT ROADMAP

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Epic: `Phase49 — Unified Product / Slider / Catalog Sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.13 — Windows URL Paste + Approved Batch Full-Fetch Recovery`
Status: `PR MERGED / FINAL CI SUCCESS / WINDOWS RERUN REQUIRED`
Production: `UNTOUCHED / NOT APPROVED`

## Permanent Delivery Order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI → WINDOWS PULL --FF-ONLY → LOCAL GATE → MANUAL QA → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION BACKUP/DEPLOY/VERIFY`

## Immediate Business Priority
1. pass Windows 49.3I.13 acceptance,
2. run exactly one Local Publish E2E,
3. obtain explicit owner approval,
4. verify Host/branch/MySQL/backup/rollback and deploy the approved GitHub snapshot,
5. implement normal Store-cart ZarinPal integration,
6. pass ZarinPal Sandbox E2E,
7. only then perform one owner-approved low-value live payment.

## Phase49.3I Path
`Discovery Review → PS5.1 Encoding → Gallery/First Paint → Live Git Snapshot → Explorer/URL Routing → Selection Guard → Credential Hydration → Preview/Provider Recovery → Observable All-Fields → AI Refresh/SEO Source Completion → AI Trace/Safe Title Retry → Provider Schema/Trace/Busy Recovery → Exact-Page Operator/Image Fit → Windows Paste/Approved Batch Recovery`.

## 49.3I.13 — Current Runtime
Real Windows 49.3I.12 QA proved exact MakerWorld Preview/result URLs are correct, then exposed two operator defects: URL paste was unreliable and approved multi-selection inherited `direct_link.headed=true`, opening one visible browser per candidate. Stored candidate errors were not directly visible.

49.3I.13 adds:
- Ctrl+V / Shift+Insert / right-click Paste / visible Paste Link action,
- approved batch only: existing RichPageExtractor runs background/headless,
- original direct-link browser setting is restored after batch completion/cancel/error,
- single-product intake keeps configured headed behavior,
- selected candidate `last_error` is visible from the operator surface,
- no duplicate crawler/extractor and no schema/data reset.

## Final GitHub Validation — 49.3I.13
PR `#59`: MERGED.
Validated feature head: `b47793c42d807285efbd8d3e005f9979856c4878`.
Merge commit: `3ad097fb3c5ccd2aed82b2dab38f3c8951e00e51`.

Successful runs:
- Phase49.3I `32633932308` — SUCCESS,
- Phase49.3H `32633932302` — SUCCESS,
- Phase49.3G `32633932340` — SUCCESS,
- Full Phase49 + Full Django `32633932224` — SUCCESS.

Django migration: NONE.
Catalog schema migration: NONE.
Production: untouched.

## Employee Catalog Release Gate — NEXT
1. clean Windows worktree,
2. live fetch/prune + ff-only pull current Epic,
3. run `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`,
4. verify runner `49.3I.13` and live Git snapshot marker,
5. verify all four URL paste methods,
6. exact `cake+stand` MakerWorld page → Preview candidates,
7. select 2+ candidates → approved Full Fetch with NO visible per-product browser windows,
8. if a row fails, open Candidate Error Detail and capture the exact stored reason,
9. verify separate direct Product URL intake,
10. regression-check Stop/live state, Product images, AI/provider/model, image limit and Fixed/Range/Formula.

After PASS, employees may begin controlled Catalog entry; then one Local Publish E2E is required before Production approval.

## Storefront Payment Track — Next Product Phase
Normal Store checkout is still manual bank transfer. Next implementation must reuse mature Phase30 ZarinPal semantics: server-owned amount, idempotent attempt, Authority match, server-to-server Verify, duplicate-callback safety, exactly-once finalization, recoverable failures, bank transfer retained, Sandbox E2E before live.

## Immediate Next Step
Run Windows 49.3I.13. Do not repeat the known-failing 49.3I.12 approved batch path. Local Publish / Production remain blocked until this acceptance passes.
