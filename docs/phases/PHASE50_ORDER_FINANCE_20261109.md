# 2026-11-09 Service Order Admin Finance — LOCAL TEST CANDIDATE

Status: LOCAL_TESTED (65/65 focused and website regressions PASS; Django check PASS with pre-existing warnings); one additive schema migration 0025 pending; NOT DEPLOYED.

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
- Additive Website migration 0025 stores an immutable quote agreement: material rate, quantity, material/machine costs, subtotal, discount, final price, timestamp. Draft quotes remain dynamic. There is NO migration backfill or write to production financial data yet.
- After a paid receipt, inline quote financial fields and order quantity/material become read-only in Admin; dedicated QuoteAdmin also prevents price field edits.
- PaymentAdmin direct payment-status editing disabled: existing action confirms only eligible manual receipts.

## Remaining financial risks / required next phase
- Quotes finalized under the new code use an immutable monetary snapshot; later Material catalog changes and order quantity edits no longer alter that quote's agreed price.
- Legacy finalized quotes without snapshot are rejected by new manual collection instead of silently backfilling today's rates. Production read-only audit on 2026-11-09 showed 1 order, 1 draft quote and 0 payments; recheck immediately before migration.
- Auditable credit notes, refunds and amendments remain a separate financial design; do not rewrite paid rows.
- The dynamic Quote cost formula includes labor/design/post-processing/shipping once per quote; confirm per-unit vs per-order tariff policy with owner before changing the pricing contract.
- New manual form uses an operator confirmation checkbox, not bank-side automatic validation.
- Local regression gate: 65/65 passed. Need Production HEAD 29495708 integration, migration-plan preflight, full verified MySQL/env/source backup, guarded staged rollout, and live admin UI/UAT. Do not overwrite actual order #1 or use another project's tunnel.
