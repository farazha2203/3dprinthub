# Phase50.A.2R — Payment / Finance / Admin Closure

Status: WIP SOURCE IMPLEMENTED / CANONICAL LOCAL TEST REQUIRED  
Date: 2026-09-20  
Base Site release: \`65d42e40979830b306e92457093aefe068086f66\`  
WIP branch: \`wip/phase50-a2r-payment-finance-admin-20260920\`

## Goal
Close the already-built payment/finance/admin foundations without creating a second payment or accounting authority.

## Existing authorities preserved
- \`StorePaymentSettings\` from Store migration 0037 is the manual-transfer singleton.
- Store checkout/manual receipt flow remains authoritative for Store orders.
- Website Quote/Payment/PaymentLedgerEntry remains authoritative for service quotes.
- ZarinPal v4 gateway implementation and Phase30 payment audit remain the online-payment foundation.
- BusinessFinanceDashboard, ProductionJob, CostEntry, inventory and finance audit remain the operational finance authority.

## A2R slice 1 — secure manual-payment operations
- Remove real bank/card identity from repository-owned bootstrap code/tests.
- Read operator values only from \`STORE_PAYMENT_*\` environment variables or the existing Admin singleton.
- Keep dry-run as default; DB write requires explicit \`--apply\`.
- Activation/deactivation is explicit and mutually exclusive.
- Never print card/Sheba/account values in command output.
- Fail closed if activation lacks account holder plus at least one payment destination.
- Put \`StorePaymentSettings\` in the Finance Admin group instead of the unassigned/advanced bucket.
- No migration.

## Security note
Historical Git commits may still contain previously committed payment destination data. A2R removes those values from current source/tests but does not rewrite Git history automatically. Any history rewrite or payment-destination rotation is a separate owner-approved security operation.

## Acceptance gate
1. Canonical Windows Local pulls exact WIP SHA.
2. Python compile + Django check.
3. No model drift and empty migration plan.
4. Focused manual-payment tests PASS.
5. Existing checkout/receipt/operator-notification regressions PASS.
6. Phase30 payment audit tests PASS.
7. Finance/Admin navigation smoke PASS.
8. Commit/push tested candidate to release only after all gates.
9. Production read-only verify exact Host/DB/migrations.
10. Fresh verified MySQL/source/env rollback backup before any settings write.
11. Apply manual-payment settings with secure environment/Admin path; read back only masked/configured-state evidence.
12. Browser checkout + receipt upload + Admin review smoke.
13. Online gateway remains disabled unless merchant credential/configuration is separately verified.

## Next slices
- ZarinPal configuration/audit UI with no secret display.
- Reconciliation between StorePayment, Website PaymentLedgerEntry and finance dashboard summaries.
- Admin review/audit trail for manual receipts.
- Final Production payment/finance/admin acceptance and documentation closure.

## Legacy deploy compatibility
The existing A2L guarded deploy runner performs both a source grep and runtime grep for \`A2L_MANUAL_PAYMENT_DRY_RUN=PASS\`. A2R intentionally preserves that dry-run marker while also emitting the new A2R marker. This keeps the mature fail-closed runner compatible while configuration storage/logging is hardened.

## A2R slice 2 — payment readiness in Command Center
- Add a read-only readiness panel to the existing business Command Center.
- Show only non-secret state: online gateway ready/enabled, provider, merchant-configured boolean, currency, sandbox boolean, manual-transfer configured/active.
- Never render Merchant ID, card number, Sheba or account number.
- Add the manual-transfer singleton to the Treasury links for direct operator access.
- Reuse \`payment_gateway_status()\`; no second gateway-health authority is introduced.
- Add secret-safety/status regression and include the Command Center test in A2R CI.
