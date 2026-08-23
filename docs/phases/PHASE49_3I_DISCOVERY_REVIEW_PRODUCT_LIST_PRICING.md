# Phase49.3I — Discovery Review + Product Explorer + Pricing + Observable AI

Updated: 2026-08-23
Branch: `epic/phase49-unified-product-slider-sync`
Current Hotfix: `49.3I.12`
Status: `PR MERGED / FINAL CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Goal
Provide a business-usable Catalog Center flow that discovers source products cheaply, previews before full acquisition, prepares Persian ecommerce/SEO content, supports explicit pricing, exposes AI/discovery execution state, protects manual edits and publishes only through verified Local/Production gates.

## Canonical State Machine
`Exact Search/Listing/Category URL → Preview Candidate → Approve/Archive → Approved Full Fetch → Product Workspace → LOCAL PUBLISH ONLY → Local Django E2E → Owner Approval → Production`

Direct Product URL is a separate mature intake path and must not be confused with Search/Listing/Category Preview.

## Preserved Core Contracts
- explicit operator Search/Listing/Category URL is authoritative,
- source `model_url_pattern` is Product-vs-Page boundary,
- Preview contains only identity/basic title/source URL/one thumbnail,
- Full Fetch only after approval,
- image limit `1..20`, default `10`,
- Archive blocks rediscovery without Full Fetch,
- dedupe by source + external id + normalized URL,
- Provider secrets remain in Windows Credential Store/environment,
- All-Fields AI uses mature Task Center,
- 90s title / 210s full-AI watchdogs,
- exact provider schema validation + one repair,
- stale/cancelled late AI result cannot mutate product,
- Product Workspace remains canonical detailed editor,
- Fixed / Range / Formula-Dynamic remain independent; Range never invokes Formula.

## 49.3I.12 — Observable Exact-Page Discovery + Single-Product Intake + Workspace Image Fit

### Owner Evidence
Windows screenshot/log showed:
- `PHASE49_3I_PREVIEW_TARGET=https://makerworld.com/en/search/models?keyword=cake+stand`,
- `candidates=20`,
- `failed=0`,
- `full_fetch=0`.

So exact-page backend discovery was working. The remaining failure was operator visibility/composition: candidate review/live run state was not clearly mounted on final UX87, direct Product URL intake was not separated as an explicit action, and Product Workspace image fitting still looked wrong.

### Corrected Contract
- mount operator controls at final UX87 `_ui` boundary,
- separate `کشف لینک‌های همین صفحه` from `دریافت محصول تکی`,
- classify direct Product URL from configured source regex rather than guessed shape,
- visible live badge/progress/elapsed/current URL/detail,
- explicit visible Stop request state,
- mature candidate thumbnail/status/title/source/external/url renderer reused,
- no duplicate crawler/extractor,
- Preview remains no-Full-Fetch until approval,
- Product Workspace cards use fixed `228x171` pixel `ImageOps.contain` letterbox fitting,
- no crop/stretch and no text-unit image Label sizing.

## Runtime / Test Surface — 49.3I.12
Added:
- `catalog_center/app/phase49_3i12_discovery_image_recovery.py`,
- `catalog_center/app/phase49_3i12_runtime_bridge.py`,
- `catalog_center/tests/test_epic49_phase49_3i12_discovery_image_recovery.py`.

Changed:
- `catalog_center/app/phase49_3i_pricing_modes.py`,
- `RUN_PHASE49_3I_LOCAL_GATE.ps1` → v`49.3I.12`,
- `.github/workflows/phase49-3i-ci.yml`.

No Django migration and no Catalog schema migration.

## Final GitHub Validation — 49.3I.12
Implementation PR `#58`: MERGED.
Validated feature head: `2a9442055d33777f675ccd3ebe11de8419bfb2b3`.
Epic merge commit: `24d5b8fdddb97fbcc4c07efa7d6f1d78a0ffb225`.

Successful runs:
- Phase49.3I `32631604990` — SUCCESS,
- Phase49.3H `32631604930` — SUCCESS,
- Phase49.3G `32631604945` — SUCCESS,
- Full Phase49 + Full Django `32631604928` — SUCCESS.

Validation includes runner/ASCII/live-Git guard, exact-page/product URL classification, UX87 final composition, candidate Treeview compatibility, live status markers, stop feedback markers, 228x171 contain image contract, prior AI/provider/Preview/pricing regressions, Django no-migration contract, Windows Catalog tests and Full Django suite.

## Database / Migration / Secret Safety
- Django migration: `NONE`,
- Catalog schema migration: `NONE`,
- no reset/drop/truncate,
- no historical data/media rewrite,
- no credential storage change,
- Production untouched.

## Employee Release Acceptance Gate — NEXT
1. Catalog Center closed; Local worktree clean,
2. live fetch/prune + ff-only pull current Epic,
3. run `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`,
4. verify runner `49.3I.12` + Git snapshot marker,
5. exact MakerWorld `cake+stand` Search URL → exact-page discovery,
6. verify live badge/progress/elapsed/current URL,
7. verify candidate links appear in review panel before Full Fetch,
8. approve one candidate → Full Fetch,
9. direct Product URL → separate single-product action,
10. verify Stop feedback,
11. verify landscape/portrait Product Workspace image cards are equal 228x171 contain-fit,
12. regression-check All-Fields AI / Provider-model / image limit / Fixed-Range-Formula.

If these pass, employees may begin controlled Catalog data entry.

## Local Publish / Production Gate
After Windows acceptance: exactly one `LOCAL PUBLISH ONLY` → Local Django E2E → verify title/SEO/source/images/pricing/visibility → explicit owner acceptance. Only then verify host branch/path/MySQL/backup/rollback and deploy the approved GitHub snapshot.

## Next Phase After Acceptance
Normal Store cart checkout remains manual bank transfer. The next implementation phase is ZarinPal Store checkout request/callback/verify + Sandbox E2E, preserving manual bank transfer and Phase30 security semantics.
