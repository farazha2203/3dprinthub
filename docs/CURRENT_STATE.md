# CURRENT PROJECT STATE

Last Updated: 2026-08-22
Updated By: ChatGPT / GitHub-first workflow

## Project
Name: 3dprinthub
Repository: farazha2203/3dprinthub
Production Domain: 3dprinthub.ir

## Git
Current Development Branch: epic/phase49-unified-product-slider-sync
Phase49.3H validated Epic HEAD: e145d1e11619e36bd766788083bee59899a80cbb
Pre-49.3H baseline HEAD: e052829c7ed34e931f52affecd7a3b74e33dc5a1
Production Branch/Commit: verify on host before deploy; no Phase49.3C..49.3I production deploy approved.

## Current Development
Current Epic: Epic49 Unified Product / Slider / Catalog Center
Current Phase: Phase49.3I — Discovery Review Queue + Product List Simplification + Explicit Pricing Modes
Status: IN_PROGRESS

## Phase49.3H GitHub Validation
Status: GITHUB_UPDATED
- Dedicated 49.3H CI Run 32565773426 — SUCCESS
- Phase49.3G regression Run 32565773459 — SUCCESS
- Full Phase49 CI Run 32565773433 — SUCCESS
- Validation PR #40 is CI-only and must be closed without merge.
- 49.3H Windows Local Gate/manual QA/Local Publish are still pending; therefore 49.3H is not LOCAL_TESTED or ACCEPTED yet.

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

## Phase49.3I Requested Delta
1. Search URL is authoritative. Example MakerWorld `https://makerworld.com/en/search/models?keyword=cake+stand` must discover candidates from that exact page, not a default listing URL.
2. Two-stage acquisition: Preview candidate first (one thumbnail + basic identity/title), operator approves/archives, only then full product extraction occurs.
3. Approved candidate full fetch uses operator-selected image limit 1..20; archive/not-needed candidate becomes blocked without full fetch.
4. Duplicate and blocked identities must never be fetched again.
5. Scraped source text stored in source fields must be Latin/English-safe; URLs/identities are untouched and Persian editorial `_fa` fields remain Persian.
6. Main products/work queue becomes lightweight: thumbnail + product name + one Product Page/Workspace action; detailed editing moves to Product Workspace.
7. Pricing UI exposes exactly three business modes: fixed exact price, operator-entered price range, formula/dynamic calculation.
8. Preserve Phase49.3H execution/cost/image-limit contracts and all mature Epic49 behavior.

## Verified Root Causes For 49.3I
- `main.py::_scan_worker` currently uses configured `listing[:1]` for mode `search`, ignoring the operator-supplied seed/search URL. This explains unrelated MakerWorld results.
- Current scan immediately enters full `collect_classic_exact` after discovery; there is no human preview/approval gate.
- Current products page still contains a large embedded editor although Product Workspace already exists.
- Current Phase49.3F pricing UI conflates `dynamic` and range into one radio option even though server profile has an explicit `range` price mode.

## Database / Migration Safety
- Expected Django migration for Phase49.3I: NONE unless later tests prove a real schema requirement.
- Candidate review state will be local-only/additive in Catalog SQLite.
- No reset/drop/truncate/delete.
- Existing historical rows are not mass-rewritten solely for source-script sanitation.

## Production
UNTOUCHED / NOT APPROVED.

## Remaining Work
- close CI-only PR #40 without merge
- implement Phase49.3I GitHub code + tests + runner + CI
- run dedicated 49.3I and full regression CI
- update docs with exact validated HEAD
- Windows `git pull --ff-only`
- run repository Phase49.3I Local Gate
- manual QA: MakerWorld cake-stand preview, approve/archive, image limit, lightweight product list, 3 pricing modes
- one LOCAL PUBLISH ONLY / local Django E2E
- explicit owner approval
- only then production plan/deploy

## Exact Next Task
Implement Phase49.3I minimally on GitHub; no production action.
