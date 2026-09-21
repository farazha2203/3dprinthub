## 2026-09-15 ? Hero 50.3.0 client-handoff Production acceptance
Current Production is exact clean `b1caeba0f20e711b29dfa9e0ff92a2f5186fb08d`. Real Chromium Home QA is HTTP 200 with 8 rendered slides and `v=50.3.0`; a desktop manual Next transition produced 7 native cuboids (`orientation=h`) and cleaned them after transition. At 390px mobile no cuboids are created and document width remains exactly 390px. The handoff Store is also intentionally empty. This supersedes the older owner-visual-review/pending-handoff language for the 50.3.0 delivery milestone.

# Phase50.A.2I — Slicebox-inspired 3D Hero

Date: 2026-09-13
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Status: `SUPERSEDED_BY_PHASE50.A.2J / HISTORICAL_PRODUCTION_VERIFIED`
Baseline: `ae8df27764b4452e2858429f3ee5759b0613e173`

> 2026-09-16: the public top Hero no longer uses the A2I optional-hook architecture. The owner requested a full engine replacement, delivered and Production-verified as `docs/phases/PHASE50_A2J_STANDALONE_SLICED_3D_HERO.md`. Keep this document as historical evidence only; do not reintroduce the A2I + mature-Phase49 public runtime stack.

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
## 2026-09-14 combined Production deploy gate
Production was freshly reverified at clean `443d1b70ecdf59e26b106d8887d56cb0e61ece8d`; Local/live GitHub A2I source is exact at `b1bbdeec2db2f3876def2fd1c61d17db01e67fb7`. `scripts/host/phase50_a2i_bridge_hero_combined_deploy.sh` is Local-tested and intentionally combines the pending ERR-49-125 Bridge public-media correction with A2I static collection. It allows no migration, dependency/settings drift or DB write; it backs up source/environment/current Hero static, ff-only promotes the live GitHub target, hashes collected A2I assets, restarts Passenger and verifies authenticated Bridge readiness/Product #15 public Product-owned WebPs plus live Home/A2I markers. Commit/push and Production execution are next.
## 2026-09-14 Production verification
GitHub-first combined deploy PASSed from `443d1b70...` to `44a7be91057c60891960fbb9d9b4f53780273c33` with verified rollback backup `/home/sfkilvrs/3dprinthub-deploy-backups/20260914-130234-phase50-a2i-bridge-hero`. Collected A2I CSS/JS and mature Hero engine hashes match source. Live Home browser QA shows five slides, exactly seven temporary 3D slices on desktop transition with cleanup, zero slices on 390px mobile and no horizontal overflow. The same acceptance also closed Product #63 strict ACK/public-media/selector/cart gate. Technical Production verification is complete; owner visual preference review can continue without blocking the safe publication contract.