# PROJECT_CONTEXT — 3DPrintHub

Updated: 2026-08-26
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Epic: `Phase50 — Finance, Commerce & Admin Command Center`
Current Subphase: `50.A.2 Checkout & Delivery`
Status: `50.A.1H + 50.A.2A PRODUCTION_VERIFIED / OWNER VISUAL QA NEXT / 50.A.2B NEXT`

## Operating rule
GitHub/Repository is permanent source of truth.
`READ DOCS → VERIFY REAL STATE → CHECK PREVIOUS ERRORS → IMPLEMENT ON GITHUB → CI/LOCAL GATE → OWNER QA → HOST READ-ONLY VERIFY → BACKUP → DEPLOY FROM GITHUB → PRODUCTION VERIFY → UPDATE DOCS`.
No permanent Production source edits; dirty worktree stops for inspection.

## Canonical paths
Windows project `D:\projects\3DPrintHub`; Windows venv `D:\projects\3DPrintHub\.venv`.
Production root `/home/sfkilvrs/3dprinthub`; Production venv `/home/sfkilvrs/virtualenv/3dprinthub/3.12`; Production DB MySQL `sfkilvrs_EmiAdmin_3dprinthub`.

## Current Production baseline
Application commit: `c283864290f9c989a9fcdf24ee8eef519560e917`.
Fresh rollback backup: `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-143650`.
Verified:
- Python 3.12.13 / Django 6.0.7,
- MySQL `sfkilvrs_EmiAdmin_3dprinthub`,
- `store.0034` and `store.0035` applied,
- migration drift NONE / migration plan empty / no migration executed,
- clean Production worktree,
- Home/Store/Admin/Product/new static HTTP 200,
- Product selector HTML/native fallback/API PASS,
- public Home private imported-media refs 0.

## Existing commerce foundation
Product/ProductVariant/ProductCatalogProfile, StoreOrder/StoreOrderItem/StorePayment/StoreInvoice/Shipment/ReturnRequest, Coupon/VAT/packaging/shipping calculations, ShippingMethod, StoreAddress/location data, payment idempotency architecture and inventory/production remain authoritative.

## Production-verified Admin shell stability
- footer normal/static flow instead of Velzon absolute positioning,
- stable flex/min-height shell,
- right sidebar 290px,
- active-menu centering scrolls only internal SimpleBar/sidebar; document-level `scrollIntoView` removed,
- Velzon V2 filter drawer/full-width table preserved,
- Admin CI `32958276378` PASS on `27335832e90c35dd95bb8a686dd89d1efd46dc8f`,
- browser visual acceptance remains owner QA.

## Production-verified Storefront sales-profile selector
- existing Product selection mode and ProductVariant profile/size/build/weight/material/color/quality/price/package metadata reused,
- Product page progressively enhances native `variant-select`,
- uses `/store/api/variant-commerce-options/`,
- modern selection controls + selected price/profile/weight/time/package summary,
- canonical ProductVariant ID remains submitted to existing cart logic,
- native selector remains fallback,
- no migration,
- Storefront CI `32958296546` PASS on `e3c57311c0c3980befeaf6012f3bb8fc502333bc`,
- Production Product/Variant API smoke PASS.

## Production deployment constraints learned
- Host remote-tracking branch is stale because `remote.origin.fetch` tracks only tag `v0.33.0`; explicit branch fetch to `FETCH_HEAD` is canonical (`ERR-50-007`).
- cPanel deployment scripts must avoid `/dev/fd` process substitution; use Python/portable file handling (`ERR-50-010`).
- JSON/API verifier payloads must be parsed as data through `python -` + `json.load`, never executed as Python source (`ERR-50-011`).

## Immediate next work
1. Owner browser QA: footer refresh stability, no whole-page menu jump, 290px sidebar readability, Product profile/size/weight/color/price interaction and price synchronization.
2. Continue 50.A.2B immutable profile/customer-choice snapshot and normalized shipping/delivery contract.
3. Product engagement schema package: Favorite/Save + counters + verified-buyer review policy.
4. Secure Store ZarinPal → Torob → accounting core.
