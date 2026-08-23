# PROJECT ROADMAP

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Epic: `Phase49 — Unified Product / Slider / Catalog Sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.8 — Observable AI Execution Recovery`
Status: `FINAL CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Permanent Delivery Order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI → WINDOWS PULL --FF-ONLY → LOCAL GATE → MANUAL QA → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION BACKUP/DEPLOY/VERIFY`

## Preserved Phase49 Foundations
- unified Product / Hero / Catalog synchronization,
- Product Workspace as canonical detailed editor,
- Persian content and SEO workflows,
- Product / Portfolio publish targets,
- AI provider/runtime/provenance/cost stack,
- image intake default 10 / hard max 20,
- Fixed / Range / Formula pricing,
- visual Products Explorer,
- Local vs Production publish separation,
- live fetched GitHub snapshot handoff.

## Phase49.3I Path
Implemented and preserved:
- exact Search/Listing/Category URL authority,
- Preview Candidate before Full Fetch,
- approved-only Full Fetch,
- archive/not-needed + blocked identity dedupe,
- source-text sanitation,
- Product-vs-Group routing by source `model_url_pattern`,
- Explorer views/multi-select/context actions,
- selection-loop guard,
- compact metadata + Persian filter/sort,
- AI first-paint,
- secure provider credential hydration/model catalog loading,
- MakerWorld Preview JavaScript recovery.

Current hotfix sequence:
`49.3I.6 Secure Credential Field Persistence → 49.3I.7 Preview + Provider Hub Recovery → 49.3I.8 Observable AI Execution Recovery`.

## Phase49.3I.8 — Observable AI Execution Recovery
### Windows Evidence
The bottom Product Workspace action `✨ تکمیل هوشمند همه فیلدهای AI` remained on `avalai ... در حال تولید محتوا...` for about five minutes with no durable progress window.

### Verified Root Cause — ERR-49-026
That exact Phase49.3C operator button still invoked legacy `ProductStudio.generate_ai("commerce")`. It bypassed the mature `_phase49_3e_run_ai()` Task Center and therefore bypassed:
- 49.3I immediate first-paint,
- 49.3F connection/send/receive progress,
- 49.3H result/error/cost visibility.

The old worker was background-threaded, but the operator only saw a status string and had no bounded/observable execution contract.

### Implemented Scope
1. Route bottom All-Fields AI → mature `_phase49_3e_run_ai("all")`.
2. Route non-Quick stage assistant actions → mature Task Center; image stage keeps image scope.
3. Preserve Quick/title-only behavior.
4. Do not create a second AI client/worker.
5. Keep the 49.3I first-paint handoff.
6. Add visible elapsed time to mature progress.
7. Add `توقف انتظار`.
8. Add 210-second operator watchdog, aligned to the existing single AI request timeout upper bound.
9. Cancel/timeout invalidates the execution generation.
10. Late results from a cancelled/timed-out run are ignored and cannot mutate product/image data.
11. Error/result stays visible; app remains open.
12. Preserve 49.3I.7 MakerWorld Preview recovery and mature approved Full Fetch.

### Final Validation
CI-only PR `#53`: `CLOSED / NOT MERGED`.
Validated Epic runtime base: `3fdab5dc4a56204b6370f72df04ec0956e8ba6ce`.
Marker head: `0d05d0fb25f02daa07df93f9cf47d2ea0333b8b8` — not merged.

Successful runs:
- Phase49.3I: `32620646603` — SUCCESS.
- Phase49.3H: `32620646600` — SUCCESS.
- Phase49.3G: `32620646605` — SUCCESS.
- Full Phase49 + Full Django: `32620646657` — SUCCESS.

CI verified runner v49.3I.8, ASCII/live-Git guards, compilation, dedicated AI execution tests, stale-result guards, Preview recovery composition, provider/Explorer/3H/3G regressions, Django checks/no-migration contract, Windows Catalog tests and Full Django suite.

## Must-Not-Touch
- Product Workspace detailed editor,
- mature Task Center/provider execution semantics,
- mature source full extraction,
- Preview → Approve → Full Fetch state machine,
- image limit default 10 / hard max 20,
- selection-loop guard,
- Product-vs-Group routing,
- 49.3H result/error/cost stack,
- Fixed / Range / Formula independence,
- Product/Hero revision/idempotency,
- Production DB/media/source,
- secrets in Git/log/SQLite.

## Windows Manual QA — NEXT
1. close Catalog Center and verify clean worktree,
2. fetch/prune + ff-only pull current Epic,
3. run `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`,
4. verify runner `49.3I.8` + Git snapshot marker,
5. click the **bottom** All-Fields AI button,
6. immediate startup progress must appear,
7. mature progress must show connection → sent → waiting/received → save/result/error,
8. elapsed time + Stop Waiting must remain visible and app must stay responsive,
9. Stop/210s timeout must block any late result from applying,
10. exact MakerWorld Search Preview must work without `Locator.evaluate_all` syntax error,
11. Preview remains one-thumbnail/basic identity only,
12. approve one candidate with image limit 20 and verify Full Fetch only after approval,
13. recheck Provider keys/model lists, FTP/Bridge credentials, Product open/selection and pricing modes.

## Local Publish Gate
Only after 49.3I.8 Windows QA passes:
- exactly one `LOCAL PUBLISH ONLY`,
- Local Django E2E,
- verify product/image/pricing/provenance payload,
- no Production endpoint.

## Production Gate
Blocked until Windows QA + Local Publish E2E + explicit owner approval. Before deployment re-verify host branch/commit/path, MySQL vendor/name, backup, rollback and host constraints.

## Immediate Next Step
Windows live GitHub snapshot pull and repository-owned Runner 49.3I.8. No manual Local source patch; no Local Publish or Production yet.
