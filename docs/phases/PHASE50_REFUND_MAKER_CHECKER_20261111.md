# 2026-11-11 — Service + Store refunds: independent maker/checker and verified payout

State: **LOCAL_TESTED**, 188/188 final integration regression PASS, release not yet deployed. Previous live Host SHA: `0ae8d7851b803ddc8ab75be3adf35ac2a2d76a5a` / Website.0028 + Store.0043.

## Why this is needed
The previous site permitted the same finance staff member to request and then finalize a refund, despite recording external bank receipts. This phase adds an independent authorization barrier on both Custom Service Quote refunds and sold ProductVariant Store RMA refunds. It **never** directly sends a bank transfer or changes an earlier paid receipt, quote snapshot, invoice or quantity.

## Audited refund state machine
1. **requested**: an authenticated requester with dedicated add permission submits amount, evidence, original real paid receipt and method. All reservation/overpayment limits still apply, but no credit or debit is written.
2. **approved**: a **different active staff user** with an independent custom permission (`website.approve_servicerefund` or `store.approve_storereturnrefund`) documents an approval note of 8+ characters. The amount remains reserved; a second requested refund cannot consume the same available funds. No bank payout and no ledger debit occurs at approval.
3. **completed**: only after someone verifies the actual external bank/POS/cash/gateway receipt, a staff operator with change permission can record the payout proof and create exactly one debit entry. The final operator must NOT be the requester; they may be the independent approver. The original payment remains `paid`. Completed/refused requests and approval provenance cannot be edited or deleted. Idempotent repeat with the *same* proof is read-only.
4. **cancelled**: a requested or approved (but still unpaid) refund can be cancelled with a reason; reserved funds are released, no debit recorded, immutable approval provenance remains for audit.

## Implementation / controls
- Add status `approved`, `approved_by`, `approved_at`, `approval_note` and permission in both refund models. Additive Website.0029 and Store.0044 migrations only. No existing production RMA/refund rows before release; preflight requires exact zero counts.
- Service `approve_service_refund` and Store `approve_store_return_refund` are transactional, quote/order-lock first, identity/permission checked and idempotent only for exact matching reviewer/evidence. Both confirm functions require approved state, a unique original-payout reference and a second finance identity.
- Admin panel action forms enforce stage order, display requester/reviewer/payout operator and approval note. Dynamic action choices prevent a requested refund jumping directly to confirmation in UI. Backend and model reject status skips even if posted manually.
- Retain pending/reserved amounts through approval in both business domains. Customer pages display high-level refund status, never internal financial reviewer credentials. Finance reconciliation detects missing independent approver and requester self-approval/confirmation.
- Paid source/ledger immutability and previous stock/price snapshots unchanged. No automatic PSP refund implemented; second-person approval must NOT be confused with external bank payment.

## Testing and release gates
- Compare Host SHA, DB identity, pending migrations, full Store/Website financial counts to previous verified source. Last host baseline: 1 StoreOrder payment_review/awaiting_review 945450 Toman, 1 StorePayment, 3798 product variants and 0 returns, refund ledgers and inventory movements; Website Order #1 draft 805000 with zero service payments.
- Run focused fraud/permission/idempotency tests and broad prior Quote, Store checkout/RMA, finance reconciliation, stock and payment regressions. Known legacy test errors (phase39 shipping fixture collision, expected 70k vs calculated 60k, generic Username text assertion) predate the new change.
- Release runner `scripts/host/phase50_refund_dual_approval_deploy.sh`: exact SHA, exact changed files, verified full source/.env/MySQL gzip SHA256 backup, before/after hash of all 3798 Variant stock/reserved fields and real Order/Payment state, exactly Website.0029 + Store.0044. Read-only independent Host Admin/payment reconciliation and HTTP smoke. No live fake transaction is allowed.
- After release, a separate authorized individual must receive the new independent approval permission in Django groups if not superuser; **never auto-grant** this right to existing generic finance accounts.

## Out of scope
Automatic bank/provider refund API, PSP reversal callbacks, two-person approval of unrelated commercial credit-note creation, legal Store invoice/tax credit notes, new role/account provisioning without human authorization and warranty replacement shipping automation require their own secure phases.

## 2026-11-11 — Dual-approval deploy runner fails before source/migration due to non-DB calculated Quote.total_price
Initial guarded Host run at exact candidate `28187358dd84bd5b873352071ab648ccc8c01db9` verified original source/env/MySQL backup at `/home/sfkilvrs/3dprinthub-deploy-backups/20261111-081756-refund-dual-approval`, but stopped before Git merge or migration when constructing its pre/post SHA256 fingerprint with `Quote.objects.values_list('total_price')`: `total_price` is a Python @property, not an ORM field. Read-only Host follow-up confirmed still clean at old SHA `0ae8d785` and zero pending migration; no actual customer rows touched. Correction: the snapshot hashes real DB columns `pricing_snapshot_total,discount,weight_grams,print_time_minutes,machine_hourly_rate,shipping_fee` instead, in both before/after branches. Verified query compilation on the local Django model (`QUOTED_FIELDS_SQL_VALID=True`) and Bash syntax (`bash -n` PASS). New SHA and guarded Host release required; original one-time runner must not be re-used against a migrated server.
