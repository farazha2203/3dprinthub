# Phase50.A.2L — Site Priority Release

Date: 2026-09-19
Status: `LOCAL_TESTED / GITHUB+PRODUCTION NEXT`

## Requested delta
- Promote the owner-approved Tympanus Slicebox Example-4 homepage Hero from the Production-based A2K lineage.
- Remove only the unbounded ProductVariant inline that caused Product Admin change-page 504 responses.
- Preserve Product gallery, compatibility, FAQ/Profile editing, Store ordering, database state and Windows Catalog behavior.

## Safety / rollback
- Production baseline: `release/phase50-a2j-hero-20260915 @ 12e319ace1eb55c114d7117e1b5a2fa170b410ab`.
- Release base/rollback: `84d1a87c4ea632823743b9cc1c5fe3ba81b08843`; branch `backup/pre-a2l-site-priority-release-20260919`.
- No migration, requirements or settings delta is allowed.
- Deployment is dedicated reverse-tunnel only and must create verified source/.env/static rollback evidence before ff-only promotion.

## Local evidence
- Node syntax PASS.
- Django check PASS with known CKEditor warning only.
- `makemigrations --check --dry-run` reports no changes.
- Hero + Product Admin focused regression: 25/25 PASS.
- Deploy runner Bash syntax and `git diff --check` PASS.
