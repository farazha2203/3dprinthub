# PROJECT CHANGELOG

Record meaningful changes only.

## 2026-08-22 — Phase49.3I.5 Selection Loop Guard + Compact Product Metadata

### Windows QA Evidence
- Windows pulled Phase49.3I.4 to `7330ad6d79d8061998b1fa143051173b558cefbd`.
- repository-owned local gate completed successfully.
- 137 Catalog Center tests PASS.
- 419 Django tests PASS with 2 skipped.
- no new migration was proposed/planned.
- Production remained untouched.
- Explorer thumbnail/view rendering was visually corrected.

### Fixed
- product selection/open no longer creates a hidden Treeview selection feedback loop.
- Root Cause `ERR-49-022`: Explorer card called `selection_set()`, mature `<<TreeviewSelect>>` invoked `load_product`, and compatibility `load_product` wrote the selection again.
- card → hidden Treeview sync is now one-way and re-entrancy guarded.
- `selection_set()` runs only when the hidden Treeview selection differs.
- Treeview `load_product()` updates current/card state only and never writes selection back.
- Product Open has a repeat-click guard and yields one Tk frame before Product Workspace construction.

### Added / Refined
- compact operator metadata on each product card:
  - Product ID,
  - product/workflow state,
  - source,
  - image count,
  - added date,
  - publish state.
- Persian operator filters including Ready, Publish Queue and Published.
- Persian sorts including Newest, Oldest and Last Updated.
- old raw filter/sort bar hidden while mature DB/filter backend remains in use.
- dedicated fake-Treeview regression test that fires the selection callback directly from `selection_set()` and proves one selection write only.

### Preserved
- Explorer Extra Large/Large/Medium/Small/List views.
- persistent view preference.
- Ctrl/Shift multi-select and context menu.
- safe Remove From Publish Queue semantics only: `upload_ready=0`, `workflow_status=review`.
- Product Workspace remains the detailed editor.
- Product-vs-Group URL routing by source `model_url_pattern`.
- Preview → Approve → Full Fetch.
- AI progress/result/error/cost behavior.
- image default 10 / hard max 20.
- Fixed / Range / Formula pricing independence.

### Runner / CI
- `RUN_PHASE49_3I_LOCAL_GATE.ps1` bumped to `49.3I.5` and remains ASCII-only for Windows PowerShell 5.1.
- new runner markers protect selection-loop guard, compact metadata and friendly filter/sort behavior.
- CI-only PR #50 closed without merge.
- validated Epic runtime base: `cdaac6680ea8545f52ece15ecaa3ce0a575eabe9`.
- marker head `57813f47f649bb2c415aa0fae1481f4a2561ce1d` not merged.
- Phase49.3I Run `32580222694` — SUCCESS.
- Phase49.3H Run `32580222686` — SUCCESS.
- Phase49.3G Run `32580222682` — SUCCESS.
- Full Phase49 + Full Django Run `32580222683` — SUCCESS.

### Database / Production
- Django migration: NONE.
- Catalog schema migration: NONE.
- no reset/drop/truncate/data rewrite.
- no media rewrite/delete.
- Production untouched / not approved.

### Acceptance State
- GitHub implementation and final CI complete.
- Windows 49.3I.5 pull/interaction/metadata QA pending.
- Local Publish remains blocked until that QA passes.

## 2026-08-22 — Phase49.3I.4 Explorer Product Gallery + Source URL Routing

### Fixed
- real product thumbnails no longer depend on a text-unit-sized Tk Label. 49.3I.4 uses a pixel-sized image holder with propagation disabled and an unconstrained child image Label, preventing the thin horizontal strip regression recorded as `ERR-49-020`.
- direct-link intake no longer relies only on a finite set of Search/Listing URL shapes. For configured sources, the source `model_url_pattern` is the authoritative Product URL boundary; valid non-product URLs route Preview-first. This is recorded as `ERR-49-021`.

### Added
- Windows-Explorer-style Products view modes: Extra Large, Large, Medium, Small and List.
- persistent local view preference through the existing Catalog settings table.
- normal/Ctrl/Shift multi-selection, Select All, Clear Selection and selected-count UI.
- right-click context menu with Open Product, Image Preview, Remove From Publish Queue, Select All and Clear Selection.
- safe multi-item local publish-queue removal using only `upload_ready=0` and `workflow_status=review`; no delete/block/Production operation.
- `catalog_center/app/phase49_3i_explorer_hotfix.py`.
- `catalog_center/tests/test_epic49_phase49_3i_explorer_hotfix.py`.

### Preserved
- Product cards still expose only image, product name and Edit Product.
- Product Workspace remains the detailed editor.
- normal image click still opens large local preview.
- local-only product thumbnail resolution remains strict mapping → `page_extract.json` → local `images/`.
- Preview → Approve → Full Fetch remains the acquisition state machine.
- image limit default 10 / hard max 20 remains unchanged.
- Fixed / Range / Formula pricing remains unchanged.
- 49.3I.3 live fetched Git snapshot handoff guard remains unchanged.

### Runner / CI
- `RUN_PHASE49_3I_LOCAL_GATE.ps1` bumped to `49.3I.4` and remains ASCII-only for Windows PowerShell 5.1.
- runner now compiles/tests the Explorer hotfix and adds manual QA for full thumbnail rendering, view switching, Ctrl/Shift selection, right-click queue removal and Product-vs-Group URL routing.
- Phase49.3I CI now validates the v49.3I.4 runner contract and dedicated Explorer/routing tests.

### Database / Production
- intended Django migration: NONE.
- no Django model/schema change.
- existing local Catalog settings table only stores the view preference.
- no product delete/block operation from Explorer queue removal.
- no media rewrite.
- Production untouched / not approved.

### Validation State
- GitHub implementation complete.
- final CI probe pending.
- Windows pull/visual/data QA pending.
- LOCAL PUBLISH ONLY remains blocked until Explorer/routing QA passes.

## 2026-08-22 — Phase49.3I.3 Windows Git Snapshot Handoff Guard

### Fixed
- Windows handoff no longer depends on a Chat-pinned `$ExpectedHead` that can become stale while the development branch advances.
- canonical runner now performs live `git fetch --prune origin`, requires the exact Epic branch and clean worktree, resolves the fetched remote branch HEAD, and requires Local HEAD to match that fetched snapshot.
- Local/Remote mismatch fails closed with an explicit `git pull --ff-only` instruction and requires rerunning the repository gate.

### Root Cause
- Windows correctly fast-forwarded from `fee6a5f...` to GitHub HEAD `53e9216ae84a3e167481253da44760179c751051`.
- the handoff then falsely failed because the Chat command still required stale SHA `789edf8652ad8a09641afedd5e959c63822800c7`.
- GitHub compare from validated base `97674a82acc97e1a623b76084b60344cfa93142b` to `53e9216...` confirmed the seven later commits were documentation-only.
- repository policy already required Remote Epic HEAD resolution after fetch; the failed Chat preflight violated that rule.
- recorded as `ERR-49-019`.

### Runner / CI
- `RUN_PHASE49_3I_LOCAL_GATE.ps1` bumped to `49.3I.3`.
- Windows PowerShell 5.1 ASCII-only contract is preserved.
- Phase49.3I CI requires exact branch guard, live fetch guard, fetched remote-ref guard and `PHASE49_3I_GIT_SNAPSHOT=OK`.

### Validation
- CI-only PR #48 closed without merge.
- validated Epic base `7117510f173f45a3d8c806e46fb0476cbaeba115`.
- marker head `fc400359442efef336b445a72d60002f78eab916` not merged.
- Phase49.3I Run `32575765467` — SUCCESS.
- Phase49.3H Run `32575765515` — SUCCESS.
- Phase49.3G Run `32575765544` — SUCCESS.
- Full Phase49 + Full Django Run `32575765457` — SUCCESS.
- Full Django suite PASS.

### Database / Production
- Django migration: NONE.
- no DB/media rewrite.
- no reset/stash/delete cleanup shortcut.
- Production untouched / not approved.

## 2026-08-22 — Phase49.3I Docs-Closed Final Validation

### Validation
- final CI-only PR #47 completed and was closed without merge.
- exact validated Epic runtime/docs base: `97674a82acc97e1a623b76084b60344cfa93142b`.
- Phase49.3I Discovery Review Pricing CI Run `32573779531` — SUCCESS.
- Phase49.3H SEO Cost Image Limit CI Run `32573779534` — SUCCESS.
- Phase49.3G Workspace Usability CI Run `32573779548` — SUCCESS.
- Phase49 Epic Unified CI Run `32573779528` — SUCCESS.
- marker head `0530181f1b4f2fcedadbdc0cc34251c43f2b1f3b` was not merged.

### Gate
- GitHub final validation is complete for the 49.3I.2 runtime/docs baseline.
- later 49.3I.3 handoff guard also passed its own CI in PR #48.
- Production remains untouched and forbidden until Windows visual/data QA, LOCAL PUBLISH ONLY, Local Django E2E and explicit owner approval.

## 2026-08-22 — Phase49.3I Local QA Regression Hotfix

### Fixed
- Products page now patches the real UX87 `_modernize_products_page` composition boundary instead of an `_products_ui` override that the shell bypassed.
- legacy table/editor Panedwindow is preserved for compatibility but hidden from the operator Products surface.
- Products page now renders a responsive scrollable gallery with large local thumbnail, product name and one `ویرایش محصول` action per card.
- product image click opens a large local preview.
- thumbnails resolve from local persisted mappings/files only and load in small Tk `after()` batches.
- full AI autofill now paints immediate startup progress before synchronous save/preflight/source preparation and hands off to the mature 49.3H progress/result UI.

### Preserved
- AI Provider/Model selection, network worker, result/error drawer, request logging and cost ledger remain the mature 49.3F/49.3H implementation.
- Product Workspace remains the detailed editor.
- MakerWorld Preview/Approve/Archive/Dedupe and image limit 10/20 remain unchanged.
- Fixed / Range / Formula pricing remains unchanged.

### Runner
- `RUN_PHASE49_3I_LOCAL_GATE.ps1` bumped to `49.3I.2`.
- ASCII-only Windows PowerShell 5.1 contract remains enforced.
- gallery composition and AI first-paint tests are now part of the canonical runner/CI.

### Database
- Django migration: NONE.
- no reset/drop/truncate/delete/data rewrite.
- Production untouched.

### Tests
- CI-only PR #46 closed without merge.
- Phase49.3I Run `32573421461` — SUCCESS.
- Phase49.3H Run `32573421431` — SUCCESS.
- Phase49.3G Run `32573421523` — SUCCESS.
- Full Phase49 + Full Django Run `32573421439` — SUCCESS.
- runtime base before docs closure: `bf51fff1000bfcc6561712a243cb13e48001123c`.

### Documentation
- `ERR-49-017` and `ERR-49-018` added.
- CURRENT_STATE / ROADMAP / REQUESTS / active Phase49.3I docs updated.

## 2026-08-22 — Phase49.3I Windows PowerShell 5.1 Runner Encoding Hotfix

### Changed
- `RUN_PHASE49_3I_LOCAL_GATE.ps1` bumped from `49.3I.0` to `49.3I.1`.
- the canonical 49.3I Windows runner is now ASCII-only to remain deterministic under Windows PowerShell 5.1 BOM-less script decoding.
- manual QA output inside the runner was converted to ASCII text; Persian UI/docs remain unchanged.
- Phase49.3I CI now rejects any non-ASCII runner byte and verifies `ASCII_ONLY_FOR_WINDOWS_POWERSHELL_5_1` before parsing.

### Fixed
- Windows Local Gate parser failure showing mojibake and `Unexpected token ')'` / reserved `<` errors before the runner could execute.
- Root Cause: UTF-8 without BOM + Persian/em-dash text was decoded through legacy ANSI by Windows PowerShell 5.1; the em-dash byte sequence became mojibake containing a smart quote interpreted as a string delimiter.

### Database
- NONE.
- no migration, reset, delete, drop, truncate, data rewrite or media change.

### Deployment
- Production untouched / not approved.
- Windows must pull the GitHub hotfix; no manual local patch is allowed.

### Tests
- CI-only PR #44 closed without merge.
- Phase49.3I Run `32570978818` — SUCCESS.
- Phase49.3H Run `32570978800` — SUCCESS.
- Phase49.3G Run `32570978829` — SUCCESS.
- Full Phase49 + Full Django Run `32570978799` — SUCCESS.
- validated runtime/base SHA: `451bcb9e264b847259a6ea0414550e4f80afa250`.

### Documentation
- `ERR-49-016` added to `docs/ERRORS.md`.
- CURRENT_STATE and active Phase49.3I documentation updated.

### Git
Branch: `epic/phase49-unified-product-slider-sync`
Runner-hotfix runtime validated commit: `451bcb9e264b847259a6ea0414550e4f80afa250`

## 2026-08-22 — Phase49.3I Discovery Review / Product List / Pricing Modes

### Added
- two-stage Discovery Review Queue: lightweight candidate preview before full product acquisition
- authoritative explicit search/listing URL contract for MakerWorld and compatible sources
- one-thumbnail candidate preview with source title/id/url
- approve-to-full-fetch flow with operator image limit `1..20`
- archive/not-needed flow that preserves blocked identity without full extraction
- scraped source-text Latin/English safety boundary while preserving URLs and Persian editorial fields
- lightweight Products/work-list surface routing detailed edits to Product Workspace
- explicit Windows pricing modes: Fixed / Range / Formula(Dynamic)
- `RUN_PHASE49_3I_LOCAL_GATE.ps1`
- `.github/workflows/phase49-3i-ci.yml`

### Changed
- Product Workspace pricing UI no longer conflates operator-entered range with formula pricing
- server sync persists semantic `pricing_strategy=range` + `price_mode=range` using existing schema
- discovery no longer silently replaces an explicit operator search URL with configured default listing

### Fixed
- unrelated MakerWorld search results caused by `mode=search` ignoring explicit seed URL
- expensive full extraction occurring before operator review
- CI-found phantom migration: runtime mutation of Django `pricing_strategy` choices proposed `store.0034`; fixed by leaving migration-owned field metadata unchanged

### Database
- Django migration: NONE
- Candidate review state is additive local Catalog SQLite only
- no reset/drop/truncate/delete and no historical mass rewrite

### Deployment
- Production untouched / not approved
- next gate is Windows Local Gate + manual QA + LOCAL PUBLISH ONLY

### Tests
- Dedicated Phase49.3I Run `32569551060` — SUCCESS
- Phase49.3H regression Run `32569551053` — SUCCESS
- Phase49.3G regression Run `32569551048` — SUCCESS
- Full Phase49 + Full Django Run `32569551034` — SUCCESS
- CI-only PR #42 closed without merge
- runtime/base SHA validated: `9d462f1ec12b00727c96acf9d4f59b4723d676b4`

### Documentation
- CURRENT_STATE, ROADMAP, ERRORS, REQUESTS and active Phase49.3I doc updated
- ERR-49-015 records migration metadata root cause and prevention rule

### Git
Branch: `epic/phase49-unified-product-slider-sync`
Runtime validated commit: `9d462f1ec12b00727c96acf9d4f59b4723d676b4`

## 2026-08-22 — Phase49.3H GitHub Validation Closure

### Added
- SEO execution/result console
- per-product AI/SEO cost ledger and publish receipt
- controlled image acquisition default 10 / hard max 20

### Deployment
- Production untouched
- Windows Local Gate/QA remains pending and is chained by the Phase49.3I runner

### Tests
- Dedicated 49.3H Run `32565773426` — SUCCESS
- Phase49.3G regression Run `32565773459` — SUCCESS
- Full Phase49 Run `32565773433` — SUCCESS
- CI-only PR #40 closed without merge