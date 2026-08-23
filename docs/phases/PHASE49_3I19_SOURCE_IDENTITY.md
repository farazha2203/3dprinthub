# Phase49.3I.19 — Canonical Source Identity Before AI

Updated: 2026-08-23  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA REQUIRED`  
Production: `UNTOUCHED / NOT APPROVED`

## Trigger
Owner supplied Windows evidence that MakerWorld product `2896217-ribbed-cake-stand-cookie-platter` was represented in Catalog by a generic model-number identity. AI then generated Persian title, image metadata, descriptions and SEO from that wrong identity.

## Verified Root Cause
49.3I.16 resilient discovery fallback methods sometimes create placeholder row text `Model <external_id>` because those methods are link-recovery methods. The mature candidate-title helper rejected only a bare numeric ID, so `Model 2896217` could be accepted as a real title. 49.3I.15 then copied candidate `source_title` into Product persistence. AI received the already-corrupted identity.

## Contract
1. Source identity is resolved before translation/SEO.
2. Generic model-number placeholders are never authoritative.
3. A valid exact-page/scraped title wins.
4. If live title retrieval is unavailable, exact MakerWorld model URL slug is the deterministic fallback.
5. Candidate upsert is guarded.
6. Add-to-Products is guarded again.
7. Product AI source context is guarded for legacy already-imported products.
8. Existing products can be repaired without deletion/reimport.
9. 49.3I.18 operator-confirmed Persian identity remains available and unchanged.

## Acceptance Examples
- `https://makerworld.com/en/models/2845731-cake-stand?...` → `Cake Stand`
- `https://makerworld.com/en/models/2896217-ribbed-cake-stand-cookie-platter?...` → `Ribbed Cake Stand Cookie Platter`
- `Model 2896217` → rejected as source identity
- `MakerWorld model 2896217` → rejected
- `مدل میکرورلد 2896217` → rejected

## Product Workspace Repair
New additive controls under content/SEO:
- `↻ بازخوانی و اصلاح عنوان منبع`
- `🌐 اصلاح عنوان منبع + بازسازی کامل AI`

The combined action first repairs English/source identity from live page metadata when available, falls back to URL slug if necessary, persists corrected `source_title`, then runs a full AI commerce rebuild from that corrected identity. AI is explicitly instructed not to invent another product type or generic number-based name.

## Files
- `catalog_center/app/phase49_3i19_source_identity.py`
- `catalog_center/app/phase49_3i12_runtime_bridge.py`
- `catalog_center/app/phase49_3i_pricing_modes.py`
- `catalog_center/tests/test_phase49_3i19_source_identity.py`

## Data / Migration / Deploy
- Django migration: `NONE`
- Catalog schema migration: `NONE`
- no database reset
- no media deletion
- no Production deploy

## Required Local Gate
1. clean Windows worktree,
2. fetch/switch/ff-only pull exact feature branch,
3. run `py_compile` for the new module + touched composition modules,
4. run `test_phase49_3i19_source_identity`, 49.3I.18, 49.3I.16, 49.3I.15, 49.3I discovery review regressions,
5. run `launch.py --verify-only`,
6. launch Catalog Center,
7. open the existing bad product `2896217`,
8. use `بازخوانی و اصلاح عنوان منبع`; verify source title becomes `Ribbed Cake Stand Cookie Platter`,
9. use `اصلاح عنوان منبع + بازسازی کامل AI`; verify Persian title/text/SEO/image metadata are regenerated from the corrected product identity,
10. verify the `2845731-cake-stand` case resolves to `Cake Stand`,
11. verify existing 49.3I.18 manual Persian override/bulk image operations still work.

Do not merge/deploy until this gate passes.