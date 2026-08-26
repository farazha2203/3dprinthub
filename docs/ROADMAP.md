# PROJECT ROADMAP

Updated: 2026-08-26
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Web Epic: `Phase50 — Finance, Commerce & Admin Command Center`
Current Web Phase: `50.A.2B — Immutable Checkout/Profile/Shipping Snapshot`
Parallel Windows Phase: `49.3I.32 — Canonical Product Source URL Guard / Catalog Center 8.8.2`
Status: `WEB 50.A.2B GITHUB CI TESTED / WINDOWS 8.8.2 BUILD 2026.08.26.2 TARGETED CI PASS / PACKAGED GATE RUNNING`

## Permanent delivery order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI/LOCAL TEST → OWNER QA → HOST READ-ONLY VERIFY → BACKUP → DEPLOY FROM GITHUB → PRODUCTION VERIFY → DOCUMENT`

## Parallel Windows track — 49.3I.29 → 49.3I.31 → 49.3I.32
Goal: keep the Catalog Center responsive on large catalogs, make Product AI exact-link grounded and batch-capable, and protect canonical Product identity from unrelated UI actions.

Implemented candidate:
- max 48 rendered Product cards/page without truncating SQLite results,
- deferred global Products refresh for Workspace Save/AI,
- exact saved mother Provider/Model/key; no hidden Product model scan/cross-provider fallback,
- exact Product link validation + page fetch/parser + canonical source title,
- safe extracted source facts organized as one bounded text body,
- AI factual payload exactly `source_title` + `source_description`, with raw HTML/auth/cookies/secrets/business state excluded,
- Persian content/SEO + selected-image metadata/finalization from the main AI action,
- selected-Product batch AI using each Product's own exact source link, per-item failure isolation and one final refresh,
- Phase49.3I.32 final Save guard: generic/silent Save cannot erase a persisted source URL when the two mirrored UI fields are temporarily blank,
- explicit non-empty link edits remain allowed,
- already damaged links can be recovered locally from exact Product history first, matching discovery identity second; no guessed URL/network reconstruction,
- release identity `8.8.2`, build `2026.08.26.2`.

Targeted verification: GitHub Actions `Phase49.3I.31-32 Smart Link Bulk AI + Source Guard CI` run `32996526852` PASS on `2ca69c4928333fc15247b99014a8fe77d781b50b`.

Windows acceptance gate before release:
1. Inspect Windows portable workflow `32996526842` and require PASS.
2. Re-verify live GitHub HEAD and clean `D:\projects\3DPrintHub` checkout.
3. Pull exact candidate; run `catalog_center\RUN_PHASE49_3I31_SMART_AI_GATE.ps1` (covers 3I.31 + 3I.32).
4. Verify populated source URLs survive Save, AI, image-related and publish-related actions.
5. Verify the Product already affected by the bug recovers its exact local historical/discovered URL where evidence exists.
6. Run large Products UI, OpenRouter, AvalAI, selected-image SEO and selected-Product batch/cancel/error-continuation QA.
7. Only after owner QA: explicitly publish/verify immutable `catalog-center-v8.8.2` and record exact SHA256/commit. Pushes no longer auto-publish the Windows release.

## Phase50.A — Admin and commerce operational completeness
- 50.A.1 Admin Storefront/Hero parity — DEPLOYED.
- 50.A.1B Product Gallery + Variant2 — DEPLOYED; `store.0034` applied.
- 50.A.1C Admin media/mobile/SEO/Windows dimensions — DEPLOYED.
- 50.A.1D Sales Profiles + Hero public media — DEPLOYED; `store.0035` applied.
- 50.A.1E Unified Product Admin Workspace — PRODUCTION VERIFIED.
- 50.A.1F Business Admin Navigation + Product Admin 500 hotfix — PRODUCTION VERIFIED.
- 50.A.1G Velzon Operator Surface V2 — PRODUCTION FOUNDATION.
- 50.A.1H Admin Shell Stability — PRODUCTION VERIFIED.
- 50.A.2A Storefront Sales Profile Selector — PRODUCTION VERIFIED.

Current Production application commit remains `c283864290f9c989a9fcdf24ee8eef519560e917`; `0034` and `0035` are applied and 50.A.2B is not yet deployed.

## 50.A.2B — Immutable Checkout/Profile/Shipping Snapshot — GITHUB CI TESTED
Migration `store.0036_phase50_checkout_snapshot` adds immutable StoreOrderItem profile/selection/final-weight/shipping-weight/print-time snapshots plus StoreOrder `insured_value` and normalized `shipping_quote_snapshot`, preserving existing `0034` size/build/package snapshots.

Runtime preserves the mature Phase6 checkout/coupon/inventory/address/notification/payment flow, uses effective ProductVariant shipping weight, finalizes snapshots inside an outer atomic boundary, keeps ShippingMethod/rate rules as the explicit fallback and does not invent combined parcel geometry or external carrier contracts.

Verification: GitHub Actions `Phase50 Variant2 Gallery CI` run `32966720475` PASS on `fba0631e60bce1f6e3f622317b70c2f7f35d978f`.

### Production gate for 50.A.2B
1. Read-only verify Host HEAD/worktree/live GitHub SHA and MySQL `0034/0035/0036` state.
2. Verify exact migration plan and backup capability.
3. Fresh source + `.env*` + MySQL backup; preserve rollback HEAD.
4. Explicit branch fetch to `FETCH_HEAD` per ERR-50-007; verify ff-only target.
5. Apply only approved `store.0036_phase50_checkout_snapshot` after backup/DB verification.
6. Passenger restart + Production schema/runtime/HTTP/order-snapshot verification without altering historical paid orders.

## Product engagement package — NEXT AFTER 50.A.2B
Favorite/Save if absent, like/save/review/comment counters/Admin visibility, qualifying paid/purchased buyer-feedback policy, dedicated migration/tests/backup while preserving ProductLike/ProductComment/ProductReview.

## 50.A.3 Secure Store ZarinPal
Server-owned amount, exact callback/Authority verification, idempotency and trusted gateway-host allowlist; never store card/PIN/CVV.

## 50.A.4 Torob
Official Product API v3 with stable Product/Profile identity, price/availability and image-quality contract.

## Phase50.B–F
Accounting Core → Treasury → Purchasing/Payables → Sales/Receivables → Reports/Close.

## Safety
No Production schema work without exact MySQL verification, migration plan, fresh successful backup and rollback target. Imported Catalog working-media remains private. Purchased/private Velzon/font assets stay out of public GitHub. Production branch fetch uses explicit live branch → `FETCH_HEAD` because Host refspec remains tag-only.
