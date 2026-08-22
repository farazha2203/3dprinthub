# PROJECT ROADMAP

Updated: 2026-08-22
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Epic: `Phase49 — Unified Product / Slider / Catalog Sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.5 — Selection Loop Guard + Compact Product Metadata`

> Historical phase detail remains in Git history and phase documents. This file is the operational forward path and acceptance gate for the active Epic.

## Permanent Delivery Order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI → WINDOWS PULL --FF-ONLY → LOCAL GATE → MANUAL QA → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION BACKUP/DEPLOY/VERIFY`

## Preserved Phase49 Foundations
- unified product import/publish and homepage-slider synchronization,
- Persian sales/product workspace,
- dual Product / Portfolio publish targets,
- material/color handling,
- readiness wizard and fail-closed Local/Production publish separation,
- AI provider/runtime recovery,
- image pipeline and image SEO metadata,
- Phase49.3D workspace hardening,
- Phase49.3E AI task center,
- Phase49.3F provider/provenance/dynamic pricing,
- Phase49.3G usability + manual-override guard,
- Phase49.3H SEO execution/result/error/cost + image default 10 / hard max 20.

## Phase49.3I Core — Implemented and CI-Validated
- exact operator Search/Listing URL authoritative,
- Preview Candidate before Full Fetch,
- approved-only Full Fetch,
- archive/not-needed + blocked identity dedupe,
- scraped source-text safety,
- Product Workspace remains canonical detailed editor,
- Fixed / Range / Formula pricing modes,
- AI progress first paint,
- Windows PowerShell 5.1 ASCII-only runner,
- live fetched GitHub snapshot handoff,
- Explorer-style product browsing,
- Product URL vs Group/Category/Search URL routing by source `model_url_pattern`.

## Phase49.3I.4 — Windows QA Result
Status: `AUTOMATED LOCAL GATE PASS / VISUAL VIEW PASS / INTERACTION REGRESSION FOUND`

Windows proved:
- clean pull to repository snapshot,
- runner 49.3I.4 passed,
- 137 Catalog tests PASS,
- 419 Django tests PASS, 2 skipped,
- no new migration,
- Product thumbnails/view modes visually corrected,
- Production untouched.

Manual interaction then exposed `ERR-49-022`: selecting/opening a product could freeze because hidden Treeview selection was written again from its own `<<TreeviewSelect>>` callback.

Owner also requested restoration of compact operational details and friendly Persian filter/sort choices.

## Phase49.3I.5 — Selection Loop Guard + Compact Metadata
Status: `FINAL CI SUCCESS / WINDOWS RERUN PENDING`

### Scope completed on GitHub
1. Break card → hidden Treeview → `load_product` → Treeview feedback loop.
2. One-way Treeview synchronization with re-entrancy guard.
3. Only call `selection_set()` when selection actually differs.
4. `load_product()` becomes state-only and never writes selection back.
5. Guard repeated Open actions and yield one Tk frame before Product Workspace construction.
6. Keep Products lightweight while showing compact metadata:
   - Product ID,
   - state,
   - source,
   - image count,
   - added date,
   - publish state.
7. Persian filters:
   - کارهای من,
   - جدید,
   - نیازمند بروزرسانی,
   - بدون تصویر,
   - بدون محتوا,
   - آماده انتشار,
   - صف انتشار,
   - منتشرشده,
   - خطادار,
   - همه محصولات.
8. Persian sorts:
   - اولویت کاری,
   - جدیدترین,
   - قدیمی‌ترین,
   - آخرین بروزرسانی,
   - بیشترین امتیاز,
   - بیشترین دانلود.
9. Hide old raw operator filter/sort bar while preserving mature DB/filter backend.
10. Preserve all 49.3I.4 Explorer/source-routing behavior.

### Regression Coverage
- fake Treeview test fires `load_product()` immediately from `selection_set()` and asserts one write only,
- compact card metadata test,
- Persian filter/sort option test,
- repeated-open/Tk-yield source contract,
- previous Explorer image/view/multi-select/context-menu tests,
- Product-vs-Group URL routing tests,
- 49.3H/3G regressions,
- Django migration and Full Django regression suites.

### Final CI Validation
CI-only PR `#50`: `CLOSED / NOT MERGED`.
Validated Epic runtime base: `cdaac6680ea8545f52ece15ecaa3ce0a575eabe9`.
Marker head: `57813f47f649bb2c415aa0fae1481f4a2561ce1d` — not merged.

Successful runs:
- Phase49.3I: `32580222694` — SUCCESS.
- Phase49.3H: `32580222686` — SUCCESS.
- Phase49.3G: `32580222682` — SUCCESS.
- Full Phase49 + Full Django: `32580222683` — SUCCESS.

### Database / Migration
- Django migration: `NONE`.
- Catalog schema migration: `NONE`.
- no DB reset/drop/truncate.
- no media rewrite/delete.
- Production untouched.

## Must-Not-Touch
- Product Workspace detailed editor,
- Phase49.3H AI progress/result/error/cost,
- image default 10 / hard max 20,
- Preview → Approve → Full Fetch,
- archive/blocked dedupe,
- Fixed / Range / Formula independence,
- product/hero revision and idempotency,
- Production source/DB/media,
- secrets,
- live Git snapshot handoff guard.

## Windows Manual QA Gate — NEXT
1. close Catalog Center.
2. verify clean worktree.
3. fetch/prune current Epic.
4. fast-forward-only pull.
5. run repository-owned `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`.
6. confirm Runner `49.3I.5` and Git snapshot marker.
7. select one card: no freeze/loop.
8. Edit Product: one Product Workspace opens.
9. close and use right-click → Open Product: one Workspace opens.
10. verify card ID/state/source/image-count/date/publish-state.
11. verify Ready / Publish Queue / Published filters.
12. verify Newest / Oldest / Last Updated sorts.
13. recheck all Explorer view modes, Ctrl/Shift selection and safe queue removal.
14. verify Direct Product URL vs Group/Search Preview routing.
15. AI first-paint/progress regression QA.
16. Fixed / Range / Formula regression QA.

## Local Publish Gate
Only after the Windows interaction/metadata/routing/AI/pricing QA passes:
- one `LOCAL PUBLISH ONLY`,
- Local Django E2E,
- verify product/image/pricing/provenance payload,
- no Production endpoint.

## Production Gate
Production remains blocked until:
- Windows 49.3I.5 local gate succeeds,
- manual visual/data/interaction QA succeeds,
- Local Publish E2E succeeds,
- explicit owner approval,
- verified Production DB/vendor/path/branch/commit,
- backup + rollback readiness.

## Immediate Next Step
Windows clean pull of current Epic and run Phase49.3I.5 with `-LaunchApp`; verify selection/open responsiveness and compact metadata/filter/sort. No Production command before owner acceptance.
