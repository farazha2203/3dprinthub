# Phase49.3I — Discovery Review Queue + Product List Simplification + Explicit Pricing Modes

Status: GITHUB_UPDATED / CI SUCCESS / WINDOWS QA PENDING
Approved: 2026-08-22
Branch: `epic/phase49-unified-product-slider-sync`
Phase49.3H validated baseline: `e145d1e11619e36bd766788083bee59899a80cbb`
Phase49.3I runtime validated SHA: `9d462f1ec12b00727c96acf9d4f59b4723d676b4`
Production: UNTOUCHED / NOT APPROVED

## Why
The previous classic discovery path immediately performed full extraction after URL discovery. For MakerWorld `mode=search`, it also ignored an operator-supplied search URL and scanned the configured first listing instead. This could produce unrelated products and spend time/bandwidth before human review.

The main products page also duplicated a large editor although Epic49 Product Workspace was already the canonical editing surface. Pricing visually conflated operator-entered price range with formula/dynamic calculation.

## Implemented Delta

### A. Exact Search / Listing Contract
- explicit HTTP(S) listing/search `seed` is authoritative
- MakerWorld example `https://makerworld.com/en/search/models?keyword=cake+stand` is not replaced by configured popular/download listings
- discovery extracts model/product candidates matching the source model pattern
- candidates deduplicate by source identity and normalized URL
- regression fixtures include MakerWorld IDs `2834255` and `2845731`

### B. Two-Stage Acquisition
Stage 1 — Preview:
- discover candidate model links
- capture one representative thumbnail when available
- capture source title/basic identity only
- persist local review candidate state, not a full product
- do not fetch full product text/specs/images/files

Stage 2 — Approved Full Fetch:
- operator selects candidate(s)
- operator chooses image limit `1..20` (default 10)
- full extraction runs only for approved candidates
- Phase49.3H image cap applies to persisted/selected/downloaded images
- source row is upserted once and candidate becomes imported/completed

Archive / Not Needed:
- no full extraction
- create/preserve a minimal blocked identity sufficient for existing blocked/dedup guards
- candidate becomes blocked/not-needed
- existing restore workflow remains available

### C. Source Text Safety
Applied to scraped/source textual payloads before persistence:
- Unicode NFKC normalization
- Latin-script text, ASCII/common punctuation, digits and useful technical symbols remain
- CJK/Cyrillic/unexpected scripts, emoji and control garbage are removed from source text
- URLs/identifiers remain exact
- Persian editorial/AI `_fa` fields are not filtered
- no destructive historical mass rewrite

### D. Lightweight Main Products Page
- mature product tree/database/workflow remains intact for compatibility
- embedded large right-side editor is hidden from the work-list surface
- list focuses on thumbnail + display name
- one clear `صفحه محصول / ویرایش کامل` action opens canonical Product Workspace
- double-click continues to open Product Workspace
- detailed Product Workspace fields/features are preserved

### E. Explicit Pricing Modes
Product Workspace exposes three independent business modes:
1. `fixed` — exact operator amount; min=max; final price.
2. `range` — operator min/max; existing range/consultation contract; not formula calculation.
3. `dynamic` — existing formula/variant engine based on materials, grams, print time, supervision and configured rates.

Server behavior:
- `range` is persisted as a semantic value in the existing `pricing_strategy` CharField
- ProductCatalogProfile uses `price_mode=range`
- range delegates to mature base price-range importer so consultation/range notes remain correct
- only `dynamic` invokes the formula engine
- no new Django migration

## Runtime Files
- `catalog_center/app/phase49_3i_discovery_review.py`
- `catalog_center/app/phase49_3i_source_safety.py`
- `catalog_center/app/phase49_3i_product_list.py`
- `catalog_center/app/phase49_3i_pricing_modes.py`
- `store/phase49_3i_pricing_modes.py`
- `catalog_center/launch.py`
- `store/apps.py`
- `RUN_PHASE49_3I_LOCAL_GATE.ps1`
- `.github/workflows/phase49-3i-ci.yml`

## Root Cause / CI Incident
Initial CI-only PR #41 found a real migration-contract bug after the new Catalog tests had passed.

Symptom:
`makemigrations --check --dry-run` proposed:
`store/migrations/0034_alter_productcatalogprofile_pricing_strategy.py`

Root Cause:
- first implementation mutated `ProductCatalogProfile.pricing_strategy` runtime `choices` to add `range`
- Django `choices` are model migration-state metadata
- therefore a supposedly runtime-only choice change produced an `AlterField` migration proposal

Failed assumption:
- treating runtime `field.choices` mutation as schema/migration neutral

Correct Fix:
- do not mutate migration-owned choices
- existing `CharField(max_length=20)` already stores the semantic value `range`
- Windows is the operator UI exposing Fixed/Range/Formula
- server profile sync writes `pricing_strategy=range` and `price_mode=range` without changing Django field metadata

Prevention:
- semantic schema-free values must not be implemented by mutating migration-owned Django field metadata

## Database Safety
- Django migration for Phase49.3I: NONE
- `makemigrations --check --dry-run`: PASS / no changes after fix
- Candidate review table: local Catalog SQLite only, additive `CREATE TABLE IF NOT EXISTS`
- no reset/drop/truncate/delete
- historical rows/media are not mass rewritten
- Production database untouched

## GitHub Verification
Final CI-only PR #42 was closed without merge.

Validated runtime/base SHA:
`9d462f1ec12b00727c96acf9d4f59b4723d676b4`

Runs:
- Dedicated Phase49.3I: `32569551060` — SUCCESS
- Phase49.3H regression: `32569551053` — SUCCESS
- Phase49.3G regression: `32569551048` — SUCCESS
- Full Phase49 + Full Django: `32569551034` — SUCCESS

Dedicated Phase49.3I coverage includes:
- PowerShell runner syntax/chain/Production guard
- compile of all new surfaces
- exact MakerWorld search target regression
- preview/no-full-fetch contract
- archive/block/dedupe contract
- source-script sanitation + URL/Persian preservation
- lightweight product list contract
- Fixed/Range/Dynamic Windows pricing contract
- Django range/consultation profile contract
- `makemigrations --check --dry-run`
- launcher markers
- no-destructive-schema assertion
- 49.3H image-limit regression
- 49.3G provenance regression

Full Phase49 CI additionally passed mature unified behavioral tests, Windows Catalog Epic49 tests and the full Django suite.

## Must Not Touch / Regress
- Production source/data
- Phase49.3H result/error console and cost ledger
- image default 10 / hard max 20
- selected-image text-only AI privacy
- Product/Hero revision/idempotency
- AI provenance/manual override
- dynamic Variant pricing source of truth
- local/production publish separation
- Persian content guard
- historical media/catalog data

## Remaining Acceptance Gates
1. Windows clean-worktree verification
2. `git fetch --prune` + `git pull --ff-only` from the Epic branch
3. run repository `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`
4. manual MakerWorld `cake+stand` preview QA
5. approve one candidate with chosen image limit
6. archive one candidate and verify blocked/no-full-fetch
7. repeat search and verify imported/blocked duplicate guard
8. validate lightweight Products list and Product Workspace routing
9. validate Fixed / Range / Formula pricing modes
10. one LOCAL PUBLISH ONLY + Local Django E2E
11. explicit owner approval
12. only then Production plan/deploy

## Delivery Gate
GitHub implementation + CI are complete. Next gate is Windows Local testing from GitHub. Production remains forbidden until Local approval.
