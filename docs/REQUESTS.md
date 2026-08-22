# OWNER REQUESTS

Last Updated: 2026-08-22

## Phase49.3H

### REQ-49H-001 — Unified SEO execution visibility
Status: GITHUB_UPDATED / FINAL CI SUCCESS / LOCAL QA PENDING
Request:
- every SEO-related button/action visibly shows execution/result/error state
- provider/model/request/tokens/cost/log information where available
- error/result remains recoverable and sanitized

### REQ-49H-002 — Per-product AI/SEO cost
Status: GITHUB_UPDATED / FINAL CI SUCCESS / LOCAL QA PENDING
Request:
- record cost spent editing/SEOing each product
- internal publish cost receipt
- real provider cost only; never invent unsupported cost

### REQ-49H-003 — Controlled image intake
Status: GITHUB_UPDATED / FINAL CI SUCCESS / LOCAL QA PENDING
Request:
- operator determines max images per product
- default 10; hard max 20
- limit applies to persisted/selected/downloaded images
- reaching the limit does not stop the multi-product workflow

## Phase49.3I

### REQ-49I-001 — Exact search URL discovery
Status: GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS RERUN PENDING
Request:
- supplied MakerWorld search/listing URL is the authoritative discovery source
- example: `https://makerworld.com/en/search/models?keyword=cake+stand`
- do not replace it with configured popular/download listings

### REQ-49I-002 — Two-stage candidate review before full fetch
Status: GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS RERUN PENDING
Request:
- Stage 1: only one thumbnail + product name/basic source identity
- Stage 2: only approved candidates receive full content/spec/text + chosen number of images
- image limit remains selectable 1..20

### REQ-49I-003 — Archive / not-needed candidate
Status: GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS RERUN PENDING
Request:
- selected candidate can be archived/not-needed without full extraction
- blocked identity must prevent rediscovery until explicit restore
- no destructive source deletion

### REQ-49I-004 — Duplicate guard
Status: GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS RERUN PENDING
Request:
- same source product must not be received twice
- guard by source code + external source id + normalized URL

### REQ-49I-005 — Safe source text persistence
Status: GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS RERUN PENDING
Request:
- do not persist Chinese/CJK or other unexpected scraped script/font garbage
- URLs/source identities remain exact
- Persian editorial/AI `_fa` fields remain Persian
- no historical mass rewrite

### REQ-49I-006 — Product page must be a real image gallery
Status: GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS RERUN PENDING
Request:
- main Products page must show products as large image gallery/cards, not a parameter-heavy table/editor
- every product card shows only product image, product name and one Edit Product action
- price/title/status/editor fields must not be displayed on the Products list surface
- clicking product image should open a larger preview
- all detailed edits continue in Product Workspace

Local QA result before fix:
- intended 49.3I lightweight patch did not execute on the real UX87 page construction boundary, so images did not appear and legacy controls remained.
- canonical root cause: `ERR-49-017`.

Fix:
- patch real `_modernize_products_page` boundary
- hide complete legacy pane while preserving it for compatibility
- local-only 260x190 gallery thumbnails + click-to-large-preview
- batched thumbnail loading through Tk `after()`

### REQ-49I-007 — Three explicit pricing modes
Status: GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS RERUN PENDING
Request:
1. exact/fixed
2. range/min-max
3. formula/dynamic
- Range must not be conflated with Formula
- preserve Dynamic Variant source of truth

### REQ-49I-008 — Full AI autofill must show progress immediately
Status: GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS RERUN PENDING
Request:
- clicking full AI autofill must not appear frozen before a progress screen opens
- progress should be visible before preflight, then show connection/send/receive/save stages
- success leaves the result/log drawer visible
- error remains visible with sanitized log/error details

Local QA root cause:
- 49.3F created `AIProgress` only after synchronous `save/preflight/source preparation`, so no UI existed to paint during that interval.
- canonical root cause: `ERR-49-018`.

Fix:
- immediate startup progress first-paint
- existing AI flow scheduled after Tk event-loop yield
- automatic handoff to existing 49.3H progress/result/error/cost stack
- no duplicate Provider/Model/network/request implementation

## Phase49.3I Final GitHub Validation
Exact validated Epic base: `97674a82acc97e1a623b76084b60344cfa93142b`.
CI-only PR #47: CLOSED / NOT MERGED.
- Phase49.3I Run `32573779531` — SUCCESS
- Phase49.3H Run `32573779534` — SUCCESS
- Phase49.3G Run `32573779548` — SUCCESS
- Full Phase49 + Full Django Run `32573779528` — SUCCESS

Canonical runner: `RUN_PHASE49_3I_LOCAL_GATE.ps1` v`49.3I.2`, ASCII-only for Windows PowerShell 5.1.

Windows automated gate + visual/data QA remain required before Local Publish/acceptance.

## Preserved Requests From Prior Phases
- Workspace stages remain accessible; incomplete task is guided, not trapped.
- AI provider/model selectable and persistent with connection test.
- Image SEO operates only on selected product images and sends no image bytes/files/URLs to AI.
- AI tasks/provenance indicate what AI filled and allow operator manual override/disable.
- Local vs Production publish separation remains fail-closed.
- Source refresh preserves human edits.
- Production cannot be touched before Local approval.

## Change Rule
A new request does not authorize unrelated redesign. Implement approved delta with minimal changes and preserve mature behavior unless owner explicitly requests removal/replacement.
