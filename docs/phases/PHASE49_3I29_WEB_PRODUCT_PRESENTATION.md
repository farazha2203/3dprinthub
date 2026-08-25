# Phase49.3I.29 — Structured Web Product Presentation

Updated: 2026-08-25
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Status: `IMPLEMENTED ON GITHUB / WINDOWS WEB QA REQUIRED`
Production: `UNTOUCHED`
Migration: `NONE`

## Owner Evidence
A successful Local Publish showed the Product detail page exposing desktop/internal Catalog payloads directly under technical notes. The customer saw source header lines followed by large raw JSON blocks, including AI/runtime fields such as provider/model, fingerprints, batch identifiers and workflow state. Missing source fields were also rendered as `-`, making the section noisy and unclear.

## Requested Delta
- keep the useful AI-generated Persian Product content,
- present source, weight, print time, dimensions, materials, colors, categories, sales bullets and technical features as a professional customer-facing layout,
- never render raw Catalog JSON on the public Product page,
- hide missing designer/license values instead of displaying `-`,
- never expose AI provider/model, fingerprint/hash, batch/workflow internals,
- preserve existing SEO, pricing, media, cart and source-link behavior,
- no runtime AI request from the public web page.

## Implementation
- added `store.templatetags.store_product_presentation` as a presentation-only compatibility layer,
- legacy JSON embedded in `Product.technical_notes` is parsed server-side only to recover customer-safe facts,
- canonical model/profile fields have priority over legacy payloads,
- public output is allowlisted; internal AI/audit fields are never returned,
- weight and print minutes receive Persian human-readable formatting,
- duplicate materials/colors/categories/tags are normalized,
- empty/unknown/`-` source values are suppressed,
- `templates/store/product_detail.html` no longer renders `product.technical_notes|linebreaks`,
- Product detail now shows structured cards for highlights, technical/build specs, materials/colors, categories and source attribution,
- existing AI-authored `description`, `use_description`, technical features and sales bullets are reused; public requests never call AI.

## Must Not Touch
- Product URLs/slugs/canonical behavior,
- Store order/cart/pricing behavior,
- Product media ownership,
- Catalog publish batch format,
- Production DB schema,
- Catalog SQLite schema,
- source acquisition or desktop AI workflow.

## Regression Contract
- raw `technical_notes` is not rendered publicly,
- internal `ai_provider`, `ai_model`, `fingerprint`, source hashes/batch/workflow metadata are absent from the public-facts result,
- `150` grams renders as `150 گرم`,
- `95` minutes renders as `1 ساعت و 35 دقیقه`,
- missing designer/license values do not render as placeholders,
- existing source URL remains linkable,
- no migration.

## Release Gate
GitHub snapshot → Windows ff-only pull → `manage.py check` + migration dry-run + focused test → Local Product detail HTTP/render QA → explicit owner approval → read-only Host audit → deploy approved GitHub snapshot → collectstatic/restart → Production Product/SEO/media smoke verification.
