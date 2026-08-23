# PROJECT ROADMAP

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Epic: `Phase49 — Unified Product / Slider / Catalog Sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.11 — Provider Schema + Trace/Busy Runtime Recovery`
Status: `FINAL CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Permanent Delivery Order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI → WINDOWS PULL --FF-ONLY → LOCAL GATE → MANUAL QA → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION BACKUP/DEPLOY/VERIFY`

## Immediate Business Priority — 2026-08-23
1. pass Windows 49.3I.11 acceptance on the exact previously failing AI product,
2. allow controlled employee Catalog entry,
3. run one Local Publish E2E,
4. obtain explicit owner approval,
5. deploy the approved GitHub snapshot to Production after host/MySQL/backup verification,
6. implement normal Store-cart ZarinPal integration,
7. pass ZarinPal Sandbox E2E,
8. only then perform one owner-approved low-value live payment.

## Phase49.3I Path
`Discovery Review → PS5.1 Encoding → Gallery/First Paint → Live Git Snapshot → Explorer/URL Routing → Selection Guard → Credential Hydration → Preview/Provider Recovery → Observable All-Fields → AI Refresh/SEO Source Completion → AI Trace/Safe Title Retry → Provider Schema/Trace/Busy Runtime Recovery`.

## 49.3I.11 — Current Runtime
Owner Windows evidence proved a successful AvalAI response could still be structurally unusable because the adapter requested only generic JSON and did not send the repository schema. The same trace also exposed UI pressure from full model-catalog rendering and a stale busy-state path after cancellation/timeout.

49.3I.11 preserves mature architecture and adds:
- actual JSON Schema delivery to AvalAI/OpenRouter,
- exact field/type validation before persistence,
- one bounded schema repair when the first JSON violates the contract,
- explicit selected-model execution,
- per-request-window model-info cache,
- compact `/models` trace,
- immediate busy-state release on Stop Waiting/watchdog/stale abort,
- late-result mutation still blocked,
- existing 90-second title and 210-second full-AI watchdogs preserved,
- prior request/response/error observability, AI-owned refresh/manual override, source/SEO, Preview/Full Fetch and pricing behavior preserved.

### Final Validation
PR `#57`: MERGED.
Validated feature head: `9bdcfb3c7997cc9570d2d94e1bafd4f7bfad5651`.
Merge commit: `41d37d56437765119b9bb274037e9af7a5defbbe`.

Successful runs:
- Phase49.3I `32628666588` — SUCCESS,
- Phase49.3H `32628666600` — SUCCESS,
- Phase49.3G `32628666558` — SUCCESS,
- Full Phase49 + Full Django `32628666582` — SUCCESS.

Django migration: NONE.
Catalog schema migration: NONE.
Production: untouched.

## Employee Catalog Release Gate — NEXT
1. clean Windows worktree,
2. live fetch/prune + ff-only pull current Epic,
3. run `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`,
4. verify runner `49.3I.11` and live Git snapshot marker,
5. retry exact AvalAI product that previously returned schema aliases,
6. verify exact schema keys/types or one visible repair attempt,
7. verify `/models` trace is compact and UI remains responsive,
8. Stop Waiting → change Provider/Model → immediate new request; stale old result cannot apply,
9. verify All-Fields + title watchdog behavior,
10. low-image warning/refetch,
11. MakerWorld Preview → Approve → Full Fetch,
12. Provider/model/FTP/Bridge persistence,
13. Product open/selection + Fixed/Range/Formula regression.

After this Windows QA passes, employees may begin Catalog entry. Production publishing remains blocked by one Local Publish E2E + explicit owner approval.

## Local Publish Gate
Exactly one product must pass Local import/visibility, title/description/SEO/source attribution, selected images/main image, pricing payload and Store/Admin rendering without unexpected migration or dirty worktree.

## Storefront Payment Track
Normal Store checkout is still manual bank transfer. The next payment implementation must reuse mature Phase30 ZarinPal security semantics: server-owned amount, idempotent attempt, Authority match, server-to-server Verify, duplicate callback safety, recoverable failure/cancel, inventory/order finalization once, Sandbox before live, secrets outside Git.

## Production Gate
Blocked until Windows QA + Local Publish E2E + explicit owner approval + host branch/path/MySQL/backup/rollback verification. Live payment has the additional Store integration + Sandbox gate.

## Immediate Next Step
Run the Windows 49.3I.11 release gate. No direct Local patch, Production deploy or live payment switch before acceptance.
