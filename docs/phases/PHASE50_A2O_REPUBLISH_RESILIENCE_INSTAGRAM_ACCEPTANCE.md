# PHASE50.A.2O — Re-publish Resilience + Instagram Acceptance

Status: LOCAL_TESTED / GITHUB+REAL ACCEPTANCE NEXT
Date: 2026-09-19

## Goal
Close the last Windows same-Product retry reliability gap, complete #625 authoritative Site acceptance, then publish exactly one SEO-complete Instagram Feed + companion Story from that verified Site revision.

## Hero gate
Production is already exact clean 36a69e76f9cd553273862ee400f9391573f3dd01. Hero cache key is 50.9.0, legacy shadow DOM/runtime is removed, desktop Slicebox remains native 3D and mobile has nonzero image-priority sizing.

## Re-publish resilience
A failed Bridge/receiver transaction records its receipt/error but cannot erase the last verified Site asset/Product/slider ids, revisions or successful public ACK. Only a confirmed publish may replace those stable identity fields.

## #625 acceptance
Restore only the stable Site linkage from verified pre-failure Catalog evidence, preserve all current edited Product/profile/media fields, create a fresh Catalog rollback, then publish through the official Windows Batch/FTP/Bridge path. Require same Site Product #39, current revision, exactly three active CC-P39 Variants, zero stale active legacy Variants, current weight/material/time/pricing and exact current ProductImage/public media.

## Instagram acceptance
Site-first only. Derive Buffer-compatible PNG assets from current verified Site media; preserve canonical source URLs in audit. Feed requires Product SEO title/description, factual bullets/specs, non-empty per-image ALT, bounded relevant hashtags, direct UTM Product URL and nationwide shipping CTA. Companion Story requires the approved 1080x1920 Gold/Navy IRANSans style and Product link. Feed and Story provider receipts/external ids are mandatory. Highlight target is recorded; final Highlight placement remains operator-required because Buffer has no Highlight mutation.

## Local gates
- Site-publish module: 19/19 PASS.
- Instagram feed/Buffer/Story/social/publish: 27/27 PASS.
- git diff --check PASS.

## Safety
No duplicate social post for a receipted Site revision. No Production source edits outside GitHub release flow. Fresh Catalog backup before linkage repair/re-publish. Historical Store Variants remain stored but inactive; no destructive order/FK cleanup.
