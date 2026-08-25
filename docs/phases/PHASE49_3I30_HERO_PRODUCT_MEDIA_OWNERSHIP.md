# Phase49.3I.30 — Production Hero Product-Media Ownership

Updated: 2026-08-25
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Status: `IMPLEMENTED ON GITHUB / LOCAL TEST REQUIRED`
Production Application: `d27489f1c2e1d36e75fdadfa8ab24660d8bec720`
Migration: `NONE`

## Owner Evidence
After the first real Catalog Site Publish, the Product page rendered its images correctly on Production, but homepage Hero slides rendered text with a blank/dark media area. Browser console showed HTTP 404 for URLs such as `/media/store/imported-models/gallery/...`. The same Hero rendered correctly on Local `127.0.0.1:8000`.

## Verified Root Cause
Production intentionally serves only public Store media namespaces (`store/products`, `store/categories`, `store/seo`) through the non-DEBUG media route. `ImportedPrintAssetImage.image` lives under `store/imported-models/gallery/`, which is an internal catalog working-media namespace and is therefore not publicly served. Local DEBUG served all `MEDIA_URL`, hiding the bug.

The Phase49 Hero Studio preferred `selected_asset_image.image.url` over the Product-owned image copy. Thus Production emitted a valid database URL pointing at an intentionally non-public media namespace.

## Requested Delta
- keep ImportedPrintAssetImage as the editor/audit selection relation,
- never require public exposure of `store/imported-models/*`,
- resolve public Hero media to the already-published Product main/gallery image whenever possible,
- preserve selected Hero image identity by matching the filename to the Product-owned gallery copy,
- fall back to Product main image if the exact Product gallery copy is unavailable,
- only fall back to the remote source URL when no Product-owned public media exists,
- preserve Product page, pricing, SEO, slider text/effects/timing, Catalog batch format and security boundaries.

## Implementation
- added `website.phase49_3i30_hero_media_ownership`, loaded after all older Hero layers,
- final `HomepageHeroSlide.effective_image_url` now resolves the selected image to Product-owned `/media/store/products/...` media,
- internal `/media/store/imported-models/...` paths are never returned as the public Hero image,
- no public media allowlist expansion was made,
- no schema/database migration.

## Regression Contract
- selected imported gallery basename maps to the matching Product gallery basename,
- missing exact Product gallery match falls back to Product main image,
- remote source is only a last fallback when Product-owned media is absent,
- imported working-media namespace remains non-public.

## Release Gate
GitHub snapshot → Windows ff-only pull → `manage.py check` + migration dry-run + focused `website.test_phase49_3i30_hero_media_ownership` → Local homepage Hero visual QA → owner approval → Host clean-state/HEAD verification → deploy exact approved GitHub snapshot → Passenger restart → Production Home/Hero image HTTP 200 verification.
