# PROJECT ROADMAP

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Epic: `Phase49 — Unified Product / Slider / Catalog Sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.20 — Visible Operator Panels`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA NEXT`
Production: `UNTOUCHED / NOT APPROVED`

## Permanent Delivery Order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → WINDOWS PULL --FF-ONLY → LOCAL TEST → COMMIT/PUSH IF LOCAL CODE CHANGES → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION BACKUP/DEPLOY/VERIFY`

## Immediate Business Priority
1. focused Windows acceptance of 49.3I.20 visible operator controls,
2. focused Windows acceptance of 49.3I.19 correct MakerWorld identity before AI,
3. regression acceptance of 49.3I.18 clipboard/bulk image/manual identity controls,
4. chain existing 49.3I.17 and acquisition gates,
5. exactly one Local Publish E2E,
6. explicit owner approval,
7. verify Production branch/path/venv/MySQL/backup/rollback,
8. deploy approved GitHub snapshot and verify Production,
9. then Store ZarinPal integration + Sandbox E2E.

## Phase49.3I Path
`Discovery Review → PS5.1 Guard → Gallery/AI First-Paint → Live Git Snapshot → Explorer/Routing → Selection Guard → Credential Persistence → Provider/Preview Recovery → Observable AI → SEO/Source → AI Trace → Provider Schema → Exact-Page UI/Image Fit → Paste/Batch Recovery → Mature Scan Restoration → Bulk Exact-Page Images/Add-to-Products → Resilient Acquisition Fallback/Cached Reuse → Single Active AI Runtime → Operator Editing/Bulk Metadata → Canonical Source Identity Before AI → Visible Operator Panels`.

## 49.3I.20 — Visible Operator Panels
The 49.3I.18/49.3I.19 controls are already functionally implemented; this hotfix fixes only their final visible layout boundary.

Required visible order:
- Stage 3 Images: `عملیات گروهی همه تصاویر منتخب سایت` before the expandable image gallery,
- Stage 4 Content/SEO: `هویت واقعی محصول در منبع — قبل از ترجمه و SEO` first,
- then `اصلاح نام محصول و بازسازی متن / SEO`,
- then the mature content toolbar/editor.

Implementation is additive and layout-only:
- new `phase49_3i20_visible_operator_panels.py`,
- wired after 49.3I.18 + 49.3I.19 in the final Product Workspace composition,
- existing button commands/state are preserved,
- no schema/migration/AI provider/pricing/publish/FTP/Bridge changes.

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
Before 49.3I.20 implementation, the live feature branch remote HEAD was verified as `6c9cb06a573f6251c55e491ce187bab27fd7ffd7`.

49.3I.20 implementation commits begin at:
- `cf634206da426e6627cb47e9a860fd6591b169b9` — layout module,
- `74b7de97531dae5346c864f06665269ffd8d84a3` — focused tests,
- `658311877a7d79b1a2d923e91054626728d2ae37` — final composition wiring.

Always use the live fetched branch HEAD for Windows delivery; documentation commits may follow.

Django migration: NONE. Catalog schema migration: NONE. Production untouched.

## Focused Windows Gate
1. clean worktree + live fetch/ff-only feature branch,
2. verify Local HEAD == fetched Remote HEAD,
3. compile 49.3I.20 + touched composition modules,
4. run 49.3I.20/19/18 tests plus 49.3I.16/15/discovery regressions,
5. `launch.py --verify-only`,
6. visually verify Stage 3 bulk panel is at the top,
7. visually verify Stage 4 source-identity + AI rebuild panels are above the editor,
8. repair existing MakerWorld product `2896217`; expect `Ribbed Cake Stand Cookie Platter`,
9. run combined source-title repair + full AI rebuild and inspect Persian title/text/SEO/image metadata,
10. verify `2845731` resolves to `Cake Stand`,
11. verify 49.3I.18 clipboard/bulk/manual override features,
12. chain existing 49.3I.17 baseline gate.

If PASS, proceed to one Local Publish E2E and then Production approval gate.

## Next Product Phase
After Catalog Production verification: Store checkout ZarinPal request/callback/verify, Sandbox E2E, then one owner-approved low-value live payment while bank transfer remains available.
