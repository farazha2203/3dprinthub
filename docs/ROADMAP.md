# PROJECT ROADMAP

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Epic: `Phase49 — Unified Product / Slider / Catalog Sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.17 — Single Active AI Runtime`
Status: `MERGED / ALL REQUIRED CI SUCCESS / WINDOWS QA NEXT`
Production: `UNTOUCHED / NOT APPROVED`

## Permanent Delivery Order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI → WINDOWS PULL --FF-ONLY → LOCAL GATE → MANUAL QA → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION BACKUP/DEPLOY/VERIFY`

## Immediate Business Priority
1. focused Windows acceptance of 49.3I.17 exact saved Provider/Model behavior and UI non-hang,
2. finish the short 49.3I.16 acquisition acceptance if still needed,
3. exactly one Local Publish E2E,
4. explicit owner approval,
5. verify Production branch/path/venv/MySQL/backup/rollback,
6. deploy approved GitHub snapshot and verify Production,
7. then Store ZarinPal integration + Sandbox E2E.

## Phase49.3I Path
`Discovery Review → PS5.1 Guard → Gallery/AI First-Paint → Live Git Snapshot → Explorer/Routing → Selection Guard → Credential Persistence → Provider/Preview Recovery → Observable AI → SEO/Source → AI Trace → Provider Schema → Exact-Page UI/Image Fit → Paste/Batch Recovery → Mature Scan Restoration → Bulk Exact-Page Images/Add-to-Products → Resilient Acquisition Fallback/Cached Reuse → Single Active AI Runtime`.

## 49.3I.17 — Canonical AI Rule
Product AI is now explicit and deterministic:
- one saved Provider,
- one saved Model for that Provider,
- one secure key belonging to that Provider,
- no automatic fallback to another configured Provider,
- no hidden AI request when a Product Workspace opens,
- no `/models` catalog request before each Product AI content request,
- Google exact Product model does not re-list models before generation,
- explicit Settings model search/test still uses live provider APIs,
- stale Tk callbacks cannot become fatal Product Workspace dialogs.

Existing 49.3I.8–11 request trace, schema repair, watchdog/Stop Waiting, stale-result protection and manual-override protection remain.

## Acquisition Contract Preserved
49.3I.16 remains unchanged:
- discovery fallback `locator-safe → HTTP/HTML → attached Chrome 9222 → cached candidate DB`,
- image fallback `locator-safe → HTTP → mature DOM → Chrome 9222 → listing thumbnail`,
- product max 100 / image max 20,
- Add-to-Products without Rich Direct Full Fetch,
- Archive/Block/dedupe and staged-image readiness.

## GitHub Validation / Merge
PR `#63` merged.
- final PR head `2917a3db5225abac71fc3e80b64ad439acd7a4d0`,
- merge commit `7f835f573b92e3aded6275c9421770c0c47d947a`.

Final runtime-head SUCCESS:
- 49.3I.17 `32649623837`,
- 49.3I `32649623808`,
- 49.3I.16 `32649623695`,
- 49.3I.15 `32649623705`,
- 49.3I.14 `32649623679`,
- 49.3H `32649623825`,
- 49.3G `32649623755`,
- Full Phase49 + Windows Catalog regressions + Full Django `32649623804`.

Django migration: NONE. Catalog schema migration: NONE. Production untouched.

## Focused Windows Gate
1. clean worktree + live fetch/ff-only current Epic,
2. `RUN_PHASE49_3I17_SINGLE_AI_GATE.ps1 -LaunchApp`,
3. select/save one active Provider/Model in AI Center,
4. open Product Workspace: no hidden AI network activity,
5. run All-Fields once: trace must use only the saved Provider/Model and not begin with `/models`,
6. Stop/failure must leave the application responsive,
7. save a different Provider/Model and verify the next request uses only that new pair.

If PASS, proceed immediately to one Local Publish E2E and then Production gate/deploy.

## Next Product Phase
After Catalog Production verification: Store checkout ZarinPal request/callback/verify, Sandbox E2E, then one owner-approved low-value live payment while bank transfer remains available.
