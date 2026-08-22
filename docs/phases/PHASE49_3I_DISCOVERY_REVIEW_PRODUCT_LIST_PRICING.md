# Phase49.3I — Discovery Review Queue + Product List Simplification + Explicit Pricing Modes

Status: GITHUB_UPDATED / HOTFIX CI SUCCESS / WINDOWS LOCAL RERUN PENDING
Approved: 2026-08-22
Branch: `epic/phase49-unified-product-slider-sync`
Phase49.3H validated baseline: `e145d1e11619e36bd766788083bee59899a80cbb`
Phase49.3I docs-closed pre-Windows validated SHA: `91f39681e2008c29d0ec7bc06794b935d794b33e`
Phase49.3I runner-hotfix runtime validated SHA: `451bcb9e264b847259a6ea0414550e4f80afa250`
Canonical runner: `RUN_PHASE49_3I_LOCAL_GATE.ps1` v`49.3I.1`
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

## CI Root Cause — Phantom Django Migration
Initial CI-only PR #41 found a real migration-contract bug after the new Catalog tests had passed.

Symptom:
`makemigrations --check --dry-run` proposed:
`store/migrations/0034_alter_productcatalogprofile_pricing_strategy.py`

Root Cause:
- first implementation mutated `ProductCatalogProfile.pricing_strategy` runtime `choices` to add `range`
- Django `choices` are model migration-state metadata

Correct Fix:
- do not mutate migration-owned choices
- existing `CharField(max_length=20)` stores semantic value `range`
- Windows exposes Fixed/Range/Formula
- server profile sync writes `pricing_strategy=range` + `price_mode=range` without changing Django field metadata

Canonical error: `ERR-49-015`.

## Windows Local Incident — PowerShell 5.1 Runner Encoding
The first Windows attempt against validated HEAD `91f39681e2008c29d0ec7bc06794b935d794b33e` completed Git safety/fetch/fast-forward verification successfully, then the runner failed before execution.

Symptoms:
- `Unexpected token ')' in expression or statement`
- later `<` reported as reserved operator
- Persian manual-QA labels displayed as mojibake such as `Ø...`
- parse errors clustered around manual QA `Write-Host` lines

Verified Root Cause:
- `RUN_PHASE49_3I_LOCAL_GATE.ps1` was UTF-8 without BOM.
- it contained Persian strings and an em dash.
- Windows PowerShell 5.1 decoded the BOM-less script using legacy ANSI semantics.
- the UTF-8 em-dash bytes became mojibake containing a smart quote; PowerShell treats smart quotes as quote delimiters, so a string terminated early and later ASCII `)` / `<` tokens became parse errors.
- Linux modern `pwsh` CI decoded UTF-8 correctly, so the old parse check missed this compatibility boundary.

Correct Fix — v49.3I.1:
- canonical Windows runner is ASCII-only.
- runner marker: `ASCII_ONLY_FOR_WINDOWS_POWERSHELL_5_1`.
- manual QA output inside the runner uses ASCII text only.
- Persian UI labels remain in the actual application and documentation.
- dedicated CI reads raw runner bytes and fails if any byte is `>127`, then parses the ASCII runner and verifies the version/chain/Production guard.

Safety:
- no DB operation happened before the parse failure.
- no migration, reset, delete, publish or Production action happened.
- hotfix changes only runner/CI compatibility, not application behavior or database schema.

Canonical error: `ERR-49-016`.

## Database Safety
- Django migration for Phase49.3I: NONE
- `makemigrations --check --dry-run`: PASS / no changes
- Candidate review table: local Catalog SQLite only, additive `CREATE TABLE IF NOT EXISTS`
- runner hotfix: no DB change
- no reset/drop/truncate/delete
- historical rows/media are not mass rewritten
- Production database untouched

## GitHub Verification
### Original Phase49.3I validation
- PR #42 closed without merge
- Dedicated Phase49.3I `32569551060` — SUCCESS
- Phase49.3H `32569551053` — SUCCESS
- Phase49.3G `32569551048` — SUCCESS
- Full Phase49 + Full Django `32569551034` — SUCCESS

### Runner encoding hotfix validation
CI-only PR #44: CLOSED / NOT MERGED.
Validated runtime/base SHA: `451bcb9e264b847259a6ea0414550e4f80afa250`.

Runs:
- Dedicated Phase49.3I: `32570978818` — SUCCESS
- Phase49.3H regression: `32570978800` — SUCCESS
- Phase49.3G regression: `32570978829` — SUCCESS
- Full Phase49 + Full Django: `32570978799` — SUCCESS

Hotfix coverage includes:
- raw-byte ASCII-only runner contract
- PowerShell parse contract
- runner version `49.3I.1`
- chain to 49.3H
- Production guard
- all Phase49.3I dedicated runtime tests
- migration drift check
- launcher markers
- mature 49.3H / 49.3G / Phase49 regressions
- full Django suite

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
1. final docs-closed GitHub validation of the hotfix state
2. Windows clean-worktree verification
3. `git fetch --prune` + `git pull --ff-only` from Epic
4. verify runner `49.3I.1`
5. run repository `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`
6. manual MakerWorld `cake+stand` preview QA
7. approve one candidate with chosen image limit
8. archive one candidate and verify blocked/no-full-fetch
9. repeat search and verify imported/blocked duplicate guard
10. validate lightweight Products list and Product Workspace routing
11. validate Fixed / Range / Formula pricing modes
12. one LOCAL PUBLISH ONLY + Local Django E2E
13. explicit owner approval
14. only then Production plan/deploy

## Delivery Gate
Hotfix implementation + CI are complete. Next execution gate is Windows Local rerun from the exact final GitHub-validated Epic HEAD. Production remains forbidden until Local approval.
