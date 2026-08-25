# PROJECT ROADMAP

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Epic: `Phase49 — Unified Product / Slider / Catalog Sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.30 — Production Hero Product-Media Ownership`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL TEST NEXT`
Production Application Commit: `d27489f1c2e1d36e75fdadfa8ab24660d8bec720`

## Permanent Delivery Order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → WINDOWS PULL --FF-ONLY → LOCAL TEST → LOCAL PUBLISH/WEB E2E → OWNER APPROVAL → READ-ONLY HOST VERIFY → BACKUP → DEPLOY FROM GITHUB → PRODUCTION VERIFY → DOCUMENT`

## Completed
- 49.3I.29 storefront Product presentation deployed and Production verified.
- Production MySQL migration/backup gate passed.
- Home, Store and Product returned HTTP 200.
- first real Catalog Site Publish produced a healthy Product page and Product-owned media.

## Current Production Defect
Homepage Hero text renders but selected slide images return 404 under `/media/store/imported-models/gallery/...`. Local works because DEBUG serves all media. Production intentionally serves Product-owned Store media only.

## 49.3I.30 Contract
- keep ImportedPrintAssetImage as internal selection/audit state,
- public Hero resolves to matching Product-owned gallery image by filename,
- if exact match is unavailable, use Product main image,
- only use remote source as final fallback,
- never widen Production public-media routing to expose imported working media,
- no migration and no Catalog batch-format change.

## Immediate Priority
1. Pull live feature branch on Windows with clean worktree.
2. Run Django check + migration dry-run + `website.test_phase49_3i30_hero_media_ownership`.
3. Visual QA Local Hero for the newly published cake-stand slides.
4. After owner approval, deploy exact tested GitHub HEAD to Production; no migration expected.
5. Passenger restart and verify each Hero image URL returns HTTP 200 and uses `/media/store/products/...`.
6. Re-publish/update one Catalog Product to verify Product/Slider identity and media remain idempotent.
7. Mark Phase49.3I accepted, then proceed to Store payment phase.

## Production Warning Debt
- CKEditor4 warning remains open.
- in-memory realtime `store.W026` remains open.
- MySQL conditional unique constraints remain known non-blocking warnings.
