# PROJECT CHANGELOG

Record meaningful changes only.

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
