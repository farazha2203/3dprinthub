# OWNER REQUESTS

Last Updated: 2026-08-23

Older detailed request history remains available in Git history. This file keeps the currently active/relevant acceptance contracts.

## Phase49.3H — Preserved

### REQ-49H-001 — Unified SEO execution visibility
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
- SEO/AI actions show execution/result/error state.
- provider/model/request/tokens/cost/log where available.
- sanitized recoverable errors/results.

### REQ-49H-002 — Per-product AI/SEO cost
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
- record real provider-supported cost only.
- never invent unsupported cost.

### REQ-49H-003 — Controlled image intake
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
- default 10, hard max 20.
- persisted/selected/downloaded image cap remains consistent.

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
Unexpected scraped script garbage must not pollute editorial data; source URL/identity and Persian fields remain preserved.

### REQ-49I-006 — Visual/lightweight Products Explorer
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
Explorer remains browse/select/preview oriented; Product Workspace remains canonical detailed editor.

### REQ-49I-007 — Fixed / Range / Formula pricing
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
Range must never invoke Formula.

### REQ-49I-009 — Windows handoff uses live GitHub snapshot
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / ACTIVE`
- fetch current remote inside the gate,
- clean exact Epic branch,
- Local HEAD equals fetched Remote Epic HEAD,
- ff-only pull,
- no reset/stash/delete shortcut,
- ASCII-only Windows PowerShell runner.
Canonical record: `ERR-49-019`.

### REQ-49I-014 — Real Provider Hub credentials/model lists persist
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
- AvalAI/OpenRouter/OpenAI/Google real Provider-card fields hydrate from secure storage,
- model catalogs remain visible/selectable,
- FTP/Bridge credentials remain secure/persistent,
- no secret in SQLite/Git/source/logs.
Canonical record: `ERR-49-025`.

### REQ-49I-015 — MakerWorld Preview does not break mature source acquisition
Status: `GITHUB_UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
Search/Listing → lightweight Preview → Approve → mature Full Fetch → selected image limit.
Canonical record: `ERR-49-024`.

### REQ-49I-016 — All real AI actions are bounded and observable
Status: `GITHUB_UPDATED IN 49.3I.8 / FINAL CI SUCCESS / WINDOWS QA PENDING`
- real bottom All-Fields action uses mature Task Center,
- immediate first-paint,
- connection/send/wait/receive/save/result-error progress,
- elapsed timer + Stop Waiting,
- 210-second operator watchdog,
- late cancelled/timed-out result cannot mutate product,
- no duplicate AI client/network worker.
Canonical record: `ERR-49-026`.

### REQ-49I-017 — Explicit All-Fields rerun refreshes AI-owned values
Status: `GITHUB_UPDATED IN 49.3I.9 / FINAL CI SUCCESS / WINDOWS QA PENDING`
Owner expectation:
- changing Provider/Model and pressing `تکمیل هوشمند همه فیلدهای AI` must regenerate AI-owned/generated content,
- proven manual edits must remain protected,
- a generic title such as `محصول چاپ سه بعدی` must not be accepted as product-specific completion,
- Persian title/description/SEO must remain grounded in real source identity/use/theme/facts,
- low image count may offer mature source refetch before AI,
- missing local preparation defaults may be filled without fabricating source facts,
- source website is publisher/source identity while designer remains separate,
- final Django Product meta/OG/source fields must receive the verified desktop SEO/source payload.
Canonical record: `ERR-49-027`.

## Operational Release Requests — 2026-08-23

### REQ-REL-001 — Hand Catalog Center to employees today
Status: `REQUESTED / WINDOWS RELEASE QA PENDING`
Goal: employees begin entering/reviewing product/catalog data today.

Acceptance:
- current GitHub Epic pulled by ff-only live snapshot,
- runner `49.3I.9` passes,
- All-Fields product-specific AI/SEO test passes,
- low-image warning/refetch passes,
- MakerWorld Preview → Approve → Full Fetch passes,
- Provider/model/FTP/Bridge persistence passes,
- Product open/selection and pricing modes pass.

After this QA passes employees may use Catalog Center for data entry. Production publishing still requires Local Publish E2E + explicit owner approval.

### REQ-PAY-001 — Normal Store checkout must support online payment
Status: `REQUESTED / IMPLEMENTATION REQUIRED`
Verified current gap:
- mature Phase30 ZarinPal online payment exists for accepted Quote payments,
- normal Store checkout currently exposes only `bank_transfer`,
- active Store checkout always redirects to `store:manual_payment`,
- `StorePayment` has a `gateway` method but Store request/callback/verify integration is not complete.

Required implementation contract:
- reuse mature ZarinPal/security semantics rather than build a parallel payment stack,
- server owns/recomputes the order amount,
- random/idempotent attempt identity,
- callback cannot trust browser amount/status,
- stored Authority must match callback Authority,
- server-to-server Verify required before marking paid,
- repeated callback cannot double-finalize payment/order/inventory,
- cancelled/failed/temporary provider errors remain recoverable,
- manual bank-transfer payment remains available,
- Sandbox E2E before live merchant activation,
- secrets remain in environment/secure server configuration only,
- one owner-approved low-value Production payment before public live activation.

Current supported online provider in repository: `ZarinPal` only.

## Canonical Runner
`RUN_PHASE49_3I_LOCAL_GATE.ps1` v`49.3I.9`.

## Change Rule
New requests do not authorize unrelated redesign. Extend/Patch/Wrap mature behavior and regression-test the exact active operator/store boundary.
