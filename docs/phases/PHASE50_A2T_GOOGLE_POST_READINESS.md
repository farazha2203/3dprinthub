# Phase50.A2T — Google Search publication, crawl and structured-data release

Date: 2026-10-08
Status: `PRODUCTION_DEPLOYED / PUBLIC_CRAWL_ENABLED / SEARCH_CONSOLE_SUBMISSION_PENDING`

## Owner request

Prepare 3DPrintHub for Google publication and indexing, with a verified `robots.txt`, canonical sitemap coverage, Product/Image structured data and Product variant URLs. Preserve Product/Variant/price/media truth and do not expose private customer, order, model-file or admin resources.

## Source and release lineage

- Development checkpoint: `wip/phase50-a2l-owner-qa-20260917 @ 04eaaad804722bd54a80a96434c3ae7c39a33122`.
- Verified Production baseline before release: `2b48a593ace2e9a3703fa0f52b4c3c13b2751cf9`.
- Production release branch: `release/phase50-a2t-google-indexing-20261008`.
- Production release source: `2b85a9c0d5d4a79219182bc9b986a5a81e70ed50`.
- Rollback branch: `backup/pre-phase50-a2t-google-indexing-20261008` at `2b48a593...`.
- Deployment was GitHub-first and ff-only through the dedicated authenticated 3DPrintHub reverse tunnel. No permanent Source edit occurred on Host.

## Implemented Google-facing contract

- `robots.txt` now enables public crawling with `Allow: /`, explicitly disallows admin/customer/cart/checkout/account/order paths, and advertises both current sitemaps.
- Root `/sitemap.xml` includes Home, Store, active/indexable Products, Categories and Service pages; the retired Ready Models catalog is not advertised.
- New `/sitemap-images.xml` contains only public media from active/indexable Store Products and never includes private 3D model files.
- Global SEO switch remains authoritative: when off, public Home/Store templates emit `noindex,nofollow`; after the verified Production toggle it is now on.
- Store search/filter/sort query URLs emit `noindex,follow` and canonicalize to the clean Store/category URL, avoiding crawlable faceted duplicates.
- Product schema keeps ProductGroup + real Product variants, but zero-price variants are not advertised as merchant Offers.
- Every advertised variant has a directly loadable `?variant=<variant-code>` URL and the server preselects the corresponding real Variant; canonical remains the Product group URL.
- Variant structured data includes actual Product image, description, SKU, brand, category, material, Offer price/currency/availability and ProductGroup relationship.
- Duplicate Product images are removed from JSON-LD.
- Unknown shipping cost is omitted instead of represented as free shipping.
- The legacy default return-policy claim is omitted until an explicit public merchant policy is verified.
- Obsolete WebSite SearchAction markup is omitted.
- Home uses shared Organization/WebSite schema and the configured canonical site URL instead of a separate hard-coded Organization claim.

## Local verification

Current related release regression excluding one proven stale baseline Hero assertion: `55/55 PASS`.

Focused Google/schema release tests: `22/22 PASS`.

Additional gates:
- Python compile: PASS.
- Django check: PASS with known CKEditor/Google-local/realtime warnings only.
- `makemigrations --check --dry-run`: no changes detected.
- release diff-check: PASS.
- no Django migration introduced.

A broader Hero test `website.test_phase50_mobile_hero_seo.Phase50MobileHeroContractTests.test_mobile_caption_is_compact_and_description_is_hidden` still expects static version `50.8.0`, while exact pre-change Production baseline already uses `50.10.0`. It was reproduced unchanged on detached baseline `2b48a593...`; therefore it is stale baseline debt, not an A2T regression.

## Production backup and deploy evidence

Pre-deploy rollback:
`/home/sfkilvrs/3dprinthub-deploy-backups/20261008-112619-phase50-a2t-google-indexing`

Verified before ff-only promotion:
- Git source bundle: valid.
- protected `.env` copy: checksum valid.
- MySQL backup `database-before-3i53.sql.gz`: gzip valid, SHA256 verification PASS.
- MySQL identity: `sfkilvrs_EmiAdmin_3dprinthub`.
- migration plan: 0.
- Host worktree: clean.

Deployment result:
- Host source advanced `2b48a593... -> 2b85a9c0...`.
- collectstatic completed.
- Passenger restart completed.
- post-deploy source worktree clean.

Fresh pre-index-toggle rollback:
`/home/sfkilvrs/3dprinthub-deploy-backups/20261008-112838-pre-google-indexing-toggle`

Its source bundle, protected environment copy and MySQL gzip were independently verified before changing `SEOSettings.allow_search_indexing`.

## Production public verification after crawl enable

The Production SEO toggle was changed transactionally from `False` to `True` only after the fresh rollback was verified.

Current public evidence:
- `/robots.txt`: HTTP 200; `Allow: /`; required private/transactional disallows present; no global `Disallow: /`.
- `/sitemap.xml`: HTTP 200; valid XML; 89 URLs; Home + Store present; private-path leak count 0.
- `/sitemap-images.xml`: HTTP 200; valid XML; 47 Product URLs / 96 image URLs; `X-Robots-Tag: noindex`.
- Home: HTTP 200, `index,follow`, canonical `https://3dprinthub.ir`.
- Store: HTTP 200, `index,follow`, canonical `https://3dprinthub.ir/store/`.
- filtered Store sample: HTTP 200, `noindex,follow`, canonical `https://3dprinthub.ir/store/`.
- Product sample: HTTP 200, `index,follow`, self-canonical, valid JSON-LD and ProductGroup.
- Product sample schema has no zero-price Offer, no unverified MerchantReturnPolicy and no obsolete SearchAction.
- Direct variant sample URL returned HTTP 200 and server-side selected the correct real Variant while retaining Product-group canonical.
- Host source remains clean at `2b85a9c0...`.
- Production `allow_search_indexing=True`.

## External Google gate still open

Google Search Console ownership/submission has not been asserted. The site's `google-site-verification` meta setting is currently empty; ownership may still exist through DNS, but that has not been verified from the project.

Next exact external step:
1. connect/verify the Search Console property for `https://3dprinthub.ir` or the domain property;
2. submit `https://3dprinthub.ir/sitemap.xml` (the image sitemap is already advertised from robots and can also be submitted);
3. run URL Inspection for Home, Store, one Product, and one direct variant URL;
4. request indexing for representative canonical pages if Search Console offers it;
5. record Search Console indexing/enhancement results in this phase. Submission is a discovery hint, not a guarantee of indexing.

Official implementation references reviewed for this release:
- Google robots.txt documentation.
- Google sitemap documentation and sitemap limits.
- Google canonicalization guidance.
- Google Product / Product variant structured-data documentation.
- Google robots meta / X-Robots-Tag documentation.


## 2026-10-08 — Search Console ownership preflight

Read-only ownership evidence was rechecked before attempting any Google-side action:
- Local release checkout is clean at `1974f064e0cfa15fb000f927f729d6e8c5edcd12` and exact with its GitHub release branch.
- Production remains clean at runtime Source `2b85a9c0d5d4a79219182bc9b986a5a81e70ed50`; the later GitHub commit is documentation-only and does not require runtime deployment.
- The dedicated 3DPrintHub reverse-tunnel health check passes.
- Public Home currently renders no `google-site-verification` meta tag.
- Both authoritative DNS servers (`ns869.mihanwebhost.com` and `ns870.mihanwebhost.com`) return only the existing SPF TXT record for the apex domain; no `google-site-verification` TXT record is present.
- No root-level `google*.html` ownership file exists under the verified public document root.
- A read-only search of the connected Google mailbox found no Search Console notification for `3dprinthub.ir`; this is supporting evidence only and is not treated as authoritative proof of property absence.

Conclusion: the Site is technically crawlable/indexable, but Search Console ownership/access still cannot be truthfully asserted from available authenticated tools. No Search Console property was created, no sitemap was submitted through Search Console, and no URL Inspection/request-indexing action was claimed.

Exact next external gate: connect an authenticated Google Search Console property for the domain/URL-prefix, then verify ownership, submit the root sitemap, inspect representative canonical URLs, and record coverage/enhancement results. No source or Production mutation is justified until that external evidence exists.


## 2026-10-08 — Auth path verification after continuation

The external gate was rechecked rather than blindly retried. Production does contain configured `GOOGLE_OAUTH_CLIENT_ID` / `GOOGLE_OAUTH_CLIENT_SECRET`, but repository settings prove these credentials belong to the existing Django-allauth sign-in flow and request only `profile` + `email` scopes. They are not evidence of Search Console authorization and must not be reused or treated as Search Console access without a separate Google consent/scoping flow.

No repository credential/file for Search Console was found, and no authenticated Search Console connector/session is currently available to this execution context. Therefore the predecessor gate is still genuinely unfinished; automatic successor-phase start is not permitted by the continuation rule. No Production/source/DB mutation was performed.

## 2026-10-08 — Owner reported Product snippet errors: REQ-50-039
Six public Product URLs were flagged by Google Search Console with missing offers/review/aggregateRating. All six current public pages were fetched read-only with HTTP 200 and 48–64 priced Variant Offers; Google-rendered crawl HTML for the reported timestamp was not available for direct comparison.
Implemented local ProductGroup/hasVariant cleanup and explicit fixed-price/unknown-price/review-only rich-result gates, without modifying Store business pricing, inventory, Product data or Google Auth.
Validation: 41 relevant Django tests PASS; Python compile, Django check (known warnings), no migration drift and diff-check PASS. Rollback/Production deploy pending exact GitHub release proof.
Search Console external access remains unconnected to this execution environment; the owner may have authenticated UI access as proven by the supplied Search Console report. Request Google Validate Fix only after the live six-URL smoke gate passes.

## 2026-10-08 — Product snippets REQ-50-039 Production release closure
Status: `PRODUCTION_VERIFIED / SEARCH_CONSOLE_VALIDATE_FIX_PENDING`.
- Site-runtime source exact SHA `8e9f395b93f6a31802b951a71fcabbc8171985af`; unchanged real variant pricing/checkout/media/DB.
- Verified Local 41/41; runner Bash/embedded Python checks; no schema migrations; exact GitHub target.
- Dedicated Host tunnel healthy; predeploy source bundle/environment and MySQL gzip rollback checksums PASS in `/home/sfkilvrs/3dprinthub-deploy-backups/20261008-203110-product-snippet`.
- Controlled GitHub fast-forward, collectstatic, Passenger restart and Product smoke `PRODUCT_SNIPPET_DEPLOY=PASS`; Host clean.
- All six Google-reported Product URLs independently HTTP 200, 48/64 individual variants each carrying positive IRR Offer; invalid AggregateOffer removed. No fabricated Review/Rating/Offer.
- ERR-50-043 cPanel 2GB account-level storage quota was exceeded despite 509GB free server filesystem; resolved fetch by only purging 82.2MB disposable pip cache; quota still ~98%. ERR-50-044 allowlist accounted for three previously approved documentation-only release paths, after exact read-only audit.
- No authenticated Search Console operation has been performed. Next: in owner's verified property URL Inspection Live Test, then Product snippets `Validate Fix`/request re-crawl and confirm Google re-evaluation. Independently address constrained cPanel quota under protected backup-retention policy.
