# CURRENT PROJECT STATE

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Branch: `epic/phase49-unified-product-slider-sync`
Active Phase: `49.3I`
Active Hotfix: `49.3I.13 — Windows URL Paste + Approved Batch Full-Fetch Recovery`
Status: `GITHUB UPDATED / PR MERGED / FINAL CI SUCCESS / WINDOWS RERUN REQUIRED`
Production: `UNTOUCHED / NOT APPROVED`

## Current Position
Real Windows QA of 49.3I.12 proved the final UX87 discovery panel and exact MakerWorld Preview are now visible and correct: candidate image/title/source/ID/URL rows are populated and the URLs themselves are correct. The same QA exposed two new release blockers:
- the exact URL field did not provide reliable paste behavior, forcing manual typing,
- approved multi-candidate Full Fetch opened/closed one visible browser per selected candidate and some rows ended in `failed` without a directly visible technical reason.

The release was therefore NOT accepted and Local Publish / Production remain blocked.

## Root Cause — ERR-49-031
Repository inspection confirmed:
- the 49.3I.12 URL field was a plain `ttk.Entry` without the explicit Windows paste bindings/context menu already used by other operator fields,
- the mature approved batch method calls the rich direct extractor once per selected candidate and inherited `direct_link.headed=true`, causing one visible persistent browser context per selected row,
- candidate `last_error` was already persisted but not exposed directly in the final operator surface.

## Phase49.3I.13 Implemented Delta
PR `#59` is merged.

Operator URL input:
- explicit Ctrl+V / Ctrl+V uppercase / Shift+Insert support,
- right-click Paste menu,
- visible `چسباندن لینک` button,
- first non-empty clipboard line is used without damaging URL query parameters.

Approved multi-candidate Full Fetch:
- reuses the existing mature RichPageExtractor; no second crawler/extractor,
- only the approved batch path temporarily forces background/headless browser mode,
- original direct-link headed setting is restored when the batch ends/cancels/errors,
- separate single-product intake keeps its configured headed behavior for login/CAPTCHA recovery,
- visible `جزئیات خطای انتخابی` reads the already-persisted `last_error` for selected candidates.

Preserved:
- exact Search/Listing URL authority,
- Preview = one thumbnail/basic identity only,
- Full Fetch only after approval,
- archive/dedupe,
- image limit 1..20 default 10,
- Product Workspace image fit 228x171 contain,
- AI/provider/schema/trace/manual-override contracts,
- Fixed/Range/Formula independence,
- Local/Production publish separation.

## GitHub Validation — 49.3I.13
Implementation PR: `#59` — MERGED.
Validated feature head: `b47793c42d807285efbd8d3e005f9979856c4878`.
Epic merge commit: `3ad097fb3c5ccd2aed82b2dab38f3c8951e00e51`.

Successful workflows:
- Phase49.3I Discovery Review Pricing CI — Run `32633932308` — SUCCESS,
- Phase49.3H SEO Cost Image Limit CI — Run `32633932302` — SUCCESS,
- Phase49.3G Workspace Usability CI — Run `32633932340` — SUCCESS,
- Phase49 Epic Unified CI / Full Django — Run `32633932224` — SUCCESS.

Validation includes:
- runner `49.3I.13` and ASCII-only Windows PowerShell 5.1 contract,
- live fetched GitHub snapshot guard,
- compile,
- dedicated 49.3I.13 clipboard/batch-browser restoration tests,
- final runtime bridge installation,
- no duplicate crawler/extractor,
- prior Discovery/AI/Provider/SEO/Pricing regressions,
- Django `makemigrations --check --dry-run`,
- Windows Catalog Epic49 tests,
- Full Django suite.

## Database / Migration / Media / Secret Safety
- Django migration for 49.3I.13: `NONE` — CI verified,
- Catalog schema migration: `NONE`,
- no DB reset/drop/truncate,
- no candidate/history/media deletion or rewrite,
- no credential storage change,
- Production DB/media/source untouched.

## Windows QA Required Now
1. close Catalog Center completely,
2. require clean Local worktree,
3. live `git fetch --prune origin` + ff-only pull current Epic,
4. run `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`,
5. verify runner `49.3I.13` + `PHASE49_3I_GIT_SNAPSHOT=OK`,
6. verify Ctrl+V, Shift+Insert, right-click Paste and `چسباندن لینک` in the exact URL field,
7. run exact MakerWorld page Preview and confirm candidates remain visible before Full Fetch,
8. select 2+ candidates and run approved Full Fetch; no browser window may flash/open per candidate,
9. if any row fails, select it and use `جزئیات خطای انتخابی` to capture the exact stored reason,
10. regression-check direct Product intake, Stop/live state, 228x171 images, AI/provider/model, image limit and Fixed/Range/Formula.

## Local Publish / Production Gate
Only after this Windows QA passes:
- exactly one `LOCAL PUBLISH ONLY`,
- Local Django E2E verifying title/SEO/source/images/pricing/Store/Admin,
- explicit owner approval,
- then read-only Host/branch/MySQL/backup/rollback verification and Production deploy from GitHub.

## Next Product Phase
Normal Store checkout still uses bank transfer/manual payment. After Catalog acceptance the next implementation track is Store ZarinPal request/callback/verify + Sandbox E2E, reusing mature Phase30 security semantics.

## Exact Next Task
Windows must pull the current live Epic and rerun the repository-owned 49.3I.13 gate. Do not repeat the failing 49.3I.12 batch action before that pull. Local Publish and Production remain blocked.
