# Phase49.3I — Discovery Review + Product Explorer + Pricing + Observable AI

Updated: 2026-08-23
Branch: `epic/phase49-unified-product-slider-sync`
Current Hotfix: `49.3I.14 — Mature Scan Restoration`
Status: `IMPLEMENTED / PR #60 OPEN / ALL REQUIRED CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Goal
Deliver a business-usable Catalog Center that preserves mature acquisition, adds lightweight Preview/Approve review, prepares Persian ecommerce/SEO data, supports explicit pricing/AI observability and publishes only through verified Local/Production gates.

## Canonical Acquisition Paths
Both paths are required and must coexist:

1. Mature acquisition path:
`Top Scan Controls → source/mode/method/URL/query → BaseApp start_scan/_scan_worker → Product Workspace`

2. New review path:
`Exact Search/Listing/Category URL → Preview Candidate → Approve/Archive → Approved Full Fetch → Product Workspace`

A new UI path must never hide, replace or silently rebind a healthy mature acquisition path.

## Preserved Core Contracts
- explicit Search/Listing/Category URL is authoritative,
- source `model_url_pattern` is Product-vs-Page boundary,
- Preview = one thumbnail + basic identity only,
- Full Fetch only after approval,
- image limit `1..20`, default `10`,
- Archive blocks rediscovery without Full Fetch,
- dedupe by source + external id + normalized URL,
- Product Workspace remains canonical detailed editor,
- AI/provider/schema/trace/manual-override contracts remain unchanged,
- Fixed / Range / Formula-Dynamic are independent,
- Local Publish and Production remain separate gates.

## 49.3I.14 — Mature Scan Controls + Single-Product Route Restoration

### Owner Evidence
Real Windows 49.3I.13 QA showed:
- the previous top acquisition area had lost working actions,
- `شروع اسکن`, `توقف محترمانه`, `دریافت هوشمند از لینک` and `کشف جدیدها` had been hidden,
- a correct MakerWorld Product URL passed into the new `دریافت محصول تکی` action failed with `RuntimeError: HTTP 403`,
- the owner confirmed the old top scan workflow was the working route before the new operator panel was added.

### Verified Root Cause — ERR-49-032
- 49.3I.12 explicitly hid healthy top buttons at the final UX87 boundary,
- the earlier Preview layer replaced `App87.start_scan` with Preview discovery, so just showing the old button would still call the wrong route,
- the new single-product action forced Rich Direct Intake / `RichPageExtractor`, which fails closed on MakerWorld HTTP 403/429,
- original BaseApp `start_scan` / `_scan_worker` still exists and is the mature path to restore.

### Corrected Contract
- restore the mature top action set,
- `شروع اسکن` binds to original BaseApp mature scan worker,
- new `دریافت محصول تکی` validates Product URL then sets `mode=single` and calls that same mature worker,
- Rich Direct `دریافت هوشمند از لینک` remains visible and optional,
- exact-page Preview/Approve/Archive/Paste/error-detail remains available,
- no new crawler/extractor,
- no unrelated UI or publishing behavior change.

## Runtime / Test Surface — 49.3I.14
Added:
- `catalog_center/app/phase49_3i14_legacy_scan_restore.py`,
- `catalog_center/tests/test_epic49_phase49_3i14_legacy_scan_restore.py`,
- `RUN_PHASE49_3I14_HOTFIX_GATE.ps1`,
- `.github/workflows/phase49-3i14-legacy-scan-restore-ci.yml`.

Changed:
- `catalog_center/app/phase49_3i12_runtime_bridge.py` to compose the additive recovery after 49.3I.13.

No Django migration and no Catalog schema migration.

## Implementation Test Incident
The initial resolver selected the first parent `start_scan`, which in a wrapper hierarchy could still be Preview. Targeted CI failed with `preview-started != legacy-started`. The command was not repeated unchanged. The resolver now selects the deepest project `start_scan` implementation in MRO; fresh CI passed.

## GitHub Validation — Current Feature Runtime
Feature runtime head: `bb6f456b50c1e12bbf6fc5c6b6cc3289f35ee6c8`.
PR: `#60` OPEN at documentation time.

Successful runs:
- Phase49.3I.14 Legacy Scan Restore `32636391530` — SUCCESS,
- Phase49.3I `32636391489` — SUCCESS,
- Phase49.3H `32636391571` — SUCCESS,
- Phase49.3G `32636391563` — SUCCESS,
- Full Phase49 + Full Django `32636391518` — SUCCESS.

Validation includes:
- mature BaseApp worker resolution,
- single-product mature routing,
- preserved legacy control labels,
- preservation of 49.3I.12/13 Preview/Paste behavior,
- compile,
- Windows PowerShell gate syntax/ASCII safety,
- Django no-migration contract,
- Windows Catalog Epic49 regression suite,
- Full Django suite.

## Database / Migration / Secret Safety
- Django migration: `NONE`,
- Catalog schema migration: `NONE`,
- no reset/drop/truncate,
- no candidate/history/media rewrite/delete,
- no credential changes,
- no FTP/Bridge/Production change.

## Focused Windows Acceptance Gate — NEXT
After PR merge:
1. Catalog Center closed; Local worktree clean,
2. live fetch/prune + ff-only pull current Epic,
3. run `RUN_PHASE49_3I14_HOTFIX_GATE.ps1 -LaunchApp`,
4. verify mature top acquisition actions are visible,
5. MakerWorld + `mode=single` + `method=auto` + known Product URL → `شروع اسکن` must use mature acquisition,
6. new `دریافت محصول تکی` must use the same mature route and must not force the Rich Direct HTTP-403 path,
7. exact-page Preview/Approve remains present.

This is intentionally a focused regression check. Do not repeat broad unrelated QA unless a focused failure appears.

## Local Publish / Production Gate
Immediately after focused Windows acceptance: exactly one `LOCAL PUBLISH ONLY` → Local Django Store/Admin E2E → verify title/SEO/source/images/pricing/visibility → explicit owner approval → verify Production branch/path/MySQL/backup/rollback → deploy approved GitHub snapshot.

## Next Phase After Acceptance
Normal Store cart checkout remains manual bank transfer. Next implementation is ZarinPal request/callback/verify + Sandbox E2E using mature Phase30 security semantics.
