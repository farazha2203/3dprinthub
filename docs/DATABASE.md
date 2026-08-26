# DATABASE — 3DPrintHub

Updated: 2026-08-26

## Production
- Engine: MySQL
- Database: `sfkilvrs_EmiAdmin_3dprinthub`
- Project root: `/home/sfkilvrs/3dprinthub`
- Python venv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`

Never assume Local SQLite behavior is identical to Production MySQL. Before every Production schema change verify effective `connection.vendor == "mysql"`, exact DB name, migration plan, backup target and rollback HEAD.

## Current Production migration state
Terminal-verified Production application commit: `c283864290f9c989a9fcdf24ee8eef519560e917`.

Applied on Production:
- `store.0034_phase50_variant2_commerce`
- `store.0035_phase50_sales_profiles`

Not yet Production-applied:
- `store.0036_phase50_checkout_snapshot`

Latest verified rollback backup before the current pending migration: `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-143650`.
A fresh backup is required before applying `0036`.

## `store.0036_phase50_checkout_snapshot`
Status: `GITHUB CI TESTED / PRODUCTION APPLY PENDING`

Adds StoreOrderItem immutable checkout fields:
- `sales_profile_name`
- `sales_profile_key`
- `sales_profile_label`
- `sales_profile_selection_mode`
- `sales_profile_selection_value`
- `final_weight_grams`
- `shipping_weight_grams`
- `print_time_minutes`

Reuses existing `0034` StoreOrderItem fields for immutable size/build/package facts:
- `size_label`
- `build_profile`
- `packaging_weight_grams`
- `package_length_cm`
- `package_width_cm`
- `package_height_cm`

Adds StoreOrder fields:
- `insured_value`
- `shipping_quote_snapshot` JSON

No destructive alteration or historical data rewrite is part of `0036`; existing rows receive safe defaults. New successful checkouts populate the snapshots through the Phase50.A.2B runtime finalizer.

CI verification: `Phase50 Variant2 Gallery CI` run `32966720475` PASS on `fba0631e60bce1f6e3f622317b70c2f7f35d978f`, including `makemigrations --check --dry-run`, migration plan and full SQLite migration through `0036`.

## Production schema-change gate
1. Verify root/branch/HEAD/worktree.
2. Verify live GitHub target and explicit `FETCH_HEAD` path per ERR-50-007.
3. Verify exact MySQL vendor/name.
4. Inspect `showmigrations store` for `0034/0035/0036`.
5. Run `migrate store 0036_phase50_checkout_snapshot --plan` after approved source is on Host.
6. Fresh source/.env/MySQL backup must succeed and be non-empty/checksummed.
7. Apply only approved `store.0036_phase50_checkout_snapshot` if pending.
8. Verify migration row, model drift, Django check and runtime fields.
9. Do not modify historical paid order snapshots as a deployment shortcut.
