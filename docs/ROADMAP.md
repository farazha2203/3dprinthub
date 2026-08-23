# PROJECT ROADMAP

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Epic: `Phase49 — Unified Product / Slider / Catalog Sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.19 — Canonical Source Identity Before AI`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA NEXT`
Production: `UNTOUCHED / NOT APPROVED`

## Permanent Delivery Order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → WINDOWS PULL --FF-ONLY → LOCAL TEST → COMMIT/PUSH IF LOCAL CODE CHANGES → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION BACKUP/DEPLOY/VERIFY`

## Immediate Business Priority
1. focused Windows acceptance of 49.3I.19 correct MakerWorld identity before AI,
2. regression acceptance of 49.3I.18 clipboard/bulk image/manual identity controls,
3. chain existing 49.3I.17 and acquisition gates,
4. exactly one Local Publish E2E,
5. explicit owner approval,
6. verify Production branch/path/venv/MySQL/backup/rollback,
7. deploy approved GitHub snapshot and verify Production,
8. then Store ZarinPal integration + Sandbox E2E.

## Phase49.3I Path
`Discovery Review → PS5.1 Guard → Gallery/AI First-Paint → Live Git Snapshot → Explorer/Routing → Selection Guard → Credential Persistence → Provider/Preview Recovery → Observable AI → SEO/Source → AI Trace → Provider Schema → Exact-Page UI/Image Fit → Paste/Batch Recovery → Mature Scan Restoration → Bulk Exact-Page Images/Add-to-Products → Resilient Acquisition Fallback/Cached Reuse → Single Active AI Runtime → Operator Editing/Bulk Metadata → Canonical Source Identity Before AI`.

## 49.3I.19 — Canonical Source Identity Rule
A Product must have a validated source identity before AI may translate or generate SEO/content:
- generic placeholders `Model <id>` / `MakerWorld model <id>` / Persian equivalents are rejected,
- valid exact-page/scraped title wins,
- exact MakerWorld model URL slug is the deterministic fallback,
- candidate title is canonicalized before candidate persistence,
- Add-to-Products canonicalizes again before Product persistence,
- legacy Product AI source context is repaired in memory before generation,
- Product Workspace can persist corrected source title and rebuild all AI text/SEO without deleting/reimporting the product.

Acceptance examples:
- `2845731-cake-stand` → `Cake Stand`,
- `2896217-ribbed-cake-stand-cookie-platter` → `Ribbed Cake Stand Cookie Platter`.

## 49.3I.18 — Preserved Additive Operator Editing
- global editable-widget clipboard shortcuts,
- bulk image filename/Alt/Title/Caption operations,
- explicit operator-authoritative Persian name,
- replace wrong name across editorial content,
- full AI rebuild for operator-confirmed identity.

## 49.3I.17 — Preserved Canonical AI Rule
- one saved Provider,
- one saved Model for that Provider,
- one secure key belonging to that Provider,
- no automatic fallback to another configured Provider,
- no hidden AI request when Product Workspace opens,
- no `/models` catalog request before Product content generation,
- explicit Settings model search/test remains available,
- stale Tk callbacks cannot become fatal Product Workspace dialogs.

## Acquisition Contract Preserved
49.3I.16 remains the fallback mechanism:
- discovery `locator-safe → HTTP/HTML → attached Chrome 9222 → cached candidate DB`,
- images `locator-safe → HTTP → mature DOM → Chrome 9222 → listing thumbnail`,
- product max 100 / image max 20,
- Add-to-Products without Rich Direct Full Fetch,
- Archive/Block/dedupe and staged-image readiness.

## Git State
Feature branch base was verified against current Epic before 49.3I.19: base `eb17847d7669d8a07e857a6e7acc4a8012a94991`, feature ahead and not behind.

49.3I.19 code implementation anchor: `d9d3d617ed22dd3096379e668697f0f9fab87ca0`; following commits are documentation updates.

Django migration: NONE. Catalog schema migration: NONE. Production untouched.

## Focused Windows Gate
1. clean worktree + live fetch/ff-only feature branch,
2. compile new/touched modules,
3. run 49.3I.19 source-identity tests plus 49.3I.18/16/15/discovery regressions,
4. `launch.py --verify-only`,
5. open existing MakerWorld product `2896217` and repair source title; expect `Ribbed Cake Stand Cookie Platter`,
6. run combined source-title repair + full AI rebuild and inspect Persian title/text/SEO/image metadata,
7. verify `2845731` resolves to `Cake Stand`,
8. verify 49.3I.18 clipboard/bulk/manual override features,
9. chain existing 49.3I.17 baseline gate.

If PASS, proceed to one Local Publish E2E and then Production approval gate.

## Next Product Phase
After Catalog Production verification: Store checkout ZarinPal request/callback/verify, Sandbox E2E, then one owner-approved low-value live payment while bank transfer remains available.