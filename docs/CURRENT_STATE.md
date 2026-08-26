# CURRENT PROJECT STATE

Updated: 2026-08-26
Repository: `farazha2203/3dprinthub`
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Release: `Phase50.A.1H Admin Shell Stability + Phase50.A.2A Storefront Sales Profile Selector`
Status: `PRODUCTION_VERIFIED / OWNER VISUAL QA NEXT`

## Production state — terminal verified
Current Production application commit: `c283864290f9c989a9fcdf24ee8eef519560e917`.

Verified Production environment:
- root `/home/sfkilvrs/3dprinthub`,
- venv `/home/sfkilvrs/virtualenv/3dprinthub/3.12`, Python 3.12.13, Django 6.0.7,
- MySQL `sfkilvrs_EmiAdmin_3dprinthub`,
- `store.0034_phase50_variant2_commerce` applied,
- `store.0035_phase50_sales_profiles` applied,
- migration drift NONE,
- migration plan empty,
- no migration executed for this release,
- clean Production worktree,
- Home/Store/Admin login/Product detail/new static assets HTTP 200,
- Product HTML selector contract PASS,
- public Variant commerce API PASS,
- public Home private imported-media refs = 0.

Fresh rollback backup for this deployment: `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-143650`.
It contains tracked-source archive + SHA256, copied `.env*` files, MySQL dump + SHA256, and deploy metadata. The earlier `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-143245` attempt stopped before deployment during environment-backup process substitution and is retained only as audit evidence.

## Phase50.A.1H — Admin Shell Stability — PRODUCTION VERIFIED
Owner QA of Velzon V2 reported footer flash/mid-page placement during refresh, whole-page jump around active-menu navigation and insufficient sidebar width.

Deployed fix:
- `static/admin/phase50-admin-shell-stability.css`,
- Velzon footer forced into normal/static document flow,
- stable flex/min-height Admin shell,
- right operator sidebar widened from 250px to 290px,
- Persian menu spacing/readability improved,
- broad shell geometry transitions disabled,
- document-level `scrollIntoView()` removed from active-menu handling,
- active link centering now adjusts only the internal SimpleBar/sidebar scroll position,
- existing Velzon V2 on-demand filter/full-width table behavior preserved,
- no schema migration.

Verification:
- GitHub Actions `Phase50 Product Admin Workspace CI` run `32958276378` PASS on `27335832e90c35dd95bb8a686dd89d1efd46dc8f`,
- Production static asset HTTP 200,
- Django check PASS with only known warnings.

Owner browser QA still required: repeated refresh must show no footer flash across content; opening/changing right-menu items must not move the document viewport; 290px sidebar must be readable.

## Phase50.A.2A — Storefront Sales Profile Selector — PRODUCTION VERIFIED
The existing Product/ProductVariant sales-profile backend is now surfaced on Product detail pages without duplicate schema/state.

Deployed behavior:
- Product selection modes remain authoritative: list / size / weight / build / size→build / build→size,
- existing endpoint `/store/api/variant-commerce-options/` reused,
- customer controls expose available size/build/weight/material/color/quality/profile distinctions,
- selected profile summary exposes price, profile, size, build, material, color, quality, part/shipping weight, print time and parcel dimensions when present,
- native `variant-select` remains progressive-enhancement fallback,
- selected choice resolves to canonical ProductVariant ID and dispatches the existing change event, preserving current price/cart/AddToCartForm logic,
- no migration.

Production smoke sample:
- Product `shoe-holder-organiser`, Product ID 1,
- selection mode `size_build`,
- Variant ID 1,
- profile label `استاندارد`, build `standard`, material `PLA`,
- unit price `2131170`, final weight `1.00`, effective shipping weight `1.00`,
- Product detail HTTP 200,
- selector CSS/JS loaded,
- native fallback present,
- public Variant API parsed and verified.

Storefront CI: `Phase50 Variant2 Gallery CI` run `32958296546` PASS on `e3c57311c0c3980befeaf6012f3bb8fc502333bc`.

## Deployment incidents captured
- `ERR-50-007`: host `remote.origin.fetch` still tracks only tag `v0.33.0`; Production deploys must verify live branch and explicitly fetch branch to `FETCH_HEAD` before ff-only merge.
- `ERR-50-010`: cPanel shell did not provide reliable `/dev/fd` for Bash process substitution during `.env*` backup; recovery uses Python filesystem enumeration/copy instead.
- `ERR-50-011`: a verifier invoked a JSON file path as the Python script, causing JSON `false` to be parsed as Python; correct pattern is `python - <args>` with JSON loaded through `json.load`.

Known warnings remain CKEditor4 maintenance/security debt, `store.W026` in-memory realtime debt and MySQL conditional-constraint warnings.

## Scope boundary
50.A.2A makes profile/size/build/weight/color/price selection visible and keeps canonical Variant ID flowing into the mature cart path. It does not yet complete immutable customer-choice checkout snapshots, normalized carrier quotes, insured value or final delivery workflow.

## Exact next work
1. Owner browser QA of Admin footer stability, right-menu no-jump behavior, 290px sidebar and Product selector interaction/price synchronization.
2. After owner visual approval, mark 50.A.1H and 50.A.2A accepted.
3. Continue 50.A.2B: immutable selected-profile/customer-choice order snapshot, effective product+packaging shipping weight, parcel dimensions/insured value and normalized delivery quote while preserving ShippingMethod fallback.
4. Then implement Product engagement package: Favorite/Save + like/save/review/comment counters + verified-purchase buyer-feedback policy with dedicated migration/tests/backup.
5. Continue secure Store ZarinPal → Torob Product API v3 → accounting core.
