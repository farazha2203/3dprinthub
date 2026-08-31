# ERR-49-083 — Qt AI gap truth + local image SEO repair

Date: 2026-08-31
Repository: `farazha2203/3dprinthub`
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Final tested code checkpoint: `7322d504b45bf53b36060d51588435833066df0b`
Rollback branch: `backup/pre-err49-083-qt-ai-gap-truth-image-local-20260831`
Production/Host touched: NO
Django migration changed: NO
Default launcher changed: NO

## Owner-observed symptoms

- Product #309 could display `تمام شد` even though AI/local-fixable fields were still incomplete.
- The stage rail did not expose the exact number and names of missing fields in the owner’s running build.
- Stage 3 `AI همین مرحله` followed the generic `source_mode=link` provider path, called MakerWorld through `crawler.public_http`, and failed with `HTTP 403 Forbidden` before image SEO could be repaired.
- Existing local Product images kept non-SEO filenames and incomplete alt/creator/source/embedded metadata.
- `openrouter/auto` was being used as an active Product model even though a variable router cannot provide stable model identity/capability guarantees for this workflow.

## Root causes

1. The older Qt current-stage AI action treated Images like text/content stages and entered the live-source/provider orchestrator even though the required image work was deterministic and local.
2. Visible readiness used a coarse legacy image Alt flag rather than exact per-image metadata truth.
3. The old completion message was not gated by a freshly recomputed post-run AI-fixable defect count.
4. Variable OpenRouter routers were unsuitable as deterministic Product defaults.
5. During the final regression, `تأیید نهایی اپراتور (ثبت مرحله)` was initially classified as AI-fixable. CI correctly rejected that boundary because AI must never finalize an operator-owned stage.

## Correct fix

- Stage rail now reports `missing_count`, exact missing field names, `ai_fixable_count`, and `operator_count` per stage.
- Operator-owned commerce/profile/filament/price/stock/publish work stays manual.
- Stage 3 `AI همین مرحله` routes to a deterministic local image smart-repair path and does not fetch MakerWorld or call the Provider for filename/metadata repair.
- The image audit reports exact selected-image defects and repairs SEO filenames, alt text, creator/source metadata, embedded metadata, and the current SEO signature where locally derivable.
- The coarse legacy image Alt proxy is replaced in Qt status by exact image metadata truth.
- AI completion is evaluated from fresh post-run readiness; a green `تمام شد` is forbidden while `ai_fixable_count > 0`.
- `openrouter/auto` and `openrouter/free` are excluded as deterministic Product defaults.
- The live model catalogue keeps Product-safe free/Persian/Structured filters and an internal priority list, but the final acceptance remains the real live Persian + JSON probe.
- Final stage confirmation remains explicitly operator-owned; after image repair it can be the only remaining manual item while AI-fixable count is zero.

## Failed condition and correction

Run `33403665261` failed one targeted image test after all actual image SEO defects had been repaired. The only remaining item was `تأیید نهایی اپراتور (ثبت مرحله)`, but it was still counted as AI-fixable. The failed condition was not rerun unchanged. The ownership classifier was corrected in commit `7322d504b45bf53b36060d51588435833066df0b` by treating final operator confirmation / stage registration as operator-owned.

## Final verification

On exact code checkpoint `7322d504b45bf53b36060d51588435833066df0b`:

- `33406362430` — Phase49.3I.42C3 Qt6 Crawl + AI Runtime CI — PASS end-to-end.
- `33406362422` — Phase49.3I.17 Single Active AI CI — PASS.
- Qt foundation/full parity, acquisition continuation, AI model/cost/crawl tests, mature acquisition, Filament, Profile/Commerce/Stage, Single Active AI, offscreen Qt launch, legacy launcher, and final source guards all passed inside the 42C3 gate.

Targeted behavior covered by regressions includes:

- Images current-stage AI uses local repair rather than Provider/live source HTTP.
- AI cannot claim success while AI-fixable defects remain.
- exact image metadata defects and counts are visible.
- live free/Persian/JSON model filtering favors known strong Product candidates.
- variable OpenRouter routers are not Product defaults.
- operator final confirmation remains manual after image SEO repair.

## OpenRouter model guidance for this workflow

The application’s preferred free-Persian candidate ordering currently includes:

1. `qwen/qwen3-32b:free`
2. `google/gemma-4-31b-it:free`
3. `openai/gpt-oss-20b:free`
4. `google/gemma-4-26b-a4b-it:free`
5. `qwen/qwen3-30b-a3b:free`

This ordering is an internal 3DPrintHub suitability prior, not a universal Persian benchmark. Runtime acceptance is authoritative: the selected model must be text-capable, pass the Product Structured/JSON capability gate, and pass the real Persian + JSON probe. A model that is free or multilingual but fails the exact Structured Product contract must be rejected.

## Owner Local acceptance next

1. clean ff-only pull of the final documentation HEAD;
2. canonical `RUN_PHASE49_3I42C_LOCAL_GATE.ps1 -LaunchApp`;
3. Product #309 stage rail must show counts, exact missing items, and AI/manual ownership split;
4. Stage 3 `AI همین مرحله` must repair local image SEO without MakerWorld HTTP 403 and without Provider cost;
5. if only `تأیید نهایی اپراتور (ثبت مرحله)` remains, it must be manual and `ai_fixable_count` must be zero;
6. Settings → OpenRouter → reload live models → choose an exact Product-safe free/Persian `JSON✓` model; do not use `openrouter/auto` or `openrouter/free`;
7. run the real Persian + JSON probe and save the exact model;
8. re-run Product #309 Link/Data AI and verify source identity + SEO remain valid.

No Production deploy is approved before this owner foreground acceptance.
