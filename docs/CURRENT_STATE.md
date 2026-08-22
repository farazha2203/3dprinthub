# CURRENT PROJECT STATE

Last Updated: 2026-08-22
Updated By: ChatGPT / GitHub-first workflow

## Project
Name: 3dprinthub
Repository: `farazha2203/3dprinthub`
Development Branch: `epic/phase49-unified-product-slider-sync`
Production Domain: `3dprinthub.ir`

## Current Epic / Phase
Current Epic: Epic49 Unified Product / Slider / Catalog Center
Current Phase: Phase49.3I — Discovery Review Queue + Product Gallery + Explicit Pricing Modes
Current Hotfix: 49.3I.3 — Windows GitHub snapshot handoff guard after stale Chat-pinned SHA failure
Status: `GITHUB_UPDATED / HANDOFF HOTFIX CI PENDING / WINDOWS RERUN BLOCKED UNTIL CI`
Production: `UNTOUCHED / NOT APPROVED`

## Latest Windows Handoff Result
Windows started from clean worktree on the correct Epic branch and successfully executed:
- `git fetch --prune origin`
- `git switch epic/phase49-unified-product-slider-sync`
- `git pull --ff-only origin epic/phase49-unified-product-slider-sync`

Local advanced from `fee6a5f...` to GitHub HEAD `53e9216ae84a3e167481253da44760179c751051`.
The preflight then stopped because the Chat command still required stale SHA `789edf8652ad8a09641afedd5e959c63822800c7`.

Canonical root cause: `ERR-49-019`.
- GitHub was correct and Local pull was correct.
- the fixed `$ExpectedHead` in Chat had become stale after later repository documentation commits.
- no reset/stash/delete/rollback is required or allowed as a shortcut.

## Handoff Safety Verification
GitHub compare from final validated runtime/docs base `97674a82acc97e1a623b76084b60344cfa93142b` to the Windows-pulled HEAD `53e9216ae84a3e167481253da44760179c751051` shows seven commits and only these surfaces:
- `PROJECT_CONTEXT.md`
- `docs/CHANGELOG.md`
- `docs/CURRENT_STATE.md`
- `docs/REQUESTS.md`
- `docs/ROADMAP.md`
- `docs/phases/PHASE49_3I_DISCOVERY_REVIEW_PRODUCT_LIST_PRICING.md`

No Catalog runtime, Django runtime, Runner, migration, database, media or production file changed in those seven commits.

## Phase49.3I.3 Implemented Fix
Canonical runner is being upgraded to `RUN_PHASE49_3I_LOCAL_GATE.ps1` version `49.3I.3`.
The repository runner now:
- requires clean Windows worktree,
- requires exact branch `epic/phase49-unified-product-slider-sync`,
- performs live `git fetch --prune origin`,
- reads the fetched `origin/epic/phase49-unified-product-slider-sync` snapshot,
- requires Local HEAD to equal that fetched Remote HEAD,
- fails closed with an explicit `git pull --ff-only` instruction when Local is behind,
- never uses a Chat-pinned SHA as the sole handoff truth,
- preserves the Windows PowerShell 5.1 ASCII-only contract.

`.github/workflows/phase49-3i-ci.yml` now asserts the 49.3I.3 Git snapshot handoff contract.
CI validation for this new runner/workflow change is pending before Windows rerun.

## Product / AI Local QA Fixes Still Preserved
### Products page
- patch wraps the real `App87._modernize_products_page` boundary.
- complete legacy product Panedwindow remains alive for compatibility but is hidden from the operator surface.
- Products page is a responsive vertically scrollable card gallery.
- each card shows only: large local thumbnail, product name, `ویرایش محصول` action.
- no price/title/status/editor parameter fields are exposed on the Products list surface.
- clicking the image opens a large local preview.
- detailed editing routes to the canonical Product Workspace.
- thumbnails are local-only and load in small Tk `after()` batches.

### AI first-paint
- `catalog_center/app/phase49_3i_local_qa_hotfix.py` paints startup progress immediately.
- existing AI flow starts after a Tk event-loop yield.
- mature 49.3H Provider/Model/network/result/error/cost/audit stack remains unchanged.

## Previous Final GitHub Validation
CI-only PR #47: `CLOSED / NOT MERGED`.
Exact validated Epic runtime/docs base: `97674a82acc97e1a623b76084b60344cfa93142b`.

SUCCESS:
- Phase49.3I dedicated Run `32573779531`
- Phase49.3H regression Run `32573779534`
- Phase49.3G regression Run `32573779548`
- Full Phase49 + Full Django Run `32573779528`
- Full Django suite step PASS
- PowerShell 5.1 ASCII runner contract PASS
- Django check / migration contract PASS
- no new Django migration

The new 49.3I.3 handoff runner/workflow change occurred after that validation and therefore requires its own final CI before Windows rerun.

## Existing Phase49.3I Contracts Preserved
- explicit operator search/listing URL is authoritative.
- discovery is Preview → operator approval → Full Fetch.
- Preview uses one candidate thumbnail/basic identity only.
- approved Full Fetch uses image limit default 10 / hard max 20.
- Archive / Not Needed preserves blocked identity without full extraction.
- duplicate/blocked guard checks source + external id + normalized URL.
- scraped unexpected source scripts are normalized without touching URLs or Persian editorial `_fa` fields.
- pricing modes remain independent: Fixed / Range / Dynamic Formula.
- Range does not invoke Dynamic formula pricing.
- SEO execution result/error drawer + per-product AI cost ledger remain protected.

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

## Database / Migration Safety
- Phase49.3I.3 handoff guard Django migration: NONE.
- no reset/drop/truncate/delete.
- no historical DB/media rewrite.
- handoff hotfix changes only Windows Git safety runner + CI contract + docs.
- Production database/source remains untouched.

## Known Separate Items
- Local `/api/v1/catalog/sitemap/` 404 remains separate before complete Epic closure.
- CKEditor4 debt remains separate.
- Production realtime/Redis warning remains separate.
- Pillow `Image.getdata()` deprecation remains non-blocking debt.

## Remaining Work
1. complete Phase49.3I.3 GitHub CI validation for runner/workflow handoff guard.
2. Windows verifies clean worktree; no reset/stash/delete shortcut.
3. Windows `git fetch --prune origin` + `git pull --ff-only` current Epic branch.
4. run repository `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp` v49.3I.3.
5. visual QA: Products page gallery-only image/name/edit + large preview.
6. AI QA: full autofill immediate startup progress → existing 49.3H progress/result drawer.
7. MakerWorld `cake+stand` Preview/Approve/Archive/Dedupe QA.
8. Fixed / Range / Formula pricing QA.
9. one LOCAL PUBLISH ONLY + Local Django E2E.
10. explicit owner approval.
11. only then Production plan/deploy.

## Exact Next Task
Finish CI for Phase49.3I.3. After CI success, Windows pulls the current Epic branch and runs the repository runner v49.3I.3. Do not manually edit Windows source and do not touch Production.
