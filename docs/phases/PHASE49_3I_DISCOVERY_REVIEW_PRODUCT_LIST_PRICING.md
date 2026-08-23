# Phase49.3I — Discovery Review + Product Explorer + Pricing + Observable AI

Updated: 2026-08-23
Branch: `epic/phase49-unified-product-slider-sync`
Current Hotfix: `49.3I.13`
Status: `PR MERGED / FINAL CI SUCCESS / WINDOWS RERUN PENDING`
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

## 49.3I.13 — Windows URL Paste + Approved Batch Full-Fetch Recovery

### Owner Evidence
Real Windows 49.3I.12 QA showed:
- exact MakerWorld candidate images/titles/IDs/URLs are visible and correct,
- URL input could not be pasted reliably and required typing,
- selecting multiple candidates then approved Full Fetch opened/closed roughly one browser window per selected candidate,
- some candidate statuses became `failed`, but the exact stored reason was not directly visible.

### Verified Root Cause — ERR-49-031
- exact URL field was a plain `ttk.Entry` without explicit Windows paste handlers,
- approved batch invokes the mature RichPageExtractor per candidate and inherited `direct_link.headed=true`, producing one visible persistent browser context per selected row,
- candidate `last_error` already existed but was not exposed in the final operator UI.

### Corrected Contract
- Ctrl+V, Ctrl+V uppercase, Shift+Insert, right-click Paste and visible Paste Link button,
- preserve pasted query parameters exactly,
- approved batch only temporarily forces the existing RichPageExtractor to background/headless mode,
- restore original direct-link headed setting after completion/cancel/error,
- direct single-product intake retains configured headed behavior,
- Candidate Error Detail exposes persisted `last_error`,
- no duplicate crawler/extractor,
- Preview/Approve/Archive/dedupe semantics unchanged.

## Runtime / Test Surface — 49.3I.13
Added:
- `catalog_center/app/phase49_3i13_batch_fetch_paste_recovery.py`,
- `catalog_center/tests/test_epic49_phase49_3i13_batch_fetch_paste_recovery.py`.

Changed:
- `catalog_center/app/phase49_3i12_runtime_bridge.py`,
- `RUN_PHASE49_3I_LOCAL_GATE.ps1` → v`49.3I.13`,
- `.github/workflows/phase49-3i-ci.yml`.

No Django migration and no Catalog schema migration.

## Final GitHub Validation — 49.3I.13
Implementation PR `#59`: MERGED.
Validated feature head: `b47793c42d807285efbd8d3e005f9979856c4878`.
Epic merge commit: `3ad097fb3c5ccd2aed82b2dab38f3c8951e00e51`.

Successful runs:
- Phase49.3I `32633932308` — SUCCESS,
- Phase49.3H `32633932302` — SUCCESS,
- Phase49.3G `32633932340` — SUCCESS,
- Full Phase49 + Full Django `32633932224` — SUCCESS.

Validation includes runner/ASCII/live-Git guard, clipboard query preservation, approved-batch background browser policy and restoration, runtime bridge wiring, no new crawler/extractor, prior Preview/AI/provider/image/pricing regressions, Django no-migration contract, Windows Catalog tests and Full Django suite.

## Database / Migration / Secret Safety
- Django migration: `NONE`,
- Catalog schema migration: `NONE`,
- no reset/drop/truncate,
- no candidate/history/media rewrite,
- no credential storage change,
- Production untouched.

## Employee Release Acceptance Gate — NEXT
1. Catalog Center closed; Local worktree clean,
2. live fetch/prune + ff-only pull current Epic,
3. run `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`,
4. verify runner `49.3I.13` + Git snapshot marker,
5. verify Ctrl+V / Shift+Insert / right-click / Paste Link,
6. exact MakerWorld `cake+stand` page → Preview,
7. select 2+ candidates → approved Full Fetch with no visible browser window per product,
8. if any candidate fails use Candidate Error Detail and capture exact stored reason,
9. direct Product URL → separate single-product action,
10. verify Stop/live state, image cards, AI/provider/model/image-limit/Fixed-Range-Formula regressions.

If these pass, employees may begin controlled Catalog data entry.

## Local Publish / Production Gate
After Windows acceptance: exactly one `LOCAL PUBLISH ONLY` → Local Django E2E → verify title/SEO/source/images/pricing/visibility → explicit owner acceptance. Only then verify host branch/path/MySQL/backup/rollback and deploy the approved GitHub snapshot.

## Next Phase After Acceptance
Normal Store cart checkout remains manual bank transfer. Next implementation is ZarinPal Store checkout request/callback/verify + Sandbox E2E, preserving bank transfer and mature Phase30 security semantics.
