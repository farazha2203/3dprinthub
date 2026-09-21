# Phase50.A.2J - Standalone Sliced 3D Hero

Date: 2026-09-16
Release branch: `release/phase50-a2j-hero-20260915`
Production source at runtime acceptance: `859b9e77de1c8ecd5c53a9c395382b35579f78b4`
Status: `PRODUCTION_VERIFIED`

## Goal
Replace the public top Hero runtime completely with the standalone A2J Slicebox-style engine while keeping Django SSR copy/media authority and keeping the client-facing Store empty until the Windows operator intentionally republishes Products.

## Production state
- Host branch/source and live GitHub release head were exact at `859b9e77...` during acceptance.
- MySQL database is `sfkilvrs_EmiAdmin_3dprinthub`; migration plan count is zero.
- Store Product/Variant/ProductImage counts remain `0/0/0`.
- Exactly four safe source-backed Hero slides are active: assets `119,120,135,136`, sort `10,20,30,40`.
- Their persisted descriptions are short and bounded to the real `HomepageHeroSlide.description` max length.

## ERR-49-147
The first Production seed attempt failed with MySQL `Data too long for column description`. Schema drift was ruled out: both MySQL and the Django model use max length 480 and the failed transaction fully rolled back. A later Persian-sales runtime patch allowed up to 1200 characters and could produce 498 characters for asset 119. The fix derives the persistence bound from the model, applies it at suggestion/effective/pre-save boundaries, and gives the four release slides explicit short descriptions.

Regression evidence: focused 29/29 PASS, broad Hero 90/90 PASS, Python compile/Django check/no-model-drift/diff-check PASS. Rollback branch `backup/pre-err49-147-a2j-description-bound-20260916` points to `f5aa5af1e3cea39f6a04099eec6ad5696e30a3ad`.

## Rollback evidence
Verified Production backup root: `/home/sfkilvrs/3dprinthub-deploy-backups/20260916-030333-phase50-a2j-description-seed`. The baseline bundle, pre-seed bundle, MySQL gzip and Hero JSON all pass their verification/checksum gates. Baseline source recorded by the backup is `f5aa5af...`; pre-seed source is `859b9e77...`.

## Browser acceptance
Desktop 1440x900: HTTP 200, four slides, A2J CSS/JS loaded, no legacy Hero JS loaded, CTA target `/#order`, no broken Hero images/page errors/request failures. Manual Next created five real 3D cuboids with `transform-style: preserve-3d`, animation `p50j-cuboid-v`, changed the active slide, then removed the overlay.

Mobile 390x844: HTTP 200, four slides, fallback transition active, zero cuboids, active slide changed, document width exactly 390, no broken images/page errors/legacy Hero JS. `/store/` is HTTP 200 with zero Product links and no Product-detail path in its rendered HTML.

## Next exact gate
Return to the canonical Windows repository, re-read project governance there, verify the current canonical branch/head/worktree and Catalog SQLite backup/receiver readiness, then launch the exact tested Catalog Center runtime so the owner can republish Products/images intentionally. Do not deploy the broader canonical branch to Production merely to launch Windows functionality; A3/payment remains outside this Hero release.
