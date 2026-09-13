# Phase50.A.2H ? Storefront Product Showcase + Price Presentation

Date: 2026-09-13
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Status: `LOCAL_TESTED / COMMIT+PUSH NEXT / PRODUCTION UNCHANGED`
Pre-phase Local/GitHub baseline: `b7fe0e5d8ea8cf8b7df0ad6b11953b92d8a98c5f`
Rollback branch: `backup/pre-phase50-a2h-storefront-showcase-polish-20260913` -> `b7fe0e5d...`
Last verified Production source before A2H: `d7cf71dceca95e191a118336c7004683083278ee`

## Goal
Improve the public first-impression and buying hierarchy without changing Product/Variant/pricing authority: give Hero products a dedicated visual stage, make the selected Variant price unmistakable, and stop the first-visit theme chooser from covering the product.

## Requested delta
- Hero image and editorial copy are spatially separated on desktop/tablet and stacked safely on mobile.
- Product image receives more visual area and a restrained specialist-commerce dark stage.
- The guided configurator price block clearly labels the actual selected Variant price and keeps tax/shipping as settlement facts.
- The first-visit theme chooser remains available but is collapsed by default into an accessible 44px toggle; click opens it and Escape closes it.
- Existing Hero data, ProductVariant resolution, price/stock/weight/time authority, cart, theme persistence and server-rendered content remain unchanged.

## Touched surfaces
- `static/css/phase50-a2h-product-showcase.css`
- `templates/website/partials/hero.html`
- `static/store/css/phase50-profile-selector.css`
- `static/store/js/phase50-profile-selector.js`
- `static/css/brand-theme-preview.css`
- `static/js/theme-preview.js`
- documentation and the dedicated no-migration Host deploy runner.

## Local database QA sync
Local Home visual QA initially hit a stale SQLite schema. Effective DB was verified as `D:\\projects\\3DPrintHub\\db.sqlite3`; checksum-identical backup was created at `D:\\projects\\3dprinthub-backups\\phase50-a2h-local-django-20260913-122930` with SHA256 `94C1C59ABDA7215BBD4565BA1FC0D1E57C5E821A7E88E063C77806365C3DB22E`. Only already-existing pending Local migrations Website 0024 + Store 0041/0042 were applied. Post-plan is empty. Production DB was not touched.

## Verification
- Django `check`: PASS with the known CKEditor warning only.
- `makemigrations --check --dry-run`: no changes.
- guided state machine: 8/8 PASS.
- guided Playwright browser regression: desktop/tablet/mobile, progress, keyboard, touch, cart, fallback, stock, ambiguity and >100 Variants PASS.
- `node --check` for touched JS: PASS.
- `git diff --check`: PASS.
- real Local Home browser QA: HTTP 200 on 1440/1024/390; Hero title/caption in viewport; no Hero image/copy horizontal overlap on desktop/tablet; theme toggle text/ARIA/open/Escape close PASS; mobile document width exactly 390.
- existing page-level horizontal overflow remains in unrelated mature sections on desktop/tablet and is not introduced by the A2H Hero.

## Safety
No Django migration file, dependency, settings, Product data, pricing formula, inventory authority, payment behavior or Production DB write is introduced. Production remains on the previously verified A2G source until this exact GitHub commit is deployed through the dedicated guarded no-migration runner.

## Next exact gate
1. finalize docs + dedicated A2H Host runner;
2. syntax/contract check;
3. commit/push and verify live GitHub SHA;
4. reverse-tunnel read-only Host identity/clean-worktree/MySQL/migration/readiness verification from the actual Production source;
5. source/env/static backup -> explicit FETCH_HEAD -> ff-only deploy -> collectstatic -> Passenger restart -> public/Bridge/static verification;
6. then perform exactly one real Product Windows-to-Production acceptance before bulk publication.
