# Phase50.A.2Z-C1/C2 — Full Product Edit + Unified Bulk Completion

Status: **GITHUB_UPDATED / WINDOWS_RUNTIME_ACCEPTED / CLOSED — A2Z CATALOG DATA COMPLETION NEXT**
Date: 2026-09-22
Baseline: `494a222b64908563c5d6b953b4ef96f9782c8e0d`
Rollback ref: `backup/pre-a2z-full-edit-bulk-completion-20260922`
Worktree: `D:\projects\3DPrintHub-a2y-converge`
Branch: `wip/phase50-a2z-image-social-authority-20260921`

## Owner request

1. Product Wizard must expose one top-level **«✏ ویرایش کامل»** action so every finalized Product stage becomes editable together rather than requiring seven separate unlock actions.
2. Products multi-select **«AI تکمیل همه موارد»** must retain the mature AI flow while also executing the deterministic completion capabilities added later:
   - factual Source Print Profile refresh/import from Product source;
   - separate multi-profile weight/time/dimension data;
   - all currently available exact-family Local Filaments for Source materials such as PLA;
   - correct validated local Category;
   - complete six-field A2X Slider SEO data;
   - physical unique SEO filenames and image metadata/finalization.
3. Existing publish, image membership, Slider membership, Social and same-identity re-publish authorities must not be weakened or silently changed.

## Safety boundaries

- Full Edit opens stage locks only. It does **not** change Product values, publish, Slider membership, selected Site media or dirty state merely by entering edit mode.
- Source/provenance facts remain factual authority; unlocking stages does not make immutable Source evidence an AI guess.
- Bulk completion may open `quick/content/specs/slider/commerce` because those are required by this explicit operator command. `publish` remains locked/operator-owned.
- Image finalization reuses the accepted A2Z physical SEO rename boundary.
- Slider membership `homepage_slider_enabled` is never changed by completeness.
- Slider image is selected only from existing selected Product media; completeness does not silently select a new Site image.
- Manual Profiles are preserved by the accepted A2W `import_source_profiles` merge contract.
- Source Profile fresh capture falls back to persisted factual capture when available; unsupported/missing Source Profile data falls back to mature Source-fact bootstrap rather than inventing technical facts.
- No Production/Host/real Catalog mutation is part of this source slice.

## Implementation

### C1 — Full Product Edit

- Added top Product identity-row button `✏ ویرایش کامل`.
- Added `StageCore.unlock_all_for_edit(product_id)` using the existing per-stage unlock authority/history.
- All finalized stages can be opened in one confirmation, including Publish stage controls.
- Merely opening edit mode does not mark an uploaded Product as changed.
- Existing per-stage `اصلاح مرحله` remains available and unchanged.

### C2 — Unified Bulk Completion

Bulk multi-select continues to use the one configured Product AI core, then runs accepted deterministic post-processing:

1. validated Category:
   - preserve explicit non-placeholder Category;
   - repair blank/`external-other` only;
   - exact Source Category match wins;
   - valid AI suggested taxonomy is fallback only.
2. Source Profile:
   - MakerWorld factual Profile refresh with existing cached fallback;
   - accepted A2W multi-profile import;
   - preserve manual Profile rows.
3. Filaments:
   - reuse A2W exact-family matching;
   - Source PLA receives every current Local PLA candidate;
   - PETG/PLA-CF/etc. cannot leak into exact PLA mapping.
4. Images:
   - reuse accepted finalizer;
   - actual Product-local files receive unique physical SEO WebP names;
   - selected/canonical authority remains unchanged.
5. Slider:
   - fill only missing official six core fields:
     `image_url, title_fa, description_fa, alt_text, button_text, focus_keyword`;
   - existing content pack is preferred;
   - Product SEO/content is deterministic fallback;
   - `homepage_slider_enabled` is invariant.
6. Publish:
   - never unlocked by Bulk completion;
   - no Site publish is triggered by completion itself.

### Category defect found during integration

ERR-49-223: the legacy ASCII-only fold helper turned Persian Category names into empty strings, so an exact Persian Source Category could match the first Persian category (`external-other`) before reaching the real category. Folded comparison now requires non-empty folded text; direct Unicode name/slug equality remains authoritative.

## Verification

- New focused contracts: **3/3 PASS**
  - Full Edit unlocks all stages without marking published Product dirty.
  - Bulk preparation opens Commerce but preserves Publish lock.
  - End-to-end deterministic completion proves two Source Profiles, exact-family PLA offers, Category, six Slider fields with membership unchanged, and physical SEO rename.
- Related Stage/Image/Profile/Filament/Site regression: **148/149 effective PASS**; sole failure is the already documented baseline ERR-49-203 Manufacturer-vs-Brand assertion, reproduced unchanged.
- Unchanged AI/completion/Unified Desktop/Slider cycles: **38/38 PASS**.
- Changed Python compile: **6 files PASS**.
- `git diff --check`: PASS.
- `RUN_QT.ps1 -VerifyOnly`: PASS.
- Migration/dependency/Server/website/template/static delta: **0**.

## Closure

- Runtime-bearing source commit: `8629f8b72c416b364a618a5aeebe2dda8a81d440`, Local=GitHub exact.
- Exact-SHA Qt VerifyOnly + real runtime launch PASS.
- Exact-SHA widget smoke 2/2 PASS for Full Edit + Products Bulk AI surface.
- Idle real Catalog remained Products=635 / history=2646 / quick_check=ok before and after.
- Focused 3/3; broad rerun 129/130 with only historical ERR-49-203; prior 148/149 effective gate confirms the same sole baseline; unchanged AI/completion rerun 40/40; compile/diff PASS.
- No Production deploy is required for this Windows-only slice.

## Exact next — Phase50.A.2Z Catalog Data Completion

1. fresh integrity-checked Catalog backup;
2. authoritative six-field Slider completeness inventory;
3. deterministic/no-AI backfill from stored content packs and Product data while preserving every Slider membership checkbox;
4. AI only for genuinely missing editorial fields;
5. real operator acceptance on #620/#625/#628 using the new Full Edit/Bulk completion surfaces;
6. final Profile/Filament/Image gates;
7. fresh backup and one guarded same-identity Site re-publish;
8. strict public Product/media/Profile/Variant/Slider parity + browser verification;
9. documentation closure.

## Following phase

A2Z-S changed-revision Social rollout / Story recovery under the existing Site-first, duplicate-safe Instagram policy.
