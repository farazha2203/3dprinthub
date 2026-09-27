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
