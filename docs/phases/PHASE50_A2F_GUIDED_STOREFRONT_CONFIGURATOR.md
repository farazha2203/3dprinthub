# Phase50.A.2F — Guided Storefront Configurator

Date: 2026-09-12
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Status: `LOCAL IMPLEMENTATION + BROWSER/DJANGO TESTS PASS / GITHUB COMMIT NEXT / PRODUCTION BLOCKED BY 3I.53G RECOVERY`

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
No Django migration is introduced by 2F. Local database migration state remains intentionally unchanged. Production is not eligible for a generic pull/deploy: documented 3I.53G partial MySQL recovery must be read-only reverified first and completed with its guarded recovery path before widening deployment.

## Next
Commit/push the tested Local delta, then run the canonical Windows Catalog Center Local gate on the clean exact GitHub HEAD. Host work begins only after that gate and a fresh read-only Production reality audit.