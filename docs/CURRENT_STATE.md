# CURRENT PROJECT STATE

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Base Epic: `epic/phase49-unified-product-slider-sync`
Active Phase: `49.3I`
Active Hotfix: `49.3I.30 — Production Hero Product-Media Ownership`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL TEST REQUIRED`
Production Application Commit: `d27489f1c2e1d36e75fdadfa8ab24660d8bec720`

## Production State Already Verified
- branch on Host: `agent/phase49-3i18-operator-bulk-ai-rebuild`,
- application HEAD: `d27489f1c2e1d36e75fdadfa8ab24660d8bec720`,
- MySQL: `sfkilvrs_EmiAdmin_3dprinthub`,
- pre-deploy DB rollback backup retained at `/home/sfkilvrs/3dprinthub-deploy-backups/20260825-150401/mysql-before-deploy.sql.gz`,
- migrations `store.0030..0033` and `website.0020..0023` applied successfully,
- post-migration plan empty,
- Home / Store / Product HTTP 200,
- Product presentation sanitization PASS,
- final Production worktree clean.

## New Owner Evidence — Hero Image 404
The first real Catalog Site Publish proved the Product page and Product media are healthy on Production, but homepage Hero media is blank while slide text renders. Browser console shows HTTP 404 for `/media/store/imported-models/gallery/...`. Local `127.0.0.1:8000` renders the same Hero correctly.

## Verified Root Cause
Production non-DEBUG routing intentionally exposes only public Store media namespaces such as `store/products`, `store/categories` and `store/seo`. Imported catalog working images live under `store/imported-models/gallery/` and are not public. Local DEBUG serves all media and therefore masked this production-only ownership bug.

The mature Hero Studio selected `ImportedPrintAssetImage.image.url` before the already-published Product-owned media copy. The page therefore emitted an internal catalog-working media URL that Production intentionally returns 404 for.

## 49.3I.30 Implemented on GitHub
- added final Hero media ownership resolver `website/phase49_3i30_hero_media_ownership.py`,
- selected Hero image basename is mapped to the matching Product-owned `store/products/gallery/` copy,
- missing exact gallery match falls back to the Product main image,
- remote source URL is only a final fallback when no Product-owned public media exists,
- internal `/media/store/imported-models/...` is never returned by the final public Hero image resolver,
- no public-media allowlist expansion,
- no migration/schema change,
- focused regression test added at `website/test_phase49_3i30_hero_media_ownership.py`.

## Must Not Touch
Product page/media ownership, Catalog batch format, pricing/cart, Hero copy/effects/timing, SEO, Production DB schema and imported working-media security boundary remain unchanged.

## Verification Status
Code is committed to GitHub. Local automated test/visual QA for 49.3I.30 has not yet been reported, so Production has not been updated with this new hotfix.

## Exact Next Task
1. Windows clean worktree + live ff-only pull of the feature branch.
2. Run `manage.py check`, migration dry-run and `website.test_phase49_3i30_hero_media_ownership`.
3. Open Local homepage and verify the published scallop/ribbed Hero images still render.
4. After owner confirmation, deploy the exact tested GitHub HEAD to Host with no migration, restart Passenger and verify every Hero image URL is Product-owned and HTTP 200.
5. Re-run the official Catalog Site Publish/re-publish E2E and then close Phase49.3I.
