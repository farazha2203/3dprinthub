# Phase50.A2W — Service discovery and Persian conversion SEO

Date: 2026-10-10
Status: LOCAL_TESTED; GitHub/Production gates pending.

## Requested delta and surfaces
- Improve all seven existing service detail pages with distinct Persian title/description, useful project-specific requirements, realistic process and technical limitations, while preserving explicit operator-authored metadata.
- Add two crawlable service pages: design/CAD from idea or drawing; jigs/fixtures and mold-prototype feasibility.
- Link real service pages from the Home and Isfahan service landing, provide a safely prefilled link to the existing request form, add sitemap entries, and use factual `Service` structured data.
- Associate only the Instagram profile evidenced by the owner-provided screenshot. Do not fabricate reviews, opening hours, geo-coordinates, certifications, delivery promises, or service capacity.

## Must not touch / safety
- Do not touch products, orders, pricing, customer records, media/gallery, social publishing, desktop Catalog, credentials, database rows, migrations, Host env or Google Search Console.
- Existing request-form POST behavior is unchanged; GET prefill is allowlisted by known service slug. No arbitrary query text is trusted.
- No Search Console indexing or ranking guarantee. No Google Business Profile setup is claimed; Google currently lists Iran as unsupported.
- No deploy until fresh exact-SHA, dedicated tunnel, official quota + actual 48/32 MiB reserves, MySQL identity/empty-plan and integrity-checked rollback gates pass.

## Local verification
- 22 focused service/Isfahan/category/Search Console tests PASS.
- Wider attempted set: 29 tests; 28 pass and one unrelated existing Product schema assertion fails because it expects a profile min/max `AggregateOffer`. Current Product schema code deliberately omits this unsupported aggregate and remains untouched by this phase. Recorded as ERR-50-051; do not weaken schema correctness to satisfy stale assertion.
- Django check PASS with existing optional Google OAuth/CKEditor warnings; `makemigrations --check --dry-run` reports no changes; touched-source compile and `git diff --check` PASS.

## Release status
Runtime Host baseline: `dc229de53db652ffe76464431c7271e5fbc25fae` on the established Host branch. Dedicated A2W runner requires exact GitHub branch/SHA, baseline ancestry, strict changed-file allowlist, fresh verified source + protected env + full MySQL rollback, no migration, then collectstatic/restart/public smoke. No Host operation has been performed for A2W yet.

Owner-provided Search Console evidence shows `/sitemap.xml` and `/sitemap-images.xml` as Success and the homepage as indexed; it does not establish that every URL is indexed or ranked. Instagram Insights was still processing in the supplied screenshot.

Research references: [Google sitemap guidance](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap) treats sitemap submission as a discovery hint, not an indexing guarantee; [Google spam policies](https://developers.google.com/search/docs/essentials/spam-policies) warn against doorway/scaled low-value landing pages, so these pages carry distinct service instructions and honest limitations; [Google Business Profile supported countries](https://support.google.com/business/answer/6270107?hl=en-G) currently excludes Iran.

## Acceptance / next
After Local gates, push the exact commit to GitHub, verify remote SHA, and run only `scripts/host/phase50_a2w_service_seo_deploy.sh` through `project-host.ps1 -Project 3dprinthub`. Confirm fresh rollback and production public smoke. Then the owner can use the existing Search Console property to inspect/request crawling of the two new URLs. No Google Business Profile promise and no Instagram post is part of this phase.
