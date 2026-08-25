# PROJECT_CONTEXT — 3DPrintHub

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Epic: `Phase50 — Finance, Commerce & Admin Command Center`
Current Subphase: `50.A.1C — Admin media integrity + mobile Hero + homepage SEO + Windows image dimensions`
Status: `GITHUB CI TESTED / HOST READ-ONLY AUDIT + MANUAL QA REQUIRED`
Production: `ACTUAL HOST STATE REQUIRES RECONCILIATION BEFORE NEXT DEPLOY`

## Operating rule
GitHub/Repository is permanent source of truth.
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI/LOCAL GATE → MANUAL QA → OWNER APPROVAL → HOST READ-ONLY VERIFY → BACKUP/DEPLOY/VERIFY`.

No direct Production source edits. Dirty Local/Host stops for inspection. New finance/commerce capabilities are additive and preserve mature orders, payments, inventory and Catalog history.

## Canonical paths
Windows project: `D:\projects\3DPrintHub`
Windows venv: `D:\projects\3DPrintHub\.venv`
Windows Django DB: `D:\projects\3DPrintHub\db.sqlite3`
Production project: `/home/sfkilvrs/3dprinthub`
Production venv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`
Production DB: MySQL `sfkilvrs_EmiAdmin_3dprinthub`

## Phase49 preserved contract
Catalog/Product/Hero release is operational. Product-owned media remains the public Hero/Product media ownership path in Production; imported Catalog working-media stays private.

## Existing business foundation
- StoreOrder/StoreOrderItem/StorePayment/StoreInvoice/Shipment/ReturnRequest,
- Coupon discount + VAT + packaging + shipping + order-weight calculation,
- ShippingMethod fixed/weight-rule pricing,
- StoreAddress and Iran Province/County/City reference data,
- custom service Order/Quote/Payment and immutable PaymentLedgerEntry,
- mature online payment request/callback/verify/idempotency architecture,
- filament purchasing/spools/movements,
- inventory reservation and movements,
- ProductionJob/MaterialUsage/CostEntry/BusinessFinanceDashboard,
- affiliate commission/payout/ledger,
- broad custom Admin.

## Phase50.A.1 / A.1B baseline
- authenticated `/admin/command-center/`,
- Product and Imported Catalog add/remove Hero actions,
- Hero 5-random / 10-random / deactivate-all,
- Product contain-fit gallery + thumbnail switch + fullscreen lightbox,
- Variant 2.0 size/build profile/packaging weight/parcel dimensions,
- StoreOrderItem snapshot columns,
- migration `store.0034_phase50_variant2_commerce`,
- Variant Admin and public selector metadata endpoint.

## Phase50.A.1C implementation
Owner evidence showed imported Admin media 404s, weak imported-model data visibility, oversized mobile Hero text, unclear homepage SEO controls, missing Windows image dimensions and a Production Product Admin 500.

Implemented:
- safe ImportedPrintAsset Admin preview resolves Product-owned public gallery/main media first and only then a remote HTTP(S) source image; private imported working-media is never emitted as public preview,
- mature Phase35 `list_display/list_editable/actions/fieldsets` remain intact while readonly media/data health is added,
- imported image inline displays source pixel dimensions,
- mobile Hero caption/title/CTA are compact; very narrow phones hide description to preserve Product image visibility,
- SiteSetting Admin keeps existing `meta_title/meta_description` and adds homepage SEO length health, SERP preview and Hero Alt/title audit,
- Windows Product image cards display original `W × H px` at the final installed workspace thumbnail boundary,
- no new migration in 50.A.1C.

## Verification
Initial CI failed because the first Admin patch replaced the mature list while Phase35 still owned dependent editable/link columns. The implementation was corrected rather than retried unchanged.

Corrected `Phase50 Admin Media Mobile CI` run `32875771848` passed on code snapshot `d74683cd54b18cc0f02c3c117515e1a34bc8ec83` with:
- compile PASS,
- Django check PASS,
- migration dry-run PASS,
- SQLite migration apply PASS,
- Admin media/homepage/mobile regressions PASS,
- Windows image-dimension regression PASS.

## Production reconciliation required
Owner screenshots now show Phase50-era Admin UI on `3dprinthub.ir` although older docs said Phase50 was undeployed, and `/admin/store/product/` returns 500. Before any new deploy/migration verify exact host branch/HEAD/worktree, MySQL vendor/name, `store.0034` state and migration plan. Do not assume the 500 is migration-related until host evidence proves it.

## Immediate next work
1. Read-only Production audit and root-cause the Product Admin 500 from actual host state.
2. If safe, fresh MySQL backup, deploy approved GitHub snapshot, apply `store.0034` only if pending, collectstatic, Passenger restart and Admin/Home/Product/mobile verification.
3. After source smoke, version/rebuild Windows EXE to include image dimensions.
4. Phase50.A.2 Checkout & Delivery.
5. Phase50.A.3 secure Store ZarinPal.
6. Phase50.A.4 Torob Product API v3.
7. Phase50.B accounting core after commerce acceptance.
