# 2026-11-09 — Service Quote print-time basis
Status: PRODUCTION_VERIFIED at runtime SHA `df1be38355da6f3fa16ce5f480e5da81b5ae239a`; 80/80 Local tests PASS, guarded Host migration 0026 / backup / HTML checks / public smoke PASS.

## Requested delta
Prevent ambiguous production-job time from inflating the machine component of multi-piece quotes. An operator must explicitly choose whether the entered slicing time refers to **each piece** or **the entire printed batch**. The price agreement and payment ledger from the previous finance release must remain correct.

## Touched surfaces
- `website.models.Quote.print_time_scope`: `per_piece` (default, historical behavior) or `batch`.
- `Quote.total_billable_machine_minutes` and machine cost formula.
- `Quote` snapshot freeze policy: `print_time_scope` is immutable once sent/accepted.
- Website order/quote Django Admin displays and customer quote detail labeling.
- Additive nullable-safe migration `website.0026_quote_print_time_scope`, default `per_piece`.
- Regression tests `website.test_quote_time_basis`.

## Pricing contract
- Material amount always uses *weight per piece* × quantity × material rate.
- Machine hours use existing minimum/increment rounding once per entered time; multiply by quantity **only** in per-piece mode.
- Existing labor, design, post-processing and shipping fees remain **once per quote**.
- Discount remains a fixed Toman value per quote, subtracted once from the subtotal, never below zero.
- Defaults remain per-piece; existing draft quotes do not reprice merely because of migration.
- Customer quote page must not expose a draft amount as a finalized quote.
- Quote mode and price become unchangeable when `status` becomes `sent`/`accepted`.

## Recorded production exemplar, READ-ONLY, no PII
Order #1: quantity 4; piece weight 20 g; entered print time 200 minutes; current increment bills 240 minutes; hourly machine rate 40,000 Toman; material 1,500 Toman/g; labor 45,000 Toman; no discount or payment; quote draft. Existing per-piece calculation: material 120,000 + machine 640,000 + labor 45,000 = **805,000 Toman**. If operator later selects `batch` on the draft: material 120,000 + machine 160,000 + labor 45,000 = **325,000 Toman**. This is a what-if comparison, not an authorization to change Order #1's actual billing basis.

## Safety / must not touch
- No write to Order #1 or production receipts or discounts during rollout.
- Do not change machine hourly tariff, quantity, catalog material price, operator fee or past payments.
- Require exact production source/migration state, verified full source/.env/MySQL backup, GitHub SHA-pinned allowed delta, one additive migration and post-migration read-only verification.
- Financial refund, credit-note and disputed-payment reversal workflows remain separate.

## Regression gates and release
Local 80/80 (including legacy finance/payments and secure order image preview) PASS. Django check and no migration drift PASS with pre-existing warnings; Bash syntax and git diff hygiene PASS. Deploy runner is fail-closed on real order #1 unchanged in the database. GitHub SHA and actual Production rollout/verification must be added only after execution.

## Production verification closeout — 2026-11-09
- Runtime code: `df1be38355da6f3fa16ce5f480e5da81b5ae239a`.
- Guarded runner: `QUOTE_TIME_BASIS_DEPLOY=PASS` with GitHub SHA, FF-only and strict allowed delta.
- Migration: exactly `website.0026_quote_print_time_scope`, successfully applied; no other pending schema work.
- Verified full source/env/MySQL rollback: `/home/sfkilvrs/3dprinthub-deploy-backups/20261109-184700-quote-time-basis`.
- Independent read-only Host Order #1 admin and private Quote GET: both 200, draft panel visible, final-price table hidden until acceptance.
- Old per_piece interpretation and amount remain the same (805000 Toman); optional batch comparison is in-memory only (325000 Toman).
- Payment and ledger records remain zero; Django checks/no-drift and Home/Store HTTP 200 PASS.
- 80/80 Local regressions PASS, including new admin field/lock tests.
- **Remaining user decision:** Whether entered 200-minute slicing estimate means 200 minutes *each* or 200 minutes *for all four pieces*; do not alter real quote until verified.
