# OWNER REQUESTS

Last Updated: 2026-08-22

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

### REQ-49I-006 — Products surface must be a real visual gallery, not a parameter-heavy editor
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS RERUN PENDING`
Original request:
- large usable product image,
- product name,
- Edit Product action,
- click image for large preview,
- detailed editing stays in Product Workspace.

Refined by owner during 49.3I.5 QA:
- the list must remain lightweight and visual,
- but it should also show compact operational details useful for browsing:
  - Product ID,
  - state,
  - source,
  - image count,
  - added date,
  - publish state.
- price/editorial/SEO/material/pricing forms must not return to the Products list.

### REQ-49I-007 — Three explicit pricing modes
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
1. Fixed exact price,
2. Range min/max,
3. Formula/Dynamic.
- Range must not invoke Formula.

### REQ-49I-008 — Full AI autofill must show progress immediately
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
- first progress paint before synchronous preflight,
- then connection/send/receive/save/result stages,
- success/result/error remains visible and sanitized.

### REQ-49I-009 — Windows handoff uses live GitHub snapshot, not stale Chat SHA
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / ACTIVE`
- fetch current remote inside the same execution,
- Local HEAD must equal fetched Remote Epic HEAD,
- dirty Local stops for inspection,
- only fast-forward pull,
- no reset/stash/delete shortcut,
- runner remains ASCII-only for Windows PowerShell 5.1.

Canonical root cause: `ERR-49-019`.

### REQ-49I-010 — Windows Explorer-style Products browsing
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS RERUN PENDING`
- full-sized thumbnails, no clipped strip,
- Extra Large / Large / Medium / Small / List views,
- persist view preference,
- normal/Ctrl/Shift selection,
- Select All / Clear Selection,
- selected count,
- right-click menu,
- safe Remove From Publish Queue,
- image click large preview.

Canonical root cause for thumbnail issue: `ERR-49-020`.

### REQ-49I-011 — Direct Product URL vs Group/Category/Search URL routes safely
Status: `WINDOWS OWNER QA CONFIRMED`
- true product URL → mature direct single-product intake,
- Group/Category/Search/Listing/sub-branch URL → Preview Candidate first,
- Full Fetch only after approval,
- configured source `model_url_pattern` is authoritative single-product boundary.

Canonical root cause: `ERR-49-021`.
Owner confirmed after 49.3I.5 that the link/sub-branch problem is corrected locally.

### REQ-49I-012 — Product selection/open must never loop + restore compact metadata and useful sorting
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS RERUN PENDING`
Owner QA request:
- selecting/opening a product must never freeze or enter a selection callback loop,
- one Open action opens one Product Workspace,
- cards should show useful compact operational details,
- restore friendly product filters and sorting such as آماده انتشار / صف انتشار / منتشرشده / جدیدترین / قدیمی‌ترین / آخرین بروزرسانی.

Verified root cause:
- Explorer card wrote hidden Treeview selection,
- `<<TreeviewSelect>>` called `load_product`,
- compatibility `load_product` wrote Treeview selection again,
- cycle repeated.
- canonical record: `ERR-49-022`.

Implemented 49.3I.5:
- one-way card → Treeview event-producing sync,
- re-entrancy guard,
- only write Treeview selection when it differs,
- Treeview callback is state-only,
- repeat-open guard + Tk paint yield before Product Workspace,
- compact card ID/state/source/images/date/publish-state,
- Persian filter/sort toolbar,
- dedicated fake-Treeview feedback-loop regression test.

Validation:
- CI-only PR #50: CLOSED / NOT MERGED,
- validated Epic runtime base `cdaac6680ea8545f52ece15ecaa3ce0a575eabe9`,
- Phase49.3I Run `32580222694` SUCCESS,
- Phase49.3H Run `32580222686` SUCCESS,
- Phase49.3G Run `32580222682` SUCCESS,
- Full Phase49 + Full Django Run `32580222683` SUCCESS,
- Django migration: NONE.

### REQ-49I-013 — Token/API Key/FTP credentials must persist visibly and securely
Status: `GITHUB IMPLEMENTED IN 49.3I.6 / FINAL CI PENDING / WINDOWS QA PENDING`
Owner report:
- Catalog Center 49.3I.5 launches,
- but Token and Key fields appear empty again,
- credentials should be entered once and remain available across save/restart/release.

Required contract:
- one stable secure source of truth,
- Windows Credential Store/environment remains the credential backend,
- securely stored AI key, FTP password and Bridge token are restored into masked fields on startup,
- successful Save must not leave the masked fields looking empty,
- Provider switch restores that Provider's stored key,
- explicit delete/clear remains supported,
- no password/token/API key in SQLite, Git, source files, diagnostics or logs.

Verified root cause:
- runtime secure fallback already existed,
- UX fields were initialized without secure-store hydration,
- mature Save handlers wrote credentials securely and then cleared the widgets,
- restart therefore looked like credential loss even when secure storage still held the value.

Canonical record: `ERR-49-023`.

## Canonical Runner
`RUN_PHASE49_3I_LOCAL_GATE.ps1` v`49.3I.6`.

Protected contracts:
- ASCII-only Windows PowerShell 5.1 compatibility,
- live fetched GitHub snapshot guard,
- selection-loop regression test,
- compact metadata/filter/sort tests,
- secure credential hydration/persistence tests,
- Explorer thumbnail/view/multi-select/context-menu tests,
- Product-vs-Group routing tests,
- Phase49.3H/3G + Django migration/full-suite regressions.

## Preserved Requests From Prior Phases
- Workspace stages remain accessible; incomplete state is guided, not trapped.
- AI provider/model remains selectable/persistent with connection test.
- Image SEO remains selected-only and text-only; no image bytes/files/URLs sent to AI.
- AI provenance/manual override/disable remains protected.
- source refresh preserves human edits.
- Local vs Production publish remains fail-closed.
- Production cannot be touched before explicit owner approval.

## Change Rule
A new request does not authorize unrelated redesign. Implement the requested delta minimally and preserve mature behavior unless the owner explicitly requests replacement/removal.
