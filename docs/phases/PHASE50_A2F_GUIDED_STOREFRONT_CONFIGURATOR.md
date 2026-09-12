# Phase50.A.2F — Guided Storefront Configurator

Date: 2026-09-12
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Status: `PRODUCTION_VERIFIED`

## Goal
Make Product ordering understandable without exposing the internal Variant/Profile matrix. The customer chooses four guided steps: size → color → compatible material → print quality. The application resolves only a real canonical `ProductVariant`, then the mature price/cart flow remains authoritative.

## Contract
- upstream choices alone filter the next step;
- changing an upstream choice clears invalid downstream state;
- unavailable/out-of-stock combinations never resolve;
- ambiguous four-step combinations require an explicit final canonical Variant choice;
- native Variant `<select>` remains the progressive-enhancement fallback;
- API failure leaves the mature native selector usable;
- price, weight, print time, stock and brand come from canonical Variant/API facts;
- no price, stock, material, quality, size or shipping fact is guessed client-side;
- mobile layout must not create horizontal overflow and keeps the cart action reachable.
## Implementation
- `phase50-profile-selector.js` progressively enhances the existing native selector;
- Variant API exposes the exact material/quality/color/stock facts required by the guided UI;
- unavailable native options are fail-closed in the mature `store.js` cart listener;
- guided state, canonical resolution and singleton progression are exported only for deterministic Node tests;
- responsive/focus/reduced-motion styles are project-owned in `phase50-profile-selector.css`;
- `.local-qa/` contains disposable Playwright screenshots and is ignored by Git.

## Local verification — 2026-09-12
- Node guided-state contract: 8/8 PASS;
- Django `store.test_phase50_filament_offer_operations` + `store.test_phase50_profile_matrix`: 15/15 PASS;
- Playwright real JS/CSS browser regression: PASS for desktop, 390px mobile, cart POST, native fallback, stock, ambiguity and >100 Variant batching;
- `manage.py check`: PASS with known CKEditor warning only;
- `makemigrations --check --dry-run`: `No changes detected`.

## Database / Production safety
No Django migration is introduced by 2F. Production recovery was reverified live on 2026-09-12: authenticated publish-readiness reports MySQL, Store 0036–0042 and Website 0024 applied, complete receiver schema/storage and `ready=true` with no blockers. The current Production source baseline is `e12fdaf281f7e08013e54c7cf936f8275127ab2b`; the old partial-0039 instructions are historical and must not be rerun. Promotion of 2F must use `scripts/host/phase50_a2f_storefront_production_deploy.sh`, which has no migrate command and requires an empty migration plan before and after ff-only source promotion.

## Next
The configurator commit `38458ceee351add5db4bb4e84c5f1980e86bd5b5` and canonical Windows gate are already PASS. Next: commit/push the Production-state documentation + no-migration deploy runner, verify the new live GitHub SHA, execute that exact runner from cPanel shell against its verified `e12fdaf...` baseline, then verify public Store/Product configurator, guided JS/CSS, Bridge health/readiness and final Production SHA.

## Production deploy attempt ? ERR-49-115
The first guarded Host attempt on 2026-09-12 stopped before merge with `unexpected_target_delta:PROJECT_CONTEXT.md`. Root `PROJECT_CONTEXT.md` was part of the reviewed documentation delta but missing from the runner allowlist. Production remained unchanged. The runner was corrected narrowly and local syntax/exact-delta/Node/Django gates passed; no migration is added.

## Production verification — 2026-09-12
Exact Production SHA: 7d0b3df03c3657106ebaf86d5f9123ba262495a5. Verified backup: /home/sfkilvrs/3dprinthub-deploy-backups/20260912-182234-phase50-a2f-storefront. Home/Store/Bridge/readiness/guided static assets all verified HTTP 200; final Host worktree clean; no migration executed.
