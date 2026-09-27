# Phase50.A.2Z-C — Dynamic Shipping Carrier Activation

Status: `IN_PROGRESS / CONTRACT_AUDIT`
Date: 2026-09-27
Branch: `wip/phase50-a2z-w5-manual-product-20260927`

## Verified starting point

- W5 Manual Product is present in commit `48b7bfd...` and its focused/current
  regression is green; W6 is accepted at the preceding GitHub head.
- The Site currently owns `ShippingMethod`, rate rules, selected shipping
  method, order shipping fee and immutable order shipping snapshot fields.
- No verified Post/Tipax/Mahex adapter, endpoint, credential, secret name or
  provider sandbox contract exists in the current Repository.
- No provider request, credential read, Host operation or Production mutation
  is authorized by this kickoff.

## Contract

1. Keep the current ShippingMethod/rate-rule path as a deterministic fallback.
2. Each carrier adapter must be provider-specific and fail closed when its
   endpoint, credentials, destination mapping or quote response is missing.
3. Quote input must use the selected Product Profile's effective shipping
   weight plus verified package dimensions/facts and destination postal data;
   never invent missing technical or package facts.
4. A selected quote must be frozen into the order snapshot: carrier,
   service, provider quote ID, amount, currency, weight/destination inputs,
   expiry and timestamp. Later provider changes must not rewrite an existing
   order.
5. Retries and webhook/tracking updates must be idempotent and auditable.
6. Provider unavailable, ambiguous or stale quote states must fall back to the
   existing method or require operator/customer re-selection; they must not
   silently charge a guessed amount.

## Evidence and gates

- Required before adapter implementation: official provider API/merchant-panel
  contract, sandbox or read-only credentials, authentication method, rate and
  service semantics, cancellation/refund behavior, and tracking contract.
- Required local tests: quote normalization, duplicate/idempotent quote,
  expiry, fallback, destination/weight validation, immutable order snapshot,
  retry and reconciliation.
- Required Server gates: migration/no-migration audit, exact GitHub SHA,
  fresh DB/source/environment backup, Host readiness and Production UAT.
- No live quote, shipment creation, payment charge or carrier activation is
  allowed during this contract-audit phase.

## Current research boundary

Public search found a Tipax cost-calculator page and third-party integration
documentation, but not a verified project-authorized merchant API contract
for all three carriers. The implementation is therefore intentionally stopped
before adapter or credential code. Official documentation/credentials from the
merchant accounts are the next required input.

## Exact next task

Inventory existing Store shipping tests/models and prepare a read-only quote
contract matrix. Then, only after an official provider contract is available,
implement one adapter behind the fallback interface and run Local tests. No
Deploy until Server delta, backup and owner release approval are complete.

## Read-only quote contract matrix — 2026-09-27

| Domain | Current authoritative field | Quote use | State |
|---|---|---|---|
| Product shipping mass | `ProductVariant.shipping_weight_grams`, fallback to `final_weight_grams` / `material_weight_grams` in Store cart logic | Per-unit grams × quantity; must be positive/verified | Available locally |
| Quantity | `StoreOrderItem.quantity` | Total shipment mass and package count input | Available locally |
| Subtotal | `StoreOrder.subtotal` | Existing `free_over` fallback rule and quote context | Available locally |
| Destination | `StoreOrder.province`, `county`, `city`, `address`, `postal_code` | Provider destination mapping; postal code must be validated | Available locally; provider mapping pending |
| Package dimensions | Product/profile data may contain dimensions, but no canonical StoreOrder package snapshot field is present | Required only if the provider contract requires volumetric weight | Not yet authoritative; do not invent |
| Packaging | `StoreOrder.packaging_fee` exists as an amount, not package dimensions/material facts | Preserve existing fee; carrier package facts need explicit contract | Amount exists; facts pending |
| Selected fallback method | `StoreOrder.shipping_method` + copied `shipping_title` | Deterministic fallback and historical display | Available locally |
| Fallback amount | `ShippingMethod.calculate_fee(subtotal, total_weight_grams)` using active `ShippingRateRule` or `flat_fee` | Safe quote when provider unavailable | Available locally |
| Order snapshot | `shipping_title`, `shipping_fee`, `total_weight_grams`, destination fields | Prevent later rate changes rewriting an order | Available locally |
| Provider quote identity | No current `provider_quote_id`, expiry or raw quote payload on `StoreOrder` | Required for dynamic quote reconciliation/idempotency | Requires approved schema/contract |

### Normalized quote input (future adapter boundary)

```text
quantity: positive integer
total_weight_grams: Decimal > 0, from selected Variant facts
subtotal: non-negative integer
destination: province/county/city/postal_code/address
package: dimensions only when explicitly factual and provider-required
fallback: ShippingMethod + active ShippingRateRule result
```

### Fallback and immutable snapshot rules

- Quote order: verified carrier quote → existing ShippingMethod/rate rule →
  fail closed for customer/operator selection; never guess a price.
- Every selected result must copy carrier/service/title, amount/currency,
  weight/destination inputs, provider quote ID, expiry and raw response into
  an immutable order/audit snapshot once the provider contract authorizes those
  fields. Existing orders must remain readable without a provider.
- Retry of the same quote key must be idempotent; a changed weight, quantity,
  destination or expired quote requires a new quote rather than overwriting a
  paid/placed order.
