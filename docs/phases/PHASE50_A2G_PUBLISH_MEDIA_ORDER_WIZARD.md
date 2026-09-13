## 2026-09-13 Operations support checkpoint - reverse Host management

A2G source is now promoted on the Host: read-only FTPS Git evidence shows Production branch HEAD `a320a0d346e4be573504978b23d197dc08f8bc2c`. Public Home, Store and the A2G selector JS/CSS currently return HTTP 200. The earlier deploy runner stopped during immediate post-restart HTTP verification; authenticated Bridge/readiness plus exact Host worktree acceptance still must be repeated before declaring A2G `PRODUCTION_VERIFIED`.

To remove repeated cPanel operator dependency, the proven Asal shared-cPanel reverse-management transport is being adopted without changing business/runtime authority. Windows side is ready (`PrintHubTunnel`, loopback `22024`, source restriction `89.39.208.237/32`); repository bridge/bootstrap scripts are local-tested and pushed at `180fe16c0e296156ef38ffc00a042c329318ff7c`. Host E2E onboarding is the next gate. This transport introduces no migration or Product/media write and does not permit direct permanent source edits on Production.

# Phase50.A.2G — Publish-ready Media + Professional Order Wizard

Date: 2026-09-12
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Status: `HOST SOURCE PROMOTED / PUBLIC HTTP RECOVERED / AUTHENTICATED FINAL ACCEPTANCE + ONE PRODUCT NEXT`
Rollback: `backup/pre-phase50-a2g-publish-media-order-wizard-20260912` → `02f654b0204266c2d7d329caf85b781c76a56a62`
Production pre-A2G baseline: `7d0b3df03c3657106ebaf86d5f9123ba262495a5`; current Host source: `a320a0d346e4be573504978b23d197dc08f8bc2c`

## Goal
Before broad Product publishing, make the complete Product path trustworthy: finalized SEO media on Windows, byte-accurate Batch transfer, idempotent Host import, and a clear responsive customer ordering wizard.

## Requested delta
- a Product cannot become publish-ready without current finalized SEO WebP media;
- the exact finalized WebP name and bytes must reach the Batch and Host;
- re-publish must refresh genuinely changed media but remain idempotent for identical bytes;
- the customer wizard remains size → color → compatible material → print quality while gaining professional progress/guidance and responsive behavior;
- server ProductVariant price, stock, weight, time and orderability remain authoritative.

## Touched surfaces
- Windows Catalog publish gate and Batch 8.5 media packaging;
- Django Catalog importer current-batch media reconciliation;
- Storefront guided selector JS/CSS and browser QA;
- focused Windows/Django regression tests.
## Media contract
Every selected Product image must have complete current metadata, current SEO signature, a unique `.webp` filename under `seo_images`, a valid WebP payload and matching SHA256. Publish-time download/JPG fallback is forbidden. The Batch copies the finalized SEO artifact byte-for-byte.

The Host treats an explicit current-Batch media mapping as authoritative. Different incoming bytes refresh the existing imported image; identical bytes do not call FileField save again, preventing storage suffix churn and false visual revisions. Historical media is not destructively deleted.

Manifest `desktop_product_id` is propagated into the editorial data before canonical Profile sync so first import and later re-import share one Desktop/Site identity.

## Wizard contract
- visible four-step progress and per-step guidance;
- active/completed/ready ordering states;
- keyboard navigation and meaningful focus behavior;
- touch-friendly controls and mobile sticky cart;
- dedicated desktop/tablet/mobile responsive layouts with no horizontal overflow;
- native Variant selector/API-failure fallback remains intact;
- ambiguous visible tuples still require explicit final canonical Variant choice.

## Must not touch
Historical paid orders, pricing authority, inventory authority, Coupon/VAT, manual non-Desktop Variants, secrets, Production migrations, external carrier/gateway contracts and private vendor assets.
## Local verification
- Catalog publish/media regression: 10/10 PASS;
- Django import + Filament/Profile regression: 16/16 PASS;
- guided selector Node state machine: 8/8 PASS;
- Playwright: desktop/tablet/mobile, progress, keyboard, touch, cart, fallback, stock, ambiguity and >100 Variants PASS;
- touched Python compile PASS;
- `manage.py check` PASS with only known CKEditor warning;
- `makemigrations --check --dry-run`: no changes;
- `git diff --check`: PASS.

## Safety
No Django migration is introduced. Local Catalog media is only read/copied by publish packaging. A2G source/importer changes are now present in Host Git at `a320a0d...`; public Home/Store/new JS/CSS are HTTP 200. Authenticated worktree/Django/migration/readiness acceptance is still required before declaring Production verified. Store 0036–0042 + Website 0024 were previously verified applied.

## Next exact gate
1. Repository state/request/error docs updated for A2G;
2. exact runtime `e76e555beef7ed549912b89ec2d9d4eecd9c6d8c` is committed/pushed and verified on live GitHub;
3. checksum-backed canonical Windows gate PASSed on that exact SHA and Catalog Center launched;
4. Host source promotion is already at `a320a0d...`; do not rerun the old `7d0b3df...` baseline deploy;
5. complete reverse-tunnel E2E and authenticated Host identity/worktree/Django/migration/readiness verification;
6. publish exactly one controlled Product Windows → Production and verify Product/Profile/Variant/WebP/public page/strict ACK before bulk publish.