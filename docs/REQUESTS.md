# OWNER REQUESTS

Last Updated: 2026-08-23

Older detailed request history remains available in Git history. This file keeps the active acceptance contracts.

## Phase49.3H — Preserved
- REQ-49H-001: AI/SEO execution/result/error visibility with sanitized diagnostics.
- REQ-49H-002: real provider-supported cost only; never invent unknown cost.
- REQ-49H-003: image intake default 10 / hard max 20.

## Phase49.3I — Preserved Core
- REQ-49I-001: explicit Search/Listing URL is authoritative.
- REQ-49I-002: Preview before Full Fetch.
- REQ-49I-003: Archive/Not Needed blocks rediscovery without destructive deletion.
- REQ-49I-004: dedupe by source + external id + normalized URL.
- REQ-49I-005: source text sanitation without damaging URL/Persian editorial fields.
- REQ-49I-006: visual/lightweight Explorer; Product Workspace remains canonical editor.
- REQ-49I-007: Fixed / Range / Formula independent; Range never invokes Formula.
- REQ-49I-009: Windows delivery uses live fetched GitHub snapshot, clean exact Epic branch, ff-only only. Canonical: ERR-49-019.
- REQ-49I-014: Provider-card credentials/model lists plus FTP/Bridge secure persistence.
- REQ-49I-015: MakerWorld Search/Listing → lightweight Preview → Approve → mature Full Fetch.
- REQ-49I-016: real All-Fields AI bounded/observable with 210s watchdog and stale discard.
- REQ-49I-017: explicit All-Fields rerun refreshes AI-owned values and protects manual overrides.
- REQ-49I-018: inspectable sanitized AI request/response/error, 90s title watchdog. Canonical: ERR-49-028.
- REQ-49I-019: exact provider schema + one repair + immediate retry after abort. Canonical: ERR-49-029.
- REQ-49I-020: exact-page discovery visibly operable; single Product URL action separate; 228x171 contain image fit. Canonical: ERR-49-030.

### REQ-49I-021 — Windows URL paste and approved batch Full Fetch must be operator-safe
Status: `GITHUB_UPDATED IN 49.3I.13 / PR #59 MERGED / FINAL CI SUCCESS / WINDOWS REGRESSION FOUND LATER`
Preserved acceptance:
- Ctrl+V / Shift+Insert / right-click / visible Paste Link,
- pasted query parameters remain intact,
- approved batch does not flash one visible browser per candidate,
- failed candidate exposes persisted `last_error`,
- no second crawler/extractor and no Preview/Approve regression.
Canonical record: `ERR-49-031`.

### REQ-49I-022 — New discovery controls must not replace healthy mature acquisition
Status: `IMPLEMENTED IN 49.3I.14 / PR #60 OPEN / ALL REQUIRED CI SUCCESS / WINDOWS QA PENDING`
Owner acceptance from real Windows QA:
- restore the previously working top acquisition controls instead of hiding them,
- specifically preserve `شروع اسکن`, `توقف محترمانه`, `دریافت هوشمند از لینک` and `کشف جدیدها`,
- `شروع اسکن` must execute the original mature BaseApp scan worker, not the 49.3I Preview wrapper,
- new `دریافت محصول تکی` must validate Product URL then route through the same mature `mode=single` scan path,
- Rich Direct Intake remains optional and must not be forced when the mature route is available,
- existing Preview/Approve/Archive/Paste/error-detail UX remains available alongside the mature workflow,
- no unrelated UI removal, crawler replacement, DB/media rewrite, migration or Production change.
Canonical record: `ERR-49-032`.

## Operational Release Request

### REQ-REL-001 — Hand Catalog Center to employees as soon as the acquisition gate passes
Status: `REQUESTED / WINDOWS 49.3I.14 FOCUSED RELEASE QA PENDING`
Acceptance now requires only the release blocker regression to be rechecked:
- current Epic pulled with live ff-only snapshot,
- `RUN_PHASE49_3I14_HOTFIX_GATE.ps1` passes,
- mature top acquisition controls are visible again,
- MakerWorld `single` + `auto` + a known real product URL works through `شروع اسکن`,
- new `دریافت محصول تکی` uses the same mature route and does not force the Rich Direct HTTP-403 path,
- exact-page Preview/Approve remains present.

Do not re-open unrelated accepted UX/features unless a focused regression appears.

After PASS: exactly one Local Publish E2E + Store/Admin verification + explicit owner approval, then Production gate/deploy from GitHub.

## Next Product Request

### REQ-PAY-001 — Normal Store checkout must support online payment
Status: `REQUESTED / IMPLEMENTATION AFTER CATALOG ACCEPTANCE`
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

Current supported online provider: `ZarinPal`.

## Canonical Gates
- existing full Phase49.3I gate: `RUN_PHASE49_3I_LOCAL_GATE.ps1` v`49.3I.13`,
- additive acquisition-regression gate: `RUN_PHASE49_3I14_HOTFIX_GATE.ps1`.

## Change Rule
New requests do not authorize unrelated redesign. Extend/Patch/Wrap mature behavior; healthy controls/features remain frozen unless the owner explicitly asks to replace them. Regression tests must verify both visibility and command routing of preserved operator actions.
