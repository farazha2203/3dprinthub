## 2026-09-14 Product #303 preview-only bounded expansion
A copied-Catalog audit found Product #303 (`Twistmas Tree`) as the only approved non-uploaded candidate with no operator-only missing facts. Its sole defect is empty Product-level SEO target phrases while finalized image metadata already contains valid Persian keywords. A DB + Product-folder preview reused that existing evidence, re-finalized Content and Images, retained five valid publish WebPs, and reached `publish_gate.ready=true`. Canonical Catalog/Production are unchanged; fresh rollback backup and one-Product publish acceptance are next.

## 2026-09-14 Product #62 controlled expansion acceptance PASS
A2G bounded publication now has a third customer-orderable Product. Catalog #62 was repaired through the canonical Profile ledger and republished to existing Site Product #18. Strict ACK/public media/visibility/orderability passed; public API exposes orderable Variant 884 with E-Sun white stock, 138 g, 180 min and 500,000 Toman. Chromium selected Variant 884 by default, kept legacy Variant 877 disabled, enabled Cart and emitted the exact variant/quantity POST, intercepted before server delivery. Product #19/#84 is explicitly not accepted: selected black-matte stock is zero and it has no orderable Variant. The approved stale-public lifecycle fix is on GitHub at `07772ca...` but Production remains `70a74e6...` until an authorized deployment path can promote it.

## 2026-09-14 - Stale-public fail-closed extension
A2G acceptance now includes lifecycle cleanup: a Product already public under an older weaker contract must be deactivated/noindexed when republish proves it has no actually orderable Variant. Local ERR-49-138 regression PASS; Production deploy and Product #62/#84 repair are next.

## 2026-09-14 - ERR-49-135 orderability hardening checkpoint
Bounded expansion found that HTTP/public visibility was weaker than customer orderability for older Products without canonical sales Profiles. A2G acceptance is therefore tightened: Desktop must have canonical Profile rows before FTP, and final Store visibility must contain at least one Variant that passes the exact shared customer `variant_is_orderable` rule. Local regression/no-drift/runner gates PASS. #628/#634 stay accepted; #62/#84 require Profile bootstrap + republish + live Cart acceptance before they join the sales-ready set.

## 2026-09-14 - Bounded multi-product acceptance PASS / SALES STARTED
Owner-license Host parity is live at `6569e5a...`. Exactly Product #628/#634 were republished through the mature Batch 8.5 -> FTP -> Bridge route and both passed strict Store/public media visibility; Local rows became `uploaded`. Real browser customer flow selected Variants 651/775, displayed 360,000/560,000 Toman and generated valid Cart POSTs intercepted before server delivery. A2G publication/order wiring is therefore accepted for this bounded two-product batch. Wider publication remains gated by fresh factual readiness/media/stage checks and a new Catalog backup.

## 2026-09-14 ERR-49-131 bounded-sales owner-license parity checkpoint

Status extension: `LOCAL_TESTED / PRODUCTION HOTFIX NEXT / BOUNDED RETRY #628+#634 ONLY`. The first two-Product bounded publish reached FTP/Bridge but both ACKs returned `review_required`. Source-of-truth review proved this was Host contract drift: the explicit 2026-09-01 owner policy uses `source_license_owner_approved=1` as business approval while preserving source license status/text as evidence. Windows readiness/export already honors it. Local Host hotfix applies the same effective rule to importer editorial state, fixed Product conversion and Store visibility; owner-approved `review` is publishable without rewriting the evidence, while unapproved `review` stays blocked. 9 focused + 16 Site + 18 Catalog regressions PASS; no migration drift. Production is unchanged at `44a7be9...` until guarded GitHub-first deployment.

## 2026-09-13 Bridge public-media hotfix deploy runner checkpoint

Production identity is freshly verified at clean `443d1b70ecdf59e26b106d8887d56cb0e61ece8d`. A dedicated no-migration/no-DB-write/no-collectstatic runner is Local-tested to promote the ERR-49-125 Bridge serializer fix only from the live GitHub branch, with verified source/.env rollback evidence, ff-only Git promotion, Passenger restart, authenticated readiness and Product #15/Hero Product-owned WebP verification. Bulk remains blocked until this deploy passes and Product #63 selector/cart/strict ACK acceptance completes.

## 2026-09-13 Controlled Product #63 media acceptance checkpoint

The first real Product exposed one remaining contract bug after successful publication: Product-owned gallery WebPs exist and return HTTP 200, but the unified Bridge read payload referenced private imported working-media and therefore produced 404 URLs. The Local no-migration fix resolves public Bridge Product/Hero image URLs through Product-owned media while retaining imported image IDs for Desktop identity. Focused Bridge/Hero/Admin regression is 31/31 PASS; no schema drift. The fix is committed/pushed at `d830a9af05d768f9b81568a0665a74f59e864a34`. Status remains `PRODUCTION_VERIFIED / CONTROLLED PRODUCT ACCEPTANCE IN PROGRESS`; bulk remains blocked until the fix is deployed and Product #63 selector/cart/strict-ACK checks pass.
## 2026-09-13 Final Production verification checkpoint

Reverse tunnel E2E, authenticated Host identity/worktree, repository read-only Production audit, MySQL/migration plan, in-process/public readiness, Home/Store, authenticated Bridge and live A2G JS/CSS marker gates all PASS at Production source `d7cf71dceca95e191a118336c7004683083278ee`. Store 0036-0042 + Website 0024 are applied; migration plan is empty; readiness is true with no blockers. No DB/Product/media mutation occurred during tunnel onboarding. Phase status is `PRODUCTION_VERIFIED`, not `ACCEPTED`; exactly one controlled real Product publish remains before bounded bulk.

## 2026-09-13 Operations support checkpoint - reverse Host management

A2G source is now promoted on the Host: read-only FTPS Git evidence shows Production branch HEAD `a320a0d346e4be573504978b23d197dc08f8bc2c`. Public Home, Store and the A2G selector JS/CSS currently return HTTP 200. The earlier deploy runner stopped during immediate post-restart HTTP verification; authenticated Bridge/readiness plus exact Host worktree acceptance still must be repeated before declaring A2G `PRODUCTION_VERIFIED`.

To remove repeated cPanel operator dependency, the proven Asal shared-cPanel reverse-management transport is being adopted without changing business/runtime authority. Windows side is ready (`PrintHubTunnel`, loopback `22024`, source restriction `89.39.208.237/32`); repository bridge/bootstrap scripts are local-tested and pushed at `180fe16c0e296156ef38ffc00a042c329318ff7c`. Host E2E onboarding is the next gate. This transport introduces no migration or Product/media write and does not permit direct permanent source edits on Production.

# Phase50.A.2G — Publish-ready Media + Professional Order Wizard

Date: 2026-09-12
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Status: `PRODUCTION_VERIFIED / CONTROLLED PRODUCT ACCEPTANCE PASS / BOUNDED BULK UNLOCKED`
Rollback: `backup/pre-phase50-a2g-publish-media-order-wizard-20260912` → `02f654b0204266c2d7d329caf85b781c76a56a62`
Production pre-A2G baseline: `7d0b3df03c3657106ebaf86d5f9123ba262495a5`; current Host source: `d7cf71dceca95e191a118336c7004683083278ee`

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
No Django migration is introduced. Local Catalog media is only read/copied by publish packaging. A2G runtime plus reverse-management ops are present in Host Git at `d7cf71d...`; authenticated Host worktree/Django/MySQL/migration/readiness acceptance PASSed, and public Home/Store/Bridge/readiness/new JS/CSS are HTTP 200. Store 0036-0042 + Website 0024 are verified applied with an empty migration plan.

## Next exact gate
1. Repository state/request/error docs updated for A2G;
2. exact runtime `e76e555beef7ed549912b89ec2d9d4eecd9c6d8c` is committed/pushed and verified on live GitHub;
3. checksum-backed canonical Windows gate PASSed on that exact SHA and Catalog Center launched;
4. Host source and authenticated reverse-management transport are verified at `d7cf71d...`; do not rerun the old `7d0b3df...` baseline deploy;
5. reverse-tunnel E2E and authenticated Host identity/worktree/Django/MySQL/migration/readiness verification PASSed;
6. publish exactly one controlled Product Windows -> Production and verify Product/Profile/Variant/WebP/public page/guided cart/strict ACK before bulk publish.

## 2026-09-14 controlled Product acceptance PASS
Combined Production source is `44a7be91057c60891960fbb9d9b4f53780273c33`. Product #63 stored ACK passes `ack_item_confirms_publish(..., require_store_visibility=True)` with Site Product #15, `visible_on_store=True`, `public_http_ok=True`, and Local state `uploaded`. Product #15 public WebPs return 200/image-webp and no imported working-media URL is public. Live selector resolves Variant 618 and Cart wiring produces the correct variant/quantity POST; the acceptance request was intercepted before server delivery, so no test order mutation occurred. The one-Product prerequisite is closed; only bounded factually-ready publishing is now permitted.