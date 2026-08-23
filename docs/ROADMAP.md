# PROJECT ROADMAP

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Epic: `Phase49 — Unified Product / Slider / Catalog Sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.9 — AI Refresh + SEO/Source Completion`
Status: `FINAL CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Permanent Delivery Order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI → WINDOWS PULL --FF-ONLY → LOCAL GATE → MANUAL QA → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION BACKUP/DEPLOY/VERIFY`

## Immediate Business Priority — 2026-08-23
The owner wants to hand Catalog Center to employees today so they can begin product/catalog entry and move the live Store toward online payments.

Priority is therefore release readiness, not additional cosmetic development:
1. finish Windows 49.3I.9 acceptance,
2. allow controlled employee Catalog entry,
3. run one Local Publish E2E and verify the Local storefront/admin payload,
4. obtain explicit owner approval,
5. deploy the approved GitHub snapshot to Production with backup/rollback verification,
6. complete normal Store-cart online-payment integration,
7. test ZarinPal Sandbox end-to-end,
8. only then enable live payment and perform one owner-approved low-value Production payment.

## Preserved Phase49 Foundations
- unified Product / Hero / Catalog synchronization,
- Product Workspace as canonical detailed editor,
- Persian content and SEO workflows,
- Product / Portfolio publish targets,
- AI provider/runtime/provenance/cost stack,
- image intake default 10 / hard max 20,
- Fixed / Range / Formula pricing,
- visual Products Explorer,
- Local vs Production publish separation,
- live fetched GitHub snapshot handoff.

## Phase49.3I.9 — Current Runtime
49.3I.9 extends 49.3I.8 without replacing mature architecture:
- explicit All-Fields rerun refreshes AI-owned/generated content using the current Provider/Model,
- real manual overrides remain protected,
- generic Persian product titles are treated as invalid AI output,
- source-grounded Persian product/SEO prompt is strengthened,
- source website is preserved as publisher/source,
- Store Product meta/OG/source fields receive desktop SEO/source data after mature conversion/visibility layers,
- low image count may offer the mature source refetch before AI,
- factual/local defaults may complete readiness without inventing source facts,
- commercial-license and sale approval remain explicit operator decisions.

### Final Validation
CI-only PR `#55`: `CLOSED / NOT MERGED`.
Validated runtime base: `390c1aba9aaf5282f44a1ec97955af4e987100ba`.
Marker head: `0e58324bfc87e39299b81b1fbe65f9cce21ec91e` — not merged.

Successful runs:
- Phase49.3I `32623618842` — SUCCESS,
- Phase49.3H `32623618854` — SUCCESS,
- Phase49.3G `32623618950` — SUCCESS,
- Full Phase49 + Full Django `32623618792` — SUCCESS.

Django migration: NONE.
Catalog schema migration: NONE.

## Employee Catalog Release Gate — NEXT
Before employees rely on the tool:
1. clean Windows worktree,
2. live fetch/prune + ff-only pull current Epic,
3. run `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`,
4. verify Runner `49.3I.9` and live Git snapshot marker,
5. real All-Fields AI product-specific title/SEO refresh,
6. low-image warning/refetch,
7. MakerWorld Preview → Approve → mature Full Fetch,
8. Provider/model/FTP/Bridge credential persistence,
9. Product open/selection,
10. Fixed / Range / Formula regression.

After this Windows QA passes, employees may begin Catalog entry. Production publishing is still gated by Local Publish E2E and owner approval.

## Local Publish Gate
Exactly one test product must pass:
- `LOCAL PUBLISH ONLY`,
- Local Django import/visibility,
- title/description/SEO/source attribution,
- selected images/main image,
- Fixed/Range/Formula payload,
- Store/Admin rendering,
- no unexpected migration or dirty worktree.

## Payment Track — Verified Current State
The repository contains the mature Phase30 ZarinPal gateway for accepted `Quote` payments:
- deposit/full/balance,
- server-calculated amount,
- callback token,
- Authority match,
- server-to-server Verify,
- idempotent payment ledger/audit.

But the normal Store cart checkout is **not yet online-payment ready**:
- active `CheckoutOperationsForm` exposes only `bank_transfer`,
- active Store `checkout_view` redirects every new order to `store:manual_payment`,
- `StorePayment` has a `gateway` method value but no completed Store request/callback/verify flow.

Therefore the next implementation after Catalog release is a narrow Storefront ZarinPal bridge that reuses the mature payment/security contracts rather than creating a second unrelated payment architecture.

### Storefront Payment Acceptance Criteria
- online gateway is shown only when environment/site settings are ready,
- order amount is recomputed server-side,
- gateway attempt has idempotent identity,
- callback cannot trust browser amount/status,
- Authority must match stored attempt,
- Verify must be server-to-server,
- paid callback repeated twice must not double-finalize inventory/order/ledger,
- cancelled/failed/temporary provider errors remain recoverable,
- StoreOrder/StorePayment status transitions are tested,
- inventory reservation is finalized exactly once after successful payment,
- manual bank-transfer path remains available,
- secrets remain only in environment/secure server settings,
- Sandbox passes before any live merchant activation.

Current supported online provider in repository: `ZarinPal` only.

## Production Gate
Blocked until:
- Windows QA PASS,
- Local Publish E2E PASS,
- explicit owner approval,
- host branch/commit/path verified,
- MySQL vendor/name verified,
- backup/rollback verified.

Live Store payment has an additional gate: Store-cart integration + Sandbox E2E + owner-approved live test.

## Immediate Next Step
Run the repository-owned Windows `49.3I.9` gate and manual release QA. No direct Local patch, no Production deploy, and no live payment switch before the gates above pass.
