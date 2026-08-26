# PROJECT_CONTEXT — 3DPrintHub

Updated: 2026-08-26
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Epic: `Phase50 — Finance, Commerce & Admin Command Center`
Current Subphase: `50.A.1H Admin Shell Stability + 50.A.2A Storefront Sales Profile Selector`
Status: `GITHUB CI TESTED / HOST READ-ONLY VERIFY NEXT`

## Operating rule
GitHub/Repository is permanent source of truth.
`READ DOCS → VERIFY REAL STATE → CHECK PREVIOUS ERRORS → IMPLEMENT ON GITHUB → CI/LOCAL GATE → OWNER QA → HOST READ-ONLY VERIFY → BACKUP → DEPLOY FROM GITHUB → PRODUCTION VERIFY → UPDATE DOCS`.
No permanent Production source edits; dirty worktree stops for inspection.

## Canonical paths
Windows project `D:\projects\3DPrintHub`; Windows venv `D:\projects\3DPrintHub\.venv`.
Production root `/home/sfkilvrs/3dprinthub`; Production venv `/home/sfkilvrs/virtualenv/3dprinthub/3.12`; Production DB MySQL `sfkilvrs_EmiAdmin_3dprinthub`.

## Production evidence boundary
Last terminal-verified application HEAD recorded in docs is `bc7b97f9c63432b8105f52f61cf5cdae1369689b`. Later owner screenshots show newer Velzon V2 visuals but do not prove the current host Git HEAD, so the Host must be read-only verified before the next deploy. Last verified Production has `store.0034` and `store.0035` applied and backup `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-125848`.

## Existing commerce foundation
Product/ProductVariant/ProductCatalogProfile, StoreOrder/StoreOrderItem/StorePayment/StoreInvoice/Shipment/ReturnRequest, Coupon/VAT/packaging/shipping calculations, ShippingMethod, StoreAddress/location data, payment idempotency architecture and inventory/production remain authoritative.

## Current GitHub runtime deltas
### Admin shell stability
- footer moved from Velzon absolute positioning to normal document flow,
- stable flex/min-height shell,
- right sidebar width 290px,
- active-menu centering scrolls only internal SimpleBar/sidebar; document-level `scrollIntoView` removed,
- preserves Admin V2 filter drawer/full-width table,
- no migration.

Admin CI `32958276378` PASS on snapshot `27335832e90c35dd95bb8a686dd89d1efd46dc8f`.

### Storefront sales-profile selector
- existing Product selection mode and ProductVariant profile/size/build/weight/material/color/quality/price/package metadata reused,
- customer Product page progressively enhances native `variant-select`,
- uses `/store/api/variant-commerce-options/`,
- modern selection controls + selected price/profile/weight/time/package summary,
- canonical ProductVariant ID remains submitted to existing cart logic,
- native selector remains fallback,
- no migration.

Storefront CI `32958296546` PASS on snapshot `e3c57311c0c3980befeaf6012f3bb8fc502333bc`.

## Immediate next work
1. Host read-only audit actual HEAD/worktree/refspec/MySQL/migrations/private Velzon assets/HTTP.
2. If clean, fresh rollback backup and explicit verified `FETCH_HEAD` ff-only no-migration deploy; collectstatic + Passenger restart + Production QA.
3. Complete remaining Phase50.A.2 immutable profile/shipping snapshot and normalized delivery contract.
4. Product engagement schema package (Favorite/Save + counters + verified-buyer review policy) according to owner priority.
5. Secure Store ZarinPal → Torob → accounting core.
