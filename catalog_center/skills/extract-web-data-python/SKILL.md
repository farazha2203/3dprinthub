---
name: extract-web-data-python
description: Multi-strategy Python web data extraction for 3DPrintHub product/catalog ingestion.
---

# Extract Web Data — Python

## Objective
Extract the richest reliable public product data while preserving provenance and avoiding anti-bot circumvention.

## Strategy order
1. Site-specific adapter.
2. JSON-LD / schema.org Product, Offer, AggregateRating.
3. Embedded application JSON such as Next.js/Nuxt state.
4. OpenGraph and meta tags.
5. Browser-rendered DOM after JavaScript.
6. Breadcrumbs, tables, definition lists, product tabs and labeled sections.
7. `currentSrc`, `srcset`, lazy-image attributes and gallery links.
8. Public JSON/XHR/fetch responses requested by the page.
9. Public downloadable file links (`STL`, `3MF`, `OBJ`, `STEP`, `STP`, `IGES`, `DXF`, ZIP).
10. Conservative text heuristics for missing weight/dimensions/spec labels.

## Browser behavior
- Use a real Playwright Chromium/installed browser context and persistent profile where appropriate.
- Preserve ordinary cookies/session and allow manual user login.
- Respect rate limits, cache results and retry transient errors with backoff.
- Do not bypass CAPTCHA, access controls, fingerprinting or anti-bot mechanisms.

## Product image rules
- Never treat a page screenshot as a product image.
- Score/filter icons, logos, avatar, banners, placeholders and tiny images.
- Preserve all credible candidate URLs and local downloaded copies.
- Keep `found`, `selected_for_site`, and `primary` as separate states.

## Data quality
- Keep source URL/canonical URL/external ID.
- Store source facts separately from translated/AI content.
- Record source method/provenance where possible.
- On refetch, diff source data and preserve operator edits.
- Prevent duplicates using source + external ID + canonical URL + stable fingerprint.
