# PROJECT_CONTEXT — 3DPrintHub

Updated: 2026-08-26
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Epic: `Phase50 — Finance, Commerce & Admin Command Center`
Current Subphase: `50.A.2B — Immutable Checkout/Profile/Shipping Snapshot`
Status: `GITHUB CI TESTED / PRODUCTION MIGRATION AUDIT NEXT`

## Operating rule
GitHub is permanent source of truth.
`READ DOCS → VERIFY REAL STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI/LOCAL GATE → HOST READ-ONLY VERIFY → BACKUP → DEPLOY FROM GITHUB → PRODUCTION VERIFY → UPDATE DOCS`.
No permanent Production source edits; dirty worktree stops for inspection.

## Canonical paths
Windows project `D:\projects\3DPrintHub`; venv `D:\projects\3DPrintHub\.venv`.
Production root `/home/sfkilvrs/3dprinthub`; venv `/home/sfkilvrs/virtualenv/3dprinthub/3.12`; DB MySQL `sfkilvrs_EmiAdmin_3dprinthub`.

## Production baseline
Application commit `c283864290f9c989a9fcdf24ee8eef519560e917`.
Latest verified rollback backup `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-143650`.
`store.0034` + `store.0035` are applied; `store.0036` is NOT yet Production-applied.
Home/Store/Admin/Product/Variant API are healthy; private imported-media refs are zero.

## Production-verified current UX
- Admin shell: normal-flow footer, stable shell, 290px sidebar, internal-only menu scrolling, Velzon V2 on-demand filters/full-width lists.
- Storefront: profile/size/build/weight/material/color/quality selector uses public Variant API and canonical ProductVariant ID with native fallback.

## 50.A.2B GitHub-tested runtime
Migration `0036_phase50_checkout_snapshot` + `store/phase50_checkout_snapshot.py` add immutable final order state while preserving mature Phase6 checkout.

StoreOrderItem freezes:
- sales-profile name/key/label,
- profile selection mode/value visible to customer,
- size/build/material/color/quality,
- final/package/effective shipping weight,
- print time and package dimensions.

StoreOrder freezes:
- `insured_value` as merchandise value after discount,
- normalized `shipping_quote_snapshot` with ShippingMethod fallback source, destination, total weight, fee and per-line packages.

Runtime guarantees:
- Cart weight uses `effective_shipping_weight_grams`,
- successful checkout is finalized in an outer atomic transaction,
- coupon/VAT/inventory/address/notification/payment logic remains the mature Phase6 path,
- payment amount stays synchronized with finalized shipping fee,
- no combined parcel geometry is guessed,
- no external carrier API is called/claimed,
- finalizer failure rolls DB state back and restores cart session.

CI: `Phase50 Variant2 Gallery CI` run `32966720475` PASS on `fba0631e60bce1f6e3f622317b70c2f7f35d978f`, including migration through `0036` and integration snapshot immutability tests.

## Host-specific deployment constraints
- ERR-50-007: remote fetch refspec is tag-only; verify live branch and explicit fetch to `FETCH_HEAD` before ff-only.
- ERR-50-010: do not depend on cPanel `/dev/fd` process substitution for backups.
- ERR-50-011: JSON verifier payloads are parsed with `python -` + `json.load`.

## Immediate next work
1. Read-only Production audit for actual HEAD/worktree/live GitHub SHA/MySQL `0034/0035/0036`/migration plan/backup capability.
2. Fresh source/.env/MySQL rollback backup.
3. Deploy approved GitHub snapshot, inspect and apply only `store.0036_phase50_checkout_snapshot`, restart and verify Production.
4. Then Product engagement: Favorite/Save + counters + verified-purchase buyer feedback.
5. Secure ZarinPal → Torob → accounting core.
