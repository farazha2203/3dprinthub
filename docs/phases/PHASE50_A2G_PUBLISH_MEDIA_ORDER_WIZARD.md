# Phase50.A.2G — Publish-ready Media + Professional Order Wizard

Date: 2026-09-12
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Status: `GITHUB_UPDATED / CANONICAL WINDOWS GATE PASS / QT LAUNCHED / HOST DEPLOY NEXT`
Rollback: `backup/pre-phase50-a2g-publish-media-order-wizard-20260912` → `02f654b0204266c2d7d329caf85b781c76a56a62`
Production baseline: `7d0b3df03c3657106ebaf86d5f9123ba262495a5`

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
No Django migration is introduced. Local Catalog media is only read/copied by publish packaging. Host importer changes are not on Production yet. Production remains on verified A2F SHA `7d0b3df03c3657106ebaf86d5f9123ba262495a5` with receiver ready and Store 0036–0042 + Website 0024 already applied.

## Next exact gate
1. Repository state/request/error docs updated for A2G;
2. exact runtime `e76e555beef7ed549912b89ec2d9d4eecd9c6d8c` is committed/pushed and verified on live GitHub;
3. checksum-backed canonical Windows gate PASSed on that exact SHA and Catalog Center launched;
4. use the locally tested no-migration A2G Host runner from exact Production baseline `7d0b3df...`;
5. deploy the approved GitHub target, collect static/restart/verify;
6. publish exactly one controlled Product Windows → Production and verify Product/Profile/Variant/WebP/public page/strict ACK before bulk publish.