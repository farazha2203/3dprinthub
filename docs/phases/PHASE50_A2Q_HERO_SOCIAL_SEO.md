# Phase50.A.2Q — Hero Shadow Cache Closure + Instagram SEO v4

Status: LOCAL_TESTED / GITHUB+SITE DEPLOY NEXT
Date: 2026-09-20

## Owner request
Finish the visible Home-slider shadow/line issue, harden Instagram Product SEO, publish the fixes, then continue remaining Phase50 payment/finance/admin work.

## Hero track
Production baseline is clean 36a69e76f9cd553273862ee400f9391573f3dd01. Current fresh Home HTML already serves Hero 50.9.0 without id=shadow, but the owner screenshot matches the retired Example-4 shadow strip. A2Q keeps current shadow-free markup and adds cache-safe CSS suppression plus runtime removal for any legacy #shadow node, then bumps Hero assets to 50.10.0.

## Instagram SEO v4 track
- Site-first/public-product-first remains mandatory.
- Existing revision duplicate prevention remains mandatory; #625 revision 8 must not be reposted.
- Product SEO title/focus keyword/category/tags feed the caption/hashtags.
- Product-specific hashtags are prioritized before generic brand tags; maximum remains 8.
- Caption always contains 3DPrintHub.ir ordering CTA, nationwide-Iran shipping and UTM Product URL.
- ALT remains per-image and descriptive.
- Any false free-print/free-download claim containing «رایگان» is removed at the social-policy boundary before caption, hashtag or ALT creation.
- Direct Instagram receipts and Buffer receipts both preserve social policy version, ALT/hashtags and Site Product evidence.

## Acceptance
Hero: local contract/browser -> GitHub release -> guarded reverse-tunnel deploy -> Production desktop/mobile screenshot/DOM/computed-style acceptance.
Instagram: policy/direct/Buffer regression -> exact GitHub SHA -> Qt VerifyOnly/relaunch. Existing #625 publication is read-only evidence; no duplicate external post.

## Next phase
Phase50.A.2R: payment/finance/admin closure, including already-implemented manual transfer activation through guarded Production backup/apply path and the remaining Store finance/admin acceptance backlog.

## A2Q social sanitizer follow-up — 2026-09-20
- Fixed the punctuation-normalization defect that could leave a literal \`\\1\` in social text after false-free cleanup.
- Extended the fail-closed social boundary to Persian \`رایگان/مجانی\` and bounded English free-download/free-print/free-shipping forms, while preserving unrelated terms such as \`Freestyle\`.
- False-free hashtag candidates are dropped as a whole instead of leaving malformed residual tags.
- Added focused Caption/hashtag/ALT/Story regression. Canonical Windows full social/Qt regression is still required before release promotion.
- Site release and Production are intentionally unchanged by this Windows/Social-only WIP commit.
