# DATABASE — 3DPrintHub

Updated: 2026-08-30

## Catalog Center local database — Phase49.3I.45

Canonical owner Local Catalog SQLite:
`D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`.

Phase49.3I.45 adds one runtime-created additive table:
`acquisition_discovery_observations`.

Purpose:
- source URL discovery metadata;
- source/Sitemap provenance;
- Sitemap `lastmod`;
- `changefreq`;
- Sitemap priority;
- first/last seen timestamps;
- seen count.

It does **not** contain:
- raw HTML;
- raw XHR/fetch JSON;
- cookies;
- credentials/tokens;
- Product editorial text;
- Django Store rows.

Creation uses `CREATE TABLE IF NOT EXISTS` from the Catalog runtime and is covered by Windows CI. This is not a Django migration and does not touch Production MySQL.

Before first owner Local execution of the new build:
1. close Catalog Center;
2. verify the exact Catalog SQLite path;
3. copy it to a fresh timestamped backup;
4. record SHA256;
5. only then run the 3I.45 runtime/tests.

Rollback code anchor:
`3616bf222f394b769cb2e3198164d735fca5267b`.
Rollback branch:
`backup/pre-phase49-3i45-book-driven-discovery-intelligence-20260830`.

## Production
- Engine: MySQL
- Database: `sfkilvrs_EmiAdmin_3dprinthub`
- Project root: `/home/sfkilvrs/3dprinthub`
- Python venv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`

Never assume Local/CI SQLite is identical to Production MySQL. Before every Production schema change verify effective `connection.vendor == "mysql"`, exact DB name, exact migration rows/plan, backup target and rollback HEAD.

## Last verified Production migration state
Application commit:
`c283864290f9c989a9fcdf24ee8eef519560e917`.

Applied:
- `store.0034_phase50_variant2_commerce`
- `store.0035_phase50_sales_profiles`

Not Production-applied at the last terminal verification:
- `store.0036_phase50_checkout_snapshot`
- `store.0037_phase50_professional_commerce_policy`
- `store.0038_phase50_profile_matrix`

Latest verified rollback backup:
`/home/sfkilvrs/3dprinthub-deploy-backups/20260826-143650`.

This backup predates the current schema candidate. A new backup is mandatory before any migration.

## Pending migration chain

### `0036_phase50_checkout_snapshot`
Adds immutable successful-checkout state.

StoreOrderItem:
- sales Profile name/key/label,
- Profile selection mode/value,
- final weight,
- shipping weight,
- print time.

Reuses `0034` item snapshot fields for:
- size,
- build,
- packaging weight,
- package dimensions.

StoreOrder:
- `insured_value`,
- `shipping_quote_snapshot`.

### `0037_phase50_professional_commerce_policy`
Depends on `0036`.

Product:
- `pricing_policy`,
- `sales_notice`,
- `enforce_color_stock`.

ProductVariant:
- `fixed_price_override`.

ShippingMethod:
- `service_type`,
- `delivery_scope`,
- `fee_mode`,
- `requires_address`,
- `requires_postal_code`,
- `customer_notice`.

Creates singleton-style `StorePaymentSettings`.

Data operations:
- existing fixed-price Products are backfilled to `product_fixed`,
- safe shipping presets are created only when the code does not already exist:
  - Isfahan pickup — active/free,
  - Isfahan courier — active/postpaid,
  - Post — inactive/calculated,
  - Tipax — inactive/calculated.

No official carrier API is claimed by these presets.

### `0038_phase50_profile_matrix`
Depends on `0037`.

Product:
- extends `sales_profile_selection_mode` with size↔weight and 3-level size/weight/build modes.

ProductVariant:
- `sales_profile_description`,
- `part_length_cm`,
- `part_width_cm`,
- `part_height_cm`.

StoreOrderItem:
- immutable `part_length_cm`,
- immutable `part_width_cm`,
- immutable `part_height_cm`.

Desktop Profile rows themselves remain Product-owned Catalog data until publish; during import they upsert canonical ProductVariant rows. No separate Production Profile table is introduced.

## CI verification
Runtime snapshot:
`7d0a2a1125e8f38771ba325427d1efa8b8d07da6`.

`Phase50 Variant2 + Profile Matrix CI` run `33051311828` PASS:
- Django system check PASS with known warning debt only,
- `makemigrations --check --dry-run` reports no changes,
- migration plan PASS,
- clean CI database applies `0034 → 0035 → 0036 → 0037 → 0038`,
- 15 Variant/Profile/Checkout regressions PASS,
- Profile API fixed-price contract PASS,
- saved-address checkout PASS,
- immutable Profile/part/package/shipping snapshot PASS.

This is **SQLite CI evidence**, not Production MySQL evidence.

## Phase49.3I.41 Filament Library dependency

Phase49.3I.41 adds **no new migration**.

Its new authenticated Filament Bridge endpoint reads/writes the existing Store `MaterialColorOption` fields introduced by:
- `store.0039_phase50_filament_offer_pricing`,
- `store.0040_phase50_filament_offer_operations`.

Therefore:
- Local Django verification must confirm the intended Local SQLite DB and actual 0039/0040 state before running Bridge tests;
- Production cannot expose the new endpoint safely until the Host read-only audit proves the real pending chain and a fresh MySQL backup is created;
- the last verified Production state remains only through `store.0035`; do not claim 0036..0040 applied without terminal evidence.

No historical Order/Product data rewrite is part of Phase49.3I.41.

## Production schema-change gate
1. Verify Host root, branch, HEAD and clean worktree.
2. Verify live GitHub branch SHA independently from stale Host remote-tracking refs.
3. Verify exact MySQL vendor/name from effective Django settings.
4. Run `showmigrations store` and record actual `0034..0038` rows.
5. Inspect exact `migrate --plan`; stop if the plan contains anything outside the approved pending chain.
6. Verify `mysqldump` availability and sufficient disk.
7. Create fresh source + `.env*` + full MySQL backup; verify non-empty gzip/checksum and record rollback HEAD.
8. Deploy the exact approved GitHub commit via explicit `FETCH_HEAD` and ff-only.
9. Re-run check/drift/DB identity/migration plan on deployed source.
10. Apply only verified pending `0036 → 0037 → 0038`.
11. Re-verify migration rows and runtime fields.
12. Never rewrite historical paid orders to simulate snapshots.

If the live Host shows any unexpected migration already applied, divergent schema, SQLite fallback or failed backup, STOP and inspect before writing.
