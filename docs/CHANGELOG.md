# PROJECT CHANGELOG

Record meaningful changes only.

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
