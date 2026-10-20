# 3DPrintHub — 2026-10-20 Instagram Services Awareness Campaign

## Purpose and content hierarchy
- Pillar 1: what 3DPrintHub does — custom 3D printing, 3D design, reverse engineering
- Pillar 2: replacement/rare parts for home appliances, equipment and non-safety automotive uses
- Pillar 3: home decor, accessories, lamp parts, maquettes and customized designs
- Pillar 4: polymer materials — PLA/PETG/ABS/ASA/TPU chosen by application, no unconditional performance claims
- Pillar 5: ordering MakerWorld and other creator models with design/license/manufacturability review

## Assets and visual
- Five separate feed assets: post-01 through post-05, each 1080x1350 JPEG.
- Five companion Story assets: story-01 through story-05, each 1080x1920 JPEG.
- Minimal WHITE layout, five different accent colors, Noto Nastaliq Urdu for headings and IRANSans for body.
- Branded media uses authorized local 3DPrintHub images and some clearly illustrative vector diagrams. Do not claim vector diagrams or model examples are verified customer deliveries.
- SHA-256 per asset in asset-manifest.json. All ten GitHub-raw public bytes and MIME were verified before submission.

## Instagram SEO / publishing contract
- Original niche-focused Persian captions with hierarchy: search-friendly opening, examples/benefits, requirements, conversion CTA, site and topical hashtags.
- Additional educational/FAQ-style topical copy merged into each **caption** (not a published comment).
- Up to seven per-post context-specific hashtags, no irrelevant hashtag stuffing or unverified "free" service claims.
- Per-image ALT submitted using Buffer asset metadata.
- Feed posts: createPost type=post, Story posts: createPost type=story; same verified 3dprinthub_ir Buffer channel.
- Site traffic landing page: https://3dprinthub.ir/ with UTM metadata for Feed. Instagram normal caption URLs are not reliably clickable.
- Buffer rejected initial post-01 attempt with **"First comment requires a paid plan"**, and returned no post ID. Retest changed conditions: omit firstComment feature and include its informative text within the caption. No paywall bypass.
- No direct Django Production change, no canonical Product Catalog identity/receipt mutation, no paid feature activation, no automatic repost.
- Provider POST IDs + statuses and public links are recorded in the APPDATA local ledger and sanitized publication-receipts.json. Treat 'sending' as pending (not sent).

## Media branch / audit
- Branch: social-assets-buffer of farazha2203/3dprinthub
- Asset publication commit: a90d61c97e757b53fecfe7acc9631c3bf98389b1
- Source tree's unrelated dirty WIP files have not been touched.
- Before marketing upload the rollback branch was backup/pre-awareness-campaign-20261020 at 597a151d217382de482b9b702a8a3d2ca8664d0b.
- Avoid changing/removing already-shared raw GitHub files until active Buffer delivery and existing Instagram posts have completed.
- Actual Instagram post/Story sent states must come from a live Buffer read-back and not merely an accepted upload.
