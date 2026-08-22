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
Phase49.3I validated runtime HEAD: 9d462f1ec12b00727c96acf9d4f59b4723d676b4
Production Branch/Commit: verify on host before deploy; no Phase49.3C..49.3I production deploy approved.

## Current Development
Current Epic: Epic49 Unified Product / Slider / Catalog Center
Current Phase: Phase49.3I — Discovery Review Queue + Product List Simplification + Explicit Pricing Modes
Status: GITHUB_UPDATED / CI SUCCESS / WINDOWS LOCAL QA PENDING

## Phase49.3I GitHub Validation
Status: GITHUB_UPDATED
- Dedicated Phase49.3I CI Run 32569551060 — SUCCESS
- Phase49.3H regression Run 32569551053 — SUCCESS
- Phase49.3G regression Run 32569551048 — SUCCESS
- Full Phase49 + Full Django CI Run 32569551034 — SUCCESS
- Final validation PR #42 was CI-only and closed without merge.
- Validated runtime/base SHA: `9d462f1ec12b00727c96acf9d4f59b4723d676b4`.
- PR #41 exposed a real migration-contract failure and was closed without merge; the fix was committed before PR #42.

## Phase49.3I Implemented
1. Exact search/listing URL contract: an explicit operator HTTP(S) seed is authoritative and is no longer silently replaced by the configured default listing.
2. Two-stage acquisition: Preview Candidate first, then operator approval, then full fetch.
3. Preview candidate stores one representative thumbnail + basic title/source identity only; no full extraction before approval.
4. Approved candidate full fetch uses the existing Phase49.3H image limit contract (default 10, hard max 20).
5. Archive / Not Needed creates or preserves a minimal blocked identity and does not full-fetch the product.
6. Duplicate/blocked guard uses source code + external id + normalized URL before full fetch.
7. Source text safety removes CJK/Cyrillic/emoji/unexpected script garbage from scraped source text while preserving URLs/identities and Persian editorial `_fa` fields.
8. Products/work queue is lightweight: thumbnail + product name + one Product Workspace action; detailed editing remains in Product Workspace.
9. Pricing is explicit: `fixed`, `range`, `dynamic/formula`.
10. Range uses existing min/max consultation contract and does not enter the dynamic formula engine.
11. Canonical repository runner: `RUN_PHASE49_3I_LOCAL_GATE.ps1`.
12. Dedicated CI workflow: `.github/workflows/phase49-3i-ci.yml`.

## Phase49.3I Root-Cause Fix During CI
Initial PR #41 failed `makemigrations --check --dry-run` because Phase49.3I mutated `ProductCatalogProfile.pricing_strategy` runtime choices and Django proposed metadata migration `store.0034_alter_productcatalogprofile_pricing_strategy`.

Correct fix:
- do not mutate migration-owned Django field choices;
- keep the existing CharField schema unchanged;
- persist semantic value `range` directly;
- Windows remains the operator UI exposing the three business modes;
- server profile sync stores `pricing_strategy=range` and `price_mode=range` without a new migration.

Verification:
- dedicated Phase49.3I tests PASS;
- `makemigrations --check --dry-run` PASS with no changes;
- full Phase49 + full Django suite PASS.

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

## Database / Migration Safety
- Phase49.3I Django migration: NONE.
- Candidate review table is local Catalog SQLite only and additive (`CREATE TABLE IF NOT EXISTS`).
- No reset/drop/truncate/delete.
- Historical product/media rows are not mass-rewritten.
- Production database is untouched.

## Production
UNTOUCHED / NOT APPROVED.

## Remaining Work
- Windows `git status --short` safety check
- Windows `git fetch --prune origin`
- Windows `git switch epic/phase49-unified-product-slider-sync`
- Windows `git pull --ff-only origin epic/phase49-unified-product-slider-sync`
- run repository `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`
- manual QA with the real MakerWorld `cake+stand` search URL
- approve one candidate and archive one candidate
- verify duplicate guard + selected image limit
- verify lightweight Products page + Product Workspace routing
- verify Fixed / Range / Formula pricing modes
- one LOCAL PUBLISH ONLY / local Django E2E
- explicit owner approval
- only then production plan/deploy

## Exact Next Task
Windows Local Gate + manual Phase49.3I QA from the GitHub branch. Production remains forbidden until explicit Local approval.
