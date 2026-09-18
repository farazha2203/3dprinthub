# LAST_IMPLEMENTATION — 3DPrintHub

Status: ACTIVE
Updated: 2026-09-18
Repository: `D:\projects\3DPrintHub`
Branch: `wip/phase50-a2l-owner-qa-20260917`
Verified HEAD at resume: `c7067f761a59e97bede2775cfc3765350241b88e`
Canonical branch remote baseline: `27dbbdc587c923fabc20e78838685689e4f0112e`
Production baseline from current docs: `12e319ace1eb55c114d7117e1b5a2fa170b410ab`
Production A2K release prepared earlier: `84d1a87c4ea632823743b9cc1c5fe3ba81b08843`

## Owner request
- Make Product Wizard image review actually usable: large scrollable gallery, multi-select/edit and working source-image recovery/display.
- Repair `Sync همه با سایت`; incomplete legacy Filament identities must not abort valid rows.
- Add selected/all Filament bulk edits for print-hour, supervision and preheat fields.
- Add deterministic product/material recommendations plus AI source/image production-spec preview with operator confirmation.
- Preserve approved Site-first Instagram workflow, all verified images (5 means 5), SEO/media quality, Product URL, Story/Highlight companion behavior and brand assets.
- Enable manual Pasargad card-transfer receipt flow with admin review + operator notification; Podium/Farataz automation is deferred until separate verified source audit.

## Resume verification
- Root `AGENTS.md` and required project docs reread.
- Global `D:\projects\AGENTS.md` requires this checkpoint.
- Worktree is intentionally dirty with A2L implementation plus temporary QA/Instagram evidence files; do not reset or blindly clean.
## Current evidence
- Existing A2L phase doc records Stage 3 as 2 large columns / 560 px minimum viewport / always-on vertical scrollbar.
- Current `ProductImageGrid` uses row-based minimum height so final row controls remain inside scroll range.
- Filament page already contains Select Visible / Clear / bulk-selected / bulk-all-active controls.
- Current Site sync loops per row, catches failures and returns `synced/failed/failures` instead of aborting the batch.
- Manual-payment seed command is dry-run by default and receipt notification targets the existing admin/operator notification pipeline.
- Current dirty diff passes `git diff --check` before test execution.

## Known blocker / safety
- Production reverse bridge `127.0.0.1:22024` was down in the last verified state (`ERR-49-154`). No Production deployment or payment apply until tunnel + Host identity + backup/readiness gates pass.
- Windows Catalog SQLite must be backed up before any real data-mutating acceptance run.
- Temporary `_tmp_*`, `.instagram-cdp-profile`, `assets/` and `instagram-assets/` require classification before any cleanup or commit.

## Current test run
- Started local gate: `git diff --check`, Django `check`, migration drift, A2L Django tests.
- `git diff --check`: PASS.
- Django `check`: reached normal CKEditor warning; process completion/result still to be reconciled.

## Exact next safe action
1. Reconcile the in-flight local gate result; do not rerun unchanged if it failed.
2. Inspect A2L source deltas + relevant tests for gallery, Filament sync/bulk, smart material/AI preview, Instagram and receipt flow.
3. Fix only evidenced failures, run focused tests, then full local acceptance.
4. Commit/push clean source/docs without temporary QA/browser profiles.
5. Reopen/verify Qt UI locally; Production remains gated by tunnel recovery.

## 2026-09-18 local gate update
- Python compile for changed A2L Qt/runtime modules: PASS.
- Catalog A2L focused suite: 30/30 PASS in 23.379 s.
- Verified behaviors include: fail-soft full Filament sync with legacy blank identity, selected/all bulk rates, decorative PLA/PETG recommendation excluding PA12-CF/PLA-CF defaults, source image dedupe/recovery, larger Stage 3 scroll contract, AI preview-only estimates using images, operator-value preservation, Buffer 5-image preservation and tracked public Product URL.
- UTF-8 corruption discovered in new AI Preview/settings/test strings was repaired; changed-file scan now reports zero `???`/replacement-character defects.

## Exact next safe action update
1. Exact A2L candidate `4375c007874faa87c874f3806705532128814176` is pushed and the stale Qt process was replaced by a fresh exact-SHA runtime; Product #628 real-data probe resolves 10 local images with a 1964 px scroll range.
2. Real full-Filament audit found 71 rows: 8 complete Site identities and 63 historical blank-Brand rows. This is ERR-49-158 data debt, not a reason to invent Brand.
3. Follow-up registered-Brand bulk repair is LOCAL_TESTED: selected rows only, registered Brand only, no Material/Color/price/stock/rate overwrite; real-copy #14 repair PASS and integrity stays ok.
4. Follow-up A2L scoped Catalog gate is 57/57 PASS; Store/checkout 10/10 and manual-payment coverage remain PASS from the exact candidate; Qt launcher verify and diff-check PASS.
5. Commit/push the Brand-repair follow-up, relaunch exact SHA, then keep Production gated on reverse-tunnel recovery + Host backup/readiness.

## 2026-09-18 regression reconciliation
- Broad 109-test Catalog regression first exposed one stale 4-column assertion after the owner-required Stage 3 redesign. Runtime was correct (2 large columns); the old test contract was updated to require 2 columns, large cards, reachable row-height and always-on scroll. Focused rerun: PASS.
- After that changed condition, broad rerun exposed an intermittent acquisition test fixture: mocked rich extraction listed downloaded filenames without creating files, while runtime intentionally counts real local files. The test fixture now creates six local image files so `images_saved` is deterministic. Focused rerun: PASS.
- These were test-contract/fixture defects; no production behavior was weakened. The image runtime still requires actual local files before claiming `images_saved`.
- Buffer Story metadata was hardened to carry the canonical tracked Product URL through the official Instagram `link` metadata field; companion-story regression PASS.
- Owner-approved gold/navy profile logo exists as a square 1254×1254 PNG and is now registered as the shared profile/highlight base asset in the brand-style contract.
