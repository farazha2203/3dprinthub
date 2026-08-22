# Phase49.3H — SEO Execution Console + AI Cost Ledger + Controlled Image Acquisition

Status: IN_PROGRESS
Approved: 2026-08-22
Branch: `epic/phase49-unified-product-slider-sync`
Pre-phase baseline: `e052829c7ed34e931f52affecd7a3b74e33dc5a1`
Production: UNTOUCHED / NOT APPROVED

## Why
Operator needs transparent SEO execution, product-level AI/SEO cost accountability, and a strict controllable image intake limit. Current code has useful diagnostics and image limit plumbing but UI/behavior is fragmented and defaults are too high.

## Requested Delta

### A. SEO Execution Console
For every SEO/AI action reachable from Product Workspace/Task Center:
- open a small execution progress surface
- show deterministic steps: preflight, provider/model, connection, payload preparation, send, response, validation, apply, persist, cost/log finalization
- record runtime/audit events per step
- on success, close transient progress if appropriate and expose a persistent/reopenable result drawer/panel under the related section
- on partial result, result stays visible with remaining manual tasks
- on error, error/result surface remains visible with sanitized error, provider/model/request ID, log path/open-log action and retry guidance
- never expose API key/token/secret

### B. AI/SEO Cost Ledger
Use existing `ai_request_log` as request-level source of truth.
- aggregate per product: requests, prompt/completion/total tokens, known USD/IRT cost, unknown-cost request count
- request provider cost lookup only where an existing provider adapter supports it (AvalAI request ID lookup)
- no fabricated exchange rate or estimated cost unless explicitly marked as estimate and backed by configured data
- record a publish-time internal cost receipt/snapshot before Local/Production handoff
- receipt is operational/internal; it is not public product content

### C. Controlled Image Acquisition
Canonical limits:
- DEFAULT = 10
- HARD MAX = 20
- operator can choose 1..20 globally for scan/direct-link and per product for refetch
- cap applies to actual downloaded files AND persisted/selected image lists
- once product reaches limit, workflow continues to next product
- legacy rows/config above 20 normalize safely; no data deletion from existing historical product records solely because the cap changed

## Must Not Touch / Regress
- 49.3G vertical scroll, horizontal gallery, AI provenance/manual override
- Image SEO selected-only + text-only privacy: no image bytes/files/image URLs to AI
- Dynamic/fixed pricing contracts and Cart/Checkout price source
- Local vs Production publish separation
- Product/Hero revision and Bridge idempotency
- Persian content guard
- secure secret store/redaction
- historical media/catalog data

## Implementation Strategy
- Extend/Patch existing 49.3E Task Center and 49.3F diagnostics/provider layers.
- Add one reusable SEO execution/session/result abstraction; do not create separate implementations per button.
- Add cost aggregation/receipt helpers around existing `ai_request_log`.
- Add one image-limit normalizer shared by UI/refetch/extractor/persistence paths.
- Compose 49.3H only from `catalog_center/launch.py`; do not inject it into independent old installers.

## Database Safety
Expected Django migration: NONE.
Catalog SQLite may receive additive local-only structures/columns for result/receipt persistence if needed.
No reset/drop/truncate/delete.

## Tests / Acceptance
- execution step state machine success/partial/error
- sanitized error/result output; secrets absent
- request ID/provider/model/token/cost visible when known
- per-product cost aggregation with known + unknown cost
- AvalAI lookup update path
- publish receipt is frozen/internal and does not alter public product fields
- image limit normalizes 0/10/20/60/100 correctly into 1..20
- 100 candidate images fixture with limit 10 -> 10 persisted/selected/downloaded max
- limit 20 -> 20 max
- batch/multi-product workflow continues after one product reaches limit
- selected-image AI privacy regression
- 49.3G provenance/manual override regression
- launcher markers
- Full Phase49 regression
- Full Django suite

## Delivery Gate
GitHub implementation -> CI -> Windows `git pull --ff-only` -> Phase49.3H Local runner -> automated Local PASS -> Manual result/error/cost/image-limit QA -> one LOCAL PUBLISH ONLY -> Local Django E2E -> explicit owner approval -> Production plan.
