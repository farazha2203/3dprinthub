# Phase50.A.2L — Site Priority Release

Date: 2026-09-19
Status: `ERR-49-173 MEDIA HOTFIX BASE ba05c7fc / ERR-49-174 PRICING LOCAL_TESTED / COMMIT+TUNNEL DEPLOY NEXT`

## Requested delta
- Keep the owner-approved Tympanus Slicebox Example-4 engine but enlarge the public stage to a 1280px responsive Product presentation.
- Prefer active Product-backed curated slides over source-only fallback slides; show canonical Product SEO copy/schema and navigate media/caption to Product detail.
- Keep the Product Admin 504 fix by leaving the unbounded ProductVariant inline removed.
- Make same-identity Windows Republish atomic and complete: Product/content/SEO/price range/current media filenames+bytes/current Profiles/Variants/material/brand/manufacturer/color/weights/time/dimensions/pricing inputs must pass post-import parity before ACK success.
- Preserve Product identity, historical physical media, compatibility, FAQ/Profile editing, Store ordering and existing DB schema.

## Safety / rollback
- Current verified Production baseline: `release/phase50-a2j-hero-20260915 @ c04539acfc6dd456699079edf206de019bf346e2`.
- Current local rollback branches: `backup/pre-a2l-hero-scale-seo-20260919` preserves the earlier Hero baseline; `backup/pre-err49-173-media-path-20260919 @ c04539acfc6dd456699079edf206de019bf346e2` is the immediate rollback for this media-path hotfix.
- No migration, requirements or settings delta is allowed.
- Deployment is dedicated reverse-tunnel only and must create verified source/.env/static rollback evidence before ff-only promotion.

## Local evidence
- Python compile + Node syntax PASS.
- Django check PASS with known CKEditor warning only; `makemigrations --check --dry-run` reports no changes.
- Focused Hero/Republish/Profile/Filament API/Admin/Visibility regression: 37/37 PASS.
- E2E proves exact Product SEO basename, same-byte idempotence and full rollback on deliberate post-import parity mismatch.
- Real read-only evidence: Catalog #625 maps to Site #39; existing ACK revision reached 5 despite shallow verification, proving ERR-49-172.
- Production read-only Hero evidence: source-only Crystal Summit plus Product #35/#36 exist; Product-first query will select only #35/#36.
- Deploy runner Git-Bash syntax, Node syntax and `git diff --check` PASS.
