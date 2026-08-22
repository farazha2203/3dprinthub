# PROJECT_CONTEXT — 3DPrintHub

> Operational Source of Truth snapshot. Repository/GitHub is authoritative. Latest verified CI/Windows/Host output and real migration/data state override stale text.

## 1) Project / Git / Paths
- Repository: `farazha2203/3dprinthub`
- Active branch: `epic/phase49-unified-product-slider-sync`
- Windows root: `D:\projects\3DPrintHub`
- Windows venv: `D:\projects\3DPrintHub\.venv`
- Catalog Center: `D:\projects\3DPrintHub\catalog_center`
- Django local DB: `D:\projects\3DPrintHub\db.sqlite3`
- Catalog persistent root: `D:\projects\3dprinthub-catalog-manager`
- Catalog SQLite: `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`
- Backups: `D:\projects\3dprinthub-backups`
- Production root: `/home/sfkilvrs/3dprinthub`
- Production venv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`
- Production DB: MySQL `sfkilvrs_EmiAdmin_3dprinthub`

## 2) Mandatory Delivery
`GitHub → CI → Windows pull --ff-only → repository Local Gate → Manual QA → LOCAL PUBLISH E2E → explicit owner approval → Production backup/deploy → Production verification`

No standalone Chat project files, no direct Production edits, no destructive reset/DB/media cleanup, no Production before explicit Local approval.

## 3) Current Phase
Epic chain ends at `Phase49.3I`.

Current phase:
`Phase49.3I — Discovery Review + Product Gallery + Explicit Pricing Modes`

Current handoff hotfix:
`49.3I.3 — live GitHub snapshot guard after stale Chat-pinned Expected HEAD failure`

Status:
`GITHUB_UPDATED / HANDOFF HOTFIX CI PENDING / WINDOWS RERUN BLOCKED UNTIL CI`

Active phase doc:
`docs/phases/PHASE49_3I_DISCOVERY_REVIEW_PRODUCT_LIST_PRICING.md`

## 4) Catalog Center Baseline
- Catalog Center version: `8.7.1`
- Canonical detailed editor: Epic49 Product Workspace
- Canonical Windows runner: `RUN_PHASE49_3I_LOCAL_GATE.ps1`
- Runner version: `49.3I.3`
- Encoding contract: `ASCII_ONLY_FOR_WINDOWS_POWERSHELL_5_1`
- Runner chain: `49.3I → 49.3H → 49.3G → 49.3F.1 → 49.3E → 49.3D/base`
- Local and Production publish targets remain separate/fail-closed.

## 5) Phase49.3I Discovery Contract
- explicit operator HTTP(S) search/listing URL is authoritative
- Preview first: one thumbnail + title + source identity/link only
- Full Fetch only after operator approval
- image limit 1..20; default 10, hard max 20
- Archive/Not Needed preserves blocked identity without full fetch
- source + external ID + normalized URL prevent duplicate full fetch
- scraped unexpected scripts are normalized; URLs and Persian `_fa` editorial fields remain protected

## 6) Products Page Contract — Corrected by Windows Local QA
Owner requirement:
- Products page is a visual gallery
- each card exposes only image + product name + Edit Product
- click image → large preview
- detailed fields only in Product Workspace

`ERR-49-017` root cause:
- first 49.3I patch wrapped `App87._products_ui`
- real UX87 shell calls `super()._products_ui()` then `_modernize_products_page()`
- patch therefore never controlled the actual shell surface

Current fix:
- wrap real `_modernize_products_page` boundary
- hide entire mature legacy Panedwindow but keep widgets alive for compatibility
- responsive vertically scrollable gallery
- 260x190 local thumbnails
- local-only resolution: strict local mapping → `page_extract.json` → `local_dir/images`
- batched Tk `after()` thumbnail loading
- click image → large local preview up to 1000x720
- card fields are exactly `thumbnail/title/edit`

## 7) AI Execution Contract — Corrected by Windows Local QA
Protected 49.3H baseline:
- SEO/AI progress + persistent Result/Error drawer
- per-product AI/SEO cost ledger
- selected-image text-only privacy
- errors sanitized, unsupported provider cost remains unknown

`ERR-49-018` root cause:
- 49.3F performed synchronous save/preflight/source preparation before constructing `AIProgress`
- network was threaded but no progress window existed during that preflight

Current fix:
- `phase49_3i_local_qa_hotfix.py` paints startup progress immediately
- mature AI flow begins via Tk `after(80)` after first paint
- startup UI hands off to the existing 49.3H progress UI
- Provider/Model/network worker/request/result/error/cost/audit logic is not duplicated or replaced

## 8) Pricing Contract
1. `fixed`: exact final amount
2. `range`: explicit min/max consultation range
3. `dynamic`: existing ProductVariant formula engine

Dynamic Source of Truth remains `ProductVariant.price_breakdown()` + cached Variant unit price.

Phase49.3I does not mutate Django field choices; semantic `range` is stored in existing CharField without a new migration (`ERR-49-015`).

## 9) Windows Runner Compatibility
Historical `ERR-49-016`: BOM-less UTF-8 runner with Persian/em-dash failed under Windows PowerShell 5.1 legacy decoding.

Current encoding contract:
- runner v49.3I.3 remains ASCII-only
- CI rejects non-ASCII runner bytes
- PowerShell parse/chain/Production guard remains protected

## 10) Windows GitHub Handoff Contract — 49.3I.3
Incident `ERR-49-019`:
- Windows clean-worktree fetch/pull correctly advanced Local from `fee6a5f...` to GitHub HEAD `53e9216ae84a3e167481253da44760179c751051`.
- the Chat preflight still pinned obsolete SHA `789edf8652ad8a09641afedd5e959c63822800c7` and falsely failed after the correct pull.

Verified evidence:
- final validated runtime/docs base before this incident: `97674a82acc97e1a623b76084b60344cfa93142b`.
- GitHub compare to Windows-pulled `53e9216...` shows seven later commits touching only `PROJECT_CONTEXT.md` and `docs/*`.
- no runtime, migration, DB, media or Production surface changed in those seven commits.

Permanent handoff rule in runner v49.3I.3:
1. clean worktree required,
2. exact Epic branch required,
3. live `git fetch --prune origin`,
4. resolve fetched `origin/epic/phase49-unified-product-slider-sync`,
5. require Local HEAD == fetched Remote HEAD,
6. mismatch → fail closed + `git pull --ff-only` instruction + rerun,
7. never use a Chat-pinned SHA as sole mutable-branch handoff truth.

CI now checks this handoff contract through `PHASE49_3I_GIT_SNAPSHOT=OK` and runner source guards.

## 11) Previous Final GitHub Validation
CI-only PR #47: `CLOSED / NOT MERGED`.
Exact validated Epic runtime/docs base:
`97674a82acc97e1a623b76084b60344cfa93142b`

SUCCESS:
- Phase49.3I `32573779531`
- Phase49.3H `32573779534`
- Phase49.3G `32573779548`
- Full Phase49 + Full Django `32573779528`
- Full Django suite step PASS
- no migration drift

Runner at that gate was v49.3I.2. The later 49.3I.3 runner/workflow handoff safety change requires fresh CI before Windows rerun.

## 12) Database / Safety
Previously applied Windows migrations remain:
- `store.0031`
- `store.0032`
- `website.0022`
- `store.0033`
- `website.0023`

Phase49.3G/3H/3I/3I.3 add no Django migration.
No reset/drop/truncate/delete, no historical media/data rewrite, Production DB/source untouched.

## 13) Known Separate Items
- Local `/api/v1/catalog/sitemap/` 404 remains separate before Epic closure.
- CKEditor4 warning/debt separate.
- Production realtime/Redis architecture warning separate.
- Pillow `Image.getdata()` deprecation non-blocking.

## 14) Production
**UNTOUCHED / NOT APPROVED / NOT DEPLOYED for Phase49.3C..49.3I.3.**

Before any Production action re-verify host path, branch/commit, worktree, venv, MySQL vendor/name, `.env`, backup and rollback.

## 15) Exact Next Gate
```text
49.3I.3 GitHub CI
→ Windows clean-worktree check
→ git fetch --prune origin
→ git pull --ff-only current Epic branch
→ run .\RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp v49.3I.3
→ runner performs its own live fetch and verifies Local HEAD == fetched Remote HEAD
→ Products gallery image/name/edit-only QA + large preview
→ full AI autofill immediate startup progress → 49.3H progress/result drawer
→ MakerWorld cake+stand Preview/Approve/Archive/Dedupe
→ image cap + Fixed/Range/Formula QA
→ LOCAL PUBLISH ONLY
→ Local Django E2E
→ explicit owner approval
→ Production plan only after approval
```

Any new Local regression is fixed at Root Cause on GitHub with regression coverage; no manual Windows source patch.
