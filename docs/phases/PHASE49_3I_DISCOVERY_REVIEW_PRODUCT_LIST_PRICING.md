# Phase49.3I — Discovery Review + Product Explorer + Pricing + Observable AI

Updated: 2026-08-25
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Hotfix: `49.3I.26 — Unified Exact-Link Completion + Canonical Wizard + Vertical Gallery + Product Archive`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA REQUIRED`
Production: `UNTOUCHED / NOT APPROVED`

## Goal
Deliver a business-usable Catalog Center where exact products are acquired reliably, real source identity is preserved, one exact-link action can prepare the Product and its SEO without image upload to AI, images are easy to curate, AI never freezes or secretly probes providers, diagnostics survive repeated sessions, and publish remains guarded by real readiness.

## Preserved Acquisition Contract
49.3I.16 remains authoritative for resilient listing/product acquisition, candidate isolation and no Rich Direct dependency for bulk intake. Hard maximum remains 20 controlled source images/product.

49.3I.26 changes the **default** new acquisition count to 5. During approved full acquisition one full-page source screenshot is also captured headlessly and appended as an extra local/non-selected gallery reference. The screenshot does not consume the normal five selected source-image slots.

## Source Identity Contract
Generic model-number placeholders are not authoritative. Valid source title wins; MakerWorld exact model URL slug is deterministic fallback. Existing Products can repair source identity without delete/reimport.

## Canonical Product Operator Contract — 49.3I.26
The canonical stage order is restored to:
1. `اطلاعات پایه`
2. `سفارش، قیمت و گزینه‌ها`
3. `تصاویر`
4. `محتوا و SEO`
5. `منبع و مجوز`
6. `اسلایدر صفحه اصلی`
7. `بررسی و انتشار`

All stages remain directly navigable even when earlier data is incomplete. Readiness is a publish gate, not a navigation lock. Product opens on Basic Info and the header exposes a maximize/full-screen toggle.

Basic Info exposes `🌐 تکمیل همه اطلاعات بر اساس لینک محصول`. That exact-link action is the canonical Product autofill path and replaces legacy Product-data-send behavior where present.

## Unified Exact-Link Completion Contract
- shows determinate 0–100% progress and explicit current stage,
- AI request ceiling is 120 seconds,
- if AI times out, source URL is rechecked separately so source failure is distinguishable from provider failure,
- reads the exact Product source URL,
- fetches/parses the real source page before AI,
- canonicalizes source title,
- carries source description/category/license/creator facts,
- carries available `estimated_weight_grams` and `estimated_print_minutes`,
- for MakerWorld `#profileId-...`, prefers the exact matching profile weight when available,
- snapshots current operator material/color/image selection,
- sends Product/source text facts only; selected image URLs/files are not sent to AI,
- performs AI work off the UI thread through the Tk main-thread bridge,
- previews and requires operator confirmation before applying,
- persists source identity and valid source weight/time,
- updates Persian title/content/SEO and selected-image filename/Alt/Title/Caption/Keywords from the same Product result,
- preserves price, stock and commercial choices,
- does not run the broad layered Workspace save before AI,
- does not start hidden source-image downloads merely to finalize image metadata.

Physical image SEO finalization is attempted only when every selected source image already has a valid local source file. If one is missing, image text metadata is still saved but file-level finalization is explicitly deferred and logged.

## Image Contract
The final visible Product image area is owned by 49.3I.26 and overrides the older 49.3G delayed horizontal callback:
- one vertical Canvas,
- five cards per row,
- rows continue downward,
- Mouse Wheel/vertical scrollbar scrolls the gallery,
- mature primary/site/bulk/open/remove controls and metadata stay intact,
- horizontal gallery scrolling is not the primary layout.

## Products List / Archive Contract
- Product cards support individual and visible-group selection,
- bulk archive is non-destructive Catalog state using existing `workflow_status/source_state`,
- archive does not automatically unpublish a live Production Product,
- bulk delete/block uses the existing identity-preserving blocked Product contract,
- blocked Product source URL/external identity remains so discovery/import does not reacquire it,
- physical files/history are not deleted by Product-list archive/block actions,
- previously synced/edited cards receive a white border treatment.

## AI / Startup Runtime Contract
- one explicitly saved Provider + Model remains authoritative,
- opening the application/Product never tests provider connectivity,
- hidden model catalog requests are blocked for the whole process,
- only visible operator Search/Test actions may temporarily authorize `/models`,
- Product requests never use hidden provider fallback,
- obvious non-text routes remain rejected,
- slow provider responses remain background/observable/cancellable,
- current exact-link AI sends no images.

## Diagnostics / Performance Contract
Historical logs are cumulative and must not be cleared merely because the app restarts or exports diagnostics. Fresh owner diagnostics must be interpreted by timestamp/session because older 401/429 events intentionally remain in exported history.

The 2026-08-25 diagnostic captured a hang sample while image finalization was blocked in network SSL/HTTP download work. 49.3I.26 therefore decouples Product text AI from missing-image network acquisition.

## Publish Contract
Local/site publish preflight remains blocking when readiness is incomplete. The operator can visit any editor at any time. AI-fillable Product/content gaps can invoke the unified exact-link completion action; commercial/license/manual requirements remain explicit and are never guessed.

## Database / Migration
Django migration: NONE. Catalog schema migration: NONE. Existing diagnostic/archive/blocked Product fields are reused. Local SQLite is never copied into Production MySQL. Production untouched.

## Focused Windows Acceptance
- clean ff-only pull live feature HEAD and verify Local==Remote,
- compile changed modules and run 49.3I.26 + inherited tests,
- `launch.py --verify-only`,
- launch without any automatic provider/model request,
- Product opens at Basic Info with canonical 1..7 rail and no lock popup,
- every stage can be opened while incomplete,
- five image cards per row persist after idle callbacks and scroll vertically,
- maximize/full-screen toggle works,
- exact-link completion shows percent/current stage and 120-second ceiling,
- no image URL/file is sent to AI,
- real source title/creator/category/description/available exact-profile weight/time are shown in preview,
- Product content/SEO and image text metadata update together,
- local selected images can finalize metadata without a second AI call; missing local images are deferred without hidden network download,
- new acquisition defaults to five source images and adds one source screenshot,
- Products gallery selection/archive/delete-block works and blocked identity prevents reacquisition,
- historical logs survive close/reopen and no new hidden startup model scan appears,
- no new unexplained SQLite transaction error or UI hang.

## Release Gate
Windows PASS → exactly one Local Publish E2E → Local Store/Admin/Product/Media/SEO verification → explicit owner approval → read-only Production environment verification → approved GitHub snapshot only → Production verification.
