# Phase49.3I — Discovery Review + Product Explorer + Pricing + Observable AI

Updated: 2026-08-23
Branch: `epic/phase49-unified-product-slider-sync`
Current Hotfix: `49.3I.17 — Single Active AI Runtime`
Status: `MERGED / ALL REQUIRED CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Goal
Deliver a business-usable Catalog Center that can bulk-acquire products from exact listing pages, survive source/browser method failures, edit products with deterministic AI, publish locally for E2E verification, then deploy only an approved GitHub snapshot.

## Canonical Acquisition Paths — Preserved
1. Mature compatibility path: `Top Scan Controls → BaseApp start_scan/_scan_worker → Product Workspace`.
2. Primary exact-page path: `Exact Search/Listing URL → product/image limits → resilient discovery → resilient local image staging → review counts → Add selected to Products / Archive unwanted → Product Workspace`.

49.3I.16 remains authoritative for acquisition:
- discovery: locator-safe → HTTP/HTML → attached Chrome 9222 → cached candidate DB,
- images: locator-safe → HTTP → mature Classic DOM → Chrome 9222 → listing thumbnail,
- product max 100 / image max 20,
- one candidate failure does not abort the batch,
- local image staging required,
- no Rich Direct `extract_direct_link` dependency in exact-page bulk intake.

## Product Workspace AI Contract — 49.3I.17
### Trigger
Windows evidence showed AI progress stuck at `در حال اتصال به هوش مصنوعی`, apparent large model/provider activity despite one saved active AI, occasional Task Manager termination, and stale `invalid command name ...listbox` Tk failures.

### Verified causes
- legacy provider resolver could treat saved OpenRouter/Google as non-explicit and fall back to AvalAI/OpenAI based on available credentials,
- Product AI ran a model-catalog probe before the useful request,
- Google could list models again,
- Product open could trigger hidden AI automatically,
- stale destroyed-widget callbacks could surface as fatal UI errors.

### Final Runtime Rule
- operator selects Provider/Model in AI Center and saves it,
- Product AI uses only saved `ai_provider` + that provider's saved model,
- API key comes only from that provider's secure secret slot,
- cross-provider fallback is forbidden,
- unsaved/`auto` runtime fails closed,
- Product open starts no AI request,
- normal Product AI skips `/models` preflight and sends the useful request directly,
- Google exact saved model skips its model-list preflight too,
- explicit AI Settings Model Search/Test remains live,
- stale destroyed-widget callbacks are suppressed/logged and busy state released,
- existing request/response/error trace, schema validation + one repair, 90s title watchdog, 210s All-Fields watchdog, Stop Waiting, stale-result protection and manual overrides remain.

### Implementation Surfaces
- `catalog_center/app/phase49_3i17_single_active_ai_runtime.py`,
- final composition in `catalog_center/app/phase49_3i_local_qa_hotfix.py`,
- `RUN_PHASE49_3I17_SINGLE_AI_GATE.ps1`,
- `.github/workflows/phase49-3i17-single-active-ai-ci.yml`,
- focused 49.3I.17 regression tests.

## GitHub Validation / Merge
PR `#63` merged.
- final runtime head `2917a3db5225abac71fc3e80b64ad439acd7a4d0`,
- merge commit `7f835f573b92e3aded6275c9421770c0c47d947a`.

SUCCESS:
- 49.3I.17 `32649623837`,
- 49.3I `32649623808`,
- 49.3I.16 `32649623695`,
- 49.3I.15 `32649623705`,
- 49.3I.14 `32649623679`,
- 49.3H `32649623825`,
- 49.3G `32649623755`,
- Full Phase49 + Windows Catalog regressions + Full Django `32649623804`.

Django migration: NONE. Catalog schema migration: NONE. Production untouched.

## Focused Windows Acceptance — Current Gate
1. close Catalog Center; clean Local worktree,
2. live fetch/prune + ff-only pull current Epic,
3. run `RUN_PHASE49_3I17_SINGLE_AI_GATE.ps1 -LaunchApp`,
4. select/save one active Provider/Model,
5. open Product Workspace and confirm no hidden AI request starts,
6. run All-Fields once and verify trace contains only that Provider/Model and no leading `/models` request,
7. Stop/failure must leave app responsive and no stale Listbox fatal popup,
8. save a different Provider/Model and repeat once; only the newly saved pair may be used.

After AI PASS, verify the already-focused exact-page acquisition if needed, then exactly one Local Publish E2E.

## Release / Production Gate
Focused Windows PASS → exactly one `LOCAL PUBLISH ONLY` → Local Store/Admin/Product/Media/SEO E2E → explicit owner approval → read-only Host path/branch/venv/MySQL/backup/rollback verification → GitHub-only Production deploy → HTTP/data/media verification.

## Next Phase
Normal Store checkout: ZarinPal request/callback/verify + Sandbox E2E while bank transfer remains available.
