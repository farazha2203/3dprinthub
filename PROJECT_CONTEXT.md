# PROJECT_CONTEXT — 3DPrintHub

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Epic: `Phase50 — Finance, Commerce & Admin Command Center`
Current Subphase: `50.A.1D — Sales Profiles + Hero Admin Public Media`
Status: `GITHUB CI TESTED / PRODUCTION DEPLOY NEXT`

## Operating rule
GitHub/Repository is permanent source of truth.
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI/LOCAL GATE → MANUAL QA → OWNER APPROVAL → HOST READ-ONLY VERIFY → BACKUP/DEPLOY/VERIFY`.

No permanent Production source edit. Dirty Local/Host stops for inspection. New commerce/finance work is additive and preserves mature orders, payments, inventory and Catalog history.

## Canonical paths
Windows project: `D:\projects\3DPrintHub`
Windows venv: `D:\projects\3DPrintHub\.venv`
Windows Django DB: `D:\projects\3DPrintHub\db.sqlite3`
Production project: `/home/sfkilvrs/3dprinthub`
Production venv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`
Production DB: MySQL `sfkilvrs_EmiAdmin_3dprinthub`

## Production verified baseline
Owner deployed Phase50.A.1C at commit `5c5c5e1e141fd3ff8df3c079abc55e4593feb41f`.
`store.0034_phase50_variant2_commerce` is applied; final migrate plan was empty; Home/Store/Admin/Product Admin/Imported Asset Admin/Hero Admin returned HTTP 200; public Home emitted no private imported-media references. Rollback backup exists at `/home/sfkilvrs/3dprinthub-deploy-backups/20260825-205719`.

## Existing business foundation
- StoreOrder/StoreOrderItem/StorePayment/StoreInvoice/Shipment/ReturnRequest,
- Coupon discount + VAT + packaging + shipping + order-weight calculation,
- ShippingMethod fixed/weight-rule pricing,
- StoreAddress and Iran Province/County/City reference data,
- custom service Order/Quote/Payment and immutable PaymentLedgerEntry,
- mature online payment request/callback/verify/idempotency architecture,
- filament purchasing/spools/movements,
- inventory reservation/movements,
- ProductionJob/MaterialUsage/CostEntry/BusinessFinanceDashboard,
- affiliate commission/payout/ledger,
- broad custom Admin.

## Phase50 deployed foundation
- authenticated `/admin/command-center/`,
- Product/Imported Catalog Hero actions and 5/10 random/deactivate-all,
- Product contain-fit gallery + thumbnail switch + fullscreen lightbox,
- Variant 2.0 size/build/packaging fields,
- StoreOrderItem snapshot columns,
- migration `store.0034` applied,
- imported-model safe Admin preview,
- compact mobile Hero,
- homepage SEO Admin audit,
- Windows source image dimensions.

## Phase50.A.1D implementation
### Sales Profiles
- Product selection mode: list / size / weight / build / size→build / build→size.
- ProductVariant profile name/key/default/order.
- profile key extends Variant identity so profiles can otherwise share size/material/color/build while differing in weight, print time, price inputs, packaging or shipping.
- Admin copy-profile action clones current Variant settings and creates a new profile/code without changing the source.
- Product Admin/Variant inline expose the new controls.
- Variant JSON metadata includes profile + selector + weight/time/price/shipping values.
- migration `store.0035_phase50_sales_profiles` is GitHub-only and not yet Production-applied.

### Hero Studio
Owner screenshot showed product/album cards in `/admin/website/homepageheroslide/<id>/change/` with broken images. The legacy Hero Studio endpoints still emitted `ImportedPrintAssetImage.image.url`, which is a private working-media path in Production.

Final Admin endpoint fix:
- Product browser uses Product-owned public media.
- Album rows use filename-matched Product gallery media; if unavailable, row-specific remote HTTP(S) source media is allowed.
- private `store/imported-models/...` URLs are never returned.
- existing selected image relation, SEO suggestions, transition controls and public Hero rendering are preserved.

## Verification
GitHub Actions `Phase50 Sales Profiles Hero Admin CI` run `32879712980` PASS on snapshot `405d2c1daa85828d1a0dc68210d201c85b6db7ba`: compile, Django check, migration dry-run/plan/apply and focused regressions all PASS.

## Immediate next work
1. Production read-only verify current `5c5c5e1...` baseline and MySQL `0034`.
2. Fresh backup, deploy current GitHub snapshot and apply only `store.0035` after plan inspection.
3. Manual QA Hero Studio images and Sales Profile copy/edit/default/order.
4. Build storefront profile selector + checkout snapshots.
5. Continue Shipping/Delivery → secure Store ZarinPal → Torob Product API v3 → accounting core.
