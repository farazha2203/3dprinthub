# PROJECT ROADMAP

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Epic: `Phase49 — Unified Product / Slider / Catalog Sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.10 — AI Trace + Safe Title Retry Recovery`
Status: `FINAL CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Permanent Delivery Order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI → WINDOWS PULL --FF-ONLY → LOCAL GATE → MANUAL QA → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION BACKUP/DEPLOY/VERIFY`

## Immediate Business Priority — 2026-08-23
The owner wants employees to begin Catalog Center data entry today. Priority order:
1. Windows 49.3I.10 acceptance,
2. controlled employee Catalog entry,
3. one Local Publish E2E,
4. explicit owner approval,
5. verified GitHub-only Production deployment,
6. Storefront ZarinPal integration,
7. Sandbox E2E,
8. owner-approved low-value live payment before public activation.

## Preserved Phase49 Foundations
- unified Product / Hero / Catalog synchronization,
- Product Workspace as canonical detailed editor,
- Persian content and SEO workflows,
- Product / Portfolio publish targets,
- AI provider/runtime/provenance/cost stack,
- image intake default 10 / hard max 20,
- Fixed / Range / Formula pricing,
- visual Products Explorer,
- Local vs Production publish separation,
- live fetched GitHub snapshot handoff.

## Phase49.3I Path
Preserved sequence:
`49.3I Discovery Review → 49.3I.1 PS5.1 Encoding → 49.3I.2 Gallery/First Paint → 49.3I.3 Live Git Snapshot → 49.3I.4 Explorer/URL Routing → 49.3I.5 Selection Guard → 49.3I.6 Credential Hydration → 49.3I.7 Preview/Provider Recovery → 49.3I.8 Observable All-Fields → 49.3I.9 AI Refresh/SEO Source Completion → 49.3I.10 AI Trace/Safe Title Retry`.

## 49.3I.10 — Current Runtime
49.3I.10 extends mature AI execution without creating a parallel client:
- AI progress contains scrollable outgoing request, incoming response and Diagnostics tabs,
- high-volume trace panes have vertical and horizontal scrollbars,
- OpenAI-compatible and Google Gemini payload/response trace is sanitized and persisted to existing runtime JSONL,
- API keys/tokens/Authorization headers are excluded,
- title translation is explicitly rerunnable with the current Provider/Model even when an old title exists,
- title-only operator watchdog is 90 seconds,
- Stop Waiting/timeout/workspace closure makes late title results non-applicable,
- generic/non-Persian/too-short title output is rejected before write,
- delayed Tk exception callbacks no longer depend on a cleared `except ... as exc` variable,
- All-Fields keeps its existing 210-second watchdog and stale-result discard,
- 49.3I.9 AI-owned refresh/manual override/source/SEO behavior remains intact.

### Validation
PR `#56` merged after required CI success.
Validated feature head: `8d1f6e02d6f722b8f047f5d7f7763a5a42516191`.
Merge commit: `256c130f179aaa4253898b0d5ec1ce2696ac4bb5`.

Runs:
- Phase49.3I `32626758096` — SUCCESS,
- Phase49.3H `32626758114` — SUCCESS,
- Phase49.3G `32626758134` — SUCCESS,
- Full Phase49 + Django `32626758119` — SUCCESS.

Django migration: NONE.
Catalog schema migration: NONE.

## Employee Catalog Release Gate — NEXT
1. clean Windows worktree,
2. live fetch/prune + ff-only pull current Epic,
3. run `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`,
4. verify Runner `49.3I.10` and Git snapshot marker,
5. wrong-title → Translate Title → request/response/diagnostic visibility,
6. active Provider/Model retry,
7. invalid key/network error remains visible and app stays open,
8. Stop Waiting + 90s title stale-result test,
9. bottom All-Fields trace + 210s stale-result behavior,
10. low-image warning/refetch,
11. MakerWorld Preview → Approve → Full Fetch,
12. Provider/model/FTP/Bridge persistence,
13. Product open/selection + Fixed/Range/Formula.

After this Windows QA passes, employees may begin Catalog entry. Production publishing is still gated by Local Publish E2E and owner approval.

## Local Publish Gate
Exactly one product must pass:
- `LOCAL PUBLISH ONLY`,
- Local Django import/visibility,
- title/description/SEO/source attribution,
- selected images/main image,
- pricing payload,
- Store/Admin rendering,
- no unexpected migration or dirty worktree.

## Storefront Payment Track
Phase30 ZarinPal already supports accepted Quote payments securely, but normal Store checkout is not wired to it. Store checkout currently presents bank transfer/manual payment only.

Next payment implementation must reuse mature security semantics:
- server-owned amount,
- idempotent attempt identity,
- stored Authority match,
- server-to-server Verify,
- duplicate callback safety,
- recoverable cancel/fail/temporary errors,
- inventory/order finalization exactly once,
- bank transfer remains available,
- Sandbox before live activation,
- secrets only in environment/secure server configuration.

Current supported online provider: `ZarinPal`.

## Production Gate
Blocked until Windows QA + Local Publish E2E + explicit owner approval + host/MySQL/backup/rollback verification. Live payment has the additional Store integration + Sandbox + owner-approved live-test gate.

## Immediate Next Step
Run the Windows 49.3I.10 release gate. No direct Local patch, no Production deploy, and no live payment switch before acceptance.
