# PROJECT CHANGELOG

Record meaningful changes only. Older detailed entries remain available in Git history.

## 2026-08-26 — Phase49.3I.32 Canonical Product Source URL Guard — Packaged Windows CI PASS
- root cause confirmed in mature `ProductStudio.save()`: both mirrored URL controls could be temporarily blank and generic/silent Save would overwrite `source_url`, `normalized_url` and fingerprint with empty identity,
- silent Save is reused by close/refetch/AI/publish/layered Workspace actions, explaining why an unrelated button could appear to delete the Product link,
- added final additive `phase49_3i32_source_url_guard.py` after 49.3I.31; existing canonical URL is fed into both URL controls before the mature Save chain when both are blank,
- explicit non-empty main/spec URL edits remain supported,
- defensive post-save invariant restores canonical URL/normalized URL/fingerprint if a legacy layer still erases it,
- already damaged Products can recover the exact prior HTTP/HTTPS source URL locally from Product history, with matching `discovered_urls(source_code, external_id)` as fallback; no network or guessed/reconstructed URL,
- recovery is recorded in Product history/diagnostics,
- Catalog Center candidate remains `8.8.2`, build `2026.08.26.2`,
- targeted Phase49.3I.31-32 CI run `32996526852` PASS on `2ca69c4928333fc15247b99014a8fe77d781b50b`,
- first Windows packaged run `32996526842` failed only on one stale legacy test literal expecting 8.8.1; new source-link tests were already PASS,
- replaced stale release literal with runtime-version == package-manifest-version contract,
- Windows packaged rerun `32997106056` PASS on `5208aa4dd3b070e9a7c7c6d6dde9b60569879631`: full regression, launcher composition, source URL invariant, one-file EXE build/self-verify, release-manifest/SHA256 verification and immutable artifact upload PASS,
- Actions artifact `3DPrintHub-CatalogCenter-v8.8.2` created as artifact ID `9617048629`,
- automatic public release publication disabled; release is explicit/manual only after owner Local QA.

## 2026-08-26 — Catalog Center 8.8.2 Smart Link + Batch AI — GitHub Candidate
- Phase49.3I.29 Windows performance base: 48-card Product presentation paging, full SQLite result preservation, deferred global Product refresh and exact saved mother Provider/Model execution without hidden Product model scans,
- Phase49.3I.31 unified Product AI: exact Product URL validation/fetch, canonical source identity, safe source facts flattened into one heading-structured text body, Persian content/SEO and selected-image metadata/finalization,
- normal Product AI transmits only `source_title` + one `source_description` text field; raw HTML, auth/cookies/secrets and unrelated pricing/stock/workflow state stay local,
- main Product AI/link actions converge on the same grounded runtime boundary,
- Products Explorer supports selected-product batch AI using each Product's own exact source URL, isolated per-item errors/cancel and one global Products refresh at batch end,
- mother AI settings remain authoritative for AvalAI/OpenRouter/Google/OpenAI; no cross-provider fallback.

## 2026-08-26 — Phase50.A.2B Immutable Checkout/Profile/Shipping Snapshot — GitHub CI Tested
- added migration `store.0036_phase50_checkout_snapshot`,
- StoreOrderItem immutable profile/selection/final-weight/shipping-weight/print-time snapshots,
- existing `0034` size/build/packaging-weight/package-dimension snapshots populated during successful checkout,
- StoreOrder `insured_value` + normalized `shipping_quote_snapshot`,
- mature Phase6 validation/coupon/inventory/address/notifications/payment remains authoritative,
- checkout finalization uses outer atomic boundary, effective shipping weight and ShippingMethod fallback without inventing external carrier contracts,
- integration regressions prove snapshot immutability and payment/shipping synchronization,
- `Phase50 Variant2 Gallery CI` run `32966720475` PASS on `fba0631e60bce1f6e3f622317b70c2f7f35d978f`,
- Production remains at `c283864290f9c989a9fcdf24ee8eef519560e917`; `0036` not yet applied.

## 2026-08-26 — Phase50.A.1H + Phase50.A.2A Production Verified
- Production fast-forwarded to `c283864290f9c989a9fcdf24ee8eef519560e917`,
- rollback backup `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-143650`,
- MySQL `store.0034` + `0035` applied; no new migration executed,
- Admin shell stability and Storefront sales-profile selector deployed and verified,
- Home/Store/Admin/Product/static/Variant API healthy; public Home private imported-media refs = 0.

### Deployment-verifier incidents
- cPanel `/dev/fd` process-substitution failure corrected with Python enumeration (`ERR-50-010`),
- JSON verifier execution mistake corrected with `python - <json-path> ...` + `json.load` (`ERR-50-011`).

## 2026-08-26 — Phase50.A.1H Admin Shell Stability + Phase50.A.2A Storefront Profile Selector
- Admin CI `32958276378` PASS on `27335832e90c35dd95bb8a686dd89d1efd46dc8f`,
- Storefront CI `32958296546` PASS on `e3c57311c0c3980befeaf6012f3bb8fc502333bc`.

## 2026-08-26 — Phase50.A.1G Velzon Operator Surface V2
- on-demand filter drawer/full-width lists,
- CI `32955310832` PASS on `3687d0922959fca53f2118be6dacd32639159346`.

## 2026-08-26 — Phase50.A.1F Business Admin Navigation / Product Admin 500 Fix — Production Verified
- fixed Product changelist SafeString numeric-formatting 500,
- deployed/verified at `bc7b97f9c63432b8105f52f61cf5cdae1369689b`.

## 2026-08-26 — Phase50.A.1E Production Deployment Verified
- deployed `9cfbc54ed4196144864b5f4201976d8466a88134`,
- backup `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-114327`,
- `0034`/`0035` applied; HTTP/private-media gates PASS.

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
