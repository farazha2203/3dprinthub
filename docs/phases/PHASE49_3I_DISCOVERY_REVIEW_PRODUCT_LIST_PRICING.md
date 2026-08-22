# Phase49.3I — Discovery Review Queue + Product List Simplification + Explicit Pricing Modes

Status: IN_PROGRESS
Approved: 2026-08-22
Branch: `epic/phase49-unified-product-slider-sync`
Phase49.3H validated baseline: `e145d1e11619e36bd766788083bee59899a80cbb`
Production: UNTOUCHED / NOT APPROVED

## Why
The current classic discovery path immediately performs full extraction after URL discovery. For MakerWorld `mode=search`, it also ignores an operator-supplied search URL and scans the configured first listing instead. This can produce unrelated products and spends time/bandwidth before human review.

The main products page still duplicates a large editor although Epic49 Product Workspace is already the canonical editing surface. Pricing also visually conflates operator-entered price range with formula/dynamic calculation.

## Requested Delta

### A. Exact Search / Listing Contract
- If `seed` is an explicit HTTP(S) listing/search URL, use it as the authoritative discovery page.
- For MakerWorld search `https://makerworld.com/en/search/models?keyword=cake+stand`, do not replace it with configured popular/download listings.
- Extract only product/model links matching the source model pattern.
- Deduplicate by `(source_code, external_id)` and normalized source URL.

### B. Two-Stage Acquisition
Stage 1 — Preview:
- discover candidate model links
- capture one representative thumbnail from the listing card when available
- capture source title/basic identity only
- persist local review candidate state, not a full product
- do not fetch all product text/specs/images/files yet

Stage 2 — Approved Full Fetch:
- operator selects candidate(s)
- operator chooses image limit `1..20` (default 10)
- full extraction runs only for approved candidates
- 49.3H image cap applies to persisted/selected/downloaded images
- source row is upserted once and candidate becomes imported/completed

Archive / Not Needed:
- no full extraction
- create/preserve a minimal blocked identity record sufficient for existing blocked/dedup guards
- candidate state becomes blocked/not_needed
- existing restore workflow remains available

### C. Source Text Safety
Apply only to scraped/source textual payloads before DB persistence:
- Unicode NFKC normalization
- keep Latin-script text, ASCII/common punctuation, digits and whitespace
- remove CJK/Cyrillic/other unexpected script text and emoji/control garbage
- preserve URLs/identifiers exactly
- preserve Persian editorial/AI `_fa` fields; this filter does not apply to those fields
- recursively sanitize textual values in source snapshots/specs/tags where safe, while leaving URL-like strings untouched
- do not mass-rewrite historical rows in this phase

### D. Lightweight Main Products Page
- keep existing database/workflow/product tree and actions internally for compatibility
- hide the embedded giant right-side editor on the main list page
- list focuses on product thumbnail + display name
- one clear `صفحه محصول / ویرایش کامل` action opens the canonical Product Workspace
- double-click still opens Product Workspace
- do not remove Product Workspace fields/features

### E. Explicit Pricing Modes
Expose three separate modes in Product Workspace:
1. `fixed` — exact operator amount. `price_min == price_max`, final price true.
2. `range` — operator min/max. Existing range/consultation contract is used; not a formula calculation.
3. `dynamic` — existing formula/variant engine based on selected materials, grams, print time, supervision and configured rates.

Server/Desktop behavior:
- add `range` to pricing strategy normalization/choices without a new Django migration
- preserve `ProductCatalogProfile.price_mode=range` for range products
- `range` delegates to the mature base price-range importer so consultation/range notes remain correct
- only `dynamic` invokes the formula engine
- fixed and dynamic regressions remain covered

## Touched Surfaces
Expected additive/minimal surfaces:
- new `catalog_center/app/phase49_3i_discovery_review.py`
- new `catalog_center/app/phase49_3i_product_list.py`
- new `catalog_center/app/phase49_3i_pricing_modes.py`
- `catalog_center/launch.py` composition only
- `store/phase49_3f_pricing.py` small range normalization/publish compatibility patch if required by tests
- tests / runner / CI / docs

## Must Not Touch / Regress
- Production source or data
- Phase49.3H result/error console and cost ledger
- image default 10 / hard max 20
- selected-image text-only AI privacy
- Product/Hero revision/idempotency
- AI provenance/manual override
- dynamic Variant pricing source of truth
- local/production publish separation
- Persian content guard
- historical media/catalog data

## Database Safety
- Django migration expected: NONE.
- Candidate review table is local Catalog SQLite only, `CREATE TABLE IF NOT EXISTS` additive.
- No destructive migration/reset/delete/truncate.
- Blocked/archive keeps identity record instead of deleting data.

## Regression / Acceptance Tests
1. Search mode with explicit MakerWorld seed uses seed URL, not `listing[:1]`.
2. MakerWorld candidate fixture includes model IDs `2834255` and `2845731` and deduplicates profile/hash variants.
3. Preview captures at most one thumbnail and performs no full extraction.
4. Approve invokes full extractor exactly once with selected limit 1..20.
5. Archive invokes no full extractor and adds blocked identity.
6. Existing product/blocked identity prevents full fetch on rediscovery.
7. Source sanitizer removes CJK/emoji/unexpected script from source fields, preserves English/digits/punctuation and URLs; Persian `_fa` payload is unchanged.
8. Main products UI has lightweight list + Product Page action; legacy editor remains hidden but available to compatibility code.
9. pricing strategy fixed/range/dynamic round-trip.
10. range min/max remains range/consultation; dynamic uses formula engine; fixed remains exact.
11. 49.3H image cap + selected-image privacy regressions.
12. Phase49.3G provenance regressions.
13. Full Phase49 + Full Django suite.

## Delivery Gate
GitHub implementation -> dedicated CI + Full Phase49 regression -> Windows `git pull --ff-only` -> Phase49.3I runner -> manual MakerWorld cake-stand candidate QA -> approve/archive/duplicate/image-limit/pricing QA -> one LOCAL PUBLISH ONLY -> Local Django E2E -> explicit owner approval -> Production plan.
