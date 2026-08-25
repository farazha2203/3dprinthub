# CURRENT PROJECT STATE

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Base Epic: `epic/phase49-unified-product-slider-sync`
Active Phase: `49.3I`
Active Hotfix: `49.3I.25 — Product-First Workflow + Persistent Diagnostics + Startup No-AI`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA REQUIRED`
Production: `UNTOUCHED / NOT APPROVED`

## Current Position
Owner diagnostics from 2026-08-25 proved three remaining runtime defects after 49.3I.24:
- hidden `/models` requests still escaped the constructor-only startup guard immediately after `startup_first_idle`; OpenAI was called automatically and even received an OpenRouter-style key, producing HTTP 401 and a 3.4–3.7s UI lag,
- Product link completion called the layered Workspace `save(silent=True)` before AI, producing many repeated Product updates/commits and UI refresh work,
- a deferred callback recorded `cannot commit - no transaction is active`, consistent with worker diagnostics and UI Product writes sharing the same SQLite connection/transaction boundary.

The same diagnostics show AvalAI generation itself can legitimately take roughly 20–65 seconds. Network AI therefore remains background work; the UI must stay responsive and cancellation/diagnostics remain available.

## 49.3I.25 Implemented on GitHub
- Product workflow now starts with `محتوا و SEO`; `اطلاعات پایه` is second, then Images, Commerce, Source/License and Publish.
- Stage navigation remains non-blocking: incomplete data does not prevent opening another stage.
- Basic Info receives the same prominent `🌐 تکمیل همه اطلاعات بر اساس لینک محصول` action.
- legacy visible Product-data-send buttons are redirected to the same exact-link completion action where present.
- link completion no longer invokes the full layered Workspace save before AI; only a changed source URL is persisted before the job.
- source facts now preserve `estimated_weight_grams` and `estimated_print_minutes`.
- MakerWorld exact `#profileId-...` is used to prefer the weight belonging to that exact print profile when present in page data; unrelated profile weight is not guessed.
- valid source weight/time are persisted together with canonical source identity before applying AI editorial fields.
- Images uses one vertically scrollable gallery page with five cards per row; existing per-card image controls/metadata remain preserved.
- Local/Production publish preflight shows missing items; when missing Content/Basic fields are AI-fillable it can launch the exact-link completion workflow. Publish itself remains blocked until readiness is satisfied.
- hidden model discovery is denied for the whole process unless a visible operator Model Search/Test action grants a short explicit discovery window. Startup never needs a provider connection test.
- diagnostics now use a dedicated SQLite connection with WAL/busy-timeout instead of committing on the Product UI connection.
- Catalog DB common operations gain an instance RLock guard for remaining shared-connection access.
- runtime text log is append-only with no finite backup rotation; previous audit/runtime logs are not cleared on startup or diagnostic export.
- focused 49.3I.25 regression test file added.

## Database / Migration / Safety
- Django migration: `NONE`
- Catalog schema migration: `NONE`
- existing diagnostic tables are reused
- no reset/drop/truncate
- no Product/media/history deletion
- no API key/token committed
- Local Catalog SQLite is never copied to Production MySQL
- Production untouched

## Verification Status
GitHub implementation and regression tests are committed, but no Windows execution result has been reported for 49.3I.25 yet. Do not call this hotfix accepted or deployable until the Local gate passes.

## Exact Next Task — Windows 49.3I.25 Gate
1. close Catalog Center and verify the Local worktree is clean,
2. fetch/prune and ff-only pull the live feature branch,
3. verify Local HEAD equals fetched Remote HEAD,
4. compile 49.3I.25 plus touched diagnostics/composition modules,
5. run focused 49.3I.25 and inherited 49.3I.24/23/22/21/20/19/18 tests,
6. run `catalog_center\launch.py --verify-only`,
7. launch and verify no provider `/models`/connection request happens until the operator explicitly presses Search/Test,
8. verify Dashboard/runtime logs still contain previous sessions after close/reopen,
9. open Product 151 / MakerWorld 2801606 and verify Stage 1 is Content/SEO, Basic Info has the exact-link completion button, and all stages remain freely navigable,
10. verify Images shows five cards per row and scrolls vertically with all product image controls/metadata intact,
11. run exact-link completion once and verify source title + available exact-profile weight + Persian Content/SEO/image text are previewed/applied without the pre-AI multi-save storm,
12. while AI is waiting, verify the main Workspace remains responsive,
13. verify no new `cannot commit - no transaction is active` event,
14. test Local publish preflight: missing items are shown and AI-fillable gaps offer exact-link completion.

## Release Gate After Windows PASS
Exactly one `LOCAL PUBLISH ONLY` → Local Store/Admin/Product/Media/SEO E2E → explicit owner approval → read-only Production path/branch/commit/venv/MySQL/backup/rollback verification → deploy approved GitHub snapshot only → Production HTTP/data/media/SEO verification.

## What Remains
Windows 49.3I.25 automated + visual/runtime gate, one Local Publish E2E, owner acceptance, then Production verification/deploy. Store ZarinPal remains after Catalog Production verification.
