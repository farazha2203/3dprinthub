# Phase50.A.2H — Storefront Product Showcase + Price Presentation

Date: 2026-09-13
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Status: `PRODUCTION_VERIFIED / ONE CONTROLLED PRODUCT ACCEPTANCE NEXT`
Pre-phase Local/GitHub baseline: `b7fe0e5d8ea8cf8b7df0ad6b11953b92d8a98c5f`
Rollback branch: `backup/pre-phase50-a2h-storefront-showcase-polish-20260913` -> `b7fe0e5d...`
Verified A2H Production source: `443d1b70ecdf59e26b106d8887d56cb0e61ece8d`
Verified A2H Production backup: `/home/sfkilvrs/3dprinthub-deploy-backups/20260913-131347-phase50-a2h-storefront-showcase`

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
Local Home visual QA initially hit a stale SQLite schema. Effective DB was verified as `D:\projects\3DPrintHub\db.sqlite3`; checksum-identical backup was created at `D:\projects\3dprinthub-backups\phase50-a2h-local-django-20260913-122930` with SHA256 `94C1C59ABDA7215BBD4565BA1FC0D1E57C5E821A7E88E063C77806365C3DB22E`. Only already-existing pending Local migrations Website 0024 + Store 0041/0042 were applied. Post-plan is empty. Production DB was not touched by this Local catch-up.

## Local verification
- Django `check`: PASS with the known CKEditor warning only.
- `makemigrations --check --dry-run`: no changes.
- guided state machine: 8/8 PASS.
- guided Playwright browser regression: desktop/tablet/mobile, progress, keyboard, touch, cart, fallback, stock, ambiguity and >100 Variants PASS.
- `node --check` for touched JS: PASS.
- `git diff --check`: PASS.
- real Local Home browser QA: HTTP 200 on 1440/1024/390; Hero title/caption in viewport; no Hero image/copy horizontal overlap on desktop/tablet; theme toggle text/ARIA/open/Escape close PASS; mobile document width exactly 390.
- existing page-level horizontal overflow remains in unrelated mature sections on desktop/tablet and is not introduced by the A2H Hero.

## Production verification
A2H was deployed GitHub-first with the dedicated no-migration runner to exact source `443d1b70ecdf59e26b106d8887d56cb0e61ece8d` after verified Host identity/worktree/MySQL/migration/readiness gates.

Production evidence:
- verified rollback backup: `/home/sfkilvrs/3dprinthub-deploy-backups/20260913-131347-phase50-a2h-storefront-showcase`;
- ff-only source promotion from the approved GitHub target;
- no migration required; migration plan remained empty;
- `collectstatic` completed;
- Passenger restart completed;
- collected static hashes matched the approved source;
- Home, Store, authenticated Bridge/readiness and new A2H assets returned HTTP 200;
- real Production desktop/mobile browser QA PASS;
- final Production worktree clean.

## Reverse tunnel persistence verification after A2H
The shared-Host management transport was subsequently hardened with a one-minute `flock`-guarded cPanel cron watchdog and Windows OpenSSH Automatic/service-recovery policy. A deliberate kill of exact 3DPrintHub tunnel PID `2179441` was recovered automatically as PID `367104` while bridge PID `2086137` stayed alive. Windows loopback `22024` returned to LISTENING and authenticated health returned `ok=True`. `AUTO_RECONNECT=PASS`, `RECONNECT_TEST_RC=0`.

Canonical persistence documentation is under `docs/operations/reverse-tunnel-ssh/`.

## Safety
A2H introduced no Django migration file, dependency, settings, Product data, pricing formula, inventory authority, payment behavior or Production DB write. Tunnel persistence likewise changed only operations availability; it did not change application DB/data/business logic. Secrets remain outside Git/chat.

## Next exact gate
1. Keep A2H at `PRODUCTION_VERIFIED`, not `ACCEPTED`, until the real Product publication gate passes.
2. Create a fresh checksum backup of canonical Windows Catalog SQLite.
3. Select exactly one factually ready Product with current finalized SEO WebPs and valid Profile/Variants/pricing.
4. Publish only through the existing Batch 8.5 -> FTPS -> authenticated Bridge path.
5. Verify strict ACK, Product/Profile/Variant identity, public WebP media/Product page, guided selector/cart and Local Published transition.
6. Only after that one-Product gate PASSes may bounded multi-product publication begin.
