# 2026-11-10 — Service Order lifecycle, payment methods and Catalog Center pricing parity

Status: LOCAL_TESTED (97/97 broad regressions PASS; no migration drift, compile, Bash syntax and diff checks PASS). Production rollout pending.

## Owner intent and acceptance
Service order admin must let an operator approve a price then allow the owner/customer to submit multiple receipts; payment kinds: deposit, partial, full/balance. Bank transfer receipts and optionally online verified gateway remain customer-controlled; office POS and cash are recorded by the finance operator and independently confirmed. Manual receipts go to awaiting_review unless a privileged operator explicitly confirms them. Finances calculate cumulative paid, awaiting review and available balances without fake ledger or order paid flags. Shipping/hand-off: use the *same active* Store ShippingMethod list to record post, courier and pickup/office; dispatched and delivered states are distinct. The operator can manually mark delivered only after a paid, accepted immutable quote. The customer sees the shipment status and tracking.

The service quote's catalog-linked path must select the identical active MaterialColorOption (type/brand/color/rate) and PrintQuality models used on the Store. Prices from the selected Desktop-managed Offer are: per-gram sale price = roll sale price / roll weight; chargeable grams = part + support×multiplier; machine = print hours×Offer's print_hourly_rate; supervision = print hours×Offer's supervision_hourly_rate; preheat = preheat hours×Offer's preheat_hourly_rate; assembly per piece, quantity. Desktop rounds monetary components HALF_UP, and the total must use the same raw combined HALF_UP rounding (record any ±1 rounding adjustment separately). A chosen Offer prices the service Quote; legacy non-Offer draft quotes preserve their prior formula and confirmed quotes retain existing immutable snapshots. Per-unit vs batch print-time is explicit.

## Scope of code changes
- `website.models.Quote`: offer, print quality, support weight, support multiplier, per-unit assembly fee; frozen supervision/preheat/assembly/rounding ledger amounts.
- `website.quote_pricing_policy`: validates actual offer availability/stock and locks pricing source, extra costs, discounts and amounts after final acceptance.
- `website.quote_catalog_offer` and admin QuoteInline/QuoteAdmin: source from exactly active, priced, saleable Store offers.
- `website.models.Payment`: POS and cash method choices and partial payment kind; no direct gateway Verify privilege assigned to operators.
- `website.order_finance_admin`: privileged manual cashier method+amount+confirmation and cash form idempotency; duplicate refs blocked.
- `website.forms.QuotePaymentForm` and bank-transfer view: user-entered partial receipt; transaction lock prevents overspending; receipt awaits finance review.
- `website.models.ServiceOrderDelivery`, `website.service_delivery_admin`: shipping selector drawn from existing Store shipping list with tracking/recipient/date/audit actor, protected from edits after final delivery and from shipping before full accepted payment.
- Quote customer page/admin Order page: separate financial/cargo summaries and actual methods.
- Additive Website migration `0027_service_order_payment_delivery_catalog_offer`. No historical backfill.

## Production invariants / safety
Keep live Order #1 (draft/4 pieces/200 minutes/`per_piece`/805000 Toman) unchanged; still no paid receipts or ledger, same uploaded private media. Do not test real payments or mark it shipped. Require exact Host SHA and branch + GitHub SHA, MySQL identity and empty preexisting migration plan, approved file allowlist, verified full source/env/MySQL backup (SHA256 + gzip), one exact expected additive migration, in-process read-only Admin Order #1 GET and customer preview/draft amounts hidden, Home/Store HTTP 200, clean git worktree. If any check fails, fail-closed. Do not copy the dirty canonical Windows development worktree. Do not use another project tunnel.

## Known scope boundaries
- Reuses 112 live active priced filament Offers, not a clone/forked price table; availability/stock must be re-verified at finalization.
- This is a service-order quote flow, not a migration of every Store ProductVariant into the Quote form. Selling finished physical Products remains handled by StoreOrder and its stock/reservation lifecycle.
- POS and cash represent manual operator attestations; no bank API verification. Payment gateway remains server Verified. Refunds, credit notes, returns and contested-payment reversal require their own audit-grade phase.
- Material/print quality and shipping availability are dynamic until an offer is finalized; its monetary snapshot must be immutable after acceptance.

## Test / release evidence
Final local broad regression **97/97 PASS** across Catalog Offer formula (including fractional total rounding), old Quote pricing and payment/gateway functionality, customer partial receipts, cash/POS idempotency, delivery with post/courier/pickup, original private images, and website baseline. `manage.py check` PASS with known prior notices, `makemigrations --check --dry-run` no drift, Python compile PASS, shell `bash -n` PASS, Git diff hygiene PASS. Tested candidate SHA and backed-up guarded deploy evidence must be recorded only after execution. Host read-only preflight reverified clean SHA `df1be38355da6f3fa16ce5f480e5da81b5ae239a`, migrations 0025/0026 applied.
