# CURRENT PROJECT STATE

Last Updated: 2026-08-22
Updated By: ChatGPT / GitHub-first workflow

## Project
Name: 3dprinthub
Repository: farazha2203/3dprinthub
Production Domain: 3dprinthub.ir

## Git
Current Development Branch: epic/phase49-unified-product-slider-sync
Pre-49.3H baseline HEAD: e052829c7ed34e931f52affecd7a3b74e33dc5a1
Production Branch/Commit: verify on host before deploy; no Phase49.3C..49.3H production deploy approved.

## Current Development
Current Epic: Epic49 Unified Product / Slider / Catalog Center
Current Phase: Phase49.3H — SEO Execution Console + AI Cost Ledger + Controlled Image Acquisition
Current Task: implement approved 49.3H on GitHub, then CI, then Windows Local Gate/QA
Status: IN_PROGRESS

## Verified Baseline
- Phase49.3G GitHub CI: SUCCESS
- Dedicated 49.3G Run 32561222101 / Job 97002924663
- Full Phase49 Run 32561222090 / Job 97002924583
- Validation PR #37 closed / not merged
- Phase49.3G Windows automated/manual QA has not yet been accepted as complete.
- Production remains UNTOUCHED / NOT APPROVED for Phase49.3C..49.3H.

## Paths
Local Project Root: D:\projects\3DPrintHub
Catalog Center: D:\projects\3DPrintHub\catalog_center
Virtual Environment: D:\projects\3DPrintHub\.venv
Django Local DB: D:\projects\3DPrintHub\db.sqlite3
Catalog Persistent Root: D:\projects\3dprinthub-catalog-manager
Catalog SQLite: D:\projects\3dprinthub-catalog-manager\catalog.sqlite3
Backups: D:\projects\3dprinthub-backups
Production Project Root: /home/sfkilvrs/3dprinthub
Production Venv: /home/sfkilvrs/virtualenv/3dprinthub/3.12
Production DB: MySQL sfkilvrs_EmiAdmin_3dprinthub

## Stack
Backend: Python / Django
Operator Desktop: Python / Tkinter Catalog Center 8.7.1
Database Local: Django SQLite + persistent Catalog SQLite
Database Production: MySQL
Production App Server: Passenger/LiteSpeed pattern; restart via tmp/restart.txt after verification

## Requested Phase49.3H Delta
1. Unified SEO/AI execution progress + result/error console for all SEO-related actions.
2. Per-product AI/SEO cost ledger using existing ai_request_log; no invented cost.
3. Publish-time internal cost receipt/snapshot.
4. Controlled image acquisition: operator-selectable per-product limit; default 10, hard max 20; apply to downloaded AND persisted/selected images.
5. Preserve selected-image text-only privacy, provenance/manual override, pricing, publish and all prior Epic49 behavior.

## Known Problems / Historical Evidence
- Old catalog log shows bridge image failures when main image was not materialized into Media.
- Historical Tk errors: pack/grid collision, dead thumbnail label callbacks, destroyed workspace callback, missing header_badge. These are historical and must not be reintroduced.
- Current uploaded historical log shows AI requests/tokens but cost may be unknown (`cost_usd=—`). Phase49.3H must not fabricate provider cost.
- Separate open item: local `/api/v1/catalog/sitemap/` 404 remains outside 49.3H.

## Remaining Work
- implement 49.3H runtime + tests + dedicated runner/workflow
- full Phase49 regression + Django suite
- sync docs with final CI
- Windows pull exact approved HEAD
- automated Local Gate
- visual/result-console/cost/image-limit QA
- one LOCAL PUBLISH ONLY
- Local Django E2E
- explicit user approval
- production backup/deploy/verify

## Exact Next Task
Implement 49.3H with minimal additive changes on GitHub; no production action.
