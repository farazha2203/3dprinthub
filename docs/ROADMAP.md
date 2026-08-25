# PROJECT ROADMAP

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Epic: `Phase49 — Unified Product / Slider / Catalog Sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.29 — Structured Web Product Presentation`
Status: `IMPLEMENTED ON GITHUB / WINDOWS WEB QA NEXT`
Production: `UNTOUCHED / NOT APPROVED`

## Permanent Delivery Order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → WINDOWS PULL --FF-ONLY → LOCAL TEST → LOCAL PUBLISH/WEB E2E → OWNER APPROVAL → READ-ONLY HOST VERIFY → DEPLOY FROM GITHUB → PRODUCTION VERIFY`

## Immediate Priority
1. Pull the live 49.3I.29 GitHub snapshot to Windows.
2. Run Django check + migration dry-run + focused storefront-presentation regression.
3. Open the already-imported Local Product and verify customer-facing technical/source content.
4. Confirm raw `technical_notes` JSON and internal Catalog/AI/audit fields are not public.
5. Confirm useful AI-curated facts are shown as structured Persian cards/chips: highlights, weight, print time, materials, colors, categories, technical features and source attribution.
6. Confirm missing designer/license values are hidden instead of showing `-`.
7. Preserve existing SEO, Product media, pricing/cart, source URL, Product schema and Catalog publish behavior.
8. After explicit owner approval, perform read-only Host/MySQL/backup/rollback audit and deploy the exact approved GitHub commit.

## 49.3I.29 Acceptance Contract
- no public template renders `product.technical_notes|linebreaks`,
- legacy embedded Catalog JSON is parsed server-side only as a compatibility source,
- only allowlisted customer facts reach the template,
- `ai_provider`, `ai_model`, fingerprints/hashes, batch UUID and desktop workflow internals are never returned,
- Persian AI-authored Product description/use-description/technical features/sales bullets remain the content source; there is no web-time AI call,
- weight/time have human-readable Persian formatting,
- source URL remains available,
- missing placeholder source fields are suppressed,
- no migration and no publish batch change.

## Preserved 49.3I Catalog Contract
- canonical Product stage order: Basic Info → Commerce → Images → Content/SEO → Source/License → Slider → Review/Publish,
- stage navigation stays free; readiness blocks publish only,
- exact-link Product completion uses saved Provider/Model and sends text facts only with zero image upload,
- Product SEO + selected-image text metadata remain one unified action,
- images remain five cards/row with vertical scrolling,
- Products selection/archive/identity-preserving block remains,
- acquisition default remains five source images plus one local source screenshot,
- startup never probes AI providers without explicit operator action,
- diagnostic history remains cumulative.

## Database / Migration
Django migration: NONE. Catalog schema migration: NONE. Local SQLite is not copied into Production MySQL. Production untouched.

## Release Gate
49.3I.29 Windows Web PASS → explicit owner approval → read-only Production project/branch/commit/venv/MySQL/backup verification → approved GitHub snapshot only → `manage.py check` + migration plan → collectstatic → Passenger restart → Product/Home/Admin/Cart/Media/SEO HTTP verification.
