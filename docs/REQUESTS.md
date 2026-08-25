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

## REQ-49I-029 — AvalAI Product generation must use the exact working provider contract
Status: `IMPLEMENTED ON FEATURE BRANCH / WINDOWS LOCAL QA REQUIRED`

Acceptance:
- exact saved AvalAI model; no hidden Product `/models`,
- application fetches/sanitizes the exact source page as deterministic evidence,
- supported AvalAI URL tools may add explicit page/web evidence when extracted facts are sparse,
- bare URL text is never treated as proof that browsing occurred,
- structured output prefers `json_schema`, with same-model compatibility fallback,
- diagnostics identify Provider/Model/URL-tool/fallback stages without secret/full prompt,
- resulting Persian identity must preserve the actual Product and reject generic model-number content.

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

## REQ-49I-031 — Program logs, hang diagnostics and startup performance must be operator-accessible
Status: `IMPLEMENTED ON FEATURE BRANCH / WINDOWS LOCAL QA REQUIRED`

Owner request: record the application from startup so slow open/close/hangs can be diagnosed, expose Program Log on Dashboard, and create one safe diagnostic file suitable for sharing/uploading to GitHub.

Acceptance:
- lifecycle logging begins before the wrapped App constructor and continues through close,
- Program Log and AI Log are visible from Dashboard,
- safe diagnostic export includes redacted runtime/main/hang-log tails,
- no API key/password/token/full Authorization header is exported,
- Tk heartbeat records meaningful UI lag,
- an extended UI stall creates an all-thread dump without asking Tk from the watchdog thread,
- hidden Provider model-list network work is not allowed during application construction,
- explicit model search remains available after first paint,
- obvious non-text models cannot be selected for Product editorial structured generation,
- AvalAI model rows are not falsely labeled all-free because generic pricing metadata is absent.

## Operational Release Request
### REQ-REL-001 — Hand Catalog Center to employees and deploy approved release
Status: `BLOCKED BY 49.3I.24 WINDOWS QA + ONE LOCAL PUBLISH E2E + OWNER APPROVAL`

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
