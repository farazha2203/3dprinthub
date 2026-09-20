# Phase50.A.2S — Instagram/SEO Social + Finance Reconciliation

Status: SOCIAL LOCAL_TESTED / REAL BUFFER CONNECTION VERIFIED / NO NEW PUBLICATION
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

## Finance next
- Verify exact StorePayment, Website Payment/PaymentLedgerEntry and finance-dashboard authorities.
- Add read-only reconciliation report first; no corrective ledger writes until discrepancies are classified.
- Audit manual receipt lifecycle and Admin review evidence without exposing payment destinations.
- Close with Local tests -> GitHub -> Production read-only verification; deploy only if runtime code requires it.
