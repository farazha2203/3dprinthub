# OWNER REQUESTS

Last Updated: 2026-08-23

Older detailed request history remains available in Git history. This file keeps the currently active/relevant acceptance contracts.

## Phase49.3H — Preserved

### REQ-49H-001 — Unified SEO execution visibility
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
AI/SEO actions expose execution/result/error state with sanitized provider/model/request/tokens/cost/log where available.

### REQ-49H-002 — Per-product AI/SEO cost
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
Record real provider-supported cost only; never invent unsupported cost.

### REQ-49H-003 — Controlled image intake
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
Default 10, hard max 20 across persisted/selected/downloaded image flow.

## Phase49.3I — Preserved Core Requests

### REQ-49I-001 — Exact search URL discovery
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
Explicit MakerWorld/Search/Listing URL is authoritative.

### REQ-49I-002 — Preview before Full Fetch
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
Preview is one thumbnail + basic identity only. Full Fetch only after approval.

### REQ-49I-003 — Archive / not-needed candidate
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
Archive blocks rediscovery without Full Fetch/destructive deletion.

### REQ-49I-004 — Duplicate guard
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
Dedupe by source + external id + normalized URL.

### REQ-49I-005 — Safe source text persistence
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
Unexpected scraped script garbage must not pollute editorial data.

### REQ-49I-006 — Visual/lightweight Products Explorer
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
Explorer remains browse/select/preview oriented; Product Workspace remains canonical detailed editor.

### REQ-49I-007 — Fixed / Range / Formula pricing
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
Range must never invoke Formula.

### REQ-49I-009 — Windows handoff uses live GitHub snapshot
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / ACTIVE`
Live fetch, clean exact Epic branch, Local HEAD == fetched Remote HEAD, ff-only pull, no reset/stash/delete shortcut, ASCII-only Windows runner. Canonical record: `ERR-49-019`.

### REQ-49I-014 — Real Provider Hub credentials/model lists persist
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
Provider-card keys hydrate from secure storage, model catalogs remain selectable, FTP/Bridge credentials remain secure/persistent, secrets never enter SQLite/Git/log payloads.

### REQ-49I-015 — MakerWorld Preview does not break mature source acquisition
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
Search/Listing → lightweight Preview → Approve → mature Full Fetch → selected image limit.

### REQ-49I-016 — All real AI actions are bounded and observable
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
Real All-Fields uses mature Task Center, immediate first-paint, connection/send/wait/receive/save/result/error progress, elapsed timer, Stop Waiting, 210-second watchdog and stale-result discard.

### REQ-49I-017 — Explicit All-Fields rerun refreshes AI-owned values
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
Changing Provider/Model and pressing All-Fields regenerates AI-owned output while proven manual edits remain protected; generic titles are rejected; source/SEO facts remain grounded.

### REQ-49I-018 — AI request/result/error must be inspectable
Status: `GITHUB_UPDATED IN 49.3I.10 / FINAL CI SUCCESS / WINDOWS QA PENDING`
Operator sees scrollable sanitized outgoing request, incoming response and diagnostics; title retry uses current Provider/Model; title watchdog 90 seconds; app remains open after provider errors. Canonical record: `ERR-49-028`.

### REQ-49I-019 — Provider output must satisfy exact Catalog schema and abort must be immediately retryable
Status: `GITHUB_UPDATED IN 49.3I.11 / FINAL CI SUCCESS / WINDOWS QA PENDING`
- AvalAI/OpenRouter receive actual JSON Schema,
- aliases cannot silently replace required fields,
- at most one schema-repair request,
- exact mismatch shown if repair fails,
- `/models` diagnostics summarized,
- Stop Waiting/watchdog immediately releases busy state,
- new Provider/Model run can start immediately,
- late old output stays stale,
- 90s title / 210s full-AI watchdogs remain,
- secrets remain redacted.
Canonical record: `ERR-49-029`.

### REQ-49I-020 — Exact-page discovery must be visibly operable and single-product intake must be separate
Status: `GITHUB_UPDATED IN 49.3I.12 / PR #58 MERGED / FINAL CI SUCCESS / WINDOWS QA PENDING`
Owner acceptance:
- pasted Search/Listing/Category URL must be the exact page scanned,
- visible badge/progress/elapsed/current URL must show whether work is running/stopping/done,
- candidate links from that page must be visible before Full Fetch,
- direct Product URL has a separate manual action validated by source `model_url_pattern`,
- Preview remains lightweight and Full Fetch remains approval-gated,
- Stop request must be visible,
- Product Workspace images must use equal fixed pixel viewports without crop/stretch,
- landscape/portrait cards use 228x171 contain-fit semantics,
- no duplicate crawler/extractor architecture.
Canonical record: `ERR-49-030`.

## Operational Release Requests — 2026-08-23

### REQ-REL-001 — Hand Catalog Center to employees today
Status: `REQUESTED / WINDOWS 49.3I.12 RELEASE QA PENDING`
Acceptance:
- current Epic pulled by live ff-only snapshot,
- runner `49.3I.12` passes,
- exact MakerWorld Search URL shows visible page discovery state and candidates,
- one candidate Preview → Approve → Full Fetch passes,
- one direct Product URL intake passes,
- Stop feedback passes,
- Product Workspace image fit passes,
- All-Fields/Provider/model/image-limit/pricing regressions remain healthy.

After this QA passes employees may use Catalog Center for controlled data entry. Production still requires one Local Publish E2E + explicit owner approval.

### REQ-PAY-001 — Normal Store checkout must support online payment
Status: `REQUESTED / IMPLEMENTATION REQUIRED AFTER CATALOG ACCEPTANCE`
- reuse mature Phase30 ZarinPal security semantics,
- server owns/recomputes amount,
- idempotent attempt identity,
- callback cannot trust browser amount/status,
- stored Authority must match callback Authority,
- server-to-server Verify before marking paid,
- duplicate callback cannot double-finalize payment/order/inventory,
- failed/cancelled/temporary errors recoverable,
- bank transfer remains available,
- Sandbox E2E before live merchant activation,
- secrets only in environment/secure server configuration,
- one owner-approved low-value Production payment before public activation.

Current supported online provider in repository: `ZarinPal` only.

## Canonical Runner
`RUN_PHASE49_3I_LOCAL_GATE.ps1` v`49.3I.12`.

## Change Rule
New requests do not authorize unrelated redesign. Extend/Patch/Wrap mature behavior and regression-test the exact active operator/store boundary.
