# CURRENT PROJECT STATE

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Base Epic: `epic/phase49-unified-product-slider-sync`
Current Release: `Phase50.A.1B — Product Gallery + Variant 2.0 foundation`
Status: `GITHUB CI TESTED / MANUAL QA + HOST DEPLOY PENDING`

## Windows Catalog Center release
Latest Windows application version: `8.8.1` (`BUILD_ID=2026.08.25.2`).
GitHub Release: `catalog-center-v8.8.1`.
Release asset: `3DPrintHub-CatalogCenter-v8.8.1.exe`.
Release EXE SHA256: `c32f37affcbd2c6ffacb803247daf804a490fecd7c8162bc37c2729a2197e990`.

The 8.8.1 release gate passed on Windows GitHub Actions with source compile, 92 current Phase49 regressions, canonical launcher verification, PyInstaller one-file/windowed build, frozen self-verification, frozen browser smoke and release SHA/manifest validation.
External third-party availability remains an operational smoke, not a CI dependency.

## Production baseline
Owner reports the Phase49 Production site and Hero are healthy. Previously verified Production state remains:
- project `/home/sfkilvrs/3dprinthub`,
- MySQL `sfkilvrs_EmiAdmin_3dprinthub`,
- Phase49 migrations through `store.0033` and `website.0023` applied,
- Product / Store / Home healthy,
- rollback DB backup retained at `/home/sfkilvrs/3dprinthub-deploy-backups/20260825-150401/mysql-before-deploy.sql.gz`.

No Phase50 migration/code from the current development branch has been deployed to Production yet.

## Phase50.A.1 Admin storefront parity
Already GitHub CI tested:
- `/admin/command-center/`,
- Product and imported Catalog add/remove Hero actions,
- Hero 5-random / 10-random / deactivate-all,
- Coupon, ShippingMethod, PricingSetting, StoreAddress and Iran location data surfaced in Admin,
- permission/POST/CSRF guarded mutations.

## Phase50.A.1B implemented and CI tested
Owner requested a product-page gallery upgrade and real sellable variants such as 20/24/26/28/30 cm with hollow/standard/solid weight profiles before shipping/payment/Torob work.

Implemented:
- product detail main image is now a contain-fit viewer instead of forced crop,
- clicking a thumbnail swaps it into the main viewer without page reload,
- clicking/keyboard-activating the main viewer opens a full-screen lightbox,
- lightbox supports close, previous/next, Escape and arrow keys,
- Variant 2.0 runtime/schema fields: `size_label`, `build_profile`, packaging weight and parcel L/W/H,
- StoreOrderItem snapshot columns prepared for size/build/packaging history,
- ProductVariant unique identity expanded from material/quality/color to include size/build profile,
- Admin exposes size/build/packaging dimensions on ProductVariant and Product variant inlines,
- safe public `/store/api/variant-commerce-options/` metadata endpoint lets the existing product selector show size/build/shipping metadata without rewriting the mature product template,
- effective shipping-weight helper prefers an explicit shipping weight and otherwise returns product/final weight + packaging weight.

Migration:
- new `store.0034_phase50_variant2_commerce` exists,
- it has NOT been applied to Production,
- Production deploy therefore requires exact MySQL verification, migration plan and a fresh successful DB backup.

## Automated verification
GitHub Actions `Phase50 Variant2 Gallery CI` run `32872549545` PASS on code snapshot `8e3c151159424437157d3ef6861881be08b1aea8`:
- touched Python compile PASS,
- `manage.py check` PASS,
- `makemigrations --check --dry-run` PASS,
- migration plan PASS,
- migrations applied successfully in CI SQLite,
- focused Variant 2.0 / Admin / endpoint / gallery contract regressions PASS.

Known warnings remain: Google credentials intentionally empty in CI, CKEditor4 maintenance/security debt, and `store.W026` in-memory realtime debt.

## Safety / Must-not-touch
- no direct Production source edit,
- no Production migration yet,
- no historical order/payment/ledger deletion,
- no Catalog/Bridge/Product media ownership change,
- no gateway behavior change yet,
- no guessed Post/Tipax/Mahex endpoint introduced.

## Exact next work
1. Manual visual/operation QA of Product gallery + Variant Admin on the approved test environment.
2. Phase50.A.2 Checkout & Delivery: persist Variant 2.0 size/build/packaging snapshots during checkout, use effective shipping weight, add normalized carrier quote snapshots and Admin provider/fallback settings.
3. Verify current official Post/Tipax/Mahex API contracts/credentials before enabling live adapters.
4. Phase50.A.3 Store ZarinPal integration using the mature secure service-payment request/callback/verify/idempotency engine.
5. Phase50.A.4 Torob Product API v3 / variant mapping / price-stock-image quality contract.
6. After commerce acceptance, continue Phase50.B accounting core.
