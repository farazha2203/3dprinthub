# CURRENT PROJECT STATE

Updated: 2026-08-26
Repository: `farazha2203/3dprinthub`
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Primary Web/Commerce Release: `Phase50.A.2B — Immutable Checkout/Profile/Shipping Snapshot`
Parallel Windows Track: `Phase49.3I.32 — Canonical Product Source URL Guard`
Status: `WEB 50.A.2B GITHUB CI TESTED / WINDOWS 8.8.2 BUILD 2026.08.26.2 TARGETED CI PASS / PACKAGED WINDOWS GATE RUNNING`

## Production state — terminal verified
Current Production application commit: `c283864290f9c989a9fcdf24ee8eef519560e917`.

Verified Production environment:
- root `/home/sfkilvrs/3dprinthub`,
- venv `/home/sfkilvrs/virtualenv/3dprinthub/3.12`, Python 3.12.13, Django 6.0.7,
- MySQL `sfkilvrs_EmiAdmin_3dprinthub`,
- `store.0034_phase50_variant2_commerce` applied,
- `store.0035_phase50_sales_profiles` applied,
- `store.0036_phase50_checkout_snapshot` NOT YET DEPLOYED/APPLIED,
- clean Production worktree,
- Home/Store/Admin/Product/Variant API verified healthy,
- public Home private imported-media refs = 0.

Latest verified Production rollback backup: `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-143650`.
A fresh backup is mandatory again before applying `0036`.

## Phase49.3I.29 / 31 — Windows performance + Smart Link / Bulk AI
Preserved candidate behavior:
- Products Explorer renders at most 48 Product cards per page while retaining all SQLite results,
- Workspace Save/AI marks the global Product list dirty instead of rebuilding all cards/thumbnails on each edit,
- mother AI settings remain authoritative: exact saved Provider + exact saved Model + secure key,
- Product AI uses the exact Product source link, parses the real page, converts safe facts into one structured text body and sends only `source_title` + `source_description` as factual Product fields,
- selected images may be included only for the explicit image-aware AI action,
- the main AI action completes Persian content + SEO + selected-image metadata,
- selected Products can run the same grounded AI pipeline in batch with per-item error isolation and one final Products refresh.

## Phase49.3I.32 — Canonical Product Source URL Guard — TARGETED CI PASS
Owner reported that one unrelated Product action could erase the saved source link. Repository inspection found the mature `ProductStudio.save()` used only the two mirrored URL controls. When both were temporarily blank, a generic/silent Save wrote empty `source_url`, then recomputed `normalized_url` and `fingerprint` from the empty value. Because silent Save is reused by close/refetch/AI/publish/layered actions, the symptom could appear after pressing a button that was not intended to edit the link.

Fix is additive at the final Workspace-save boundary:
- an explicit non-empty URL edit remains allowed,
- if both mirrored URL controls are blank, an existing DB source URL is preserved before the old Save chain runs,
- a post-save invariant restores source URL/normalized URL/fingerprint if a legacy layer still tries to erase them,
- a Product already damaged by the old bug can recover its exact link locally from `product_history` first and matching `discovered_urls` second,
- recovery uses only an exact previously stored HTTP/HTTPS URL; no URL is guessed or reconstructed and no network is used,
- recovery/preservation is recorded in Product history/diagnostics,
- no price, stock, material, color, AI provider/model or Production schema behavior is changed.

Candidate identity:
- Catalog Center `8.8.2`,
- build `2026.08.26.2`,
- targeted runtime/CI snapshot `2ca69c4928333fc15247b99014a8fe77d781b50b`,
- targeted CI run `32996526852` PASS.

Targeted CI covered source-link preservation, intentional URL edits, exact local history recovery, exact discovery fallback, final Workspace guard, Phase49.3I.31 smart/batch AI, Phase49.3I.29 performance, single-active-AI, exact-link regressions, Django safety and launcher smoke.

Windows portable release workflow run `32996526842` is the remaining packaged-runtime gate as of this update. GitHub Release publication is now manual-only (`workflow_dispatch` + `publish_release=true`) so a push cannot publish an unaccepted EXE automatically.

## Phase50.A.1H — Admin Shell Stability — PRODUCTION VERIFIED
- footer normal/static flow,
- stable Admin shell,
- 290px right sidebar,
- internal-only active-menu scrolling,
- Velzon V2 on-demand filters/full-width lists preserved.

## Phase50.A.2A — Storefront Sales Profile Selector — PRODUCTION VERIFIED
- Product page exposes configured profile/size/build/weight/material/color/quality choices,
- `/store/api/variant-commerce-options/` remains authoritative,
- selected choice resolves to canonical ProductVariant ID and existing Cart/AddToCartForm.

## Phase50.A.2B — Immutable Checkout/Profile/Shipping Snapshot — GITHUB CI TESTED
Migration `store.0036_phase50_checkout_snapshot` adds immutable StoreOrderItem profile/selection/final-weight/shipping-weight/print-time snapshots and StoreOrder `insured_value` + `shipping_quote_snapshot`. Existing `0034` size/build/packaging/package snapshots are reused.

Runtime keeps mature Phase6 validation/coupon/inventory/address/notifications/payment authoritative, finalizes successful checkout inside an outer atomic boundary, uses `ProductVariant.effective_shipping_weight_grams`, preserves per-line package facts without inventing combined carton geometry, uses current ShippingMethod/rate rules as explicit fallback, and restores the session cart if finalization fails.

GitHub Actions `Phase50 Variant2 Gallery CI` run `32966720475` PASS on `fba0631e60bce1f6e3f622317b70c2f7f35d978f`. Production has not applied `0036` yet.

## Known operational incidents
- `ERR-49-052`: repeated Product Save/AI rebuilt the entire Products gallery; candidate correction is 49.3I.29 deferred refresh + 48-card paging.
- `ERR-49-053`: generic/silent Product Save could erase canonical source identity when both mirrored URL controls were temporarily blank; corrected by 49.3I.32 preserve/recover guard.
- `ERR-50-007`: Production remote fetch refspec is stale/tag-only; live `ls-remote` + explicit branch fetch to `FETCH_HEAD` + ff-only.
- `ERR-50-010`: avoid cPanel `/dev/fd` process substitution for backup enumeration.
- `ERR-50-011`: JSON verifier uses `python - <args>` + `json.load`.

Known warnings remain CKEditor4 maintenance/security debt, `store.W026` in-memory realtime debt and MySQL conditional-constraint warnings.

## Exact next work
1. Wait for/inspect Windows portable release workflow `32996526842`; do not claim packaged 8.8.2 acceptance before it passes.
2. Re-verify live GitHub branch HEAD, then on canonical Windows checkout run `catalog_center\RUN_PHASE49_3I31_SMART_AI_GATE.ps1` (now 3I.31+3I.32) with exact expected HEAD.
3. QA the previously damaged Product: Save or smart-AI should restore its exact historical source URL if history/discovery contains it; then verify Save/AI/image/publish actions cannot erase a populated source link.
4. Run controlled OpenRouter + AvalAI exact-link AI and selected-Product batch smoke; confirm no per-action full Products refresh.
5. Only after owner QA may Catalog Center 8.8.2 be published/accepted.
6. Separately, Web Production Phase50.A.2B still requires read-only Host/MySQL audit + fresh backup before `store.0036` migration/deploy.
