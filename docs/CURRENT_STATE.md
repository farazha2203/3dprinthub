# CURRENT PROJECT STATE

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Branch: `epic/phase49-unified-product-slider-sync`
Active Phase: `49.3I`
Active Hotfix: `49.3I.11 — Provider Schema + Trace/Busy Runtime Recovery`
Status: `GITHUB UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Current Position
49.3I.11 is merged into the active Epic after the owner supplied a real Windows AI trace proving that the Provider returned HTTP success and useful Persian content, but the returned JSON did not satisfy the exact Catalog schema. Windows must now pull the live Epic snapshot and rerun the release gate before employee handoff.

Canonical release order remains:
`GitHub → Windows ff-only pull → Local automated gate → Manual visual/data/interaction QA → one LOCAL PUBLISH ONLY → Local Django E2E → explicit owner approval → Production backup/deploy/verify`.

## New Runtime Incident — ERR-49-029
Owner evidence showed AvalAI `gemini-3.5-flash-lite` returned a successful structured-content response containing a good specific Persian title, but fields were named/typed incorrectly for the repository contract:
- returned `seo_title`; required `seo_title_fa`,
- returned `seo_description`; required `seo_description_fa`,
- returned `content_notes` as a string; required an array,
- several other required schema fields were absent.

Therefore the existing validator correctly refused to persist the incomplete pack and surfaced the apparently misleading symptom `SEO Title فارسی ... خالی برگشت`.

Two additional runtime issues were confirmed from the same trace/code path:
- full `/models` payloads were inserted into the Tk trace UI and could make Provider/Model changes look frozen,
- Stop Waiting/watchdog could leave Product Workspace busy state set until the old background worker returned, blocking immediate retry with another Provider/Model.

## Phase49.3I.11 Implemented Delta
New additive runtime:
`catalog_center/app/phase49_3i_schema_runtime_recovery.py`

Behavior:
- AvalAI/OpenRouter receive the actual JSON Schema using strict `json_schema` where compatible,
- exact schema/property names/types are also embedded in the provider instruction,
- bounded compatibility sequence: strict schema → `json_object` → no response format,
- provider output is validated against the exact schema before application,
- one repair request is allowed when the first syntactically valid JSON violates schema; a second schema failure becomes a precise visible error,
- explicit operator-selected model is used directly for the current request,
- model catalog is cached inside the request window and duplicate probes are avoided,
- `/models` trace is summarized as count + bounded sample rather than rendered in full,
- Stop Waiting/watchdog/stale abort releases Product Workspace busy/start/source flags immediately,
- the old network worker may finish in background but its stale result cannot mutate the product,
- 49.3I.10 scrollable sanitized request/response/error console remains,
- title-only watchdog remains 90 seconds; full AI watchdog remains 210 seconds,
- manual override, AI-owned refresh, source/SEO, Preview/Full Fetch and pricing contracts remain intact.

## GitHub Validation — 49.3I.11
Implementation PR: `#57` — MERGED after all required workflows succeeded.
Validated feature head: `9bdcfb3c7997cc9570d2d94e1bafd4f7bfad5651`.
Epic merge commit: `41d37d56437765119b9bb274037e9af7a5defbbe`.

Successful workflows:
- Phase49.3I Discovery Review Pricing CI — Run `32628666588` — SUCCESS.
- Phase49.3H SEO Cost Image Limit CI — Run `32628666600` — SUCCESS.
- Phase49.3G Workspace Usability CI — Run `32628666558` — SUCCESS.
- Phase49 Epic Unified CI / Full Django — Run `32628666582` — SUCCESS.

Validated:
- runner `49.3I.11` / ASCII-only Windows PowerShell 5.1 contract,
- live fetched GitHub snapshot guard,
- compile,
- exact owner malformed-response regression,
- strict schema delivery + one repair,
- model trace compaction,
- abort/watchdog busy-state release,
- title and full-AI stale-result safety,
- prior AI trace/refresh/manual override/source/SEO behavior,
- Preview/provider/Explorer/pricing regressions,
- Django check and no-migration contract,
- Windows Catalog Epic49 tests,
- Full Django suite.

## Database / Migration / Media / Secret Safety
- Django migration for 49.3I.11: `NONE` — CI verified.
- Catalog schema migration: `NONE`.
- no DB reset/drop/truncate.
- no historical data/media rewrite/delete.
- no credential storage change.
- Production DB/media/source untouched.

## Windows QA Required Now — Employee Release Gate
1. close Catalog Center completely,
2. require clean Local worktree,
3. live fetch/prune + ff-only pull current Epic,
4. run repository `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`,
5. verify Runner `49.3I.11` + `PHASE49_3I_GIT_SNAPSHOT=OK`,
6. retry the exact product/model that previously returned `seo_title`/`seo_description`,
7. confirm outgoing request shows the schema contract and final accepted response uses exact required keys/types,
8. if first provider output is malformed, verify at most one visible `structured_content_repair` request,
9. confirm `/models` trace is compact rather than a full huge catalog dump,
10. use Stop Waiting, immediately change Provider/Model and start a new request; old late output must not apply,
11. verify request/response/error tabs stay responsive and scrollable,
12. run bottom All-Fields AI once,
13. test low-image warning/refetch once,
14. test MakerWorld Preview → Approve → Full Fetch once,
15. verify Provider/model/FTP/Bridge credential persistence,
16. verify Product open/selection and Fixed/Range/Formula remain healthy.

If these pass, employees may use Catalog Center for controlled data entry. Production publishing remains separately gated.

## Local Publish / Production Gate
After Windows QA passes:
- exactly one `LOCAL PUBLISH ONLY`,
- Local Django E2E,
- verify title/SEO/images/pricing/source attribution in Local Store/Admin,
- explicit owner approval,
- then host read-only branch/path/commit verification, MySQL/database/backup/rollback verification, GitHub-only deploy and Production smoke/data checks.

## Payment Track
Phase30 ZarinPal remains mature for accepted Quote payments. Normal Store cart checkout is still manual bank-transfer only and still requires a narrow Storefront ZarinPal request/callback/verify integration + Sandbox E2E before any live payment activation.

## Exact Next Task
Windows must pull the current Epic using live ff-only GitHub snapshot semantics and run the repository-owned 49.3I.11 gate. Do not Local Publish, deploy Production, or enable live Store payments before this acceptance passes.
