# Phase49.3I — Discovery Review + Product Explorer + Pricing + Observable AI

Updated: 2026-08-25
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Hotfix: `49.3I.25 — Product-First Workflow + Persistent Diagnostics + Startup No-AI`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA REQUIRED`
Production: `UNTOUCHED / NOT APPROVED`

## Goal
Deliver a business-usable Catalog Center where exact products are acquired reliably, real source identity is preserved, editorial Content/SEO is completed early, images are easy to curate, AI never freezes or secretly probes providers, diagnostics survive repeated sessions, and publish remains guarded by real readiness.

## Preserved Acquisition Contract
49.3I.16 remains authoritative: resilient listing/product acquisition, max 100 candidates, max 20 controlled images/product, local staging, per-candidate failure isolation and no Rich Direct dependency for bulk intake.

## Source Identity Contract
Generic model-number placeholders are not authoritative. Valid source title wins; MakerWorld exact model URL slug is deterministic fallback. Existing Products can repair source identity without delete/reimport.

## Product-First Operator Contract — 49.3I.25
The canonical stage order is:
1. `محتوا و SEO`
2. `اطلاعات پایه`
3. `تصاویر`
4. `سفارش، قیمت و گزینه‌ها`
5. `منبع و مجوز`
6. `بررسی و انتشار`

All stages remain directly navigable even when earlier data is incomplete.

Basic Info exposes `🌐 تکمیل همه اطلاعات بر اساس لینک محصول`. That exact-link action is the canonical Product autofill path and replaces legacy Product-data-send actions where present.

## Exact-Link Completion Contract
- reads the exact Product source URL,
- fetches/parses the real source page before AI,
- canonicalizes source title,
- carries source description/category/license/creator facts,
- carries available `estimated_weight_grams` and `estimated_print_minutes`,
- for MakerWorld `#profileId-...`, prefers the exact matching profile weight when available,
- snapshots current material/color/image choices,
- performs AI work off the UI thread through the existing Tk main-thread bridge,
- previews and requires operator confirmation before applying,
- persists source identity and valid source weight/time,
- updates Persian title/content/SEO/image text through the mature operator apply path,
- preserves price, stock and commercial choices,
- does not run the broad layered Workspace save before AI.

## Image Contract
The Product image area uses one vertical canvas, all controlled images on one page, five cards per row, existing primary/site/bulk/open/remove controls and existing metadata. Mouse wheel scrolls vertically when rows exceed the viewport.

## AI / Startup Runtime Contract
- one explicitly saved Provider + Model remains authoritative,
- opening the application/Product never tests provider connectivity,
- hidden model catalog requests are blocked for the whole process,
- only visible operator Search/Test actions may temporarily authorize `/models`,
- Product requests never use hidden provider fallback,
- obvious non-text routes remain rejected,
- slow provider responses remain background/observable/cancellable.

## Diagnostics / Database Stability
Fresh owner diagnostics proved a post-first-idle hidden model scan leak, a broad pre-AI save storm and `cannot commit - no transaction is active` during overlapping worker/UI writes.

49.3I.25 therefore:
- moves diagnostics to a dedicated SQLite connection with WAL/busy timeout,
- serializes common Catalog Database operations with an instance RLock,
- keeps audit/runtime history across application restarts,
- uses append-only runtime text logging with no finite rotation deletion,
- diagnostic export does not clear historical rows/files.

## Publish Contract
Local/site publish preflight remains blocking when readiness is incomplete. The operator sees actual missing items; if Content/Basic gaps are AI-fillable, exact-link completion can be launched from the preflight. The operator can still navigate to any stage manually.

## Database / Migration
Django migration: NONE. Catalog schema migration: NONE. Existing diagnostic tables are reused. Local SQLite is never copied into Production MySQL. Production untouched.

## Focused Windows Acceptance
- clean ff-only pull live feature HEAD and verify Local==Remote,
- compile changed modules and run 49.3I.25 + inherited tests,
- `launch.py --verify-only`,
- launch without any automatic provider/model request,
- close/reopen and confirm historical logs remain,
- Product 151 / MakerWorld 2801606: confirm Content/SEO first and exact-link action in Basic Info,
- verify free stage navigation,
- verify five image cards per row with vertical scroll and mature card controls,
- run exact-link completion and verify real source title plus available exact-profile weight/content/SEO/image text,
- verify no broad pre-AI Product update storm,
- verify Workspace stays responsive during slow AvalAI response,
- verify no new SQLite transaction error,
- verify publish missing-item list + AI assist.

## Release Gate
Windows PASS → exactly one Local Publish E2E → Local Store/Admin/Product/Media/SEO verification → explicit owner approval → read-only Production environment verification → approved GitHub snapshot only → Production verification.
