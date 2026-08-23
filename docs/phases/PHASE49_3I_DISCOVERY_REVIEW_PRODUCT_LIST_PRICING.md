# Phase49.3I — Discovery Review + Product Explorer + Pricing + Observable AI

Updated: 2026-08-23
Branch: `epic/phase49-unified-product-slider-sync`
Current Hotfix: `49.3I.16 — Resilient Acquisition Fallback + Cached Candidate Reuse`
Status: `MERGED / ALL REQUIRED CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Goal
Deliver a business-usable Catalog Center that acquires products from exact source listing pages in bulk, survives individual browser/parser failures, stages local images, lets the operator select wanted products, prepares them in Product Workspace and publishes only after verified Local/Production gates.

## Canonical Acquisition Paths
1. Mature compatibility path: `Top Scan Controls → BaseApp start_scan/_scan_worker → Product Workspace`.
2. Primary exact-page path: `Exact Search/Listing URL → product/image limits → resilient discovery → resilient local image staging → review counts → Add selected to Products / Archive unwanted → Product Workspace`.

The exact-page bulk path does not depend on Rich Direct `extract_direct_link`.

## Preserved Contracts
- explicit listing URL authoritative,
- source `model_url_pattern` is Product-vs-Page boundary,
- dedupe by source + external id + normalized URL,
- Archive/Block prevents unwanted rediscovery without destructive deletion,
- Product Workspace remains canonical editor,
- AI/provider/schema/trace/manual override contracts unchanged,
- image hard max 20; product hard max 100,
- Fixed / Range / Formula remain independent,
- mature top scan actions remain available,
- Local Publish and Production remain separate gates.

## 49.3I.16 — Resilient Acquisition
### Trigger
Windows 49.3I.15 showed correct previously-discovered MakerWorld candidates but a new run aborted with `Locator.evaluate_all: SyntaxError: Invalid or unexpected token`. This is the ERR-49-024 embedded-JavaScript failure class at an older Preview boundary.

### Final Discovery Ladder
1. locator-safe Playwright without embedded `evaluate_all`,
2. public HTTP/HTML link extraction,
3. attached Chrome 9222 locator-safe discovery when available,
4. cached candidate DB reuse for the same source/listing URL.

### Final Image Ladder
1. locator-safe fresh browser,
2. public HTTP HTML + existing parser/downloader,
3. mature Classic DOM collector,
4. attached Chrome 9222 locator-safe path,
5. listing-card thumbnail fallback.

### Operational Rules
- each method failure is recorded and the next method is tried,
- previously successful candidate discovery is reusable instead of discarded,
- per-candidate manifest records discovery/acquisition trace and successful methods,
- at least one image must actually be staged locally before readiness/Add-to-Products,
- one candidate failure does not abort the rest,
- no Rich Direct dependency is reintroduced.

### Implementation Surfaces
- `catalog_center/app/phase49_3i16_resilient_acquisition.py`,
- `catalog_center/app/phase49_3i16_review_hardening.py`,
- runtime composition in `phase49_3i12_runtime_bridge.py`,
- `RUN_PHASE49_3I16_FALLBACK_GATE.ps1`,
- `.github/workflows/phase49-3i16-resilient-acquisition-ci.yml`,
- focused 49.3I.16 regression tests.

## GitHub Validation / Merge
PR `#62` merged.
- final PR head `8f4fbe6d0264f673d0e6564a4ed1e383db023ab6`,
- merge commit `44216546162fead0b752d92cf6cae8d658f034f2`.

SUCCESS:
- 49.3I.16 `32645660164`,
- 49.3I `32645660154`,
- 49.3I.15 `32645660045`,
- 49.3I.14 `32645660071`,
- 49.3H `32645660135`,
- 49.3G `32645660118`,
- Full Phase49 + Windows Catalog regressions + Full Django `32645660123`.

Django migration: NONE. Catalog schema migration: NONE. Production untouched.

## Focused Windows Acceptance — Current Gate
1. close Catalog Center; clean Local worktree,
2. live fetch/prune + ff-only pull current Epic,
3. run `RUN_PHASE49_3I16_FALLBACK_GATE.ps1 -LaunchApp`,
4. test MakerWorld `cake+stand` with 10 products × 10 images,
5. first-method failure must fall through instead of aborting,
6. if live listing methods fail, previously persisted candidates should be reused,
7. verify staged image counts,
8. select 2–3 ready rows → Add to Products without Direct Full Fetch,
9. Archive one unwanted row,
10. open one added Product and verify images.

## Release / Production Gate
After focused PASS: exactly one `LOCAL PUBLISH ONLY` → Local Store/Admin/Product/Media/SEO E2E → explicit owner approval → read-only Host path/branch/venv/MySQL/backup/rollback verification → GitHub-only Production deploy → HTTP/data/media verification.

## Next Phase
Normal Store checkout: ZarinPal request/callback/verify + Sandbox E2E while bank transfer remains available.
