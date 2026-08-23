# Phase49.3I — Discovery Review + Product Explorer + Pricing + Observable AI

Updated: 2026-08-23
Branch: `epic/phase49-unified-product-slider-sync`
Current Hotfix: `49.3I.14 — Mature Scan Restoration`
Status: `PR #60 MERGED / ALL REQUIRED CI SUCCESS / FOCUSED WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Goal
Deliver a business-usable Catalog Center that preserves mature acquisition, adds lightweight Preview/Approve review, prepares Persian ecommerce/SEO data, supports explicit pricing/AI observability and publishes only through verified Local/Production gates.

## Canonical Acquisition Paths
Both paths are required and must coexist.

1. Mature acquisition:
`Top Source/Mode/Method/URL/Query → شروع اسکن → BaseApp start_scan/_scan_worker → Product Workspace`

2. Review acquisition:
`Exact Search/Listing/Category URL → Preview Candidate → Approve/Archive → Approved Full Fetch → Product Workspace`

A new UI path must never hide, replace or silently rebind a healthy mature acquisition path.

## Preserved Core Contracts
- explicit Search/Listing/Category URL authoritative,
- source `model_url_pattern` is Product-vs-Page boundary,
- Preview = one thumbnail + basic identity only,
- Full Fetch only after approval,
- image limit `1..20`, default `10`,
- Archive blocks rediscovery without Full Fetch,
- dedupe by source + external id + normalized URL,
- Product Workspace remains canonical editor,
- AI/provider/schema/trace/manual-override contracts unchanged,
- Fixed / Range / Formula-Dynamic independent,
- Local Publish and Production remain separate gates.

## 49.3I.14 — Mature Scan Controls + Single-Product Route Restoration
Owner Windows QA after 49.3I.13 showed that mature top acquisition controls were hidden and the new manual single-product action forced Rich Direct Intake, causing a correct MakerWorld Product URL to fail with `RuntimeError: HTTP 403`.

Canonical root cause: `ERR-49-032`.

Corrected contract:
- restore mature top actions,
- `شروع اسکن` binds to original BaseApp mature worker,
- manual `دریافت محصول تکی` validates Product URL then sets `mode=single` and calls the same mature worker,
- Rich Direct `دریافت هوشمند از لینک` remains optional,
- exact-page Preview/Approve/Archive/Paste/error-detail remains,
- no new crawler/extractor or unrelated behavior change.

## Runtime / Test Surface
Added:
- `catalog_center/app/phase49_3i14_legacy_scan_restore.py`,
- `catalog_center/tests/test_epic49_phase49_3i14_legacy_scan_restore.py`,
- `RUN_PHASE49_3I14_HOTFIX_GATE.ps1`,
- `.github/workflows/phase49-3i14-legacy-scan-restore-ci.yml`.

Changed:
- `catalog_center/app/phase49_3i12_runtime_bridge.py` to compose the additive recovery after 49.3I.13.

No Django migration and no Catalog schema migration.

## Validation
Initial targeted CI correctly found an MRO resolver defect and failed. The resolver changed before fresh CI.

Final PR head: `f12a25e1fe50fb16a03a1324c84912c830a2608e`.
Merge commit: `124662cf2436dfcce245282b01b2da694802aa55`.
PR #60: MERGED.

Successful final PR-head runs:
- Phase49.3I.14 Legacy Scan Restore `32636771174` — SUCCESS,
- Phase49.3I `32636771071` — SUCCESS,
- Phase49.3H `32636771154` — SUCCESS,
- Phase49.3G `32636771049` — SUCCESS,
- Full Phase49 + Full Django `32636771103` — SUCCESS.

## Safety
- Django migration: NONE,
- Catalog schema migration: NONE,
- no reset/drop/truncate,
- no candidate/history/media rewrite/delete,
- no credential changes,
- no FTP/Bridge/Production change.

## Focused Windows Acceptance Gate — NEXT
1. Catalog Center closed; Local worktree clean,
2. live fetch/prune + ff-only pull current Epic,
3. run `RUN_PHASE49_3I14_HOTFIX_GATE.ps1 -LaunchApp`,
4. verify mature top acquisition actions are visible,
5. MakerWorld + `mode=single` + `method=auto` + known Product URL → `شروع اسکن` uses mature acquisition,
6. manual `دریافت محصول تکی` uses the same mature route and does not force Rich Direct 403,
7. exact-page Preview/Approve remains present.

Do not repeat broad unrelated QA unless this focused gate fails.

## Local Publish / Production Gate
Immediately after focused Windows acceptance: exactly one `LOCAL PUBLISH ONLY` → Local Django Store/Admin E2E → verify title/SEO/source/images/pricing/visibility → explicit owner approval → verify Production branch/path/MySQL/backup/rollback → deploy approved GitHub snapshot.

## Next Phase After Acceptance
Normal Store cart checkout remains manual bank transfer. Next implementation is ZarinPal request/callback/verify + Sandbox E2E using mature Phase30 security semantics.
