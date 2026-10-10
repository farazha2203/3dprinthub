# Phase50.A2Y — Persian service verticals and catalog discovery

Date: 2026-10-10
Status: PRODUCTION_VERIFIED
Branch: `release/phase50-a2w-service-seo-20261010`
Base: `1341502661deb154bdeefef49ff71d55fe2e5521`

## Requested delta

Publish crawlable, useful Persian service pages for studio photography props, custom figures, rare automotive parts, rare motorcycle parts, rare home-appliance parts and architectural/scale maquettes. Each page must explain practical inputs, review steps and limitations, prefill the existing request form, link only matching public catalog products, and be discoverable from Home, Isfahan services and the sitemap.

## Implementation

- Five new static, canonical routes supplement the studio-props page introduced in A2X; all six are linked in service navigation and sitemap.
- Each has a unique Persian title and description, three subject-specific H2 article sections, request type/title and technical/safety boundaries.
- A page displays up to six matching products only when the Product is active, indexable and in an active Category. Match is derived from the profile's curated category section and subject terms across title, descriptions, technical notes and saved hashtags. No product is fabricated or retagged. If no actual catalog Product matches, the page says that no ready example is listed and offers the request form.
- H2S nominal build volume is rendered as 340×320×340 mm, sourced from Bambu Lab's official page. It is explicitly described as nominal, not a promise of usable dimensions, tolerance, material suitability or part performance. All pages retain preflight checks for geometry, orientation, supports, shrinkage, fit and operating environment.
- Automotive safety-critical parts, appliance electrical/gas/food-contact/high-heat components, child safety, photography structures and unsupported post-processing are not promised. Feasibility is conditional on review and agreed tests.
- Existing Store Product search continues searching persisted hashtags/technical notes and expands studio intent; no all-product keyword assignment was made.

## Instagram evidence and boundaries

The repository has a working application architecture for Buffer (default Feed + companion Story) and Direct Meta/Instagram (Graph API Feed/Carousel). Credentials are read from the Windows secure credential store. Phase A2S records a real Buffer Instagram-channel connection as PASS. This task did not inspect secret values, re-test current token validity, change account settings or publish anything. Direct Meta eligibility/permissions must be validated against the currently selected login mode/app/account; code presence alone is not current connection proof. See the official [Meta Instagram API collection](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api).

## Safety contract

- Requested delta: service information architecture, article content, search synonyms and matching product display.
- Touched surfaces: `store/phase50_service_seo.py`, Store routes/sitemap/view template/tests, Home/Isfahan cross-links and project documentation.
- Must not touch: Instagram publication/credentials/posts, Product/order/media records, Gallery/screenshot capture, image model, schema/migrations, Search Console, Host/Production.
- Regression: every route/metadata/schema/CTA, request prefill, true related-product match, inactive product exclusion, Home/Isfahan links, sitemap, existing SEO, Hero and Store schema.
- No database writes or migrations.

## Local verification

- Focused Store/A2V/A2U/Hero regression: 33/33 PASS.
- Python compile PASS; Django system check PASS with existing Google OAuth and CKEditor warnings; `makemigrations --check --dry-run` reports no changes; `git diff --check` PASS.
- Existing Django warnings: optional Google OAuth disabled, CKEditor 4 unsupported, in-memory realtime channel layer.
- No GitHub push, Host operation, public crawl of these candidate pages, Search Console action or Instagram API call has happened in this phase.

## Release sequence

Review exact diff and all release docs; run compile/check/no-migration/diff and CI; commit/push the exact tested release SHA; run the repository-owned GitHub-first Host workflow only after fresh dedicated tunnel, quota, DB identity and rollback checks; verify the six canonical pages, related product links, sitemap and public crawl. Owner-side Search Console URL inspection/request indexing remains a separate external action. No search rank is guaranteed.

## 2026-10-10 release execution

Owner authorized publication. The existing guarded A2W runner was extended narrowly for this successor: its exact Host baseline is the verified current Production SHA `06f37f75cf01c1de3ddfeb06aafe97536f69d5b8`, its allowlist admits only these A2Y phase documents in addition to the prior approved A2W files, and its public smoke now checks the two A2W pages plus all six A2X/A2Y service landings. It still requires the dedicated bridge, GitHub exact SHA/fast-forward ancestry, cPanel quota and real 48/32 MiB reserves, correct MySQL identity with empty migration plan, verified source/env/full-DB backup, no migration/dependency/settings/env delta, and post-restart smoke. The initial attempted test command named two nonexistent module paths; corrected test discovery ran the actual service and category test modules successfully. No Product/order data, Instagram, Search Console or Production has been changed in preparation.

The first GitHub-runner promotion passed quota (1805/2000 MiB), both real reserves, MySQL identity/empty plan, and source/env/full-DB rollback checks, then fast-forwarded Production from `06f37f75…` to `be22597de43dde2ba42ffff2ade491f4e26790f9`. Its post-restart smoke caught a test-only title assertion mismatch («قطعه» is singular); a corrected public smoke verified all eight sitemap-discovered pages. The follow-up exact-base runner was then pushed and deployed successfully at `33b45d494def37db00cfed79d24b60f8e43fc81b`; automated post-restart smoke PASSed all eight routes. Verified fresh rollback: `/home/sfkilvrs/3dprinthub-deploy-backups/20261010-143931-phase50-a2w-service-seo` (source/.env SHA checks, complete MySQL gzip/checksum and rollback-script checksum PASS). Host is clean, MySQL identity correct, and migration plan zero. ERR-50-055 records the initial runner bootstrap/assertion corrections. Search Console was not mutated; owner URL Inspection/request indexing remains pending and Google ranking is not guaranteed.

## Live catalog relevance audit

Read-only Production audit found 47 active/indexable products, all in the `general` category section; there are no active public products in creative, automotive, motorcycle, home-appliance or academic sections. Existing figurines are in `general`, so the custom-figure page is being widened only to `creative` + `general` to show genuine catalog examples. The other specialized pages retain the honest no-ready-example state because no verified related public catalog item exists; no unrelated Product is mislabeled and no catalog row is changed.
