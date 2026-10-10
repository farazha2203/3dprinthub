# Phase50.A2V — Persian SEO and Isfahan service landing

Date: 2026-10-10
Status: PRODUCTION_VERIFIED for website runtime; Google indexing and carrier integration remain pending

## Lineage and scope
- Isolated Windows worktree: `D:\projects\.worktrees\3dprinthub\isfahan-seo-release-20261010`.
- Release branch: `release/phase50-a2v-isfahan-seo-20261010`.
- Exact verified Production baseline: `0277018726cf02e565ba83eb724cfbf8acc523fb`, Host branch `release/phase50-a2j-hero-20260915`.
- Canonical dirty Windows WIP and other release worktrees were preserved and not merged.
- Requested delta: stronger factual Persian page metadata, OG/Twitter tags, accurate Organization/WebSite identity, Persian fallback titles/descriptions for three English-slug categories, and an indexable Isfahan 3D-printing service page linked from Home and sitemap.
- Must not touch: Products/orders/prices/media, desktop Catalog/gallery/social workflows, schema migrations, credentials, Google Search Console ownership, fabricated business address/hours/claims, or carrier API/rates.

## Local verification
- Focused SEO/category/Search Console/store regressions: 39/39 PASS.
- New guarded deploy-runner contract tests: 4/4 PASS.
- `manage.py check`: PASS with known optional Google OAuth/CKEditor/realtime warnings.
- `makemigrations --check --dry-run`: no changes.
- Python compile, Bash syntax and `git diff --check`: PASS.
- Known unrelated baseline test: mobile Hero test has a stale expected Slicebox version (`50.8.0` versus unchanged baseline `50.10.0`); it is excluded and not modified.

## Release contract
The deploy runner is restricted to the exact baseline and release branch, checks cPanel quota and real writable reserve, requires an exact GitHub SHA, no migrations/settings/dependency changes, matching MySQL identity and an empty migration plan, then takes checksum-verifiable source, protected `.env`, and full MySQL rollback backups before fast-forward promotion. It records a guarded source rollback script adjacent to the verified backup. It runs Django checks, collectstatic, Passenger restart and the public sitemap/page smoke.

## Acceptance and honest limitations
- Production acceptance requires exact Host SHA/clean status, `/robots.txt`, every root-sitemap URL returning HTTP 200 with unique title/description/canonical and indexable robots, and the Isfahan landing's Persian metadata/City+Service schema/Home link.
- A successful website deploy only makes pages crawlable. Google indexing, ranking, rich-result display and Business Profile/knowledge panel are not guaranteed by source changes. Search Console ownership, sitemap submission, URL Inspection and re-crawl confirmation remain owner-authenticated external steps.
- Iran Post carrier API/contract, live credentials, tariff and approved internal fallback price are not present in this release evidence. No live carrier quote/label/dispatch is claimed or activated; shipment fee must remain factual and nonzero only when backed by an approved rate.

## Next
Runtime commit `dc229de53db652ffe76464431c7271e5fbc25fae` is on GitHub and live on Host branch `release/phase50-a2j-hero-20260915`; Host worktree is clean. Fresh cPanel StatsBar was 1789/2000 MB; real 48MiB and 32MiB reserves passed. Verified rollback root: `/home/sfkilvrs/3dprinthub-deploy-backups/20261010-113529-phase50-a2v-isfahan-seo` (source files, protected `.env`, full MySQL gzip, guarded rollback script all checksum-verified; DB gzip valid; no migrations). Host-side all-URL smoke hit a transient Python HTTPS read timeout without returning a URL; independent rerun from the Windows workstation passed all 64/64 sitemap pages, unique metadata, Isfahan schema/canonical and Home link. Host read-only recheck passed exact runtime SHA/clean status and Home, Isfahan landing, robots and sitemap HTTP 200. A current Google web search returned no indexed result for the domain; Search Console owner verification/submission and Google re-crawl remain pending, and indexing/ranking is not guaranteed. Next: owner-authenticated Search Console submit `/sitemap.xml` and inspect/request indexing. Iran Post contract/tariff/API remains a separate unimplemented phase.

Owner evidence update 2026-10-10: later screenshots show the Search Console property `3dprinthub.ir`, submitted `/sitemap.xml` and `/sitemap-images.xml` both reporting Success, and homepage URL Inspection reporting indexed. This supersedes the earlier “property/sitemap submission pending” note above; it does not prove every URL is indexed. A2W's two new service URLs still need owner URL Inspection/request crawling. Instagram Insights for `@3dprinthub_ir` showed processing, not finalized metrics.
