# Phase 50 — Store ProductVariant RMA / physical stock / proven cash refunds (2026-11-10)

Status: LOCAL_TESTED, READY FOR GUARDED DEPLOYMENT. 176/176 project-targeted regression PASS; 3 separately proven pre-existing baseline test failures, independent on original e9a branch. Last live SHA before release: e9a088cfe7fc3ebcdcde49e70e31b8f59709478e.

## What already existed (must be reused, not duplicated)
- Store ProductVariant references Product, Material, PrintQuality and optional MaterialColorOption. StoreOrderItem carries immutable name/variant/price/weight snapshots and its original ProductVariant FK.
- Store checkout reserves ProductVariant.available_quantity, and paid completion records sale movement, decrements quantity and releases reservation. Invoice, production job and StoreOrder event are already created in Store services.
- Customer ReturnRequest was present, but had no quantity; in Admin its status was directly editable, with no controlled inspection, original Variant restoration, refund financial debit or duplicate detection. Old signal reversed the entire affiliate commission on every "refunded" return, even a single partial item.

## Targeted next step
- Add request quantity for a specific sold StoreOrderItem (must match same order/customer) and prevent combined non-rejected claims from exceeding sold quantity. A partially received claim uses actual inspected quantity for future claims.
- Staff review (approved/rejected with reason), then independent physically received inspection. Record restockable_quantity only for the same inventory-tracked ProductVariant, after verifying a historical sale InventoryMovement from that order. A single immutable inspection and one linked stock movement prevent duplicate restocks. Defects with restock=0 never increase stock.
- Authorized financial operator requests a refund against an existing actually paid StorePayment; request is *not* a money transfer. Caps by confirmed receipt, returned unit snapshot price and other pending/completed refunds. Completion requires explicit external payout proof (unique number); one StoreReturnRefundLedger debit per refund; StorePayment original status, amount and invoice never rewritten.
- Customer sees RMA quantity, inspection, refund status and proven payment reference on their own StoreOrder; staff gets status-gated forms instead of a mutable status dropdown.
- Block unpaid fake processing/shipping/delivery, and forged whole-order refunded state; partial refund must NOT reverse all affiliate commission. Whole-commission reversal can only happen when every line and full paid amount were truly returned, not just one RMA.
- Finance reconciliation calculates Store gross/net/returned and audits refund ledger vs source receipt as well as inspected inventory movements. All adjustments are additive; no data deletion/backfill of old prices or traffic.

## Files / migration
- `store.models.ReturnRequest.quantity` default 1 for legacy requests (historical quantity uncertain until review), new `StoreReturnInspection`, `StoreReturnRefund`, `StoreReturnRefundLedger`.
- `store.rma_services`, `store.rma_admin`, Store admin/forms/views/services/signals, customer StoreOrder template, `store.finance_reconciliation`.
- Exactly one migration expected: `store.0043_store_variant_rma_stock_refund_audit`.
- New test module: `store.test_phase50_variant_rma`; re-run old phase6, phase7, finance recon and Store checkout/payment suites.

## Production safety gates
- Only deploy from a dedicated clean branch based on exact clean Host e9a088cf. Do not touch the large dirty canonical D:\projects\3DPrintHub tree or any live buyer/customer records for tests.
- Confirm MySQL correct identity, known original Website Order #1 draft 805000 Toman / no receipts, no pending migrations, and no unexpected prior RMA rows. Verify full source/.env/SQL gzip backup with SHA256 before migration. Enforce changed-file allowlist and exactly Store.0043 migration.
- After migration, independent in-process read-only Django GET of Store RMA admin list and customer draft Quote; project Finance reconciliation; main/store/admin public HTTP200, Host clean source exact SHA. New Store RMA tables should start empty. Do not create fake live payment, refund, stock movement or return.
- If preflight not met, abort; no automatic payout or bank API call is provided.

## Follow-on boundaries
- Real-world store returns/replacements with shipping label integrations, automatic provider refund APIs, maker-checker sign-off for large returns, warranty/country-specific tax credit-note issuance and partial affiliate commission correction are separate phases.
- The service Quote flow (customer uploads a model and requests custom work) remains distinct from StoreOrder ProductVariant sale. This phase consolidates existing Stock & Order authority rather than inventing a duplicate product catalog.

## Final QA before publication
- New RMA/Checkout/Finance focused suite 42/42 PASS; wider release regression 176/176 PASS for Store Phase6/7, Store finance reconciliation, service finance, gateway and all original Website quote/order suites.
- The old baseline test `store.test_phase39` and one `store.test_phase49_3f_pricing` test failed in both new and exact original e9a source, same 1 error and 2 failures. No pricing or checkout assertions were weakened to force a pass.
- Django `manage.py check` and `makemigrations --check --dry-run` PASS, no ungenerated schema; Store migration 0043 only. Python compile, `bash -n` and Git diff hygiene PASS.
- Production preflight through dedicated tunnel: clean source e9a088cf, MySQL `sfkilvrs_EmiAdmin_3dprinthub`, 1 StoreOrder / 1 StorePayment / 0 ReturnRequest / 0 InventoryMovement / 3798 ProductVariants; Website Order #1 draft 805000 with zero service financial movements; Store 0042 / Website 0028 last applied, no pending migrations.
- Deployment pending exact target SHA, verified full source/env/MySQL backup and read-only Host smoke.
