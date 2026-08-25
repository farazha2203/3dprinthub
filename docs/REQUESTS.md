# OWNER REQUESTS

Last Updated: 2026-08-25

Older detailed request history remains available in Git history. This file keeps the active acceptance contracts.

## Preserved Core Contracts
- REQ-49H-001: AI/SEO execution/result/error visibility with sanitized diagnostics.
- REQ-49H-002: real provider-supported cost only; never invent unknown cost.
- REQ-49H-003: image intake default 5 / hard max 20 from 49.3I.26 onward.
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
Status: `CORE CONTRACT VERIFIED IN REPOSITORY / LOCAL PUBLISH E2E REPORTED OK`

Persian title/content, unique SEO title/description, canonical, index state, OG, image Alt, Product/Offer/Breadcrumb/Review/FAQ structured data, safe slug/redirect, sitemap and Local media/product verification are required before Production.

## REQ-49I-031 — Program logs, hang diagnostics and startup performance are operator-accessible
Status: `IMPLEMENTED ON FEATURE BRANCH / WINDOWS LOCAL QA REQUIRED`

Lifecycle logging, Dashboard Program/AI logs, safe diagnostic export, Tk lag/hang trace, secret redaction and no automatic provider work during startup are required.

## REQ-49I-032 — Product editing workflow and stable repeated operation
Status: `SUPERSEDED/REFINED BY REQ-49I-033..038`

49.3I.25 tested Content-first ordering. Owner QA determined the original 1..7 sequence is clearer and that readiness should not lock stage navigation.

## REQ-49I-033 — Restore canonical 1..7 Product order with free navigation
Status: `IMPLEMENTED ON FEATURE BRANCH / WINDOWS LOCAL QA REQUIRED`

Owner acceptance:
- 1 Basic Info, 2 Commerce, 3 Images, 4 Content/SEO, 5 Source/License, 6 Slider, 7 Review/Publish,
- Product opens on Basic Info with no Content-first lock popup,
- operator can open every stage even when another stage is incomplete,
- readiness remains visible and blocks publish only,
- Product Workspace has a maximize/full-screen action.

## REQ-49I-034 — Exact-link completion is the single complete Product AI action
Status: `IMPLEMENTED ON FEATURE BRANCH / WINDOWS LOCAL QA REQUIRED`

Owner acceptance:
- progress shows percentage and current phase from source read through apply,
- AI wait ceiling is 120 seconds,
- if AI response times out, source URL is rechecked separately and source/provider failure is distinguished,
- source facts include real title, creator/manufacturer where available, source/category, URL, description, weight and print time,
- selected image files/URLs are not sent to AI,
- the same Product result fills Persian Product content/SEO and image filename/Alt/Title/Caption/Keywords,
- a second Image SEO AI request is not required for the normal locally-acquired Product path,
- unified completion must not start hidden network image downloads merely to finish image Metadata.

## REQ-49I-035 — Images page is five-column vertical gallery
Status: `IMPLEMENTED ON FEATURE BRANCH / WINDOWS LOCAL QA REQUIRED`

Five image cards per row, continue downward, vertical scrollbar/mouse wheel when needed, mature image controls preserved. A delayed older horizontal layout must not overwrite this final layout.

## REQ-49I-036 — Products gallery bulk archive/delete with duplicate prevention
Status: `IMPLEMENTED ON FEATURE BRANCH / WINDOWS LOCAL QA REQUIRED`

Owner acceptance:
- Product cards can be selected individually and as a visible group,
- both unpublished and already-synced Products can be archived from the Products gallery,
- synced/edited cards have a white visual treatment,
- delete/block keeps source identity/link so the same Product is not downloaded again,
- physical files are not deleted by this Catalog list action,
- archive and delete/block remain distinct operations.

## REQ-49I-037 — New acquisition defaults to five images plus source screenshot
Status: `IMPLEMENTED ON FEATURE BRANCH / WINDOWS LOCAL QA REQUIRED`

Normal source image intake defaults to five while hard maximum remains 20. One full-page source screenshot is added as an extra local, non-selected Product gallery reference during approved full acquisition.

## REQ-49I-038 — Storefront Product intelligence must be customer-readable, not raw JSON
Status: `IMPLEMENTED ON GITHUB / WINDOWS WEB QA REQUIRED`

Owner acceptance:
- public Product page must not dump desktop Catalog JSON or `[Catalog Intelligence v8.5]`,
- AI-generated useful data must be organized into clear Persian sections,
- weight, print time, materials, colors, categories, technical features and sales highlights should be presented cleanly when available,
- source link remains visible,
- missing designer/license values are hidden instead of showing `-`,
- AI provider/model, fingerprints/hashes, batch UUID and desktop workflow internals must never be public,
- public web rendering must not make a runtime AI request.

## Operational Release Request
### REQ-REL-001 — Hand Catalog Center to employees and deploy approved release
Status: `BLOCKED BY 49.3I.29 WINDOWS WEB QA + OWNER APPROVAL`

Product data moves through the existing publish/bridge/import contract. Local SQLite is never copied over Production MySQL.

## Next Product Request
### REQ-PAY-001 — Normal Store checkout must support online payment
Status: `REQUESTED / AFTER CATALOG DEPLOY`

## Change Rule
New requests do not authorize unrelated redesign. Extend/Patch/Wrap mature behavior and regression-test the exact active operator/store boundary.
