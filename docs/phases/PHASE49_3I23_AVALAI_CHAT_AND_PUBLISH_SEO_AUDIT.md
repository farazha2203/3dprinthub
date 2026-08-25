# Phase49.3I.23 — AvalAI Exact Chat Contract + Publish SEO Audit

Updated: 2026-08-25
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA REQUIRED`
Production: `UNTOUCHED / NOT APPROVED`

## Owner Evidence
The exact MakerWorld link works when used directly with AvalAI, while Catalog Center's `تکمیل همه اطلاعات بر اساس لینک محصول` does not reliably produce/apply the requested Persian product content. The same product already has a correct canonical English source identity but still retains a generic Persian model-number title.

## Verified Request-Contract Defects
Repository inspection found that the generic non-OpenAI structured path did not match the intended Product AI contract:
- `AIProviderClient.structured_response()` called `choose_model()` first, causing a hidden `/models` discovery before normal Product generation,
- Responses-style `input_text` / `input_image` wrapper objects were serialized as one JSON string and sent as chat user text,
- the system message demanded output matching a schema but the actual JSON schema was not included in the prompt,
- image placeholder objects therefore appeared as text rather than as a valid multimodal AvalAI request,
- this contradicted the Phase49.3I.17 rule that Product AI uses the exact operator-saved Provider/Model without hidden model discovery.

## Implemented 49.3I.23
`catalog_center/app/phase49_3i23_avalai_chat_contract.py` is an additive AvalAI-only Product request adapter:
- applies only to product-bound AvalAI structured generation,
- uses the exact saved model directly; no hidden `/models` request,
- sends a normal Chat Completions `model + messages` request through the existing provider transport,
- extracts the actual product/source text instead of serializing Responses API wrappers,
- includes the exact output JSON schema in the system instruction,
- does not serialize fake `input_image` placeholders into the prompt,
- keeps `response_format=json_object` when supported and falls back to the same prompt/model without it when the gateway rejects that parameter,
- parses one JSON object and then returns through the existing content validation/apply path,
- records only sanitized request-contract metadata; no key, Authorization header or full prompt is logged.

Composition installs this after 49.3I.22 so the corrected request inherits the bounded timeout, diagnostics and Tk main-thread handoff.

## Publish SEO Audit
The current Store publish path already carries the core SEO contract:
- Persian H1/product title, short/full content and image Alt values are imported from Catalog data,
- `seo_title_fa` and `seo_description_fa` sync to Product meta title/description,
- focus keyword, OG title/description, source attribution and hashtags are synchronized,
- product pages emit canonical URL and robots index/follow controls,
- Product/ProductGroup + Offer + Breadcrumb + optional Review/FAQ structured data are emitted,
- public `/sitemap.xml` contains product/category/service/static sitemap classes,
- product detail emits OG product metadata and product image,
- safe public ASCII slug / legacy redirect contract is preserved,
- image metadata and selected local media are part of the Catalog import/publish contract.

Non-blocking enhancement debt: the base template currently emits `twitter:card` but not dedicated `twitter:title`, `twitter:description`, `twitter:image`, and does not emit `og:image:alt`. These improve social previews but are not treated as a blocker for the current Catalog publish gate.

## Safety
- Django migration: NONE
- Catalog schema migration: NONE
- no reset/drop/truncate
- no whole SQLite database transfer to Production
- no secrets committed/logged
- no Production change

## Windows Acceptance
1. clean worktree and ff-only pull live feature branch,
2. compile 49.3I.23 and composition modules,
3. run `test_phase49_3i23_avalai_chat_contract` plus inherited 49.3I.22/21/20/19/18 regressions,
4. run `catalog_center/launch.py --verify-only`,
5. open product `2896217-ribbed-cake-stand-cookie-platter`,
6. run `تکمیل همه اطلاعات بر اساس لینک محصول`,
7. Diagnostics must show `avalai_exact_chat_contract` followed by `structured_content_avalai_exact` (or compatibility fallback) and no Product `/models` preflight,
8. received preview must contain the real product identity and a non-generic Persian title,
9. approve apply and verify content/SEO/image metadata remain consistent,
10. if any request fails, export the sanitized Diagnostics bundle before closing the app.

## Release Gate After PASS
Run exactly one `LOCAL PUBLISH ONLY`, then verify Local Store/Admin/Product/Media/SEO including canonical, meta, OG, Product JSON-LD and `/sitemap.xml`. Only after explicit owner approval may Production state be verified read-only and the approved GitHub snapshot be deployed.
