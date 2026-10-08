# Phase50.A2U — Public SEO crawl, category snippets and indexability

Date: 2026-10-09
Status: LOCAL_TESTED / HOST_DEPLOY_BLOCKED_BY_QUOTA
User request: continue unfinished 3DPrintHub phases and evaluate SEO strength based on evidence.

## Source of truth and scope
- Local isolated worktree: D:\projects\.worktrees\3dprinthub\product-snippet-20261008; branch fix/phase50-product-snippet-20261008, began at clean GitHub SHA 232bea9efaaa6abd5418e048db01c45de2ae3249.
- Canonical Windows Catalog WIP D:\projects\3DPrintHub intentionally left untouched.
- Live Host read-only: branch release/phase50-a2j-hero-20260915, clean runtime c4cf19504081b8ccc9ed9cbeed392d44745a24ba.
- Cpanel official StatsBar count rose to 1996/2000 MB (~99.8%, only 4 MB headroom). Fresh protected source/env/full MySQL backup is mandatory. No new Host deploy or deletion authorized while safety gate fails.

## Public technical audit (read-only)
Script: scripts/seo/phase50_live_seo_audit.py. Runs on verified Local Python environment, 3 concurrent public GET requests, no credentials or mutations.
Sitemap audit baseline:
- 89 unique public sitemap URLs, 89/89 HTTP 200, 47 Product pages, 33 category pages and 9 other pages.
- robots.txt, /sitemap.xml, /sitemap-images.xml: each HTTP 200.
- zero absent title, zero absent canonical, zero unexpected noindex among sitemap entries, zero missing H1 or image-alt attributes, and zero ProductGroup/positive IRR Offer failures found by this bounded parser.
- 25 categories with empty meta description (25/89).
- 8 separate external-* categories share one category-description string (1 duplicate-description cluster); zero duplicate-title clusters.
- 42/89 pages lack nonempty og:image (Home, Store, categories and service pages), one page lacks twitter:card (Home).
- Median HTTP server response latency in this Local sample: 660 ms (not a PageSpeed, LCP, INP or Search Console ranking metric).
- 26/33 category URLs display zero current Product cards yet were included in sitemap and emitted index,follow.
- Product titles mean length ~56 Unicode characters and descriptions ~142; content quality, backlinks, impressions, clicks and actual CWV were not measured.
- User Search Console evidence confirms homepage Product microdata six-error already corrected by REQ-50-041, but Search Console API/traffic data remains unavailable.

## Approved SEO improvement delta
- Preserve all explicit Category.meta_description and Category.og_description as editorial source of truth.
- For blank category meta, render unique name-grounded and non-promissory text instead of an empty meta tag; when only Category.description is present, prepend the real category name and truncate to bound snippets, avoiding repeated public descriptions.
- For categories with no active/indexable Product in direct or currently active child categories, keep HTTP 200, visible category UI/links, but emit noindex with existing follow policy.
- Remove empty categories from root sitemap automatically; reinclude when a real indexable Product is added. Preserve explicit Category.robots_index false, Product.robots_index false and filtered-query noindex.
- Do NOT change DB, images, Product/Variant prices, Hero, Instagram receipts, canonical IDs, category record data, customer orders or protected Host files.
- No synthetic ratings, offers, OG image asset or fabricated category description inserted into DB.

## Verification
- Focused tests: 29/29 PASS: category metadata, noindex, sitemap, existing Store product schema and Search Console readiness.
- Broad tests: 62/62 PASS including SEO, Slicebox, ProductGroup, price defaults, Variant/Profile, checkout and filament operations.
- Touched Python py_compile PASS; Django check PASS with known Google CI OAuth/CKEditor4/in-memory channel warnings.
- makemigrations --check --dry-run: No changes detected; git diff --check PASS.
- Production promotion NOT attempted (official cPanel quota 1996/2000 MB, old protected rollback retained). No production code or database changed in this phase.
- Review after deploy: crawl new root sitemap expecting 63 entries if unchanged (89 minus 26 empty categories), check all live sitemap URLs index,follow, confirm empty categories remain HTTP 200+noindex and exit sitemap, unique nonempty category descriptions, ProductGroup/Offer parity and unchanged Hero and Cart.

## Further SEO work / limitations
1. Owner-provided Google Search Console Performance + Page Indexing export for actual impressions, CTR, rankings and excluded URL evidence. Do not invent.
2. Measure LCP, INP, CLS through real Lighthouse/CrUX on mobile and desktop; HTTP response latency is not CWV.
3. Supply/select verified category-specific OG images or legitimate default brand social share image at suitable dimensions; 42 pages currently lack valid og:image. Avoid using tiny icon or unrelated Product photo.
4. Audit 47 Product editorial texts, English/Persian titles and copyright/licensing claims individually (especially source-asset descriptions); no wholesale content fabrication.
5. Complete Phase50.A2R Video/Site/Instagram duplicate-safe acceptance independently after verifying exact source and protected social receipts. Do not post without current product revision ACK checks.
6. Raise cPanel storage allocation or perform separately approved, retention-aware safe cleanup while preserving verified rollback; 4 MB remaining is unsafe for even a fresh full MySQL gzip backup + Git transfer.

Next exact gate: commit/push tested A2U source and docs from isolated branch to verified GitHub release (no Host mutation). Wait for cPanel quota ≥ documented fresh backup/deploy reserve before exact-SHA guarded Production deploy. Then re-run live public crawl and Google validation; do not prematurely mark PRODUCTION_VERIFIED.
