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
- REQ-49I-020: exact-page discovery visibly operable; 228x171 contain image fit. Canonical: ERR-49-030.
- REQ-49I-021: reliable Windows URL paste, background approved batch, selected-candidate error detail. Canonical: ERR-49-031.

### REQ-49I-022 — New discovery UI must not remove mature acquisition
Status: `IMPLEMENTED / PR #60 MERGED / ALL REQUIRED CI SUCCESS / WINDOWS QA PENDING`
Owner acceptance:
- `شروع اسکن`, `توقف محترمانه`, `دریافت هوشمند از لینک`, `کشف جدیدها` remain visible,
- visible `شروع اسکن` invokes the original mature BaseApp scan worker,
- manual `دریافت محصول تکی` validates Product URL and then uses the same mature `mode=single` route,
- Rich Direct intake remains optional and cannot be forced when the mature path is intended,
- Preview/Approve/Archive/Paste/error-detail remain additive,
- no unrelated feature may be deleted/rebound while fixing this area.
Canonical record: `ERR-49-032`.

## Operational Release Request

### REQ-REL-001 — Hand Catalog Center to employees and update Production
Status: `REQUESTED / 49.3I.14 MERGED / FOCUSED WINDOWS QA PENDING`
Acceptance now requires only the focused release path:
1. current Epic pulled by live ff-only snapshot,
2. `RUN_PHASE49_3I14_HOTFIX_GATE.ps1 -LaunchApp` passes,
3. mature top acquisition controls are visible,
4. known MakerWorld Product URL works through mature `single + auto + شروع اسکن`,
5. manual `دریافت محصول تکی` uses the same mature route rather than forcing Rich Direct 403,
6. exact-page Preview/Approve remains present.

After PASS: exactly one Local Publish E2E + Store/Admin verification + explicit owner approval, then Production branch/path/MySQL/backup/rollback verification and GitHub-only deploy.

## Next Product Request

### REQ-PAY-001 — Normal Store checkout must support online payment
Status: `REQUESTED / IMPLEMENTATION AFTER CATALOG ACCEPTANCE`
Reuse mature Phase30 ZarinPal security semantics, preserve bank transfer, require Sandbox E2E before live activation and keep secrets outside Git.

## Canonical Windows Gates
- base regression gate: `RUN_PHASE49_3I_LOCAL_GATE.ps1`,
- final focused release gate: `RUN_PHASE49_3I14_HOTFIX_GATE.ps1`.

## Change Rule
New requests do not authorize unrelated redesign. Extend/Patch/Wrap mature behavior and regression-test the exact active operator/store boundary.
