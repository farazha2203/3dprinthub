# OWNER REQUESTS

Last Updated: 2026-08-23

## Phase49.3H

### REQ-49H-001 — Unified SEO execution visibility
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / LOCAL QA PENDING`
- every SEO-related action shows execution/result/error state,
- provider/model/request/tokens/cost/log where available,
- sanitized recoverable errors/results.

### REQ-49H-002 — Per-product AI/SEO cost
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / LOCAL QA PENDING`
- record real AI/SEO cost per product where provider data supports it,
- internal publish cost receipt,
- never invent unsupported cost.

### REQ-49H-003 — Controlled image intake
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / LOCAL QA PENDING`
- operator image limit,
- default 10,
- hard max 20,
- applies to persisted/selected/downloaded images,
- per-product cap must not stop later products.

## Phase49.3I

### REQ-49I-001 — Exact search URL discovery
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
- explicit MakerWorld/Search/Listing URL is authoritative,
- do not silently replace with default popular/download listing.

### REQ-49I-002 — Two-stage candidate review before full fetch
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
- Preview: one thumbnail + title/basic source identity only,
- Full Fetch only after approval,
- image limit remains selectable 1..20.

### REQ-49I-003 — Archive / not-needed candidate
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
- archive without Full Fetch,
- preserve blocked identity so it does not reappear,
- no destructive source deletion.

### REQ-49I-004 — Duplicate guard
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
- prevent duplicate source products by source code + external id + normalized URL.

### REQ-49I-005 — Safe source text persistence
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
- discard unexpected scraped CJK/Cyrillic/emoji garbage from source text,
- preserve URLs/source identity,
- preserve Persian editorial `_fa` fields,
- no historical mass rewrite.

### REQ-49I-006 — Products surface remains visual/lightweight
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
- usable product image,
- product name,
- compact Product ID/state/source/image-count/date/publish-state,
- Edit Product action,
- click image for large preview,
- detailed editing stays in Product Workspace.

### REQ-49I-007 — Three explicit pricing modes
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
1. Fixed exact price,
2. Range min/max,
3. Formula/Dynamic.
- Range must not invoke Formula.

### REQ-49I-008 — Full AI autofill progress immediately
Status: `SUPERSEDED/EXTENDED BY REQ-49I-016 / WINDOWS QA PENDING`
- first progress paint before synchronous preflight,
- then connection/send/receive/save/result stages,
- success/result/error stays visible and sanitized.
Canonical root cause for the original preflight gap: `ERR-49-018`.

### REQ-49I-009 — Windows handoff uses live GitHub snapshot
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / ACTIVE`
- fetch current remote inside same execution,
- Local HEAD equals fetched Remote Epic HEAD,
- dirty Local stops for inspection,
- ff-only pull,
- no reset/stash/delete shortcut,
- runner remains ASCII-only for Windows PowerShell 5.1.
Canonical root cause: `ERR-49-019`.

### REQ-49I-010 — Windows Explorer-style Products browsing
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
- full thumbnails,
- Extra Large / Large / Medium / Small / List,
- persistent view preference,
- normal/Ctrl/Shift selection,
- Select All / Clear,
- right-click actions,
- safe Remove From Publish Queue.
Canonical root cause: `ERR-49-020`.

### REQ-49I-011 — Product URL vs Group/Category/Search routing
Status: `WINDOWS OWNER QA CONFIRMED`
- true product URL → mature direct intake,
- Group/Category/Search/Listing/sub-branch → Preview first,
- Full Fetch only after approval,
- source `model_url_pattern` is authoritative.
Canonical root cause: `ERR-49-021`.

### REQ-49I-012 — Product selection/open never loops
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
- one Open action → one Product Workspace,
- one-way Treeview sync,
- re-entrancy guard,
- state-only reverse callback,
- useful Persian filters/sorts.
Canonical root cause: `ERR-49-022`.

### REQ-49I-013 — Token/API Key/FTP credentials persist visibly and securely
Status: `SUPERSEDED BY 49.3I.7 REAL PROVIDER-HUB FIX / WINDOWS QA PENDING`
- Windows Credential Store/environment stays source of truth,
- FTP password + Bridge token remain masked/populated after Save/restart,
- AI credentials remain masked/populated,
- no secret in SQLite/Git/source/logs.
Canonical root cause: `ERR-49-023`.

### REQ-49I-014 — Real AI Provider Hub keys and model lists survive updates and stay visible
Status: `GITHUB UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
- AvalAI/OpenRouter/OpenAI/Google real Provider-card fields hydrate from secure storage,
- Provider keys entered once do not visually disappear after update/restart,
- configured Provider model catalogs background-load through the mature API client,
- Model ID/model picker remains visible/selectable,
- manual API refresh remains available,
- no secret moves into SQLite/Git/source/logs.
Canonical root cause: `ERR-49-025`.

### REQ-49I-015 — Search Preview works without breaking mature full source extraction
Status: `GITHUB UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
Owner workflow:
1. Search/Listing URL is scanned,
2. show lightweight candidate(s) with one thumbnail/basic identity,
3. operator approves wanted product,
4. only then follow product link and run mature full extraction,
5. download/persist operator-selected image count, e.g. 20,
6. rejected/archived candidates are not full-fetched.
- raw/escaped Preview JavaScript fixes `Locator.evaluate_all` syntax regression,
- mature `extract_direct_link` / direct Product / approved Full Fetch remain preserved.
Canonical root cause: `ERR-49-024`.

### REQ-49I-016 — Every real operator AI action must show a bounded, observable execution path
Status: `GITHUB UPDATED IN 49.3I.8 / FINAL CI SUCCESS / WINDOWS QA PENDING`
Owner report:
- the bottom `تکمیل هوشمند همه فیلدهای AI` stayed on AvalAI content generation for ~5 minutes,
- no useful progress window showed connection/send/receive/save state,
- operator could not tell whether the request was working or stuck,
- the Workspace eventually had to be closed.

Required contract:
- the actual visible bottom All-Fields action must use the mature Task Center,
- immediate startup progress before preflight,
- visible connection / data sent / waiting / response received / save / result-error path,
- elapsed time visible continuously,
- a `توقف انتظار` action,
- bounded operator wait instead of indefinite-looking wait,
- provider/network errors remain visible and do not close the app,
- cancel/timeout must make any late network result stale so it cannot overwrite product data,
- no duplicate AI client/worker implementation.

Verified root cause:
- Phase49.3C `_phase49_3c_all_ai()` still called legacy `generate_ai("commerce")`, bypassing `_phase49_3e_run_ai()` and therefore bypassing the already-correct 49.3I/3H progress stack.
Canonical record: `ERR-49-026`.

## Canonical Runner
`RUN_PHASE49_3I_LOCAL_GATE.ps1` v`49.3I.8`.

Protected contracts:
- ASCII-only Windows PowerShell 5.1 compatibility,
- live fetched GitHub snapshot guard,
- Preview JavaScript escape regression,
- Preview-only lightweight candidate boundary,
- real Provider-card secure hydration,
- Provider model-catalog auto-load/cache/combobox visibility,
- real bottom All-Fields AI → mature Task Center routing,
- elapsed progress + Stop Waiting + 210s operator watchdog,
- stale late AI result discard,
- selection-loop and Explorer regressions,
- Product-vs-Group routing,
- Phase49.3H/3G + Django migration/full-suite regressions.

## Preserved Requests From Prior Phases
- Product Workspace remains canonical detailed editor.
- AI provider/model remains selectable and persistent.
- Image SEO is selected-only and text-only; image bytes/files/URLs are not sent to the mature Task Center AI path.
- AI provenance/manual override/disable remains protected.
- source refresh preserves human edits.
- Local vs Production publish remains fail-closed.
- Production cannot be touched before explicit owner approval.

## Change Rule
A new request does not authorize unrelated redesign. Extend/Patch/Wrap mature behavior and regression-test the exact broken boundary.
