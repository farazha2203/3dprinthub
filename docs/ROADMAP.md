# PROJECT ROADMAP

Last Updated: 2026-08-22
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`

## Goal
Unified 3DPrintHub catalog workflow from Windows discovery/review/edit/AI/SEO/pricing/hero through controlled Batch/Bridge sync into Django Store/Admin, with safe Local/Production separation and auditable operations.

## Epic49 Path
- [x] 49.2A / 49.2B / 49.2C foundations
- [x] Epic49 unified product/slider sync
- [x] 49.3A readiness
- [x] 49.3B guided AI / hero / diagnostics
- [x] 49.3C operator recovery + Persian content integrity
- [x] 49.3D workflow hardening + runner hotfix
- [x] 49.3E AI task completion/recovery
- [x] 49.3F product intelligence / dynamic pricing / AI UX
- [x] 49.3F runtime redaction + 49.3F.1 native capture hotfix
- [x] 49.3G workspace usability + AI provenance — GitHub CI complete
- [x] 49.3H SEO Execution Console + AI Cost Ledger + Controlled Image Acquisition — GitHub CI SUCCESS; Windows Local Gate/QA pending
- [x] 49.3I Discovery Review Queue + Product List Simplification + Explicit Pricing Modes — GitHub CI SUCCESS; Windows Local Gate/QA pending

## Phase49.3I Delivered Contract
- operator-supplied search/listing URL is authoritative; configured default listing cannot silently replace it
- discovery creates a lightweight review queue first: one thumbnail + title + source identity/URL
- no full product extraction before operator approval
- approved candidates full-fetch with operator image cap `1..20` (default 10)
- archive/not-needed candidates become blocked without full extraction
- duplicate/blocked source identity is fail-closed before full fetch
- scraped source text is normalized to Latin/English-safe text before persistence; URLs remain exact; Persian editorial fields remain Persian
- Products/work queue is lightweight and detailed editing routes to Product Workspace
- pricing modes are explicit and independent: Fixed / Range / Formula(Dynamic)

## Pricing Contract
1. `fixed`: exact operator price, e.g. 1,200,000 toman.
2. `range`: operator min/max, e.g. 200,000–500,000 toman; non-final/consultation behavior remains the existing range contract.
3. `dynamic`: formula from material grams/rates + print time + supervision/other configured charges using the existing Variant pricing source of truth.

## Phase49.3I GitHub Gates
- Dedicated 49.3I CI Run `32569551060` — SUCCESS
- 49.3H regression Run `32569551053` — SUCCESS
- 49.3G regression Run `32569551048` — SUCCESS
- Full Phase49 + Full Django Run `32569551034` — SUCCESS
- Runtime base validated by final CI probe: `9d462f1ec12b00727c96acf9d4f59b4723d676b4`
- PR #42: CI-only / closed / not merged

## Must Not Regress
- Phase49.3H SEO execution result/error console and AI cost ledger
- image intake default 10 / hard max 20
- selected-image-only + text-only image SEO
- manual override/provenance rules
- dynamic pricing source of truth in ProductVariant
- Local vs Production publish separation
- revision/idempotency guards
- Persian content integrity
- Hero/Product sync contracts
- secure secret handling

## Remaining Gates Before Production
1. Windows `git status --short` safety check
2. Windows `git fetch --prune` + `git pull --ff-only`
3. Run repository `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`
4. Manual Visual/Data QA using the MakerWorld `cake+stand` search URL
5. approve one candidate and archive one candidate; verify no duplicate/full-fetch for blocked item
6. validate image cap and all 3 pricing modes
7. real LOCAL PUBLISH ONLY
8. Local Django E2E
9. explicit user approval
10. verified production backup/deploy/migrate/collectstatic/restart/smoke

## Deferred / Separate
- `/api/v1/catalog/sitemap/` local 404 root cause
- CKEditor4 debt
- Production Redis/realtime architecture warning

## Next Recommended Task
Windows Local Gate + manual Phase49.3I QA from the GitHub branch. Production remains out of scope until Local approval.
