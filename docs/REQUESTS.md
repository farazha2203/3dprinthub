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
- REQ-49I-006: Product Workspace remains canonical editor.
- REQ-49I-007: Fixed / Range / Formula remain independent.
- REQ-49I-009: Windows delivery uses live fetched GitHub snapshot, clean exact Epic branch, ff-only only.
- REQ-49I-014: Provider/FTP/Bridge secure persistence.
- REQ-49I-016..019: observable AI, rerun generated values, sanitized trace, exact provider schema, bounded watchdogs.
- REQ-49I-020: exact-page discovery visibly operable and Product Workspace images contain-fit.
- REQ-49I-021: Windows URL paste, operator-safe batch behavior and candidate error details.
- REQ-49I-014A: mature top acquisition controls remain additive and preserved.

### REQ-49I-022 — Bulk exact-page image acquisition + Add-to-Products
Status: `MERGED / CI SUCCESS / WINDOWS QA PENDING`
- exact Search/Listing/Category URL authoritative,
- product presets include 30/50/100; hard max 100,
- images/product supports 10/20; hard max 20,
- selected rows add to Products without Rich Direct Full Fetch,
- at least one local staged image required,
- Archive/Block/dedupe/Stop preserved,
- Product Workspace/AI/pricing/publish/FTP/Bridge untouched.

### REQ-49I-023 — Resilient acquisition fallback + persistent method trace
Status: `MERGED / ALL REQUIRED CI SUCCESS / WINDOWS QA PENDING`
Owner requirement after Windows evidence:
- if one discovery/crawling/download technique fails, do not stop before trying other registered safe techniques,
- reuse previously successful candidate discovery for the same exact listing when live rediscovery fails,
- do not lose the visible/correct candidate list because a later crawler implementation breaks,
- record which method was attempted, why it failed, and which method finally succeeded,
- no embedded `evaluate_all` at the new resilient discovery boundary,
- final discovery ladder: locator-safe → HTTP/HTML → attached Chrome 9222 → cached candidate DB,
- image ladder: locator-safe fresh → HTTP parser/downloader → mature Classic DOM → attached Chrome 9222 → listing thumbnail,
- one candidate failure must not abort the rest of the batch,
- local staging guard remains mandatory,
- no Rich Direct Full Fetch dependency is reintroduced.

Merge evidence:
- PR `#62` merged,
- final PR head `8f4fbe6d0264f673d0e6564a4ed1e383db023ab6`,
- merge commit `44216546162fead0b752d92cf6cae8d658f034f2`,
- all required final-head CI success including Full Phase49 + Windows Catalog regressions + Full Django.

## Operational Release Request

### REQ-REL-001 — Hand Catalog Center to employees and deploy approved release
Status: `BLOCKED ONLY BY 49.3I.16 WINDOWS QA + ONE LOCAL PUBLISH E2E + OWNER APPROVAL`
Acceptance:
- live ff-only Windows pull,
- exact-page batch does not abort on first acquisition-method error,
- correct cached candidates can be reused,
- visible staged image counts work,
- selected rows Add to Products without Direct Full Fetch,
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
`RUN_PHASE49_3I16_FALLBACK_GATE.ps1`; it chains the 49.3I.15 gate and all prior 49.3I regression gates.

## Change Rule
New requests do not authorize unrelated redesign. Extend/Patch/Wrap mature behavior and regression-test the exact active operator/store boundary.
