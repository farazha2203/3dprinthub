# Phase49.3I — Discovery Review + Product Explorer + Pricing + Observable AI

Updated: 2026-08-25
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Hotfix: `49.3I.21 — Observable AI Jobs + Link-Grounded Full Refresh`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA REQUIRED`
Production: `UNTOUCHED / NOT APPROVED`

## Goal
Deliver a business-usable Catalog Center that bulk-acquires exact products, preserves real source identity, keeps the UI responsive during AI work, exposes deterministic diagnostics, can rebuild all editorial data from one authoritative product link, then publishes only after Local acceptance.

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

## Observable AI Runtime — 49.3I.21
### Trigger
Windows QA showed multiple AI commands could remain at `در حال اتصال به هوش مصنوعی`. The source-title refresh itself succeeded, but combined source repair + AI rebuild and other generation paths could wait until the visible 03:30 ceiling.

### Verified cause
The provider chat generation path used a 210-second timeout, exactly matching 03:30. Existing generation workers were already threaded; the key failure was long provider waiting plus insufficient start-stage observability, not product field-write permissions.

### Runtime rule
- all AI POST requests pass through a bounded provider guard,
- default request ceiling is 75 seconds; `CATALOG_AI_TIMEOUT_SECONDS` may set 20..120 seconds,
- request-start is persisted before network wait,
- finish/error/timeout persists Provider/Model/operation/duration through the existing redacted diagnostics layer,
- late/cancelled link-refresh results never apply to the Product,
- cancel releases the local busy state,
- no API key/token is exported to diagnostics.

## Link-Grounded Full Refresh — 49.3I.21
New Stage 4 action: `🌐 تکمیل همه اطلاعات بر اساس لینک محصول`.

Flow:
1. read the exact Product `source_url`,
2. fetch and parse the actual source page using the mature crawler,
3. derive canonical source title,
4. build sanitized source facts,
5. send URL + source facts + selected images/materials/colors to AI,
6. show received preview,
7. require explicit operator confirmation,
8. use the mature 49.3I.18 apply path to update Persian title, descriptions, SEO, keywords and image metadata,
9. preserve source URL, price, stock and commercial/operator choices.

The job dialog shows elapsed time and live stages and provides `توقف انتظار` and sanitized report copy. Diagnostics bundle export is available directly from the same panel.

## Implementation Surfaces
- `catalog_center/app/phase49_3i21_observable_ai_link_refresh.py`
- `catalog_center/app/phase49_3i21_cancel_guard.py`
- `catalog_center/app/phase49_3i_pricing_modes.py`
- `catalog_center/tests/test_phase49_3i21_observable_ai_link_refresh.py`
- `docs/phases/PHASE49_3I21_OBSERVABLE_AI_LINK_REFRESH.md`
- previous 49.3I.20/19/18/17/16 surfaces preserved.

## Database / Migration
Django migration: NONE.
Catalog schema migration: NONE.
Existing diagnostic tables are reused.
Production untouched.

## Focused Windows Acceptance — Current Gate
1. clean Local worktree and ff-only pull live feature HEAD,
2. verify Local HEAD == fetched remote HEAD,
3. compile 49.3I.21 + 49.3I.20/19/18 composition modules,
4. run 49.3I.21/20/19/18 tests plus inherited 49.3I.16/15/discovery tests,
5. run `catalog_center/launch.py --verify-only`,
6. launch Catalog Center and confirm new AI panel is visible in Stage 4,
7. open product `2896217`,
8. run link-grounded full refresh and observe source fetch → AI request → received preview → apply,
9. verify Persian identity no longer stays `مدل میکرورلد 2896217`,
10. verify descriptions/SEO/image Alt/Title/Caption align to the same real product,
11. cancel a waiting request and verify a late result is not applied and another AI action can be started,
12. export Diagnostics and verify no API key/token appears,
13. retest existing All-Fields/source-rebuild/image-SEO AI actions and verify responsive UI + useful failure stage,
14. chain the existing 49.3I.17 and acquisition baseline gates.

## Release / Production Gate
Windows PASS → exactly one `LOCAL PUBLISH ONLY` → Local Store/Admin/Product/Media/SEO E2E → explicit owner approval → read-only Host path/branch/venv/MySQL/backup/rollback verification → deploy approved GitHub snapshot only → Production HTTP/data/media verification.

## Next Phase
After Catalog Production verification: ZarinPal request/callback/verify + Sandbox E2E while bank transfer remains available.