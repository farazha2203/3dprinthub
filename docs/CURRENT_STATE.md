# CURRENT PROJECT STATE

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Branch: `epic/phase49-unified-product-slider-sync`
Active Phase: `49.3I`
Active Hotfix: `49.3I.9 — AI Refresh + SEO/Source Completion`
Status: `GITHUB UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Current Position
Phase49.3I.9 is implemented and CI-validated on GitHub. The owner now wants an operational release today so employees can start catalog/product entry and the live site can move toward accepting payments.

The immediate release policy remains fail-closed:
`GitHub → Windows ff-only pull → Local automated gate → Manual visual/data QA → one LOCAL PUBLISH ONLY → Local Django E2E → explicit owner approval → Production backup/deploy/verify`.

No Production action is authorized before those gates pass.

## Phase49.3I.9 Runtime Delta
49.3I.9 addresses `ERR-49-027`:
- explicit All-Fields AI rerun can refresh AI-owned/generated content when Provider/Model changes,
- proven manual operator overrides remain protected,
- generic Persian titles such as `محصول چاپ سه بعدی` are refreshable and newly generated generic titles are rejected,
- Persian ecommerce/SEO prompt is more source-grounded and product-specific,
- source website identity is stored as publisher/source rather than being replaced by designer identity,
- desktop SEO/source attribution is applied to real Django Product meta/OG/source fields after mature conversion/visibility layers,
- when product images are below the selected limit, All-Fields may offer the existing mature source `refetch()` before AI,
- missing local readiness defaults can be filled without fabricating source facts,
- missing price falls back locally to 500,000 Toman only as an operator-preparation default,
- legal commercial-license confirmation and final sale approval still require explicit operator confirmation.

## Final GitHub Validation — 49.3I.9
CI-only PR `#55`: `CLOSED / NOT MERGED`.
Validated runtime base: `390c1aba9aaf5282f44a1ec97955af4e987100ba`.
CI marker head: `0e58324bfc87e39299b81b1fbe65f9cce21ec91e` — not merged.

Successful workflows:
- Phase49.3I Discovery Review Pricing CI — Run `32623618842` — SUCCESS.
- Phase49.3H SEO Cost Image Limit CI — Run `32623618854` — SUCCESS.
- Phase49.3G Workspace Usability CI — Run `32623618950` — SUCCESS.
- Phase49 Epic Unified CI / Full Django — Run `32623618792` — SUCCESS.

Validated:
- runner `49.3I.9`, ASCII-only Windows PowerShell 5.1 contract,
- live fetched GitHub snapshot guard,
- Python compile,
- AI-owned refresh/manual-override protection,
- generic-title rejection,
- source-image preflight/refetch contract,
- publisher/source-site mapping,
- real Product SEO meta/OG/source mapping,
- Phase49.3I/3H/3G regressions,
- Django checks,
- `makemigrations --check --dry-run` = no changes,
- safe migration plan,
- Windows Catalog Epic49 tests,
- Full Django suite.

## Database / Migration / Media / Secret Safety
- Django migration for 49.3I.9: `NONE` — CI verified.
- Catalog schema migration: `NONE`.
- no DB reset/drop/truncate.
- no historical data/media rewrite/delete.
- no secret storage change.
- Production DB/media/source untouched.

## Payment Readiness — Important Verified Gap
The repository already has a mature Phase30 **ZarinPal** online-payment flow for accepted `Quote` payments (deposit/full/balance), including server-side amount calculation, callback token, Authority matching, server-to-server Verify, idempotent ledger and audit.

However the current public **Store cart/checkout** is not yet wired to that online gateway:
- active `CheckoutOperationsForm.payment_method` currently exposes only `bank_transfer`,
- the active store `checkout_view` always redirects new orders to `store:manual_payment`,
- `StorePayment` has a semantic `gateway` method but there is no completed Store checkout request/callback/verify flow using it.

Therefore enabling the existing Quote ZarinPal environment switches alone does **not** make normal Store cart checkout pay online. Storefront gateway integration is an urgent release task and must be tested before live money is accepted.

Current supported gateway implementation in repository: `ZarinPal` only.

## Windows QA Required Now — Employee Release Gate
1. close Catalog Center completely,
2. verify Local worktree is clean,
3. fetch/prune and ff-only pull the live Epic branch,
4. run repository `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`,
5. verify Runner `49.3I.9` and `PHASE49_3I_GIT_SNAPSHOT=OK`,
6. open one known Product Workspace,
7. run bottom All-Fields AI and verify product-specific Persian title/SEO, current Provider/Model refresh, progress visibility and manual-override safety,
8. test low-image warning/refetch once,
9. test MakerWorld Preview → Approve → Full Fetch once,
10. verify Provider keys/model lists + FTP/Bridge credentials remain available,
11. verify Product open/selection and Fixed/Range/Formula remain healthy.

If those pass, employees may begin using the Windows Catalog Center for data entry while the Local Publish E2E/Production release is completed. They must not use direct Production source edits.

## Local Publish Gate
After Windows QA passes:
- exactly one `LOCAL PUBLISH ONLY`,
- Local Django E2E,
- verify product title/SEO/images/pricing/source attribution in Local Store/Admin,
- verify no unexpected data/migration changes,
- explicit owner approval.

## Production Release Gate
Only after owner approval:
- verify host project root, branch and fetched commit read-only,
- verify host worktree safety,
- verify effective `.env` without exposing secrets,
- verify MySQL vendor and exact database name,
- verify backup/rollback target,
- pull approved GitHub commit only,
- `manage.py check`, migration plan, collectstatic if needed, Passenger restart,
- HTTP/admin/store/product/cart smoke tests,
- Production data/media verification.

## Payment Release Track
After Store checkout gateway integration is implemented and tested:
1. Local/Sandbox ZarinPal request → redirect → callback → verify,
2. repeated callback idempotency,
3. failed/cancelled/temporary-error cases,
4. StoreOrder/StorePayment status transitions,
5. inventory reservation/finalization behavior,
6. Production configuration read-only precheck,
7. live low-value payment only after explicit owner approval,
8. payment audit and Production verification.

## Exact Next Task
Do the Windows 49.3I.9 release gate first. Do **not** deploy Production or enable live Store payments yet. In parallel, treat Store-cart ZarinPal integration as the next urgent implementation task because the existing Phase30 gateway currently covers Quote payments, not the normal Store cart checkout.
