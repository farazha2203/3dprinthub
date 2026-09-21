# Phase50.A.2Z — Image + Social Authority Hotfix

Status: LOCAL_TESTED / PHYSICAL SEO RENAME ADDED / COMMIT-PUSH + EXACT-SHA RUNTIME + REAL #609 ACCEPTANCE NEXT
Date: 2026-09-21
Branch: `wip/phase50-a2z-image-social-authority-20260921`
Baseline: `f5f401167d14e560e53fc9cdc292024c67174459`

## Owner-reported failures
- Product #609 selected Local media `local://04.webp` and `local://05.webp` were outside canonical `images_json`, so Site publish failed closed.
- UI could show the same SEO filename for two query-variant source URLs because metadata lookup collapsed them to one canonical asset key.
- Instagram/Buffer failed before publish because branch `social-assets-buffer` was already registered at another Git worktree.

## Correct contract
- A real trusted Product-local card checked for Site becomes canonical Product media at the same Stage-3 save boundary.
- Exact source URL identity wins metadata/SEO-slot lookup; canonical-key fallback is compatibility-only.
- Final physical publish media lives under `seo_images`, uses unique numbered SEO WebP names, and Batch copies those exact files/bytes.
- Social provider media reuses an already-registered worktree for its branch instead of attempting a duplicate `git worktree add`.
- Applying Product image SEO now promotes the actual selected Product-local physical file to the unique SEO WebP basename under `images/`; the old bytes are preserved under `source_originals/`.
- Remote source URL remains provenance, while exact `source_local_file` points to the SEO-named Product-local file. Local `local://` identities are remapped to the SEO basename.
- Duplicate physical SEO basenames are forbidden; numbering remains deterministic `-01, -02, ...`.

## Local verification
- New focused image/social/publish gate: 9/9 PASS.
- Broad Image/Publish/Windows/Social gate: 113/113 PASS.
- Two historical UI assertions first failed broad gate and reproduced identically on clean baseline `f5f40116...`; assertions were aligned to the already-accepted Site-selection/source-refresh UI contract.
- `git diff --check`, touched Python compile (7 files), and Qt VerifyOnly PASS.

## Real #609 checkpoint
- Fresh rollback: `phase50-a2z-609-pre-repair-20260921-194148`; SQLite integrity OK + full media manifest.
- Application-level repair completed: selected=5, canonical=5, physical SEO names `-01..-05.webp`, original selected bytes archived.
- Site Product remains #42 revision 1; no Site publish yet.
- ERR-49-218 fixes false source drift introduced by the new physical SEO boundary.
- Source-drift/promotion/Batch 3/3 and Image+Site Publish 51/51 PASS.

## Exact next
Compile/diff/Qt VerifyOnly -> commit/push ERR-49-218 fix -> verify Local=GitHub -> exact-SHA Qt -> explicit mark-ready #609 -> verify five-image Batch -> verify tunnel/Host/Production + fresh rollback -> one same-identity Site #42 republish -> strict five-image filename/SHA/HTTP parity -> changed-revision Instagram Feed+Story acceptance -> update docs.

## Phase after this hotfix
Continue A2Z Catalog Slider completeness/backfill and final Windows operator acceptance; then A2Z-S changed-revision Social rollout.
