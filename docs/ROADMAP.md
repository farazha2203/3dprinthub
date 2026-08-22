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
- [ ] 49.3I Discovery Review Queue + Product List Simplification + Explicit Pricing Modes — IN_PROGRESS

## Phase49.3I Requested Delta
- operator-supplied search/listing URL is authoritative; do not silently replace it with configured default listing
- discovery first creates a lightweight review queue: one thumbnail + source title + source identity/URL
- no full product extraction before operator approval
- operator can approve selected candidates, choose image cap 1..20, then fetch full data
- archive/not-needed candidates become blocked without full extraction
- duplicate/blocked source identity remains fail-closed and is not re-fetched
- scraped source text is normalized to Latin/English-safe text before persistence; URLs are untouched; Persian editorial fields remain Persian
- products/work queue is simplified to thumbnail + title + Product Page/Workspace action; detailed editing remains in Product Workspace
- pricing modes are explicit and separate: Fixed / Range / Formula(Dynamic)

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

## Gates Before Production
1. GitHub implementation + regression tests
2. GitHub dedicated Phase49.3I CI + Full Phase49/Django regression
3. Windows `git pull --ff-only`
4. repository Phase49.3I Local Gate runner
5. Manual Visual/Data QA using the MakerWorld `cake+stand` search URL
6. approve one candidate and archive one candidate; verify no duplicate/full-fetch for blocked item
7. validate image cap and all 3 pricing modes
8. real LOCAL PUBLISH ONLY
9. Local Django E2E
10. explicit user approval
11. verified production backup/deploy/migrate/collectstatic/restart/smoke

## Deferred / Separate
- `/api/v1/catalog/sitemap/` local 404 root cause
- CKEditor4 debt
- Production Redis/realtime architecture warning

## Next Recommended Task
Implement and CI-validate Phase49.3I on GitHub. Production remains out of scope until Local approval.
