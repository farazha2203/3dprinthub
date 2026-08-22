# PROJECT ROADMAP

Last Updated: 2026-08-22
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`

## Goal
Unified 3DPrintHub catalog workflow from Windows intake/edit/AI/SEO/pricing/hero through controlled Batch/Bridge sync into Django Store/Admin, with safe Local/Production separation and auditable operations.

## Epic49 Path
- [x] 49.2A / 49.2B / 49.2C foundations
- [x] Epic49 unified product/slider sync
- [x] 49.3A readiness
- [x] 49.3B guided AI / hero / diagnostics
- [x] 49.3C operator recovery + Persian content integrity
- [x] 49.3D workflow hardening + runner hotfix
- [x] 49.3E AI task completion/recovery
- [x] 49.3F product intelligence / dynamic pricing / AI UX
- [x] 49.3F runtime redaction + 49.3F.1 native capture hotfix
- [x] 49.3G workspace usability + AI provenance — GitHub CI complete
- [ ] 49.3H SEO Execution Console + AI Cost Ledger + Controlled Image Acquisition — IN_PROGRESS

## Phase49.3H Requested Delta
- unified visible execution steps/result/error for every SEO/AI action
- result drawer/history and sanitized log linkage
- per-product AI/SEO cost aggregation and publish-time internal receipt
- default image acquisition limit 10, operator-selectable, hard max 20
- cap both downloaded files and persisted/selected image lists

## Must Not Regress
- selected-image-only + text-only image SEO
- manual override/provenance rules
- dynamic pricing source of truth
- Local vs Production publish separation
- revision/idempotency guards
- Persian content integrity
- Hero/Product sync contracts
- secure secret handling

## Gates Before Production
1. GitHub implementation + regression tests
2. GitHub CI + Full Phase49/Django regression
3. Windows `git pull --ff-only`
4. repository Local Gate runner
5. Manual Visual/Data QA
6. real LOCAL PUBLISH ONLY
7. Local Django E2E
8. explicit user approval
9. verified production backup/deploy/migrate/collectstatic/restart/smoke

## Deferred / Separate
- `/api/v1/catalog/sitemap/` local 404 root cause
- CKEditor4 debt
- Production Redis/realtime architecture warning

## Next Recommended Task
Complete Phase49.3H on GitHub, then run CI. Production is not part of this step.
