# PROJECT ROADMAP

Updated: 2026-08-22
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Epic: `Phase49 — Unified Product / Slider / Catalog Sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.6 — Secure Credential Field Persistence`

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
- Local vs Production publish separation,
- GitHub-first Windows delivery and live fetched snapshot guard.

## Phase49.3I Progress
Implemented and preserved:
- explicit operator Search/Listing/Category URL is authoritative,
- Preview Candidate before Full Fetch,
- approved-only Full Fetch,
- archive/not-needed + blocked identity dedupe,
- source-text sanitation,
- visual Products Explorer,
- Explorer view modes/multi-select/context menu,
- selection feedback-loop guard,
- compact Product ID/state/source/image/date/publish metadata,
- Persian filters/sorts,
- source `model_url_pattern` Product-vs-Group routing,
- AI first paint,
- Windows PowerShell 5.1 ASCII runner.

## Windows QA Confirmed After 49.3I.5
Owner confirmed:
- Catalog Center launches after the 49.3I.5 handoff,
- Product link vs Group/Category/Search/sub-branch routing is fixed.

The remaining newly reported regression is operator-visible credential persistence.

## Phase49.3I.6 — Secure Credential Field Persistence
Status: `GITHUB IMPLEMENTED / FINAL CI PENDING / WINDOWS QA PENDING`

### Requested Delta
Credentials that were saved securely must not appear to vanish on the next save/restart/release. The stable secure location remains Windows Credential Store; the solution must not put passwords/tokens/API keys into SQLite, Git, source files or logs.

### Verified Boundary
Existing secure backend already persists and reads credentials. The UX defect is that masked fields are initialized without secure-store hydration and mature Save handlers clear the input widgets after writing to the secure store.

### Implemented Scope
1. Add `phase49_3i_secret_persistence.py` as an additive App87 shell layer.
2. Hydrate FTP password and Bridge token from the secure store at startup when their fields are empty.
3. Hydrate selected AI provider key from its secure provider entry.
4. Rehydrate masked fields after a successful mature Save clears them.
5. When Provider changes, load that Provider's stored key.
6. Do not overwrite a newly typed unsaved key during normal same-provider refresh.
7. Preserve explicit credential delete/clear behavior.
8. Keep all credentials out of SQLite/log/source/Git.
9. No schema migration and no Production action.

### Regression Tests
Dedicated tests cover startup hydration, post-save hydration, provider switching, unsaved input preservation and source-level secret-safety. CI also checks same-phase composition and previous Phase49.3I/3H/3G behavior.

### Runner / CI
- canonical runner: `RUN_PHASE49_3I_LOCAL_GATE.ps1` v49.3I.6,
- ASCII-only for Windows PowerShell 5.1,
- live fetched Remote Epic HEAD equality guard preserved,
- new marker: `PHASE49_3I_SECRET_PERSISTENCE=ENABLED`,
- new module/test included in compile and dedicated unit gate,
- final CI probe still required before Windows handoff.

## Must-Not-Touch
- Product Workspace detailed editor,
- existing secure backend semantics and explicit delete actions,
- 49.3I.5 selection-loop guard,
- Product-vs-Group routing,
- AI result/error/cost stack,
- image limit 10/20,
- Fixed / Range / Formula independence,
- Product/Hero revision/idempotency,
- Production DB/media/source,
- historical media,
- secrets in Git/log/SQLite.

## Windows Manual QA After Final CI
Windows must prove saved AI key, FTP password and Bridge token remain visibly present as masked values immediately after Save and after restart; switching AI provider restores that provider's saved key; live AI/FTP/Bridge tests still consume the secure credentials; no secret appears in SQLite/logs/source. Existing link-routing, selection/open, AI progress and pricing regressions are rechecked.

## Local Publish Gate
Only after credential + remaining 49.3I manual QA passes:
- one `LOCAL PUBLISH ONLY`,
- Local Django E2E,
- verify product/image/pricing/provenance payload,
- no Production endpoint.

## Production Gate
Production remains blocked until Windows QA and Local Publish E2E pass and the owner explicitly approves Production. Before deploy, re-verify host branch/commit/path, MySQL vendor/name, backup and rollback.

## Immediate Next Step
Finish GitHub CI for 49.3I.6 and close the CI-only validation probe without merge. Then provide Windows fast-forward-only pull + repository runner instructions. No Production command yet.
