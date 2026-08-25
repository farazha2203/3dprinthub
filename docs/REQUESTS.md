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

## REQ-49I-029 — AvalAI Product generation uses the exact working provider contract
Status: `IMPLEMENTED ON FEATURE BRANCH / WINDOWS LOCAL QA REQUIRED`

Exact saved model, no hidden Product model scan, deterministic source-page fetch, schema-first structured output, sanitized diagnostics and real Product identity are required.

## REQ-49I-030 — Re-audit SEO before Catalog Web publish
Status: `CORE CONTRACT VERIFIED IN REPOSITORY / LOCAL PUBLISH E2E REQUIRED`

Persian title/content, unique SEO title/description, canonical, index state, OG, image Alt, Product/Offer/Breadcrumb/Review/FAQ structured data, safe slug/redirect, sitemap and Local media/product verification are required before Production.

## REQ-49I-031 — Program logs, hang diagnostics and startup performance are operator-accessible
Status: `IMPLEMENTED ON FEATURE BRANCH / WINDOWS LOCAL QA REQUIRED`

Lifecycle logging, Dashboard Program/AI logs, safe diagnostic export, Tk lag/hang trace, secret redaction and no automatic provider work during startup are required.

## REQ-49I-032 — Product-first editing workflow and stable repeated operation
Status: `IMPLEMENTED ON FEATURE BRANCH / WINDOWS LOCAL QA REQUIRED`

Owner acceptance:
- `محتوا و SEO` is Product Stage 1 so Persian identity/content/SEO can be filled first,
- `اطلاعات پایه` is Stage 2 and contains `🌐 تکمیل همه اطلاعات بر اساس لینک محصول`,
- any legacy Product-data-send action routes to that same exact-link workflow,
- exact-link source intake also carries available weight/print time; MakerWorld exact `profileId` weight is preferred when present,
- incomplete stages never block opening Images/Commerce/Source or another stage,
- Images displays all controlled Product image cards in rows of five and scrolls vertically when needed; existing metadata/selection/primary/remove/open controls remain,
- exact-link completion must not broadly resave the Product before AI,
- Local/site publish preflight shows the actual missing items and may offer exact-link AI completion for AI-fillable gaps,
- opening the application does not test provider connectivity or fetch models; only explicit operator Search/Test may do so,
- historical Program/audit logs survive close/reopen and diagnostic export; startup never clears them,
- repeated Product edit/AI cycles must not produce `cannot commit - no transaction is active`,
- AI remains background/observable during legitimate slow provider responses.

## Operational Release Request
### REQ-REL-001 — Hand Catalog Center to employees and deploy approved release
Status: `BLOCKED BY 49.3I.25 WINDOWS QA + ONE LOCAL PUBLISH E2E + OWNER APPROVAL`

Product data moves through the existing publish/bridge/import contract. Local SQLite is never copied over Production MySQL.

## Next Product Request
### REQ-PAY-001 — Normal Store checkout must support online payment
Status: `REQUESTED / AFTER CATALOG DEPLOY`

## Change Rule
New requests do not authorize unrelated redesign. Extend/Patch/Wrap mature behavior and regression-test the exact active operator/store boundary.
