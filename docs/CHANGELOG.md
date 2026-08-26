# PROJECT CHANGELOG

Record meaningful changes only. Older detailed entries remain available in Git history.

## 2026-08-26 — Phase49.3I.32 Canonical Product Source URL Guard — Targeted CI PASS
- root cause confirmed in mature `ProductStudio.save()`: both mirrored URL controls could be temporarily blank and generic/silent Save would overwrite `source_url`, `normalized_url` and fingerprint with empty identity,
- silent Save is reused by close/refetch/AI/publish/layered Workspace actions, explaining why an unrelated button could appear to delete the Product link,
- added final additive `phase49_3i32_source_url_guard.py` after 49.3I.31; existing canonical URL is fed into both URL controls before the mature Save chain when both are blank,
- explicit non-empty main/spec URL edits remain supported,
- defensive post-save invariant restores canonical URL/normalized URL/fingerprint if a legacy layer still erases it,
- already damaged Products can recover the exact prior HTTP/HTTPS source URL locally from Product history, with matching `discovered_urls(source_code, external_id)` as fallback; no network or guessed/reconstructed URL,
- recovery is recorded in Product history/diagnostics,
- Catalog Center candidate remains `8.8.2` with build advanced to `2026.08.26.2`,
- Phase49.3I.31-32 targeted CI run `32996526852` PASS on runtime snapshot `2ca69c4928333fc15247b99014a8fe77d781b50b`, including source-link preserve/edit/recovery tests plus smart/batch AI, performance, exact-link, Django safety and launcher smoke,
- Windows portable release run `32996526842` remains the packaged-runtime gate,
- Windows release publication changed to explicit manual `workflow_dispatch` with `publish_release=true`; branch pushes build/test artifacts but cannot publish an unaccepted release automatically.

## 2026-08-26 — Catalog Center 8.8.2 Smart Link + Batch AI — GitHub Candidate
- added Phase49.3I.29 Windows performance base: 48-card Product presentation paging, full SQLite result preservation, deferred global Product refresh and exact saved mother Provider/Model execution without hidden Product model scans,
- added Phase49.3I.31 unified Product AI pipeline: exact Product URL validation/fetch, canonical source identity, safe source facts flattened into one heading-structured text body, Persian content/SEO generation and selected-image metadata/finalization,
- normal Product AI transmits only `source_title` + one `source_description` text field; raw HTML, auth/cookies/secrets and unrelated pricing/stock/workflow state stay local,
- main Product AI/link actions converge on the same grounded runtime boundary,
- Products Explorer supports selected-product batch AI using each Product's own exact source URL, isolated per-item errors/cancel and one global Products refresh at batch end,
- mother AI settings remain authoritative for AvalAI/OpenRouter/Google/OpenAI; no cross-provider fallback,
- release identity advanced to candidate `8.8.2`; current correction build is `2026.08.26.2`,
- Windows release workflow includes Phase49.3I.29/31/32 regressions and launcher/portable gates,
- `ERR-49-052` records the global Product refresh storm prevention rule.

## 2026-08-26 — Phase50.A.2B Immutable Checkout/Profile/Shipping Snapshot — GitHub CI Tested
- added migration `store.0036_phase50_checkout_snapshot`,
- StoreOrderItem now has immutable sales-profile name/key/label, selection mode/value, final weight, effective shipping weight and print-time snapshots,
- existing `0034` StoreOrderItem size/build/packaging-weight/package-dimension fields are populated during successful checkout finalization,
- StoreOrder now has `insured_value` and normalized `shipping_quote_snapshot`,
- added `store/phase50_checkout_snapshot.py` following the additive runtime-field pattern rather than rewriting mature `store/models.py`,
- Cart summary uses `ProductVariant.effective_shipping_weight_grams`, including packaging when no explicit shipping-weight override exists,
- mature Phase6 checkout remains authoritative for validation, coupon, inventory reservation, address, notifications, payment creation and redirect,
- successful checkout is wrapped in an outer atomic boundary and finalized before commit; finalizer failure restores session cart and rolls back DB writes,
- normalized shipping snapshot uses current `ShippingMethod`/rate rules as explicit `shipping_method_fallback`; no external carrier API is claimed,
- insured value is frozen as merchandise value after order discount,
- per-line/unit package dimensions are preserved; combined carton geometry is deliberately not invented,
- pending StorePayment amount is synchronized if effective shipping weight changes final fallback shipping fee,
- integration regressions prove profile/package/weight snapshotting, packaging-aware shipping weight, payment synchronization and immutability after later Variant changes,
- GitHub Actions `Phase50 Variant2 Gallery CI` run `32966720475` PASS on snapshot `fba0631e60bce1f6e3f622317b70c2f7f35d978f`,
- Production remains at `c283864290f9c989a9fcdf24ee8eef519560e917`; `0036` is not yet applied and requires fresh Production backup/migration gate.

## 2026-08-26 — Phase50.A.1H + Phase50.A.2A Production Verified
- Production fast-forwarded from `0f7f22fdcef4b8e288e0530bfe74f5b2411599dc` to `c283864290f9c989a9fcdf24ee8eef519560e917` using explicit verified branch fetch to `FETCH_HEAD`,
- fresh rollback backup `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-143650`,
- MySQL `sfkilvrs_EmiAdmin_3dprinthub` verified; `store.0034` and `store.0035` applied; no migration executed,
- deployed Admin shell stability and Storefront sales-profile selector,
- Home/Store/Admin/Product/new static resources HTTP 200,
- Product HTML selector and Variant commerce API verified,
- public Home private imported-media refs = 0,
- final Production worktree clean at `c283864...`.

### Deployment-verifier incidents
- cPanel Bash process substitution `/dev/fd` failure corrected with Python enumeration (`ERR-50-010`),
- JSON verifier execution mistake corrected with `python - <json-path> ...` + `json.load` (`ERR-50-011`).

## 2026-08-26 — Phase50.A.1H Admin Shell Stability + Phase50.A.2A Storefront Profile Selector
- Admin CI `32958276378` PASS on `27335832e90c35dd95bb8a686dd89d1efd46dc8f`,
- Storefront CI `32958296546` PASS on `e3c57311c0c3980befeaf6012f3bb8fc502333bc`.

## 2026-08-26 — Phase50.A.1G Velzon Operator Surface V2
- replaced permanent legacy Django filter column with on-demand drawer and full-width lists,
- CI `32955310832` PASS on `3687d0922959fca53f2118be6dacd32639159346`.

## 2026-08-26 — Phase50.A.1F Business Admin Navigation / Product Admin 500 Fix — Production Verified
- fixed Product changelist 500 caused by SafeString numeric formatting,
- reorganized Admin by business domains,
- deployed/verified at `bc7b97f9c63432b8105f52f61cf5cdae1369689b` with backup `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-125848`.

## 2026-08-26 — Phase50.A.1E Production Deployment Verified
- deployed `9cfbc54ed4196144864b5f4201976d8466a88134`,
- backup `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-114327`,
- `0034`/`0035` applied and HTTP/private-media gates PASS,
- stale remote-tracking incident fixed through explicit `FETCH_HEAD` (`ERR-50-007`).

## 2026-08-26 — Phase50.A.1E Unified Product Admin Workspace
- business-ordered Product workspace preserving mature Product/Profile/Variant/SEO contracts,
- CI `32941662288` PASS on `f34eaa3bbad965b2092279291ff8adf93f3d908e`.

## 2026-08-25 — Phase50.A.1C Admin Media / Mobile / SEO / Windows Dimensions
- safe ImportedPrintAsset Admin public-media resolver, compact mobile Hero, homepage SEO audit and Windows image dimensions; CI PASS.

## 2026-08-25 — Phase50.A.1B Product Gallery + Variant 2.0 Foundation
- Product gallery/lightbox, Variant2 size/build/package fields, StoreOrderItem snapshots, `store.0034`; CI PASS.

## 2026-08-25 — Catalog Center Windows v8.8.1 Final Portable Release
- released `3DPrintHub-CatalogCenter-v8.8.1.exe`, build `2026.08.25.2`, SHA256 `c32f37affcbd2c6ffacb803247daf804a490fecd7c8162bc37c2729a2197e990`.

## 2026-08-25 — Phase50.A.1 Admin Storefront / Hero Parity
- Product/imported-asset Hero controls and Storefront/Coupon/Shipping/Pricing/address Admin surfaces.

## 2026-08-25 — Phase50.A Admin Command Center
- authenticated `/admin/command-center/` organized around Sales, Treasury, Accounting/Ledgers, Purchasing and Inventory/Production.

## 2026-08-25 — Phase49.3I Production closeout
- Product-owned public Hero media, structured web Product presentation and verified Production deploy; imported Catalog working-media remained private.
