# OWNER REQUESTS

Last Updated: 2026-08-25

Older detailed request history remains available in Git history. This file keeps the active acceptance contracts.

## Preserved Core Contracts
- REQ-49H-001: AI/SEO execution/result/error visibility with sanitized diagnostics.
- REQ-49H-002: real provider-supported cost only; never invent unknown cost.
- REQ-49H-003: image intake default 10 / hard max 20.
- REQ-49I-001: explicit Search/Listing URL is authoritative.
- REQ-49I-003: Archive/Not Needed blocks rediscovery without destructive deletion.
- REQ-49I-004: dedupe by source + external id + normalized URL.
- REQ-49I-006: Product Workspace remains canonical editor.
- REQ-49I-007: Fixed / Range / Formula remain independent.
- REQ-49I-009: Windows delivery uses live fetched GitHub snapshot, clean branch and ff-only pull.
- REQ-49I-014: Provider/FTP/Bridge secure persistence.
- REQ-49I-016..019: observable AI, rerun generated values, sanitized trace, exact schema and bounded watchdog.
- REQ-49I-022: bulk exact-page image acquisition + Add-to-Products.
- REQ-49I-023: resilient acquisition fallback + persistent method trace.
- REQ-49I-024: exactly one saved Provider/Model/key path for Product AI; no hidden fallback/model scan/AI-on-open.
- REQ-49I-025: source title must be canonical before translation/SEO.
- REQ-49I-026: operator controls must be visibly reachable in normal Workspace use.
- REQ-49I-027: AI actions must not freeze and must be diagnosable.
- REQ-49I-028: exact Product URL grounds the full Product AI refresh.

## REQ-49I-029 — AvalAI Product generation must use the exact working chat contract
Status: `IMPLEMENTED ON FEATURE BRANCH / WINDOWS LOCAL QA REQUIRED`

Owner evidence: the same MakerWorld link works directly in AvalAI, while Catalog Center's link completion did not reliably return/apply usable content.

Acceptance:
- product request uses the exact saved AvalAI model,
- no hidden Product `/models` request,
- request is normal Chat Completions `model + messages`,
- exact source/link/operator facts are visible to the model as text,
- requested output JSON schema is actually included,
- Responses API image placeholder objects are not serialized as fake chat content,
- unsupported `response_format` may fall back without changing model/prompt,
- diagnostics identify the exact contract stage without key/token/full prompt,
- resulting Persian title must preserve the real source identity and reject generic model-number output.

## REQ-49I-030 — Re-audit SEO before Catalog Web publish
Status: `CORE CONTRACT VERIFIED IN REPOSITORY / LOCAL PUBLISH E2E REQUIRED`

Required before Production:
- Persian title/H1 and useful product content,
- unique SEO title and description,
- canonical and index/follow state,
- OG product title/description/image,
- image Alt text,
- Product/ProductGroup + Offer structured data,
- breadcrumb and available review/FAQ structured data,
- safe public slug/legacy redirect,
- public product inclusion in `/sitemap.xml`,
- media/product page data verified after Local publish.

Dedicated Twitter title/description/image and `og:image:alt` are optional social-preview enhancements and are not blockers for this Catalog release.

## Operational Release Request
### REQ-REL-001 — Hand Catalog Center to employees and deploy approved release
Status: `BLOCKED BY 49.3I.23 WINDOWS QA + ONE LOCAL PUBLISH E2E + OWNER APPROVAL`

Product data must move through the existing publish/bridge/import contract. Do not copy the Local SQLite database over Production MySQL.

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
- bank transfer remains available,
- Sandbox E2E before live activation,
- secrets only in secure configuration.

## Change Rule
New requests do not authorize unrelated redesign. Extend/Patch/Wrap mature behavior and regression-test the exact active operator/store boundary.
