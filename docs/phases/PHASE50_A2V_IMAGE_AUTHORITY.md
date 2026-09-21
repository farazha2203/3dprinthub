# Phase50.A.2V — Windows Image Authority Hardening

Status: **PRODUCTION_VERIFIED — CLOSED**

## Scope
- Preserve A2U v8.9.11 as the Windows UI ancestor.
- Separate temporary bulk-edit `ویرایش` from persisted `ارسال سایت`.
- Require every Site-selected image to belong to canonical `images_json`.
- Preserve persisted Site-selected local images across source refetch, including legacy numbered files.
- Prove one real same-identity #625 → #39 republish with byte-level parity.

## Source acceptance
- Branch: `wip/phase50-a2v-image-authority-20260920`
- Tested source commit: `4e69ed6a5c0996c7249830fbe029cd01460ad5b1`
- Prior docs checkpoint: `318fb410c063df660767a9e8ff66d0847a765f03`
- Stable Image/SEO/Packaging/Republish regression: **72/72 PASS**
- `git diff --check`, py_compile, `RUN_QT.ps1 -VerifyOnly`: PASS
- A wider legacy probe's four failures reproduce identically on clean A2U baseline and are not A2V regressions.

## Revision-11 acceptance
- Persisted Site selection: exactly `local://04.webp`
- Primary: `local://04.webp`
- SEO filename: `mini-articulated-skeletal-spinosaurus-3d-print-01.webp`
- SEO metadata: ready; final file exists; bytes = 36,162
- Batch: `desktop_catalog_v85_20260921_081158`
- Batch UUID: `cb51fb28-acd2-45a7-8a86-40ea5268614c`
- Site identity preserved: Product #39
- Revision: 10 → 11 exactly once
- ACK: `status=updated`, `republish_parity.ok=true`, media_count=1, profile_count=3

## Byte and Production parity
- Local final SEO SHA256: `cf6f0422f0cde915e9203ddbca6564df694fb4b6a97320e1af0e7f4117c68fff`
- Batch image SHA256: exact same value.
- Production stored main image/ProductImage SHA256: exact same value.
- Fresh public HTTPS download SHA256: exact same value, 36,162 bytes.
- Public Product: HTTP 200 and contains the revision-11 image filename.
- Public image: HTTP 200 / `image/webp`.
- Production has exactly one authoritative ProductImage and exactly three active current CC Variants.
- Active Variant values remain 110 g material, 60 g final, 180 min and 1,095,000 / 1,215,000 / 1,215,000 Toman.
- Production source remains clean at `03042d0430ee6e688c992c875f12edc969df103d`; no A2V Host source deploy, migration, collectstatic or restart occurred.

## Rollback evidence
- Verified revision-10 A2V rollback: `D:\projects\3dprinthub-backups\phase50-a2v-image-authority-20260921-005619\catalog-before-a2v.sqlite3`
- Revision-10 backup integrity PASS; SHA256 `20bd5c1d6b776c14e90d9aa91a9866b909121614d9e042faeb252cbac75c0e9e`.
- The planned fresh snapshot immediately before revision 11 was not captured before the publish completed; this is recorded as ERR-49-199 and is not represented as PASS.
- No revision 12 was created to recreate ordering.
- Fresh post-revision-11 snapshot: `D:\projects\3dprinthub-backups\phase50-a2v-post-rev11-20260921-081557\catalog-after-rev11.sqlite3`
- Post-revision-11 snapshot integrity PASS; SHA256 `1f6ecd4c9250ed9b46e612489294fea0f1fe7c6b57a6a02aa1493b738bc72869`.

## Closure
A2V is Production-verified and no further #625 publish is required. Future Product publishes must take and integrity-check the rollback snapshot as a programmatic precondition before the publish action.
