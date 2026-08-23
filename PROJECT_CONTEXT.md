# PROJECT_CONTEXT — 3DPrintHub

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.8 — Observable AI Execution Recovery`
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

49.3I.7 corrected the Playwright Preview expression (`ERR-49-024`) without rewriting mature Direct Product/approved Full Fetch. 49.3I.8 preserves that recovery. Real Windows MakerWorld Preview QA is still required.

## AI Provider Hub Contract
Current Provider cards:
- AvalAI,
- OpenRouter,
- Google Gemini Direct,
- OpenAI Direct.

The existing `AIProviderClient` / Google adapter remains authoritative for model APIs.

49.3I.7 (`ERR-49-025`) hydrates the real per-provider card keys from Windows Credential Store, rehydrates after secure Save, preserves FTP/Bridge credentials, and background-loads provider model catalogs into existing Model ID controls/cache. Secrets remain outside SQLite/Git/source/logs.

## Observable AI Execution — ERR-49-026
Latest Windows screenshot/QA showed the bottom `تکمیل هوشمند همه فیلدهای AI` could sit on AvalAI content generation for roughly five minutes without useful execution visibility.

Verified boundary:
- that exact Phase49.3C operator action still called legacy `ProductStudio.generate_ai("commerce")`,
- it bypassed mature `_phase49_3e_run_ai()`,
- therefore it bypassed the already-implemented 49.3I first-paint and 49.3F/3H connection/send/receive/result/error/cost Task Center.

49.3I.8:
- routes the real bottom All-Fields action to mature `_phase49_3e_run_ai("all")`,
- routes non-Quick stage actions through the same Task Center while images retain image scope,
- preserves Quick/title-only behavior,
- creates no parallel AI client/network worker,
- keeps immediate first-paint,
- adds elapsed time + `توقف انتظار`,
- adds a 210-second operator watchdog aligned with the existing single-request timeout bound,
- cancel/timeout invalidates the execution generation,
- stale late full/image results cannot mutate product data,
- errors/results remain visible and the app stays open.

The blocking HTTP worker is not force-killed; after cancel/timeout it may finish in the background, but its result is stale and discarded.

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
Canonical runner: `RUN_PHASE49_3I_LOCAL_GATE.ps1` v49.3I.8.
- ASCII-only Windows PowerShell 5.1,
- clean exact Epic branch,
- live `git fetch --prune origin`,
- Local HEAD equals fetched Remote Epic HEAD,
- no fixed Chat SHA as sole truth,
- no reset/stash/delete shortcut.

## Latest GitHub Validation — 49.3I.8
CI-only PR #53: `CLOSED / NOT MERGED`.
Validated runtime base: `3fdab5dc4a56204b6370f72df04ec0956e8ba6ce`.
Marker head: `0d05d0fb25f02daa07df93f9cf47d2ea0333b8b8` — not merged.

Successful runs:
- Phase49.3I `32620646603` — SUCCESS,
- Phase49.3H `32620646600` — SUCCESS,
- Phase49.3G `32620646605` — SUCCESS,
- Full Phase49 + Full Django `32620646657` — SUCCESS.

Django migration: NONE.
Catalog schema migration: NONE.
Production untouched.

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
- ERR-49-025 real Provider Hub key/model visibility,
- ERR-49-026 real All-Fields AI action bypassed mature Task Center.

Always inspect `docs/ERRORS.md` before troubleshooting.

## Current Windows Acceptance Gate
1. close Catalog Center and pull current Epic using live fetch + ff-only,
2. run v49.3I.8 gate with `-LaunchApp`,
3. click the **bottom** All-Fields AI action,
4. immediate startup progress must paint,
5. mature progress must show connection/send/wait/receive/save/result-error,
6. elapsed time + Stop Waiting remain visible; app stays responsive,
7. Stop/210s timeout makes any later result stale/non-applicable,
8. exact MakerWorld Search Preview returns candidates without JS syntax error,
9. Preview remains one-thumbnail/basic identity only,
10. approve candidate with image limit 20 then mature Full Fetch,
11. archive candidate → no Full Fetch,
12. Provider keys/model lists + FTP/Bridge remain available,
13. Product open/selection and Fixed/Range/Formula regressions pass.

Only then: one `LOCAL PUBLISH ONLY` → Local Django E2E → explicit owner approval → Production backup/deploy/verify.
