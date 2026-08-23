# CURRENT PROJECT STATE

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Branch: `epic/phase49-unified-product-slider-sync`
Active Phase: `49.3I`
Active Hotfix: `49.3I.12 — Observable Exact-Page Discovery + Single-Product Intake + Workspace Image Fit`
Status: `GITHUB UPDATED / PR MERGED / FINAL CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Current Position
Phase49.3I.12 is merged into the active Epic. The owner screenshots proved the exact MakerWorld search URL backend path itself was already successful (`PREVIEW_TARGET` used the exact pasted URL, `candidates=20`, `failed=0`, `full_fetch=0`), but the UX87 operator surface did not make the review/result/live-running state visible enough and did not expose a clean separate single-product manual intake path. The owner also reported poor Product Workspace image fitting.

Canonical release order remains:
`GitHub → Windows ff-only pull → Local automated gate → Manual visual/data/interaction QA → one LOCAL PUBLISH ONLY → Local Django E2E → explicit owner approval → Production backup/deploy/verify`.

## Phase49.3I.12 Implemented Delta
PR `#58` is merged.

Discovery/operator behavior:
- exact pasted Search/Listing/Category URL remains authoritative,
- final UX87 `_ui` boundary mounts a visible manual operator panel,
- separate `کشف لینک‌های همین صفحه` action for page discovery,
- separate `دریافت محصول تکی` action validated by the configured source `model_url_pattern`,
- visible live state badge, indeterminate progress, elapsed time, current URL/detail and explicit Stop request feedback,
- mature candidate review contract preserved: one thumbnail + basic title/identity/source/external-id/url,
- Preview still performs no Full Fetch,
- approved candidates still reuse mature Full Fetch,
- archive/dedupe/image-limit contracts remain unchanged.

Product Workspace image behavior:
- fixed `228x171` pixel viewport,
- `ImageOps.contain` + letterbox fitting,
- no crop/stretch,
- no Tk text-unit width/height sizing for image labels.

## GitHub Validation — 49.3I.12
Implementation PR: `#58` — MERGED.
Validated feature head: `2a9442055d33777f675ccd3ebe11de8419bfb2b3`.
Epic merge commit: `24d5b8fdddb97fbcc4c07efa7d6f1d78a0ffb225`.

Successful workflows on the validated feature head:
- Phase49.3I Discovery Review Pricing CI — Run `32631604990` — SUCCESS.
- Phase49.3H SEO Cost Image Limit CI — Run `32631604930` — SUCCESS.
- Phase49.3G Workspace Usability CI — Run `32631604945` — SUCCESS.
- Phase49 Epic Unified CI / Full Django — Run `32631604928` — SUCCESS.

Validated:
- runner `49.3I.12` / ASCII-only Windows PowerShell 5.1 contract,
- live fetched GitHub snapshot guard,
- compile,
- exact-page/manual-product URL classification,
- final UX87 composition-boundary operator UI,
- candidate Treeview compatibility with mature thumbnail renderer,
- live status/stop markers,
- 228x171 contain-fit image contract,
- prior AI schema/trace/busy-release behavior,
- Preview/Approve/Full Fetch safety,
- image limit 1..20 default 10,
- Fixed/Range/Formula regressions,
- Django check and no-migration contract,
- Windows Catalog Epic49 tests,
- Full Django suite.

## Database / Migration / Media / Secret Safety
- Django migration for 49.3I.12: `NONE` — CI verified.
- Catalog schema migration: `NONE`.
- no DB reset/drop/truncate.
- no historical data/media rewrite/delete.
- no credential storage change.
- Production DB/media/source untouched.

## Current Known Release Blocker
Windows still has to pull the current live Epic snapshot and execute the repository-owned 49.3I.12 Local gate. Phase49.3I is not accepted until the visible operator flows are manually verified on the real Windows runtime.

## Windows QA Required Now
1. close Catalog Center completely,
2. require clean Local worktree,
3. live fetch/prune + ff-only pull current Epic,
4. run `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`,
5. verify Runner `49.3I.12` + `PHASE49_3I_GIT_SNAPSHOT=OK`,
6. paste `https://makerworld.com/en/search/models?keyword=cake+stand` and use exact-page discovery,
7. confirm visible badge/progress/elapsed/current URL while running,
8. confirm candidate links from that same page are visible before Full Fetch,
9. select one candidate and run approved Full Fetch,
10. paste one real MakerWorld Product URL and use single-product intake,
11. confirm Stop visibly registers,
12. open Product Workspace Images and verify portrait/landscape images use equal 228x171 contain viewports without crop/stretch,
13. regression-check All-Fields AI / Provider-model / image limit / Fixed-Range-Formula.

## Local Publish / Production Gate
After Windows QA passes:
- exactly one `LOCAL PUBLISH ONLY`,
- Local Django E2E,
- verify title/SEO/images/pricing/source attribution in Local Store/Admin,
- explicit owner approval,
- then re-verify host branch/path/MySQL/backup/rollback and deploy only the approved GitHub snapshot.

## Next Product Phase After Catalog Acceptance
Normal Store-cart online payment remains incomplete. The next implementation track is Store checkout ZarinPal request/callback/verify with server-owned amount, idempotency, Authority verification, duplicate-callback safety, inventory/order finalization exactly once and Sandbox E2E before any live activation. Manual bank transfer remains available.

## Exact Next Task
Windows must pull the current Epic with live ff-only GitHub snapshot semantics and run the 49.3I.12 repository gate. Do not skip this acceptance. After it passes, run one Local Publish E2E and then proceed immediately to Production gate and the Store payment phase.
