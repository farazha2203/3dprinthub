# CURRENT PROJECT STATE

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Base Epic: `epic/phase49-unified-product-slider-sync`
Active Phase: `49.3I`
Active Hotfix: `49.3I.29 — Structured Web Product Presentation`
Status: `IMPLEMENTED ON GITHUB / WINDOWS WEB QA REQUIRED`
Production: `UNTOUCHED / NOT APPROVED`

## Current Evidence
The owner reports the Local Catalog publish path successfully sent a Product into the Local Django Store. The resulting Product detail page then exposed an old generated `technical_notes` block directly to customers: source header lines followed by raw Catalog JSON and a duplicated `[Catalog Intelligence v8.5]` payload.

That payload contained useful customer facts such as weight/materials/categories, but also internal fields such as AI provider/model, fingerprint/source hash, batch UUID and desktop workflow state. Missing designer/license fields rendered as `-`.

## Verified Root Cause
`templates/store/product_detail.html` rendered `product.technical_notes|linebreaks` verbatim. Historical Catalog import code stores machine-oriented JSON inside that field for compatibility. The public template therefore treated an internal/debug persistence field as customer copy.

## 49.3I.29 Implemented on GitHub
- added `store/templatetags/store_product_presentation.py`,
- public presentation uses an explicit allowlist of customer-safe facts,
- legacy JSON is parsed server-side only for safe facts and is never emitted verbatim,
- canonical Product/Profile data takes precedence over legacy technical-notes payloads,
- missing `-`/unknown designer/license values are suppressed,
- weight and print time are formatted for Persian storefront display,
- Product detail now renders professional sections for highlights, technical/build facts, materials/colors, category path and source attribution,
- raw `product.technical_notes` is no longer rendered on the public Product page,
- internal AI provider/model, hashes/fingerprint, batch/workflow metadata are not returned to the template,
- existing AI-generated Persian description/use-description/technical features/sales bullets are reused; the public web request does not call AI,
- focused regression test added in `store/test_phase49_web_product_presentation.py`,
- dedicated phase document added at `docs/phases/PHASE49_3I29_WEB_PRODUCT_PRESENTATION.md`.

## Preserved Catalog Contract
- exact-link AI remains text-only and does not send image files/URLs,
- Product stage order remains 1..7 with free navigation,
- five-column vertical image gallery/full-screen/archive/block behavior remains,
- persistent diagnostics/no hidden startup AI remain,
- Product publish/bridge batch format is unchanged.

## Database / Migration / Safety
- Django migration: `NONE`
- Catalog schema migration: `NONE`
- no Product/media/history deletion
- no secret/API key changes
- Local SQLite is not copied to Production MySQL
- Production source and database untouched

## Verification Status
- owner reported the pre-49.3I.29 Local Publish path completed successfully,
- 49.3I.29 source + test are committed to GitHub,
- new storefront presentation still requires Windows Local pull/test/render QA,
- do not deploy Production until this new web delta passes Local Product-page verification.

## Exact Next Task
1. close Local Django/Catalog processes that hold stale code if needed,
2. verify clean Windows worktree,
3. fetch/prune + ff-only pull the live feature branch and verify Local HEAD == Remote HEAD,
4. run `manage.py check`, `makemigrations --check --dry-run`, and `store.test_phase49_web_product_presentation`,
5. start Local Django and open the already-imported Product,
6. verify no raw JSON / `[Catalog Intelligence v8.5]` / AI provider/model/hash/batch text is visible,
7. verify weight/materials/colors/categories/source are cleanly presented and missing fields are hidden,
8. after owner approval, perform read-only Host audit and deploy the approved GitHub snapshot only.

## Release Gate
49.3I.29 Local Web PASS → explicit owner approval → read-only Production branch/HEAD/venv/MySQL/backup verification → approved GitHub snapshot deploy → collectstatic + Passenger restart → public Product/SEO/media verification.
