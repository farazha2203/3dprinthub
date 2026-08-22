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
- [x] 49.3H SEO Execution Console + AI Cost Ledger + Controlled Image Acquisition — GitHub CI SUCCESS
- [x] 49.3I Discovery Review Queue + Product Gallery + Explicit Pricing Modes — GitHub CI SUCCESS
- [x] 49.3I.1 Windows PowerShell 5.1 Runner Encoding Hotfix — GitHub CI SUCCESS
- [x] 49.3I.2 Local QA Regression Hotfix: real UX87 product gallery + AI first-paint — GitHub CI SUCCESS
- [x] 49.3I.2 docs-closed final GitHub validation — PR #47 CLOSED / NOT MERGED; all required workflows SUCCESS
- [x] ERR-49-019 root cause verified: stale Chat-pinned Expected HEAD after valid GitHub branch advancement
- [x] 49.3I.3 Git snapshot handoff guard implemented on GitHub
- [ ] 49.3I.3 CI validation
- [ ] Windows Local Gate + visual/data QA
- [ ] LOCAL PUBLISH ONLY + Local Django E2E
- [ ] Owner acceptance
- [ ] Production deploy + verification

## Phase49.3I Delivered Contract
- operator-supplied search/listing URL is authoritative
- discovery creates a lightweight review queue first: one thumbnail + title + source identity/URL
- no full product extraction before operator approval
- approved candidates full-fetch with image cap `1..20` (default 10)
- archive/not-needed candidates become blocked without full extraction
- duplicate/blocked source identity is fail-closed before full fetch
- source text is normalized before persistence while URLs and Persian editorial `_fa` fields remain protected
- pricing modes are independent: Fixed / Range / Formula(Dynamic)

## Products Gallery Contract — 49.3I.2
- real UX87 composition boundary is `_modernize_products_page`
- complete legacy table/editor pane remains alive only for compatibility and is hidden from the operator surface
- Products page is a responsive scrollable card gallery
- each card exposes only: large local image, product name, Edit Product action
- price, title fields, status fields and other editor parameters are not displayed on the Products list surface
- click product image opens a large local preview
- detailed editing routes to Product Workspace
- thumbnails are local-only and loaded in small Tk `after()` batches

## AI First-Paint Contract — 49.3I.2
- full AI autofill paints a startup progress window before synchronous save/preflight preparation
- existing 49.3F AI flow begins after a short Tk event-loop yield
- startup window hands off to the existing 49.3H AI progress window
- existing Provider/Model/network worker/result/error drawer/cost ledger/audit remain unchanged
- no parallel AI request implementation is introduced

## Git Handoff Contract — 49.3I.3
Root cause: a fixed Expected HEAD copied into Chat became stale after the mutable Epic branch advanced with later documentation commits. Windows correctly fast-forwarded to current GitHub HEAD, then the stale Chat constant falsely blocked the handoff (`ERR-49-019`).

Canonical rule now:
1. Windows worktree must be clean.
2. exact Epic branch is required.
3. repository runner performs live `git fetch --prune origin`.
4. runner reads the fetched `origin/epic/phase49-unified-product-slider-sync` snapshot.
5. Local HEAD must equal that fetched Remote HEAD.
6. mismatch fails closed and instructs `git pull --ff-only` then rerun.
7. no Chat-pinned SHA is the sole handoff source of truth.
8. no reset/stash/delete shortcut.

Runner version: `49.3I.3`.
CI contract checks live fetch, branch guard, remote-ref guard, ASCII-only Windows PowerShell 5.1 compatibility and `PHASE49_3I_GIT_SNAPSHOT=OK`.

## Previous Final GitHub Validation
CI-only PR #47: CLOSED / NOT MERGED.
Exact validated Epic runtime/docs base: `97674a82acc97e1a623b76084b60344cfa93142b`.

SUCCESS:
- Phase49.3I Run `32573779531`
- Phase49.3H Run `32573779534`
- Phase49.3G Run `32573779548`
- Full Phase49 + Full Django Run `32573779528`

GitHub compare from that validated base to Windows-pulled HEAD `53e9216ae84a3e167481253da44760179c751051` contains only `PROJECT_CONTEXT.md` and `docs/*`; runtime/migrations/database/media were unchanged.

## Pricing Contract
1. `fixed`: exact operator price, e.g. 1,200,000 toman.
2. `range`: operator min/max, e.g. 200,000–500,000 toman; non-final/consultation behavior.
3. `dynamic`: formula from material grams/rates + print time + supervision/other configured charges using existing Variant pricing source of truth.

## Must Not Regress
- 49.3H SEO result/error console and AI cost ledger
- immediate AI progress feedback
- image intake default 10 / hard max 20
- selected-image-only + text-only image SEO
- AI provenance/manual override rules
- Product page gallery list contract: image/name/edit only
- dynamic pricing source of truth in ProductVariant
- Local vs Production publish separation
- revision/idempotency guards
- Persian content integrity
- Hero/Product sync contracts
- secure secret handling
- Windows PowerShell 5.1-safe Local Gate runner
- live fetched GitHub snapshot handoff guard

## Remaining Gates Before Production
1. validate 49.3I.3 runner/workflow in GitHub CI.
2. Windows clean-worktree safety check.
3. fetch + fast-forward pull current Epic branch.
4. run `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp` v49.3I.3; runner re-fetches and verifies Local == fetched Remote snapshot.
5. verify Products gallery images/name/edit-only + large image preview.
6. verify full AI autofill immediate startup progress → mature 49.3H progress/result drawer.
7. MakerWorld `cake+stand` Preview/Approve/Archive/Dedupe QA using IDs `2834255` and `2845731`.
8. validate image cap and Fixed / Range / Formula modes.
9. real LOCAL PUBLISH ONLY.
10. Local Django E2E.
11. explicit user approval.
12. only then verified Production backup/deploy/restart/smoke.

## Deferred / Separate
- `/api/v1/catalog/sitemap/` local 404 root cause
- CKEditor4 debt
- Production Redis/realtime architecture warning
- Pillow `Image.getdata()` deprecation

## Next Recommended Task
Complete Phase49.3I.3 CI validation. After success, Windows pulls the current Epic branch and runs the repository runner v49.3I.3. Production remains out of scope until Local approval.
