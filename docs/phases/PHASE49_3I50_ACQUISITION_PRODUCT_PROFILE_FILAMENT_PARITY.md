# Phase49.3I.50 — Search-Link Acquisition, Product Republish and Filament Brand/Color Parity

Date: 2026-09-02

## Goal

Restore the owner-facing workflows that were present in the mature Catalog Center while keeping the current Qt6/Core architecture authoritative:

- open the original source Product page directly from Products and Crawl inventory;
- make Search/Listing URL acquisition the obvious operator path again;
- show received image count and available source technical facts in Crawl inventory;
- let the operator review a discovered Product, receive it, or receive + run the existing single AI completion path;
- use persisted source dimensions/weight/print-time to bootstrap Product Profile 1 and match all real Filament Library offers declared by the source;
- manage reusable Filament brands and colors independently from individual Filament rows;
- repair Filament editing and make long fields/price controls usable;
- edit an already-published Product and republish it as an update to the same server Product identity;
- when stages 1..6 are fully ready/finalized after Full AI, advance to the guarded Publish review without auto-publishing.

## Repository baseline and rollback

Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Pre-change head: `5daaca573c3249b05beeeec0ac5d5a005830a157`  
Rollback branch: `backup/pre-phase49-3i50-acquisition-product-filament-parity-20260902` → `5daaca573c3249b05beeeec0ac5d5a005830a157`.

Exact executable + owner-runner checkpoint:
`d45730990cc90002fb1da1236380e033a379db7a`.

Application identity:
- Version: `8.9.10`
- Build: `2026.09.02.1`
- Local gate: `49.3I.50.1`

## Products and republish contract

Products now expose an explicit `باز کردن صفحه محصول` / source-page action.

A real edit to a Product that already has a server identity and `workflow_status=uploaded` now sets:
- `needs_update = 1`;
- `upload_ready = 0`;

while preserving the existing server/source identity.

The existing site importer remains authoritative:
- existing ImportedPrintAsset is resolved by source identity;
- if `asset.product_id` already exists, the Store Product is updated in place through the mature sync path;
- a second duplicate Product is not created by the intended republish path.

The existing 3I.49 guarded Ready/Publish gate remains mandatory. Full AI may move the UI to final Publish review when stages 1..6 are green, but it does not silently publish or set the final upload-ready approval.

## Search-Link acquisition and Crawl review

The receive workspace is explicitly named:

`دریافت محصولات از لینک جستجو`

and Search/Listing is the default operator mode.

Crawl inventory now provides:
- large-image/gallery and detail/table modes;
- source-page review button and source-page double-click;
- Product title/description;
- explicit `N عکس` image count;
- source weight when available;
- estimated print time when available;
- source dimensions when available;
- source tags when available;
- add selected items to Products;
- `دریافت + ترجمه/SEO با AI` using the existing shared `complete_products_with_ai(..., "link")` path.

No new crawler/AI authority was created.

### 403 behavior

Hybrid/static discovery no longer dies immediately when the public Listing HTTP request returns AccessDenied/403.

It now:
1. does not repeat the same blocked static request;
2. keeps RobotsDenied/RateLimited fail-closed behavior;
3. continues once into the mature Browser collector;
4. that Browser path runs the existing robots gate before navigation.

This is fallback, not an access-control bypass. Login/CAPTCHA/robots restrictions remain enforced.

## Product Profile bootstrap

The existing Commerce bootstrap remains source-grounded.

It now also understands structured dimension objects such as:

`{"x": 120, "y": 80, "z": 35, "unit": "mm"}`

in addition to legacy dimension strings.

When source facts exist, Profile 1 can use:
- real dimensions;
- estimated source weight;
- estimated source print minutes;
- all active Filament Library offers whose material is actually declared by the source.

No weight, dimensions, print time, material, color or price is invented when source evidence is absent.

## Filament workspace

The Filament area is task-oriented and split into:
- `فیلامنت‌ها`;
- `برندها`;
- `رنگ‌ها`.

Brand registry:
- reusable central brand names;
- brand assignment from Filament editor;
- used brands cannot be deleted from the registry until their active Filament use is resolved.

Color registry:
- Qt/Windows Color Picker;
- up to seven palette colors;
- behavior: solid / dual / multicolor / gradient / color-shift;
- independent Finish;
- reusable assignment from Filament editor.

The registry uses the existing Catalog `settings` table; no new Django or destructive Catalog migration was introduced.

The Filament editor crash caused by missing `QWidget` import is fixed. Column sizing remains user-resizable/interactive and numeric controls remain directly typable without the old spin-button-heavy UX.

## Errors fixed during the phase

- ERR-49-089 — Filament editor `QWidget` NameError.
- ERR-49-090 — Listing HTTP 403 aborted Hybrid discovery before guarded Browser fallback.
- ERR-49-091 — first Brand/Color registry CI run missed the canonical `normalize_palette_hexes` import.
- ERR-49-092 — a new Crawl-fact regression used a bare test DB instead of the real Qt composed schema and therefore lacked the pre-existing image metadata column.

Failed conditions were changed before rerun; no failed command was repeated unchanged.

## Verification

Final exact owner-runner/source checkpoint `d45730990cc90002fb1da1236380e033a379db7a`:
- `33601382428` — Phase49.3I.42C3 Qt6 Crawl + AI Runtime — **PASS**;
- `33601382483` — Phase49.3I.17 Single Active AI / no-migration — **PASS**.

Exact code checkpoint `b6bc5b08903e6880d01dc0fd27d7f8c2b17fab47`:
- `33601229888` — Qt full parity including acquisition, 3I.48 Filament/registry and 3I.49 republish/Operations regressions — **PASS**;
- `33601229884` — Windows Portable Release — **PASS**.

Modern Acquisition on the implemented acquisition/source subset:
- `33600888264` — Phase49.3I.43-45 Modern Acquisition Intelligence on `8a62f6782a59c1aab3212b8ba16d5f1d82332a23` — **PASS**.

The earlier intermediate failure `33600978202` was test-fixture-only and was corrected by initializing the same `ensure_qt_parity_schema` composition used by the real Qt runtime.

## Safety

- Django migration: NO.
- Production MySQL write: NO.
- Production source change: NO.
- Host touched: NO.
- destructive Catalog migration: NO.
- secret-store change: NO.
- CAPTCHA/login/robots bypass: NO.
- direct Production source edit: NO.

Last verified Production application commit remains:
`c283864290f9c989a9fcdf24ee8eef519560e917`.

Last verified Production migration evidence remains only `store.0034` and `store.0035`; later migrations are not assumed applied.

## Owner Local acceptance next

Run the canonical checksum-backed Local gate on the clean Windows checkout and verify with disposable Products:

1. Product source-page open action.
2. Search-Link MakerWorld receive with requested Product count.
3. Gallery/details image count and thumbnails.
4. weight/time/dimensions/tags where the source provides them.
5. source review → receive → receive+AI.
6. Filament edit, Brand tab and Color tab.
7. Profile 1 bootstrap from real source facts and available matching Filaments.
8. six green stages advancing to final Publish review only.
9. edit one already-published disposable Product and verify it enters the update queue rather than becoming a duplicate.

Do not perform a real Production publish/deploy until owner Local acceptance and the normal Host read-only audit/backup/deploy chain.
