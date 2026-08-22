# PROJECT_CONTEXT — 3DPrintHub

Updated: 2026-08-22
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.7 — Preview + Provider Hub Recovery`
Status: `FINAL CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Operating Rule
GitHub/Repository is the permanent source of truth.
Required flow:
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI → WINDOWS PULL --FF-ONLY → LOCAL GATE → MANUAL QA → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION BACKUP/DEPLOY/VERIFY`

No direct Production source edits. No ZIP/Patch/source delivery through Chat. Dirty Local/Host stops for inspection; no reset/stash/delete shortcut.

## Canonical Paths
Windows project: `D:\projects\3DPrintHub`
Windows Catalog Center: `D:\projects\3DPrintHub\catalog_center`
Windows venv: `D:\projects\3DPrintHub\.venv`
Windows Django DB: `D:\projects\3DPrintHub\db.sqlite3`
Windows Catalog persistent root: `D:\projects\3dprinthub-catalog-manager`
Windows Catalog DB: `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`
Windows backups: `D:\projects\3dprinthub-backups`
Production project: `/home/sfkilvrs/3dprinthub`
Production venv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`
Production DB: MySQL `sfkilvrs_EmiAdmin_3dprinthub`

Always re-read `docs/PATHS.md` and `docs/HOST_CONSTRAINTS.md` before environment/deployment work.

## Current Discovery Contract
- explicit Search/Listing/Category URL is authoritative,
- configured source `model_url_pattern` is Product-vs-Group boundary,
- Product URL → mature direct intake,
- Group/Category/Search/sub-branch → Preview Candidate first,
- Preview stores source identity/basic title/one thumbnail only,
- Full Fetch only after approval,
- image limit default 10 / hard max 20,
- Archive/Not Needed does not Full Fetch,
- dedupe: source + external id + normalized URL.

Owner already confirmed URL/sub-branch routing is fixed.

## Current Regression Fix — ERR-49-024
Windows log showed Preview reached the exact MakerWorld target but failed with:
`Locator.evaluate_all: SyntaxError: Invalid or unexpected token`.

Root cause: Python converted an intended JavaScript `\n` escape inside a normal triple-quoted string into a literal newline before Playwright evaluated it.

49.3I.7 adds `phase49_3i_preview_recovery.py` with a raw JavaScript source string and patches only Stage-1 Preview. Mature `discover_classic` / `collect_classic_exact` full extraction is untouched.

## AI Provider Hub Contract
Current Provider cards:
- AvalAI,
- OpenRouter,
- Google Gemini Direct,
- OpenAI Direct.

The existing `AIProviderClient` / Google adapter remains authoritative for model APIs.

## Current Regression Fix — ERR-49-025
49.3I.6 hydrated legacy AI/connection fields, but the real Phase49.3F Provider Hub uses `_ai_hub_key_vars` and its mature Save clears those variables after secure persistence.

49.3I.7:
- hydrates real per-provider card keys from Windows Credential Store,
- rehydrates after mature secure Save,
- preserves FTP password + Bridge token persistence,
- hydrates stored management/admin masked fields,
- background-loads configured Provider model catalogs into existing Model ID controls/cache,
- keeps manual model picker/API refresh,
- never writes secrets to SQLite/Git/source/logs.

## Products Explorer / Workspace
Preserved:
- Product Workspace is canonical detailed editor,
- Explorer cards show image/name/ID/state/source/image-count/date/publish-state,
- Extra Large/Large/Medium/Small/List views,
- normal/Ctrl/Shift selection,
- context actions,
- selection-loop guard,
- safe Remove From Publish Queue only changes local queue state.

## AI / Pricing
- immediate AI first-paint before synchronous preflight,
- mature 49.3H result/error/cost stack,
- no fabricated provider cost,
- Fixed / Range / Formula independent,
- Range never invokes Formula.

## Windows Delivery Contract
Canonical runner: `RUN_PHASE49_3I_LOCAL_GATE.ps1` v49.3I.7.
- ASCII-only Windows PowerShell 5.1,
- clean exact Epic branch,
- live `git fetch --prune origin`,
- Local HEAD equals fetched Remote Epic HEAD,
- no fixed Chat SHA as sole truth,
- no reset/stash/delete shortcut.

## Latest GitHub Validation
CI-only PR #52: `CLOSED / NOT MERGED`.
Validated runtime base: `4e0b1b7f0f8934a03ab74037bdce5f9abe55b425`.
Marker head: `5097f45f069e40af64d452ffaa8cd07399a977f2` — not merged.

Runs:
- Phase49.3I `32585956198` — SUCCESS
- Phase49.3H `32585956149` — SUCCESS
- Phase49.3G `32585956156` — SUCCESS
- Full Phase49 + Full Django `32585956155` — SUCCESS

Django migration: NONE.
Catalog schema migration: NONE.
Post-validation commits are documentation-only.

## Relevant Error Knowledge
- ERR-49-013 exact Search URL ignored,
- ERR-49-014 full fetch before review,
- ERR-49-018 AI first-paint,
- ERR-49-019 stale Chat SHA,
- ERR-49-020 clipped thumbnails,
- ERR-49-021 Product-vs-Group routing,
- ERR-49-022 Treeview selection loop,
- ERR-49-023 legacy secure-field hydration,
- ERR-49-024 Preview JavaScript escape regression,
- ERR-49-025 real Provider Hub key/model visibility.

Always inspect `docs/ERRORS.md` before troubleshooting.

## Current Windows Acceptance Gate
1. pull current Epic with live fetch + ff-only,
2. run v49.3I.7 gate with `-LaunchApp`,
3. FTP password + Bridge token stay masked after Save/restart,
4. AvalAI/OpenRouter stored keys stay masked in real Provider cards,
5. configured Provider model lists load and can be selected,
6. exact MakerWorld Search Preview returns candidates without JS syntax error,
7. Preview remains one-thumbnail/basic-identity only,
8. approve candidate with requested image limit (20 allowed) then Full Fetch,
9. archive candidate → no Full Fetch,
10. direct Product URL still works,
11. Product open, AI progress, Fixed/Range/Formula regressions pass.

Only then: one `LOCAL PUBLISH ONLY` → Local Django E2E → explicit owner approval → Production backup/deploy/verify.
