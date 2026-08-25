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

## REQ-49I-027 — AI actions must not look frozen and must be diagnosable
Status: `IMPLEMENTED ON FEATURE BRANCH / WINDOWS LOCAL QA REQUIRED`

Owner evidence:
- multiple AI buttons can stay at `در حال اتصال به هوش مصنوعی`,
- Task Center showed a 03:30 ceiling,
- source-title reread works while source-title + full AI rebuild can remain waiting,
- image SEO/product info/all-fields AI actions exhibit the same failure class.

Acceptance:
- normal Product AI may not block the Tk UI thread,
- provider request has a bounded fail-fast ceiling rather than an opaque multi-minute wait,
- request-start must be recorded before network wait,
- success/error/timeout must identify Provider/Model/operation/duration,
- a Stop/Cancel action prevents late result application,
- busy state is released after cancellation/failure,
- diagnostics must redact API key/token/Authorization values,
- operator can export a local diagnostic bundle for troubleshooting,
- no GitHub PAT/API key is stored in logs or requested through Chat.

Implementation: 49.3I.21 global provider guard + observable link-refresh job dialog. Default AI POST ceiling 75 seconds, environment override constrained to 20..120 seconds.

## REQ-49I-028 — Complete all editable product information from the exact Product URL
Status: `IMPLEMENTED ON FEATURE BRANCH / WINDOWS LOCAL QA REQUIRED`

Owner request: add one professional action that starts from the exact product link, reads the real source, gives the AI enough grounded information, shows received data, then updates the whole editable editorial surface only after confirmation.

Acceptance:
- new action `تکمیل همه اطلاعات بر اساس لینک محصول`,
- exact persisted `source_url` is authoritative,
- app fetches/parses the actual source page first,
- canonical source title is established before generation,
- AI receives the URL plus sanitized source facts and selected images/materials/colors,
- dialog visibly shows source fetch → AI request → response received → preview → apply,
- no DB update before operator confirmation,
- apply updates Persian title, descriptions, SEO, keywords and image Alt/Title/Caption/metadata consistently through the existing mature apply path,
- source URL, price, stock and commercial/operator choices are not overwritten,
- if source/AI fails, previous Product data remains intact,
- cancellation means a late result is ignored.

Primary acceptance fixture:
`https://makerworld.com/en/models/2896217-ribbed-cake-stand-cookie-platter?from=search#profileId-3236824`

After successful refresh, the product must not retain the generic Persian identity `مدل میکرورلد 2896217`.

## Operational Release Request
### REQ-REL-001 — Hand Catalog Center to employees and deploy approved release
Status: `BLOCKED BY 49.3I.21 WINDOWS QA + ONE LOCAL PUBLISH E2E + OWNER APPROVAL`

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

## Canonical Windows Gate
Run 49.3I.21 focused tests + 49.3I.20/19/18 regressions, then chain the existing 49.3I.17 and acquisition baseline gates. Production remains untouched until PASS + Local Publish E2E + owner approval.

## Change Rule
New requests do not authorize unrelated redesign. Extend/Patch/Wrap mature behavior and regression-test the exact active operator/store boundary.