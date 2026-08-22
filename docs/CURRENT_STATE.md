# CURRENT PROJECT STATE

Last Updated: 2026-08-22
Updated By: ChatGPT / GitHub-first workflow

## Project
Name: 3dprinthub
Repository: `farazha2203/3dprinthub`
Production Domain: `3dprinthub.ir`

## Git
Current Development Branch: `epic/phase49-unified-product-slider-sync`
Phase49.3H validated Epic HEAD: `e145d1e11619e36bd766788083bee59899a80cbb`
Phase49.3I docs-closed validation before Windows run: `91f39681e2008c29d0ec7bc06794b935d794b33e`
Phase49.3I runner-hotfix runtime validated base: `451bcb9e264b847259a6ea0414550e4f80afa250`
Production Branch/Commit: verify on host before deploy; no Phase49.3C..49.3I production deploy approved.

## Current Development
Current Epic: Epic49 Unified Product / Slider / Catalog Center
Current Phase: Phase49.3I — Discovery Review Queue + Product List Simplification + Explicit Pricing Modes
Current Hotfix: Phase49.3I Windows PowerShell 5.1 Runner Encoding
Status: GITHUB_UPDATED / HOTFIX CI SUCCESS / WINDOWS LOCAL RERUN PENDING

## Windows Local Result — 2026-08-22
Windows successfully:
- verified clean worktree
- fetched GitHub
- verified remote validated HEAD `91f39681e2008c29d0ec7bc06794b935d794b33e`
- fast-forwarded 57 commits
- verified local HEAD matched the validated GitHub HEAD
- found repository `RUN_PHASE49_3I_LOCAL_GATE.ps1`

The Local Gate then failed before executing any test because Windows PowerShell 5.1 could not parse the BOM-less UTF-8 runner. The failure showed mojibake Persian text and parser errors such as `Unexpected token ')'` around the manual QA output section.

No DB migration, reset, delete, Local Publish or Production action occurred during this failure.

## Runner Encoding Root Cause / Fix
Canonical error: `ERR-49-016` in `docs/ERRORS.md`.

Root Cause:
- GitHub stored `RUN_PHASE49_3I_LOCAL_GATE.ps1` as UTF-8 without BOM.
- The runner contained Persian text and an em dash.
- Windows PowerShell 5.1 decodes BOM-less scripts using legacy ANSI semantics.
- the em-dash UTF-8 bytes became mojibake containing a smart quote that PowerShell treats as a string delimiter, causing downstream `)` and `<` parse errors.
- modern Linux `pwsh` CI parsed UTF-8 correctly, so the old syntax-only test did not exercise this Windows PowerShell 5.1 encoding boundary.

Correct Fix:
- runner bumped to `49.3I.1`.
- canonical runner is ASCII-only.
- manual QA text inside the runner is ASCII; Persian UI labels remain in UI/docs.
- `.github/workflows/phase49-3i-ci.yml` now reads raw runner bytes and fails if any byte is greater than 127 before parsing the runner.
- CI checks marker `ASCII_ONLY_FOR_WINDOWS_POWERSHELL_5_1`.

## Phase49.3I Runner Hotfix GitHub Validation
CI-only PR #44: CLOSED / NOT MERGED.
Validated Epic base/runtime SHA: `451bcb9e264b847259a6ea0414550e4f80afa250`.

SUCCESS:
- Phase49.3I dedicated Run `32570978818`
- Phase49.3H regression Run `32570978800`
- Phase49.3G regression Run `32570978829`
- Full Phase49 + Full Django Run `32570978799`
- runner ASCII-byte contract PASS
- PowerShell syntax/chain/Production guard PASS
- Django check/migration contract PASS
- mature Phase49 regressions PASS
- full Django suite PASS

## Phase49.3I Implemented
1. Explicit operator search/listing URL is authoritative.
2. Discovery is two-stage: lightweight candidate Preview, then approved Full Fetch.
3. Preview stores one representative thumbnail + basic source identity only.
4. Approved Full Fetch uses Phase49.3H image limit default 10 / hard max 20.
5. Archive / Not Needed creates or preserves blocked identity without full extraction.
6. Duplicate/blocked guard checks source code + external id + normalized URL.
7. Source text safety removes unexpected scripts from scraped source text while preserving URLs/identity and Persian editorial fields.
8. Products/work list is lightweight and routes detailed editing to Product Workspace.
9. Pricing modes are explicit: Fixed / Range / Dynamic Formula.
10. Range does not invoke the dynamic formula engine.

## Paths
Local Project Root: `D:\projects\3DPrintHub`
Catalog Center: `D:\projects\3DPrintHub\catalog_center`
Virtual Environment: `D:\projects\3DPrintHub\.venv`
Django Local DB: `D:\projects\3DPrintHub\db.sqlite3`
Catalog Persistent Root: `D:\projects\3dprinthub-catalog-manager`
Catalog SQLite: `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`
Backups: `D:\projects\3dprinthub-backups`
Production Project Root: `/home/sfkilvrs/3dprinthub`
Production Venv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`
Production DB: MySQL `sfkilvrs_EmiAdmin_3dprinthub`

## Stack
Backend: Python / Django
Operator Desktop: Python / Tkinter Catalog Center 8.7.1
Database Local: Django SQLite + persistent Catalog SQLite
Database Production: MySQL
Production App Server: Passenger/LiteSpeed pattern

## Database / Migration Safety
- Phase49.3I Django migration: NONE.
- Runner encoding hotfix changes no Python/Django model/database behavior.
- Candidate review table remains local Catalog SQLite only and additive.
- no reset/drop/truncate/delete.
- historical product/media rows are untouched.
- Production database is untouched.

## Production
**UNTOUCHED / NOT APPROVED.**

## Known Separate Items
- Local `/api/v1/catalog/sitemap/` 404 remains separate before complete Epic closure.
- CKEditor4 debt remains separate.
- Production realtime/Redis warning remains separate.

## Remaining Work
- final docs-closed GitHub revalidation of the runner hotfix branch state
- Windows `git status --short`
- Windows `git fetch --prune origin`
- Windows `git pull --ff-only origin epic/phase49-unified-product-slider-sync`
- verify repository runner version `49.3I.1`
- run `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`
- manual MakerWorld `cake+stand` discovery/review QA
- approve one candidate with image limit 10
- archive one candidate and verify blocked/no-full-fetch
- repeat search and verify duplicate guard
- lightweight Products page + Product Workspace QA
- Fixed / Range / Formula pricing QA
- one LOCAL PUBLISH ONLY + Local Django E2E
- explicit owner approval
- only then Production plan/deploy

## Exact Next Task
After final GitHub validation of this documentation-closed hotfix state: Windows pulls the exact validated Epic HEAD and reruns repository `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`. Do not edit the runner manually on Windows and do not touch Production.
