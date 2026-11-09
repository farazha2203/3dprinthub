# 2026-11-09 Service Order Admin Finance — LOCAL TEST CANDIDATE

Status: LOCAL_TESTED (14/14 finance/admin/payment tests PASS; Django check PASS with pre-existing warnings; no migration drift); not deployed to Production.

## Requested change
The Django Website Order admin lacked an integrated manual-receipt and reconciliation workflow. Service Quote had a discount and computed paid/remaining values, but Order admin did not expose a trusted receipt form or payment history.

## Implemented in isolated clean worktree
Branch: fix/website-order-finance-20261109
Worktree: D:\projects\3DPrintHub-order-finance-20261109
Baseline: d1f4ecc9 (existing November 7 attachment hotfix).

- Admin order page: visual price/discount/paid/pending/remaining/available panel with last 15 receipts.
- Scoped manual receipt form: amount, payment kind, bank reference, note, confirmation; pending review does not count as paid.
- Transactional quote/order row lock, anti-overpayment and duplicate reference checks.
- Confirmed receipts reuse Payment.mark_paid(), creating existing accounting ledger and reviewer metadata; online gateway callbacks remain separate.
- The change does not add migrations or write to production financial data.
- After a paid receipt, inline quote financial fields and order quantity/material become read-only in Admin; dedicated QuoteAdmin also prevents price field edits.
- PaymentAdmin direct payment-status editing disabled: existing action confirms only eligible manual receipts.

## Remaining financial risks / required next phase
- Quote total currently reads live Material sale prices; formal quote-version snapshots and auditable post-payment adjustments need a schema-backed design before this can be considered accounting-grade.
- Changing live Material catalog prices could alter historical quote amounts; avoid price edits for billed orders until price snapshots are implemented.
- The dynamic Quote cost formula includes labor/design/post-processing/shipping once per quote; confirm per-unit vs per-order tariff policy with owner before changing the pricing contract.
- New manual form uses an operator confirmation checkbox, not bank-side automatic validation.
- Need full local regression, production baseline integration, verified backup, staged rollout and production UI/UAT. Do not deploy an unverified branch or overwrite live order #1.
