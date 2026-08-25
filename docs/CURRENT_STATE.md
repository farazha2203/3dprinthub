# CURRENT PROJECT STATE

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Base Epic: `epic/phase49-unified-product-slider-sync`
Active Phase: `49.3I`
Active Hotfix: `49.3I.28 — Exact-Link Canonical Title Call Contract`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA REQUIRED`
Production: `UNTOUCHED / NOT APPROVED`

## Owner Evidence Driving 49.3I.28
After 49.3I.27 removed the `Database.categories` crash, the same exact-link button reached source fetch and then failed with:

`canonical_source_title() got multiple values for argument 'current_title'`

The progress dialog reached queued/source_fetch, proving the category bridge is now active and this is the next independent failure.

## Verified Root Cause
`phase49_3i19_source_identity.canonical_source_title` has the mature signature:

`canonical_source_title(current_title, source_url, external_id='', *, candidates=())`

49.3I.26 called it using `source_url` as the first positional argument, external id as the second positional argument, and also supplied `current_title=` by keyword. Python therefore bound `current_title` twice and aborted before AI.

## 49.3I.28 Implemented on GitHub
- preserved the working 49.3I.19 source-identity implementation as authoritative,
- added a narrow compatibility adapter at the final exact-link boundary so 49.3I.26 arguments are reordered into the mature 49.3I.19 signature,
- no change to AI provider/model selection,
- no image URL/file is sent to AI,
- no change to source fetch, Product content generation, image text metadata, pricing, publish or archive behavior,
- retained the 49.3I.27 App category-provider bridge,
- added `tests.test_phase49_3i28_exact_link_contract`, including the exact MakerWorld-shaped call that previously raised the duplicate `current_title` error,
- Windows gate now runs the 49.3I.28 regression before inherited 49.3I tests.

## Preserved 49.3I.26/27 Contract
- canonical stage order remains Basic Info → Commerce → Images → Content/SEO → Source/License → Slider → Review/Publish,
- exact-link completion remains 0–100% observable with 120-second AI ceiling,
- AI receives Product/source text only and `image_urls=[]`,
- one workflow still applies Product Persian content/SEO plus image filename/Alt/Title/Caption/Keywords,
- image network downloads are not started by the unified AI completion path,
- five-column vertical gallery, full-screen toggle, archive/block and default-five acquisition remain unchanged,
- logs remain cumulative and startup does not test AI connectivity.

## Database / Migration / Safety
- Django migration: `NONE`
- Catalog schema migration: `NONE`
- no reset/drop/truncate
- no Product/media/history physical deletion
- no API key/token committed
- Local Catalog SQLite is never copied to Production MySQL
- Production untouched

## Verification Status
GitHub hotfix + regression + Windows runner are committed. No Windows execution result has been reported for 49.3I.28 yet. Do not mark accepted or deployable until the Local gate and real exact-link button test pass.

## Exact Next Task — Windows 49.3I.28 Gate
1. close Catalog Center,
2. verify Local worktree clean,
3. fetch/prune + ff-only pull the live feature branch,
4. verify Local HEAD equals fetched Remote HEAD,
5. run `catalog_center\RUN_PHASE49_3I26_OPERATOR_COMPLETION_GATE.ps1` with the verified 49.3I.28 HEAD,
6. press `تکمیل همه اطلاعات بر اساس لینک محصول`,
7. verify queued → source_fetch → source_ready → ai_request,
8. verify Product/source text is sent to AI with zero image URLs/files,
9. verify preview and one-shot Product SEO + image text metadata apply,
10. export fresh diagnostics if any new failure occurs.

## Release Gate
Windows PASS → one Local Publish E2E → Local Store/Admin/Product/Media/SEO verification → explicit owner approval → read-only Production environment verification → approved GitHub snapshot only → Production verification.
