# Phase50.A.2S — Instagram/SEO Social + Finance Reconciliation

Status: SOCIAL WORKFLOW DEPLOYED / FINANCE_RECEIPT ACCEPTED / NO NEW PUBLICATION
Date: 2026-09-20
Base release: `1d602fcb221ba2e86204d2c18dbd4802df6166fc`
Branch: `wip/phase50-a2s-social-finance-20260920`

## Goal
Continue after accepted A2R without regressing Store, Hero, authoritative republish or payment flows.
First close the hardened Site-first Instagram/Buffer workflow, then reconcile Store/Website finance authorities and close receipt audit.

## Social requested delta
- Reuse the mature parallel Social implementation surgically; do not merge the old parallel branch wholesale.
- Buffer is the default provider; Direct Instagram remains fallback.
- Keep secrets in Windows Credential Store.
- Feed + companion Story are the standard Product workflow.
- Enforce Product-specific SEO policy v4, per-image ALT, UTM Product URL, nationwide shipping CTA and bounded hashtags.
- Strip unsupported free/download/free-print claims from caption, hashtags and ALT.
- Use stable Buffer-compatible Feed/Story media derivatives without changing Product canonical media.
- Preserve Site-first gating and same-ACK duplicate prevention.
- Never repost Product #625 revision 8.

## Social verification
- Final Social service/config/test files were ported from hardened commit `21a1ae27...` only.
- Kernel change is limited to `InstagramCore`; Settings change is limited to Instagram provider controls; unrelated Image/Product code from the parallel branch was not imported.
- Social focused tests: 32/32 PASS.
- Existing Qt regressions: 32/32 PASS.
- SettingsPage construction regression: 1/1 PASS.
- Python compile and diff-check PASS.
- Real Buffer credential/channel connection: PASS; service resolves to Instagram.
- Real Catalog scan: 6 public-social-ready Products; 0 policy-v4 forbidden-free violations.
- Current-ACK missing Feed/Story candidates are 628, 309, 301, 273, 303; no automatic publication was performed.
- Product #625 current ACK duplicate guard is true for both Feed and Story, so revision 8 cannot be reposted by this workflow.

## Finance / receipt audit
- Authority audit complete: Store uses StorePayment/StoreOrder -> ProductionJob; custom orders use Website Payment/PaymentLedgerEntry/Quote -> ProductionJob; finance summary remains ProductionJob/CostEntry derived.
- Added `phase50_finance_reconciliation` as a read-only integrity gate. It checks payment/order/ledger/job amount parity, manual receipt references/storage, active custom-order job coverage and finance summary metrics.
- Admin reviewer evidence is additive on existing persistence only:
  - Store: authenticated actor reaches the existing `StoreOrderEvent.created_by`.
  - Website: existing PaymentLedgerEntry metadata stores `review_source=admin_manual` and reviewer user id.
- No model/migration/new ledger and no destination value is logged.
- Production baseline audit before deploy: StorePayment=0, paid StoreOrder=0, Website Payment=0, PaymentLedgerEntry=0, ProductionJob=0, Phase30 audit OK.
- Local verification: compile PASS; focused 7/7; adjacent payment/finance 39/39; Django check PASS with known warnings; no migration drift; diff-check PASS.
- ERR-49-192 records the first pre-run secret-boundary failure and CI-only environment correction.

## Deploy gate
- Finance/receipt source pushed at `8fabbcd59e1b5526e96833238f4999fffc678aed`.
- Authenticated reverse-tunnel Production preflight PASS at clean Host `888af6b4551b2e6b1e5681aab4c3d9610735474a`, correct MySQL and empty migration plan.
- Existing Phase30 Production audit remains OK with zero payment/ledger rows.
- Dedicated `scripts/host/phase50_a2s_finance_receipt_deploy.sh` is Local Git-Bash syntax tested and fail-closed:
  - exact baseline/live target/fast-forward/delta;
  - no migration/dependency/settings/env changes;
  - masked manual-payment readiness;
  - checksum-verified source/.env/MySQL rollback before promotion;
  - post-merge compile/check/no-drift + Phase30 + Phase50 reconciliation;
  - Passenger restart + public Home/Store smoke.

## Production acceptance
- First runner attempt stopped before promotion on Host account quota; ERR-49-193 records the checksum-verified redundant-backup cleanup and exact 15,600,484-byte reclaim.
- Second runner created fresh verified rollback `20260920-180912-phase50-a2s-finance-receipt`.
- Production ff-only promoted to exact `a8baf281f2a60cb4acbf301d9db32ef12a627811`.
- Post-deploy compile/check/no-drift PASS.
- `phase30_payment_audit` = OK.
- `phase50_finance_reconciliation` = OK.
- Manual payment remains configured + active.
- Current finance authorities contain zero operational payment/ledger/job rows, so no correction write was performed.
- Public Home/Store HTTP 200; final Host worktree clean.
- Independent post-deploy read-only verification repeated SHA/DB/migration/audit/rollback checks and PASSed.

## Closure
Finance/reconciliation/receipt-audit scope is ACCEPTED. The Social workflow code is deployed in the same lineage, Buffer connection/policy/duplicate guards were already Local/real-connection verified, and this deploy intentionally did not create a new Instagram post.
