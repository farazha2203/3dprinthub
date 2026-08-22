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
Current Hotfix: 49.3I.2 — Windows Local QA regressions: real Products gallery composition + AI progress first-paint
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS LOCAL RERUN PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Latest Windows QA Findings
1. Products page did not show the intended product image gallery and legacy parameter/editor UI remained visible.
2. Clicking full AI autofill appeared to hang briefly before the progress UI became visible.

Canonical root causes:
- `ERR-49-017`: old 49.3I product-list patch wrapped `App87._products_ui`, but UX87 constructs the page through `super()._products_ui()` and then `self._modernize_products_page()`. The patch missed the real composition boundary.
- `ERR-49-018`: mature 49.3F AI flow performed synchronous save/preflight/source preparation before constructing `AIProgress`, so no progress window existed during that interval.

## Implemented Local QA Fixes
### Products page
- patch wraps the real `App87._modernize_products_page` boundary.
- complete legacy product Panedwindow remains alive for compatibility but is hidden from the operator surface.
- Products page is a responsive vertically scrollable card gallery.
- each card shows only: large local thumbnail, product name, `ویرایش محصول` action.
- no price/title/status/editor parameter fields are exposed on the Products list surface.
- clicking the image opens a large local preview.
- detailed editing routes to the canonical Product Workspace.
- thumbnails are local-only and resolve through strict local mapping, `page_extract.json`, then `local_dir/images` fallback.
- thumbnails load in small Tk `after()` batches to avoid a large synchronous UI stall.

### AI first-paint
- additive module: `catalog_center/app/phase49_3i_local_qa_hotfix.py`.
- startup progress paints immediately before legacy synchronous preflight.
- existing AI flow starts via Tk `after(80)` after the first paint.
- when mature 49.3H progress is created, startup progress hands off to it.
- Provider/Model selection, network worker, AI request, SEO result/error drawer, cost ledger and audit remain the existing 49.3F/49.3H implementation; no duplicate AI workflow was added.

### Runner
- canonical runner: `RUN_PHASE49_3I_LOCAL_GATE.ps1` version `49.3I.2`.
- Windows PowerShell 5.1 ASCII-only runner contract remains enforced.
- runner tests Product gallery composition + AI first-paint regression.

## Final GitHub Validation
CI-only PR #47: `CLOSED / NOT MERGED`.
Exact validated Epic runtime/docs base: `97674a82acc97e1a623b76084b60344cfa93142b`.
Marker head `0530181f1b4f2fcedadbdc0cc34251c43f2b1f3b` was not merged.

SUCCESS:
- Phase49.3I dedicated Run `32573779531`
- Phase49.3H regression Run `32573779534`
- Phase49.3G regression Run `32573779548`
- Full Phase49 + Full Django Run `32573779528`
- Full Django suite step PASS
- PowerShell 5.1 ASCII runner contract PASS
- Django check / migration contract PASS
- no new Django migration

Post-validation commits after `97674a82...` are documentation-only; runtime validated by PR #47 is unchanged. Changelog, Requests, Roadmap and the active Phase49.3I document are synchronized with the final CI result.

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
- Phase49.3I Local QA hotfix Django migration: NONE.
- no reset/drop/truncate/delete.
- no historical DB/media rewrite.
- Product gallery is a UI layer over existing rows/files.
- AI first-paint hotfix changes UI sequencing only.
- Production database/source remains untouched.

## Known Separate Items
- Local `/api/v1/catalog/sitemap/` 404 remains separate before complete Epic closure.
- CKEditor4 debt remains separate.
- Production realtime/Redis warning remains separate.
- Pillow `Image.getdata()` deprecation remains non-blocking debt.

## Remaining Work
1. Windows clean-worktree + `git fetch --prune` + `git pull --ff-only`.
2. verify runner version `49.3I.2`.
3. run repository `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`.
4. visual QA: Products page must be gallery-only cards with image/name/edit + large image preview.
5. AI QA: full autofill must show immediate startup progress, then existing connection/send/receive progress and result/error drawer.
6. MakerWorld `cake+stand` Preview/Approve/Archive/Dedupe QA.
7. Fixed / Range / Formula pricing QA.
8. one LOCAL PUBLISH ONLY + Local Django E2E.
9. explicit owner approval.
10. only then Production plan/deploy.

## Exact Next Task
Pull the current Epic branch on Windows and rerun `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`. Do not manually edit Windows source and do not touch Production.
