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
- [x] 49.3H SEO Execution Console + AI Cost Ledger + Controlled Image Acquisition — GitHub CI SUCCESS; Windows Local QA pending
- [x] 49.3I Discovery Review Queue + Product List Simplification + Explicit Pricing Modes — GitHub CI SUCCESS
- [x] 49.3I.1 Windows PowerShell 5.1 Runner Encoding Hotfix — GitHub CI SUCCESS; Windows rerun pending

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

## Runner Hotfix Contract
Observed Windows failure:
- GitHub sync to validated `91f39681...` succeeded.
- `RUN_PHASE49_3I_LOCAL_GATE.ps1` then failed at parse time under Windows PowerShell 5.1.
- Persian text appeared as mojibake and later manual-QA lines produced `Unexpected token ')'`.

Root Cause:
- BOM-less UTF-8 PowerShell script contained Persian text and an em dash.
- Windows PowerShell 5.1 decoded the file using legacy ANSI semantics.
- the em-dash byte sequence became mojibake containing a smart quote treated as a PowerShell quote delimiter.

Permanent fix:
- canonical runner version `49.3I.1` is ASCII-only.
- CI reads raw bytes and rejects any non-ASCII byte in this Windows runner.
- CI marker: `ASCII_ONLY_FOR_WINDOWS_POWERSHELL_5_1`.
- no database/runtime/Production behavior changed.

Hotfix validation:
- CI-only PR #44 closed / not merged
- Phase49.3I Run `32570978818` — SUCCESS
- Phase49.3H Run `32570978800` — SUCCESS
- Phase49.3G Run `32570978829` — SUCCESS
- Full Phase49 + Full Django Run `32570978799` — SUCCESS
- runtime/base SHA `451bcb9e264b847259a6ea0414550e4f80afa250`

## Pricing Contract
1. `fixed`: exact operator price, e.g. 1,200,000 toman.
2. `range`: operator min/max, e.g. 200,000–500,000 toman; non-final/consultation behavior remains the existing range contract.
3. `dynamic`: formula from material grams/rates + print time + supervision/other configured charges using the existing Variant pricing source of truth.

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
- Windows PowerShell 5.1-safe canonical Local Gate runner

## Remaining Gates Before Production
1. final docs-closed GitHub hotfix validation
2. Windows `git status --short` safety check
3. Windows `git fetch --prune` + `git pull --ff-only`
4. verify `RUN_PHASE49_3I_LOCAL_GATE.ps1` version `49.3I.1`
5. run repository `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`
6. Manual Visual/Data QA using the MakerWorld `cake+stand` search URL
7. approve one candidate and archive one candidate; verify no duplicate/full-fetch for blocked item
8. validate image cap and all 3 pricing modes
9. real LOCAL PUBLISH ONLY
10. Local Django E2E
11. explicit user approval
12. verified production backup/deploy/migrate/collectstatic/restart/smoke

## Deferred / Separate
- `/api/v1/catalog/sitemap/` local 404 root cause
- CKEditor4 debt
- Production Redis/realtime architecture warning

## Next Recommended Task
After final GitHub validation of the documentation-closed runner hotfix, Windows pulls the exact validated Epic HEAD and reruns `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`. Production remains out of scope until Local approval.
