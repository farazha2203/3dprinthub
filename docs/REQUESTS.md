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
Status: `GITHUB_UPDATED IN 49.3I.13 / PR #59 MERGED / FINAL CI SUCCESS / WINDOWS RERUN PENDING`
Owner acceptance from real Windows QA:
- exact URL field must accept Ctrl+V,
- Shift+Insert and right-click Paste must work,
- a visible Paste Link action must exist,
- pasted query parameters such as `?keyword=cake+stand` must remain intact,
- approved multi-candidate Full Fetch must not open/close one visible browser window per selected candidate,
- approved batch continues to reuse the mature RichPageExtractor in the background,
- separate direct single-product intake retains configured headed behavior for login/CAPTCHA recovery,
- original direct-link headed configuration must be restored after batch completion/cancel/error,
- any failed candidate must expose its persisted `last_error` directly to the operator,
- no new crawler/extractor, no Preview/Approve contract regression, no data reset.
Canonical record: `ERR-49-031`.

## Operational Release Request

### REQ-REL-001 — Hand Catalog Center to employees today
Status: `REQUESTED / WINDOWS 49.3I.13 RELEASE RERUN PENDING`
Acceptance now requires:
- current Epic pulled by live ff-only snapshot,
- runner `49.3I.13` passes,
- Windows paste controls pass,
- exact MakerWorld page Preview remains correct,
- 2+ approved candidates Full Fetch with no visible per-candidate browser windows,
- any failed row exposes exact Candidate Error Detail,
- direct Product URL intake remains healthy,
- Stop/live state, image fit, All-Fields/Provider/model/image-limit/pricing regressions remain healthy.

After PASS employees may use Catalog Center for controlled data entry. Production still requires exactly one Local Publish E2E + explicit owner approval.

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

## Canonical Runner
`RUN_PHASE49_3I_LOCAL_GATE.ps1` v`49.3I.13`.

## Change Rule
New requests do not authorize unrelated redesign. Extend/Patch/Wrap mature behavior and regression-test the exact active operator/store boundary.
