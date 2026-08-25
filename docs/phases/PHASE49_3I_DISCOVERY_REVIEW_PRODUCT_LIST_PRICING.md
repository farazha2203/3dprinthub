# Phase49.3I — Discovery Review + Product Explorer + Pricing + Observable AI

Updated: 2026-08-25
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Hotfix: `49.3I.24 — Runtime Observability + AvalAI URL Tools + Startup No-Network Guard`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA REQUIRED`
Production: `UNTOUCHED / NOT APPROVED`

## Goal
Deliver a business-usable Catalog Center that bulk-acquires exact products, preserves real source identity, keeps the UI responsive during AI work, exposes deterministic diagnostics from startup through close, can rebuild editorial data from one authoritative product link, then publishes only after Local acceptance.

## Preserved Acquisition Contract
49.3I.16 remains authoritative:
- discovery: locator-safe → HTTP/HTML → attached Chrome 9222 → cached candidate DB,
- images: locator-safe → HTTP → mature Classic DOM → Chrome 9222 → listing thumbnail,
- product max 100 / image max 20,
- one candidate failure does not abort batch,
- local image staging required,
- no Rich Direct dependency in bulk intake.

## Source Identity Contract — 49.3I.19 Preserved
- generic model-number placeholders are not authoritative,
- valid scraped/page title wins,
- MakerWorld exact model URL slug is deterministic fallback,
- candidate and Product persistence are canonicalized,
- legacy Product AI context is canonicalized,
- existing products can repair source identity without delete/reimport.

Acceptance examples:
- `2845731-cake-stand` → `Cake Stand`,
- `2896217-ribbed-cake-stand-cookie-platter` → `Ribbed Cake Stand Cookie Platter`.

## Operator/UI Contract — 49.3I.18 + 49.3I.20 Preserved
- global editable-widget clipboard support,
- bulk image SEO filename / Alt / Title / Caption operations,
- operator-authoritative Persian title replacement,
- full AI rebuild for confirmed identity,
- Stage 3/4 operator panels remain visible above expandable gallery/editor content.

## Product AI Identity Contract — 49.3I.17 Preserved
- one saved Provider + Model,
- secure key only for that Provider,
- no provider fallback scanning,
- no hidden AI-on-open,
- no Product `/models` preflight,
- explicit Settings model search/test remain available.

## Observable AI + Tk Safety — 49.3I.21/22 Preserved
- bounded provider wait and visible request stages,
- cancellation ignores late result,
- Product AI workers do not mutate Tk directly,
- Tk-backed source state is snapshotted before worker work,
- right Product rail has vertical scrolling.

## Phase49.3I.24 — Current Runtime Contract
### Verified owner evidence
The latest diagnostic and screenshots show:
- AvalAI Product request can fail before HTTP with `audit_event() got an unexpected keyword argument 'provider'`,
- startup can perform hidden `/models` requests immediately after `app_start`,
- a wrong Provider key can therefore be probed against another Provider during startup noise,
- `google/lyria-3-pro-preview` can return HTTP 200 but cannot satisfy Product JSON content,
- successful AvalAI Product calls can take tens of seconds,
- `num_sources_used=0` proves a bare URL in normal chat is not equivalent to browsing the source page.

### Request rules
- app-side exact-page fetch/sanitize is the deterministic evidence path,
- exact saved Provider/Model remains authoritative,
- AvalAI Product output prefers strict `json_schema`, then bounded compatibility fallback,
- sparse source context may use explicit supported AvalAI URL tools:
  - supported Gemini routes use `urlContext`,
  - GPT-5 routes use Responses `web_search`,
  - any unsupported/error tool path falls back to app-fetched facts without Provider/Model switching,
- obvious non-text model families are hidden/rejected for Product editorial structured generation.

### Startup/performance rules
- application construction must not launch Provider model-catalog network requests,
- model search is explicit and available after first Tk idle,
- runtime session logging begins before wrapped App construction,
- Tk heartbeat records meaningful recovered lag,
- >8s heartbeat stall produces an all-thread `faulthandler` dump from a non-Tk watchdog,
- Dashboard exposes Program Log, AI Log, safe diagnostic export and log folder,
- safe export includes redacted runtime/main/hang-log tails.

### AvalAI Free-label rule
Absence/zero of generic pricing metadata is not sufficient proof that every AvalAI model is free. The Product UI only marks a model Free when its routed ID explicitly denotes a free route.

## Implementation Surfaces
- `catalog_center/app/phase49_3i21_observable_ai_link_refresh.py`
- `catalog_center/app/phase49_3i22_tk_thread_bridge.py`
- `catalog_center/app/phase49_3i23_avalai_chat_contract.py`
- `catalog_center/app/phase49_3i24_runtime_observability.py`
- `catalog_center/app/phase49_3i12_runtime_bridge.py`
- `catalog_center/tests/test_phase49_3i23_avalai_chat_contract.py`
- `catalog_center/tests/test_phase49_3i24_runtime_observability.py`
- `docs/phases/PHASE49_3I24_RUNTIME_OBSERVABILITY_AVALAI_URL_TOOLS.md`
- previous 49.3I.20/19/18/17/16 surfaces preserved.

## Database / Migration
Django migration: NONE.
Catalog schema migration: NONE.
Existing diagnostic tables are reused.
Production untouched.

## Focused Windows Acceptance — Current Gate
1. close Catalog Center; verify no project process remains,
2. clean Local worktree and ff-only pull live feature HEAD,
3. verify Local HEAD == fetched remote HEAD,
4. compile 49.3I.24/23 + inherited AI/Tk composition modules,
5. run focused 49.3I.24/23 tests plus inherited 49.3I.22/21/20/19/18 regressions,
6. run `catalog_center/launch.py --verify-only`,
7. launch Catalog Center and confirm Dashboard diagnostic card is visible,
8. inspect logs: no automatic Provider `/models` HTTP should occur during startup,
9. explicitly use model search and confirm live Provider model discovery still works,
10. confirm Product model picker cannot select Lyria/obvious non-text routes,
11. open product `2896217`, run `تکمیل همه اطلاعات بر اساس لینک محصول`,
12. confirm source fetch → optional explicit AvalAI URL evidence/fallback → structured request → preview/apply,
13. confirm no `audit_event provider` crash and no Product `/models` preflight,
14. verify Persian title/content/SEO/image metadata align to the real product,
15. if UI becomes unresponsive long enough, verify hang dump is persisted and included in safe diagnostic export,
16. close/reopen normally and confirm lifecycle logging persists.

## Release / Production Gate
Windows PASS → exactly one `LOCAL PUBLISH ONLY` → Local Store/Admin/Product/Media/SEO E2E → explicit owner approval → read-only Host path/branch/venv/MySQL/backup/rollback verification → deploy approved GitHub snapshot only → Production HTTP/data/media verification.

## Next Phase
After Catalog Production verification: ZarinPal request/callback/verify + Sandbox E2E while bank transfer remains available.
