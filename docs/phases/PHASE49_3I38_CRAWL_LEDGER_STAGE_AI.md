# Phase49.3I.38 — Permanent Crawl Ledger, Reject/Purge Tombstones and Stage-scoped AI

Updated: 2026-08-27  
Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Catalog Center: `8.9.6` / build `2026.08.27.8`  
Tested runtime SHA: `c904193a7f0af9aad80365834ec3f0b856e77dc9`  
Status: `GITHUB CI + WINDOWS PORTABLE PASS / OWNER LOCAL VISUAL QA NEXT / PRODUCTION UNTOUCHED`

## Requested delta

Preserve the mature receive/crawl/browser/parser/image-download pipeline while adding three operator contracts:

1. previously crawled/received/rejected Product identities remain permanently known and are skipped before re-download,
2. rejecting an unwanted Product can delete its local acquired files/images while keeping its source link/identity as a tombstone,
3. all Product AI actions share one configured engine/source authority, including bulk selected-Product SEO and a single-stage cleanup such as Stage 4 only.

## Must-not-touch boundary

The following mature acquisition code remains the receive authority:
- `classic_methods.discover_classic()`,
- existing browser context/profile setup,
- existing Product parser,
- existing image downloader/fallback path,
- existing file-link discovery,
- existing `discovered_urls` unique identity ledger.

3I.38 extends/wraps those boundaries. It does not replace them.

## Permanent crawled/received ledger

The mature `discovered_urls` table remains canonical for individual Product identities.

Meaningful states now include:
- `new`,
- `running`,
- `collected`,
- `failed`,
- `rejected`,
- `blocked`.

`collected`, `rejected` and existing blocked Product identities do not become new crawl work by simply scanning the same Listing again.

A new UI action opens:
`📚 دفتر لینک‌های کرال‌شده / دریافت‌شده`

It exposes source, external ID, Product URL, discovery origin, status, attempts and last update time with filters/search.

## 100 + next 100 continuation contract

For a Listing where Products 1–100 are already in the ledger:
- discovering 1–100 again counts them as duplicates,
- they are not requeued and are not redownloaded,
- newly observed identities 101–200 enter the pending queue,
- a request for 100 new Products therefore processes 101–200.

For infinite-scroll/category pages, 3I.38 adds only a persisted continuation cursor:
`crawl_listing_state`.

It records the deepest previous scroll window and advances by bounded increments:
- first pass: 8 scroll rounds,
- later pass: previous + 8,
- cap: 96.

The existing `discover_classic()` function still performs the browser discovery. 3I.38 does not rewrite its browser/parser behavior.

Four consecutive deeper attempts with no new identities stop the current scan so a depleted Listing does not loop indefinitely.

## Reject + purge tombstone

Products page now has:
`🗑 رد دائمی + حذف فایل‌ها و عکس‌های محلی`.

When explicitly confirmed:
- Product source URL and external identity are retained,
- `discovered_urls.status` becomes `rejected`,
- Product becomes blocked/rejected and leaves active/publish queues,
- image/file/local pointers are cleared,
- the Product's local acquisition directory is physically removed,
- the source identity remains a permanent tombstone and is skipped by future Crawl/Direct Link runs.

Filesystem safety:
- physical deletion is allowed only below the canonical `<Catalog DATA>/collected/` root,
- any path outside that root fails closed and is not deleted.

Explicit restore from blocked/rejected Products is the only operator path that changes that tombstone back to `new` and permits acquisition again.

## Direct Link pre-acquisition guard

Terminal identity is checked **before** `extract_direct_link()`.

Therefore a rejected/blocked Product cannot open browser acquisition or redownload images/files before the DB later notices it is blocked.

Successful Direct Link acquisition records the identity as `collected`.

Saved-HTML import follows the same terminal identity rule.

## One AI engine, three inputs

The same 3I.37 resilient orchestrator remains the only Product AI engine.

Configured source choices remain exactly:
- Product Link,
- Crawled/Saved Product Data,
- Product Screenshot.

3I.38 does not instantiate another AI client or another Content Pack generator.

## Stage-scoped AI

The same engine now accepts a bounded `target_stages` write scope.

Normal seven-stage action:
- missing/invalid AI-owned fields only,
- every locked stage skipped,
- operator-owned Commerce/Publish remain unchanged.

Explicit single-stage cleanup:
- operator chooses a stage,
- only that unlocked stage can receive AI writes,
- existing AI-owned values in that stage may be cleaned/replaced with a validated pack,
- all other stages are out of scope and immutable for that run,
- locked stage refuses until operator presses `اصلاح`,
- Commerce and Publish remain operator-only even when selected.

For Stage 4:
`✨ پاکسازی/تکمیل فقط همین Stage`
updates only Content/SEO.

## Products bulk SEO

Products page exposes:
`✨ SEO/محتوا انتخابی — فقط مرحله ۴`.

It calls the exact same:
`run_resilient_orchestrator(... target_stages={"content"}, refresh_existing=True)`.

There is no separate bulk SEO provider/model/prompt engine.

Each Product still has isolated retry/failure behavior and the Products Explorer is not globally rebuilt per Product.

## Image AI no-op rule

Image AI remains SEO-only.

If image SEO/metadata is already complete:
- image-only scoped run returns `no_ai_needed`,
- Provider is not called,
- file rename/WebP work remains deterministic image-tool ownership.

## Verification

Targeted Phase49.3I.31–38:
- run `33077213590`,
- result PASS,
- 84 tests PASS.

The 3I.38 tests prove:
- Products 1–100 collected + discovery 1–200 → exactly 100 duplicates and pending 101–200,
- Listing cursor advances 8 → 16 → 24,
- reject/purge removes a real temp Product directory and keeps a rejected tombstone,
- deletion outside canonical `collected/` is refused,
- Stage 4 cleanup changes Content/SEO only,
- image-only complete SEO makes zero provider calls,
- Bulk Stage 4 uses the same orchestrator,
- Direct Link terminal guard appears before acquisition.

Single Active AI:
- run `33077239617`,
- result PASS.

Windows Portable:
- run `33077239660`,
- result PASS,
- version `8.9.6`,
- build `2026.08.27.8`,
- artifact `3DPrintHub-CatalogCenter-v8.9.6`,
- artifact ID `9648474905`,
- EXE size `65,520,499` bytes,
- EXE SHA256 `6490e4815f1e6e0d75f09c112bb6990041578616f170954f62fae037b98bd507`,
- artifact ZIP digest `sha256:13ae8582be09b71f90e607c2230075d875b7445f8a46b6462a9241edf9d52563`,
- browser smoke PASS,
- portable self verify PASS,
- source URL preservation gate PASS.

## Errors/prevention

- `ERR-49-062`: Direct Link terminal identity was checked only after acquisition; now guard is before any extract/download.
- `ERR-49-063`: category/site crawl had a fixed first-window depth; now it persists a bounded deeper continuation cursor while retaining the same mature discoverer.

## Rollback

Pre-3I.38 Git rollback branch:
`backup/pre-phase49-3i38-crawl-ledger-stage-ai-20260827` → `d1ed566a82d3818aa45a5c720df3e7efcb0044f3`.

This is only a source rollback anchor. Production source/environment/MySQL backup remains mandatory before any Host deployment.

## Production

Production was not touched.

Last terminal-verified Production application remains:
`c283864290f9c989a9fcdf24ee8eef519560e917`.

Last verified new Phase50 migration state remains:
- applied `store.0034`,
- applied `store.0035`,
- `0036..0039` are not claimed applied without fresh Host read-only verification.

## Exact next step

Owner Local visual/functional QA on the final GitHub docs head:
1. pull ff-only and verify exact head/clean worktree,
2. run the 31–38 local gate,
3. foreground launch 8.9.6,
4. verify the crawl ledger UI,
5. on a disposable test Product, confirm reject+purge removes only its local collected folder and leaves it visible as rejected,
6. rescan the same Listing and verify old collected/rejected identities are skipped while new identities continue,
7. verify Products bulk Stage-4 SEO uses the mother source mode,
8. verify Product single-stage selector changes only the chosen stage,
9. verify locked stages remain unchanged,
10. verify Direct Link to a rejected identity skips before any receive/download,
11. verify ordinary new Direct Link/Crawl/image/file receive still works.

Only after owner Local QA PASS:
Host read-only audit → fresh backups → explicit `FETCH_HEAD` deploy → actual pending migration verification/apply → Production verification.
