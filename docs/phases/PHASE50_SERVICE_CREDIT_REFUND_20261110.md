# 2026-11-10 — Service Order credit notes, refunds and audit-safe money history

Status: **LOCAL_TESTED**; final combined regression **129/129 PASS**, including original Website financial and Store reconciliation suites. Python compile, Bash syntax, Django check and migration drift checks PASS. Production publish pending.

## Scope and finance contract
The existing Service Order/Quote/Payment/Store shipping workflow is live at SHA `b5687b8120ee8ec3cfe7ad68aa04a8c531cf1c95` and Website migration 0027. Requested next step is accurate post-acceptance price reductions and manual refunds without rewriting original confirmed payment rows or previously snapshotted quote prices. The staff may issue a uniquely referenced, immutable **credit note** reducing the collectible amount; that is not a refund or bank action. If previous receipts exceed the adjusted amount, finance may open a refund **request** attached to one genuine settled receipt, reserving only the applicable overpayment. Separate **confirmation of actual external payout** with a unique receipt/reference and responsible operator creates one immutable debit in `PaymentLedgerEntry`. The website does not initiate a bank refund, POS reversal, cash distribution, or provider API request.

The customer quote page shows the immutable original price, credit notes, adjusted due, gross money received, actually returned amount and net balance; staff admin shows the corresponding breakdown and links to issue credit, request refund and confirm/cancel it. Existing online gateway is still server-verified and never manually impersonated. Cash/POS/card-to-card payments remain independent audited entries.

## Core invariants
- Immutable quote snapshot `pricing_snapshot_total` never changes after sent/accepted; `ServiceCreditNote` sums into `quote.effective_total_price = max(original - credits, 0)`, no history rewrite.
- `quote.gross_paid_amount` still sums all verified Payment rows; `quote.refunded_amount` comes only from `PaymentLedgerEntry(entry_type=refund,direction=debit)`; net `paid_amount` is gross minus debits.
- Refund requests **never** subtract money or issue bank instructions. They reserve eligible excess only. Completion needs explicit confirmation of external payment and proof, and is idempotent on `service-refund:{id}`; payout proof must be unique. Cancelled/completed refunds cannot be edited or deleted.
- Lock `Quote` before processing credit issuance, requesting/completing refunds, and manually or gateway verifying payments to prevent racing payments that exceed the adjusted due.
- A credit cannot be issued while a gateway attempt or manual receipt remains pending; no later bank callback may secretly overcharge after a note is issued.
- Each refund references a real already-`paid` Payment; total confirmed+reserved cannot exceed this source payment and cannot exceed current overpayment. Original Payment and existing credit ledger records are never reclassified as refunded or overwritten.
- Status `delivered` is still gated on the positive, *adjusted* due being fully settled. Full commercial credit cannot fake a paid delivery. Reconciliation checks credit notes, debit ledger correlations, overrefund and mismatch.
- Record only confirmed real-world receipts. Never use user data to simulate deposits/refunds; tests create isolated database rows only.

## New code and schema
- New `website.ServiceCreditNote`, `website.ServiceRefund` models and additive `website.migrations.0028_service_credit_refund_ledger`.
- New `website.service_adjustments` quote-first transactional business layer and `website.service_adjustment_admin` authenticated operator workflows.
- Updated Quote net/gross/excess/adjusted-due properties, payment settlement and service delivery guards, admin panels and customer quote financial history.
- `store.finance_reconciliation` audits credits/refunds and accepts finance-verified, operator-recorded bank receipts with audited reviewer instead of requiring a customer receipt photo for office bank bookkeeping.
- Hardened existing ledger rows against edits or instance-level deletes; completed payouts have unique evidence and immutable provenance.
- Planned guarded runner `scripts/host/phase50_service_credit_refund_deploy.sh` with exact SHA and allowlist, full source/.env/MySQL backup SHA256/gzip, one expected Website 0028 migration and independent read-only Host/UI sanity checks.

## Deployment boundary / safety
Production must remain on its exact clean old SHA until regression and backup gates pass. Refuse deployment when pending migrations, dirty source, wrong branch, DB identity mismatch or unexpected financial counts are detected. Current baseline to verify: one Order #1 with draft 4 pieces, `per_piece`, 805000 Toman; 0 Payment, 0 ledger, 0 delivery; 0027 applied. No real money event may be created during smoke tests. Rollback path is a fresh backed-up full database and source, not modifying paid rows in place.

## Follow-up scope
External automatic bank/provider refunds, 2-person financial approvals, customer dispute document exchange, product RMA inventory restocking, StoreOrder credits, site-wide ledger finance reports and BI should be separate milestones. These finance controls apply to service Quote/Payment, not all StoreOrder return and subscription cases.
