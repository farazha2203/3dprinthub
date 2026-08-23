# PROJECT ROADMAP

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Epic: `Phase49 — Unified Product / Slider / Catalog Sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.12 — Observable Exact-Page Discovery + Single-Product Intake + Workspace Image Fit`
Status: `PR MERGED / FINAL CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Permanent Delivery Order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI → WINDOWS PULL --FF-ONLY → LOCAL GATE → MANUAL QA → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION BACKUP/DEPLOY/VERIFY`

## Immediate Business Priority — 2026-08-23
1. pass Windows 49.3I.12 acceptance on exact-page discovery, single-product intake and image fitting,
2. run one Local Publish E2E,
3. obtain explicit owner approval,
4. deploy the approved GitHub snapshot to Production after host/MySQL/backup verification,
5. implement normal Store-cart ZarinPal integration,
6. pass ZarinPal Sandbox E2E,
7. only then perform one owner-approved low-value live payment.

## Phase49.3I Path
`Discovery Review → PS5.1 Encoding → Gallery/First Paint → Live Git Snapshot → Explorer/URL Routing → Selection Guard → Credential Hydration → Preview/Provider Recovery → Observable All-Fields → AI Refresh/SEO Source Completion → AI Trace/Safe Title Retry → Provider Schema/Trace/Busy Runtime Recovery → Observable Exact-Page Discovery/Single-Product Intake/Image Fit`.

## 49.3I.12 — Current Runtime
Owner evidence showed the backend exact MakerWorld page scan itself succeeded, but the final UX87 operator surface did not expose the review panel/live operation state clearly enough, and manual single-product intake was not separated from page discovery. Product Workspace image cards also needed a stable fixed-pixel fitting contract.

49.3I.12 preserves the mature discovery/extractor architecture and adds:
- final UX87 `_ui`-boundary operator panel,
- exact-page Search/Listing/Category discovery action,
- separate direct Product URL action validated by configured source regex,
- visible running/stopping/done state, progress, elapsed time and active URL/detail,
- mature candidate thumbnail/title/source/id/url renderer reused through a runtime bridge,
- fixed 228x171 `ImageOps.contain` image cards without crop/stretch,
- Preview remains lightweight and Full Fetch still requires approval,
- AI/provider/pricing/source/publish behavior preserved.

### Final Validation
PR `#58`: MERGED.
Validated feature head: `2a9442055d33777f675ccd3ebe11de8419bfb2b3`.
Merge commit: `24d5b8fdddb97fbcc4c07efa7d6f1d78a0ffb225`.

Successful runs:
- Phase49.3I `32631604990` — SUCCESS,
- Phase49.3H `32631604930` — SUCCESS,
- Phase49.3G `32631604945` — SUCCESS,
- Full Phase49 + Full Django `32631604928` — SUCCESS.

Django migration: NONE.
Catalog schema migration: NONE.
Production: untouched.

## Employee Catalog Release Gate — NEXT
1. clean Windows worktree,
2. live fetch/prune + ff-only pull current Epic,
3. run `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`,
4. verify runner `49.3I.12` and live Git snapshot marker,
5. paste exact `cake+stand` MakerWorld Search URL and run exact-page discovery,
6. verify visible live state/progress/elapsed/current URL,
7. verify candidate links appear before Full Fetch,
8. approve one candidate and run Full Fetch,
9. test one direct Product URL with the separate single-product action,
10. test Stop feedback,
11. verify Product Workspace portrait/landscape images fit into equal 228x171 cards,
12. regression-check All-Fields AI, Provider/model, image limit and Fixed/Range/Formula.

After this Windows QA passes, run exactly one Local Publish E2E. Production remains blocked until owner approval.

## Local Publish Gate
Exactly one product must pass Local import/visibility, title/description/SEO/source attribution, selected images/main image, pricing payload and Store/Admin rendering without unexpected migration or dirty worktree.

## Storefront Payment Track — Next Product Phase
Normal Store checkout is still manual bank transfer. The next implementation must reuse mature Phase30 ZarinPal security semantics:
- server-owned/recomputed amount,
- idempotent Store payment attempt,
- stored Authority must match callback Authority,
- server-to-server Verify before marking paid,
- duplicate callback cannot double-finalize payment/order/inventory,
- failed/cancelled/temporary errors remain recoverable,
- bank transfer remains available,
- Sandbox E2E before live,
- secrets outside Git,
- one owner-approved low-value live test before public activation.

## Production Gate
Blocked until Windows QA + Local Publish E2E + explicit owner approval + host branch/path/MySQL/backup/rollback verification. Live payment has the additional Store integration + Sandbox gate.

## Immediate Next Step
Run the Windows 49.3I.12 release gate. On PASS, immediately perform one Local Publish E2E and then move to Production approval/deploy and the Store ZarinPal phase.
