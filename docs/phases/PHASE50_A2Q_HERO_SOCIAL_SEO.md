# Phase50.A.2Q — Hero Shadow Cache Closure + Instagram SEO v4

Status: LOCAL_TESTED / GITHUB+PRODUCTION NEXT
Date: 2026-09-20

## Requested delta
Close the owner-visible dark horizontal band under the Home Slicebox and harden the already-working Instagram Product workflow so future Product Feed/Story publications use Product-specific SEO, never free-product claims, and keep auditable Site-first links/media.

## Hero acceptance
- Current Production baseline: 36a69e76f9cd553273862ee400f9391573f3dd01.
- Fresh server HTML already uses Hero cache 50.9.0 and contains no id=shadow.
- Owner screenshot visually matches the historical Slicebox Example-4 shadow.png strip below the slider.
- Current template remains shadow-free.
- A2Q explicitly hides any legacy/cached #shadow node in CSS and removes it at runtime if stale markup survives.
- Cache key becomes 50.10.0.
- Desktop/mobile Slicebox transition, arrows/dots, SEO Product overlay and Product navigation must remain unchanged.

## Instagram SEO acceptance
- Keep Site-first Product publication and duplicate-revision prevention.
- Feed + companion Story remain the default workflow.
- Keep Product primary image first, per-image ALT, bounded relevant hashtags, UTM Product URL, nationwide shipping copy and approved Highlight target.
- Product-specific title/keywords/categories are preferred over generic tags.
- No free-product/download/free-print claim may be generated or propagated into caption, hashtag or ALT.
- Record policy version and audit facts in receipts.
- #625 revision 8 is already externally published and must not be reposted.

## Next after A2Q
Close payment/finance/admin backlog as the next Phase50 slice, then continue bounded Product -> Site -> Feed+Story workflow for new/changed revisions only.
