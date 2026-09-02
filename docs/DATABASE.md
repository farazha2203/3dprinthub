## 2026-09-02 — Phase49.3I.52 bidirectional Product sync database contract

Phase49.3I.52/3I.52B adds no new Django migration and no destructive Catalog SQLite migration.

The new synchronization contract reuses existing fields:
- Store `ProductCatalogProfile` pricing intelligence from the existing `store.0033` chain;
- existing Product/Profile optimistic sync revision fields;
- existing Catalog Local `server_product_id`, `server_product_revision`, `last_sync_conflict`, pricing/Profile and Slider columns;
- existing Product source identity fields.

Site-only Products pulled into Windows are represented as Local mirrors with `reference_only=1`; this is a workflow safety state, not a new table/schema.

Production evidence is unchanged:
- last verified application commit remains `c283864290f9c989a9fcdf24ee8eef519560e917`;
- last verified applied Production Store migrations remain only through `store.0035`;
- 3I.51 candidates `website.0024` and `store.0042` remain unapplied until a fresh Host read-only audit and verified backups prove the exact migration plan.

# DATABASE — 3DPrintHub

## 2026-09-02 — Phase49.3I.51 Filament registry/site-sync schema candidates

### Windows Catalog SQLite
Canonical path remains:
`D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`.

Additive local schema delta:
- `available_filament_offers.description TEXT NOT NULL DEFAULT ''`.

Registry persistence:
- Brand metadata uses existing Catalog `settings`;
- Material metadata uses existing Catalog `settings`;
- Color presets use existing Catalog `settings`;
- no destructive table rewrite is introduced.

The canonical Local gate must create and checksum a backup before the 3I.51 runtime opens the real Catalog DB.

### Django candidate migrations
New additive candidates:
- `website.0024_phase49_3i51_material_catalog_description`;
- `store.0042_phase49_3i51_filament_registry_descriptions`.

They provide:
- `Material.catalog_description`;
- persistent `FilamentBrand` registry with optional description;
- optional `MaterialColorOption.description`.

CI evidence:
- Product Admin/Bridge run `33611936196` PASS;
- `makemigrations --check --dry-run` PASS;
- isolated CI SQLite migration application PASS through `website.0024` and `store.0042`;
- Bridge v3 and Admin regressions PASS.

This is NOT Production MySQL evidence.

### Production gate
Last verified Production app commit remains:
`c283864290f9c989a9fcdf24ee8eef519560e917`.

Last verified applied Production Store migrations remain only through `store.0035`. Do not assume `0036..0042` or `website.0024` are applied.

Before any Production migration:
1. read-only verify Host root/branch/HEAD/clean worktree;
2. verify effective Django DB vendor is MySQL and exact DB name is `sfkilvrs_EmiAdmin_3dprinthub`;
3. capture actual `showmigrations store website`;
4. inspect exact `migrate --plan`;
5. verify disk and `mysqldump`;
6. create fresh source/environment/MySQL backups and verify non-empty dump/checksums;
7. stop on any unexpected migration/schema divergence.

## 2026-09-01 — Catalog SQLite paging/index stabilization (Phase49.3I.46)

Environment: Windows Catalog Center local persistent SQLite only.  
Canonical persistent DB path remains: `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`.

Additive, non-destructive Catalog indexes introduced for Qt paging/query planning:
- `ix_products_active_workflow` on Product block/workflow/id ordering;
- `ix_products_source_updated` on source/update/id ordering;
- `ix_discovered_source_status_id`;
- `ix_discovered_status_id`;
- `ix_discovered_source_status_from_id` for Listing-scoped pending queue continuation.

Query boundary changes:
- Qt Product list uses bounded `COUNT + LIMIT/OFFSET` lightweight projection;
- Crawl inventory uses bounded `COUNT + LIMIT/OFFSET` then resolves Product identities for only the current page;
- mature full Product reads remain available where the Product editor/business logic needs the complete row.

No Django migration was created. No Production MySQL schema/data was changed. No destructive Catalog table rewrite was performed.

Verification code checkpoint: `a659155da4a4a41e01e926b2ac1263a1756c24e6`; Windows Qt CI `33500317538` PASS.
Owner Local gate must back up the real Catalog SQLite before acceptance testing.


## 2026-08-31 — Qt 42B2 Catalog SQLite composition

Phase49.3I.42B2 adds **no Django migration** and does not alter Production MySQL.

The Qt kernel composes the already-mature additive Catalog SQLite schemas before presenting editors, including:
- Epic49 desktop Product commerce/Filament fields and `available_filament_offers`;
- pricing/Profile Matrix fields;
- `sales_profile_ledger_json`, `sales_profiles_json`, stage lock/manual approval fields;
- image metadata fields;
- guided/Product-local homepage slider fields.

First owner Local foreground run must use the verified persistent Catalog DB
`D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`
and create a checksum-verified backup before Qt initializes against that real database.

CI uses isolated temporary SQLite only. Production MySQL remains unchanged.


Updated: 2026-08-30

## Catalog Center local database — Phase49.3I.43–45

Canonical owner Local Catalog SQLite:
`D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`.

Phase49.3I.43/44 adds runtime-created additive acquisition metadata:
- `acquisition_http_cache` — conditional HTTP cache metadata/body cache for bounded permitted text/XML/JSON representations;
- `acquisition_attempts` — request outcome, latency, bytes and cache telemetry;
- `source_endpoint_hints` — sanitized same-site public endpoint identity plus bounded response schema/shape hash, not raw XHR/fetch payloads;
- `source_capabilities` — robots/Sitemap/structured-data capability observations;
- `acquisition_host_state` — per-source/host latency EWMA, adaptive delay and request/error counters.

It also adds local Catalog Product provenance fields:
- `source_provenance_json`;
- `acquisition_method`;
- `acquisition_quality`;
- `source_last_http_status`;
- `source_last_fetch_ms`.

Phase49.3I.45 adds one further runtime-created additive table:
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
