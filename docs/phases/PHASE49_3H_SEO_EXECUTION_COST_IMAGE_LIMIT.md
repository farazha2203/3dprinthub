# Phase49.3H — SEO Execution Console + AI Cost Ledger + Controlled Image Acquisition

Status: GITHUB_UPDATED
Approved: 2026-08-22
Branch: `epic/phase49-unified-product-slider-sync`
Pre-phase baseline: `e052829c7ed34e931f52affecd7a3b74e33dc5a1`
Validated Epic HEAD: `e145d1e11619e36bd766788083bee59899a80cbb`
Production: UNTOUCHED / NOT APPROVED

## Implemented

### A. SEO Execution Console
For SEO/AI actions reachable from Product Workspace/Task Center:
- visible execution progress and deterministic step log
- provider/model/request/token/cost information where available
- persistent/reopenable result/error drawer
- retry/open-log guidance
- sanitized errors; no API key/token/secret exposure

### B. AI/SEO Cost Ledger
Existing `ai_request_log` remains request-level source of truth.
- aggregate per product: requests, prompt/completion/total tokens, known USD/IRT cost, unknown-cost request count
- provider cost lookup only where supported by verified adapter
- no fabricated exchange rate/cost
- internal publish-time cost receipt/snapshot

### C. Controlled Image Acquisition
Canonical limits:
- DEFAULT = 10
- HARD MAX = 20
- operator-selectable 1..20
- cap applies to downloaded files and persisted/selected image lists
- one product reaching cap does not stop following products
- historical rows are not destructively rewritten just because cap changed

## Must Not Regress
- 49.3G vertical scroll, horizontal gallery, AI provenance/manual override
- Image SEO selected-only + text-only privacy: no image bytes/files/image URLs to AI
- Dynamic/fixed pricing contracts and Cart/Checkout price source
- Local vs Production publish separation
- Product/Hero revision and Bridge idempotency
- Persian content guard
- secure secret store/redaction
- historical media/catalog data

## Database Safety
Django migration: NONE.
Catalog SQLite changes are local-only/additive.
No reset/drop/truncate/delete.

## Final GitHub Validation
Validation probe PR #40 was CI-only and must not be merged.
All final workflows on the validated runtime passed:
- Phase49.3H SEO Cost Image Limit CI — Run `32565773426` — SUCCESS
- Phase49.3G Workspace Usability regression — Run `32565773459` — SUCCESS
- Phase49 Epic Unified CI — Run `32565773433` — SUCCESS

Earlier CI probe lessons:
- PR #38 exposed an incorrect test assumption about `Database.upsert_product()` return value; fixture corrected to resolve the real DB row identity.
- PR #39 exposed an assertion coupled to exact redaction formatting; runtime was already safe and test was corrected to assert leak absence/masked Authorization.
- both earlier probe PRs were closed without merge.

## Remaining Acceptance Gate
Phase49.3H is NOT `LOCAL_TESTED` or `ACCEPTED` yet.
Still required:
1. Windows pulls GitHub-approved head (now Phase49.3I will supersede the standalone 3H Windows delivery).
2. repository Local Gate passes.
3. manual result/error/cost/image-limit QA.
4. one LOCAL PUBLISH ONLY + Local Django E2E.
5. explicit owner approval.
6. only then Production planning/deploy.

## Next Phase
Phase49.3I extends the same Epic with exact discovery review, lightweight product list and explicit Fixed/Range/Formula pricing while preserving every 49.3H contract.
