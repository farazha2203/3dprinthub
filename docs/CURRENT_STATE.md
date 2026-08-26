# CURRENT PROJECT STATE

Updated: 2026-08-26
Repository: `farazha2203/3dprinthub`
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Primary Web/Commerce Release: `Phase50.A.2B — Immutable Checkout/Profile/Shipping Snapshot`
Parallel Windows Track: `Phase49.3I.31 — Smart Link + Bulk Product AI`
Status: `WEB 50.A.2B GITHUB CI TESTED / WINDOWS 8.8.2 IMPLEMENTED, FULL WINDOWS GATE PENDING`

## Production state — terminal verified
Current Production application commit: `c283864290f9c989a9fcdf24ee8eef519560e917`.

Verified Production environment:
- root `/home/sfkilvrs/3dprinthub`,
- venv `/home/sfkilvrs/virtualenv/3dprinthub/3.12`, Python 3.12.13, Django 6.0.7,
- MySQL `sfkilvrs_EmiAdmin_3dprinthub`,
- `store.0034_phase50_variant2_commerce` applied,
- `store.0035_phase50_sales_profiles` applied,
- `store.0036_phase50_checkout_snapshot` NOT YET DEPLOYED/APPLIED,
- clean Production worktree,
- Home/Store/Admin/Product/Variant API verified HTTP/runtime healthy,
- public Home private imported-media refs = 0.

Latest verified Production rollback backup: `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-143650`.
A fresh backup is mandatory again before applying `0036`.

## Phase49.3I.31 — Windows Smart Link + Bulk Product AI — IMPLEMENTED / RELEASE GATE PENDING
Candidate identity:
- Catalog Center `8.8.2`,
- build `2026.08.26.1`,
- active branch is the same canonical development branch above,
- latest candidate source continues to advance on GitHub; exact release SHA must be re-verified immediately before Local/Windows QA.

Implemented runtime:
- Phase49.3I.29 performance base renders at most 48 Product cards per page without truncating SQLite results,
- ProductWorkspace Save/AI no longer rebuilds the global Products page on every edit; it marks the list dirty and defers the global refresh,
- mother AI settings remain authoritative: exact saved Provider + saved Provider model + secure key; no cross-provider fallback and no hidden Product model scan,
- Phase49.3I.31 validates each exact Product source URL, fetches/parses the real product page, canonicalizes source identity and converts all safe extracted product facts into one heading-structured text field,
- Product AI payload remains exactly `source_title` + one `source_description` text body; raw HTML, cookies/auth headers, credentials and unrelated price/stock/workflow state are excluded,
- the main Product AI action now performs link grounding + Persian content + SEO + selected-image alt/title/caption/keywords + existing image finalization in one workflow,
- Products Explorer has a selected-product batch AI action; each selected Product uses its own exact link, failures are isolated, and the global Products view refreshes only once at batch end,
- OpenRouter/AvalAI/Google/OpenAI all pass through the same mother active-profile boundary.

Windows release files now identify candidate `8.8.2` consistently in `app/version.py`, `launch.py`, `PACKAGE_MANIFEST.json` and `config.example.json`. The Windows release workflow now includes Phase49.3I.29 and Phase49.3I.31 regressions and launcher markers.

Verification completed so far:
- Phase31 source/test syntax and pure helper behavior were checked in an isolated local stub harness,
- exact GitHub source composition was re-read after writes.

Verification still required:
- full repository Windows unit/regression suite,
- `launch.py --verify-only`,
- one-file PyInstaller build/self-verify,
- packaged Playwright/browser smoke,
- live exact Product link QA with at least OpenRouter and AvalAI,
- owner confirmation that Product page no longer visibly refreshes on every AI/edit and batch behavior is acceptable.

GitHub Actions note: commits created through the connected GitHub integration have not automatically produced a new workflow run for the latest heads, so no PASS is claimed for 8.8.2 yet.

## Phase50.A.1H — Admin Shell Stability — PRODUCTION VERIFIED
- footer normal/static flow instead of vendor absolute positioning,
- stable Admin flex/min-height shell,
- right sidebar 290px,
- active-menu scrolling constrained to the internal sidebar,
- Velzon V2 on-demand filter/full-width tables preserved.

## Phase50.A.2A — Storefront Sales Profile Selector — PRODUCTION VERIFIED
- customer Product page exposes configured profile/size/build/weight/material/color/quality choices,
- `/store/api/variant-commerce-options/` remains authoritative,
- selected choice resolves to canonical ProductVariant ID and existing Cart/AddToCartForm,
- Production sample `shoe-holder-organiser` / Variant 1 verified through public API.

## Phase50.A.2B — Immutable Checkout/Profile/Shipping Snapshot — GITHUB CI TESTED
Implemented additively without rewriting mature `store/models.py` or the Phase6 checkout implementation.

Migration `store.0036_phase50_checkout_snapshot` adds immutable StoreOrderItem profile/selection/final-weight/shipping-weight/print-time snapshots and StoreOrder `insured_value` + `shipping_quote_snapshot`. Existing `0034` size/build/packaging/package snapshots are reused.

Runtime keeps mature Phase6 validation/coupon/inventory/address/notifications/payment authoritative, finalizes successful checkout inside an outer atomic boundary, uses `ProductVariant.effective_shipping_weight_grams`, preserves per-line package facts without inventing combined carton geometry, uses current ShippingMethod/rate rules as explicit fallback, and restores the session cart if finalization fails.

GitHub Actions `Phase50 Variant2 Gallery CI` run `32966720475` PASS on `fba0631e60bce1f6e3f622317b70c2f7f35d978f`, including migration through `0036` and snapshot immutability/integration tests. Production has not applied `0036` yet.

## Known operational incidents
- `ERR-49-052`: Product Save/AI could rebuild the entire Products gallery and thumbnails repeatedly; corrected by Phase49.3I.29 deferred global refresh + 48-card presentation paging, with Phase49.3I.31 batch performing one final refresh.
- `ERR-50-007`: Production remote fetch refspec is stale/tag-only; use live `ls-remote` + explicit branch fetch to `FETCH_HEAD` + ff-only.
- `ERR-50-010`: avoid cPanel `/dev/fd` process substitution for backup enumeration; use Python filesystem copy.
- `ERR-50-011`: JSON verifier must use `python - <args>` and `json.load`, never execute JSON as Python.

Known warnings remain CKEditor4 maintenance/security debt, `store.W026` in-memory realtime debt and MySQL conditional-constraint warnings.

## Exact next work
1. Re-verify live GitHub branch HEAD, then run the full Windows 8.8.2 Local/release gate from the canonical Windows checkout; do not accept the candidate on source changes alone.
2. If Windows tests pass, build/self-verify the one-file EXE, run frozen browser smoke and controlled exact-link AI QA with OpenRouter + AvalAI, then publish/verify immutable `catalog-center-v8.8.2` release.
3. Separately, when returning to Web Production, perform the Phase50.A.2B read-only Host/MySQL audit and fresh backup before any `store.0036` migration/deploy.
4. After 50.A.2B Production verification: Product engagement package → secure Store ZarinPal → Torob Product API v3 → accounting core.
