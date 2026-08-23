# OWNER REQUESTS

Last Updated: 2026-08-23

Older detailed request history remains available in Git history. This file keeps the active acceptance contracts.

## Phase49.3H — Preserved
- REQ-49H-001: AI/SEO execution/result/error visibility with sanitized diagnostics.
- REQ-49H-002: real provider-supported cost only; never invent unknown cost.
- REQ-49H-003: image intake default 10 / hard max 20.

## Phase49.3I — Preserved Core
- REQ-49I-001: explicit Search/Listing URL is authoritative.
- REQ-49I-003: Archive/Not Needed blocks rediscovery without destructive deletion.
- REQ-49I-004: dedupe by source + external id + normalized URL.
- REQ-49I-005: source text sanitation without damaging URL/Persian editorial fields.
- REQ-49I-006: visual/lightweight Explorer; Product Workspace remains canonical editor.
- REQ-49I-007: Fixed / Range / Formula independent; Range never invokes Formula.
- REQ-49I-009: Windows delivery uses live fetched GitHub snapshot, clean exact Epic branch, ff-only only. Canonical: ERR-49-019.
- REQ-49I-014: Provider-card credentials/model lists plus FTP/Bridge secure persistence.
- REQ-49I-016: real All-Fields AI bounded/observable with 210s watchdog and stale discard.
- REQ-49I-017: explicit All-Fields rerun refreshes AI-owned values and protects manual overrides.
- REQ-49I-018: inspectable sanitized AI request/response/error, 90s title watchdog. Canonical: ERR-49-028.
- REQ-49I-019: exact provider schema + one repair + immediate retry after abort. Canonical: ERR-49-029.
- REQ-49I-020: exact-page discovery visibly operable and Product Workspace images contain-fit. Canonical: ERR-49-030.
- REQ-49I-021: explicit Windows URL paste, operator-safe batch behavior and candidate error details. Canonical: ERR-49-031.
- REQ-49I-014A: mature top acquisition controls restored and new UI remains additive. Canonical: ERR-49-032.

### REQ-49I-022 — Bulk exact-page image acquisition + Add-to-Products
Status: `IMPLEMENTED ON PR #61 / CI VALIDATION / WINDOWS QA PENDING`
Owner explicitly changes the exact-page business workflow:
- do not depend on single-product/Rich Direct Full Fetch for selected Search/Listing candidates,
- exact Search/Listing/Category URL remains authoritative,
- operator chooses product count with practical presets including 30 / 50 / 100; hard max 100,
- operator chooses images per product, especially 10 or 20; hard max 20,
- the same exact-page discovery first finds candidate product links,
- then the bulk flow gathers staged public product images with the mature Classic browser/image helpers,
- each candidate row must show image count before operator selection,
- wanted rows are selected and added with `اضافه کردن انتخاب‌شده‌ها به محصولات`,
- adding selected rows must not call `extract_direct_link` or another per-product Rich Direct Full Fetch,
- unwanted rows use existing Archive/Block semantics,
- one candidate failure must not abort the whole batch,
- Stop remains safe and visible,
- no Catalog candidate-table migration is required; staged image metadata may live under persistent Catalog DATA,
- restored mature scan controls, AI/provider/SEO/pricing/publish/FTP/Bridge/credentials are Must-Not-Touch.

This request supersedes the old one-thumbnail-only Preview contract **for this exact-page bulk operator path only**. Historical Preview logic remains available internally and mature top scan remains compatible.

## Operational Release Request

### REQ-REL-001 — Hand Catalog Center to employees and deploy approved release
Status: `BLOCKED ONLY BY 49.3I.15 WINDOWS QA + ONE LOCAL PUBLISH E2E`
Acceptance:
- final CI-successful 49.3I.15 merged into Epic,
- live ff-only Windows pull,
- bulk Search/Listing acquisition with visible image counts works,
- selected rows add to Products without Direct Full Fetch,
- Archive/Block works,
- one added Product opens with staged images,
- exactly one Local Publish E2E passes,
- explicit owner approval.

After approval: verify Host/branch/MySQL/backup/rollback and deploy only the approved GitHub snapshot.

## Next Product Request

### REQ-PAY-001 — Normal Store checkout must support online payment
Status: `REQUESTED / AFTER CATALOG DEPLOY`
- reuse mature Phase30 ZarinPal security semantics,
- server owns/recomputes amount,
- idempotent attempt identity,
- stored Authority must match callback,
- server-to-server Verify before paid,
- duplicate callback cannot double-finalize order/inventory,
- failed/cancelled/temporary errors recoverable,
- bank transfer remains available,
- Sandbox E2E before live merchant activation,
- secrets only in environment/secure server configuration,
- one owner-approved low-value Production payment before public activation.

## Canonical Windows Gate
`RUN_PHASE49_3I15_BULK_GATE.ps1` after Phase49.3I.15 merge; it chains all prior 49.3I gates.

## Change Rule
New requests do not authorize unrelated redesign. Extend/Patch/Wrap mature behavior and regression-test the exact active operator/store boundary.
