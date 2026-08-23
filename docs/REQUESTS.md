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
Status: `MERGED / CI SUCCESS`
- exact Search/Listing/Category URL authoritative,
- product presets include 30/50/100; hard max 100,
- images/product supports 10/20; hard max 20,
- selected rows add to Products without Rich Direct Full Fetch,
- at least one local staged image required,
- Archive/Block/dedupe/Stop preserved.

### REQ-49I-023 — Resilient acquisition fallback + persistent method trace
Status: `MERGED / ALL REQUIRED CI SUCCESS`
- failed discovery/image technique must fall through to other registered safe techniques,
- reuse prior correct candidates for the same listing if live discovery fails,
- record attempted/successful methods,
- discovery ladder: locator-safe → HTTP/HTML → attached Chrome 9222 → cached candidate DB,
- image ladder: locator-safe → HTTP → mature DOM → Chrome 9222 → listing thumbnail,
- one candidate failure does not abort batch,
- no Rich Direct dependency returns.

### REQ-49I-024 — Exactly one saved Provider/Model for all Product AI
Status: `MERGED / ALL REQUIRED CI SUCCESS / WINDOWS QA PENDING`
Owner requirement after Product Workspace hang evidence:
- AI Center remains the only place that selects the active Provider and Model,
- after `ذخیره Provider و مدل فعال`, every Product AI action must use exactly that saved Provider and exactly that saved Model,
- other configured API keys/providers must not be scanned or selected automatically,
- normal Product AI must not enumerate the provider model catalog before generation,
- Google Product AI with an exact saved model must not list models again,
- Product Workspace open must not start hidden/automatic AI requests,
- AI requests are explicit operator actions only,
- existing request/response/error trace and Stop Waiting/watchdog remain,
- stale destroyed-widget callbacks must not crash or freeze the application,
- explicit AI Settings `Search model` and `Test connection` remain available and may call the provider API,
- no acquisition/pricing/publish/FTP/Bridge/schema change is authorized by this request.

Merge evidence:
- PR `#63` merged,
- final runtime head `2917a3db5225abac71fc3e80b64ad439acd7a4d0`,
- merge commit `7f835f573b92e3aded6275c9421770c0c47d947a`,
- 49.3I.17 `32649623837` SUCCESS,
- all inherited 49.3I/49.3I.16/49.3I.15/49.3I.14/49.3H/49.3G workflows SUCCESS,
- Full Phase49 + Windows Catalog regressions + Full Django `32649623804` SUCCESS,
- no migration; Production untouched.

### REQ-49I-025 — Source title must be correct before translation/SEO
Status: `IMPLEMENTED ON FEATURE BRANCH / LOCAL QA REQUIRED`
Owner evidence: MakerWorld product `2896217-ribbed-cake-stand-cookie-platter` entered Catalog as a generic model-number title; AI then translated/generated all content from that wrong identity.

Acceptance:
- generic discovery placeholders such as `Model 2896217`, `MakerWorld model 2896217` or Persian equivalents are never authoritative product titles,
- a valid scraped/page title wins,
- if live title retrieval is unavailable, the exact MakerWorld product URL slug is the deterministic source-identity fallback,
- `https://makerworld.com/en/models/2845731-cake-stand...` resolves to `Cake Stand`,
- `https://makerworld.com/en/models/2896217-ribbed-cake-stand-cookie-platter...` resolves to `Ribbed Cake Stand Cookie Platter`,
- canonical source title is enforced again before Add-to-Products so a stale generic candidate cannot poison the Product DB,
- Product AI receives canonical source title even for an already-imported legacy product,
- Product Workspace exposes `بازخوانی و اصلاح عنوان منبع` and `اصلاح عنوان منبع + بازسازی کامل AI` for existing wrong products,
- operator-entered Persian authoritative title from 49.3I.18 remains available and is not removed,
- no DB migration, acquisition-limit, pricing, publish, FTP, Bridge or Production change.

Implementation anchor: `d9d3d617ed22dd3096379e668697f0f9fab87ca0` plus following documentation commits on `agent/phase49-3i18-operator-bulk-ai-rebuild`.

## Operational Release Request

### REQ-REL-001 — Hand Catalog Center to employees and deploy approved release
Status: `BLOCKED BY FOCUSED WINDOWS QA + ONE LOCAL PUBLISH E2E + OWNER APPROVAL`
Acceptance now additionally requires the 49.3I.18/49.3I.19 operator editing + source-identity acceptance to pass before release.

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
Use the focused 49.3I.18/49.3I.19 test commands on the feature branch, then chain the existing `RUN_PHASE49_3I17_SINGLE_AI_GATE.ps1` baseline gate. Production remains untouched until PASS + owner approval.

## Change Rule
New requests do not authorize unrelated redesign. Extend/Patch/Wrap mature behavior and regression-test the exact active operator/store boundary.