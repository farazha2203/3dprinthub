# OWNER REQUESTS

Last Updated: 2026-08-25

Older detailed request history remains available in Git history. This file keeps the active acceptance contracts.

## Preserved Core Contracts
- REQ-49H-001: AI/SEO execution/result/error visibility with sanitized diagnostics.
- REQ-49H-002: real provider-supported cost only; never invent unknown cost.
- REQ-49H-003: image intake default 5 / hard max 20.
- REQ-49I-001: explicit Search/Listing URL is authoritative.
- REQ-49I-003: Archive/Not Needed blocks rediscovery without destructive deletion.
- REQ-49I-004: dedupe by source + external id + normalized URL.
- REQ-49I-006: Product Workspace remains canonical editor.
- REQ-49I-007: Fixed / Range / Formula remain independent.
- REQ-49I-009: GitHub-first delivery; verify live branch/HEAD before Local/Host operations.
- REQ-49I-014: Provider/FTP/Bridge secure persistence.
- REQ-49I-024: exactly one saved Provider/Model/key path for Product AI; no hidden fallback/model scan/AI-on-open.
- REQ-49I-025: source title canonical before translation/SEO.
- REQ-49I-027: AI actions must not freeze and must be diagnosable.
- REQ-49I-028: exact Product URL grounds full Product AI refresh.

## REQ-49I-033 — Canonical Product stages and free navigation
Status: `IMPLEMENTED / PRODUCTION CODE DEPLOYED`

## REQ-49I-034 — Exact-link completion is the single complete Product AI action
Status: `IMPLEMENTED / PRODUCTION CODE DEPLOYED`

## REQ-49I-035 — Images page five-column vertical gallery
Status: `IMPLEMENTED / PRODUCTION CODE DEPLOYED`

## REQ-49I-036 — Products gallery bulk archive/delete with duplicate prevention
Status: `IMPLEMENTED / PRODUCTION CODE DEPLOYED`

## REQ-49I-037 — New acquisition defaults to five images plus source screenshot
Status: `IMPLEMENTED / PRODUCTION CODE DEPLOYED`

## REQ-49I-038 — Storefront Product intelligence must be customer-readable, not raw JSON
Status: `PRODUCTION VERIFIED`

Owner acceptance verified in Production:
- public Product page does not dump raw Catalog JSON,
- internal AI/runtime/hash fields are not exposed,
- Product presentation endpoint returned HTTP 200 and sanitization checks passed,
- missing-source placeholder noise is removed by the presentation layer,
- public rendering performs no AI call.

## Operational Release Request
### REQ-REL-001 — Hand Catalog Center to employees and deploy approved release
Status: `PRODUCTION CODE DEPLOYED / ONE REAL CATALOG SITE-PUBLISH E2E REMAINS`

Remaining acceptance:
- publish one new prepared Product through the official Site Publish/Bridge path,
- verify Product + media + SEO on Production,
- verify safe/idempotent re-publish,
- then mark Phase49.3I accepted.

## Next Product Request
### REQ-PAY-001 — Normal Store checkout must support online payment
Status: `REQUESTED / AFTER PHASE49.3I FINAL PRODUCT-PUBLISH E2E`

## Change Rule
New requests do not authorize unrelated redesign. Extend/Patch/Wrap mature behavior and regression-test the exact active operator/store boundary.
