# Phase50.A.2I — Slicebox-inspired 3D Hero

Date: 2026-09-13
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Status: `LOCAL_TESTED / COMMIT+PUSH NEXT`
Baseline: `ae8df27764b4452e2858429f3ee5759b0613e173`

## Goal
Bring the visual idea of Codrops Slicebox to the existing 3DPrintHub Hero without importing its old jQuery runtime or replacing the mature Django Hero/SEO/Admin contracts.

## Requested delta
- add a desktop 3D sliced/cube transition to the existing managed Hero;
- keep server-rendered title, description, alt text and Product links unchanged;
- preserve current Hero timing, arrows, dots, keyboard, swipe and automatic rotation;
- fall back to the mature transition on mobile, reduced-motion or unsupported 3D CSS;
- add no runtime dependency, migration, Product/price/cart authority or DB write.

## Implementation
- new `static/js/phase50-a2i-slicebox-hero.js` builds seven temporary transition slices;
- new `static/css/phase50-a2i-slicebox-hero.css` provides perspective/cube faces and staggered turns;
- existing `phase49_2c-home-hero.js` calls the optional A2I hook while retaining the mature transition engine;
- `hero.html` loads the new assets after A2H presentation styles;
- mobile under 721px and `prefers-reduced-motion` use the existing non-3D behavior.
## Regression alignment
One mature Phase49.2C test still expected private `store/imported-models` Hero media. That expectation is obsolete after ERR-49-125. The test now expects the Product-owned main image fallback and asserts that imported working-media is never public.

## Local verification
- Python compile: PASS.
- Node syntax for mature Hero engine + A2I runtime: PASS.
- focused Hero/Public-Media suite: 30/30 PASS.
- Django `check`: PASS with known CKEditor warning only.
- `makemigrations --check --dry-run`: no changes.
- `migrate --plan`: no planned operations.
- `git diff --check`: PASS.
- real Playwright Home QA: HTTP 200, four real slides, one 3D overlay with seven slices during desktop transition, overlay removed after transition, zero slices on 390px mobile and document width exactly 390.

## Safety / must-not-touch
No Product data, Catalog SQLite, Production MySQL, migrations, dependency files, pricing, inventory, payment, cart authority, secrets or private media routing are changed by A2I.

## Next exact gate
Document the Local-tested state, create a rollback branch, commit/push the exact reviewed delta, then use a dedicated no-migration/static deploy path from GitHub. Production must verify collected A2I CSS/JS, Home Hero desktop transition/mobile fallback and the still-required Product #63 Bridge/cart/strict-ACK gate before A2G/A2H/A2I can be accepted.