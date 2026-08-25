# CURRENT PROJECT STATE

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Base Epic: `epic/phase49-unified-product-slider-sync`
Current Release: `Phase50.A.1 — Admin Storefront / Hero parity`
Status: `GITHUB CI TESTED / MANUAL ADMIN QA + HOST DEPLOY PENDING`

## Windows Catalog Center release
Latest Windows application version: `8.8.1` (`BUILD_ID=2026.08.25.2`).
GitHub Release: `catalog-center-v8.8.1`.
Release asset: `3DPrintHub-CatalogCenter-v8.8.1.exe`.
Release EXE SHA256: `c32f37affcbd2c6ffacb803247daf804a490fecd7c8162bc37c2729a2197e990`.

The 8.8.1 release gate passed on Windows GitHub Actions:
- source compile,
- 92 current Phase49 regression tests,
- canonical `launch.py --verify-only`,
- PyInstaller one-file/windowed build,
- frozen `--portable-verify`,
- frozen Playwright/browser smoke,
- release manifest/SHA256 validation,
- immutable artifact upload and GitHub Release publish.

Release-recovery fixes completed before publication:
- aligned `launch.py` EXPECTED_VERSION, package manifest, example config and release tests with `APP_VERSION=8.8.1`,
- removed frozen verification's dependency on reading a physical `launch.py` source file from the PyInstaller one-file extraction bundle,
- frozen verify now imports the packaged canonical launcher and validates `EXPECTED_VERSION == APP_VERSION` plus callable launcher entrypoint.

External third-party source availability (MakerWorld/Printables/etc.) is intentionally not a CI dependency; Playwright/Chrome frozen runtime is release-tested and a final employee live-source smoke remains the operational acceptance check.

## Production baseline
Owner reports the Phase49 Production site and Hero are healthy. Previously verified Production state remains:
- project `/home/sfkilvrs/3dprinthub`,
- MySQL `sfkilvrs_EmiAdmin_3dprinthub`,
- Phase49 migrations through `store.0033` and `website.0023` applied,
- Product / Store / Home healthy,
- rollback DB backup retained at `/home/sfkilvrs/3dprinthub-deploy-backups/20260825-150401/mysql-before-deploy.sql.gz`.

No Phase50 code has been deployed to Production yet.

## Phase50.A / A.1 implemented on GitHub
The business-oriented `/admin/command-center/` now groups mature Sales, Storefront/Checkout, Treasury, Accounting/Ledgers, Purchasing and Inventory/Production surfaces with permission-aware links and operational counters.

Admin storefront parity added:
- Store Product bulk action: add selected products to homepage slider,
- Store Product bulk action: remove selected products from homepage slider,
- Imported Catalog Asset actions for the same add/remove operations,
- Homepage Hero professional quick controls: `۵ محصول رندوم`, `۱۰ محصول رندوم`, `حذف همه از اسلایدر`,
- random Hero replacement uses only active Product-backed, publicly renderable assets,
- existing operator-edited slide copy is preserved when a slide already exists,
- removal deactivates slides instead of deleting history,
- quick mutations are POST-only, CSRF-protected through Admin templates and permission protected,
- Command Center links to Product, imported Catalog assets, Hero, Coupon, ShippingMethod, PricingSetting, customer addresses and Iran Province/County/City data.

## Existing backend verified before new shipping/payment work
- coupon validation and order discount calculation already exist,
- VAT, packaging fee, shipping fee and total-weight calculations already exist in Store checkout,
- ShippingMethod already supports flat/range-by-weight pricing,
- Iran Province/County/City reference data and customer StoreAddress are already present,
- service online payment already uses server-owned amount, random callback token, exact Authority matching, database locking, server-to-server verify and idempotent ledger creation,
- Production security settings already include HTTPS redirect, HSTS, Secure cookies, SameSite, HttpOnly, nosniff and DENY framing when DEBUG is off.

## Automated verification
GitHub Actions workflow `Phase50 Admin Storefront Parity CI` PASS on code snapshot `7c8714b5715cd00900a76b99097823266251d4a2`:
- Python compile PASS,
- `manage.py check` PASS with only known warnings,
- `makemigrations --check --dry-run` => `No changes detected`,
- Phase50 Admin regression suite PASS,
- no migration/schema change.

Known warnings remain: Google credentials intentionally empty in CI, CKEditor4 maintenance/security debt, and `store.W026` in-memory realtime debt.

## Safety / Must-not-touch
- NO migration/schema change in Phase50.A.1,
- no StoreOrder/Quote/Payment semantics changed,
- no gateway/idempotency behavior changed,
- no Catalog Bridge/Product public rendering/media ownership changed,
- no destructive Hero delete operation,
- Production untouched by Phase50.

## Exact next work
1. Employee acceptance smoke on `3DPrintHub-CatalogCenter-v8.8.1.exe`: open application, verify persisted profile/credentials, fetch one known MakerWorld exact/listing URL, and execute one approved publish path.
2. Manual Admin visual/operation QA on development/staging host: Product actions, Imported Asset actions, Hero 5/10-random and deactivate-all, Command Center links, mobile/desktop layout.
3. Phase50.A.2 Checkout & Delivery: package weight/dimensions, normalized carrier quote adapter, Post/Tipax/Mahex only after current official API contracts/credentials are verified; retain current weight-rule fallback.
4. Phase50.A.3 Payment hardening/unification, then Phase50.B accounting core.
