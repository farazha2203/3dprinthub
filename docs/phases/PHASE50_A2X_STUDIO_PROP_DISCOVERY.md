# Phase50.A2X — Studio/photography prop discovery

Date: 2026-10-10
Status: LOCAL_TESTED; GitHub/Host/Production pending.

## Requested delta
- Make relevant custom studio props and photography decor discoverable through Persian Store search.
- Add a distinct service landing that explains what can be requested and starts the existing custom Product Request flow.
- Cross-link the page from Home services, the Isfahan service landing and the public sitemap.
- Review the public Instagram profile and existing public decor products; do not change account state or publish.

## Findings
- Before the code change, public `GET /store/?q=آتلیه` returned zero product cards, while `?q=دکور` returned decor products, including table lamps, display pieces and decorative figures.
- The Product model already has `hashtags` and technical notes, but Store search omitted both fields. Search now honors them and expands explicit studio/photography intent to decor/prop/stand-related terms. This does not rewrite catalog records or mass-tag products; false positives should be reviewed against actual product detail pages.
- Public profile `@3dprinthub_ir` loads and its public bio already mentions professional 3D printing, custom parts and decor. The profile is small and its public Insights cannot be inspected through available tools. This chat has no connected Meta management tool; that is distinct from the existing desktop app's provider credentials/API implementation.
- Google recommends useful, people-first page content, descriptive headings and truthful structured data; a sitemap is discovery help, not an indexing or ranking guarantee. See [Google helpful content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content), [Search Essentials](https://developers.google.com/search/docs/essentials) and [LocalBusiness structured data](https://developers.google.com/search/docs/appearance/structured-data/local-business).
- Repository verification: Catalog Center includes Buffer (default) and Direct Meta/Instagram providers. Buffer Feed/Story services are implemented in `catalog_center/app/buffer_publish.py`; the Direct Graph API Feed/Carousel client is in `catalog_center/app/instagram_publish.py`; Settings reads credentials through the secure secret store / Windows Credential Store. A2S records a real Buffer Instagram channel connection as PASS. That historical Buffer check does not prove the current token is valid, nor does Direct Meta configuration prove its token/app permissions are currently active. No API connection test or post was executed in this SEO task. Meta's requirements and limits are documented in its [Instagram API collection](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api).

## Implementation
- New canonical candidate: `/store/services/studio-props-and-photography-decor/`.
- Persian title targets “پراپ و دکور آتلیه عکاسی” and Isfahan, with coverage for product photography, children/newborn props, lightweight tabletop decor, display stands and custom design from sketches/samples.
- Existing request form is prefilled only with a server-authored title/type; no schema or migration.
- Service JSON-LD uses existing Service graph and Provider identity; service area is Iran. The copy says Isfahan and nationwide without inventing a shop address or hours.
- Page is linked from Home services, the Isfahan services page and `sitemap.xml`.
- Product search now matches saved hashtags and technical notes; queries including «آتلیه», «استودیو», «پراپ» or «عکاسی» also search titles/descriptions/tags for existing decor/prop/stand terms.

## Safety boundaries
- Must not touch: product/order/pricing/media rows, all-product tag assignments, Instagram posts/settings/credentials, Search Console, gallery/screenshot workflows, database schema/migrations, Host or production data.
- SEO keyword meta tags are not added; actual visible content, descriptive titles, internal links and user-facing product search carry the intent.
- No Business Profile/knowledge panel, indexing, ranking, sales or manufacturing-capability guarantee. The new service page phase adds H2S nominal build volume sourced from the manufacturer's [official specification page](https://us.store.bambulab.com/en/products/h2s); actual usable envelope and suitability remain project-specific.

## Verification
- Related A2W/A2V/A2U/Hero regressions: 33/33 PASS with process-scoped test settings (`DJANGO_DEBUG=1`, blank `DB_NAME`, `SECURE_SSL_REDIRECT=0`). Django check reports three existing warnings: absent optional Google OAuth, unsupported CKEditor 4 and in-memory realtime. The later six-service-page extension is tracked in `PHASE50_A2Y_SERVICE_VERTICAL_LANDINGS.md`.
- `makemigrations --check --dry-run`: no changes; touched Python compile and `git diff --check`: PASS.
- Before current implementation, live product search returned 0 for «آتلیه» and existing decor results for «دکور»; public Instagram GET returned 200 and its profile title/bio metadata.
- Broader A2U/A2W regression, migration/compile/diff checks and public post-release search smoke remain required.

## Release and next
- Current local branch: `release/phase50-a2w-service-seo-20261010`, base `1341502661deb154bdeefef49ff71d55fe2e5521`.
- Production remains exact runtime SHA `06f37f75cf01c1de3ddfeb06aafe97536f69d5b8` until any tested commit passes GitHub and dedicated 3DPrintHub Host deployment gates.
- Next exact step: run related broad regressions and static/migration checks; then review the release allowlist and proceed through the GitHub-first guarded Host workflow if gates pass. After deployment, verify the new URL/search results and request URL Inspection in owner-authenticated Search Console.
