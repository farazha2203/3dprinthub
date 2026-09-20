# Phase50.A.2V — Windows Image Authority Hardening

Status: **ACTIVE — SOURCE PUSHED / EXACT-SHA QT RUNNING / OPERATOR SITE-SELECTION REQUIRED**

## Scope
- Preserve A2U v8.9.11 as the Windows UI ancestor.
- Separate temporary bulk-edit selection from persisted `ارسال سایت` selection.
- Require every Site-selected image to belong to canonical `images_json`.
- Preserve persisted Site-selected local images across source refetch, including legacy numbered files.
- Re-publish #625 exactly once only after the owner makes the visual Site-image choice in A2V.

## Source checkpoint
- Branch: `wip/phase50-a2v-image-authority-20260920`
- Source commit: `4e69ed6a5c0996c7249830fbe029cd01460ad5b1`
- GitHub exact-SHA read-back: PASS
- Stable Image/SEO/Packaging/Republish regression: **72/72 PASS**
- `git diff --check`, py_compile, `RUN_QT.ps1 -VerifyOnly`: PASS
- Exact-SHA Qt runtime launched from repository-owned runner.

## #625 evidence and repair
- Local #625 / Site #39 is currently revision 10.
- Revision 10 carried the same final image SHA values as the prior live media.
- Pre-repair state had `selected_images_json=[04.webp,05.webp]` outside canonical `images_json`.
- New fail-closed gate correctly rejected that state before batch creation.
- Catalog rollback: `D:\projects\3dprinthub-backups\phase50-a2v-image-authority-20260921-005619\catalog-before-a2v.sqlite3`
- Backup integrity: PASS; SHA256 `20bd5c1d6b776c14e90d9aa91a9866b909121614d9e042faeb252cbac75c0e9e`.
- Evidence-based repair changed only canonical image authority to include the already-persisted Site selections; selected set, primary, SEO metadata, Site identity and revision were unchanged.
- Post-repair #625 media gate: PASS; no republish was triggered.

## Production baseline
- Production source remains clean at `03042d0430ee6e688c992c875f12edc969df103d`; A2V is Windows-only.
- Site Product #39 profile revision: 10.
- Current live image SHA256: `cf6f0422f0cde915e9203ddbca6564df694fb4b6a97320e1af0e7f4117c68fff` and `28d50b4b482e1d653e6eff3deba448525c8ecf1a59d5f5f1d5f61291fefe67e5`.
- Exactly 3 active current Variants remain authoritative.

## Remaining gate
Owner visually selects the intended new image(s) with `ارسال سایت` in the running exact-SHA A2V UI → verify Local state/SEO finalization → fresh pre-publish rollback → one controlled same-identity republish → Local/Batch/Production SHA parity → public HTTP/browser verification → final docs closure.
